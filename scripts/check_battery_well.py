import FreeCAD as App
import Part

from pathlib import Path
import json
import sys


def normalized_board(path, bottom):
    shape = Part.read(str(path))
    matrix = App.Matrix()
    matrix.A33 = 1.6 / shape.BoundBox.ZLength
    shape = shape.transformGeometry(matrix)
    shape.translate(App.Vector(0, 0, bottom - shape.BoundBox.ZMin))
    return shape


def main():
    output, stage = map(Path, sys.argv[1:])
    geometry = json.loads((output / 'board_geometry.json').read_text())
    well, pack = geometry['battery_well'], geometry['battery']
    x, y, length, width, chamfer = (well[k] for k in ('x', 'y', 'length', 'width', 'corner_chamfer'))
    points = [(x + chamfer, y), (x + length - chamfer, y), (x + length, y + chamfer),
              (x + length, y + width - chamfer), (x + length - chamfer, y + width),
              (x + chamfer, y + width), (x, y + width - chamfer), (x, y + chamfer)]
    wire = Part.makePolygon([App.Vector(px, py, -3.2) for px, py in points + points[:1]])
    floor = Part.Face(wire).extrude(App.Vector(0, 0, 1.6))
    empty_well = floor.copy()
    empty_well.translate(App.Vector(0, 0, 1.6))
    main_pcb = normalized_board(stage / 'macropad.step', -1.6)
    baseplate = normalized_board(stage / 'baseplate.step', -3.2)
    cutout_overlap = main_pcb.common(empty_well).Volume
    floor_missing = floor.cut(baseplate).Volume
    battery = Part.makeBox(pack['length'], pack['width'], pack['thickness'],
                           App.Vector(pack['x'] - pack['length'] / 2,
                                      pack['y'] - pack['width'] / 2, pack['bottom_z']))
    battery_overlap = main_pcb.common(battery).Volume + baseplate.common(battery).Volume
    if max(cutout_overlap, floor_missing, battery_overlap) > 0.0001:
        raise RuntimeError(f'Battery well STEP checks failed: {cutout_overlap}, {floor_missing}, {battery_overlap}')
    for name, shape in (('main_pcb', main_pcb), ('baseplate', baseplate)):
        if abs(shape.BoundBox.XLength - geometry['width']) > 0.001 or abs(shape.BoundBox.YLength - geometry['height']) > 0.001:
            raise RuntimeError(name + ' outer dimensions changed')
    report = {'passed': True, 'native_step_main_well_overlap_mm3': round(cutout_overlap, 7),
              'native_step_missing_baseplate_floor_mm3': round(floor_missing, 7),
              'native_step_pack_pcb_overlap_mm3': round(battery_overlap, 7),
              'continuous_baseplate_floor_volume_mm3': round(floor.Volume, 5),
              'well': well, 'battery': pack,
              'pcb_stack_mm': {'main_pcb': [-1.6, 0], 'baseplate': [-3.2, -1.6]},
              'pcb_thickness_note': 'Native KiCad body normalized to nominal 1.6 mm FR4, matching the touching stack.'}
    (output / 'checks/battery-well.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Native KiCad STEP confirms the battery well, continuous baseplate floor and pack clearance')


if __name__ == '__main__':
    main()
