import os
from pathlib import Path
import tempfile
import tkinter as tk
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from PIL import Image

from main import NormSpecGenApp


class AppTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.source = self.directory / 'input.png'
        image = Image.new('RGBA', (3, 3), (80, 120, 160, 100))
        image.save(self.source)
        self.app = SimpleNamespace(
            source_path=str(self.source), normalized_image=image,
            normal_image=Image.new('RGB', (3, 3), (127, 127, 255)),
            specular_image=Image.new('L', (3, 3), 100),
            _show_preview=Mock(),
            maps_stale=False, status_var=Mock(), save_button=Mock(),
            material_preview=Mock(),
        )
        for name in ('showerror', 'showwarning', 'showinfo', 'askyesno'):
            patcher = patch('main.messagebox.' + name)
            setattr(self, name, patcher.start())
            self.addCleanup(patcher.stop)

    def save(self, name, folder=None):
        result = None if name is None else (str(folder or self.directory), name)
        with patch('main.SaveMapsDialog', return_value=SimpleNamespace(result=result)):
            NormSpecGenApp.save_maps(self.app)

    def test_save_to_selected_folder(self):
        folder = self.directory / 'exports'
        folder.mkdir()
        self.save('output', folder)
        self.assertEqual(len(list(folder.glob('*.png'))), 3)
        self.assertFalse((self.directory / 'output_normal.png').exists())

    def test_declining_overwrite_writes_nothing(self):
        target = self.directory / 'output_specular.png'
        target.write_bytes(b'keep me')
        self.askyesno.return_value = False
        self.save('output')
        self.assertEqual(target.read_bytes(), b'keep me')
        self.assertFalse((self.directory / 'output_source.png').exists())
        self.assertIn(str(target), self.askyesno.call_args.args[1])
        self.showinfo.assert_not_called()

    def test_accepting_overwrite_saves_maps(self):
        target = self.directory / 'output_specular.png'
        target.write_bytes(b'replace me')
        self.askyesno.return_value = True
        self.save('output')
        with Image.open(target) as saved:
            self.assertEqual(saved.tobytes(), self.app.specular_image.tobytes())
        self.askyesno.assert_called_once()

    def test_changed_settings_block_save_until_regeneration(self):
        self.prepare_options()
        NormSpecGenApp._settings_changed(self.app)
        self.assertTrue(self.app.maps_stale)
        with patch('main.SaveMapsDialog') as dialog:
            NormSpecGenApp.save_maps(self.app)
            dialog.assert_not_called()
        self.app.save_button.config.assert_called_with(state=tk.DISABLED)
        NormSpecGenApp.generate_maps(self.app)
        self.assertFalse(self.app.maps_stale)
        self.app.save_button.config.assert_called_with(state=tk.NORMAL)
        self.save('current')
        self.assertTrue((self.directory / 'current_normal.png').exists())

    def test_save_preserves_source_and_alpha(self):
        original = self.source.read_bytes()
        self.save('output')
        self.assertEqual(self.source.read_bytes(), original)
        for suffix, expected in (
            ('source', self.app.normalized_image),
            ('normal', self.app.normal_image),
            ('specular', self.app.specular_image),
        ):
            with Image.open(self.directory / ('output_' + suffix + '.png')) as result:
                self.assertEqual(result.mode, expected.mode)
                self.assertEqual(result.size, expected.size)
                self.assertEqual(result.tobytes(), expected.tobytes())
        self.showinfo.assert_called_once()

    def test_each_source_collision_rejected_before_any_write(self):
        for suffix in ('source', 'normal', 'specular'):
            with self.subTest(suffix=suffix):
                source = self.directory / ('brick_' + suffix + '.png')
                self.app.normalized_image.save(source)
                self.app.source_path = str(source)
                before = {p.name: p.read_bytes() for p in self.directory.iterdir()}
                self.save('brick')
                self.assertEqual(before, {p.name: p.read_bytes() for p in self.directory.iterdir()})
        self.assertEqual(self.showerror.call_count, 3)

    def test_invalid_names_and_cancel_write_nothing(self):
        for name in (None, '', '  ', '../escaped', '..\\escaped',
                     'nested/file', 'nested\\file', '/absolute', 'C:\\absolute',
                     'bad:name', 'bad\x00name'):
            with self.subTest(name=name):
                self.save(name)
                self.assertEqual(list(self.directory.iterdir()), [self.source])
        self.showinfo.assert_not_called()

    def test_hard_link_to_source_is_protected(self):
        target = self.directory / 'output_normal.png'
        os.link(self.source, target)
        before = self.source.read_bytes()
        self.save('output')
        self.assertEqual(self.source.read_bytes(), before)
        self.assertFalse((self.directory / 'output_source.png').exists())
        self.showerror.assert_called_once()

    def prepare_options(self):
        # Tcl variables exercise the same conversion as the editable spinboxes,
        # without creating a Tk window or requiring a display.
        self.interp = tk.Tcl()
        self.app.strength_var = tk.DoubleVar(self.interp, value=2)
        self.app.contrast_var = tk.DoubleVar(self.interp, value=1.5)
        self.app.invert_var = tk.BooleanVar(self.interp, value=False)

    def test_invalid_options_preserve_previous_maps(self):
        self.prepare_options()
        previous = (self.app.normal_image, self.app.specular_image)
        for field in ('strength_var', 'contrast_var'):
            for value in ('', 'abc', 'Inf', '-Inf', 'NaN', '-1', '0', '0.09', '11'):
                with self.subTest(field=field, value=value):
                    self.app.strength_var.set(2)
                    self.app.contrast_var.set(1.5)
                    self.interp.setvar(str(getattr(self.app, field)), value)
                    self.showerror.reset_mock()
                    NormSpecGenApp.generate_maps(self.app)
                    self.showerror.assert_called_once()
                    self.assertEqual((self.app.normal_image, self.app.specular_image), previous)
        self.app._show_preview.assert_not_called()

    def test_valid_option_boundaries_generate_maps(self):
        self.prepare_options()
        for strength, contrast in ((0.1, 0.1), (10, 5), (2, 1.5)):
            self.app.strength_var.set(strength)
            self.app.contrast_var.set(contrast)
            NormSpecGenApp.generate_maps(self.app)
            self.assertEqual(self.app.normal_image.mode, 'RGB')
            self.assertEqual(self.app.specular_image.mode, 'L')
            self.assertEqual(self.app.normal_image.size, (3, 3))
        self.showerror.assert_not_called()

    def test_missing_images_show_warnings(self):
        self.app.normalized_image = None
        NormSpecGenApp.generate_maps(self.app)
        self.app.normal_image = None
        NormSpecGenApp.save_maps(self.app)
        self.assertEqual(self.showwarning.call_count, 2)


if __name__ == '__main__':
    unittest.main()
