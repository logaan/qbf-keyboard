import FreeCAD as App
import Part

from pathlib import Path
import json
import struct
from assembly_parts import module_parts, cap_one, plug_allowance, base_wire, fastener_parts, support_film

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'ergogen-kikad/design/models'


def box(x, y, z, dx, dy, dz):
    return Part.makeBox(dx, dy, dz, App.Vector(x, y, z))


def cylinder(x, y, z, radius, height):
    return Part.makeCylinder(radius, height, App.Vector(x, y, z))


def mesh_shape(shape, color):
    vertices, triangles = shape.tessellate(0.05)
    return [(p.x, p.y, p.z) for p in vertices], triangles, color


def write_model(name, parts):
    chunks = ['#VRML V2.0 utf8']
    bounds = []
    for vertices, triangles, color in parts:
        bounds.extend(vertices)
        coordinates = ',\n'.join(' '.join(f'{value / 2.54:.6f}' for value in p) for p in vertices)
        indices = ',\n'.join(f'{a}, {b}, {c}, -1' for a, b, c in triangles)
        chunks.append(f'''Shape {{
 appearance Appearance {{ material Material {{ diffuseColor {' '.join(map(str, color))} shininess 0.25 }} }}
 geometry IndexedFaceSet {{ solid FALSE coord Coordinate {{ point [
{coordinates}
 ] }} coordIndex [
{indices}
 ] }}
}}''')
    (OUT / (name + '.wrl')).write_text('\n'.join(chunks) + '\n')
    return {axis: [round(min(p[i] for p in bounds), 4), round(max(p[i] for p in bounds), 4)]
            for i, axis in enumerate(('x', 'y', 'z'))}


def main():
    OUT.mkdir(exist_ok=True)
    manifest = {}
    black, metal, green = (0.07, 0.08, 0.09), (0.68, 0.7, 0.73), (0.12, 0.28, 0.18)
    gold = (0.78, 0.58, 0.18)
    data = (OUT / 'source/mbk_1.5u.stl').read_bytes()
    vertices, triangles = [], []
    for i in range(struct.unpack_from('<I', data, 80)[0]):
        for j in range(3):
            x, y, z = struct.unpack_from('<3f', data, 84 + i * 50 + 12 + j * 12)
            vertices.append((x - 13.5, y + 8.5, z + 7.0))
        triangles.append((i * 3, i * 3 + 1, i * 3 + 2))
    manifest['mbk_15u'] = write_model('mbk_15u', [(vertices, triangles, (0.86, 0.88, 0.87))])
    switch = [mesh_shape(box(-6.9, -6.9, 0, 13.8, 13.8, 5), black),
              mesh_shape(box(-7.5, -7.5, 2.2, 15, 15, 0.8), black),
              mesh_shape(box(-2.1, -5.6, 5, 4.2, 11.2, 3), (0.55, 0.24, 0.18))]
    for x, y, radius in [(0, 0, 1.6), (-5.5, 0, 0.8), (5.5, 0, 0.8)]:
        switch.append(mesh_shape(cylinder(x, y, -2.2, radius, 2.2), black))
    for x, y in [(5, 3.8), (0, 5.9)]:
        switch.append(mesh_shape(cylinder(x, y, -3, 0.3, 3), metal))
    manifest['choc_reference'] = write_model('choc_reference', switch)
    manifest['mbk_1u_reference'] = write_model('mbk_1u_reference', [mesh_shape(cap_one(), (0.86, 0.88, 0.87))])
    manifest['xiao_plus_reference'] = write_model('xiao_plus_reference', [mesh_shape(shape, color) for _, shape, color in module_parts()])
    manifest['xiao_battery_wire'] = write_model('xiao_battery_wire', [mesh_shape(base_wire(), (0.72, 0.08, 0.06))])
    manifest['jst_sh_plug_allowance'] = write_model('jst_sh_plug_allowance', [mesh_shape(plug_allowance(), (0.88,0.86,0.8))])
    manifest['m2_low_head_reference'] = write_model('m2_low_head_reference', [mesh_shape(s, metal) for s in fastener_parts()])
    manifest['module_support_film'] = write_model('module_support_film', [mesh_shape(support_film(), (.76,.65,.2))])
    base_path=OUT/'source/baseplate.step'
    if base_path.exists():
        base=Part.read(str(base_path))
        matrix=App.Matrix();matrix.A33=1.6/base.BoundBox.ZLength
        base=base.transformGeometry(matrix)
        base.translate(App.Vector(0,0,-3.2-base.BoundBox.ZMin))
        manifest['baseplate_native'] = write_model('baseplate_native', [mesh_shape(base,(.15,.29,.18))])
    spec = json.loads((ROOT / 'ergogen-kikad/design/battery.json').read_text())
    length, width, depth = spec['length'], spec['width'], spec['thickness']
    cell = box(-length / 2, -width / 2, spec['bottom_z'], length, width, depth)
    try:
        cell = cell.makeFillet(0.3, cell.Edges)
    except Part.OCCError:
        pass
    battery = [mesh_shape(cell, (0.73, 0.75, 0.77)),
               mesh_shape(box(length / 2 - 3, -width / 2, spec['bottom_z'], 3, width, depth), (0.83, 0.61, 0.16))]
    for y, color in [(-0.9, (0.72, 0.08, 0.06)), (0.9, black)]:
        start = App.Vector(length / 2, y, spec['lead_exit_z'])
        finish = App.Vector(spec['lead_end'][0] - spec['center'][0], y, spec['lead_end'][2])
        direction = finish - start
        wire = Part.makeCylinder(spec['lead_radius'], direction.Length, start, direction)
        battery.append(mesh_shape(wire, color))
    manifest['battery_301055'] = write_model('battery_301055', battery)
    (OUT / 'bounds.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print('Built active KiCad reference models; supplier STEP is assigned separately')


if __name__ == '__main__':
    main()
