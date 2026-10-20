from pathlib import Path
from datetime import date
import math
import argparse
import heapq
import itertools
import json
import re
import subprocess
import sys
import pcbnew as pcb
from attach_models import attach_models

OUTPUT=Path(__file__).resolve().parents[1]/'ergogen-kikad/generated'
BOARD=OUTPUT/'pcbs/macropad.kicad_pcb'
BASE_PLATE=OUTPUT/'pcbs/baseplate.kicad_pcb'
WIDTH_MM=0.30
GRID_MM=0.20
CLEARANCE_MM=0.25
PAGE_OFFSET_MM=(0,0)
DRAWING_TITLE='QBF XIAO Direct-Wired Keyboard'
WELL_COPPER_CLEARANCE_MM=0.5

def point(xy):
    return pcb.VECTOR2I(pcb.FromMM(xy[0]), pcb.FromMM(xy[1]))


def mm_point(vector):
    return (round(pcb.ToMM(vector.x), 4), round(pcb.ToMM(vector.y), 4))


def point_to_segment_distance(position, start, end):
    delta = (end[0] - start[0], end[1] - start[1])
    length_squared = delta[0] ** 2 + delta[1] ** 2
    fraction = max(0, min(1, ((position[0] - start[0]) * delta[0]
                               + (position[1] - start[1]) * delta[1])
                           / length_squared))
    closest = (start[0] + fraction * delta[0], start[1] + fraction * delta[1])
    return math.dist(position, closest)


def segment_distance(start1, end1, start2, end2):
    d1 = (end1[0] - start1[0], end1[1] - start1[1])
    d2 = (end2[0] - start2[0], end2[1] - start2[1])
    offset = (start1[0] - start2[0], start1[1] - start2[1])
    determinant = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(determinant) > 1e-12:
        t = (d2[0] * offset[1] - d2[1] * offset[0]) / determinant
        u = (d1[0] * offset[1] - d1[1] * offset[0]) / determinant
        if 0 <= t <= 1 and 0 <= u <= 1:
            return 0
    return min(point_to_segment_distance(start1, start2, end2),
               point_to_segment_distance(end1, start2, end2),
               point_to_segment_distance(start2, start1, end1),
               point_to_segment_distance(end2, start1, end1))


def pad_distance(pad, start, end):
    center = mm_point(pad.GetPosition())
    if pad.GetAttribute() == pcb.PAD_ATTRIB_NPTH:
        size = pad.GetDrillSize()
    else:
        size = pad.GetSize()
    if pad.GetShape() == pcb.PAD_SHAPE_CIRCLE:
        return point_to_segment_distance(center, start, end) - pcb.ToMM(size.x) / 2
    angle = math.radians(pad.GetOrientationDegrees())
    cosine, sine = math.cos(angle), math.sin(angle)
    half_x, half_y = pcb.ToMM(size.x) / 2, pcb.ToMM(size.y) / 2
    def local(position):
        x, y = position[0] - center[0], position[1] - center[1]
        return (x * cosine - y * sine, x * sine + y * cosine)
    first, last = local(start), local(end)
    if any(abs(x) <= half_x and abs(y) <= half_y for x, y in (first, last)):
        return 0
    corners = [(-half_x, -half_y), (half_x, -half_y),
               (half_x, half_y), (-half_x, half_y)]
    return min(segment_distance(first, last, corner, corners[(index + 1) % 4])
               for index, corner in enumerate(corners))


def route(board, net, layer, coordinates):
    previous_direction = None
    for start, end in zip(coordinates, coordinates[1:]):
        if start == end:
            continue
        direction = (round(end[0] - start[0], 6), round(end[1] - start[1], 6))
        if previous_direction and abs(sum(a * b for a, b in zip(previous_direction, direction))) < 1e-9:
            raise RuntimeError(f'90-degree turn in {net.GetNetname()} at {start}')
        dx = round(abs(end[0] - start[0]), 6)
        dy = round(abs(end[1] - start[1]), 6)
        if dx and dy and abs(dx - dy) > 0.000002:
            raise RuntimeError(f'Non-45-degree track in {net.GetNetname()}: {start}->{end}')
        track = pcb.PCB_TRACK(board)
        track.SetStart(point(start))
        track.SetEnd(point(end))
        track.SetWidth(pcb.FromMM(WIDTH_MM))
        track.SetLayer(layer)
        track.SetNetCode(net.GetNetCode())
        board.Add(track)
        previous_direction = direction


