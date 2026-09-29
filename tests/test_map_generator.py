import unittest

import numpy as np
from PIL import Image

from map_generator import load_grayscale, generate_normal_map, generate_specular_map


class MapGeneratorTests(unittest.TestCase):
    def test_grayscale_range_and_dtype(self):
        image = Image.fromarray(np.array([[0, 128, 255]], dtype=np.uint8))
        gray = load_grayscale(image)
        self.assertEqual(gray.dtype, np.float32)
        np.testing.assert_allclose(gray, [[0, 128 / 255, 1]])

    def test_flat_normal_points_outward_including_single_pixel(self):
        for size in ((1, 1), (1, 5), (5, 1), (4, 3)):
            with self.subTest(size=size):
                normal = generate_normal_map(Image.new('RGB', size, 'gray'))
                self.assertEqual(normal.size, size)
                vectors = np.asarray(normal).astype(float) / 255 * 2 - 1
                np.testing.assert_allclose(vectors[..., :2], 0, atol=1 / 255 + 1e-8)
                np.testing.assert_allclose(vectors[..., 2], 1)

    def test_ramp_direction_strength_and_unit_length(self):
        image = Image.fromarray(np.tile(np.array([0, 64, 128, 192, 255], dtype=np.uint8), (3, 1)))
        weak = np.asarray(generate_normal_map(image, strength=1))
        strong = np.asarray(generate_normal_map(image, strength=3))
        self.assertLess(strong[1, 2, 0], weak[1, 2, 0])
        self.assertLess(weak[1, 2, 0], 127)
        self.assertGreater(weak[1, 0, 0], 127)  # Wrapped boundary slopes back down.
        vectors = strong.astype(float) / 255 * 2 - 1
        np.testing.assert_allclose(np.linalg.norm(vectors, axis=-1), 1, atol=0.014)

    def test_vertical_ramp_affects_green(self):
        image = Image.fromarray(np.array([[0], [128], [255]], dtype=np.uint8))
        normal = generate_normal_map(image)
        self.assertLess(normal.getpixel((0, 1))[1], 127)
        self.assertEqual(normal.getpixel((0, 1))[0], 127)

    def test_specular_identity_clipping_brightness_and_inversion(self):
        image = Image.fromarray(np.array([[0, 64, 128, 192, 255]], dtype=np.uint8))
        identity = np.asarray(generate_specular_map(image, contrast=1))
        np.testing.assert_allclose(identity, np.asarray(image), atol=1)
        regular = np.asarray(generate_specular_map(image, contrast=2))
        inverted = np.asarray(generate_specular_map(image, contrast=2, invert=True))
        self.assertEqual(int(regular[0, 0]), 0)
        self.assertEqual(int(regular[0, -1]), 255)
        np.testing.assert_allclose(regular.astype(int) + inverted, 255, atol=1)
        bright = np.asarray(generate_specular_map(image, contrast=1, brightness=1))
        np.testing.assert_array_equal(bright, 255)

    def test_processing_does_not_mutate_rgba_source(self):
        image = Image.new('RGBA', (4, 4), (80, 120, 160, 100))
        before = image.tobytes()
        generate_normal_map(image, blur_radius=1)
        generate_specular_map(image, invert=True)
        self.assertEqual(image.tobytes(), before)
        self.assertEqual(image.mode, 'RGBA')


if __name__ == '__main__':
    unittest.main()
