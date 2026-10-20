import FreeCAD as App
import Part
import json
import math
import hashlib
import sys
from pathlib import Path
from assembly_parts import ROOT, SPEC, STANDARD, box, bounds_box, wire, place, module_parts, fastener_parts, base_wire, support_film

OUTPUT, STAGE = map(Path,sys.argv[1:])
GEOMETRY=json.loads((OUTPUT/'board_geometry.json').read_text())
AUDIT=json.loads((OUTPUT/'checks/assembly-board.json').read_text())
PACK=json.loads((ROOT/'ergogen-kikad/design/battery.json').read_text())
FP={f['reference']:f for f in AUDIT['footprints']}
checks=[]


def require(name, value, threshold=0):
    passed=value>=threshold-1e-6
    checks.append({'check':name,'value':round(value,6),'minimum':threshold,'passed':passed})
    if not passed:raise RuntimeError(name+': '+str(value))


def no_overlap(name, a, b):
    overlap=a.common(b).Volume
    require(name, .00001-overlap)
    return a.distToShape(b)[0]


def native_board(name, bottom):
    shape=Part.read(str(STAGE/(name+'.step')))
    matrix=App.Matrix();matrix.A33=1.6/shape.BoundBox.ZLength
    shape=shape.transformGeometry(matrix)
    shape.translate(App.Vector(0,0,bottom-shape.BoundBox.ZMin))
    return shape


def bound(shape):
    b=shape.BoundBox
    return [round(v,6) for v in [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]]


main=native_board('macropad',-1.6)
base=native_board('baseplate',-3.2)
require('main width unchanged',.001-abs(main.BoundBox.XLength-97.7))
require('main height unchanged',.001-abs(main.BoundBox.YLength-58.5))
require('baseplate width unchanged',.001-abs(base.BoundBox.XLength-97.7))
require('baseplate height unchanged',.001-abs(base.BoundBox.YLength-58.5))
parts={};caps={};switches={};keys=[]
for f in AUDIT['footprints']:
    if not f['reference'].startswith('S'):continue
    name=f['reference'];cx,cy=f['center'];angle=f['rotation'];one=f['value']=='Choc v1 1U'
    index=int(next(p['net'][1:] for p in f['pads'] if p['net'].startswith('D')))
    expected_x=[10.9,29.95,49,68.05,87.1][index%5]
    expected_y=(66.75 if index==4 else 29.25 if index==9 else 61.75 if index<5 else 34.25)
    require(name+' fixed center',1e-5-math.dist((cx,cy),(expected_x,expected_y)))
    width,height=(17.5,16.5) if one else (16.5,26.5)
    caps[name]=box(cx-width/2,cy-height/2,4,width,height,6.969114)
    shoulder=box(cx-7.5,cy-7.5,2.2,15,15,.8)
    body=box(cx-6.9,cy-6.9,0,13.8,13.8,5)
    switches[name]=Part.makeCompound([shoulder,body])
    for px,py,r,z,h in [(0,0,1.6,-2.2,2.2),(-5.5,0,.8,-2.2,2.2),(5.5,0,.8,-2.2,2.2),(5,3.8,.3,-3,3),(0,5.9,.3,-3,3)]:
        pin=place(Part.makeCylinder(r,h,App.Vector(px,py,z)),(cx,cy),angle)
        no_overlap(name+' pin clears main PCB',pin,main)
        no_overlap(name+' pin clears baseplate',pin,base)
    keys.append({'name':('t' if index<5 else 'b')+str(index%5+1),'reference':name,'center':[cx,cy],'cap_mm':[width,height],'shoulder_mm':[15,15],'shoulder_z':[2.2,3],'body_bounds':[cx-6.9,cy-6.9,0,cx+6.9,cy+6.9,5],'peg_bottom_z':-2.2,'pin_bottom_z':-3,'cap_rest_z':[7,10.969114],'travel':3,'cap_swept_bounds':bound(caps[name])})
