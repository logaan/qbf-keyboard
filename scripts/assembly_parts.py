import FreeCAD as App
import Part
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STANDARD = Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/3dmodels')
SPEC = json.loads((ROOT / 'ergogen-kikad/design/assembly.json').read_text())


def box(x, y, z, dx, dy, dz):
    return Part.makeBox(dx, dy, dz, App.Vector(x, y, z))


def bounds_box(bounds, bottom, height):
    x1, y1, x2, y2 = bounds
    return box(x1, y1, bottom, x2-x1, y2-y1, height)


def wire(path, radius):
    pieces = []
    for start, end in zip(path, path[1:]):
        direction = App.Vector(*end) - App.Vector(*start)
        pieces.append(Part.makeCylinder(radius, direction.Length, App.Vector(*start), direction))
    for p in path[1:-1]:
        pieces.append(Part.makeSphere(radius, App.Vector(*p)))
    return Part.makeCompound(pieces)


def place(shape, center, angle=0):
    result = shape.copy()
    result.rotate(App.Vector(), App.Vector(0, 0, 1), angle)
    result.translate(App.Vector(*center, 0))
    return result


def module_parts():
    m = SPEC['module']
    top = m['pcb_top_z']
    pcb = box(-10.5, -8.9, top-1.6, 21, 17.8, 1.6)
    contact_parts = []
    for side, xs in [(1, [7.62, 5.08, 2.54, 0, -2.54, -5.08, -7.62]),
                     (-1, [-7.62, -5.08, -2.54, 0, 2.54, 5.08, 7.62])]:
        for x in xs:
            pcb = pcb.cut(Part.makeCylinder(.3, 1.7, App.Vector(x, side*8.89, top-1.65)))
            contact_parts.append(box(x-.4, min(side*8.8, side*10.5), 0, .8, 1.7, .8))
    pieces = [('pcb', pcb, (.09, .23, .19))]
    pieces += [('solder', s, (.66, .68, .7)) for s in contact_parts]
    pieces += [('usb', bounds_box(m['usb_local_bounds'], top, 3.2), (.68, .7, .72)),
               ('reset', bounds_box(m['reset_local_bounds'], top, .53), (.18, .18, .18)),
               ('microphone', bounds_box(m['microphone_local_bounds'], top, .94), (.62, .62, .59)),
               ('antenna', bounds_box(m['antenna_local_bounds'], top, 1.3), (.75, .73, .66)),
               ('radio', bounds_box([-5.76928,-4.2386,1.39072,2.9214], top, 1.0), (.6,.62,.64)),
               ('imu', bounds_box([.09072,3.3084,3.09072,5.8284], top, 1.0), (.1,.1,.12))]
    return pieces


def cap_one():
    outer = box(-8.75,-8.25,7,17.5,16.5,3.969114)
    inner = box(-7.75,-7.25,6.9,15.5,14.5,2.5)
    return outer.cut(inner)


def plug_allowance():
    return box(-3, -6.325, .2, 6, 3.75, 2.8)


def base_wire():
    m=SPEC['module']
    center=m['center']
    path=[[p[0]-center[0],p[1]-center[1],m['battery_wire_z']] for p in m['battery_wire_path']]
    path=[[path[0][0],path[0][1],-1.55],*path,[path[-1][0],path[-1][1],-1.6]]
    return wire(path,m['battery_wire_od']/2)


def fastener_parts():
    screw = Part.makeCylinder(1, 5, App.Vector(0,0,-5)).fuse(Part.makeCylinder(1.9,1.6))
    import math
    points=[App.Vector(4/math.sqrt(3)*math.cos(i*math.pi/3),4/math.sqrt(3)*math.sin(i*math.pi/3),-4.8) for i in range(6)]
    nut=Part.Face(Part.makePolygon(points+[points[0]])).extrude(App.Vector(0,0,1.6)).cut(Part.makeCylinder(1,2,App.Vector(0,0,-5)))
    return screw,nut


def support_film():
    film=box(-10.5,-8.9,-1.6,21,17.8,.05)
    x,y=SPEC['module']['center']
    for bounds in SPEC['module']['baseplate_access_windows']:
        b=[bounds[0]-x,bounds[1]-y,bounds[2]-x,bounds[3]-y]
        film=film.cut(bounds_box(b,-1.7,.3))
    return film
