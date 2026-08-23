# NormSpecGen

Select an image and generate a **normal map** and **specular map** from it.

## Usage

```powershell
python main.py
```

1. Click **Select Image...** and choose a source image. PNG, JPEG/JPG, BMP, TGA, and TIFF/TIF files are supported; other Pillow-supported formats can be selected through **All files**.
2. Adjust **Normal strength**, **Specular contrast**, and **Invert specular** as desired.
3. Click **Generate Maps** to preview the results.
4. Click **Save Maps...** to save `<name>_source.png`, `<name>_normal.png`, and `<name>_specular.png` next to the source image. The source reference is always saved as a PNG, regardless of the original image format.

Images are normalized in memory to RGB or RGBA before processing. Transparency is
preserved in the source reference, while the normal and specular maps are generated
from image luminance. The original image is not changed. Saving again overwrites
existing output files with the same names.

## How it works

- The **normal map** is derived from the image's luminance treated as a height field. Sobel-style gradients are computed and converted into an RGB tangent-space normal map.
- The **specular map** is a grayscale image derived from luminance with adjustable contrast/brightness, optionally inverted (useful when brighter areas should be less shiny).

## Development and Builds

See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) for source setup, validation,
and standalone Windows executable build instructions.
