from pathlib import Path
import json
import math
from html import escape

ROOT=Path(__file__).resolve().parent
P=json.loads((ROOT/'no-display-compact-layout.json').read_text())
S=10
OX,OY=180,245
X0,Y0,X1,Y1=P['board_bounds']
E=[]


def point(x,y):
    return OX+(x-X0)*S,OY+(Y1-y)*S


def text(x,y,label,size=20,color='#283a4c',weight='400',anchor='start',rotate=None):
    label=escape(label)
    transform='' if rotate is None else f'transform="rotate({rotate} {x} {y})"'
    E.append(f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}" {transform}>{label}</text>')


def line(x1,y1,x2,y2,color='#7b8b9c',dash='',arrows=False,width=1.5):
    markers='marker-start="url(#arrow)" marker-end="url(#arrow)"' if arrows else ''
    E.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" stroke-dasharray="{dash}" {markers}/>')


def rect(bounds,fill,stroke,r=4,dash='',opacity=1,width=1.7):
    x0,y0,x1,y1=bounds;x,y=point(x0,y1)
    E.append(f'<rect x="{x}" y="{y}" width="{(x1-x0)*S}" height="{(y1-y0)*S}" rx="{r}" fill="{fill}" fill-opacity="{opacity}" stroke="{stroke}" stroke-width="{width}" stroke-dasharray="{dash}"/>')


def bounds(center,size):
    x,y=center;w,h=size[:2]
    return [x-w/2,y-h/2,x+w/2,y+h/2]


def gap(a,b):
    return math.hypot(max(a[0]-b[2],b[0]-a[2],0),max(a[1]-b[3],b[1]-a[3],0))


def label(x,y,caption,size=18,color='#283a4c',weight='400'):
    px,py=point(x,y);text(px,py,caption,size,color,weight,'middle')


def circle(x,y,r,fill,stroke,width=1.6,dash=''):
    px,py=point(x,y)
    E.append(f'<circle cx="{px}" cy="{py}" r="{r*S}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-dasharray="{dash}"/>')


