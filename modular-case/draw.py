from pathlib import Path
import json
from html import escape
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'modular-case/generated'
C=json.loads((ROOT/'ergogen-kikad/generated/assembly-contract.json').read_text())
V=json.loads((OUT/'validation.json').read_text())
s=['<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1100" viewBox="0 0 1800 1100"><rect width="1800" height="1100" fill="#f5f7f8"/><style>text{font-family:Arial,sans-serif;fill:#22323b} .dim{stroke:#516974;stroke-width:1.5;fill:none} .small{font-size:21px} .label{font-size:25px}</style>']


def text(x,y,value,size=25,color='#22323b',anchor='start'):
    s.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}">{escape(value)}</text>')


def rect(x,y,w,h,fill,stroke='none',radius=0):
    s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')


def line(x1,y1,x2,y2,color='#516974'):
    s.append(f'<path d="M {x1},{y1} L {x2},{y2}" stroke="{color}" stroke-width="1.5" fill="none"/>')


def dim(x1,y1,x2,y2,label,vertical=False):
    line(x1,y1,x2,y2)
    if vertical:
        for y in (y1,y2):line(x1-7,y,x1+7,y)
        text(x1+15,(y1+y2)/2,label,21)
    else:
        for x in (x1,x2):line(x,y1-7,x,y1+7)
        text((x1+x2)/2,y1-12,label,21,anchor='middle')


def xy(x,y):
    return 120+(x-.4)*7,190+(77.25-y)*7


def plan(bounds,fill,stroke='none',r=0):
    x,y=xy(bounds[0],bounds[3])
    rect(x,y,(bounds[2]-bounds[0])*7,(bounds[3]-bounds[1])*7,fill,stroke,r*7)

text(90,75,'QBF  /  MODULAR CASE',40)
text(90,112,'Dimensioned nominal geometry • millimetres • two identical halves, second rotated 180°',22)
plan(C['pcb_bounds'],'#b7d5d7','#20515b',1.5)
plan([2.4,20.75,96.1,75.25],'#edf1ed')
plan([6.45,42.45,64.55,53.55],'#70a6ae','#20515b')
for k in C['keys']:
    cx,cy=k['center'];w,h=k['cap_mm']
    plan([cx-w/2,cy-h/2,cx+w/2,cy+h/2],'#ffffff','#637780',1)
    x,y=xy(cx,cy)
    text(x,y+8,k['name'],23,anchor='middle')
plan([77,38.6,98,56.4],'#b4c49f','#50705b')
plan([92.13872,43.0064,99.48872,52.0064],'#b6bdc3','#65717a')
x,y=xy(85,47.5)
text(x,y+7,'XIAO',18,anchor='middle')
for m in C['mounts']:
    x,y=xy(m['x'],m['y'])
    s.append(f'<circle cx="{x}" cy="{y}" r="7.7" fill="white" stroke="#20515b" stroke-width="2"/>')
plan([.62,44.15,5.62,51.85],'#b8bec5','#65717a')
x,y=xy(.62,48)
line(x-55,y,x-5,y)
text(x-62,y+7,'Power',20,anchor='end')
dim(120,163,803.9,163,'97.7 PCB / tray / rim')
dim(843,190,843,599.5,'58.5',True)
text(120,638,'Joined width: 97.7 + 10 + 97.7 = 205.4',21)
text(975,195,'Key and wall clearances',30)
for i,t in enumerate(['Main caps: 16.5 × 26.5 (portrait 1.5U)','Column 5: 17.5 × 16.5 (1U)','PCB beyond cap edges: 2.25','Perimeter wall: 2.0 • cap gap: 0.25','Four M2 mounts • battery roof clearance: 0.30','Controller: 21 × 17.8 • USB faces inward']):
    text(975,242+i*39,t,22)
text(975,525,'Transport envelope, each half',30)
text(975,570,'100.9 × 63.3 × 21.2',34)
text(975,607,'Includes the cover finger tabs and tray feet.',21)
text(90,715,'SIDE VIEW  /  HEIGHT ENVELOPES',28)
x0=115;scale=11;z=lambda v:990-(v+7.8)*scale
rect(x0,z(-3.2),680,3.2*scale,'#225665')
rect(x0+50,z(-6.4),65,1.4*scale,'#225665')
rect(x0+565,z(-6.4),65,1.4*scale,'#225665')
rect(x0,z(0),680,3.2*scale,'#8b9a7e')
rect(x0,z(3.6),22,3.6*scale,'#478e9a')
rect(x0+658,z(3.6),22,3.6*scale,'#478e9a')
rect(x0+65,z(10.969114),550,3.969114*scale,'white','#637780',6)
rect(x0+65,z(7),550,3*scale,'#d9e1e3')
rect(x0-15,z(13.4),710,1.2*scale,'#db7830')
rect(x0-15,z(12.2),14,8.6*scale,'#db7830')
rect(x0+681,z(12.2),14,8.6*scale,'#db7830')
dim(850,z(13.4),850,z(-7.8),'21.2',True)
line(600,z(12.2),650,740)
text(665,741,'1.23 cap-to-roof gap',21)
text(975,730,'Tool-free everyday use',30)
for i,t in enumerate(['Join: insert four bridge heads, then slide 6.5 mm.','Split: press both underside tabs, slide back, lift off.','Cover: press down until the front/back clips catch.','Uncover: pull both cover tabs outward and lift.','Each half can be used and covered on its own.','Separate halves for straight USB cable access.']):
    text(975,775+i*39,t,21)
text(90,1060,'CAD fit is verified; print fit, clip fatigue, luggage loads and the recessed controller assembly need physical testing.',21)
s.append('</svg>')
(OUT/'dimensions.svg').write_text('\n'.join(s)+'\n')

font_path='/System/Library/Fonts/Supplemental/Arial.ttf'
font=lambda n:ImageFont.truetype(font_path,n)
canvas=Image.new('RGB',(1600,1400),'#f5f7f8')
d=ImageDraw.Draw(canvas)
d.text((60,35),'QBF — join, split, protect',fill='#18303a',font=font(44))
d.text((60,94),'Two independent halves • removable bridge • individual snap-on covers',fill='#4b636c',font=font(24))
for name,bounds,size,pos in [('joined',(340,270,1640,850),(1480,660),(60,150)),('assembled',(250,100,1750,980),(720,422),(60,895)),('solo_closed',(250,100,1750,980),(720,422),(820,895))]:
    im=Image.open(OUT/(name+'.png')).crop(bounds).resize(size,Image.Resampling.LANCZOS)
    canvas.paste(im,pos)
d.text((60,825),'Joined flat · 205.4 mm across the trays',fill='#18303a',font=font(27))
d.text((60,1335),'Solo or split use',fill='#18303a',font=font(27))
d.text((820,1335),'Protected · 100.9 × 63.3 × 21.2 mm',fill='#18303a',font=font(27))
canvas.save(OUT/'overview.png')
print('Created dimension drawing and native-render overview')
