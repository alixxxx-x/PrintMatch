import customtkinter as ctk
from tkinter.filedialog import askopenfilename
import os
import cv2
from signature import match
from PIL import Image, ImageTk

# CustomTkinter appearance configuration
ctk.set_appearance_mode("dark")  # Options: "dark", "light", "system"
ctk.set_default_color_theme("dark-blue")  # Options: "blue", "dark-blue", "green"

# Match Threshold
THRESHOLD = 80

def browsefunc(ent, preview_frame):
    filename = askopenfilename(filetypes=[
        ("Image files", "*.jpeg *.png *.jpg"),
    ])
    if filename:
        ent.delete(0, ctk.END)
        ent.insert(ctk.END, filename)
        update_preview(preview_frame, filename)

def update_preview(frame, image_path):
    for widget in frame.winfo_children():
        widget.destroy() 

    try:
        # open and resize img
        img = Image.open(image_path)
        ctk_image = ctk.CTkImage(light_image=img, size=(250, 250))

        # display img in frame
        label = ctk.CTkLabel(frame, image=ctk_image, text="")  # empty text to show image only
        label.pack(expand=True)
    except Exception as e:
        # placeholder if img doesnt work
        label = ctk.CTkLabel(frame, text="No Preview Available")
        label.pack(expand=True)
        print(f"Error loading image: {e}")



def capture_image_from_cam_into_temp(sign=1):
    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cv2.namedWindow("Camera Preview")

    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed to grab frame")
            break
        cv2.imshow("Camera Preview", frame)

        k = cv2.waitKey(1)
        if k % 256 == 27:  # ESC pressed
            print("Escape hit, closing...")
            break
        elif k % 256 == 32:  # SPACE pressed
            if not os.path.isdir('temp'):
                os.mkdir('temp', mode=0o777)
            img_name = f"./temp/test_img{sign}.png"
            cv2.imwrite(filename=img_name, img=frame)
            print(f"{img_name} written!")
            break

    cam.release()
    cv2.destroyAllWindows()
    return True

def captureImage(ent, preview_frame, sign):
    filename = os.path.join(os.getcwd(), 'temp', f'test_img{sign}.png')
    dialog = ctk.CTkInputDialog(
        text="Press Space Bar to capture image and ESC to exit.",
        title="Camera Capture"
    )
    result = dialog.get_input()
    if result is not None:
        capture_image_from_cam_into_temp(sign=sign)
        ent.delete(0, ctk.END)
        ent.insert(ctk.END, filename)
        update_preview(preview_frame, filename)
    return True

def checkSimilarity(window, path1, path2):
    if not path1 or not path2:
        CustomDialog(
            master=window,
            title="Error",
            message="Please select both signatures first!",
        )
        return False

    result = match(path1=path1, path2=path2)
    if result <= THRESHOLD:
        CustomDialog(
            master=window,
            title="Failure",
            message=f"Signatures are {result}% similar!!\nSignatures do not match.",
        )
    else:
        CustomDialog(
            master=window,
            title="Success",
            message=f"Signatures are {result}% similar!!\nSignatures match successfully!",
        )
    return True


class SignatureMatcherApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Signature Matching App")
        self.geometry("800x600")

        # Create main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Title
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="Compare Two Signatures",
            font=ctk.CTkFont(size=24, weight="bold")
        )

        self.title_footer = ctk.CTkLabel(
            self.main_frame,
            text="Signature Matching project made by Nazym Noui and Rahma Zendaoui",
            font=ctk.CTkFont(size=10, weight="bold")
        )
        self.title_footer.pack(side="bottom")
        self.title_label.pack(pady=20, expand=True)
        # placeholder for signature preview
        self.preview_frame = ctk.CTkFrame(self.main_frame, width=300, height=100)
        self.preview_frame.pack(pady=10, padx=20, fill="x", expand=True)
        self.preview_label = ctk.CTkLabel(
            self.preview_frame,
            text="Signature Preview",
            font=ctk.CTkFont(size=16)
        )
        self.preview_sig1 = ctk.CTkFrame(self.preview_frame, width=250, height=250)
        self.preview_sig1.pack(side="left", pady=10, padx=10, expand=True)
        #self.preview_sig1_label = ctk.CTkLabel()

        self.preview_sig2 = ctk.CTkFrame(self.preview_frame, width=250, height=250)
        self.preview_sig2.pack(side="right", pady=10, padx=10, expand=True)

        # signature 1 Frame
        self.sig1_frame = ctk.CTkFrame(self.main_frame)
        self.sig1_frame.pack(pady=10, padx=20, fill="x", expand=True)

        self.sig1_label = ctk.CTkLabel(
            self.sig1_frame,
            text="Signature 1",
            font=ctk.CTkFont(size=16)
        )
        self.sig1_label.pack(side="left", padx=10, expand=True)

        self.sig1_entry = ctk.CTkEntry(
            self.sig1_frame,
            width=300,
            placeholder_text="Select or capture signature 1"
        )
        self.sig1_entry.pack(side="left", padx=10, expand=True)

        self.sig1_capture_btn = ctk.CTkButton(
            self.sig1_frame,
            text="Capture",
            command=lambda: captureImage(self.sig1_entry, self.preview_sig1, 1)
        )
        self.sig1_capture_btn.pack(side="left", padx=5, expand=True)

        self.sig1_browse_btn = ctk.CTkButton(
            self.sig1_frame,
            text="Browse",
            command=lambda: browsefunc(self.sig1_entry, self.preview_sig1)
        )
        self.sig1_browse_btn.pack(side="left", padx=5, expand=True)

        # signature 2 Frame
        self.sig2_frame = ctk.CTkFrame(self.main_frame)
        self.sig2_frame.pack(pady=10, padx=20, fill="x", expand=True)

        self.sig2_label = ctk.CTkLabel(
            self.sig2_frame,
            text="Signature 2",
            font=ctk.CTkFont(size=16)
        )
        self.sig2_label.pack(side="left", padx=10, expand=True)

        self.sig2_entry = ctk.CTkEntry(
            self.sig2_frame,
            width=300,
            placeholder_text="Select or capture signature 2"
        )
        self.sig2_entry.pack(side="left", padx=10, expand=True)

        self.sig2_capture_btn = ctk.CTkButton(
            self.sig2_frame,
            text="Capture",
            command=lambda: captureImage(self.sig2_entry, self.preview_sig2, 2)
        )
        self.sig2_capture_btn.pack(side="left", padx=5, expand=True)

        self.sig2_browse_btn = ctk.CTkButton(
            self.sig2_frame,
            text="Browse",
            command=lambda: browsefunc(self.sig2_entry, self.preview_sig2)
        )
        self.sig2_browse_btn.pack(side="left", padx=5, expand=True)

        # compare Button
        self.compare_btn = ctk.CTkButton(
            self.main_frame,
            text="Compare Signatures",
            font=ctk.CTkFont(size=16, weight="bold"),
            command=lambda: checkSimilarity(
                self,
                self.sig1_entry.get(),
                self.sig2_entry.get()
            ),
            height=40
        )
        self.compare_btn.pack(pady=30, expand=True)

class CustomDialog(ctk.CTkToplevel):
    def __init__(self, master, title, message, on_close=None):
        super().__init__(master)

        #dialog window
        self.title(title)
        self.geometry("400x150")
        self.resizable(False, False)
        self.on_close = on_close

        #dialog message
        self.message_label = ctk.CTkLabel(self, text=message, font=ctk.CTkFont(size=16))
        self.message_label.pack(pady=20)

        
        self.ok_button = ctk.CTkButton(self, text="OK", command=self.close_dialog)
        self.ok_button.pack(pady=20)

    def close_dialog(self):
        if self.on_close:
            self.on_close()  
        self.destroy()  

if __name__ == "__main__":
    app = SignatureMatcherApp()
    app.mainloop()