from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / 'placements.json').read_text())
SCALE = 5.5
ELEMENTS = []


def text(x, y, label, size=18, color='#243445', anchor='start', weight='400'):
    ELEMENTS.append(f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{label}</text>')


def line(x1, y1, x2, y2, color='#68798a', dash='', arrows=False):
    extra = 'marker-start="url(#arrow)" marker-end="url(#arrow)"' if arrows else ''
    ELEMENTS.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.4" stroke-dasharray="{dash}" {extra}/>')


def panel(name, origin, title, subtitle):
    data = DATA[name]
    w, h = data['board_mm']
    ox, oy = origin
    def rect(x, y, width, height, fill, stroke, radius=4, dash=''):
        ELEMENTS.append(f'<rect x="{ox+x*SCALE}" y="{oy+(h-y-height)*SCALE}" width="{width*SCALE}" height="{height*SCALE}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="1.6" stroke-dasharray="{dash}"/>')
    def label(x, y, caption, size=15, color='#243445', weight='400'):
        text(ox+x*SCALE, oy+(h-y)*SCALE, caption, size, color, 'middle', weight)
    text(ox, 61, title, 25, weight='600')
    text(ox, 89, subtitle, 16, '#526375')
    rect(0, 0, w, h, '#ffffff', '#7e91a4', 9)
    rect(0, 0, 80, 80, 'none', '#b55056', 0, '8 6')
    rect(2, h-19.4, 39.1, 18.3, '#dcebf2', '#7195ab')
    label(21.55,h-8.4,'nice!view',17,weight='600')
    label(21.55,h-13.4,'nice!nano below',13)
    rect(47, h-19, 6, 6, '#fdebd4', '#bc915f', 3)
    label(57,h-16.8,'reset',12)
    rect(45.7, h-7.15, 8.6, 4.3, '#fdebd4', '#bc915f', 3)
    label(59,h-5.8,'power',12)
    rect(4, 3.5, 32, 13, '#e2efdf', '#7fa477')
    label(20,10.3,'301230 battery',14,weight='600')
    label(20,6.3,'110 mAh',12)
    rect(37.75, 7.05, 13.6, 5.9, '#e2efdf', '#7fa477', 2)
    label(44.55,9.3,'JST-PH',11)
    for switch in data['switches']:
        cw,ch=switch['cap'];x,y=switch['x'],switch['y']
        fill='#e7eaf3' if switch['label'].endswith('5') else '#e8eef9'
        rect(x-cw/2,y-ch/2,cw,ch,fill,'#6983ac',5)
        label(x,y-1.1,switch['label'],18,weight='600')
    line(ox,119,ox+w*SCALE,119,arrows=True)
    line(ox,125,ox,137)
    line(ox+w*SCALE,125,ox+w*SCALE,137)
    text(ox+w*SCALE/2,112,'98 mm',17,anchor='middle',weight='600')
    dx=ox-21
    line(dx,oy,dx,oy+h*SCALE,arrows=True)
    text(dx-9,oy+h*SCALE/2,f'{h} mm',17,anchor='end',weight='600')
    a=next(s for s in data['switches'] if s['label']=='b1')
    b=next(s for s in data['switches'] if s['label']=='t1')
    pitch=b['y']-a['y']
    dx=ox+w*SCALE+14
    y1=oy+(h-b['y'])*SCALE;y2=oy+(h-a['y'])*SCALE
    line(dx,y1,dx,y2,arrows=True)
    text(dx+7,(y1+y2)/2-5,f'{pitch:g}',14,weight='600')
    text(dx+7,(y1+y2)/2+13,'mm',12)
    base=oy+h*SCALE+27
    text(ox,base,'19.05 mm column pitch',17,weight='600')
    text(ox,base+24,f'{pitch:g} mm row pitch',17)
    text(ox,base+48,'2.55 mm vertical cap gap' if name.endswith('1u') else '1.00 mm gap between the large caps',15,'#526375')


panel('five-column-1u',(92,155),'A  ·  Ten 1U keys','17.5 × 16.5 mm caps · Sofle pitch in both directions')
panel('five-column-15u',(820,155),'B  ·  Eight 1.5U + two 1U keys','Portrait 16.5 × 26.5 mm caps · 1U fifth column')
line(92,826,135,826,'#b55056','8 6')
text(146,832,'Original 80 × 80 mm target',17,'#a44850')
text(92,875,'1.5U caps overlap by 7.45 mm at 19.05 mm row pitch; version B needs 27.5 mm row pitch.',18,weight='600')
text(92,910,'PROVISIONAL · Placement comparison only · No routing, fabrication, fastener or assembly validation',16,'#6b7380')
svg='<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="950" viewBox="0 0 1500 950"><defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="3.5" refY="3.5" orient="auto-start-reverse"><path d="M7 3.5 L0 0 L0 7 Z" fill="#68798a"/></marker></defs><rect width="1500" height="950" fill="#f6f8fa"/>'+''.join(ELEMENTS)+'</svg>'
(ROOT/'comparison.svg').write_text(svg+'\n')
