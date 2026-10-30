# Quiz Deteksi Mata - versi web untuk ngrok

Versi web ini mempertahankan proses deteksi wajah dan mata dengan OpenCV Haar Cascade, tetapi mengganti antarmuka Tkinter menjadi halaman web Flask. Kamera diakses langsung oleh browser pada perangkat yang membuka halaman. Karena itu, kamera HP dapat digunakan ketika halaman dibuka dari HP.

## Isi tambahan

- `web_app.py`: server Flask dan proses deteksi OpenCV.
- `templates/index.html`: halaman aplikasi.
- `static/style.css`: tampilan responsif untuk komputer dan HP.
- `static/app.js`: preview kamera langsung di browser, pengiriman frame analisis ringan, overlay kotak deteksi, dan unduh hasil.
- `requirements.txt`: library yang dibutuhkan.
- `run_web.bat`: cara cepat menjalankan di Windows.

File Tkinter (`face_tracking_gui.py`) dan script uji gambar (`deteksi_mata.py`) tetap disimpan sebagai versi desktop/tes lama.

## A. Menjalankan di Windows

1. Ekstrak folder `Quiz_Deteksi_Mata`.
2. Pastikan Python sudah terpasang dan perintah `py --version` dapat dijalankan di CMD/Terminal.
3. Buka folder project di VS Code.
4. Buka Terminal pada folder yang berisi `web_app.py`.
5. Pada terminal PowerShell VS Code, jalankan:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   python web_app.py
   ```

   Jika terminal yang digunakan adalah Command Prompt (CMD), perintah aktivasinya:

   ```bat
   .venv\Scripts\activate.bat
   ```

6. Buka `http://127.0.0.1:5000` di browser komputer.
7. Tekan **Mulai Kamera** dan izinkan akses kamera.

Alternatif paling mudah di Windows: klik dua kali `run_web.bat`. File tersebut akan membuat virtual environment, memasang dependency, lalu menjalankan server.

## B. Membuka melalui ngrok

Biarkan server Flask tetap berjalan. Buka terminal kedua, lalu jalankan:

```bash
ngrok http 5000
```

Salin alamat HTTPS yang diberikan ngrok, misalnya `https://contoh.ngrok-free.app`, kemudian buka alamat itu melalui browser HP atau bagikan kepada pengguna lain.

**Penting:** gunakan URL HTTPS dari ngrok, bukan alamat HTTP lokal. Browser modern mensyaratkan secure context untuk mengakses kamera. Saat pertama dibuka, tekan **Mulai Kamera** lalu pilih **Izinkan** ketika browser meminta izin.

## C. Optimasi agar tampilan HP lebih lancar

- Preview video ditampilkan langsung dari kamera HP di browser; tidak menunggu gambar hasil proses server.
- Frame analisis dikecilkan hingga maksimal 480 piksel dan dikompresi JPEG kualitas 55%.
- OpenCV mengembalikan koordinat kotak wajah/mata dan jumlah deteksi, bukan mengirim ulang seluruh gambar melalui jaringan.
- Analisis dijalankan berkala sekitar 2-3 kali per detik. Kotak deteksi dapat sedikit tertinggal dari gerakan wajah, tetapi video utama tetap mengikuti frame rate kamera.

Kualitas tetap dipengaruhi oleh kemampuan HP, prosesor laptop yang menjalankan Flask, serta kecepatan dan kestabilan internet. Jika deteksi terasa lambat, dekatkan wajah ke kamera dan gunakan pencahayaan yang cukup.

## D. Hal yang harus tetap berjalan

- Komputer/laptop tempat Flask berjalan harus tetap menyala dan terhubung internet.
- Terminal yang menjalankan `python web_app.py` harus tetap aktif.
- Terminal ngrok juga harus tetap aktif.
- Jika salah satu dihentikan, alamat publik tidak dapat mengakses aplikasi.

## E. Catatan keamanan dan privasi

- Siapa pun yang memiliki URL ngrok dapat membuka halaman aplikasi selama tunnel aktif. Jangan gunakan untuk data sensitif tanpa menambahkan autentikasi.
- Frame kamera dikirim ke server Flask untuk diproses dan tidak disimpan oleh aplikasi ini. Tombol **Simpan Hasil** mengunduh gambar hasil deteksi ke perangkat pengguna.
- Gunakan aplikasi hanya dengan persetujuan orang yang sedang direkam.
- Jangan aktifkan Flask debug mode ketika aplikasi dibuka ke internet.

## F. Pemecahan masalah

- **Kamera tidak muncul di HP:** pastikan memakai link HTTPS ngrok, izinkan akses kamera, dan buka melalui Chrome/Safari terbaru.
- **Kamera sedang digunakan:** tutup aplikasi lain yang sedang memakai kamera.
- **`ModuleNotFoundError: No module named flask/cv2`:** aktifkan `.venv`, lalu jalankan `pip install -r requirements.txt`.
- **File Haar Cascade gagal dimuat:** pastikan kedua file XML tetap satu folder dengan `web_app.py`.
- **Link ngrok tidak bisa dibuka:** pastikan server Flask dan proses ngrok masih berjalan serta port yang digunakan adalah `5000`.

## G. Endpoint pemeriksaan

Buka `http://127.0.0.1:5000/health`. Jika aplikasi berjalan, hasilnya berupa JSON dengan `ok: true`.
