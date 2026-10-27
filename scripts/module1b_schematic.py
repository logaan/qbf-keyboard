import os
import copy
import json
import math
from pathlib import Path
import uuid
import sexpdata as sx

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'boards/module1b'
OUT=Path(os.environ.get('MODULE1B_OUTPUT',str(BASE/'source')))
SYMS=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols')
S=sx.Symbol

def tag(x):
    return str(x[0]) if isinstance(x,list) and x else ''

def child(x,k):
    return next((i for i in x if tag(i)==k),None)

def children(x,k):
    return [i for i in x if tag(i)==k]

def prop(x,k):
    return next((i for i in children(x,'property') if i[1]==k),None)

def uid(name):
    return str(uuid.uuid5(uuid.NAMESPACE_URL,'qbf-module1b/'+name))

def form(text):
    return sx.loads(text)

def label(name,x,y,angle=0):
    return [S('global_label'),name,[S('shape'),S('input')],[S('at'),round(x,4),round(y,4),angle],[S('effects'),[S('font'),[S('size'),0.8,0.8]],[S('justify'),S('left'),S('bottom')]],[S('uuid'),S(uid(f'label/{name}/{x}/{y}'))]]

def build():
    overrides=json.loads((BASE/'parts.json').read_text())
    original=sx.loads((BASE/'vendor/mikoto/mikoto.kicad_sch').read_text())
    libs=copy.deepcopy(child(original,'lib_symbols'))
    old={prop(x,'Reference')[2]:x for x in children(original,'symbol') if prop(x,'Reference')}
    parts=json.loads((OUT/'components.json').read_text())
    rootid=uid('root')
    document=[S('kicad_sch'),[S('version'),20211123],[S('generator'),S('eeschema')],[S('uuid'),S(rootid)],[S('paper'),'A1'],[S('title_block'),[S('title'),'Module1b - engineering prototype'],[S('rev'),'0.1'],[S('company'),'QBF / derived controller: zhiayang Mikoto rev6.3, Apache-2.0']],libs]
    paths=[S('symbol_instances')]
    mapping={}
    def load_symbol(libid):
        for item in children(libs,'symbol'):
            if item[1]==libid:return item
        lib,name=libid.split(':',1)
        source=sx.loads((SYMS/(lib+'.kicad_sym')).read_text())
        symbol=copy.deepcopy(next(x for x in children(source,'symbol') if x[1]==name))
        if child(symbol,'extends'):raise ValueError('Inherited library symbol: '+libid)
        symbol[1]=libid
        libs.append(symbol)
        return symbol
    def add(part,libid,x,y,angle=0):
        x=round(x/1.27)*1.27;y=round(y/1.27)*1.27
        ref=part['reference'];symbolid=uid('symbol/'+ref)
        symbol=load_symbol(libid)
        if libid=='mikoto:USB_C_Receptacle_USB2.0':
            for unit in children(symbol,'symbol'):
                for pin in children(unit,'pin'):
                    at=child(pin,'at');at[1]=round(at[1]/1.27)*1.27
        instance=[S('symbol'),[S('lib_id'),libid],[S('at'),x,y,angle],[S('unit'),1],[S('in_bom'),S('no' if ref in ('AE1','NT1') or ref.startswith('TP') else 'yes')],[S('on_board'),S('yes')],[S('uuid'),S(symbolid)]]
        properties={'Reference':ref,'Value':part['value'],'Footprint':('Module1b:'+ref) if part['footprint'] else ''}
        if ref in old:
            for p in children(old[ref],'property'):
                if p[1] not in properties and p[1] not in ('ki_keywords','ki_description','ki_fp_filters'):properties[p[1]]=p[2].replace("\u200e", "")
        if ref=='R7':properties.update({'Manufacturer Part':'RC0402FR-078K66L','LCSC Part':'C185387','JLC Part':'C185387','Datasheet':'https://www.ti.com/lit/ds/symlink/bq24075.pdf'})
        if ref in overrides:
            row=overrides[ref]
            if ref in ('U2','U5','DISP1'):properties['Value']=row['mpn']
            properties.update({'Manufacturer Part':row['mpn'],'LCSC Part':row['lcsc'],'JLC Part':row['lcsc'],'Assembly status':row['status']})
        for index,(name,value) in enumerate(properties.items()):
            effects=[S('effects'),[S('font'),[S('size'),1,1]]]
            if index>1:effects.append(S('hide'))
            instance.append([S('property'),name,value,[S('id'),index],[S('at'),x,y-5-index*1.5,0],effects])
        pins=[]
        for unit in children(symbol,'symbol'):
            if str(unit[1]).endswith(('_1_1','_0_1','_0_0')):pins.extend(children(unit,'pin'))
        for pin in pins:
            number=str(child(pin,'number')[1]);local=child(pin,'at');px,py=local[1:3]
            a=math.radians(angle)
            tx=round(x+px*math.cos(a)-py*math.sin(a),4);ty=round(y-px*math.sin(a)-py*math.cos(a),4)
            net='GND' if ref=='J1' and number.startswith('S') else part['pads'].get(number,'')
            instance.append([S('pin'),number,[S('uuid'),S(uid(f'pin/{ref}/{number}'))]])
            if not net or net.startswith('unconnected-') or (ref=='U1' and net in {'CHARGE_CTRL_1','CHARGE_CTRL_2','P0.09','P0.10','P0.25'}):
                document.append([S('no_connect'),[S('at'),tx,ty],[S('uuid'),S(uid(f'nc/{ref}/{number}'))]])
            else:document.append(label(net.lstrip('/'),tx,ty))
        document.append(instance)
        paths.append([S('path'),'/'+symbolid,[S('reference'),ref],[S('unit'),1],[S('value'),part['value']],[S('footprint'),('Module1b:'+ref) if part['footprint'] else '']])
        mapping[ref]=symbolid
    order=sorted(parts,key=lambda p:(0 if p['reference']=='U1' else 1,p['reference']))
    slot=0
    for part in order:
        ref=part['reference']
        if ref in old:libid=child(old[ref],'lib_id')[1]
        elif ref.startswith('S') and ref not in {'SW1','SW2'}:libid='Switch:SW_Push'
        elif ref=='SW1':libid='Switch:SW_SPDT'
        elif ref=='SW2':libid='Switch:SW_Push'
        elif ref=='J2':libid='Connector_Generic:Conn_01x02'
        elif ref=='DISP1':libid='Connector_Generic:Conn_01x05'
        elif ref.startswith('H'):libid='Mechanical:MountingHole_Pad'
        else:raise ValueError(ref)
        if ref=='U1':x,y=105,120
        else:
            x,y=235+(slot%8)*72,40+(slot//8)*49
            slot+=1
        add(part,libid,x,y)
    for i,net in enumerate(['GND','VBUS','VDD_NRF','VSS_PA','Net-(C23-Pad1)']):
        add({'reference':f'#FLG0{i+1}','value':'PWR_FLAG','footprint':'','pads':{'1':net}},'power:PWR_FLAG',40+i*35,280)
    document.append([S('sheet_instances'),[S('path'),'/',[S('page'),'1']]])
    document.append(paths)
    renames={}
    standalone=[S('kicad_symbol_lib'),[S('version'),20211014],[S('generator'),S('kicad_symbol_editor')]]
    for symbol in children(libs,'symbol'):
        oldname=symbol[1];name=oldname.replace(':','_');renames[oldname]='Module1b:'+name
        base=oldname.split(':')[-1]
        for nested in children(symbol,'symbol'):
            nested[1]=name+str(nested[1])[len(base):]
        symbol[1]='Module1b:'+name
        external=copy.deepcopy(symbol);external[1]=name;standalone.append(external)
    for symbol in children(document,'symbol'):
        entry=child(symbol,'lib_id');entry[1]=renames[entry[1]]
    (OUT/'Module1b.kicad_sym').write_text(sx.dumps(standalone)+'\n')
    (OUT/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "Module1b") (type "KiCad") (uri "${KIPRJMOD}/Module1b.kicad_sym") (options "") (descr "Project-local pinned symbols")))\n')
    (OUT/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "Module1b") (type "KiCad") (uri "${KIPRJMOD}/Module1b.pretty") (options "") (descr "Module1b footprints")))\n')
    (OUT/'module1b.kicad_sch').write_text(sx.dumps(document)+'\n')
    (OUT/'schematic-map.json').write_text(json.dumps({'root':rootid,'symbols':mapping},indent=2)+'\n')

if __name__=='__main__':build()
