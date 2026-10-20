import FreeCAD as App
import Part
import MeshPart
import json
import math
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from assembly_parts import box, place, STANDARD, SPEC
OUT = ROOT / 'modular-case/generated'
OUT.mkdir(parents=True, exist_ok=True)
C = json.loads((ROOT / 'ergogen-kikad/generated/assembly-contract.json').read_text())
P = json.loads((ROOT / 'modular-case/parameters.json').read_text())
checks = []


def require(name, value, minimum=0):
    passed = value >= minimum - 1e-6
    checks.append({'name': name, 'value': round(float(value), 6), 'minimum': minimum, 'passed': passed})
    if not passed:
        raise RuntimeError(name + ': ' + str(value))


def clear(name, a, b, minimum=0):
    require(name + ' overlap mm3', 0.00001 - a.common(b).Volume)
    distance = a.distToShape(b)[0]
    require(name + ' clearance mm', distance, minimum)
    return distance


def bounds(shape):
    b = shape.BoundBox
    return [b.XMin, b.YMin, b.ZMin, b.XMax, b.YMax, b.ZMax]


def envelope(v):
    return box(*v[:3], v[3]-v[0], v[4]-v[1], v[5]-v[2])


def fuse(parts):
    return parts[0].fuse(parts[1:]).removeSplitter() if len(parts) > 1 else parts[0]


def rounded(x, y, z, w, h, depth, r):
    return fuse([box(x+r,y,z,w-2*r,h,depth), box(x,y+r,z,w,h-2*r,depth)] + [Part.makeCylinder(r,depth,App.Vector(a,b,z)) for a in (x+r,x+w-r) for b in (y+r,y+h-r)])


def hexagon(x,y,z,af,height):
    points = [App.Vector(x+af/math.sqrt(3)*math.cos(i*math.pi/3),y+af/math.sqrt(3)*math.sin(i*math.pi/3),z) for i in range(6)]
    return Part.Face(Part.makePolygon(points+[points[0]])).extrude(App.Vector(0,0,height))


def prism(points, direction):
    vertices=[App.Vector(*p) for p in points]
    return Part.Face(Part.makePolygon(vertices+[vertices[0]])).extrude(App.Vector(*direction))


def moved(shape, dx=0, dy=0, dz=0):
    result=shape.copy()
    result.translate(App.Vector(dx,dy,dz))
    return result


def right(shape):
    result=shape.copy()
    result.rotate(App.Vector(49.25,48,0),App.Vector(0,0,1),180)
    result.translate(App.Vector(97.7+P['joined_gap'],0,0))
    return result


def wrl(name, shape, color):
    vertices, faces=shape.tessellate(.06)
    coordinates=',\n'.join(' '.join(f'{v/2.54:.6f}' for v in (p.x,p.y,p.z)) for p in vertices)
    indices=',\n'.join(', '.join(map(str,t))+', -1' for t in faces)
    (OUT/(name+'.wrl')).write_text('#VRML V2.0 utf8\nShape { appearance Appearance { material Material { diffuseColor '+ ' '.join(map(str,color))+' } } geometry IndexedFaceSet { solid FALSE coord Coordinate { point [\n'+coordinates+'\n] } coordIndex [\n'+indices+'\n] } }\n')


for name,digest in C['board_sha256'].items():
    require('frozen board '+name, int(hashlib.sha256((ROOT/'ergogen-kikad/generated/pcbs'/name).read_bytes()).hexdigest()==digest),1)
for name,digest in C['design_sha256'].items():
    require('frozen design '+name,int(hashlib.sha256((ROOT/'ergogen-kikad/design'/name).read_bytes()).hexdigest()==digest),1)

x0,y0,x1,y1=C['pcb_bounds']
mounts=[(m['x'],m['y']) for m in C['mounts']]
tray=rounded(x0,y0,P['tray_bottom'],x1-x0,y1-y0,-3.2-P['tray_bottom'],1.5)
tray=fuse([tray]+[Part.makeCylinder(3,1.4,App.Vector(x,y,P['foot_bottom'])) for x in (9,86) for y in (22,74)])
for x,y in mounts:
    tray=tray.cut(Part.makeCylinder(1.2,5,App.Vector(x,y,-7)))
    tray=tray.cut(hexagon(x,y,-6.5,4.3,2.5))
