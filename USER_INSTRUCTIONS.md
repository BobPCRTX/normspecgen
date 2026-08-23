# NormSpecGen - User Instructions (Simple Guide)

This guide is for anyone who just wants to generate normal and specular maps.
No coding or technical setup is required if you use the `.exe`.

## What You Need

- A Windows computer
- The program file: `NormSpecGen.exe`

## How to Start the Program

1. Double-click `NormSpecGen.exe`.
2. Wait a few seconds for the window to open.

## If Windows Shows a Warning

Sometimes Windows may show a SmartScreen warning the first time.

1. Click **More info**.
2. Click **Run anyway**.

This can happen with new apps that are not digitally signed.

## How to Use It

1. Click **Select Image...** and choose the picture you want to make maps from. PNG,
   JPEG/JPG, BMP, TGA, and TIFF/TIF files are supported. Other image formats supported
   by Pillow can also be selected through **All files**.
2. The image is normalized in memory before processing. RGB images remain RGB, while
   images with transparency are kept as RGBA. The original file is never changed.
3. (Optional) Adjust the sliders:
   - **Normal strength**: how strong the bumps/dents look in the normal map. Higher = more exaggerated.
   - **Specular contrast**: how much the shiny/dull areas stand out.
   - **Invert specular**: check this if you want bright areas to be less shiny instead of more shiny.
4. Click **Generate Maps** to preview the normal map and specular map next to your original image.
5. Click **Save Maps...** to save three PNG files next to your original file, named:
   - `yourfile_source.png`
   - `yourfile_normal.png`
   - `yourfile_specular.png`

The source reference is always saved as PNG, even when the selected image was a JPEG,
TGA, TIFF, or another format. Existing files with these names are overwritten when
you save again.

## Tips

- If the normal map looks too flat, increase **Normal strength**.
- If the normal map looks too noisy/jagged, try a smaller/blurrier source image or lower the strength.
- The specular map is just a grayscale image - white = shiny, black = dull. You can touch it up afterward in any image editor.
- Transparency is preserved in `yourfile_source.png`, but normal and specular maps are generated from the image luminance.

## Developer and Build Instructions

Source setup and instructions for building the standalone `.exe` are in
[BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md).
