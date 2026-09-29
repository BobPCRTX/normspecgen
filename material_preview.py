"""Small CPU material renderer and its interactive Tk view."""
import tkinter as tk
from tkinter import ttk

import numpy as np
from PIL import Image, ImageTk


def render_material(source, normal, specular, size=(480, 320), shape="Plane",
                    light=(0.4, -0.4, 1.0), use_normal=True, use_specular=True):
    """Render a qualitative, fixed-shininess material with a tangent-space normal map."""
    width, height = size
    yy, xx = np.mgrid[:height, :width].astype(np.float32)
    x = (xx + 0.5 - width / 2) / (min(size) * 0.45)
    y = (yy + 0.5 - height / 2) / (min(size) * 0.45)
    sphere = shape == "Sphere"
    if sphere:
        mask = x*x + y*y <= 1
        z = np.sqrt(np.maximum(0, 1 - x*x - y*y))
        u = 0.5 + np.arctan2(x, z) / (2*np.pi)
        v = 0.5 + np.arcsin(np.clip(y, -1, 1)) / np.pi
        base = np.stack((x, y, z), axis=-1)
        tangent = np.stack((z, np.zeros_like(x), -x), axis=-1)
        tangent /= np.maximum(np.linalg.norm(tangent, axis=-1, keepdims=True), 1e-6)
        bitangent = np.cross(base, tangent)
    else:
        # Preserve image proportions on the plane instead of stretching it.
        fit = min(width / source.width, height / source.height) * 0.9
        u = (xx + 0.5 - width/2) / (source.width * fit) + 0.5
        v = (yy + 0.5 - height/2) / (source.height * fit) + 0.5
        mask = (u >= 0) & (u <= 1) & (v >= 0) & (v <= 1)

    def sample(image, mode):
        # Bound intermediate texture memory for very large input images.
        texture = image.convert(mode)
        texture.thumbnail((1024, 1024))
        array = np.asarray(texture, dtype=np.float32) / 255
        ix = np.clip((u * texture.width).astype(int), 0, texture.width-1)
        iy = np.clip((v * texture.height).astype(int), 0, texture.height-1)
        return array[iy, ix]

    color = sample(source, "RGBA")
    n = sample(normal, "RGB") * 2 - 1 if use_normal else np.broadcast_to([0., 0., 1.], (height, width, 3))
    if sphere:
        n = tangent*n[..., 0:1] + bitangent*n[..., 1:2] + base*n[..., 2:3]
    n = n / np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-6)
    direction = np.array(light, dtype=float)
    direction /= max(np.linalg.norm(direction), 1e-6)
    diffuse = np.maximum(0, n @ direction)
    halfway = direction + [0, 0, 1]
    halfway /= max(np.linalg.norm(halfway), 1e-6)
    shine = np.maximum(0, n @ halfway) ** 40
    spec = sample(specular, "L") if use_specular else 0
    rgb = color[..., :3] * (0.2 + 0.8*diffuse[..., None])
    rgb += (0.65 * shine * spec * (diffuse > 0))[..., None]
    alpha = color[..., 3:4] * mask[..., None]
    rgb = rgb*alpha + np.array([0.12, 0.13, 0.15])*(1-alpha)
    return Image.fromarray(np.uint8(np.clip(rgb, 0, 1)*255))


class MaterialPreview(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=8)
        self.images = None
        self.light = (0.4, -0.4, 1.0)
        self.pending = None
        bar = ttk.Frame(self)
        bar.pack(fill=tk.X)
        self.shape = tk.StringVar(value="Plane")
        self.normals = tk.BooleanVar(value=True)
        self.specular = tk.BooleanVar(value=True)
        ttk.Label(bar, text="Surface:").pack(side=tk.LEFT)
        ttk.Combobox(bar, textvariable=self.shape, values=("Plane", "Sphere"), state="readonly", width=8).pack(side=tk.LEFT, padx=6)
        for label, variable in (("Normal", self.normals), ("Specular", self.specular)):
            ttk.Checkbutton(bar, text=label, variable=variable).pack(side=tk.LEFT, padx=6)
        ttk.Button(bar, text="Reset light", command=self.reset_light).pack(side=tk.LEFT, padx=6)
        ttk.Label(self, text="Drag across the surface to move the light.").pack(anchor="w", pady=4)
        self.canvas = tk.Canvas(self, background="#1f2126", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        ttk.Label(self, text="Approximate preview; appearance may differ in your target application.", wraplength=620).pack(anchor="w", pady=4)
        self.canvas.bind("<Configure>", self.schedule)
        self.canvas.bind("<Button-1>", self.move_light)
        self.canvas.bind("<B1-Motion>", self.move_light)
        for variable in (self.shape, self.normals, self.specular):
            variable.trace_add("write", self.schedule)

    def set_images(self, source=None, normal=None, specular=None):
        self.images = None
        if normal is not None and specular is not None:
            self.images = []
            for image in (source, normal, specular):
                preview = image.copy()
                preview.thumbnail((1024, 1024))
                self.images.append(preview)
        self.schedule()

    def reset_light(self):
        self.light = (0.4, -0.4, 1.0)
        self.schedule()

    def move_light(self, event):
        self.light = (4*(event.x/max(1, self.canvas.winfo_width())-0.5),
                      4*(event.y/max(1, self.canvas.winfo_height())-0.5), 1)
        self.schedule()

    def schedule(self, *args):
        if self.pending is None:
            self.pending = self.after(35, self.draw)

    def draw(self):
        self.pending = None
        self.canvas.delete("all")
        width, height = max(1, self.canvas.winfo_width()), max(1, self.canvas.winfo_height())
        if self.images is None:
            self.canvas.create_text(width/2, height/2, text="Generate maps to see the material preview.", fill="white")
            return
        scale = min(1, 640/width, 480/height)
        rendered = render_material(*self.images, size=(max(1, int(width*scale)), max(1, int(height*scale))),
                                   shape=self.shape.get(), light=self.light,
                                   use_normal=self.normals.get(), use_specular=self.specular.get())
        self.photo = ImageTk.PhotoImage(rendered.resize((width, height), Image.Resampling.BILINEAR))
        self.canvas.create_image(width/2, height/2, image=self.photo)

    def destroy(self):
        if self.pending is not None:
            self.after_cancel(self.pending)
        super().destroy()