for name,cap in caps.items():
    for other,shape in caps.items():
        if name<other:require(name+'/'+other+' cap gap',no_overlap(name+'/'+other+' caps',cap,shape),1)
    for other,shape in switches.items():
        if name!=other:no_overlap(name+'/'+other+' cap/switch travel',cap,shape)
module=SPEC['module'];center=module['center']
for name,shape,color in module_parts():
    placed=place(shape,center)
    if name=='solder':
        parts.setdefault('controller_solder',[]).append(placed)
        continue
    parts['controller_'+name]=placed
parts['controller_solder']=Part.makeCompound(parts['controller_solder'])
parts['support_film']=place(support_film(),center)
parts['battery_wire']=place(base_wire(),center)
lead_paths=[[[PACK['center'][0]+PACK['length']/2,PACK['center'][1]+dy,PACK['lead_exit_z']],[PACK['lead_end'][0],PACK['lead_end'][1]+dy,PACK['lead_end'][2]]] for dy in [-.9,.9]]
parts['battery_leads']=Part.makeCompound([wire(path,PACK['lead_radius']) for path in lead_paths])
parts['battery']=box(PACK['center'][0]-PACK['length']/2,PACK['center'][1]-PACK['width']/2,PACK['bottom_z'],PACK['length'],PACK['width'],PACK['thickness'])
parts['power']=place(Part.read(str(STANDARD/SPEC['power']['native_model'])),SPEC['power']['origin'],-90)
parts['connector']=place(Part.read(str(STANDARD/SPEC['connector']['native_model'])),SPEC['connector']['origin'],-90)
parts['connector_mated_allowance']=bounds_box(SPEC['connector']['mated_allowance_bounds'],0,3)
for f in AUDIT['footprints']:
    if f['reference'].startswith('H'):
        screw,nut=fastener_parts()
        parts[f['reference']+'_screw']=place(screw,f['center'])
        parts[f['reference']+'_nut']=place(nut,f['center'])
        no_overlap(f['reference']+' screw/main hole',parts[f['reference']+'_screw'],main)
        no_overlap(f['reference']+' screw/base hole',parts[f['reference']+'_screw'],base)
        for other,body in switches.items():no_overlap(f['reference']+'/'+other+' screw/switch',parts[f['reference']+'_screw'],body)
        for axis in (0,1):
            low,high=(.4,98.1) if axis==0 else (18.75,77.25)
            require(f['reference']+' nut/board border '+str(axis),min(f['center'][axis]-low,high-f['center'][axis])-4/math.sqrt(3),2)
minima=[]
for name,shape in parts.items():
    for key,cap in caps.items():
        distance=no_overlap(name+'/'+key+' full cap travel',shape,cap)
        minima.append({'component':name,'key':key,'clearance':round(distance,6)})
    if name not in ['controller_solder','battery_wire','support_film'] and not name.endswith(('_screw','_nut')):
        no_overlap(name+'/main PCB',shape,main)
        no_overlap(name+'/baseplate',shape,base)
        for key,body in switches.items():no_overlap(name+'/'+key+' switch body',shape,body)
for key,shape in switches.items():
    require('solder land to '+key+' switch shoulder',parts['controller_solder'].distToShape(shape)[0],.25)
no_overlap('underside battery wire/baseplate access',parts['battery_wire'],base)
support=base.copy();support.translate(App.Vector(0,0,.05))
require('module film fully supported by native baseplate',1e-5-parts['support_film'].cut(support).Volume)
no_overlap('film/module body',parts['support_film'],parts['controller_pcb'])
require('controller PCB to host minimum including rounded notch corners',parts['controller_pcb'].distToShape(main)[0],.2)
rf=bounds_box(module['rf_keepout_bounds'],-5,15)
for name in ['power','connector','connector_mated_allowance','battery']:
    require('RF component clearance '+name,no_overlap('RF/'+name,rf,parts[name]),0)
