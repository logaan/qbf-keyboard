"""Make explicit dimension-envelope models for KiCad's real 3D renderer.

These solids are review envelopes, not manufacturer STEP component models.
The acrylic, matching holes, hollow standoffs and accessory ring are modelled.
"""
from pathlib import Path
import json
import math
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/pydeps'))
import numpy as np
import mapbox_earcut
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
import pcbnew as pcb

data = json.loads((ROOT/'kicad/geometry.json').read_text())
u, pts = data['units'], data['points']
cx, cy = 100+1.5*u['pitch_x'], 100
models = ROOT/'models'
models.mkdir(exist_ok=True)

def polygon_body(poly, z0, z1, color, alpha=0):
    if poly.geom_type == 'MultiPolygon':
        return ''.join(polygon_body(p,z0,z1,color,alpha) for p in poly.geoms)
    rings = [np.array(poly.exterior.coords[:-1],dtype=np.float64)]
    rings.extend(np.array(r.coords[:-1],dtype=np.float64) for r in poly.interiors)
    vertices = np.vstack(rings)
    ends = np.cumsum([len(r) for r in rings]).astype(np.uint32)
    triangles = mapbox_earcut.triangulate_float64(vertices, ends).reshape(-1,3)
    n = len(vertices)
    coords=[]
    for z in [z0,z1]:
        coords.extend(f'{x/2.54:.7f} {y/2.54:.7f} {z/2.54:.7f}' for x,y in vertices)
    faces=[]
    for tri in triangles:
        faces.append(' '.join(str(int(v)) for v in tri[::-1])+' -1')
        faces.append(' '.join(str(int(v)+n) for v in tri)+' -1')
    start=0
    for ring in rings:
        count=len(ring)
        for i in range(count):
            a,b=start+i,start+(i+1)%count
            faces.append(f'{a} {b} {b+n} {a+n} -1')
        start+=count
    rgb=' '.join(map(str,color))
    return ('Shape { appearance Appearance { material Material { diffuseColor '+rgb+
            f' transparency {alpha} specularColor 0.2 0.2 0.2 shininess 0.35'+' } }\n'+
            'geometry IndexedFaceSet { solid FALSE coord Coordinate { point [\n'+
            ',\n'.join(coords)+'\n] } coordIndex [\n'+',\n'.join(faces)+'\n] } }\n')

def rect_at(x,y,w,h,z0,z1,color,alpha=0):
    return polygon_body(box(x-w/2,y-h/2,x+w/2,y+h/2),z0,z1,color,alpha)

def center(p):
    return p['x']-cx, p['y']+cy  # Ergogen y points upward.

parts=[]
for name,p in pts.items():
    if 'switch' not in p['meta']['tags']: continue
    x,y=center(p)
    parts.append(rect_at(x,y,14,14,0,u['switch_preview_height'],(0.13,0.16,0.19)))
    parts.append(rect_at(x,y,p['meta']['width'],p['meta']['height'],u['keycap_preview_z'],
                         u['keycap_preview_z']+u['keycap_preview_thickness'],
                         (0.47,0.78,0.74) if name.endswith('middle') else (0.63,0.72,0.87)))

pcb_t=1.6
mx,my=center(pts['controller'])
mcu_top=-pcb_t-u['controller_socket_height']
parts.append(rect_at(mx,my-0.03,17.78,33.08,mcu_top-3.2,mcu_top,(0.13,0.33,0.29)))
parts.append(rect_at(mx-0.127,my+17.272,7.366,1.524,mcu_top-3.2,mcu_top,(0.64,0.67,0.71)))
for sx in [-7.62,7.62]:
    parts.append(rect_at(mx+sx,my,2.54,33.02,-pcb_t-u['controller_socket_height'],-pcb_t,(0.15,0.16,0.18)))
dx,dy=center(pts['display'])
disp_top=-pcb_t-u['display_socket_height']
parts.append(rect_at(dx,dy,14,36,disp_top-2.9,disp_top,(0.32,0.26,0.45)))
parts.append(rect_at(dx,dy+0.75,10.8,25.3,disp_top-2.95,disp_top-2.9,(0.13,0.16,0.20)))
bx,by=center(pts['battery'])
bat_top=-pcb_t-u['battery_mount_drop']
parts.append(rect_at(bx,by,u['battery_w'],u['battery_h'],bat_top-u['battery_t'],bat_top,(0.74,0.76,0.77)))
parts.append(rect_at(bx,by,u['battery_w']+0.12,2.5,bat_top-u['battery_t']-0.05,bat_top+0.05,(0.88,0.70,0.15)))

