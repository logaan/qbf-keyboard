import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from toolchain import kicad_cli,kicad_python

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'boards/module1b'
SOURCE=BASE/'source'
OUT=BASE/'generated'
BOARD=SOURCE/'module1b.kicad_pcb'
SCH=SOURCE/'module1b.kicad_sch'

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def run(*args):
    result=subprocess.run([str(v) for v in args],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    if result.returncode:raise RuntimeError(result.stdout)
    return result.stdout

def check():
    OUT.mkdir(exist_ok=True)
    cli=kicad_cli()
    run(cli,'sch','erc',SCH,'--format','json','-o',OUT/'erc.json')
    run(cli,'pcb','drc',BOARD,'--schematic-parity','--format','json','-o',OUT/'drc.json')
    run(cli,'sch','export','netlist','--format','kicadxml','-o',OUT/'netlist.xml',SCH)
    erc=json.loads((OUT/'erc.json').read_text());drc=json.loads((OUT/'drc.json').read_text())
    problems=[v for sheet in erc['sheets'] for v in sheet['violations']]+drc['violations']+drc['unconnected_items']+drc.get('schematic_parity',[])
    if problems:raise RuntimeError(f'Module1b has {len(problems)} check findings; see generated ERC/DRC reports')
    netlist=ET.parse(OUT/'netlist.xml')
    nets={(node.get('ref'),node.get('pin')):net.get('name') for net in netlist.findall('.//nets/net') for node in net.findall('node')}
    gpio=[nets[(f'S{i}','1')] for i in range(1,13)]
    assert len(set(gpio))==12 and all(n.startswith(('P0.','P1.')) for n in gpio)
    assert all(nets[(f'S{i}','2')]=='GND' for i in range(1,13))
    assert [nets[('J2',p)] for p in ('1','2')]==['VBAT','GND']
    assert [nets[('SW1',p)] for p in ('1','2','3')]==['VBAT','SYSOFF','GND']
    assert nets[('U2','15')]=='SYSOFF'
    assert nets[('R7','1')]=='GND'
    assert nets[('DISP1','3')]=='PPH_VCC' and nets[('U3','3')]=='PPH_VCC_CTRL'
    assert nets[('J1','A5')]=='CC1' and nets[('J1','B5')]=='CC2'
    assert nets[('R9','2')]=='GND' and nets[('R10','2')]=='GND'
    manifest={'stage':'routed engineering prototype','fabrication_ready':False,'erc_findings':0,'drc_findings':0,'unconnected_items':0,'schematic_parity_findings':0,'electrical_assertions':'passed','source_sha256':{str(p.relative_to(ROOT)):digest(p) for p in sorted([*[f for f in SOURCE.rglob('*') if f.is_file() and f.suffix!='.kicad_prl'],BASE/'design.json',BASE/'parts.json',BASE/'layout-reference.json',BASE/'ergogen.yaml',*ROOT.glob('scripts/module1b*.py')])},'required_release_checks':json.loads((BASE/'design.json').read_text())['release_blockers']}
    (OUT/'validation.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Module1b: ERC, DRC, schematic parity and electrical assertions pass; engineering prototype, not manufacturing release')
    return manifest

def export():
    validation=check();cli=kicad_cli();folder=OUT/'fabrication-review';folder.mkdir(exist_ok=True)
    run(cli,'pcb','export','gerbers','--check-zones','--layers','F.Cu,In1.Cu,In2.Cu,B.Cu,F.Mask,B.Mask,F.Paste,B.Paste,F.SilkS,B.SilkS,Edge.Cuts','-o',str(folder/'gerbers')+'/',BOARD)
    run(cli,'pcb','export','drill','--format','excellon','--excellon-separate-th','--generate-map','--map-format','svg','-o',str(folder/'gerbers')+'/',BOARD)
    run(cli,'pcb','export','pos','--format','csv','--units','mm','--side','both','-o',folder/'kicad-positions.csv',BOARD)
    components=json.loads((SOURCE/'components.json').read_text());xml=ET.parse(OUT/'netlist.xml');rows={}
    for c in xml.findall('.//components/comp'):
        fields={x.get('name'):x.text or '' for x in c.findall('fields/field')};rows[c.get('ref')]=(c.findtext('value'),fields)
    with (folder/'jlc-bom-review.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['Comment','Designator','Footprint','LCSC Part #','Manufacturer Part','Assembly status'])
        for c in sorted(components,key=lambda p:p['reference']):
            ref=c['reference']
            if ref in ('AE1','NT1') or ref.startswith('TP'):continue
            value,fields=rows[ref]
            w.writerow([value,ref,'Module1b:'+ref,fields.get('JLC Part',''),fields.get('Manufacturer Part',''),fields.get('Assembly status','Inherited catalog selection; quote and stock review required')])
    with (folder/'jlc-cpl-review.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['Designator','Mid X','Mid Y','Layer','Rotation'])
        for c in sorted(components,key=lambda p:p['reference']):
            ref=c['reference']
            if ref in ('AE1','NT1') or ref.startswith('TP'):continue
            w.writerow([ref,f"{c['position'][0]-62.4:.6f}mm",f"{137.6-c['position'][1]:.6f}mm",'bottom' if c['side']=='B.Cu' else 'top',c['angle']%360])
    for name in ('design.json','parts.json'):shutil.copy2(BASE/name,folder/name)
    shutil.copy2(SOURCE/'components.json',folder/'pin-map-and-placement.json')
    manifest={'status':'ENGINEERING REVIEW ONLY - NOT RELEASED FOR ORDER','checks':validation,'cpl_origin':'lower-left outline corner x62.4 y137.6; x right/y up; angles are KiCad angles, require JLC component-origin/rotation preview approval','files':{str(p.relative_to(folder)):digest(p) for p in sorted(folder.rglob('*')) if p.is_file() and p.name!='manifest.json'}}
    (folder/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    with zipfile.ZipFile(OUT/'module1b-fabrication-review.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(folder.rglob('*')):
            if p.is_file():z.write(p,str(p.relative_to(folder)))
    print('Module1b: four-layer Gerbers, drills, BOM and CPL exported for engineering review')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['build','check','export','preview','render','anime-render','pipeline','status','list']);args=parser.parse_args()
    if args.action in ('status','list'):
        print('module1b: routed bare-nRF52840 engineering prototype; not order-ready; boards/module1b/source/module1b.kicad_pro');return
    if args.action in ('build','check'):check()
    elif args.action=='export':export()
    elif args.action in ('preview','render','anime-render'):
        check();run(sys.executable,ROOT/'scripts/module1b_render.py')
    elif args.action=='pipeline':
        export();run(sys.executable,ROOT/'scripts/module1b_render.py')

if __name__=='__main__':main()
