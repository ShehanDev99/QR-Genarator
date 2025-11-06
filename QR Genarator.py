import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import qrcode

class FuturisticQRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("⚡ Futuristic QR Generator ⚡")
        self.root.geometry("900x700")
        self.root.resizable(False, False)

        # State variables
        self.image_path = None
        self.qr_pil_image = None
        self.preview_tk_image = None  # <— Keep reference
        self.dark_mode = True

        # Colors and fonts
        self.font_title = ("Orbitron", 20, "bold")
        self.font_normal = ("Consolas", 11, "bold")

        self.accent_cyan = "#00f0ff"
        self.bg_dark = "#071021"
        self.panel_dark = "#0f1724"
        self.bg_light = "#eef6ff"
        self.panel_light = "#f0f6fb"
        self.text_dark = "#cccccc"  # <-- updated font color for dark theme
        self.text_light = "#0a1724"

        # Build interface
        self.build_ui()
        self.apply_theme()

    def build_ui(self):
        # Title
        self.title_label = tk.Label(self.root, text="⚙️ Image → QR Code Generator", font=self.font_title)
        self.title_label.pack(pady=14)

        # Buttons frame
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(pady=8)

        self.btn_select = self.make_btn(self.top_frame, "📁 SELECT IMAGE", self.select_image)
        self.btn_select.grid(row=0, column=0, padx=8)

        self.btn_generate = self.make_btn(self.top_frame, "⚡ GENERATE QR", self.generate_qr)
        self.btn_generate.grid(row=0, column=1, padx=8)

        self.btn_save = self.make_btn(self.top_frame, "💾 SAVE QR", self.save_qr)
        self.btn_save.grid(row=0, column=2, padx=8)

        self.btn_mode = self.make_btn(self.top_frame, "☀️ Light Mode", self.toggle_mode)
        self.btn_mode.grid(row=0, column=3, padx=8)

        # Info label
        self.info_var = tk.StringVar(value="Select an image (PNG / JPG / JPEG).")
        self.info_label = tk.Label(self.root, textvariable=self.info_var, font=self.font_normal)
        self.info_label.pack(pady=6)

        # Panels
        self.main_panel = tk.Frame(self.root)
        self.main_panel.pack(padx=18, pady=6, fill="both", expand=True)

        # QR panel
        self.qr_panel = tk.Frame(self.main_panel)
        self.qr_panel.pack(side="left", padx=28)
        tk.Label(self.qr_panel, text="Generated QR", font=("Orbitron", 11, "bold")).pack(pady=6)
        self.canvas = tk.Canvas(self.qr_panel, width=420, height=420, bd=0, highlightthickness=0)
        self.canvas.pack(pady=6)

        # Image preview panel
        self.preview_panel = tk.Frame(self.main_panel)
        self.preview_panel.pack(side="left", padx=20)
        tk.Label(self.preview_panel, text="Original Image Preview", font=("Orbitron", 11, "bold")).pack(pady=6)
        self.preview_label = tk.Label(self.preview_panel, bd=2, relief="ridge", width=220, height=220)
        self.preview_label.pack(pady=6)

        # Footer
        self.footer = tk.Label(self.root, text="Made with ⚡ Futuristic UI", font=("Consolas", 9))
        self.footer.pack(side="bottom", pady=10)

    def make_btn(self, parent, text, cmd):
        btn = tk.Label(parent, text=text, font=self.font_normal, cursor="hand2", bd=0, relief="flat")
        btn.bind("<Button-1>", lambda e: cmd())
        btn.bind("<Enter>", lambda e: btn.configure(relief="raised"))
        btn.bind("<Leave>", lambda e: btn.configure(relief="flat"))
        return btn

    # -------------------- Functions --------------------
    def select_image(self):
        filetypes = [("Image files", "*.png *.jpg *.jpeg"), ("All files", "*.*")]
        path = filedialog.askopenfilename(title="Select image", filetypes=filetypes)
        if not path:
            self.info_var.set("No image selected.")
            return

        try:
            im = Image.open(path)
            im.thumbnail((250, 250))
            self.preview_tk_image = ImageTk.PhotoImage(im)  # <— store reference
            self.preview_label.configure(image=self.preview_tk_image)
            self.image_path = path
            self.info_var.set(f"Selected: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Image Error", f"Could not open image:\n{e}")
            self.image_path = None

    def generate_qr(self):
        if not self.image_path:
            messagebox.showwarning("No image", "Please select an image first.")
            return

        try:
            data = f"Image Path: {os.path.abspath(self.image_path)}"
            qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=8,
                border=2,
            )
            qr.add_data(data)
            qr.make(fit=True)
            fill = "cyan" if self.dark_mode else "black"
            back = "black" if self.dark_mode else "white"
            pil_qr = qr.make_image(fill_color=fill, back_color=back).convert("RGB")
            self.qr_pil_image = pil_qr

            self.display_qr(pil_qr)
            self.info_var.set("QR generated — click '💾 SAVE QR' to save.")
        except Exception as e:
            messagebox.showerror("QR Error", f"Failed to generate QR:\n{e}")

    def display_qr(self, pil_img):
        cw, ch = int(self.canvas["width"]), int(self.canvas["height"])
        w, h = pil_img.size
        scale = min(cw / w, ch / h, 1.0)
        new_w, new_h = int(w * scale), int(h * scale)
        resized = pil_img.resize((new_w, new_h), Image.NEAREST)
        tkimg = ImageTk.PhotoImage(resized)
        self.canvas.delete("all")
        self.canvas.create_image(cw // 2, ch // 2, image=tkimg)
        self.canvas.image = tkimg  # keep reference

    def save_qr(self):
        if not self.qr_pil_image:
            messagebox.showwarning("No QR", "Generate a QR first.")
            return

        default_name = (
            os.path.splitext(os.path.basename(self.image_path))[0] + "_QR.png"
            if self.image_path
            else "qr.png"
        )

        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")],
            initialfile=default_name,
        )
        if not path:
            return

        try:
            self.qr_pil_image.save(path)
            messagebox.showinfo("Saved", f"QR saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save QR:\n{e}")

    # -------------------- Theme --------------------
    def toggle_mode(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_theme(self):
        if self.dark_mode:
            root_bg = self.bg_dark
            panel_bg = self.panel_dark
            title_fg = self.accent_cyan
            text_fg = self.text_dark  # <-- this is now #cccccc
        else:
            root_bg = self.bg_light
            panel_bg = self.panel_light
            title_fg = "#0b2740"
            text_fg = self.text_light

        # root background
        self.root.configure(bg=root_bg)
        self.title_label.configure(bg=root_bg, fg=title_fg)
        self.info_label.configure(bg=root_bg, fg=text_fg)
        self.footer.configure(bg=root_bg, fg=text_fg)

        # panels
        for panel in [self.main_panel, self.qr_panel, self.preview_panel]:
            panel.configure(bg=panel_bg)

        # canvas & preview
        self.canvas.configure(bg=panel_bg)
        self.preview_label.configure(bg=panel_bg)

        # buttons
        widgets = [self.btn_select, self.btn_generate, self.btn_save, self.btn_mode]
        for btn in widgets:
            btn.configure(bg=panel_bg, fg=self.accent_cyan if self.dark_mode else "#003050")

# Run app
if __name__ == "__main__":
    root = tk.Tk()
    app = FuturisticQRApp(root)
    root.mainloop()