def battery_well_bounds(board):
    wells = [f for f in board.GetFootprints() if f.GetReference().startswith('WELL')]
    if len(wells) != 1:
        raise RuntimeError('Main PCB must have exactly one battery well')
    coordinates = [mm_point(position) for drawing in wells[0].GraphicalItems()
                   if drawing.GetLayer() == pcb.Edge_Cuts
                   for position in (drawing.GetStart(), drawing.GetEnd())]
    if len(coordinates) != 16:
        raise RuntimeError('Battery well must have eight closed chamfered edges')
    return (min(x for x, y in coordinates), min(y for x, y in coordinates),
            max(x for x, y in coordinates), max(y for x, y in coordinates))


def rectangle_edges(bounds):
    left, top, right, bottom = bounds
    corners = [(left, top), (right, top), (right, bottom), (left, bottom)]
    return [(corner, corners[(index + 1) % 4]) for index, corner in enumerate(corners)]


def check_battery_well(board):
    bounds = battery_well_bounds(board)
    left, top, right, bottom = bounds
    outer = board_bounds(board)
    if min(left - outer[0], top - outer[1], outer[2] - right, outer[3] - bottom) < 1.3:
        raise RuntimeError('Battery well must retain at least a 1.3 mm outer PCB web')
    for footprint in board.GetFootprints():
        for pad in footprint.Pads():
            center = mm_point(pad.GetPosition())
            if left <= center[0] <= right and top <= center[1] <= bottom:
                raise RuntimeError('Battery well includes a through-hole component pad')
            if min(pad_distance(pad, start, end) for start, end in rectangle_edges(bounds)) < WELL_COPPER_CLEARANCE_MM:
                raise RuntimeError('Battery well is too close to a component pad')
    return bounds


def board_bounds(board):
    coordinates = [mm_point(position) for drawing in board.GetDrawings()
                   if drawing.GetLayer() == pcb.Edge_Cuts
                   for position in (drawing.GetStart(), drawing.GetEnd())]
    return (min(x for x, y in coordinates), min(y for x, y in coordinates),
            max(x for x, y in coordinates), max(y for x, y in coordinates))


def cap_bounds(footprint):
    positions = [mm_point(position) for drawing in footprint.GraphicalItems()
                 if drawing.GetLayer() == pcb.Dwgs_User
                 for position in (drawing.GetStart(), drawing.GetEnd())]
    return (min(x for x, y in positions), min(y for x, y in positions),
            max(x for x, y in positions), max(y for x, y in positions))


def grid_point(position):
    return tuple(round(value / GRID_MM) for value in position)


def grid_mm(position):
    return tuple(round(value * GRID_MM, 6) for value in position)


def mark_obstacle(blocked, start, end, radius):
    left, top = grid_point((min(start[0], end[0]) - radius - GRID_MM,
                            min(start[1], end[1]) - radius - GRID_MM))
    right, bottom = grid_point((max(start[0], end[0]) + radius + GRID_MM,
                                max(start[1], end[1]) + radius + GRID_MM))
    for x in range(left, right + 1):
        for y in range(top, bottom + 1):
            position = grid_mm((x, y))
            distance = math.dist(position, start) if start == end else point_to_segment_distance(position, start, end)
            if distance < radius:
                blocked.add((x, y))


def terminal(start, end):
    dx, dy = end[0] - start[0], end[1] - start[1]
    diagonal = min(abs(dx), abs(dy))
    knee = (round(start[0] + math.copysign(diagonal, dx), 6),
            round(start[1] + math.copysign(diagonal, dy), 6))
    return [start, knee, end]


