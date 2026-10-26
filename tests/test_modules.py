import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import modules


class LayoutTests(unittest.TestCase):
    def setUp(self):
        self.spec = modules.design()

    def test_all_layouts(self):
        for name in self.spec['modules']:
            modules.validate(self.spec, name)

    def test_same_outline_and_mounts(self):
        configs = [modules.configuration(self.spec, name) for name in self.spec['modules']]
        for config in configs[1:]:
            self.assertEqual(config['outlines']['pcb_boundary'], configs[0]['outlines']['pcb_boundary'])
            self.assertEqual({k: v for k, v in config['points']['zones'].items() if k.startswith('mount_')},
                             {k: v for k, v in configs[0]['points']['zones'].items() if k.startswith('mount_')})

    def test_missing_mirror_rejected(self):
        self.spec['modules']['module2']['rows'][0]['columns'].remove(0)
        with self.assertRaisesRegex(ValueError, 'mirrored'):
            modules.validate(self.spec, 'module2')

    def test_small_caps_rejected(self):
        self.spec['modules']['module3']['rows'][0]['cap'] = 'one_u'
        with self.assertRaisesRegex(ValueError, 'four'):
            modules.validate(self.spec, 'module3')

    def test_bottom_display_rejected(self):
        self.spec['display']['side'] = 'B'
        with self.assertRaisesRegex(ValueError, 'top face'):
            modules.validate(self.spec, 'module1')

    def test_interaction_collision_rejected(self):
        self.spec['modules']['module3']['trackpad_x'] = 24
        with self.assertRaisesRegex(ValueError, 'overlapping'):
            modules.validate(self.spec, 'module3')

    def test_cap_outside_rounded_corner_rejected(self):
        self.spec['outline']['corner'] = 5
        with self.assertRaisesRegex(ValueError, 'rounded outline'):
            modules.validate(self.spec, 'module1')

    def test_display_nets_preserved(self):
        for name in self.spec['modules']:
            config = modules.configuration(self.spec, name)
            pins = config['pcbs'][name]['footprints']['controller']['params']
            self.assertEqual([pins[f'P{i}'] for i in (1, 2, 3)], ['DISPLAY_CS', 'DISPLAY_MOSI', 'DISPLAY_SCK'])
            keys = [i for i in modules.interactions(self.spec, name) if i['kind'] == 'key']
            self.assertEqual([pins[p] for p in modules.PINS[:len(keys)]], [k['name'] for k in keys])

    def test_failed_build_preserves_previous_output(self):
        with tempfile.TemporaryDirectory() as directory:
            generated = Path(directory)
            output = generated / 'module1'
            output.mkdir()
            marker = output / 'previous'
            marker.write_text('retained')
            with patch.object(modules, 'GENERATED', generated), patch.object(modules.subprocess, 'run', side_effect=RuntimeError('failed')):
                with self.assertRaises(RuntimeError):
                    modules.build('module1')
            self.assertEqual(marker.read_text(), 'retained')

    def test_stale_output_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'module1'
            output.mkdir()
            (output / 'validation.json').write_text(json.dumps({'source_sha256': 'outdated'}))
            with patch.object(modules, 'GENERATED', Path(directory)):
                with self.assertRaisesRegex(ValueError, 'stale'):
                    modules.check('module1')


if __name__ == '__main__':
    unittest.main()
