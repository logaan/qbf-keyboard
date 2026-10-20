from pathlib import Path
import json
import math
import sys
import pcbnew as pcb

ROOT=Path(__file__).resolve().parent
BOARD=pcb.LoadBoard(sys.argv[1])


def xy(position):
    return [round(pcb.ToMM(position.x),6),round(-pcb.ToMM(position.y),6)]


def box_gap(a,b):
    return math.hypot(max(a[0]-b[2],b[0]-a[2],0),max(a[1]-b[3],b[1]-a[3],0))


def main():
    expected_bounds=[0.4,18.75,98.1,77.25]
    switches={}
    mounts=[]
    components={}
    for footprint in BOARD.GetFootprints():
        reference=footprint.GetReference()
        position=xy(footprint.GetPosition())
        entry={'reference':reference,'position':position,'rotation':footprint.GetOrientationDegrees(),'footprint':str(footprint.GetFPID().GetLibItemName()),'pad_count':len(list(footprint.Pads()))}
        components[reference]=entry
        if reference.startswith('S'):
            labels=[item.GetText() for item in footprint.GraphicalItems() if hasattr(item,'GetText') and item.GetText() in ['t1','t2','t3','t4','t5','b1','b2','b3','b4','b5']]
            assert len(labels)==1
            label=labels[0]
            cap=[17.5,16.5] if label.endswith('5') else [16.5,26.5]
            signal=[pad.GetNetname() for pad in footprint.Pads() if pad.GetNetname() and pad.GetNetname()!='GND']
            assert len(signal)==1
            switches[label]={**entry,'cap_mm':cap,'signal':signal[0]}
        if reference.startswith('H'):
            mounts.append(position)
    assert len(switches)==10 and len(mounts)==4
    assert sorted(mounts)==sorted([[20.425,23.5],[20.425,72.5],[58.525,23.5],[58.525,72.5]])
    margins=[]
    for row,ys in [('t',61.75),('b',34.25)]:
        for i,x in enumerate([10.9,29.95,49,68.05],1):
            key=switches[row+str(i)]
            assert key['position']==[x,ys] and key['rotation']==90
    assert switches['t5']['position']==[87.1,66.75]
    assert switches['b5']['position']==[87.1,29.25]
    for i in range(1,6):
        top,bottom=switches['t'+str(i)],switches['b'+str(i)]
        assert abs(top['position'][1]+bottom['position'][1]-96)<0.000001
        assert abs(top['position'][1]+top['cap_mm'][1]/2-75)<0.000001
        assert abs(bottom['position'][1]-bottom['cap_mm'][1]/2-21)<0.000001
    for label,key in switches.items():
        x,y=key['position'];w,h=key['cap_mm']
        margin=min(x-w/2-expected_bounds[0],y-h/2-expected_bounds[1],expected_bounds[2]-x-w/2,expected_bounds[3]-y-h/2)
        assert margin>=2.25-0.000001
        margins.append(margin)
        assert key['signal']=='D'+str((0 if label.startswith('t') else 5)+int(label[1])-1)
    controller=next(c for c in components.values() if 'XIAO' in c['footprint'])
    assert controller['position']==[87.5,48] and controller['pad_count']==0
    assert not any(any(token in c['footprint'] for token in ['Nice_Nano','Nice_View','reset','SW_PUSH']) for c in components.values())
    power=next(c for c in components.values() if c['footprint']=='CK_PCM12SMTR')
    power_fp=next(fp for fp in BOARD.GetFootprints() if fp.GetReference()==power['reference'])
    power_fab=[]
    for drawing in power_fp.GraphicalItems():
        if hasattr(drawing,'GetStart') and hasattr(drawing,'GetEnd') and drawing.GetLayer()==pcb.F_Fab:
            power_fab.extend([xy(drawing.GetStart()),xy(drawing.GetEnd())])
    actuator_left=min(p[0] for p in power_fab)
    actuator_inset=actuator_left-expected_bounds[0]
    assert actuator_inset>=0.25-0.000001
    copper_right=max(pcb.ToMM(pad.GetBoundingBox().GetRight()) for pad in power_fp.Pads() if pad.GetAttribute()!=pcb.PAD_ATTRIB_NPTH)
    well=[6.45,42.45,64.55,53.55]
    power_copper_clearance=well[0]-copper_right
    assert power_copper_clearance>=0.3
    shoulder_clearance=min(box_gap(well,[s['position'][0]-7.5,s['position'][1]-7.5,s['position'][0]+7.5,s['position'][1]+7.5]) for s in switches.values())
    assert shoulder_clearance>=0.7-0.000001
    for footprint in BOARD.GetFootprints():
        for pad in footprint.Pads():
            bb=pad.GetBoundingBox()
            envelope=[pcb.ToMM(bb.GetLeft()),-pcb.ToMM(bb.GetBottom()),pcb.ToMM(bb.GetRight()),-pcb.ToMM(bb.GetTop())]
            assert box_gap(envelope,well)>=0.3,(footprint.GetReference(),pad.GetNumber(),envelope)
    outline=BOARD.GetBoardEdgesBoundingBox()
    stroke_bounds=[pcb.ToMM(outline.GetLeft()),-pcb.ToMM(outline.GetBottom()),pcb.ToMM(outline.GetRight()),-pcb.ToMM(outline.GetTop())]
    radius=max(pcb.ToMM(drawing.GetWidth()) for drawing in BOARD.GetDrawings() if drawing.GetLayer()==pcb.Edge_Cuts)/2
    centerline_bounds=[stroke_bounds[0]+radius,stroke_bounds[1]+radius,stroke_bounds[2]-radius,stroke_bounds[3]-radius]
    assert all(abs(a-b)<=0.000001 for a,b in zip(centerline_bounds,expected_bounds))
    result={'passed':True,'stage':'1: Ergogen geometry only','manufacturing_ready':False,'board_bounds_mm':expected_bounds,'board_mm':[97.7,58.5],'outline_stroke_bounds_mm':stroke_bounds,'minimum_cap_margin_mm':round(min(margins),6),'cap_outer_edges_y_mm':[21,75],'key_symmetry_axis_y_mm':48,'mounts':mounts,'power_actuator_minimum_x_mm':actuator_left,'power_actuator_pcb_inset_mm':round(actuator_inset,6),'power_rear_copper_to_well_mm':round(power_copper_clearance,6),'minimum_well_to_switch_shoulder_mm':round(shoulder_clearance,6),'switches':switches,'components':components,'deferred':['XIAO electrical landing pattern and coplanar cutout','Full mated JST-SH dimensions and battery lead routing','Copper routing, fabrication DRC and native component models','Firmware GPIO implementation','Mechanical and case design after prior stages are complete']}
    (ROOT/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['passed','board_mm','minimum_cap_margin_mm','power_actuator_pcb_inset_mm','power_rear_copper_to_well_mm','minimum_well_to_switch_shoulder_mm']}))


if __name__=='__main__':
    main()