def smooth_path(coordinates):
    compact = []
    for position in coordinates:
        if compact and math.dist(compact[-1], position) < 1e-6:
            continue
        compact.append(position)
        while len(compact) >= 3:
            a, b, c = compact[-3:]
            first, second = (b[0] - a[0], b[1] - a[1]), (c[0] - b[0], c[1] - b[1])
            if abs(first[0] * second[1] - first[1] * second[0]) > 1e-6 or sum(x * y for x, y in zip(first, second)) <= 0:
                break
            compact.pop(-2)
    result = [compact[0]]
    for a, b, c in zip(compact, compact[1:], compact[2:]):
        first, second = (b[0] - a[0], b[1] - a[1]), (c[0] - b[0], c[1] - b[1])
        if abs(sum(x * y for x, y in zip(first, second))) < 1e-6:
            trim = min(GRID_MM / 2, math.hypot(*first) / 3, math.hypot(*second) / 3)
            result.append(tuple(round(b[i] - first[i] / math.hypot(*first) * trim, 6) for i in (0, 1)))
            result.append(tuple(round(b[i] + second[i] / math.hypot(*second) * trim, 6) for i in (0, 1)))
        else:
            result.append(b)
    return result + [compact[-1]]


def assembly_spec():
    return json.loads((Path(__file__).resolve().parents[1] / 'ergogen-kikad/design/assembly.json').read_text())


def add_rectangle(board,bounds,layer=pcb.Edge_Cuts):
    for a,b in rectangle_edges(bounds):
        shape=pcb.PCB_SHAPE(board)
        shape.SetShape(pcb.SHAPE_T_SEGMENT)
        shape.SetStart(point(a));shape.SetEnd(point(b));shape.SetLayer(layer);shape.SetWidth(pcb.FromMM(0.05))
        board.Add(shape)


def add_rounded_rectangle(board,bounds,r):
    x0,y0,x1,y1=bounds
    lines=[((x0+r,y0),(x1-r,y0)),((x1,y0+r),(x1,y1-r)),((x1-r,y1),(x0+r,y1)),((x0,y1-r),(x0,y0+r))]
    for start,end in lines:
        shape=pcb.PCB_SHAPE(board);shape.SetShape(pcb.SHAPE_T_SEGMENT);shape.SetStart(point(start));shape.SetEnd(point(end));shape.SetLayer(pcb.Edge_Cuts);shape.SetWidth(pcb.FromMM(0.05));board.Add(shape)
    d=r/math.sqrt(2)
    arcs=[((x1-r,y0),(x1-r+d,y0+r-d),(x1,y0+r)),((x1,y1-r),(x1-r+d,y1-r+d),(x1-r,y1)),((x0+r,y1),(x0+r-d,y1-r+d),(x0,y1-r)),((x0,y0+r),(x0+r-d,y0+r-d),(x0+r,y0))]
    for start,mid,end in arcs:
        shape=pcb.PCB_SHAPE(board);shape.SetShape(pcb.SHAPE_T_ARC);shape.SetArcGeometry(point(start),point(mid),point(end));shape.SetLayer(pcb.Edge_Cuts);shape.SetWidth(pcb.FromMM(0.05));board.Add(shape)


def fixed_to_kicad(bounds):
    return [bounds[0],-bounds[3],bounds[2],-bounds[1]]


def make_base_plate():
    global PAGE_OFFSET_MM
    source=pcb.LoadBoard(str(BOARD))
    plate=pcb.BOARD()
    plate.GetDesignSettings().SetBoardThickness(pcb.FromMM(1.6))
    raw=board_bounds(source)
    PAGE_OFFSET_MM=(210-(raw[0]+raw[2])/2,148.5-(raw[1]+raw[3])/2)
    add_rounded_rectangle(plate,raw,1.5)
    for source_fp in source.GetFootprints():
        reference=source_fp.GetReference()
        if not reference.startswith(('S','H','PWR')):continue
        fp=pcb.FOOTPRINT(plate);fp.SetReference(reference);fp.SetPosition(source_fp.GetPosition());fp.Reference().SetVisible(False);fp.Value().SetVisible(False);plate.Add(fp)
        for source_pad in source_fp.Pads():
            if reference.startswith('PWR') and source_pad.GetAttribute()!=pcb.PAD_ATTRIB_NPTH:continue
            size=source_pad.GetDrillSize() if source_pad.GetAttribute()==pcb.PAD_ATTRIB_NPTH else point((2.8,2.8))
            pad=pcb.PAD(fp);pad.SetAttribute(pcb.PAD_ATTRIB_NPTH);pad.SetShape(pcb.PAD_SHAPE_CIRCLE);pad.SetPosition(source_pad.GetPosition());pad.SetSize(size);pad.SetDrillSize(size);pad.SetLayerSet(pcb.LSET.AllCuMask());fp.Add(pad)
    access=assembly_spec()['module']['baseplate_access_windows']
    x0=min(b[0] for b in access);x1=max(b[2] for b in access)
    low=min(b[1] for b in access);high=max(b[3] for b in access)
    points=[(access[0][0],high),(access[0][2],high),(access[0][2],low),(x0,low),(x0,access[1][3]),(access[0][0],access[1][3])]
    for a,b in zip(points,points[1:]+points[:1]):
        edge=pcb.PCB_SHAPE(plate);edge.SetShape(pcb.SHAPE_T_SEGMENT);edge.SetStart(point((a[0],-a[1])));edge.SetEnd(point((b[0],-b[1])));edge.SetLayer(pcb.Edge_Cuts);edge.SetWidth(pcb.FromMM(0.05));plate.Add(edge)
    plate.GetTitleBlock().SetTitle('QBF circuit-free insulating baseplate')
    plate.RemoveUnusedNets(None)
    plate.Move(point(PAGE_OFFSET_MM));pcb.SaveBoard(str(BASE_PLATE),plate)
    if len([pad for fp in plate.GetFootprints() for pad in fp.Pads()])!=56:
        raise RuntimeError('Expected 50 switch clearances, four M2 holes and two power locating holes')
    if list(plate.GetTracks()) or list(plate.Zones()):raise RuntimeError('Baseplate contains copper routing')


