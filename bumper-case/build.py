import FreeCAD as App
import FreeCADGui as Gui
import MeshPart
import Part

from pathlib import Path
import json
import math

ROOT = Path(__file__).resolve().parent
P = json.loads((ROOT / 'parameters.json').read_text())
REF = json.loads((ROOT / 'reference/placements.json').read_text())
OUT = ROOT / 'generated'
V = App.Vector


def box(x, y, z, dx, dy, dz):
    return Part.makeBox(dx, dy, dz, V(x, y, z))


def cylinder(x, y, z, r, height):
    return Part.makeCylinder(r, height, V(x, y, z))


def rounded(x, y, z, dx, dy, dz, radius):
    shape = box(x, y, z, dx, dy, dz)
    edges = [e for e in shape.Edges if e.BoundBox.ZLength > dz - 0.001]
    return shape.makeFillet(radius, edges)


def union(shapes):
    return shapes[0].fuse(shapes[1:]).removeSplitter() if len(shapes) > 1 else shapes[0]


def polygon_prism(points, height):
    wire = Part.makePolygon([V(*p) for p in points] + [V(*points[0])])
    return Part.Face(wire).extrude(V(0, 0, height))


def nut(x, y, z):
    radius = P['nut_across_flats'] / math.sqrt(3)
    pts = [(x + radius * math.cos(math.radians(30 + 60 * i)),
            y + radius * math.sin(math.radians(30 + 60 * i)), z) for i in range(6)]
    return polygon_prism(pts, P['nut_thickness']).cut(cylinder(x, y, z - 0.1, 1, 2))


def control_hood(y0, y1, case_top, aperture):
    w, h = REF['width'], REF['height']
    extra = P['wall'] + P['pcb_edge_clearance']
    left = P['control_hood_left']
    underside = case_top + P['control_housing_clearance']
    top = underside + P['wall']
    hood = rounded(-extra, -extra, 0, w + 2 * extra, h + 2 * extra, top, 1.5 + extra)
    hood = hood.common(box(left, y0, 0, w + extra - left, y1 - y0, top))
    hood = hood.cut(box(left + P['wall'], y0 + P['wall'], -0.1,
                        w + extra - left - 2 * P['wall'], y1 - y0 - 2 * P['wall'], underside + 0.1))
    hood = hood.cut(aperture)
    edges = [e for e in hood.Edges if abs(e.BoundBox.ZMin - top) < 0.001
             and abs(e.BoundBox.ZMax - top) < 0.001]
    return hood.makeFillet(0.2, edges)


