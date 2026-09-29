"""Zoomable map inspection using viewport-sized crops."""
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


class MapViewer(tk.Toplevel):
    def __init__(self, parent, title, image):
        super().__init__(parent)
        self.title(title + " — map snapshot")
        self.geometry("800x650")
        self.image = image.convert("RGBA")
        self.zoom = 1.0
        self.offset = [0., 0.]
        bar = ttk.Frame(self, padding=6)
        bar.pack(fill=tk.X)
        for label, command in (("−", lambda: self.scale(1/1.25)), ("+", lambda: self.scale(1.25)),
                               ("100%", self.actual), ("Fit", self.fit)):
            ttk.Button(bar, text=label, command=command).pack(side=tk.LEFT, padx=3)
        self.info = ttk.Label(bar)
        self.info.pack(side=tk.LEFT, padx=10)
        ttk.Label(self, text="Mouse wheel: zoom • Drag: pan • Snapshot of the map when opened").pack()
        self.canvas = tk.Canvas(self, background="#333333", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda e: self.draw())
        self.canvas.bind("<MouseWheel>", lambda e: self.scale(1.25 if e.delta > 0 else 1/1.25))
        self.canvas.bind("<Button-1>", self.start_pan)
        self.canvas.bind("<B1-Motion>", self.pan)
        self.bind("<Escape>", lambda e: self.destroy())
        self.after_idle(self.fit)

    def start_pan(self, event):
        self.anchor = (event.x, event.y)

    def pan(self, event):
        self.offset[0] += event.x-self.anchor[0]
        self.offset[1] += event.y-self.anchor[1]
        self.anchor = (event.x, event.y)
        self.draw()

    def scale(self, factor):
        old = self.zoom
        self.zoom = min(16, max(0.01, old*factor))
        cx, cy = self.canvas.winfo_width()/2, self.canvas.winfo_height()/2
        self.offset = [cx+(self.offset[0]-cx)*self.zoom/old, cy+(self.offset[1]-cy)*self.zoom/old]
        self.draw()

    def actual(self):
        self.scale(1/self.zoom)

    def fit(self):
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        self.zoom = min(w/self.image.width, h/self.image.height, 1)
        self.offset = [(w-self.image.width*self.zoom)/2, (h-self.image.height*self.zoom)/2]
        self.draw()

    def draw(self):
        w, h = max(1, self.canvas.winfo_width()), max(1, self.canvas.winfo_height())
        viewport = self.image.transform(
            (w, h), Image.Transform.AFFINE,
            (1/self.zoom, 0, -self.offset[0]/self.zoom, 0, 1/self.zoom, -self.offset[1]/self.zoom),
            resample=Image.Resampling.NEAREST)
        self.photo = ImageTk.PhotoImage(viewport)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        self.info.config(text=f"{self.zoom:.0%} · {self.image.width} × {self.image.height}")