# Side controls and JST are rectangular body/actuator envelopes from library drawings.
rx,ry=center(pts['reset'])
parts.append(rect_at(rx,ry,3.5,4.7,-3.4,-pcb_t,(0.30,0.32,0.35)))
parts.append(rect_at(rx-2.25,ry,1,2.6,-3.2,-pcb_t,(0.50,0.52,0.55)))
px,py=center(pts['power'])
parts.append(rect_at(px,py,6.7,2.6,-3.1,-pcb_t,(0.30,0.32,0.35)))
parts.append(rect_at(px,py-2.07,2,1.55,-3,-pcb_t,(0.16,0.17,0.20)))
jx,jy=center(pts['jst'])
parts.append(rect_at(jx,jy-2.45,5.9,7.6,-6.4,-pcb_t,(0.82,0.81,0.76)))

bare_parts=''.join(parts)
mech=[]
half_w,half_h=u['board_w']/2,u['board_h']/2
r=u['board_corner']
acrylic=box(-half_w+r,-half_h+r,half_w-r,half_h-r).buffer(r,quad_segs=12)
holes=[]
for name,p in pts.items():
    if not name.startswith('mount_'):continue
    x,y=center(p)
    holes.append(Point(x,y).buffer(u['mount_diameter']/2,quad_segs=16))
    spacer=Point(x,y).buffer(u['standoff_diameter']/2,quad_segs=16).difference(
        Point(x,y).buffer(u['mount_diameter']/2,quad_segs=16))
    mech.append(polygon_body(spacer,-pcb_t-u['standoff_height'],-pcb_t,(0.65,0.68,0.71)))
acrylic=acrylic.difference(unary_union(holes))
plate_top=-pcb_t-u['standoff_height']
plate_bottom=plate_top-u['acrylic_thickness']
mech.append(polygon_body(acrylic,plate_bottom,plate_top,(0.65,0.79,0.84),0.65))
ring=Point(0,0).buffer(u['ring_outer_diameter']/2,quad_segs=64).difference(
    Point(0,0).buffer(u['ring_inner_diameter']/2,quad_segs=64))
mech.append(polygon_body(ring,plate_bottom-u['ring_thickness'],plate_bottom,(0.53,0.55,0.58)))
for name,p in pts.items():
    if not name.startswith('mount_'):continue
    x,y=center(p)
    # Flush screw-head envelope. Countersink details must match chosen hardware.
    disk=Point(x,y).buffer(1.9,quad_segs=20)
    mech.append(polygon_body(disk,plate_bottom,plate_bottom+0.7,(0.55,0.58,0.60)))

prefix='#VRML V2.0 utf8\n# Review envelopes only; dimensions from editable Ergogen units.\n'
for name,content in [('modules-envelopes.wrl',bare_parts),('assembly-envelopes.wrl',bare_parts+''.join(mech))]:
    (models/name).write_text(prefix+content)

for name,model in [('braille_modules_preview','modules-envelopes.wrl'),
                   ('braille_assembly_preview','assembly-envelopes.wrl')]:
    board=pcb.LoadBoard(str(ROOT/'kicad/braille_review_routed.kicad_pcb'))
    fp=pcb.FOOTPRINT(board)
    fp.SetReference('MECH_PREVIEW')
    fp.SetValue('REVIEW_ENVELOPES_ONLY')
    fp.SetPosition(pcb.VECTOR2I(pcb.FromMM(cx),pcb.FromMM(cy)))
    fp.SetLayer(pcb.F_Cu)
    m=pcb.FP_3DMODEL()
    m.m_Filename='${KIPRJMOD}/../models/'+model
    fp.Models().push_back(m)
    board.Add(fp)
    pcb.SaveBoard(str(ROOT/'kicad'/f'{name}.kicad_pcb'),board)

# Dimensional assertions, conditional on provisional ring and flush screw heads.
for name,p in pts.items():
    if name.startswith('mount_'):
        x,y=center(p)
        assert math.hypot(x,y)-1.9 > u['ring_outer_diameter']/2
assert u['screw_head_projection'] <= u['ring_thickness']
assert -7.9 > plate_top  # Lowest dimension envelope has clearance in this study.
snapshot={'description':'Provisional assembly envelopes; NOT manufacturer 3D models',
          'acrylic_inner_face_below_pcb_bottom_mm':u['standoff_height'],
          'acrylic_thickness_mm':u['acrylic_thickness'],
          'ring_below_acrylic_mm':u['ring_thickness'],
          'illustrated_height_mm':u['keycap_preview_z']+u['keycap_preview_thickness']-plate_bottom+u['ring_thickness'],
          'flush_screw_heads_assumed':True,'units':u}
(models/'assembly-parameters.json').write_text(json.dumps(snapshot,indent=2)+'\n')
print('Created real 3D envelope meshes, acrylic holes, standoffs and passive ring for KiCad rendering.')
print('Full component models and assembled heights remain unverified.')
