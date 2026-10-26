import hashlib
import json
from pathlib import Path
import sys
import unittest

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from anime_render import grade


class AnimeRenderTests(unittest.TestCase):
    def setUp(self):
        self.settings = json.loads((ROOT / 'anime-render/scene.json').read_text())

    def test_required_pairs(self):
        self.assertEqual(self.settings['pairs'], [[1, 1], [1, 2], [1, 3], [2, 3]])

    def test_actual_40mm_camera(self):
        self.assertEqual(self.settings['camera']['lens_mm'], 40)
        self.assertEqual(self.settings['camera']['sensor_width_mm'], 36)
        self.assertEqual(self.settings['camera']['sensor_height_mm'], 24)
        self.assertEqual(self.settings['image']['width'] / self.settings['image']['height'], 1.5)

    def test_single_background_provenance(self):
        background = ROOT / 'anime-render/background.png'
        provenance = json.loads((ROOT / 'anime-render/background-provenance.json').read_text())
        self.assertEqual(hashlib.sha256(background.read_bytes()).hexdigest(), provenance['output']['sha256'])
        self.assertEqual(provenance['camera']['position_mm'], self.settings['camera']['position_mm'])
        self.assertEqual(provenance['camera']['target_mm'], self.settings['camera']['target_mm'])

    def test_grading_preserves_opaque_geometry(self):
        pixels = np.array([[[0, 0, 0, 255], [180, 120, 80, 255], [0, 0, 0, 0]]], dtype=np.uint8)
        output = np.asarray(grade(Image.fromarray(pixels), self.settings['grading']))
        self.assertEqual(output[0, 0, 3], 255)
        self.assertEqual(output[0, 1, 3], 255)
        self.assertEqual(output[0, 2, 3], 0)
        self.assertFalse(np.array_equal(output[0, 1, :3], pixels[0, 1, :3]))

    def test_battery_clear_of_antenna_reservation(self):
        for number in (1, 2, 3):
            data = json.loads((ROOT / f'anime-render/generated/native/module{number}/components.json').read_text())
            battery = next(i for i in data['instances'] if i['name'] == 'protected_battery')
            x, y, _ = battery['position_mm']
            w, h, _ = battery['size_mm']
            bounds = [100 + x - w / 2, 100 - y - h / 2, 100 + x + w / 2, 100 - y + h / 2]
            routing = json.loads((ROOT / f'boards/modules/generated/module{number}/routing.json').read_text())
            left, top, right, bottom = routing['antenna_keepout_kicad']
            self.assertTrue(bounds[2] <= left - 5 or bounds[0] >= right + 5 or bounds[3] <= top - 5 or bounds[1] >= bottom + 5)

    def test_component_models_include_underside_hardware(self):
        for number in (1, 2, 3):
            path = ROOT / f'anime-render/generated/native/module{number}/components.json'
            data = json.loads(path.read_text())
            names = {item['name'] for item in data['instances']}
            self.assertTrue({'controller', 'display', 'display_socket', 'protected_battery', 'power_switch', 'reset_switch', 'battery_connector'} <= names)
            cap_count = sum(name.endswith('_cap') for name in names)
            self.assertEqual(cap_count, {1: 12, 2: 6, 3: 4}[number])
            self.assertEqual(sum(name.endswith('_switch') and name.startswith('key_') for name in names), cap_count)
            if number == 1:
                parts = {item['name']: item for item in data['instances']}
                self.assertEqual(parts['display']['rotation_degrees'][0], 180)
                self.assertEqual(parts['display_socket']['rotation_degrees'][0], 180)
                self.assertLess(parts['display']['position_mm'][2], 0)
                self.assertEqual(data['preview_pcb_top_z_mm'], 13)
                electrical = json.loads((ROOT / 'boards/modules/generated/module1/electrical.json').read_text())
                mcu = next(f for f in electrical['footprints'] if f['reference'] == 'MCU1')
                self.assertAlmostEqual(parts['controller']['position_mm'][0], mcu['position'][0] - 100)
                self.assertEqual(parts['controller']['rotation_degrees'][2], mcu['rotation_degrees'])
            if number == 3:
                self.assertTrue({'TPS43_module', 'TPS43_overlay', 'TPS43_adapter_header'} <= names)


if __name__ == '__main__':
    unittest.main()
