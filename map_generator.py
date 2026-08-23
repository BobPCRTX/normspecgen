"""Core image processing: generate normal maps and specular maps from a source image."""
import numpy as np
from PIL import Image, ImageFilter


def load_grayscale(image: Image.Image) -> np.ndarray:
    """Return a float32 grayscale array in range [0, 1] from a PIL image."""
    gray = image.convert("L")
    return np.asarray(gray, dtype=np.float32) / 255.0


def generate_normal_map(image: Image.Image, strength: float = 2.0, blur_radius: float = 0.0) -> Image.Image:
    """Generate a tangent-space normal map from the luminance (height) of an image."""
    source = image
    if blur_radius > 0:
        source = source.filter(ImageFilter.GaussianBlur(blur_radius))

    height = load_grayscale(source)

    # Sobel-style gradients (wrap at edges so tiling textures stay seamless).
    gx = (np.roll(height, -1, axis=1) - np.roll(height, 1, axis=1)) * strength
    gy = (np.roll(height, -1, axis=0) - np.roll(height, 1, axis=0)) * strength

    normal_x = -gx
    normal_y = -gy
    normal_z = np.ones_like(height)

    length = np.sqrt(normal_x ** 2 + normal_y ** 2 + normal_z ** 2)
    normal_x /= length
    normal_y /= length
    normal_z /= length

    # Map from [-1, 1] to [0, 255] for standard RGB normal map encoding.
    r = ((normal_x * 0.5 + 0.5) * 255).astype(np.uint8)
    g = ((normal_y * 0.5 + 0.5) * 255).astype(np.uint8)
    b = ((normal_z * 0.5 + 0.5) * 255).astype(np.uint8)

    normal_map = np.stack([r, g, b], axis=-1)
    return Image.fromarray(normal_map, mode="RGB")


def generate_specular_map(
    image: Image.Image,
    contrast: float = 1.5,
    brightness: float = 0.0,
    invert: bool = False,
) -> Image.Image:
    """Generate a grayscale specular map by boosting contrast of the image luminance."""
    gray = load_grayscale(image)

    # Apply contrast/brightness around the midpoint, then clamp to valid range.
    spec = (gray - 0.5) * contrast + 0.5 + brightness
    spec = np.clip(spec, 0.0, 1.0)

    if invert:
        spec = 1.0 - spec

    spec_map = (spec * 255).astype(np.uint8)
    return Image.fromarray(spec_map, mode="L")