for name,shape in switches.items():require('RF switch clearance '+name,no_overlap('RF/'+name,rf,shape),0)
for name,shape in parts.items():
    if name.endswith(('_screw','_nut')):no_overlap('RF/'+name,rf,shape)
require('power actuator inside left outline',parts['power'].BoundBox.XMin-.4,.2)
for delta in [0,-1.5]:
    moving=parts['power'].copy();moving.translate(App.Vector(0,delta,0))
    no_overlap('power stroke '+str(delta)+'/battery',moving,parts['battery'])
    for key,cap in caps.items():no_overlap('power stroke '+str(delta)+'/'+key,moving,cap)
contacts=AUDIT['native_module_castellations'];bridges=[]
for c in contacts:
    number=int(c['number'])
    if number>14:continue
    host=next(p for p in FP['MCU1']['pads'] if p['number']==c['number'])
    x=host['center'][0]-center[0];y=c['center'][1];side=1 if y>0 else -1
    bridge=bounds_box([x-.4,min(side*8.8,side*10.5),x+.4,max(side*8.8,side*10.5)],0,.8)
    for other in contacts:
        if other['number']==c['number']:continue
        ox,oy=other['center']
        copper=Part.makeCylinder(other['copper_diameter']/2,.8,App.Vector(ox,oy,0))
        distance=no_overlap('bridge '+str(number)+'/castellation '+other['number'],bridge,copper)
        bridges.append(distance)
require('smallest bridge/other castellation clearance',min(bridges),.25)
require('native RF copper audit',1-AUDIT['rf_copper_intersections'],1)
require('native baseplate has no copper',1-AUDIT['baseplate_copper_objects'],1)
reset=parts['controller_reset'];b=reset.BoundBox
probe=Part.makeCylinder(1,12,App.Vector((b.XMin+b.XMax)/2,(b.YMin+b.YMax)/2,b.ZMax))
for name,shape in parts.items():
    if name not in ['controller_reset','controller_pcb','controller_solder','support_film','battery_wire']:
        no_overlap('reset 2 mm probe/'+name,probe,shape)
for name,cap in caps.items():no_overlap('reset probe/'+name,probe,cap)
usb=parts['controller_usb'].BoundBox
usb_access=box(usb.XMax,center[1]-6,-1,15,12,7)
for name,cap in caps.items():no_overlap('USB reference plug/'+name,usb_access,cap)
for name,shape in switches.items():no_overlap('USB reference plug/'+name,usb_access,shape)
intentional={frozenset(pair) for pair in [('controller_pcb','controller_solder'),('controller_pcb','battery_wire'),('battery','battery_leads'),('connector','connector_mated_allowance'),('battery_leads','connector_mated_allowance')]}
for i,(a,sa) in enumerate(parts.items()):
    for b,sb in list(parts.items())[i+1:]:
        if frozenset((a,b)) not in intentional:no_overlap(a+'/'+b,sa,sb)
