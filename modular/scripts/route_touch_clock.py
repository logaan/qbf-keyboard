"""Grid-based two-layer A* router for the remaining module 3 TP_SCL connection.
Run after finish_module_routes.py; requires pcbnew, numpy, Pillow.
Always validate the resulting board with kicad-cli pcb drc.
"""
import pcbnew as p, numpy as np, heapq, math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
board_path=Path(__file__).resolve().parents[1]/'kicad/module3_routed.kicad_pcb'
b=p.LoadBoard(str(board_path))
step=.25; x0=90;y0=62;W=312;H=308
pix=lambda v,o: round((v/1e6-o)/step)
point=lambda v:(pix(v.x,x0),pix(v.y,y0))
net=b.FindNet('TP_SCL');nid=net.GetNetCode()
imgs=[Image.new('L',(W,H)),Image.new('L',(W,H))]
for obj in b.GetTracks():
 if obj.GetNetCode()==nid:continue
 for layer,im in zip((p.F_Cu,p.B_Cu),imgs):
  if not obj.IsOnLayer(layer):continue
  d=ImageDraw.Draw(im);a=point(obj.GetStart());z=point(obj.GetEnd());r=((obj.GetWidth(layer) if isinstance(obj,p.PCB_VIA) else obj.GetWidth())/1e6+.65)/step
  if isinstance(obj,p.PCB_VIA):
   d.ellipse((a[0]-r/2,a[1]-r/2,a[0]+r/2,a[1]+r/2),fill=255)
  else:d.line([a,z],fill=255,width=math.ceil(r),joint='curve')
for f in b.GetFootprints():
 for pad in f.Pads():
  if pad.GetNetCode()==nid:continue
  box=pad.GetBoundingBox(); l=pix(box.GetLeft(),x0)-2; t=pix(box.GetTop(),y0)-2;r=pix(box.GetRight(),x0)+2;bot=pix(box.GetBottom(),y0)+2
  for lay,im in zip((p.F_Cu,p.B_Cu),imgs):
   if pad.IsOnLayer(lay):ImageDraw.Draw(im).rectangle((l,t,r,bot),fill=255)
# avoid through holes, large board edge clearance
blocked=[np.asarray(im).copy()>0 for im in imgs]
viablock=[np.asarray(im.filter(ImageFilter.MaxFilter(5)))>0 for im in imgs]
start=(pix(102857500,x0),pix(96620000,y0),0);end=(pix(129845000,x0),pix(115000000,y0),0)
for layer in range(2):
 for x,y,_ in (start,end):
  blocked[layer][max(0,y-2):y+3,max(0,x-2):x+3]=False
  viablock[layer][max(0,y-2):y+3,max(0,x-2):x+3]=False
print(start,end,flush=True)
# A* with via move only at clearance-safe locations
cost={start:0};prev={};heap=[(0,start)];dirs=[(1,0,1),(0,1,1),(-1,0,1),(0,-1,1),(1,1,1.42),(1,-1,1.42),(-1,1,1.42),(-1,-1,1.42)]
count=0
while heap:
 _,state=heapq.heappop(heap);x,y,layer=state
 if state==end:break
 count+=1
 for dx,dy,dc in dirs+([(0,0,13)] if not viablock[0][y,x] and not viablock[1][y,x] else []):
  xx=x+dx;yy=y+dy;ll=layer if dc!=13 else 1-layer
  if not(6<=xx<W-6 and 6<=yy<H-6) or blocked[ll][yy,xx]:continue
  if dx and dy and (blocked[ll][yy,x] or blocked[ll][y,xx]):continue
  s=(xx,yy,ll);new=cost[state]+dc
  if new>=cost.get(s,float('inf')):continue
  cost[s]=new;prev[s]=state
  h=math.hypot(end[0]-xx,end[1]-yy)+(13 if ll!=0 else 0)
  heapq.heappush(heap,(new+h,s))
else:print('NO ROUTE',count);raise SystemExit
path=[end]
while path[-1]!=start:path.append(prev[path[-1]])
path.reverse();print('FOUND',len(path),'vias',[(x*step+x0,y*step+y0) for i,(x,y,l) in enumerate(path[1:],1) if l!=path[i-1][2]],'expansions',count,flush=True)
# simplify straight runs; create tracks and vias
coords=lambda a:p.VECTOR2I(round((x0+a[0]*step)*1e6),round((y0+a[1]*step)*1e6))
def trace(a,z,l):
 t=p.PCB_TRACK(b);t.SetStart(coords(a));t.SetEnd(coords(z));t.SetWidth(200000);t.SetLayer([p.F_Cu,p.B_Cu][l]);t.SetNet(net);b.Add(t)
def via(a):
 v=p.PCB_VIA(b);v.SetPosition(coords(a));v.SetWidth(600000);v.SetDrill(300000);v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(net);b.Add(v)
way=[path[0]]
for i in range(1,len(path)-1):
 a=path[i-1];c=path[i];z=path[i+1]
 if c[2]!=a[2] or c[2]!=z[2] or (c[0]-a[0],c[1]-a[1])!=(z[0]-c[0],z[1]-c[1]):way.append(c)
way.append(path[-1]);print('waypoints',len(way))
for a,z in zip(way,way[1:]):
 if a[:2]==z[:2]:via(a)
 else:trace(a,z,a[2])
p.SaveBoard(str(board_path),b)
