import FreeCAD as App
import Import
import Part

from pathlib import Path
import hashlib
import json
import math
import re
import sys

from build import ROOT, P, REF, V, box, cylinder, nut, union, write_wrl


def model_points(path):
    text = path.read_text()
    groups = re.findall(r'point\s*\[([^\]]+)\]', text)
    result = []
    for group in groups:
        values = [float(x) * 2.54 for x in re.findall(r'[-+]?\d*\.?\d+(?:[Ee][-+]?\d+)?', group)]
        result.extend(zip(values[0::3], values[1::3], values[2::3]))
    return result


def main():
    stage = Path(sys.argv[1])
    parts = [Part.read(str(ROOT / 'generated' / (name + '.step'))) for name in ('left_bumper', 'right_bumper')]
    case = union(parts)
    checks = []
    for source, expected in REF['source_files'].items():
        actual = hashlib.sha256((ROOT.parent / source).read_bytes()).hexdigest()
        if actual != expected:
            raise RuntimeError('Reference changed; capture placements and rebuild before checking: ' + source)
    for fp in REF['footprints']:
        for model in fp['models']:
            if 'source_path' not in model or 'choc_reference' in model['source_path']:
                continue
            points = model_points(ROOT.parent / model['source_path'])
            if model['rotation'][:2] != [0.0, 0.0] or model['offset'] != [0.0, 0.0, 0.0]:
                raise RuntimeError('Unexpected model transform')
            angle = math.radians(fp['rotation'] - model['rotation'][2])
            cs, sn = math.cos(angle), math.sin(angle)
            coords = [(fp['x'] + cs * x - sn * y, fp['y'] + sn * x + cs * y, z) for x, y, z in points]
            minimum = [min(p[i] for p in coords) for i in range(3)]
            maximum = [max(p[i] for p in coords) for i in range(3)]
            is_cap = 'mbk_15u' in model['source_path']
            if is_cap:
                minimum[2] -= P['key_travel']
            envelope = box(*minimum, *(maximum[i] - minimum[i] for i in range(3)))
            volume = case.common(envelope).Volume
            label = fp['reference'] + ': ' + Path(model['source_path']).stem + (' full travel' if is_cap else '')
            checks.append({'name': label, 'overlap_mm3': round(volume, 7),
                           'distance_mm': round(case.distToShape(envelope)[0], 5)})
            if volume > 0.0001:
                raise RuntimeError(f'{label} intersects case by {volume:.6f} mm3')
    doc = App.newDocument('NativeKiCadReference')
    Import.insert(str(stage / 'kicad-assembly.step'), doc.Name)
    root = next(o for o in doc.Objects if o.TypeId == 'App::Part' and not o.InList)
    for obj in root.Group:
        shape = obj.Shape.copy()
        if obj.Label.endswith('_PCB'):
            matrix = App.Matrix()
            matrix.A33 = P['pcb_thickness'] / shape.BoundBox.ZLength
            shape = shape.transformGeometry(matrix)
            shape.translate(V(0, 0, -P['pcb_thickness']))
        else:
            shape.translate(V(0, 0, -1.595))
        volume = case.common(shape).Volume
        checks.append({'name': obj.Label + ' native KiCad STEP', 'overlap_mm3': round(volume, 7)})
        if volume > 0.0001:
            raise RuntimeError(f'{obj.Label} intersects case by {volume:.6f} mm3')
    App.closeDocument(doc.Name)
    base = Part.read(str(stage / 'kicad-baseplate.step'))
    matrix = App.Matrix()
    matrix.A33 = P['baseplate_thickness'] / base.BoundBox.ZLength
    base = base.transformGeometry(matrix)
    base.translate(V(0, 0, -P['pcb_thickness'] - P['baseplate_thickness']))
    volume = case.common(base).Volume
    if volume > 0.0001:
        raise RuntimeError('Case interferes with baseplate')
    checks.append({'name': 'Native baseplate', 'overlap_mm3': round(volume, 7)})
    write_wrl(base, stage / 'baseplate.wrl', (0.13, 0.24, 0.18))
    hardware = []
    for fp in REF['footprints']:
        if fp['reference'].startswith('H'):
            x, y = fp['x'], fp['y']
            hardware.append(nut(x, y, P['nut_seat_height']))
            hardware.append(cylinder(x, y, -3.2, 1, 7))
            hardware.append(cylinder(x, y, -4.4, 1.9, 1.2))
    fasteners = Part.makeCompound(hardware)
    if case.common(fasteners).Volume > 0.0001:
        raise RuntimeError('Hardware intersects printed case')
    for fp in REF['footprints']:
        if fp['reference'].startswith('S'):
            landscape = fp['rotation'] == 0
            cw, ch = (26.5, 16.5) if landscape else (16.5, 26.5)
            swept = box(fp['x'] - cw / 2, fp['y'] - ch / 2, 4, cw, ch, 7)
            if fasteners.common(swept).Volume > 0.0001:
                raise RuntimeError('Hardware intersects full key travel')
    write_wrl(fasteners, stage / 'fasteners.wrl', (0.64, 0.67, 0.7))
    feet = [box(x, y, -5.2, 10, 20, 2) for x in (2, REF['width'] - 12) for y in (2, REF['height'] - 22)]
    if fasteners.common(Part.makeCompound(feet)).Volume > 0.0001:
        raise RuntimeError('Rubber feet intersect screw heads')
    write_wrl(Part.makeCompound(feet), stage / 'feet.wrl', (0.07, 0.08, 0.09))
    report = {'passed': True, 'checks': checks, 'native_step_component_z_shift_mm': -1.595,
              'pcb_body_note': 'KiCad exports the dielectric body at 1.51 mm; its through-hole outline is normalized to nominal 1.6 mm FR4 for the specified touching stack.',
              'case_file_contains_keyboard_reference': False,
              'hardware': 'Six M2 x 7 mm screws, modeled 3.8 mm diameter by 1.2 mm high heads, six plain 4 mm AF x 1.6 mm M2 nuts; no washers.'}
    (ROOT / 'generated/assembly-verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Native KiCad STEP, original component mesh bounds, full key travel, stack and hardware checks passed')


if __name__ == '__main__':
    main()
