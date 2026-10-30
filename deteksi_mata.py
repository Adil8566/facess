from pathlib import Path
import cv2

# Semua aset dicari berdasarkan lokasi script, bukan folder terminal aktif.
BASE_DIR = Path(__file__).resolve().parent
IMAGE_PATH = BASE_DIR / "faces.jpg"
FACE_CASCADE_PATH = BASE_DIR / "haarcascade_frontalface_default.xml"
EYE_CASCADE_PATH = BASE_DIR / "haarcascade_eye.xml"

image = cv2.imread(str(IMAGE_PATH))
if image is None:
    raise FileNotFoundError(f"Gambar tidak ditemukan: {IMAGE_PATH}")

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
face_cascade = cv2.CascadeClassifier(str(FACE_CASCADE_PATH))
eye_cascade = cv2.CascadeClassifier(str(EYE_CASCADE_PATH))

if face_cascade.empty():
    raise FileNotFoundError(f"Haar Cascade wajah gagal dimuat: {FACE_CASCADE_PATH}")
if eye_cascade.empty():
    raise FileNotFoundError(f"Haar Cascade mata gagal dimuat: {EYE_CASCADE_PATH}")

faces = face_cascade.detectMultiScale(
    gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
)
jumlah_mata = 0

for x, y, w, h in faces:
    roi_gray = gray[y:y + h, x:x + w]
    roi_color = image[y:y + h, x:x + w]
    eyes = eye_cascade.detectMultiScale(
        roi_gray, scaleFactor=1.05, minNeighbors=5, minSize=(15, 15)
    )

    for ex, ey, ew, eh in eyes:
        center = (ex + ew // 2, ey + eh // 2)
        radius = max(2, min(ew, eh) // 2)
        cv2.circle(roi_color, center, radius, (255, 0, 0), 2)
        jumlah_mata += 1

print("Jumlah wajah terdeteksi:", len(faces))
print("Jumlah mata terdeteksi:", jumlah_mata)
cv2.imshow("Hasil Deteksi Mata", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