for cy in (30,66):
    tray=tray.cut(box(90.1,cy-9.5,-5.6,6,19,1))
    tray=tray.cut(box(91.3,cy-9.5,-6.5,3.6,19,1.9))
    for dy in (-9.5,3.5):
        tray=tray.cut(box(90.1,cy+dy,-6.5,6,6,1.9))
tray=tray.cut(box(91.3,46.9,-6.5,3.6,2.2,.95)).removeSplitter()

rim=rounded(x0,y0,0,x1-x0,y1-y0,P['rim_top'],1.5).cut(box(x0+P['wall'],y0+P['wall'],-.1,x1-x0-2*P['wall'],y1-y0-2*P['wall'],4))
rim=rim.cut(box(-1,42.15,-.1,7,11.7,3.2)).cut(box(95.8,38.35,-.1,5,18.3,4))
additions=[rim,box(6.45,42.45,2.4,58.1,11.1,1.2)]
for x,y in mounts:
    low=y<48
    tab=box(x-4,18.75 if low else 69.5,0,8,7.75,.4)
    tab=tab.cut(Part.makeCylinder(1.2,1,App.Vector(x,y,-.1)))
    additions += [tab,box(x-.6,26.1 if low else 53.55,0,1.2,16.35,3.6)]
rim=fuse(additions)
for y in (18.65,76.65):
    rim=rim.cut(box(44.95,y,1.5,8.6,.7,1.2))
rim=rim.removeSplitter()

cover=rounded(-1.2,17.15,3.6,100.9,61.7,9.8,2.8).cut(rounded(.1,18.45,3.5,98.3,59.1,8.7,1.5))
ledge=rounded(-1.2,17.15,3.6,100.9,61.7,.8,2.8).cut(box(2.15,20.5,3.5,94.2,55,1))
cover=fuse([cover,ledge]+[box(x-.6,18.45,10.4,1.2,59.1,1.8) for x in (20.425,39.475,58.525,77.325)])
ramps=[]
for outer,inner in ((.1,2.15),(98.4,96.35)):
    ramps.append(prism([(outer,20.5,4.4),(inner,20.5,4.4),(outer,20.5,6.45)],(0,55,0)))
for outer,inner in ((18.45,20.5),(77.55,75.5)):
    for a,b in ((2.15,44.65),(53.85,96.35)):
        ramps.append(prism([(a,outer,4.4),(a,inner,4.4),(a,outer,6.45)],(b-a,0,0)))
cover=fuse([cover]+ramps)
for front in (True,False):
    wy=17.15 if front else 77.55
    cover=cover.fuse(box(45.25,wy,1.4,8,1.3,3))
    cover=cover.cut(box(45.15,18.45 if front else 75.5,3.5,8.2,2.05,1))
    for sx in (44.65,53.25):
        cover=cover.cut(box(sx,16.9 if front else 75.4,1.3,.6,4,10.3))
    sy=18.4 if front else 76.85
    cover=cover.fuse(box(45.25,sy,2.1,8,.75,.3))
    points=[App.Vector(45.25,18.4 if front else 77.6,1.8),App.Vector(45.25,19.15 if front else 76.85,2.1),App.Vector(45.25,18.4 if front else 77.6,2.1)]
    wedge=Part.Face(Part.makePolygon(points+[points[0]])).extrude(App.Vector(8,0,0))
    cover=cover.fuse(wedge)
    cover=cover.fuse(box(46.25,16.35 if front else 78.8,1.4,6,.85,1.1))
cover=cover.removeSplitter()

bridge_parts=[box(89.7,y-3,-7.6,26.8,6,1.1) for y in (30,66)]
bridge_parts.append(box(101.1,27,-7.6,4,42,1.1))
for x in (93.1,113.1):
    for y in (30,66):
        bridge_parts += [box(x-1.5,y-2.7,-6.5,3,5.4,1),box(x-2.7,y-2.7,-5.5,5.4,5.4,.7)]
    bridge_parts += [box(x-1.5,47,-7.6,3,19,1),box(x-1.5,47.2,-6.6,3,1.6,.8)]
