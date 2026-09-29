# NormSpecGen

Select an image and generate a **normal map** and **specular map** from it.

## Usage

Click **Help (F1)** or press **F1** for guidance on source images, numeric
settings, map limitations, and saving. The guide can stay open while you work.

```powershell
python main.py
```

1. Click **Select Image...** and choose a source image. PNG, JPEG/JPG, BMP, TGA, and TIFF/TIF files are supported; other Pillow-supported formats can be selected through **All files**.
2. Adjust **Normal strength**, **Specular contrast**, and **Invert specular** as desired.
3. Click **Generate Maps** to preview the results.
4. Click **Save Maps...**, choose the output folder and base filename, and review the three paths before saving `<name>_source.png`, `<name>_normal.png`, and `<name>_specular.png`. The folder defaults to the source directory. The source reference is always PNG.

Changing any option marks previews as outdated and disables saving until you click
**Generate Maps** again. Existing output files require confirmation before replacement.

Images are normalized in memory to RGB or RGBA before processing. Transparency is
preserved in the source reference, while the normal and specular maps are generated
from image luminance. The original image is not changed. Saving again overwrites
existing output files with the same names only after confirmation.

## How it works

The **Maps** tab supports clicking an image to open a zoomable, pannable snapshot.
The **Material Preview** tab shows a lit plane or sphere. Drag to move its light,
toggle Normal/Specular effects, or reset the light. Display controls do not change
exported maps. The material preview is approximate and uses fixed shininess.

- The **normal map** is derived from the image's luminance treated as a height field. Sobel-style gradients are computed and converted into an RGB tangent-space normal map.
- The **specular map** is a grayscale image derived from luminance with adjustable contrast/brightness, optionally inverted (useful when brighter areas should be less shiny).

## Development and Builds

See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) for source setup, validation,
and standalone Windows executable build instructions.
