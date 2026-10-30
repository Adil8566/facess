"""Aplikasi web deteksi wajah dan mata dengan Flask + OpenCV.

Preview kamera tetap berjalan langsung di browser. Server hanya menerima
frame berukuran kecil untuk analisis dan mengembalikan koordinat deteksi,
bukan mengirim ulang seluruh gambar. Cara ini lebih ringan untuk HP/ngrok.
"""
from __future__ import annotations

import base64
import binascii
import os
from pathlib import Path

import cv2
import numpy as np
from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import RequestEntityTooLarge

BASE_DIR = Path(__file__).resolve().parent
FACE_CASCADE_PATH = BASE_DIR / "haarcascade_frontalface_default.xml"
EYE_CASCADE_PATH = BASE_DIR / "haarcascade_eye.xml"

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 700 * 1024  # frame kecil saja

face_cascade = cv2.CascadeClassifier(str(FACE_CASCADE_PATH))
eye_cascade = cv2.CascadeClassifier(str(EYE_CASCADE_PATH))

if face_cascade.empty():
    raise RuntimeError(f"Haar Cascade wajah gagal dimuat: {FACE_CASCADE_PATH}")
if eye_cascade.empty():
    raise RuntimeError(f"Haar Cascade mata gagal dimuat: {EYE_CASCADE_PATH}")


def process_frame(data_url: str) -> dict:
    """Decode frame kecil, deteksi wajah/mata, lalu kembalikan koordinat."""
    if not isinstance(data_url, str) or not data_url:
        raise ValueError("Data gambar tidak ditemukan.")

    if "," in data_url:
        header, encoded = data_url.split(",", 1)
        if "base64" not in header:
            raise ValueError("Format gambar tidak didukung. Gunakan JPEG.")
    else:
        encoded = data_url

    try:
        image_bytes = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("Data gambar tidak valid.") from exc
    if not image_bytes:
        raise ValueError("Gambar kosong.")

    buffer = np.frombuffer(image_bytes, dtype=np.uint8)
    frame = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError("Gambar tidak dapat dibaca oleh OpenCV.")

    height, width = frame.shape[:2]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Parameter dibuat sedikit lebih ringan untuk perangkat dan koneksi HP.
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.15,
        minNeighbors=5,
        minSize=(45, 45),
    )

    face_boxes = []
    eye_boxes = []
    face_count = len(faces)
    position = "-"

    for x, y, w, h in faces:
        if position == "-":
            position = f"X: {int(x)}, Y: {int(y)}"
        face_boxes.append({"x": int(x), "y": int(y), "w": int(w), "h": int(h)})

        eye_top = int(h * 0.15)
        eye_bottom = int(h * 0.50)
        eye_gray = gray[y + eye_top:y + eye_bottom, x:x + w]
        if eye_gray.size == 0:
            continue

        eyes = eye_cascade.detectMultiScale(
            eye_gray,
            scaleFactor=1.15,
            minNeighbors=7,
            minSize=(14, 10),
            maxSize=(max(24, int(w * 0.48)), max(20, int(h * 0.25))),
        )

        valid_eyes = []
        region_height = eye_bottom - eye_top
        for ex, ey, ew, eh in eyes:
            center_x = ex + ew // 2
            center_y = ey + eh // 2
            if w * 0.10 < center_x < w * 0.90 and region_height * 0.12 < center_y < region_height * 0.92:
                valid_eyes.append((ex, ey, ew, eh))

        valid_eyes.sort(key=lambda item: item[0])
        for ex, ey, ew, eh in valid_eyes[:2]:
            eye_boxes.append({
                "x": int(x + ex),
                "y": int(y + eye_top + ey),
                "w": int(ew),
                "h": int(eh),
            })

    return {
        "frame": {"width": int(width), "height": int(height)},
        "faces": face_count,
        "eyes": len(eye_boxes),
        "face_boxes": face_boxes,
        "eye_boxes": eye_boxes,
        "position": position,
        "status": "Wajah terdeteksi" if face_count else "Arahkan wajah ke kamera",
    }


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify({"ok": True, "message": "Aplikasi deteksi mata aktif."})


@app.post("/api/detect")
def detect():
    payload = request.get_json(silent=True) or {}
    try:
        return jsonify(process_frame(payload.get("image", "")))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        app.logger.exception("Terjadi kesalahan saat memproses frame kamera")
        return jsonify({"error": "Terjadi kesalahan saat memproses gambar."}), 500


@app.errorhandler(RequestEntityTooLarge)
def too_large(_error):
    return jsonify({"error": "Ukuran gambar terlalu besar. Coba lagi."}), 413


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