def make_parts():
    w, h = REF['width'], REF['height']
    extra = P['wall'] + P['pcb_edge_clearance']
    outer = (-extra, -extra, w + 2 * extra, h + 2 * extra)
    wall_bottom = -P['pcb_thickness'] - P['baseplate_thickness'] - P['board_gap']
    skirt = rounded(*outer[:2], wall_bottom, *outer[2:], -wall_bottom, 1.5 + extra)
    clearance = P['pcb_edge_clearance']
    skirt = skirt.cut(rounded(-clearance, -clearance, wall_bottom - 0.1,
                             w + 2 * clearance, h + 2 * clearance, -wall_bottom + 0.2,
                             1.5 + clearance))
    lip = rounded(*outer[:2], 0, *outer[2:], P['ledge_height'], 1.5 + extra)
    inset = P['ledge_overlap']
    lip = lip.cut(rounded(inset, inset, -0.1, w - 2 * inset, h - 2 * inset,
                         P['ledge_height'] + 0.2, 0.7))
    perimeter = skirt.fuse(lip).removeSplitter()
    plate = rounded(*outer[:2], P['plate_top'] - P['plate_thickness'],
                    *outer[2:], P['plate_thickness'], 1.5 + extra)
    bridge = rounded(*outer[:2], P['ledge_height'] - 0.1, *outer[2:], 0.5, 1.5 + extra)
    bridge = bridge.cut(rounded(inset, inset, P['ledge_height'] - 0.2,
                               w - 2 * inset, h - 2 * inset, 0.8, 0.7))
    plate = plate.fuse(bridge)
    plate = plate.cut(rounded(0.5, 21.65, 0.7, 73.9, 11.7, 2, 1.0))
    plate = plate.cut(box(103.5, -2, 0.7, 14, 19.15, 2))
    plate = plate.cut(box(103.5, 37.85, 0.7, 14, 19.2, 2))
    mounts = [f for f in REF['footprints'] if f['reference'].startswith('H')]
    supports = []
    for m in mounts:
        x, y = m['x'], m['y']
        boss = cylinder(x, y, 0, P['boss_radius'], P['plate_top'])
        rib = rounded(x - P['rib_width'] / 2, y - P['rib_length'] / 2, 0,
                      P['rib_width'], P['rib_length'], P['rib_height'], 0.5)
        supports.append(boss.fuse(rib))
    structural = union([perimeter, plate] + supports)
    structural = structural.cut(rounded(0.5, 21.65, 0, 73.9, 11.7, 4.5, 1.0))
    structural = structural.cut(box(74.4, 18.15, -0.1, 40.05, 18.7, 3))
    switches = [f for f in REF['footprints'] if f['reference'].startswith('S')]
    for switch in switches:
        s = P['switch_aperture']
        structural = structural.cut(rounded(switch['x'] - s / 2, switch['y'] - s / 2,
                                            -0.1, s, s, 2.6, 0.15))
    for m in mounts:
        x, y = m['x'], m['y']
        structural = structural.cut(cylinder(x, y, -0.1, P['screw_clearance_diameter'] / 2, 3))
        structural = structural.cut(cylinder(x, y, P['nut_seat_height'], P['boss_radius'], 1))
    gap = P['seam_gap'] / 2
    left_clip = box(-3, -3, -4, P['seam_x'] - gap + 3, h + 6, 20)
    right_clip = box(P['seam_x'] + gap, -3, -4, w + 3 - P['seam_x'] - gap, h + 6, 20)
    left = structural.common(left_clip).removeSplitter()
    right = structural.common(right_clip).removeSplitter()
    x0, y0, y1 = P['cover_left'], P['cover_bottom'], P['cover_top_y']
    cover = rounded(x0, y0, 0, w + extra - x0, y1 - y0,
                    P['cover_roof_top'], 1.5)
    cover = cover.cut(box(x0 - 2, y0 + P['wall'], -0.1,
                          w + extra - P['wall'] - x0 + 2, y1 - y0 - 2 * P['wall'],
                          P['cover_roof_top'] - P['cover_roof_thickness'] + 0.1))
    a, b, c, d = P['display_window']
    cover = cover.cut(rounded(a, b, 10.9, c, d, 2.0, 0.5))
    uy, uz, uw, uh = P['usb_opening']
    cover = cover.cut(rounded(w - 2, uy, uz, 5, uw, uh, 0.5))
    cover = cover.cut(box(x0 - 1, y0 - 1, -0.1,
                          P['seam_x'] + gap - x0 + 1, y1 - y0 + 2, 2.55))
    top_edges = [e for e in cover.Edges if abs(e.BoundBox.ZMin - P['cover_roof_top']) < 0.001
                 and abs(e.BoundBox.ZMax - P['cover_roof_top']) < 0.001]
    cover = cover.makeFillet(0.25, top_edges)
    rx, ry = P['reset_button_center']
    reset_opening = cylinder(rx, ry, -0.1, P['reset_hole_diameter'] / 2, 10)
    sx, sy, sw, sh = P['power_slot']
    power_opening = rounded(sx, sy, -0.1, sw, sh, 11, 0.25)
    reset_hood = control_hood(y1, h + extra, P['reset_case_top'], reset_opening)
    power_hood = control_hood(-extra, y0, P['power_case_top'], power_opening)
    hood_links = [box(103.3, lo, 1, P['control_hood_left'] - 103.3 + 0.2, hi - lo, 1.2)
                  for lo, hi in ((-extra, y0), (y1, h + extra))]
    hood_links = [s.common(rounded(-extra, -extra, 0.9, w + 2 * extra, h + 2 * extra, 1.4, 1.5 + extra))
                  for s in hood_links]
    right = union([right, cover, reset_hood, power_hood] + hood_links)
    return {'left_bumper': left, 'right_bumper': right}, mounts, switches


def write_wrl(shape, filename, color):
    vertices, faces = shape.tessellate(0.035)
    coords = ',\n'.join(f'{v.x / 2.54:.7f} {v.y / 2.54:.7f} {v.z / 2.54:.7f}' for v in vertices)
    indices = ',\n'.join(f'{a}, {b}, {c}, -1' for a, b, c in faces)
    filename.write_text('#VRML V2.0 utf8\nShape {\n appearance Appearance { material Material { diffuseColor '
                        + ' '.join(map(str, color)) + ' shininess 0.28 } }\n'
                        + ' geometry IndexedFaceSet { solid TRUE coord Coordinate { point [\n'
                        + coords + '\n] } coordIndex [\n' + indices + '\n] }\n}\n')


