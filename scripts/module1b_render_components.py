import json
from pathlib import Path
from attach_models import module_instances
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'boards/module1b'
spec=json.loads((BASE/'layout-reference.json').read_text());components=module_instances(spec,'module1')
components['instances']=[i for i in components['instances'] if i['name'].startswith('key_') or i['name'] in ('display','display_socket')]
components['limitations']=['Illustrative key/display assembly only; battery mounting unresolved and omitted','Socket, reset, power-switch, JST battery connector and 32 kHz crystal bodies have no available verified 3D model and are omitted','Display stack is inherited nominal envelope; supplier must verify clearance','Actual routed PCB and available manufacturer/package models are used']
path=BASE/'generated/native/module1b/components.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(components,indent=2)+'\n')