bridge=fuse(bridge_parts)
rigid=fuse(bridge_parts[:3]+[s for i,s in enumerate(bridge_parts[3:]) if i%6<4])

hardware=[]
for x,y in mounts:
    screw=Part.makeCylinder(1,6,App.Vector(x,y,-5.6)).fuse(Part.makeCylinder(1.9,1.6,App.Vector(x,y,.4)))
    nut=hexagon(x,y,-5.2,4,1.2).cut(Part.makeCylinder(1,1.4,App.Vector(x,y,-5.3)))
    hardware += [screw,nut]
hardware=fuse(hardware)
parts={'tray':tray,'rim':rim,'cover':cover,'bridge':bridge}
for name,shape in parts.items():
    require(name+' valid',int(shape.isValid()),1)
    require(name+' one solid',int(len(shape.Solids)==1),1)
    for other,other_shape in parts.items():
        if name<other:
            clear(name+'/'+other,shape,other_shape)
for name,shape in {'tray':tray,'rim':rim,'cover':cover}.items():
    clear(name+'/case hardware',shape,hardware)
    for k in C['keys']:
        clear(name+'/'+k['name']+' full travel',shape,envelope(k['cap_swept_bounds']))
        clear(name+'/'+k['name']+' switch body',shape,envelope(k['body_bounds']))
        cx,cy=k['center']
        clear(name+'/'+k['name']+' switch shoulder',shape,box(cx-7.5,cy-7.5,2.2,15,15,.8))
    for component,b in C['components'].items():
        if component.endswith(('_screw','_nut')):continue
        s=envelope(b)
        if component in ('power','connector'):
            s=place(Part.read(str(STANDARD/SPEC[component]['native_model'])),SPEC[component]['origin'],-90)
        clear(name+'/'+component,shape,s)
    if name!='cover':
        for label in ('reset_2mm_probe','usb_reference_plug','power_access'):
            clear(name+'/'+label,shape,envelope(C['operating_keepouts'][label]))
for k in C['keys']:
    clear('case fasteners/'+k['name'],hardware,envelope(k['cap_swept_bounds']))
require('rim lateral cap clearance',min(rim.distToShape(envelope(k['cap_swept_bounds']))[0] for k in C['keys']),P['cap_edge_clearance'])
clear('battery roof clearance',rim,envelope(C['components']['battery']),.3)
require('cover roof above resting caps',P['cover_roof_bottom']-max(k['cap_rest_z'][1] for k in C['keys']),1.2)
clear('right tray/left cover',right(tray),cover)
clear('two covers',right(cover),cover)
for name,shape in {'tray':tray,'rim':rim,'cover':cover}.items():
    clear('bridge/right '+name,bridge,right(shape))
for i in range(27):
    travel=-P['bridge_slide']+i*.25
    pose=moved(rigid,dy=travel)
    clear('bridge slide '+str(travel)+'/left tray',pose,tray)
    clear('bridge slide '+str(travel)+'/right tray',pose,right(tray))
for dy in (-6.5,6.5):
    for dz in (-1,-2,-3,-4):
        clear('bridge vertical entry '+str((dy,dz)),moved(rigid,dy=dy,dz=dz),fuse([tray,right(tray)]))
for component in ('power',):
    stock=place(Part.read(str(STANDARD/SPEC[component]['native_model'])),SPEC[component]['origin'],-90)
    for delta in (0,-.75,-1.5):
        for name,shape in parts.items():
            clear('power stroke '+str(delta)+'/'+name,moved(stock,dy=delta),shape)
base=Part.read(str(ROOT/'ergogen-kikad/design/models/source/baseplate.step'))
matrix=App.Matrix()
matrix.A33=1.6/base.BoundBox.ZLength
base=base.transformGeometry(matrix)
base.translate(App.Vector(0,0,-3.2-base.BoundBox.ZMin))
for name,shape in parts.items():
    clear(name+'/native baseplate',shape,base)