def check(parts, mounts, switches):
    results = {'parts': {}, 'clearance_checks': [], 'parameters': P,
               'reference_source_hashes': REF['source_files'],
               'pcb_stack': {'main_pcb': [-1.6, 0], 'baseplate': [-3.2, -1.6],
                             'feet': [-5.2, -3.2], 'case_bottom': -3.2},
               'limitations': ['The original Choc model flange is an approximation and conflicts with the drawing-based plate datum; switch plate mating is checked against the 13.8 mm body from the Kailh drawing.',
                               'Physical switch clip retention, cap internal cavities, solder protrusion, print tolerances, and fastener tightening require a prototype.',
                               'A 2 mm nozzle cannot conventionally print the requested 1 mm walls; print with a smaller nozzle.',
                               'Board touching is specified by the user; no PCB or baseplate geometry has been changed.']}
    both = union(list(parts.values()))
    def collision(label, shape):
        volume = both.common(shape).Volume
        results['clearance_checks'].append({'name': label, 'overlap_mm3': round(volume, 7)})
        if volume > 0.00001:
            raise RuntimeError(f'{label}: overlap {volume:.6f} mm3')
    def distance(label, a, b):
        value = a.distToShape(b)[0]
        results['clearance_checks'].append({'name': label, 'distance_mm': round(value, 5)})
        return value
    for name, shape in parts.items():
        if not shape.isValid() or len(shape.Solids) != 1:
            raise RuntimeError(f'{name}: invalid or disconnected solid ({len(shape.Solids)})')
        bb = shape.optimalBoundingBox(False, False)
        results['parts'][name] = {'solid_count': len(shape.Solids), 'valid': shape.isValid(),
                                 'volume_mm3': round(shape.Volume, 3),
                                 'bounds_mm': [round(v, 5) for v in (bb.XMin, bb.YMin, bb.ZMin, bb.XMax, bb.YMax, bb.ZMax)]}
        if abs(bb.ZMin + 3.2) > 0.001:
            raise RuntimeError('Case must end at baseplate underside')
    distance('Separate case pieces', *parts.values())
    if parts['left_bumper'].common(parts['right_bumper']).Volume > 0.00001:
        raise RuntimeError('Case pieces overlap')
    if parts['left_bumper'].BoundBox.ZMax > P['plate_top'] + 0.001:
        raise RuntimeError('Left part exceeds switch plate plane')
    for s in switches:
        landscape = s['rotation'] == 0
        cw, ch = (26.5, 16.5) if landscape else (16.5, 26.5)
        full_travel_z = P['cap_rest_underside'] - P['key_travel']
        swept = box(s['x'] - cw / 2, s['y'] - ch / 2, full_travel_z, cw, ch, 7)
        collision(s['reference'] + ' full cap travel envelope', swept)
        distance(s['reference'] + ' full cap travel clearance', both, swept)
        body = box(s['x'] - 6.9, s['y'] - 6.9, -0.1, 13.8, 13.8, 5.1)
        collision(s['reference'] + ' switch body', body)
    collision('Battery and wire/plug corridor', box(0.9, 22.25, 0.15, 64.85, 10.5, 3.6))
    collision('JST-PH body', box(66.15, 24.55, 0, 7.6, 5.9, 4.85))
    collision('Nice nano body and sockets', box(77.75, 18.35, 0, 36, 18.3, 6.8))
    collision('Nice view module', box(74.65, 20.5, 8, 36, 14, 2.91))
    collision('Nice view socket', box(74.68, 21.15, 0, 2.54, 12.7, 9))
    collision('Power housing envelope', box(106.575, 6.45, 0, 4.3, 8.6, P['power_case_top']))
    collision('Power actuator full travel', box(107.725, 8.75, P['power_case_top'],
                                                2, 2 + P['power_actuator_stroke'],
                                                P['power_actuator_top'] - P['power_case_top']))
    rx, ry = P['reset_button_center']
    collision('Reset housing envelope', box(105.725, 43.15, 0, 6, 6, P['reset_case_top']))
    collision('Reset button access', cylinder(rx, ry, 3.6, 1.65, 4))
    reset_roof = P['reset_case_top'] + P['control_housing_clearance'] + P['wall']
    power_roof = P['power_case_top'] + P['control_housing_clearance'] + P['wall']
    if reset_roof <= P['reset_button_top'] or power_roof >= P['power_actuator_top']:
        raise RuntimeError('Reset must be recessed and power actuator must stand proud')
    results['controls'] = {'housing_clearance_mm': P['control_housing_clearance'],
                          'reset_roof_top_mm': reset_roof,
                          'reset_recess_mm': reset_roof - P['reset_button_top'],
                          'reset_hole_diameter_mm': P['reset_hole_diameter'],
                          'power_roof_top_mm': power_roof,
                          'power_actuator_exposed_mm': P['power_actuator_top'] - power_roof,
                          'power_stroke_mm': P['power_actuator_stroke'],
                          'power_slot_mm': P['power_slot']}
    collision('USB plug path', box(113.4, 21.8, 3, 20, 11.4, 7))
    for m in mounts:
        n = nut(m['x'], m['y'], P['nut_seat_height'])
        collision(m['reference'] + ' nut', n)
        if P['cap_rest_underside'] - P['key_travel'] - n.BoundBox.ZMax < 0.59:
            raise RuntimeError('Nut is too high')
        collision(m['reference'] + ' screw passage', cylinder(m['x'], m['y'], -4, 1.01, 9))
        contact = n.copy()
        contact.translate(V(0, 0, -0.001))
        area = both.common(contact).Volume / 0.001
        if area < 8:
            raise RuntimeError('Insufficient nut support area')
        results['clearance_checks'].append({'name': m['reference'] + ' nut seating area',
                                           'area_mm2': round(area, 4)})
    for x in (2, REF['width'] - 12):
        for y in (2, REF['height'] - 22):
            collision('Rubber foot', box(x, y, -5.2, 10, 20, 2))
    results['passed'] = True
    return results