def check_layout(board,output):
    parts={fp.GetReference():fp for fp in board.GetFootprints()}
    switches=[fp for fp in parts.values() if fp.GetReference().startswith('S')]
    mounts=[mm_point(fp.GetPosition()) for fp in parts.values() if fp.GetReference().startswith('H')]
    if len(switches)!=10 or len(mounts)!=4 or 'MCU1' not in parts or any(r.startswith(('LCD','RST')) for r in parts):
        raise RuntimeError('Expected ten direct keys, one XIAO, four mounts, no display or external reset')
    left,top,right,bottom=board_bounds(board)
    if any(abs(a-b)>0.001 for a,b in zip([left,top,right,bottom],[0.4,-77.25,98.1,-18.75])):raise RuntimeError('Fixed outline changed')
    if set(mounts)!={(20.425,-23.5),(20.425,-72.5),(58.525,-23.5),(58.525,-72.5)}:raise RuntimeError('Mount positions changed')
    for fp in switches:
        labels=[item.GetText() for item in fp.GraphicalItems() if hasattr(item,'GetText') and re.fullmatch('[tb][1-5]',item.GetText())]
        if len(labels)!=1:raise RuntimeError('Missing key label')
        name=labels[0];i=int(name[1])-1
        x=87.1 if i==4 else [10.9,29.95,49,68.05][i]
        y=(66.75 if name[0]=='t' else 29.25) if i==4 else (61.75 if name[0]=='t' else 34.25)
        if mm_point(fp.GetPosition())!=(x,-y):raise RuntimeError('Key position changed: '+name)
        signal='D'+str(i+(0 if name[0]=='t' else 5))
        if sorted(p.GetNetname() for p in fp.Pads() if p.GetNetname())!=sorted(['GND',signal]):raise RuntimeError('Incorrect direct wiring: '+name)
        cap=cap_bounds(fp)
        if min(cap[0]-left,cap[1]-top,right-cap[2],bottom-cap[3])<2.249:raise RuntimeError('Cap border less than 2.25 mm')
    if mm_point(parts['MCU1'].GetPosition())!=(87.5,-47.5):raise RuntimeError('XIAO position changed')
    if len(list(parts['MCU1'].Pads()))!=14:raise RuntimeError('Expected official 14 standard castellations')
    well=check_battery_well(board)
    spec=json.loads((Path(__file__).resolve().parents[1]/'ergogen-kikad/design/battery.json').read_text())
    geometry={'origin_kicad':[left+PAGE_OFFSET_MM[0],bottom+PAGE_OFFSET_MM[1]],'assembly_origin_kicad':[PAGE_OFFSET_MM[0],PAGE_OFFSET_MM[1]],'assembly_bounds_mm':[left,-bottom,right,-top],'width':round(right-left,3),'height':round(bottom-top,3),'mounts':[{'x':x-left,'y':bottom-y} for x,y in mounts],'fixed_mounts':[{'x':x,'y':-y} for x,y in mounts],'battery_well':{'x':well[0]-left,'y':bottom-well[3],'length':well[2]-well[0],'width':well[3]-well[1],'corner_chamfer':0.5,'main_pcb_only':True,'baseplate_floor_z':-3.2,'baseplate_top_z':-1.6},'battery':{'x':spec['center'][0]-left,'y':spec['center'][1]+bottom,'length':spec['length'],'width':spec['width'],'thickness':spec['thickness'],'bottom_z':spec['bottom_z'],'top_z':spec['bottom_z']+spec['thickness'],'model':spec['model'],'capacity_mah':spec['capacity_mah']},'controller':assembly_spec()['module'],'controls':[]}
    (output/'board_geometry.json').write_text(json.dumps(geometry,indent=2)+'\n')
    print('Validated fixed 97.7 x 58.5 mm layout and ten direct GPIO nets',flush=True)