def check(keys):
    shoulders={k['label']:bounds(k['center'],P['switch_shoulder_mm']) for k in keys}
    caps={k['label']:bounds(k['center'],k['cap']) for k in keys}
    controller=bounds(P['controller']['center'],P['controller']['body_mm'])
    well=bounds(P['battery']['center'],P['battery']['well_mm'])
    pack=bounds(P['battery']['center'],P['battery']['envelope_mm'])
    report={'scope':'Nominal layout envelopes only; no routed PCB or assembled geometry validation.','board_mm':[X1-X0,Y1-Y0],'main_eight_unchanged':True,'fifth_center_inward_shift_each_mm':0.6,'checks':[]}
    def clearance(name,value,minimum):
        assert value>=minimum-0.000001,(name,value,minimum)
        report['checks'].append({'name':name,'clearance_mm':round(value,6),'minimum_mm':minimum})
    for name,cap in caps.items():
        clearance(name+' cap to XIAO body',gap(cap,controller),1 if name.endswith('5') else 0.5)
        clearance(name+' cap to board outline',min(cap[0]-X0,cap[1]-Y0,X1-cap[2],Y1-cap[3]),1.5)
    for name,shoulder in shoulders.items():
        clearance('Battery well to '+name+' shoulder',gap(well,shoulder),0.5)
    clearance('Power courtyard to battery well',gap(P['power']['courtyard_bounds'],well),0.8)
    clearance('Battery well to JST-SH allowance',gap(well,P['connector']['assembly_allowance_bounds']),1)
    clearance('JST-SH allowance to XIAO body',gap(P['connector']['assembly_allowance_bounds'],controller),1)
    for x,y in P['mounts']['centers']:
        r=P['mounts']['screw_keepout_diameter']/2
        for name,shoulder in shoulders.items():
            clearance(f'Mount {x},{y} screw allowance to '+name+' shoulder',gap([x,y,x,y],shoulder)-r,0.3)
        clearance(f'Mount {x},{y} screw allowance to PCB edge',min(x-X0,y-Y0,X1-x,Y1-y)-r,1.5)
    for center in P['mounts']['centers']:
        assert P['assumed_full_travel_cap_underside_z']-P['mounts']['proposed_top_head_height_max']>=2
    for x in P['main_columns_x']:
        assert abs(P['main_rows_y'][0]+P['main_rows_y'][1]-96)<0.000001
    assert abs(sum(P['fifth_rows_y'])-96)<0.000001
    report['passed']=True
    report['usb_projection_beyond_pcb_mm']=controller[2]+P['controller']['usb_right_projection']-X1
    report['power_actuator_projection_beyond_pcb_mm']=X0-P['power']['actuator_left_x']
    report['battery_top_z_mm']=P['battery']['bottom_z']+P['battery']['envelope_mm'][2]
    report['full_travel_cap_to_screw_head_vertical_allowance_mm']=P['assumed_full_travel_cap_underside_z']-P['mounts']['proposed_top_head_height_max']
    (ROOT/'no-display-compact-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    return pack,well,controller


keys=[]
for i,x in enumerate(P['main_columns_x'],1):
    for row,y in zip(['b','t'],P['main_rows_y']):
        keys.append({'label':row+str(i),'center':[x,y],'cap':P['main_cap_mm']})
for row,y in zip(['b','t'],P['fifth_rows_y']):
    keys.append({'label':row+'5','center':[P['fifth_column_x'],y],'cap':P['fifth_cap_mm']})
pack,well,controller=check(keys)
text(100,55,'No display · Compact XIAO layout',33,weight='600')
text(100,91,'Main eight switches unchanged · Fifth keys 1 mm clear of XIAO · Left-facing power · Onboard reset',21,color='#5a6e82')
rect(P['board_bounds'],'#ffffff','#8396aa',r=P['corner_radius']*S,width=2)
for key in keys:
    rect(bounds(key['center'],key['cap']),'#e7eef8','#8299b9',r=5)
    rect(bounds(key['center'],P['switch_shoulder_mm']),'none','#718397',r=2,dash='4 4',width=1.3)
    label(key['center'][0],key['center'][1]-0.5,key['label'],22,weight='600')
rect(well,'none','#63924f',r=3,dash='2 4',width=2)
rect(pack,'none','#507f3d',r=3,dash='8 5',width=2)
label(35.5,48.1,'Protected 301055',19,'#406d31','600')
label(35.5,45.5,'57.5 × 10.5 mm · below caps',16,'#406d31')
rect(P['power']['courtyard_bounds'],'none','#b28a57',r=1,dash='4 3')
rect(P['power']['body_bounds'],'#efcf9c','#ac7c40',r=2)
rect([0,46.5,1.5,49.5],'#bd8b4c','#9b703d',r=1)
rect(P['connector']['assembly_allowance_bounds'],'#dce9d5','#739b62',r=2,dash='5 3',opacity=0.6,width=1.8)
rect(P['connector']['header_body_bounds'],'#dce9d5','#739b62',r=2,width=1.8)
label(69.55,47.4,'JST-SH',13,'#4e773d','600')
rect(controller,'#8dc9d6','#2d7d94',r=4,opacity=0.3,width=2.6)
label(87.5,49.7,'Seeed XIAO Plus',17,'#256d84','600')
label(87.5,47.1,'21 × 17.8 mm',16,'#256d84')
label(87.5,44.7,'integrated antenna',12,'#4f7888')
rect([98,43.5,99.5,52.5],'#9eabb6','#657586',r=1)
reset=P['controller']['onboard_reset_center'];circle(*reset,0.45,'#ffffff','#455f71',width=1.7)
for x,y in P['mounts']['centers']:
    circle(x,y,P['mounts']['screw_keepout_diameter']/2,'#ffffff','#5d6f84',width=1.3,dash='4 3')
    circle(x,y,P['mounts']['hole_diameter']/2,'#ffffff','#455c75',width=1.5)
line(OX,146,OX+(X1-X0)*S,146,arrows=True)
text(OX+(X1-X0)*S/2,135,'97.5 mm PCB',24,weight='600',anchor='middle')
line(71,OY,71,OY+(Y1-Y0)*S,arrows=True)
text(55,OY+(Y1-Y0)*S/2,'57 mm PCB',22,weight='600',anchor='middle',rotate=-90)
a,b=point(10.9,75)[0],point(29.95,75)[0]
line(a,189,b,189,arrows=True)
text((a+b)/2,178,'19.05 mm pitch',18,anchor='middle')
a,b=point(2.65,75)[0],point(19.15,75)[0]
line(a,225,b,225,arrows=True)
text((a+b)/2,216,'16.5 mm cap',18,anchor='middle')
y0,y1=point(10.9,75)[1],point(10.9,48.5)[1]
line(114,y0,114,y1,arrows=True)
text(101,(y0+y1)/2,'26.5 mm cap',18,anchor='middle',rotate=-90)
y0,y1=point(10.9,61.75)[1],point(10.9,34.25)[1]
line(151,y0,151,y1,arrows=True)
text(138,(y0+y1)/2,'27.5 mm row pitch',18,anchor='middle',rotate=-90)
for upper,lower in [(57.9,56.9),(39.1,38.1)]:
    x=1193;y0=point(0,upper)[1];y1=point(0,lower)[1]
    line(x,y0,x,y1,'#2d7d94',arrows=True)
    line(point(98,upper)[0],y0,x-4,y0,'#2d7d94','3 3')
    line(point(98,lower)[0],y1,x-4,y1,'#2d7d94','3 3')
    text(x+15,(y0+y1)/2+6,'1.0 mm',18,'#2d7d94','600')
ux,uy=point(99.5,48)
line(ux+3,uy,ux+34,uy,'#657586')
text(ux+41,uy+6,'USB-C',17,'#657586')
text(ux+41,uy+27,'~1 mm past PCB',14,'#657586')
rx,ry=point(*reset)
line(rx+5,ry+3,1210,ry+4,'#455f71')
text(1223,ry+10,'onboard reset',17,'#455f71')
text(1350,230,'LAYOUT DIMENSIONS',22,weight='600')
for y,first,second in [(273,'Main caps','16.5 × 26.5 mm'),(336,'Fifth caps','17.5 × 16.5 mm'),(399,'Choc shoulders','15 × 15 mm nominal'),(462,'Fifth center separation','36.3 mm'),(525,'Battery well','58.1 × 11.1 mm'),(588,'JST-SH allowance','8 × 6 mm incl. plug space'),(651,'Six M2 mounts','Ø2.2 holes · Ø4.6 keepouts')]:
    text(1350,y,first,18,color='#61758a')
    text(1350,y+26,second,22,weight='600')
text(1350,700,'Column four to XIAO: 0.7 mm',18,color='#256d84')
text(1350,733,'POWER SWITCH',20,color='#986c35',weight='600')
text(1350,762,'C&K PCM12 · 6.7 × 2.6 × 1.4 mm',19)
text(1350,791,'Left-facing actuator · 1.5 mm stroke',19)
text(1350,820,'1.5 mm projection from switch body',19)
text(1350,849,'1.0 mm past provisional PCB edge',19)
text(180,885,'PCB trimmed from the previous 98 × 96 mm outline; 1.5 mm top/bottom cap border reserved for a future case.',20,color='#576d82')
text(180,921,'Left power sits beneath column one’s outer cap edge. Battery shifted 3.5 mm right to clear its pads and courtyard.',20,color='#576d82')
text(180,957,'Green connector envelope is an allowance, not verified mated geometry. Battery-wire routing and RF keepout are deferred.',20,color='#576d82')
text(180,993,'Mounts propose low heads above the PCB and nuts below; fastener, PCB-cutout and case-support geometry remain unresolved.',20,color='#576d82')
text(180,1044,'PROVISIONAL SKETCH ONLY · Nominal envelope checks passed · No production PCB, routing, firmware or case changes',20,color='#6b7784')
svg='<svg xmlns="http://www.w3.org/2000/svg" width="1900" height="1100" viewBox="0 0 1900 1100"><defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="3.5" refY="3.5" orient="auto-start-reverse"><path d="M7 3.5 L0 0 L0 7 Z" fill="#75879b"/></marker></defs><rect width="1900" height="1100" fill="#f6f8fa"/>'+''.join(E)+'</svg>'
(ROOT/'no-display-compact-layout.svg').write_text(svg+'\n')
