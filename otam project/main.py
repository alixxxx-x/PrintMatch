import os
import cv2
from PIL import Image
import customtkinter as ctk
from tkinter.filedialog import askopenfilename

# Your signature matching function
# Make sure you have signature.py with function match(path1, path2)
from signature import match

# -----------------------------
# CustomTkinter configuration
# -----------------------------
ctk.set_appearance_mode("dark")          # "dark", "light", "system"
ctk.set_default_color_theme("dark-blue") # "blue", "dark-blue", "green"

THRESHOLD = 80  # Match threshold (percent)

TEMP_DIR = os.path.join(os.getcwd(), "temp")
os.makedirs(TEMP_DIR, exist_ok=True)


# -----------------------------
# Helpers
# -----------------------------
def update_preview(frame: ctk.CTkFrame, image_path: str):
    """Show image preview inside a frame."""
    # clear previous widgets
    for w in frame.winfo_children():
        w.destroy()

    if not image_path or not os.path.exists(image_path):
        label = ctk.CTkLabel(frame, text="No Preview Available")
        label.pack(expand=True)
        return

    try:
        img = Image.open(image_path)
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(250, 250))

        label = ctk.CTkLabel(frame, image=ctk_img, text="")
        # IMPORTANT: keep a reference, otherwise image can disappear
        label.image = ctk_img
        label.pack(expand=True)
    except Exception as e:
        label = ctk.CTkLabel(frame, text="No Preview Available")
        label.pack(expand=True)
        print(f"Error loading image preview: {e}")


def browsefunc(entry: ctk.CTkEntry, preview_frame: ctk.CTkFrame):
    filename = askopenfilename(filetypes=[("Image files", "*.jpeg *.png *.jpg")])
    if filename:
        entry.delete(0, ctk.END)
        entry.insert(ctk.END, filename)
        update_preview(preview_frame, filename)


def capture_image_from_cam(sign: int) -> str | None:
    """Capture image from webcam. SPACE to capture, ESC to cancel."""
    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cam.isOpened():
        print("Cannot open camera")
        return None

    cv2.namedWindow("Camera Preview", cv2.WINDOW_NORMAL)

    saved_path = None
    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed to grab frame")
            break

        cv2.imshow("Camera Preview", frame)
        k = cv2.waitKey(1) & 0xFF

        if k == 27:  # ESC
            break
        elif k == 32:  # SPACE
            saved_path = os.path.join(TEMP_DIR, f"test_img{sign}.png")
            cv2.imwrite(saved_path, frame)
            print(f"Saved: {saved_path}")
            break

    cam.release()
    cv2.destroyAllWindows()
    return saved_path


def captureImage(entry: ctk.CTkEntry, preview_frame: ctk.CTkFrame, sign: int):
    CustomDialog(
        master=entry.winfo_toplevel(),
        title="Camera Capture",
        message="A camera window will open.\n\nPress SPACE to capture.\nPress ESC to cancel.",
        on_close=lambda: _do_capture(entry, preview_frame, sign),
    )


def _do_capture(entry: ctk.CTkEntry, preview_frame: ctk.CTkFrame, sign: int):
    path = capture_image_from_cam(sign=sign)
    if path:
        entry.delete(0, ctk.END)
        entry.insert(ctk.END, path)
        update_preview(preview_frame, path)


def checkSimilarity(window, path1: str, path2: str):
    if not path1 or not path2:
        CustomDialog(master=window, title="Error", message="Please select both signatures first!")
        return

    if not os.path.exists(path1) or not os.path.exists(path2):
        CustomDialog(master=window, title="Error", message="One or both file paths do not exist.")
        return

    try:
        result = match(path1=path1, path2=path2)  # expected percent number
    except Exception as e:
        CustomDialog(master=window, title="Error", message=f"Matching failed:\n{e}")
        return

    if result <= THRESHOLD:
        CustomDialog(
            master=window,
            title="Failure",
            message=f"Signatures are {result}% similar.\n\nSignatures do NOT match.",
        )
    else:
        CustomDialog(
            master=window,
            title="Success",
            message=f"Signatures are {result}% similar.\n\nSignatures match successfully!",
        )


