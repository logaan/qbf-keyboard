import argparse
import hashlib
import json
from pathlib import Path

from attach_models import module_instances

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('name', choices=['module1', 'module2', 'module3'])
parser.add_argument('output', type=Path)
args = parser.parse_args()
spec = json.loads((ROOT / 'boards/modules/design.json').read_text())
result = module_instances(spec, args.name)
paths = {ROOT / item['source'] for item in result['instances'] if item['kind'] == 'vrml'}
paths.update([ROOT / 'boards/modules/design.json', ROOT / 'scripts/attach_models.py'])
result['sources'] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(result, indent=2) + '\n')
