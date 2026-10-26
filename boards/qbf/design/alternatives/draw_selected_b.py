from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent
DATA=json.loads((ROOT/'placements.json').read_text())['five-column-15u']
S=7
OX,OY=100,135
E=[]


def text(x,y,label,size=18,color='#26364a',weight='400',anchor='start'):
    E.append(f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}">{label}</text>')


def rect(x,y,w,h,fill,stroke,r=4,dash=''):
    E.append(f'<rect x="{OX+x*S}" y="{OY+(96-y-h)*S}" width="{w*S}" height="{h*S}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="1.8" stroke-dasharray="{dash}"/>')


def label(x,y,caption,size=17,color='#26364a',weight='400'):
    text(OX+x*S,OY+(96-y)*S,caption,size,color,weight,'middle')


def line(x1,y1,x2,y2,color='#7c8b9c',dash='',arrows=False):
    marker='marker-start="url(#arrow)" marker-end="url(#arrow)"' if arrows else ''
    E.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.7" stroke-dasharray="{dash}" {marker}/>')


text(100,55,'Selected B · Revised component layout',29,weight='600')
text(100,87,'Eight portrait 1.5U keys + two 1U keys · Main eight switches stay in place',19,color='#56677a')
rect(0,0,98,96,'#ffffff','#8597a9',10)
for x,y,w,h,title in [(2,76.6,36,18.3,'nice!nano'),(42,78.75,36,14,'nice!view')]:
    rect(x,y,w,h,'#dcebf2','#7195ab')
    label(x+w/2,y+h/2-1,title,19,weight='600')
rect(42.03,79.4,2.54,12.7,'#bdd3df','#7195ab',1)
label(20,79.8,'USB faces left',12)
for key in DATA['switches']:
    w,h=key['cap'];x,y=key['x'],key['y']
    rect(x-w/2,y-h/2,w,h,'#e7eaf3' if key['label'].endswith('5') else '#e8eef9','#6983ac',5)
    label(x,y-1,key['label'],20,weight='600')
rect(78.5,50,6,6,'#fdebd4','#bd9059',3)
rect(87.2,50.85,8.6,4.3,'#fdebd4','#bd9059',3)
label(81.5,51.9,'R',16,weight='600')
label(91.5,51.9,'P',16,weight='600')
rect(77.25,40.05,13.6,5.9,'#e3eedf','#7ea076',2)
label(84.05,42.15,'JST-PH',12)
rect(3.25,42.75,57.5,10.5,'none','#487d3e',3,'7 5')
rect(2.95,42.45,58.1,11.1,'none','#649455',3,'2 5')
label(31.5,47.1,'301055 · below cap overhang',15,'#386431','600')
points=[(60.75,48),(74.8,48),(77.25,43)]
poly=' '.join(f'{OX+x*S},{OY+(96-y)*S}' for x,y in points)
E.append(f'<polyline points="{poly}" fill="none" stroke="#b16b38" stroke-width="3" stroke-linejoin="round"/>')
line(OX,115,OX+98*S,115,arrows=True)
text(OX+49*S,107,'98 mm',18,weight='600',anchor='middle')
line(76,OY,76,OY+96*S,arrows=True)
text(61,OY+48*S+6,'96 mm',18,weight='600',anchor='end')
for y in [75,21]:
    sy=OY+(96-y)*S
    line(OX-8,sy,OX+98*S+9,sy,'#7388a6','4 5')
text(842,283,'Top cap edges align',18,weight='600')
text(842,309,'y = 75 mm',17,color='#56677a')
text(842,657,'Bottom cap edges align',18,weight='600')
text(842,683,'y = 21 mm',17,color='#56677a')
text(842,384,'Reset left · power right',18,weight='600')
text(842,411,'Between t5 and b5',17,color='#56677a')
text(842,445,'Connector clears the caps',18,weight='600')
text(842,472,'Battery wires stay below',17,color='#56677a')
text(842,496,'the cap travel envelope',17,color='#56677a')
text(842,173,'Separate module footprints',18,weight='600')
text(842,201,'4 mm gap between boards',17,color='#56677a')
text(100,848,'19.05 mm column pitch · 27.5 mm main row pitch · 1 mm gap between the large caps',19,weight='600')
text(100,882,'Protected 301055 envelope: 57.5 × 10.5 × 3.5 mm, supported in a main-PCB-only well.',18,color='#47733c')
text(100,911,'The wider 301230 envelope will not fit the 12.5 mm gap between switch shoulders.',17,color='#56677a')
text(100,956,'PROVISIONAL · Layout checks only · Routing, assembled models, case and fabrication validation deferred',16,color='#6a7582')
svg='<svg xmlns="http://www.w3.org/2000/svg" width="1260" height="1000" viewBox="0 0 1260 1000"><defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="3.5" refY="3.5" orient="auto-start-reverse"><path d="M7 3.5 L0 0 L0 7 Z" fill="#7c8b9c"/></marker></defs><rect width="1260" height="1000" fill="#f6f8fa"/>'+''.join(E)+'</svg>'
(ROOT/'selected-B.svg').write_text(svg+'\n')
