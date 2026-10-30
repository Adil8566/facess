(() => {
  const video = document.getElementById('cameraVideo');
  const overlay = document.getElementById('detectionOverlay');
  const overlayContext = overlay.getContext('2d');
  const placeholder = document.getElementById('cameraPlaceholder');
  const stage = document.getElementById('videoStage');
  const startButton = document.getElementById('startButton');
  const stopButton = document.getElementById('stopButton');
  const captureButton = document.getElementById('captureButton');
  const message = document.getElementById('message');
  const cameraState = document.getElementById('cameraState');
  const faceCount = document.getElementById('faceCount');
  const eyeCount = document.getElementById('eyeCount');
  const detectionStatus = document.getElementById('detectionStatus');
  const facePosition = document.getElementById('facePosition');

  // Canvas kecil di luar layar hanya dipakai untuk mengambil frame analisis.
  const processingCanvas = document.createElement('canvas');
  const processingContext = processingCanvas.getContext('2d', { willReadFrequently: true });
  let stream = null;
  let running = false;
  let processing = false;
  let latestDetections = null;
  let loopTimer = null;

  function setMessage(text, isError = false) {
    message.textContent = text;
    message.style.color = isError ? '#ff9d9d' : '';
  }

  function setMetrics(faces = 0, eyes = 0, status = 'Kamera tidak aktif', position = '-') {
    faceCount.textContent = faces;
    eyeCount.textContent = eyes;
    detectionStatus.textContent = status;
    facePosition.textContent = position;
  }

  function clearOverlay() {
    overlayContext.clearRect(0, 0, overlay.width, overlay.height);
    latestDetections = null;
  }

  function drawDetections(result) {
    if (!video.videoWidth || !video.videoHeight) return;

    // Ukuran bitmap overlay mengikuti ukuran asli video agar kotak presisi.
    if (overlay.width !== video.videoWidth || overlay.height !== video.videoHeight) {
      overlay.width = video.videoWidth;
      overlay.height = video.videoHeight;
    }
    overlayContext.clearRect(0, 0, overlay.width, overlay.height);

    const sourceWidth = result.frame?.width || 1;
    const sourceHeight = result.frame?.height || 1;
    const scaleX = overlay.width / sourceWidth;
    const scaleY = overlay.height / sourceHeight;
    const lineWidth = Math.max(2, overlay.width / 320);

    overlayContext.lineWidth = lineWidth;
    overlayContext.strokeStyle = '#55d6a5';
    overlayContext.fillStyle = '#55d6a5';
    overlayContext.font = `bold ${Math.max(13, overlay.width / 38)}px Arial`;

    (result.face_boxes || []).forEach((box) => {
      const x = box.x * scaleX;
      const y = box.y * scaleY;
      const w = box.w * scaleX;
      const h = box.h * scaleY;
      overlayContext.strokeRect(x, y, w, h);
      overlayContext.fillText('FACE', x, Math.max(18, y - 7));
    });

    overlayContext.strokeStyle = '#ffb45c';
    (result.eye_boxes || []).forEach((box) => {
      overlayContext.strokeRect(
        box.x * scaleX,
        box.y * scaleY,
        box.w * scaleX,
        box.h * scaleY
      );
    });
    latestDetections = result;
  }

  async function startCamera() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setMessage('Browser tidak mendukung kamera. Buka link HTTPS ngrok melalui Chrome atau Safari.', true);
      return;
    }

    startButton.disabled = true;
    setMessage('Meminta izin kamera dari browser...');
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        audio: false,
        video: {
          facingMode: { ideal: 'user' },
          width: { ideal: 640 },
          height: { ideal: 480 },
          frameRate: { ideal: 24, max: 30 }
        }
      });
      video.srcObject = stream;
      await video.play();
      running = true;
      placeholder.hidden = true;
      stage.classList.add('scanning');
      cameraState.textContent = 'Aktif';
      cameraState.classList.add('active');
      stopButton.disabled = false;
      captureButton.disabled = false;
      clearOverlay();
      setMessage('Kamera aktif. Preview berjalan langsung; deteksi diperbarui berkala.');
      setMetrics(0, 0, 'Menunggu deteksi', '-');
      processNextFrame();
    } catch (error) {
      stopCamera(false);
      startButton.disabled = false;
      let reason = 'Kamera tidak dapat diakses.';
      if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
        reason = 'Izin kamera ditolak. Izinkan kamera pada pengaturan browser, lalu coba lagi.';
      } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
        reason = 'Kamera tidak ditemukan pada perangkat ini.';
      } else if (error.name === 'NotReadableError') {
        reason = 'Kamera sedang digunakan aplikasi lain. Tutup aplikasi tersebut lalu coba lagi.';
      }
      setMessage(reason, true);
    }
  }

  async function processNextFrame() {
    if (!running || processing) return;
    if (video.readyState < HTMLMediaElement.HAVE_CURRENT_DATA || !video.videoWidth) {
      loopTimer = window.setTimeout(processNextFrame, 350);
      return;
    }

    processing = true;
    try {
      // Kirim maksimal 480px, bukan 720px, agar upload dari HP lebih ringan.
      const scale = Math.min(1, 480 / video.videoWidth);
      processingCanvas.width = Math.max(1, Math.round(video.videoWidth * scale));
      processingCanvas.height = Math.max(1, Math.round(video.videoHeight * scale));
      processingContext.drawImage(video, 0, 0, processingCanvas.width, processingCanvas.height);
      const image = processingCanvas.toDataURL('image/jpeg', 0.55);

      const response = await fetch('/api/detect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image }),
        cache: 'no-store'
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || 'Gagal memproses gambar.');

      drawDetections(result);
      setMetrics(result.faces, result.eyes, result.status, result.position);
      setMessage('Deteksi aktif. Preview kamera berjalan langsung dari perangkat.');
    } catch (error) {
      setMessage(error.message || 'Koneksi ke server terputus.', true);
    } finally {
      processing = false;
      // Analisis sekitar 2-3 kali/detik; preview video tetap berjalan lancar lokal.
      if (running) loopTimer = window.setTimeout(processNextFrame, 350);
    }
  }

  function stopCamera(showMessage = true) {
    running = false;
    if (loopTimer) window.clearTimeout(loopTimer);
    loopTimer = null;
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      stream = null;
    }
    video.srcObject = null;
    clearOverlay();
    placeholder.hidden = false;
    stage.classList.remove('scanning');
    cameraState.textContent = 'Belum aktif';
    cameraState.classList.remove('active');
    startButton.disabled = false;
    stopButton.disabled = true;
    captureButton.disabled = true;
    setMetrics();
    if (showMessage) setMessage('Kamera dihentikan.');
  }

  function captureImage() {
    if (!video.videoWidth) {
      setMessage('Belum ada gambar kamera untuk disimpan.', true);
      return;
    }
    const output = document.createElement('canvas');
    output.width = video.videoWidth;
    output.height = video.videoHeight;
    const ctx = output.getContext('2d');
    ctx.drawImage(video, 0, 0, output.width, output.height);
    if (overlay.width && overlay.height) ctx.drawImage(overlay, 0, 0, output.width, output.height);

    const link = document.createElement('a');
    const stamp = new Date().toISOString().replace(/[:.]/g, '-');
    link.href = output.toDataURL('image/jpeg', 0.9);
    link.download = `hasil-deteksi-mata-${stamp}.jpg`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    setMessage('Gambar hasil deteksi berhasil disiapkan untuk diunduh.');
  }

  startButton.addEventListener('click', startCamera);
  stopButton.addEventListener('click', () => stopCamera());
  captureButton.addEventListener('click', captureImage);
  window.addEventListener('pagehide', () => stopCamera(false));
})();
