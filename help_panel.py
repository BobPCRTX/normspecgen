"""In-app guidance for preparing images and adjusting map settings."""

import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from version import __version__


HELP_SECTIONS = (
    ("Preview tabs",
     "Maps shows the source, normal, and specular images. Click one to open a "
     "snapshot with zoom and pan: use the mouse wheel or +/− to zoom, drag to pan, "
     "and use Fit or 100% to reset the view. Reopen the snapshot after generating "
     "new maps.\n\n"
     "Material Preview applies the generated maps to a plane or sphere. Drag "
     "across the surface to move the light, or use Reset light. Toggle Normal "
     "and Specular to compare their effects. These display controls do not "
     "change exported maps. The preview uses simplified lighting and fixed "
     "shininess; appearance may differ in your target application. Both tabs "
     "show the last generated maps until you generate again."),
    ("Quick start",
     "Select Image → adjust the options → Generate Maps → Save Maps.\n"
     "After changing any option, click Generate Maps again before saving. "
     "A status message marks outdated previews, and saving is disabled until "
     "you generate maps with the new settings."),
    ("Choose a useful source image",
     "Image brightness is treated as height: lighter areas are higher and darker "
     "areas are lower. The normal map describes changes in that height, so a "
     "uniform area stays flat regardless of its brightness.\n\n"
     "Start with a clean image whose light and dark details represent the surface "
     "you want. Shadows, highlights, JPEG artifacts, and noise can become unwanted "
     "bumps. A photograph is a starting point, not a measured height map. "
     "If details look rough, try a cleaner or gently blurred source image."),
    ("Normal strength · 0.1–10.0 · default 2.0",
     "Lower values make slopes gentler; higher values exaggerate them. "
     "Start at 2.0, then adjust gradually. Increasing strength does not add "
     "detail that is missing from the source.\n\n"
     "If the result looks too harsh or noisy, lower the strength. Inspect the "
     "normal map on your material under lighting to judge the effect; the "
     "colored preview alone does not show the final surface appearance."),
    ("Specular contrast · 0.1–5.0 · default 1.5",
     "The specular output is grayscale: white represents a stronger specular "
     "response and black a weaker one when used in a compatible material.\n\n"
     "Below 1.0: bring values closer to mid-gray.\n"
     "At 1.0: preserve the source luminance.\n"
     "Above 1.0: push bright areas brighter and dark areas darker.\n\n"
     "High contrast can clip details to solid black or white. If you lose "
     "subtle variations, reduce contrast. Only finite numbers within the "
     "displayed ranges are accepted for both controls."),
    ("Invert specular",
     "Reverses the specular map after contrast is applied. Use it when brighter "
     "source areas should have a weaker specular response. It does not change "
     "the normal map.\n\n"
     "Source brightness does not determine a real material's shininess. Treat "
     "this map as a starting point for editing. It is not a metallic or "
     "roughness map; check which inputs your material expects."),
    ("Edges, transparency, and previews",
     "Normal-map processing wraps across opposite image edges for tiling "
     "textures. If those edges do not match, the result can show a strong seam. "
     "Prepare matching edges when you want a repeating texture.\n\n"
     "Transparency is preserved in the source PNG reference. Normal and "
     "specular maps use color luminance, including colors in transparent "
     "pixels, and have no transparency.\n\n"
     "Previews are reduced to fit; saved maps retain the source pixel dimensions. "
     "Inspect exported maps at full size for fine detail."),
    ("Saving your maps",
     "Enter a base filename to save <name>_source.png, <name>_normal.png, and "
     "<name>_specular.png. The save dialog shows all three paths; use Browse "
     "to choose an output folder. It defaults to the source folder. The source "
     "reference is always PNG. Use a filename, not a folder path.\n\n"
     "The selected original is protected from being overwritten. Other existing "
     "output files with matching names are listed for confirmation before replacement. "
     "Choose a different base name to keep multiple versions."),
)


def create_help_panel(parent):
    """Open a nonmodal, scrollable guide that can stay beside the previews."""
    window = tk.Toplevel(parent)
    window.title(f"NormSpecGen v{__version__} — Help")
    window.geometry("640x620")
    window.minsize(420, 320)
    window.transient(parent)

    content = ttk.Frame(window, padding=12)
    content.pack(fill=tk.BOTH, expand=True)
    ttk.Label(content, text="Getting useful maps", font="TkHeadingFont").pack(anchor="w", pady=(0, 8))
    text = ScrolledText(content, wrap=tk.WORD, font="TkDefaultFont", padx=12, pady=10)
    text.pack(fill=tk.BOTH, expand=True)
    text.tag_configure("heading", font="TkHeadingFont", spacing1=12, spacing3=6)
    for heading, body in HELP_SECTIONS:
        text.insert(tk.END, heading + "\n", "heading")
        text.insert(tk.END, body + "\n\n")
    text.configure(state=tk.DISABLED)
    ttk.Button(content, text="Close", command=window.destroy).pack(anchor="e", pady=(10, 0))
    window.bind("<Escape>", lambda event: window.destroy())
    return window
