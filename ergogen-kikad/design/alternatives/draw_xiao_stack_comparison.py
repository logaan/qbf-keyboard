from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent
DATA=json.loads((ROOT/'xiao-stack-comparison-placements.json').read_text())
SCALE=7
ELEMENTS=[]


def text(x,y,label,size=20,color='#26364a',weight='400',anchor='start'):
    ELEMENTS.append(f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}">{label}</text>')


def line(x1,y1,x2,y2,color='#74869a',dash='',width=1.8,arrows=False):
    marker='marker-start="url(#arrow)" marker-end="url(#arrow)"' if arrows else ''
    ELEMENTS.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" stroke-dasharray="{dash}" {marker}/>')


def panel(kind,ox):
    oy=190
    variant=DATA['variants'][kind]
    def rect(bounds,fill,stroke,rx=4,dash='',opacity=1,width=1.8):
        x0,y0,x1,y1=bounds
        ELEMENTS.append(f'<rect x="{ox+x0*SCALE}" y="{oy+(96-y1)*SCALE}" width="{(x1-x0)*SCALE}" height="{(y1-y0)*SCALE}" rx="{rx}" fill="{fill}" fill-opacity="{opacity}" stroke="{stroke}" stroke-width="{width}" stroke-dasharray="{dash}"/>')
    def label(x,y,caption,size=18,color='#26364a',weight='400'):
        text(ox+x*SCALE,oy+(96-y)*SCALE,caption,size,color,weight,'middle')
    def point(x,y):
        return ox+x*SCALE,oy+(96-y)*SCALE
    rect([0,0,98,96],'#ffffff','#7e91a4',10)
    rect(DATA['common']['provisional_relocation']['jst_body_bounds'],'#e1ecdc','#7fa477',2)
    rect(DATA['common']['provisional_relocation']['jst_mating_plug_bounds'],'#eef3e9','#7fa477',2)
    label(16,84.3,'JST-PH',13)
    rect([45.7,82.85,54.3,87.15],'#f6e7d2','#b48b59',3)
    label(50,80,'power',14)
    label(33,92,'Provisional connector / power locations',14,'#627184')
    for key in DATA['common']['main_keys']+DATA['common']['fifth_keys']:
        x,y=key['center'];w,h=key['cap_mm']
        rect([x-w/2,y-h/2,x+w/2,y+h/2],'#e7edf7','#768eb2',5)
        label(x,y-1,key['label'],21,weight='600')
    rect([3.25,42.75,60.75,53.25],'none','#638e54',3,'8 5',width=2)
    label(31.5,47,'301055 below caps',16,'#4b753d','600')
    rect(DATA['common']['controller']['plan_bounds'],'#edf0f2','#6f7881',3,'6 4',opacity=0.35,width=2)
    rect(variant['display_body_bounds'],'#7cc7d2','#2d7c8e',3,opacity=0.23,width=2.8)
    if kind=='horizontal':
        for overlap in variant['fourth_column_cap_overlap_rectangles']:
            rect(overlap,'url(#hatch)','#b84e54',0,opacity=1,width=2)
    rect(variant['native_socket_bounds'],'#e9c490','#a47d48',1,width=1.8)
    rect([98,43.5,99.5,52.5],'#9aa5af','#596775',1,width=1.5)
    px,py=point(99.5,48)
    line(px+3,py,px+33,py,'#596775')
    text(px+39,py+6,'USB-C',17,'#596775')
    rx,ry=point(*DATA['common']['controller']['onboard_reset_center'])
    ELEMENTS.append(f'<circle cx="{rx}" cy="{ry}" r="4.3" fill="#f8f8f4" stroke="{"#9e4b52" if kind=="horizontal" else "#4b6958"}" stroke-width="2"/>')
    line(rx+4,ry-2,ox+98*SCALE+23,ry-28,'#9e4b52' if kind=='horizontal' else '#4b6958')
    text(ox+98*SCALE+29,ry-28,'reset',16,'#9e4b52' if kind=='horizontal' else '#4b6958')
    text(ox+98*SCALE+29,ry-8,'covered' if kind=='horizontal' else 'exposed',14,'#9e4b52' if kind=='horizontal' else '#4b6958')
    if kind=='portrait':
        label(87.5,59,'nice!view',15,'#226c7d','600')
        label(87.5,56,'portrait',14,'#226c7d')
    else:
        label(84,49,'nice!view',17,'#226c7d','600')
        label(84,45.5,'horizontal',14,'#226c7d')
    line(ox,169,ox+98*SCALE,169,arrows=True)
    text(ox+49*SCALE,159,'98 mm',18,weight='600',anchor='middle')
    line(ox-24,oy,ox-24,oy+96*SCALE,arrows=True)
    text(ox-33,oy+48*SCALE+6,'96 mm',18,weight='600',anchor='end')
    x1,y1=point(97,39.1)
    line(x1,y1,ox+98*SCALE+23,y1+30,'#707b87','4 4')
    text(ox+98*SCALE+29,y1+34,'XIAO',16,'#5e6976')
    text(ox+98*SCALE+29,y1+54,'below',15,'#5e6976')
    base=899
    if kind=='portrait':
        text(ox,base,'PORTRAIT · Plan-view candidate',25,'#236c74','600')
        text(ox,base+34,'1 mm to each fifth-column cap; 4.2 mm to column four.',20)
        text(ox,base+65,'Native five-pin socket clears the recessed XIAO body.',20)
        text(ox,base+96,'Reset center exposed; operating clearance needs checking.',19,'#5d6d7f')
    else:
        text(ox,base,'HORIZONTAL · Overlaps column four',25,'#a2434d','600')
        text(ox,base+34,'Hatched overlap with column four is 14.3 mm wide.',20)
        text(ox,base+65,'Above the caps, it obstructs the paired-key press area.',19)
        text(ox,base+96,'Low mounting conflicts with key travel; reset access is unresolved.',19,'#a2434d')


text(105,55,'Two nice!view / recessed-XIAO concepts',34,weight='600')
text(105,92,'Same scale · Same 98 × 96 mm outline · Same main eight keys · Fifth keys moved outward 8.5 mm in both',22,'#556779')
panel('portrait',105)
panel('horizontal',1095)
text(105,1062,'Dashed gray: recessed XIAO below the display. Amber: native nice!view socket on the main PCB. Green dashed: battery below caps.',20,'#556779')
text(105,1100,'DIAGRAM ONLY · Recess depth, vertical stack, reset access and solder mounting are unvalidated. Electrical and battery-lead routing deferred.',20,'#6a7582')
svg='<svg xmlns="http://www.w3.org/2000/svg" width="2100" height="1150" viewBox="0 0 2100 1150"><defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="3.5" refY="3.5" orient="auto-start-reverse"><path d="M7 3.5 L0 0 L0 7 Z" fill="#74869a"/></marker><pattern id="hatch" width="9" height="9" patternUnits="userSpaceOnUse"><path d="M-2 2 L2 -2 M0 9 L9 0 M7 11 L11 7" stroke="#c36c72" stroke-width="2"/></pattern></defs><rect width="2100" height="1150" fill="#f6f8fa"/>'+''.join(ELEMENTS)+'</svg>'
(ROOT/'xiao-stack-comparison.svg').write_text(svg+'\n')
