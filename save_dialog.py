"""Choose and preview the three map destinations before saving."""
import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk


class SaveMapsDialog(simpledialog.Dialog):
    def __init__(self, parent, source_path):
        self.source_path = source_path
        super().__init__(parent, "Save Maps")

    def body(self, master):
        self.folder = tk.StringVar(master, value=os.path.dirname(os.path.abspath(self.source_path)))
        self.name = tk.StringVar(master, value=os.path.splitext(os.path.basename(self.source_path))[0])
        ttk.Label(master, text="Output folder:").grid(row=0, column=0, sticky="w")
        ttk.Entry(master, textvariable=self.folder, width=60).grid(row=1, column=0, sticky="ew")
        ttk.Button(master, text="Browse...", command=self.browse).grid(row=1, column=1, padx=8)
        ttk.Label(master, text="Base filename (without extension):").grid(row=2, column=0, sticky="w", pady=(12, 0))
        entry = ttk.Entry(master, textvariable=self.name, width=60)
        entry.grid(row=3, column=0, sticky="ew")
        self.preview = tk.StringVar(master)
        ttk.Label(master, textvariable=self.preview, wraplength=560, justify=tk.LEFT).grid(row=4, column=0, columnspan=2, sticky="w", pady=12)
        self.folder.trace_add("write", self.refresh)
        self.name.trace_add("write", self.refresh)
        self.refresh()
        return entry

    def browse(self):
        folder = filedialog.askdirectory(parent=self, initialdir=self.folder.get(), title="Choose output folder")
        if folder:
            self.folder.set(folder)

    def refresh(self, *args):
        paths = [os.path.join(self.folder.get(), self.name.get().strip() + suffix)
                 for suffix in ("_source.png", "_normal.png", "_specular.png")]
        self.preview.set("Files to save:\n" + "\n".join(paths) +
                         "\n\nExisting files will require confirmation before replacement.")

    def validate(self):
        if not os.path.isdir(self.folder.get()):
            messagebox.showerror("Invalid folder", "Choose an existing output folder.", parent=self)
            return False
        name = self.name.get().strip()
        if not name or any(c in '<>:"|?*/\\' or ord(c) < 32 for c in name):
            messagebox.showerror("Invalid name", "Enter a base filename without path separators or special characters.", parent=self)
            return False
        return True

    def apply(self):
        self.result = (os.path.abspath(self.folder.get()), self.name.get().strip())

    def buttonbox(self):
        box = ttk.Frame(self)
        ttk.Button(box, text="Save", command=self.ok).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(box, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=5, pady=5)
        box.pack()
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
