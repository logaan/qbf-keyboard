from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent
SCALE=16
CX,CY=640,572
OUT=[]


def point(x,y):
    return CX+(x-68.05)*SCALE,CY+(48-y)*SCALE


def text(x,y,label,size=21,color='#25374b',weight='400',anchor='start',rotate=None):
    transform='' if rotate is None else f'transform="rotate({rotate} {x} {y})"'
    OUT.append(f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}" {transform}>{label}</text>')


def line(x1,y1,x2,y2,color='#7a8a9b',width=1.5,dash='',arrows=False):
    markers='marker-start="url(#arrow)" marker-end="url(#arrow)"' if arrows else ''
    OUT.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" stroke-dasharray="{dash}" {markers}/>')


def rect(bounds,fill,stroke,opacity=1,width=2,dash='',rx=4):
    x0,y0,x1,y1=bounds
    x,y=point(x0,y1)
    OUT.append(f'<rect x="{x}" y="{y}" width="{(x1-x0)*SCALE}" height="{(y1-y0)*SCALE}" rx="{rx}" fill="{fill}" fill-opacity="{opacity}" stroke="{stroke}" stroke-width="{width}" stroke-dasharray="{dash}"/>')


def bounds(x,y,w,h):
    return [x-w/2,y-h/2,x+w/2,y+h/2]


def horizontal_dimension(x0,x1,y,label,label_y,color='#566b82'):
    line(x0,y,x1,y,color,arrows=True)
    text((x0+x1)/2,label_y,label,20,color,'600','middle')


def vertical_dimension(x,y0,y1,label,color='#566b82',rotate=False):
    line(x,y0,x,y1,color,arrows=True)
    if rotate:
        text(x-12,(y0+y1)/2,label,20,color,'600','middle',-90)
    else:
        text(x+13,(y0+y1)/2+6,label,19,color,'600')


def inset():
    ox,oy,s=1190,190,2.4
    text(ox,150,'Layout context',21,weight='600')
    text(ox,174,'98 × 96 mm',18,color='#627589')
    OUT.append(f'<rect x="{ox}" y="{oy}" width="{98*s}" height="{96*s}" rx="5" fill="#fff" stroke="#91a0b0" stroke-width="1.5"/>')
    keys=[]
    for i,x in enumerate([10.9,29.95,49,68.05],1):
        for row,y in [('b',34.25),('t',61.75)]:
            keys.append({'label':row+str(i),'center':[x,y],'cap_mm':[16.5,26.5]})
    keys += [{'label':'b5','center':[87.1,29.25],'cap_mm':[17.5,16.5]},{'label':'t5','center':[87.1,66.75],'cap_mm':[17.5,16.5]}]
    for key in keys:
        x,y=key['center'];w,h=key['cap_mm']
        OUT.append(f'<rect x="{ox+(x-w/2)*s}" y="{oy+(96-y-h/2)*s}" width="{w*s}" height="{h*s}" rx="2" fill="#edf1f7" stroke="#91a2b8" stroke-width="1"/>')
    OUT.append(f'<rect x="{ox+57.55*s}" y="{oy+(96-56.9)*s}" width="{21*s}" height="{17.8*s}" fill="#6bb7c9" fill-opacity="0.4" stroke="#318296" stroke-width="2"/>')
    OUT.append(f'<rect x="{ox+56.5*s}" y="{oy+(96-76)*s}" width="{24*s}" height="{56*s}" fill="none" stroke="#b5535c" stroke-width="1.5" stroke-dasharray="5 3"/>')
    text(ox,457,'Main eight switches unchanged',16,color='#627589')
    text(ox,482,'Blue: proposed controller',16,color='#318296')
    return keys


text(100,48,'Can the Seeed XIAO fit between t4 and b4?',31,weight='600')
text(100,78,'Dimensioned top view · Proposed test position only · No display',21,color='#607287')
for name,y in [('t4',61.75),('b4',34.25)]:
    rect(bounds(68.05,y,16.5,26.5),'#ecf1f8','#9caec5',opacity=0.55,width=1.8,rx=8)
    rect(bounds(68.05,y,15,15),'#dae2eb','#5e7188',opacity=0.7,width=2.5,rx=4)
    px,py=point(68.05,y)
    text(px,py-12,name+' switch',24,weight='600',anchor='middle')
    text(px,py+20,'15 × 15 mm shoulder',18,color='#566b82',anchor='middle')
    line(px-23,py,px+23,py,'#8a9aad',dash='3 4')
    line(px,py-23,px,py+23,'#8a9aad',dash='3 4')
rect(bounds(68.05,48,21,17.8),'#65b6cc','#287c93',opacity=0.25,width=3,rx=5)
for overlap in [[60.55,54.25,75.55,56.9],[60.55,39.1,75.55,41.75]]:
    rect(overlap,'url(#hatch)','#b85460',width=2,rx=0)