clear('case screws/native baseplate holes',hardware,base)
released=cover.copy()
for front in (True,False):
    region=box(44.65,16 if front else 75.4,1.3,9.2,4.7,10.3)
    tongue=released.common(region)
    released=released.cut(region).fuse(moved(tongue,dy=-.5 if front else .5))
for dz in (0,.25,.5,1,2,4,8,14):
    clear('released cover upward '+str(dz),moved(released,dz=dz),rim)
    for k in C['keys']:
        clear('released cover '+str(dz)+'/'+k['name'],moved(released,dz=dz),envelope(k['cap_swept_bounds']))
for x in (93.1,113.1):
    for dy in (-6.5,-4,-2,0):
        lowered=box(x-1.5,47.2+dy,-7.35,3,1.6,.8)
        clear('bridge detent deflected '+str((x,dy)),lowered,fuse([tray,right(tray)]))
require('cover clip strain estimate',1.2-100*3*1.3*P['cover_clip_deflection']/(2*9.35**2))
require('bridge clip strain estimate',1-100*3*1*P['bridge_clip_deflection']/(2*15**2))

palette={'tray':(.12,.34,.4),'rim':(.18,.49,.55),'cover':(.86,.47,.19),'bridge':(.9,.53,.21)}
doc=App.newDocument('QBF_Modular_Case')
manifest={}
for name,shape in parts.items():
    obj=doc.addObject('PartDesign::Feature',name.title())
    obj.Shape=shape
    obj.addProperty('App::PropertyString','PrintOrientation').PrintOrientation='Roof/top down' if name in ('tray','rim','cover') else 'Base down'
    obj.addProperty('App::PropertyString','Source').Source='modular-case/build.py and parameters.json'
    shape.exportStep(str(OUT/(name+'.step')))
    wrl(name,shape,palette[name])
    mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.06,AngularDeflection=.25,Relative=False)
    require(name+' mesh closed',int(mesh.isSolid()),1)
    mesh.write(str(OUT/(name+'_assembly.stl')))
    oriented=shape.copy()
    if name in ('tray','rim','cover'):
        oriented.rotate(App.Vector(),App.Vector(1,0,0),180)
    b=oriented.BoundBox
    oriented.translate(App.Vector(-b.XMin,-b.YMin,-b.ZMin))
    mesh=MeshPart.meshFromShape(Shape=oriented,LinearDeflection=.06,AngularDeflection=.25,Relative=False)
    mesh.write(str(OUT/(name+'_print.stl')))
    manifest[name]={'bounds':bounds(shape),'volume_mm3':shape.Volume,'print_size_mm':[oriented.BoundBox.XLength,oriented.BoundBox.YLength,oriented.BoundBox.ZLength],'quantity':1 if name=='bridge' else 2}
wrl('case_hardware',hardware,(.65,.67,.7))
doc.recompute()
doc.saveAs(str(OUT/'qbf_modular_case.FCStd'))
report={'passed':True,'check_count':len(checks),'checks':checks,'source_contract_sha256':hashlib.sha256((ROOT/'ergogen-kikad/generated/assembly-contract.json').read_bytes()).hexdigest(),'parts':manifest,'joined_pcb_width_mm':205.4,'protected_height_mm':P['cover_roof_top']-P['foot_bottom'],'cap_rest_to_roof_mm':P['cover_roof_bottom']-10.969114,'estimated_clip_outer_fiber_strain_percent':{'cover':100*3*1.3*P['cover_clip_deflection']/(2*9.35**2),'bridge':100*3*P['bridge_clip_deflection']/(2*15**2)},'limitations':['Nominal CAD clearance verification, not a physical load, drop, fatigue, or tolerance test.','Snap fits need PETG coupon/prototype verification; release tabs intentionally flex during assembly.','Cover ribs clear keycap envelopes; cover roof deflection under luggage loads is not simulated.','Separate halves for ordinary straight USB cable access.','Electronics assembly-contract limitations remain applicable.']}
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Case built and verified:',len(checks),'checks')
