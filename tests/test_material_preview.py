import unittest
import numpy as np
from PIL import Image
from material_preview import render_material


class MaterialTests(unittest.TestCase):
    def setUp(self):
        self.source = Image.new('RGB', (32, 16), (100, 80, 60))
        self.normal = Image.new('RGB', (32, 16), (240, 128, 180))
        self.specular = Image.new('L', (32, 16), 255)

    def render(self, **options):
        return np.asarray(render_material(self.source, self.normal, self.specular, size=(80, 60), **options))

    def test_shapes_are_distinct_and_preserve_output_size(self):
        plane = self.render()
        sphere = self.render(shape='Sphere')
        self.assertEqual(plane.shape, (60, 80, 3))
        self.assertFalse(np.array_equal(plane, sphere))
        np.testing.assert_array_equal(sphere[0, 0], [30, 33, 38])

    def test_normal_toggle_and_light_change_result(self):
        self.assertFalse(np.array_equal(self.render(), self.render(use_normal=False)))
        self.assertFalse(np.array_equal(self.render(light=(1, 0, 1)), self.render(light=(-1, 0, 1))))

    def test_specular_adds_highlights(self):
        on = self.render(use_normal=False, light=(0, 0, 1))
        off = self.render(use_normal=False, light=(0, 0, 1), use_specular=False)
        self.assertTrue(np.all(on >= off))
        self.assertTrue(np.any(on > off))

    def test_transparent_source_shows_background(self):
        self.source = Image.new('RGBA', (32, 16), (255, 0, 0, 0))
        np.testing.assert_array_equal(self.render()[30, 40], [30, 33, 38])

    def test_source_maps_are_unchanged(self):
        before = [im.tobytes() for im in (self.source, self.normal, self.specular)]
        self.render(shape='Sphere')
        self.assertEqual(before, [im.tobytes() for im in (self.source, self.normal, self.specular)])