# -----------------------------
# UI Classes
# -----------------------------
class CustomDialog(ctk.CTkToplevel):
    def __init__(self, master, title: str, message: str, on_close=None):
        super().__init__(master)
        self.title(title)
        self.geometry("420x180")
        self.resizable(False, False)
        self.on_close = on_close

        # Make dialog modal-ish
        self.transient(master)
        self.grab_set()

        self.message_label = ctk.CTkLabel(self, text=message, font=ctk.CTkFont(size=14))
        self.message_label.pack(pady=20, padx=20)

        self.ok_button = ctk.CTkButton(self, text="OK", command=self.close_dialog)
        self.ok_button.pack(pady=10)

        # Close with window X
        self.protocol("WM_DELETE_WINDOW", self.close_dialog)

    def close_dialog(self):
        self.grab_release()
        self.destroy()
        if self.on_close:
            self.on_close()


class SignatureMatcherApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Signature Matching App")
        self.geometry("900x650")

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="Compare Two Signatures",
            font=ctk.CTkFont(size=26, weight="bold")
        )
        self.title_label.pack(pady=(20, 10))

        # Preview area
        self.preview_frame = ctk.CTkFrame(self.main_frame)
        self.preview_frame.pack(pady=10, padx=20, fill="x")

        self.preview_sig1 = ctk.CTkFrame(self.preview_frame, width=250, height=250)
        self.preview_sig1.pack(side="left", pady=10, padx=10, expand=True, fill="both")

        self.preview_sig2 = ctk.CTkFrame(self.preview_frame, width=250, height=250)
        self.preview_sig2.pack(side="right", pady=10, padx=10, expand=True, fill="both")

        # Signature 1 controls
        self.sig1_frame = ctk.CTkFrame(self.main_frame)
        self.sig1_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(self.sig1_frame, text="Signature 1", font=ctk.CTkFont(size=16)).pack(
            side="left", padx=10
        )

        self.sig1_entry = ctk.CTkEntry(self.sig1_frame, width=420, placeholder_text="Select or capture signature 1")
        self.sig1_entry.pack(side="left", padx=10, expand=True)

        ctk.CTkButton(
            self.sig1_frame,
            text="Capture",
            command=lambda: captureImage(self.sig1_entry, self.preview_sig1, 1)
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            self.sig1_frame,
            text="Browse",
            command=lambda: browsefunc(self.sig1_entry, self.preview_sig1)
        ).pack(side="left", padx=5)

        # Signature 2 controls
        self.sig2_frame = ctk.CTkFrame(self.main_frame)
        self.sig2_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(self.sig2_frame, text="Signature 2", font=ctk.CTkFont(size=16)).pack(
            side="left", padx=10
        )

        self.sig2_entry = ctk.CTkEntry(self.sig2_frame, width=420, placeholder_text="Select or capture signature 2")
        self.sig2_entry.pack(side="left", padx=10, expand=True)

        ctk.CTkButton(
            self.sig2_frame,
            text="Capture",
            command=lambda: captureImage(self.sig2_entry, self.preview_sig2, 2)
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            self.sig2_frame,
            text="Browse",
            command=lambda: browsefunc(self.sig2_entry, self.preview_sig2)
        ).pack(side="left", padx=5)

        # Compare button
        self.compare_btn = ctk.CTkButton(
            self.main_frame,
            text="Compare Signatures",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            command=lambda: checkSimilarity(self, self.sig1_entry.get(), self.sig2_entry.get())
        )
        self.compare_btn.pack(pady=25)

        # Footer
        self.footer = ctk.CTkLabel(
            self.main_frame,
            text="Signature Matching project made by Nazym Noui and Rahma Zendaoui",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.footer.pack(side="bottom", pady=10)


if __name__ == "__main__":
    app = SignatureMatcherApp()
    app.mainloop()