models={}
for path in (ROOT/'ergogen-kikad/design/models').glob('*.wrl'):
    if path.stem in json.loads((ROOT/'ergogen-kikad/design/models/bounds.json').read_text()):models[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
contract={'status':'PASS within source-backed nominal envelopes; physical sample and assembly process validation remain required','coordinate_system':'fixed layout frame, x right, y up, main PCB top z=0; KiCad conversion x=origin.x+x, y=origin.y-y','origin_kicad':GEOMETRY['assembly_origin_kicad'],'pcb_bounds':[.4,18.75,98.1,77.25],'native_step_note':'Board-only STEP omits outer copper/mask. Native outline/hole solids are normalized to the nominal 1.6 mm full stack, as in the battery-floor proof.','pcb_outer_corner_radius':1.5,'pcb_stack':{'main':[-1.6,0],'baseplate':[-3.2,-1.6],'module':[-1.55,.05],'support_film':[-1.6,-1.55]},'keys':keys,'pcb_voids':{'main_battery_well':[6.45,42.45,64.55,53.55],'battery_well_corner_chamfer':.5,'main_controller_notch':module['notch_bounds'],'controller_notch_radius':.5,'baseplate_battery_wire_access':module['baseplate_access_windows']},'mounts':GEOMETRY['fixed_mounts'],'fasteners':SPEC['fasteners'],'components':{name:bound(s) for name,s in parts.items()},'operating_keepouts':{'rf':bound(rf),'reset_2mm_probe':bound(probe),'usb_reference_plug':bound(usb_access),'power_access':[-7.6,42.65,0,3.75,53.35,3],'power_actuator_motion_world_y':[-1.5,0]},'sources':SPEC['sources'],'board_sha256':{name:hashlib.sha256((OUTPUT/'pcbs'/name).read_bytes()).hexdigest() for name in ['macropad.kicad_pcb','baseplate.kicad_pcb']},'design_sha256':{name:hashlib.sha256((ROOT/'ergogen-kikad/design'/name).read_bytes()).hexdigest() for name in ['config.yaml','assembly.json','battery.json']},'minimum_clearances':{'module_to_native_host':round(parts['controller_pcb'].distToShape(main)[0],6),'solder_to_switch_shoulder':round(min(parts['controller_solder'].distToShape(s)[0] for s in switches.values()),6),'antenna_rf_to_switch':round(min(rf.distToShape(s)[0] for s in switches.values()),6),'antenna_rf_to_connector':round(rf.distToShape(parts['connector'])[0],6),'reset_probe_to_usb':round(probe.distToShape(parts['controller_usb'])[0],6),'actuator_inside_left_border':round(parts['power'].BoundBox.XMin-.4,6)},'component_models':{f['reference']:{'center':f['center'],'rotation':f['rotation'],'models':f['models']} for f in AUDIT['footprints'] if f['models']},'native_model_sources':{kind:{'path':SPEC[kind]['native_model'],'sha256':hashlib.sha256((STANDARD/SPEC[kind]['native_model']).read_bytes()).hexdigest()} for kind in ['power','connector']},'model_sha256':models,'minimum_cap_clearances':sorted(minima,key=lambda d:d['clearance'])[:15],'minimum_solder_bridge_to_other_castellation':round(min(bridges),6),'check_count':len(checks),'limitations':['Choc housing/pin models are nominal drawing references; clip compliance and actual board seating require a hardware trial. Cap mesh is rendering-only. Envelope proof excludes each cap mating to its own switch; cap cavity, stem fit and actual bottom-out must be checked with the purchased hardware.','XIAO component outlines follow official PCB; microphone and IMU are conservative optional Sense envelopes, not a claim that non-Sense Plus populates them; unmodelled small passives lie within the 21 x 17.8 mm module plan. Component heights and 1.6 mm module PCB thickness require sample confirmation.','Coplanar module requires 0.05 mm insulating support film with BAT wire access, controlled hand solder bridges, and a measured module/cutout fit. This is not a supplier-qualified mounting process.','JST mating plug is a conservative reserve with native header and metal tails; exact purchased plug/wire bend must fit it.','M2 fasteners are dimension references: procure heads no larger than 3.8 x 1.6 mm, 5 mm underhead length, and 4 mm AF x 1.6 mm nuts.','USB access is a 12 mm wide by 7 mm high reference cable reserve; check chosen cable boot. Case geometry is not evaluated here.'],'fabrication':SPEC['fabrication']}
(OUTPUT/'assembly-contract.json').write_text(json.dumps(contract,indent=2)+'\n')
(OUTPUT/'checks/assembly-clearance.json').write_text(json.dumps({'passed':True,'check_count':len(checks),'minimum_cap_clearances':contract['minimum_cap_clearances'],'minimum_solder_bridge_to_other_castellation':contract['minimum_solder_bridge_to_other_castellation'],'minimum_clearances':contract['minimum_clearances']},indent=2)+'\n')
print('Assembly envelope proof passed: '+str(len(checks))+' checks')
