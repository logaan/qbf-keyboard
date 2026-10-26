"""Repair edge-infringing reset placements in legacy routed drafts; add TPS43 clock.
Use KiCad pcbnew Python; copper changes must still be verified with DRC.
"""
from pathlib import Path
import pcbnew as p
root=Path(__file__).resolve().parents[1]/'kicad'
def xy(x,y): return p.VECTOR2I(round(x*1e6),round(y*1e6))
def trace(b,net,layer,points,width=.25):
 for a,z in zip(points,points[1:]):
  t=p.PCB_TRACK(b); t.SetStart(xy(*a)); t.SetEnd(xy(*z)); t.SetWidth(round(width*1e6)); t.SetLayer(layer); t.SetNet(net); b.Add(t)
def via(b,net,x,y):
 v=p.PCB_VIA(b); v.SetPosition(xy(x,y)); v.SetWidth(600000); v.SetDrill(300000); v.SetViaType(p.VIATYPE_THROUGH); v.SetLayerPair(p.F_Cu,p.B_Cu); v.SetNet(net); b.Add(v)
for n in (2,3):
 b=p.LoadBoard(str(root/f'module{n}_autorouted_base.kicad_pcb'))
 fs={f.GetReference():f for f in b.GetFootprints()}
 if n==2:
  # Free the power switch courtyard while retaining both routed nets.
  jst=fs['JST1'];jst.SetPosition(jst.GetPosition()+xy(0,-5.6))
  for pad in jst.Pads():
   v=pad.GetPosition();x=v.x/1e6;y=v.y/1e6
   trace(b,pad.GetNet(),p.F_Cu if pad.GetNumber()=='1' else p.B_Cu,
         [(x,y),(x,y+5.6)],width=.2)
 f=fs['RST1']; f.SetPosition(f.GetPosition()+xy(0,-2.7))
 pads={x.GetNumber():x for x in f.Pads()}
 def pos(i):
  a=pads[str(i)].GetPosition();return (a.x/1e6,a.y/1e6)
 g=pads['1'].GetNet(); rst=pads['2'].GetNet()
 x1,y1=pos(1); x2,y2=pos(2); x3,y3=pos(3); x4,y4=pos(4)
 # Both pairs are intentionally electrically redundant, but all four pads
 # must be tied down. Keep the RST jumper on B.Cu across the GND bus.
 trace(b,g,p.F_Cu,[pos(1),(x1,132.875)])
 if n==2:
  trace(b,g,p.F_Cu,[pos(3),(x3,133.9517)])
 else:
  via(b,g,x1,y1); via(b,g,x3,y3)
  trace(b,g,p.B_Cu,[pos(1),pos(3)])
 if n==2:
  trace(b,rst,p.F_Cu,[pos(2),(x2,132.875)])
  via(b,rst,x2,132.875)
 else:
  via(b,rst,x2,y2)
  via(b,rst,x2,133.9517)
  trace(b,rst,p.B_Cu,[(x2,y2),(x2,133.9517)])
  # Remove the orphaned original upper-pad stub (original endpoint 132.875).
  for t in list(b.GetTracks()):
   a,z=t.GetStart(),t.GetEnd()
   if (t.GetLayer()==p.F_Cu and t.GetNetname()=='RST' and
       a.x==xy(x2,0).x and z.x==xy(x2,0).x and
       {a.y,z.y}=={xy(0,132.875).y,xy(0,133.9517).y}):
    b.Remove(t)
 via(b,rst,x4,y4)
 trace(b,rst,p.B_Cu,[(x4,y4),(x2,132.875 if n==2 else 133.9517)])
 out=root/f'module{n}_routed.kicad_pcb';p.SaveBoard(str(out),b)
 print(out)
