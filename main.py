"""NormSpecGen: pick an image and generate a normal map and a specular map for it."""
import math
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

from map_generator import generate_normal_map, generate_specular_map
from version import __version__
from help_panel import create_help_panel
from save_dialog import SaveMapsDialog
from material_preview import MaterialPreview
from map_viewer import MapViewer


class NormSpecGenApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"NormSpecGen v{__version__} - Normal & Specular Map Generator")
        self.geometry("900x600")
        self.minsize(700, 450)

        self.source_path = None
        self.source_image = None
        self.normalized_image = None
        self.normal_image = None
        self.specular_image = None
        self._preview_refs = {}
        self._help_window = None
        self.maps_stale = False

        self._build_ui()
        for variable in (self.strength_var, self.contrast_var, self.invert_var):
            variable.trace_add("write", self._settings_changed)
        self.bind("<F1>", self.show_help)

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
        ttk.Button(options, text="Help (F1)", command=self.show_help).grid(row=0, column=5, padx=(10, 0))

        ttk.Button(controls, text="Generate Maps", command=self.generate_maps).pack(side=tk.RIGHT)
        self.save_button = ttk.Button(controls, text="Save Maps...", command=self.save_maps, state=tk.DISABLED)
        self.save_button.pack(side=tk.RIGHT, padx=(0, 10))
        self.status_var = tk.StringVar(value="Select an image to begin.")
        ttk.Label(self, textvariable=self.status_var, padding=(10, 4), wraplength=650).pack(fill=tk.X)

        self.preview_tabs = ttk.Notebook(self)
        self.preview_tabs.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)
        previews = ttk.Frame(self.preview_tabs, padding=10)
        self.preview_tabs.add(previews, text="Maps")
        self.material_preview = MaterialPreview(self.preview_tabs)
        self.preview_tabs.add(self.material_preview, text="Material Preview")
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
            label.config(cursor="hand2")
            label.bind("<Button-1>", lambda event, selected=key: self.open_map(selected))
        ttk.Label(previews, text="Click a map to inspect it with zoom and pan.").grid(row=2, column=0, columnspan=3, pady=4)

    def open_map(self, key):
        image = {"source": self.source_image, "normal": self.normal_image,
                 "specular": self.specular_image}[key]
        if image is not None:
            title = key.title() + (" (outdated)" if self.maps_stale and key != "source" else "")
            MapViewer(self, title, image)

    def _settings_changed(self, *args):
        if self.normal_image is not None:
            self.maps_stale = True
            self.status_var.set("Settings changed — previews are outdated. Click Generate Maps before saving.")
            self.save_button.config(state=tk.DISABLED)

    def show_help(self, event=None):
        if self._help_window is None or not self._help_window.winfo_exists():
            self._help_window = create_help_panel(self)
        else:
            self._help_window.deiconify()
            self._help_window.lift()

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
        self.maps_stale = False
        self.status_var.set("Image loaded — click Generate Maps.")
        self.save_button.config(state=tk.DISABLED)
        self.path_label.config(text=os.path.basename(path))
        self._show_preview("source", self.source_image)
        self._show_preview("normal", None)
        self._show_preview("specular", None)
        self.material_preview.set_images()

    def generate_maps(self):
        if self.normalized_image is None:
            messagebox.showwarning("No image", "Please select an image first.")
            return

        try:
            strength = self.strength_var.get()
            contrast = self.contrast_var.get()
            if not (math.isfinite(strength) and 0.1 <= strength <= 10.0
                    and math.isfinite(contrast) and 0.1 <= contrast <= 5.0):
                raise ValueError("Options out of range")
        except (tk.TclError, ValueError, OverflowError):
            messagebox.showerror(
                "Invalid options",
                "Normal strength must be a finite number from 0.1 to 10.0.\n"
                "Specular contrast must be a finite number from 0.1 to 5.0.",
            )
            return
        invert = self.invert_var.get()

        self.normal_image = generate_normal_map(self.normalized_image, strength=strength)
        self.specular_image = generate_specular_map(self.normalized_image, contrast=contrast, invert=invert)
        self.maps_stale = False
        self.status_var.set("Previews are current — ready to save.")
        self.save_button.config(state=tk.NORMAL)

        self._show_preview("normal", self.normal_image)
        self._show_preview("specular", self.specular_image)
        self.material_preview.set_images(self.normalized_image, self.normal_image, self.specular_image)

    def save_maps(self):
        if self.maps_stale:
            messagebox.showwarning("Outdated previews", "Settings changed. Click Generate Maps before saving.")
            return
        if self.normal_image is None or self.specular_image is None:
            messagebox.showwarning("Nothing to save", "Generate the maps before saving.")
            return

        selection = SaveMapsDialog(self, self.source_path).result
        if selection is None:
            return
        directory, new_name = selection
        
        if not new_name.strip():
            messagebox.showwarning("Invalid name", "Filename cannot be empty.")
            return
        
        # Sanitize the filename
        new_name = new_name.strip()
        invalid_chars = '<>:"|?*/\\'
        if any(char in new_name for char in invalid_chars) or any(ord(char) < 32 for char in new_name):
            messagebox.showerror("Invalid name", f"Filename cannot contain: {invalid_chars}")
            return
        
        # Build new paths in the selected output directory.
        source_path = os.path.join(directory, f"{new_name}_source.png")
        normal_path = os.path.join(directory, f"{new_name}_normal.png")
        specular_path = os.path.join(directory, f"{new_name}_specular.png")

        try:
            # Check every destination before writing any files. realpath handles
            # symbolic links; samefile also detects existing hard links.
            original = os.path.normcase(os.path.realpath(self.source_path))
            parent = os.path.normcase(os.path.realpath(directory or os.curdir))
            for output in (source_path, normal_path, specular_path):
                resolved = os.path.normcase(os.path.realpath(output))
                if os.path.dirname(resolved) != parent:
                    messagebox.showerror("Invalid name", "Output files must stay in the selected output directory.")
                    return
                if resolved == original or (
                    os.path.exists(output) and os.path.samefile(output, self.source_path)
                ):
                    messagebox.showerror(
                        "Source protected",
                        "An output filename matches the original image. Choose a different base filename.",
                    )
                    return
            existing = [path for path in (source_path, normal_path, specular_path) if os.path.exists(path)]
            if existing and not messagebox.askyesno(
                "Replace existing files?",
                "These files already exist:\n\n" + "\n".join(existing) + "\n\nReplace them?",
                default=messagebox.NO,
            ):
                return
            self.normalized_image.save(source_path, format="PNG")
            self.normal_image.save(normal_path)
            self.specular_image.save(specular_path)
            messagebox.showinfo("Saved", f"Saved:\n{source_path}\n{normal_path}\n{specular_path}")
        except Exception as exc:
            messagebox.showerror("Error", f"Could not save files:\n{exc}")

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