def main():
    OUT.mkdir(exist_ok=True)
    if not App.GuiUp:
        Gui.setupWithoutGUI()
    parts, mounts, switches = make_parts()
    report = check(parts, mounts, switches)
    doc = App.newDocument('QBF_Bumper_Case')
    settings = doc.addObject('App::FeaturePython', 'Dimensions')
    settings.Label = 'Design dimensions (mm); edit parameters.json and rebuild'
    for name, value in P.items():
        if isinstance(value, (float, int)):
            settings.addProperty('App::PropertyLength', ''.join(w.title() for w in name.split('_')), 'Dimensions')
            setattr(settings, ''.join(w.title() for w in name.split('_')), value)
    colors = {'left_bumper': (0.16, 0.38, 0.49), 'right_bumper': (0.92, 0.49, 0.22)}
    export_info = {}
    for name, shape in parts.items():
        obj = doc.addObject('PartDesign::Feature', ''.join(w.title() for w in name.split('_')))
        obj.Label = name.replace('_', ' ').title()
        obj.Shape = shape
        obj.addProperty('App::PropertyString', 'PrintOrientation', 'Manufacture')
        obj.PrintOrientation = 'Uppermost flat face on build plate; print STL is already oriented'
        if obj.ViewObject:
            obj.ViewObject.ShapeColor = colors[name]
            obj.ViewObject.LineColor = (0.12, 0.15, 0.17)
            obj.ViewObject.DisplayMode = 'Flat Lines'
        shape.exportStep(str(OUT / (name + '.step')))
        mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.035, AngularDeflection=0.12, Relative=False)
        if not mesh.isSolid():
            raise RuntimeError(name + ': STL mesh is not closed')
        mesh.write(str(OUT / (name + '_assembly.stl')))
        print_shape = shape.copy()
        print_shape.rotate(V(0, 0, 0), V(1, 0, 0), 180)
        bb = print_shape.optimalBoundingBox(False, False)
        print_shape.translate(V(-bb.XMin, -bb.YMin, -bb.ZMin))
        print_mesh = MeshPart.meshFromShape(Shape=print_shape, LinearDeflection=0.035, AngularDeflection=0.12, Relative=False)
        if not print_mesh.isSolid():
            raise RuntimeError(name + ': print mesh is not closed')
        if abs(print_mesh.BoundBox.ZMin) > 0.00001:
            raise RuntimeError(name + ': print mesh does not touch z=0')
        print_mesh.write(str(OUT / (name + '_print.stl')))
        pb = print_mesh.BoundBox
        export_info[name] = {'facets': mesh.CountFacets, 'closed_mesh': mesh.isSolid(),
                             'print_bounds_mm': [pb.XLength, pb.YLength, pb.ZLength]}
        write_wrl(shape, OUT / (name + '.wrl'), colors[name])
    report['exports'] = export_info
    doc.recompute()
    doc.saveAs(str(ROOT / 'QBF_Bumper_Case.FCStd'))
    Part.export([doc.getObject('LeftBumper'), doc.getObject('RightBumper')], str(OUT / 'bumper_case.step'))
    for path in OUT.glob('*.step'):
        path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines()) + '\n')
    (OUT / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    App.closeDocument(doc.Name)
    print('Generated two valid single solids, closed STL meshes, case-only FreeCAD and STEP, and clearance report')


if __name__ == '__main__':
    main()
