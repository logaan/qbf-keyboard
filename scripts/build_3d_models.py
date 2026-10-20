import FreeCAD as App
import Part

from pathlib import Path
import json
import struct

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
              mesh_shape(box(-7.5, -7.5, 0.8, 15, 15, 1.4), black),
              mesh_shape(box(-2.1, -5.6, 5, 4.2, 11.2, 3), (0.55, 0.24, 0.18))]
    for x, y, radius in [(0, 0, 1.6), (-5.5, 0, 0.8), (5.5, 0, 0.8)]:
        switch.append(mesh_shape(cylinder(x, y, -2.2, radius, 2.2), black))
    for x, y in [(5, 3.8), (0, 5.9)]:
        switch.append(mesh_shape(cylinder(x, y, -3, 0.3, 3), metal))
    manifest['choc_reference'] = write_model('choc_reference', switch)
    nano_pcb = box(-9.15, -18, 3.6, 18.3, 36, 0.8)
    nano = []
    for x in (-7.62, 7.62):
        nano.append(mesh_shape(box(x - 1.27, -15.24, 0, 2.54, 30.48, 3.6), black))
        for i in range(12):
            y = -13.97 + i * 2.54
            nano_pcb = nano_pcb.cut(cylinder(x, y, 3.5, 0.5, 1))
            ring = cylinder(x, y, 4.4, 0.88, 0.04).cut(cylinder(x, y, 4.39, 0.5, 0.1))
            nano.append(mesh_shape(ring, gold))
    nano.append(mesh_shape(nano_pcb, green))
    usb = box(-4.5, -18, 3.6, 9, 7, 3.2).cut(box(-3.7, -18.1, 4.2, 7.4, 6.5, 2))
    nano.extend([mesh_shape(usb, metal), mesh_shape(box(-3.2, -17.6, 4.9, 6.4, 5.2, 0.6), black),
                 mesh_shape(box(-4, -4, 4.4, 8, 9, 2.2), metal),
                 mesh_shape(box(-3, 10, 4.4, 6, 6, 0.1), gold)])
    manifest['nice_nano_reference'] = write_model('nice_nano_reference', nano)
    pcb = box(-18, -7, 9, 36, 14, 1)
    for i in range(5):
        pcb = pcb.cut(cylinder(-16.7, 5.08 - i * 2.54, 8.9, 0.5, 1.2))
    lcd = [mesh_shape(pcb, black), mesh_shape(box(-14.8, -6.8, 10, 29, 13.6, 0.9), black),
           mesh_shape(box(-13.4, -5.4, 10.9, 25.3, 10.8, 0.01), (0.64, 0.69, 0.66)),
           mesh_shape(box(4.4, -4.7, 8, 3.8, 9.4, 1), black),
           mesh_shape(box(-17.97, -6.35, 6.5, 2.54, 12.7, 2.5), black)]
    for i in range(5):
        y = 5.08 - i * 2.54
        lcd.append(mesh_shape(box(-17.02, y - 0.32, 3.2, 0.64, 0.64, 6.8), gold))
    manifest['nice_view_reference'] = write_model('nice_view_reference', lcd)
    socket = box(-17.97, -6.35, 0, 2.54, 12.7, 6.5)
    manifest['display_socket'] = write_model('display_socket', [mesh_shape(socket, black)])
    cell = box(-28.75, -5.25, 0.2, 57.5, 10.5, 3.5)
    try:
        cell = cell.makeFillet(0.3, cell.Edges)
    except Part.OCCError:
        pass
    battery = [mesh_shape(cell, (0.73, 0.75, 0.77)),
               mesh_shape(box(25.75, -5.25, 0.2, 3, 10.5, 3.5), (0.83, 0.61, 0.16))]
    for y, color in [(-0.9, (0.72, 0.08, 0.06)), (0.9, black)]:
        wire = Part.makeCylinder(0.3, 1.75, App.Vector(28.75, y, 1.7), App.Vector(1, 0, 0))
        battery.append(mesh_shape(wire, color))
    manifest['battery_301055'] = write_model('battery_301055', battery)
    plug = box(-2.9, -12.25, 0.2, 5.8, 6, 4.3)
    manifest['battery_plug_reference'] = write_model('battery_plug_reference', [mesh_shape(plug, (0.88, 0.86, 0.8))])
    (OUT / 'bounds.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print('Built seven KiCad assembly models; MBK mesh from designer, other generated models are references')


if __name__ == '__main__':
    main()