rect([78.55,44.2,79.55,51.8],'#a4afb9','#637384',opacity=0.8,width=1.5,rx=1)
text(CX,CY-11,'Seeed XIAO nRF52840 Plus',21,'#226c82','600','middle')
text(CX,CY+20,'21 × 17.8 mm body',20,'#226c82','400','middle')
text(CX+110,CY+48,'USB →',16,'#526b7e','400','middle')
cap_left,cap_top=point(59.8,75)
cap_right,cap_bottom=point(76.3,48.5)
line(cap_left,cap_top,cap_left,113)
line(cap_right,cap_top,cap_right,113)
horizontal_dimension(cap_left,cap_right,111,'16.5 mm keycap',102)
vertical_dimension(275,cap_top,cap_bottom,'26.5 mm keycap',rotate=True)
line(282,cap_top,cap_left-8,cap_top)
line(282,cap_bottom,cap_left-8,cap_bottom)
switch_left,switch_top=point(60.55,69.25)
switch_right,switch_bottom=point(75.55,54.25)
horizontal_dimension(switch_left,switch_right,211,'15 mm switch',201)
line(switch_left,217,switch_left,switch_top)
line(switch_right,217,switch_right,switch_top)
vertical_dimension(439,switch_top,switch_bottom,'15 mm switch',rotate=True)
line(446,switch_top,switch_left-6,switch_top)
line(446,switch_bottom,switch_left-6,switch_bottom)
y_top=point(68.05,61.75)[1];y_bottom=point(68.05,34.25)[1]
vertical_dimension(355,y_top,y_bottom,'27.5 mm switch-center pitch',rotate=True)
line(362,y_top,switch_left-6,y_top,dash='4 5')
line(362,y_bottom,switch_left-6,y_bottom,dash='4 5')
gap_top=point(68.05,54.25)[1];gap_bottom=point(68.05,41.75)[1]
vertical_dimension(890,gap_top,gap_bottom,'12.5 mm',color='#697c90')
text(903,(gap_top+gap_bottom)/2+33,'shoulder gap',17,'#697c90')
for upper,lower in [(56.9,54.25),(41.75,39.1)]:
    y0=point(68.05,upper)[1];y1=point(68.05,lower)[1]
    vertical_dimension(843,y0,y1,'2.65 mm overlap',color='#b04b58')
    line(switch_right+5,y0,837,y0,'#b04b58')
    line(switch_right+5,y1,837,y1,'#b04b58')
xiao_left,xiao_top=point(57.55,56.9)
xiao_right,xiao_bottom=point(78.55,39.1)
vertical_dimension(1055,xiao_top,xiao_bottom,'',color='#287c93')
text(1070,CY-4,'17.8 mm',19,'#287c93','600')
text(1070,CY+21,'XIAO body',17,'#287c93')
line(xiao_right+7,xiao_top,1049,xiao_top,'#287c93',dash='4 4')
line(xiao_right+7,xiao_bottom,1049,xiao_bottom,'#287c93',dash='4 4')
horizontal_dimension(xiao_left,xiao_right,1043,'21 mm XIAO body',1070,'#287c93')
line(xiao_left,xiao_bottom+6,xiao_left,1037,'#287c93',dash='4 4')
line(xiao_right,xiao_bottom+6,xiao_right,1037,'#287c93',dash='4 4')
keys=inset()
text(1190,575,'FIT RESULT',19,'#a94e59','600')
text(1190,609,'17.8 mm controller',19)
text(1190,638,'in a 12.5 mm gap:',19)
text(1190,676,'2.65 mm overlap',21,'#a94e59','600')
text(1190,705,'into each switch',21,'#a94e59','600')
text(1190,734,'shoulder footprint.',21,'#a94e59','600')
text(100,1126,'Light outline: 16.5 × 26.5 mm keycap. Dark square: nominal 15 × 15 mm Choc switch shoulder. Red hatch: footprint overlap.',20,color='#586c80')
text(100,1164,'Illustration only. Dimensions test plan-view fit; recess depth, module height and assembled operating clearances remain unvalidated.',19,color='#6a7786')
svg='<svg xmlns="http://www.w3.org/2000/svg" width="1510" height="1210" viewBox="0 0 1510 1210"><defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="3.5" refY="3.5" orient="auto-start-reverse"><path d="M7 3.5 L0 0 L0 7 Z" fill="#6f8297"/></marker><pattern id="hatch" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M-2 2 L2 -2 M0 10 L10 0 M8 12 L12 8" stroke="#bc606c" stroke-width="2"/></pattern></defs><rect width="1510" height="1210" fill="#f7f9fb"/>'+''.join(OUT)+'</svg>'
(ROOT/'xiao-between-switches.svg').write_text(svg+'\n')
data={'status':'Illustration only; proposed test position, no design changes.','board_context_mm':[98,96],'all_key_context':keys,'column_four':{'top_switch_center':[68.05,61.75],'bottom_switch_center':[68.05,34.25],'keycap_mm':[16.5,26.5],'switch_shoulder_mm':[15,15],'switch_center_pitch_mm':27.5,'shoulder_gap_mm':12.5},'controller':{'module':'Seeed XIAO nRF52840 Plus','center':[68.05,48],'body_mm':[21,17.8],'bounds':[57.55,39.1,78.55,56.9],'usb_orientation':'right','usb_outline':'Schematic projection; excluded from 21 mm body dimension.'},'overlap_rectangles':[[60.55,54.25,75.55,56.9],[60.55,39.1,75.55,41.75]],'overlap_into_each_shoulder_mm':2.65,'dimensions_scope':'Nominal plan-view envelopes. Does not validate actual body geometry, cutout recess, vertical stack or operating clearance.'}
assert abs((17.8-12.5)/2-2.65)<0.000001
assert abs(61.75-34.25-27.5)<0.000001
assert abs((61.75-7.5)-(34.25+7.5)-12.5)<0.000001
(ROOT/'xiao-between-switches-placements.json').write_text(json.dumps(data,indent=2)+'\n')