def add_rule_area(board,bounds,name,layer):
    area=pcb.ZONE(board);area.SetIsRuleArea(True);area.SetPlacementAreaEnabled(False)
    area.SetLayer(layer);area.SetDoNotAllowTracks(True);area.SetDoNotAllowVias(True);area.SetDoNotAllowPads(True);area.SetDoNotAllowZoneFills(True);area.SetZoneName(name)
    outline=area.Outline();outline.NewOutline()
    for p in [(bounds[0],bounds[1]),(bounds[2],bounds[1]),(bounds[2],bounds[3]),(bounds[0],bounds[3])]:outline.Append(*point(p))
    board.Add(area)


def add_ground_zone(board,ground,layer):
    zone=pcb.ZONE(board);zone.SetLayer(layer);zone.SetNetCode(ground.GetNetCode());zone.SetMinThickness(pcb.FromMM(0.1));zone.SetLocalClearance(pcb.FromMM(CLEARANCE_MM));zone.SetThermalReliefGap(pcb.FromMM(0.25));zone.SetThermalReliefSpokeWidth(pcb.FromMM(0.3));zone.SetIslandRemovalMode(pcb.ISLAND_REMOVAL_MODE_ALWAYS)
    polygon=zone.Outline();polygon.NewOutline()
    left,top,right,bottom=board_bounds(board)
    for p in [(left,top),(right,top),(right,bottom),(left,bottom)]:polygon.Append(*point(p))
    board.Add(zone)


def pad_layers(pad):
    return [i for i,layer in enumerate((pcb.F_Cu,pcb.B_Cu)) if pad.IsOnLayer(layer)]


def route_blocked(board,net):
    blocked=[set(),set()]
    margin=WIDTH_MM/2+CLEARANCE_MM+GRID_MM/math.sqrt(2)+0.01
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetAttribute()!=pcb.PAD_ATTRIB_NPTH and pad.GetNetCode()==net.GetNetCode():continue
            bb=pad.GetBoundingBox();x1,y1,x2,y2=[pcb.ToMM(v) for v in (bb.GetLeft(),bb.GetTop(),bb.GetRight(),bb.GetBottom())]
            layers=[0,1] if pad.GetAttribute()==pcb.PAD_ATTRIB_NPTH else pad_layers(pad)
            gx1,gy1=grid_point((x1-margin-GRID_MM,y1-margin-GRID_MM));gx2,gy2=grid_point((x2+margin+GRID_MM,y2+margin+GRID_MM))
            for gx in range(gx1,gx2+1):
                for gy in range(gy1,gy2+1):
                    x,y=grid_mm((gx,gy))
                    if math.hypot(max(x1-x,x-x2,0),max(y1-y,y-y2,0))<margin:
                        for layer in layers:blocked[layer].add((gx,gy))
    for track in board.GetTracks():
        if track.GetNetCode()==net.GetNetCode():continue
        layers=[0,1] if isinstance(track,pcb.PCB_VIA) else [0 if track.GetLayer()==pcb.F_Cu else 1]
        for layer in layers:mark_obstacle(blocked[layer],mm_point(track.GetStart()),mm_point(track.GetEnd()),pcb.ToMM(track.GetWidth(pcb.F_Cu) if isinstance(track,pcb.PCB_VIA) else track.GetWidth())/2+margin)
    exclusions=[(battery_well_bounds(board),0.5),(fixed_to_kicad(assembly_spec()['module']['notch_bounds']),0.25),(fixed_to_kicad(assembly_spec()['module']['rf_keepout_bounds']),0)]
    for bounds,edge_clearance in exclusions:
        radius=WIDTH_MM/2+edge_clearance+GRID_MM/math.sqrt(2)+0.01
        gx1,gy1=grid_point((bounds[0]-radius-GRID_MM,bounds[1]-radius-GRID_MM));gx2,gy2=grid_point((bounds[2]+radius+GRID_MM,bounds[3]+radius+GRID_MM))
        for gx in range(gx1,gx2+1):
            for gy in range(gy1,gy2+1):
                x,y=grid_mm((gx,gy))
                if bounds[0]-radius<=x<=bounds[2]+radius and bounds[1]-radius<=y<=bounds[3]+radius:
                    blocked[0].add((gx,gy));blocked[1].add((gx,gy))
    return blocked


