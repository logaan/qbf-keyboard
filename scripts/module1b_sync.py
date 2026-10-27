import xml.etree.ElementTree as ET
from pathlib import Path
import pcbnew as pcb
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'boards/module1b'
path=BASE/'source/module1b.kicad_pcb'
b=pcb.LoadBoard(str(path))
xml=ET.parse(BASE/'generated/netlist.xml')
expected={(n.get('ref'),n.get('pin')):net.get('name') for net in xml.findall('.//nets/net') for n in net.findall('node')}
components={c.get('ref'):c for c in xml.findall('.//components/comp')}
renames={}
for f in b.GetFootprints():
    ref=f.GetReference();c=components[ref]
    f.SetValue(c.findtext('value') or '')
    f.SetExcludedFromBOM(ref in ('AE1','NT1') or ref.startswith('TP'))
    for field in c.findall('fields/field'):
        name=field.get('name')
        if name not in ('Footprint','Description'):
            f.SetField(name,field.text or '')
            f.GetField(name).SetVisible(False)
    for p in f.Pads():
        if ref=='SW2' and p.GetNumber() in ('3','4'):p.SetNumber({'3':'1','4':'2'}[p.GetNumber()])
        new=expected.get((ref,p.GetNumber()))
        if new and new.startswith('unconnected-'):new=new.replace('/','{slash}')
        if new and p.GetNetname() and new!=p.GetNetname():
            previous=renames.setdefault(p.GetNetname(),new)
            if previous!=new:raise ValueError('Ambiguous net rename')
for old,new in renames.items():b.FindNet(old).SetNetname(new)
pcb.SaveBoard(str(path),b)
print('net names synchronized',len(renames))
