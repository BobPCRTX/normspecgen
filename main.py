"""NormSpecGen: pick an image and generate a normal map and a specular map for it."""
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

from map_generator import generate_normal_map, generate_specular_map


class NormSpecGenApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NormSpecGen - Normal & Specular Map Generator")
        self.geometry("900x600")
        self.minsize(700, 450)

        self.source_path = None
        self.source_image = None
        self.normalized_image = None
        self.normal_image = None
        self.specular_image = None
        self._preview_refs = {}

        self._build_ui()

    def _build_ui(self):
        controls = ttk.Frame(self, padding=10)
        controls.pack(side=tk.TOP, fill=tk.X)

        ttk.Button(controls, text="Select Image...", command=self.select_image).pack(side=tk.LEFT)
        self.path_label = ttk.Label(controls, text="No image selected")
        self.path_label.pack(side=tk.LEFT, padx=10)

        options = ttk.LabelFrame(self, text="Options", padding=10)
        options.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(0, 10))

        ttk.Label(options, text="Normal strength:").grid(row=0, column=0, sticky="w")
        self.strength_var = tk.DoubleVar(value=2.0)
        ttk.Spinbox(options, from_=0.1, to=10.0, increment=0.1, textvariable=self.strength_var, width=8).grid(row=0, column=1, padx=5)

        ttk.Label(options, text="Specular contrast:").grid(row=0, column=2, sticky="w", padx=(20, 0))
        self.contrast_var = tk.DoubleVar(value=1.5)
        ttk.Spinbox(options, from_=0.1, to=5.0, increment=0.1, textvariable=self.contrast_var, width=8).grid(row=0, column=3, padx=5)

        self.invert_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options, text="Invert specular", variable=self.invert_var).grid(row=0, column=4, padx=(20, 0))

        ttk.Button(controls, text="Generate Maps", command=self.generate_maps).pack(side=tk.RIGHT)
        ttk.Button(controls, text="Save Maps...", command=self.save_maps).pack(side=tk.RIGHT, padx=(0, 10))

        previews = ttk.Frame(self, padding=10)
        previews.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        previews.columnconfigure((0, 1, 2), weight=1)
        previews.rowconfigure(1, weight=1)

        self.preview_labels = {}
        for col, key, title in ((0, "source", "Source"), (1, "normal", "Normal Map"), (2, "specular", "Specular Map")):
            ttk.Label(previews, text=title, anchor="center").grid(row=0, column=col, sticky="ew")
            frame = ttk.Frame(previews, relief="sunken", borderwidth=1)
            frame.grid(row=1, column=col, sticky="nsew", padx=5, pady=5)
            label = ttk.Label(frame, anchor="center")
            label.pack(fill=tk.BOTH, expand=True)
            self.preview_labels[key] = label

    def select_image(self):
        path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.tga *.tif *.tiff"), ("All files", "*.*")],
        )
        if not path:
            return

        try:
            with Image.open(path) as image:
                image.load()
                has_alpha = image.mode in ("RGBA", "LA") or "transparency" in image.info
                self.normalized_image = image.convert("RGBA" if has_alpha else "RGB")
                self.source_image = self.normalized_image.copy()
        except Exception as exc:
            messagebox.showerror("Error", f"Could not open image:\n{exc}")
            return

        self.source_path = path
        self.normal_image = None
        self.specular_image = None
        self.path_label.config(text=os.path.basename(path))
        self._show_preview("source", self.source_image)
        self._show_preview("normal", None)
        self._show_preview("specular", None)

    def generate_maps(self):
        if self.normalized_image is None:
            messagebox.showwarning("No image", "Please select an image first.")
            return

        strength = self.strength_var.get()
        contrast = self.contrast_var.get()
        invert = self.invert_var.get()

        self.normal_image = generate_normal_map(self.normalized_image, strength=strength)
        self.specular_image = generate_specular_map(self.normalized_image, contrast=contrast, invert=invert)

        self._show_preview("normal", self.normal_image)
        self._show_preview("specular", self.specular_image)

    def save_maps(self):
        if self.normal_image is None or self.specular_image is None:
            messagebox.showwarning("Nothing to save", "Generate the maps before saving.")
            return

        base, _ = os.path.splitext(self.source_path)
        source_path = f"{base}_source.png"
        normal_path = f"{base}_normal.png"
        specular_path = f"{base}_specular.png"

        self.normalized_image.save(source_path, format="PNG")
        self.normal_image.save(normal_path)
        self.specular_image.save(specular_path)

        messagebox.showinfo("Saved", f"Saved:\n{source_path}\n{normal_path}\n{specular_path}")

    def _show_preview(self, key, image):
        label = self.preview_labels[key]
        if image is None:
            label.config(image="", text="")
            self._preview_refs.pop(key, None)
            return

        preview = image.copy()
        preview.thumbnail((280, 280))
        photo = ImageTk.PhotoImage(preview)
        label.config(image=photo, text="")
        self._preview_refs[key] = photo  # keep a reference so it isn't garbage collected


def main():
    app = NormSpecGenApp()
    app.mainloop()


if __name__ == "__main__":
    main()
