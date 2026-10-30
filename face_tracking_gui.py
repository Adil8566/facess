import cv2
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os


class FaceTrackingGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Face Tracking Mode GUI")
        self.root.geometry("1150x720")
        self.root.resizable(False, False)

        self.camera = None
        self.running = False
        self.current_frame = None

        # Lokasi file
        base_dir = os.path.dirname(os.path.abspath(__file__))

        face_path = os.path.join(
            base_dir,
            "haarcascade_frontalface_default.xml"
        )

        eye_path = os.path.join(
            base_dir,
            "haarcascade_eye.xml"
        )

        # Load Haar Cascade
        self.face_cascade = cv2.CascadeClassifier(face_path)
        self.eye_cascade = cv2.CascadeClassifier(eye_path)

        if self.face_cascade.empty() or self.eye_cascade.empty():
            messagebox.showerror(
                "Error",
                "File Haar Cascade tidak ditemukan atau gagal dimuat!"
            )
            root.destroy()
            return

        # ==============================
        # JUDUL
        # ==============================
        tk.Label(
            root,
            text="FACE TRACKING MODE",
            font=("Arial", 26, "bold")
        ).pack(pady=15)

        # ==============================
        # FRAME UTAMA
        # ==============================
        main_frame = tk.Frame(root)
        main_frame.pack()

        # ==============================
        # FRAME KAMERA
        # ==============================
        camera_frame = tk.Frame(
            main_frame,
            bg="black",
            bd=2,
            relief="solid"
        )

        camera_frame.grid(
            row=0,
            column=0,
            padx=15
        )

        self.camera_label = tk.Label(
            camera_frame,
            text="Kamera belum aktif",
            bg="black",
            fg="white",
            font=("Arial", 18)
        )

        self.camera_label.pack()

        # ==============================
        # INFORMASI DETEKSI
        # ==============================
        info_frame = tk.Frame(
            main_frame,
            width=300,
            height=500,
            bd=2,
            relief="groove"
        )

        info_frame.grid(
            row=0,
            column=1,
            padx=15,
            sticky="n"
        )

        info_frame.pack_propagate(False)

        tk.Label(
            info_frame,
            text="INFORMASI DETEKSI",
            font=("Arial", 17, "bold")
        ).pack(pady=30)

        self.status_label = tk.Label(
            info_frame,
            text="Status: Kamera Tidak Aktif",
            font=("Arial", 12)
        )
        self.status_label.pack(pady=15)

        self.face_label = tk.Label(
            info_frame,
            text="Jumlah Wajah: 0",
            font=("Arial", 12)
        )
        self.face_label.pack(pady=15)

        self.eye_label = tk.Label(
            info_frame,
            text="Jumlah Mata: 0",
            font=("Arial", 12)
        )
        self.eye_label.pack(pady=15)

        self.position_label = tk.Label(
            info_frame,
            text="Posisi Wajah: -",
            font=("Arial", 12)
        )
        self.position_label.pack(pady=15)

        # ==============================
        # TOMBOL
        # ==============================
        button_frame = tk.Frame(root)
        button_frame.pack(pady=15)

        tk.Button(
            button_frame,
            text="START CAMERA",
            width=15,
            height=2,
            command=self.start_camera
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            button_frame,
            text="STOP CAMERA",
            width=15,
            height=2,
            command=self.stop_camera
        ).grid(row=0, column=1, padx=5)

        tk.Button(
            button_frame,
            text="CAPTURE",
            width=15,
            height=2,
            command=self.capture_image
        ).grid(row=0, column=2, padx=5)

        tk.Button(
            button_frame,
            text="EXIT",
            width=15,
            height=2,
            command=self.close_application
        ).grid(row=0, column=3, padx=5)

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close_application
        )

    # ==============================
    # START CAMERA
    # ==============================
    def start_camera(self):

        if self.running:
            return

        self.camera = cv2.VideoCapture(
            0,
            cv2.CAP_DSHOW
        )

        if not self.camera.isOpened():
            self.camera.release()

            self.camera = cv2.VideoCapture(
                1,
                cv2.CAP_DSHOW
            )

        if not self.camera.isOpened():
            messagebox.showerror(
                "Error",
                "Kamera tidak dapat dibuka!"
            )
            self.camera = None
            return

        self.camera.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            1280
        )

        self.camera.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            720
        )

        self.running = True

        self.status_label.config(
            text="Status: Face Tracking Aktif"
        )

        self.update_camera()

    # ==============================
    # UPDATE CAMERA
    # ==============================
    def update_camera(self):

        if not self.running:
            return

        ret, frame = self.camera.read()

        if not ret:
            # Coba baca lagi pada siklus berikutnya agar tampilan tidak macet.
            self.root.after(100, self.update_camera)
            return

        # Mirror kamera
        frame = cv2.flip(
            frame,
            1
        )

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        # ==============================
        # DETEKSI WAJAH
        # ==============================
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=6,
            minSize=(100, 100)
        )

        face_count = len(faces)
        eye_count = 0
        position = "-"

        # ==============================
        # PROSES WAJAH
        # ==============================
        for x, y, w, h in faces:

            if position == "-":
                position = f"X: {x}, Y: {y}"

            # Kotak wajah
            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                "FACE",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

            # Area wajah
            roi_gray = gray[
                y:y + h,
                x:x + w
            ]

            roi_color = frame[
                y:y + h,
                x:x + w
            ]

            # ==============================
            # AREA MATA
            # Hanya 15% - 50% bagian atas wajah
            # ==============================
            eye_top = int(h * 0.15)
            eye_bottom = int(h * 0.50)

            eye_gray = roi_gray[
                eye_top:eye_bottom,
                0:w
            ]

            eye_color = roi_color[
                eye_top:eye_bottom,
                0:w
            ]

            # Deteksi mata
            eyes = self.eye_cascade.detectMultiScale(
                eye_gray,
                scaleFactor=1.1,
                minNeighbors=10,
                minSize=(25, 15),
                maxSize=(100, 60)
            )

            # ==============================
            # FILTER MATA
            # ==============================
            valid_eyes = []

            for ex, ey, ew, eh in eyes:

                center_x = ex + ew // 2
                center_y = ey + eh // 2

                if (
                    w * 0.10 < center_x < w * 0.90
                    and
                    (eye_bottom - eye_top) * 0.15
                    < center_y
                    < (eye_bottom - eye_top) * 0.90
                ):
                    valid_eyes.append(
                        (ex, ey, ew, eh)
                    )

            # Urutkan dari kiri ke kanan
            valid_eyes.sort(
                key=lambda e: e[0]
            )

            # Maksimal 2 mata
            for ex, ey, ew, eh in valid_eyes[:2]:

                center = (
                    ex + ew // 2,
                    ey + eh // 2
                )

                radius = min(
                    ew,
                    eh
                ) // 2

                cv2.circle(
                    eye_color,
                    center,
                    radius,
                    (255, 0, 0),
                    2
                )

                eye_count += 1

        # ==============================
        # UPDATE INFORMASI
        # ==============================
        self.face_label.config(
            text=f"Jumlah Wajah: {face_count}"
        )

        self.eye_label.config(
            text=f"Jumlah Mata: {eye_count}"
        )

        self.position_label.config(
            text=f"Posisi Wajah: {position}"
        )

        # ==============================
        # TAMPILKAN FRAME
        # ==============================
        frame_rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        image = Image.fromarray(
            frame_rgb
        )

        image = image.resize(
            (750, 500),
            Image.Resampling.LANCZOS
        )

        photo = ImageTk.PhotoImage(
            image
        )

        self.camera_label.config(
            image=photo,
            text=""
        )

        self.camera_label.image = photo

        self.current_frame = frame.copy()

        # Update kamera
        self.root.after(
            15,
            self.update_camera
        )

    # ==============================
    # STOP CAMERA
    # ==============================
    def stop_camera(self):

        self.running = False

        if self.camera:
            self.camera.release()
            self.camera = None

        self.camera_label.config(
            image="",
            text="Kamera belum aktif"
        )

        self.camera_label.image = None

        self.status_label.config(
            text="Status: Kamera Tidak Aktif"
        )

        self.face_label.config(
            text="Jumlah Wajah: 0"
        )

        self.eye_label.config(
            text="Jumlah Mata: 0"
        )

        self.position_label.config(
            text="Posisi Wajah: -"
        )

        self.current_frame = None

    # ==============================
    # CAPTURE
    # ==============================
    def capture_image(self):

        if self.current_frame is None:
            messagebox.showwarning(
                "Peringatan",
                "Kamera belum aktif!"
            )
            return

        filename = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            "capture_face.jpg"
        )

        if cv2.imwrite(
            filename,
            self.current_frame
        ):
            messagebox.showinfo(
                "Berhasil",
                f"Gambar disimpan:\n{filename}"
            )

    # ==============================
    # EXIT
    # ==============================
    def close_application(self):

        self.running = False

        if self.camera:
            self.camera.release()

        self.root.destroy()


# ==============================
# PROGRAM UTAMA
# ==============================
if __name__ == "__main__":

    root = tk.Tk()

    app = FaceTrackingGUI(
        root
    )

    root.mainloop()