def find_multilayer_path(board,net,first,last):
    blocked=route_blocked(board,net)
    origin,target=grid_point(mm_point(first.GetPosition())),grid_point(mm_point(last.GetPosition()))
    starts=[(layer,*origin) for layer in pad_layers(first) if origin not in blocked[layer]]
    targets={(layer,*target) for layer in pad_layers(last) if target not in blocked[layer]}
    if not starts or not targets:raise RuntimeError('Blocked endpoint for '+net.GetNetname())
    left,top,right,bottom=board_bounds(board);xmin,ymin=grid_point((left+0.7,top+0.7));xmax,ymax=grid_point((right-0.7,bottom-0.7))
    def heuristic(state):return math.hypot(state[1]-target[0],state[2]-target[1])
    serial=itertools.count();queue=[];cost={};parents={}
    for start in starts:cost[start]=0;heapq.heappush(queue,(heuristic(start),next(serial),start))
    visited=set();directions=[(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
    while queue:
        _,_,current=heapq.heappop(queue)
        if current in visited:continue
        if current in targets:
            result=[current]
            while current in parents:current=parents[current];result.append(current)
            return list(reversed(result))
        visited.add(current);layer,x,y=current
        neighbors=[((layer,x+dx,y+dy),math.hypot(dx,dy)) for dx,dy in directions]
        if all((x+dx,y+dy) not in blocked[other] for other in [0,1] for dx in [-1,0,1] for dy in [-1,0,1]):neighbors.append(((1-layer,x,y),15))
        for neighbor,step in neighbors:
            nl,nx,ny=neighbor
            if not xmin<=nx<=xmax or not ymin<=ny<=ymax or neighbor in visited or (nx,ny) in blocked[nl]:continue
            if nl==layer and nx!=x and ny!=y and ((nx,y) in blocked[layer] or (x,ny) in blocked[layer]):continue
            value=cost[current]+step
            if value<cost.get(neighbor,math.inf):cost[neighbor]=value;parents[neighbor]=current;heapq.heappush(queue,(value+heuristic(neighbor),next(serial),neighbor))
    raise RuntimeError('No multilayer route for '+net.GetNetname())


def route_connection(board,net,first,last):
    path=find_multilayer_path(board,net,first,last)
    section=terminal(mm_point(first.GetPosition()),grid_mm(path[0][1:]));layer=path[0][0]
    for state in path:
        position=grid_mm(state[1:])
        if state[0]!=layer:
            route(board,net,[pcb.F_Cu,pcb.B_Cu][layer],smooth_path(section+[position]))
            via=pcb.PCB_VIA(board);via.SetPosition(point(position));via.SetWidth(pcb.FromMM(0.65));via.SetDrill(pcb.FromMM(0.3));via.SetLayerPair(pcb.F_Cu,pcb.B_Cu);via.SetNetCode(net.GetNetCode());board.Add(via)
            section=[position];layer=state[0]
        else:section.append(position)
    section+=terminal(section[-1],mm_point(last.GetPosition()))[1:]
    section=terminal(section[0],section[1])+section[2:] if len(section)>1 else section
    route(board,net,[pcb.F_Cu,pcb.B_Cu][layer],smooth_path(section))


def add_connector_ground_stitch(board):
    net=board.FindNet('GND')
    pad=next(p for fp in board.GetFootprints() if fp.GetReference()=='J1' for p in fp.Pads() if p.GetNetname()=='GND')
    position=(72.4,-47.4)
    route(board,net,pcb.F_Cu,smooth_path(terminal(mm_point(pad.GetPosition()),position)))
    via=pcb.PCB_VIA(board);via.SetPosition(point(position));via.SetWidth(pcb.FromMM(0.65));via.SetDrill(pcb.FromMM(0.3));via.SetLayerPair(pcb.F_Cu,pcb.B_Cu);via.SetNetCode(net.GetNetCode());board.Add(via)


def route_signals(board):
    endpoints={}
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetname():endpoints.setdefault(pad.GetNetname(),[]).append(pad)
    expected={**{'D'+str(i):2 for i in range(10)},'BAT_POS':2,'VBAT':2}
    if any(len(endpoints.get(name,[]))!=count for name,count in expected.items()):raise RuntimeError('Incorrect direct-key or battery net terminal count')
    connections=[]
    for name,pads in endpoints.items():
        connected,pending=pads[:1],pads[1:]
        while pending:
            a,b=min(itertools.product(connected,pending),key=lambda pair:math.dist(mm_point(pair[0].GetPosition()),mm_point(pair[1].GetPosition())))
            connections.append((name,a,b));connected.append(b);pending.remove(b)
    connections.sort(key=lambda c:(0 if c[0]=='BAT_POS' else 1 if c[0]=='VBAT' else 3 if c[0]=='GND' else 2,math.dist(mm_point(c[1].GetPosition()),mm_point(c[2].GetPosition()))))
    for name,a,b in connections:
        if name=='GND' and not any(p.GetParentFootprint().GetReference()=='MCU1' for p in [a,b]):continue
        print('Routing '+name+' '+str(mm_point(a.GetPosition()))+' -> '+str(mm_point(b.GetPosition())),flush=True)
        route_connection(board,board.FindNet(name),a,b)


def check_board(board):
    board.BuildConnectivity()
    if board.GetConnectivity().GetUnconnectedCount(False):raise RuntimeError('Routed board has unconnected nets')
    copper=[zone for zone in board.Zones() if not zone.GetIsRuleArea()]
    if len(copper)!=2 or not all(zone.IsFilled() for zone in copper):raise RuntimeError('Expected two filled ground zones')
    check_battery_well(board)


def main():
    global BOARD,BASE_PLATE,PAGE_OFFSET_MM
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=OUTPUT);parser.add_argument('--baseplate',action='store_true');args=parser.parse_args()
    BOARD=args.output/'pcbs/macropad.kicad_pcb';BASE_PLATE=args.output/'pcbs/baseplate.kicad_pcb'
    if args.baseplate:make_base_plate();return
    subprocess.run([sys.executable,__file__,'--output',str(args.output),'--baseplate'],check=True)
    board=pcb.LoadBoard(str(BOARD))
    if list(board.GetTracks()) or list(board.Zones()):raise RuntimeError('Expected fresh Ergogen board')
    left,top,right,bottom=board_bounds(board);PAGE_OFFSET_MM=(210-(left+right)/2,148.5-(top+bottom)/2)
    check_layout(board,args.output);add_connector_ground_stitch(board);route_signals(board)
    print('Adding RF rule area',flush=True)
    well=battery_well_bounds(board)
    for layer in [pcb.F_Cu,pcb.B_Cu]:
        add_rule_area(board,fixed_to_kicad(assembly_spec()['module']['rf_keepout_bounds']),'ANT1 3 mm RF keepout',layer)
        add_rule_area(board,[well[0]-0.5,well[1]-0.5,well[2]+0.5,well[3]+0.5],'Battery well 0.5 mm copper clearance',layer)
    print('Adding ground zones',flush=True)
    for layer in [pcb.F_Cu,pcb.B_Cu]:add_ground_zone(board,board.FindNet('GND'),layer)
    print('Assigning models',flush=True)
    board.GetTitleBlock().SetTitle(DRAWING_TITLE);board.GetTitleBlock().SetDate(date.today().isoformat())
    attach_models(board);board.Move(point(PAGE_OFFSET_MM));board.BuildConnectivity();print('Filling ground zones',flush=True);pcb.ZONE_FILLER(board).Fill(board.Zones());board.BuildConnectivity();pcb.SaveBoard(str(BOARD),board)
    check_board(pcb.LoadBoard(str(BOARD)));print('Routed '+str(len(list(board.GetTracks())))+' tracks/vias with no opens',flush=True)


if __name__=='__main__':main()
