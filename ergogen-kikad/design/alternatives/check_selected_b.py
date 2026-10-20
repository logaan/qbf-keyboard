from pathlib import Path
import json
import math
import pcbnew as pcb

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / 'placements.json').read_text())['five-column-15u']
BATTERY = json.loads((ROOT / 'selected-B-battery.json').read_text())


def bounds(x, y, w, h):
    return [x-w/2, y-h/2, x+w/2, y+h/2]


def gap(a, b):
    dx = max(a[0]-b[2], b[0]-a[2], 0)
    dy = max(a[1]-b[3], b[1]-a[3], 0)
    overlap = min(a[2], b[2])-max(a[0], b[0]) > 0.000001 and min(a[3], b[3])-max(a[1], b[1]) > 0.000001
    return math.hypot(dx, dy), overlap


def main():
    checks = []
    def record(name, value, minimum):
        checks.append({'name': name, 'clearance_mm': round(value, 6), 'minimum_mm': minimum})
        assert value >= minimum-0.000001, (name, value, minimum)
    switches = {s['label']: s for s in DATA['switches']}
    for i, x in enumerate([10.9, 29.95, 49, 68.05], 1):
        for prefix, y in [('b',34.25), ('t',61.75)]:
            key=switches[f'{prefix}{i}']
            assert abs(key['x']-x)<0.000001 and abs(key['y']-y)<0.000001
    for i in range(1,6):
        a,b=switches[f't{i}'],switches[f'b{i}']
        assert abs(a['x']-b['x'])<0.000001 and abs(a['y']+b['y']-96)<0.000001
        assert abs(a['y']+a['cap'][1]/2-75)<0.000001
        assert abs(b['y']-b['cap'][1]/2-21)<0.000001
    bodies={name:bounds(s['x'],s['y'],15,15) for name,s in switches.items()}
    bodies.update({'battery':bounds(32,48,57.5,10.5),'controller':bounds(20,85.75,36,18.3),'display':bounds(60,85.75,36,14),'display socket':bounds(43.3,85.75,2.54,12.7),'reset':bounds(81.5,53,6,6),'power':bounds(91.5,53,8.6,4.3),'JST housing':[83.25,40.05,90.85,45.95],'JST mating plug':[77.25,40.1,83.25,45.9]})
    for i,(name,a) in enumerate(bodies.items()):
        for other,b in list(bodies.items())[i+1:]:
            if {name,other} <= {'display','display socket'} or {name,other} <= {'JST housing','JST mating plug'}:
                continue
            value,overlap=gap(a,b)
            assert not overlap,(name,other)
            record(name+' to '+other,value,0)
    well=bounds(32,48,58.1,11.1)
    for name,s in switches.items():
        record('Battery well to '+name+' shoulder',gap(well,bodies[name])[0],0.5)
    board=pcb.LoadBoard(str(ROOT/'five-column-15u/pcbs/macropad.kicad_pcb'))
    pads=[]
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            center=pad.GetPosition();size=pad.GetSize()
            x,y=pcb.ToMM(center.x),-pcb.ToMM(center.y)
            angle=math.radians(pad.GetOrientationDegrees())
            width=abs(math.cos(angle))*pcb.ToMM(size.x)+abs(math.sin(angle))*pcb.ToMM(size.y)
            height=abs(math.sin(angle))*pcb.ToMM(size.x)+abs(math.cos(angle))*pcb.ToMM(size.y)
            envelope=bounds(x,y,width,height)
            name=fp.GetReference()+'/'+pad.GetNumber()
            pads.append((fp.GetReference(),name,envelope))
            record(name+' copper/drill to battery well',gap(envelope,well)[0],0.5)
            record(name+' copper/drill to PCB edge',min(envelope[0],envelope[1],98-envelope[2],96-envelope[3]),0.5)
    for i,(reference,name,a) in enumerate(pads):
        for other_reference,other,b in pads[i+1:]:
            if reference==other_reference:
                continue
            value,overlap=gap(a,b)
            assert not overlap,(name,other)
            record(name+' to '+other+' copper/drill',value,0.2)
    cap_clearances=[]
    for name,s in switches.items():
        cap=bounds(s['x'],s['y'],*s['cap'])
        for part in ['JST housing','JST mating plug','reset','power','controller','display','display socket']:
            value,overlap=gap(cap,bodies[part])
            assert not overlap,(name,part)
            cap_clearances.append({'key':name,'part':part,'plan_clearance_mm':round(value,6)})
    battery_top=BATTERY['bottom_z']+BATTERY['thickness']
    record('Battery top to full-travel cap underside',4-battery_top,0.5)
    record('Future 1 mm roof above battery with 0.3 mm gap to full-travel cap underside',4-(battery_top+0.3+1),0.5)
    record('Lead top to full-travel cap underside',4-BATTERY['maximum_lead_top_z'],0.5)
    result={'passed':True,'scope':'Conservative layout envelope checks only; unrouted PCB; native assembled geometry, case, firmware and fabrication checks deferred.','assumptions':{'full_travel_cap_underside_z_mm':4,'switch_shoulder_plan_mm':[15,15],'pad_method':'Axis-aligned outer copper/drill rectangles, conservative for circles and ovals; 0.5 mm to well and board edge; 0.2 mm between different footprints.','connector_mated_height_mm':4.85},'unchanged_main_eight':True,'cap_outer_edges_y_mm':[21,75],'horizontal_symmetry_axis_y_mm':48,'checks':checks,'cap_full_travel_plan_checks':cap_clearances,'minimum_well_to_shoulder_mm':min(gap(well,bodies[name])[0] for name in switches),'minimum_copper_drill_to_well_mm':min(gap(p[2],well)[0] for p in pads),'controller_display_body_gap_mm':gap(bodies['controller'],bodies['display'])[0],'maximum_battery_top_z_mm':battery_top,'maximum_wire_top_z_mm':BATTERY['maximum_lead_top_z']}
    result['checked_clearance_count'] = len(checks)
    result['closest_clearances'] = sorted(checks, key=lambda c:c['clearance_mm'])[:20]
    result.pop('checks')
    (ROOT/'selected-B-layout-checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Passed selected B layout geometry, cap edges, stationary keys, component bodies and pad/drill clearance checks')


if __name__=='__main__':
    main()
