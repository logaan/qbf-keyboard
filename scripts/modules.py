import hashlib
import html
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

import yaml

from toolchain import kicad_cli, kicad_python

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'boards/modules'
GENERATED = SOURCE / 'generated'
PINS = ['P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10', 'P14', 'P15', 'P16', 'P18', 'P19']


def digest():
    paths = [SOURCE / 'design.json', SOURCE / 'hardware.yaml', SOURCE / 'project.json', Path(__file__), ROOT / 'scripts/module_pcb.py', ROOT / 'scripts/route_modules.py', ROOT / 'scripts/route_board.py', ROOT / 'scripts/toolchain.py', ROOT / 'package-lock.json']
    paths += sorted((SOURCE / 'footprints').rglob('*'))
    h = hashlib.sha256()
    for path in paths:
        if path.is_file():
            h.update(str(path.relative_to(ROOT)).encode())
            h.update(path.read_bytes())
    return h.hexdigest()


def design():
    return json.loads((SOURCE / 'design.json').read_text())


def interactions(spec, name):
    module = spec['modules'][name]
    items = []
    for row_index, row in enumerate(module['rows']):
        for column in row['columns']:
            items.append({'name': f'key_r{row_index + 1}_c{column + 1}', 'kind': 'key',
                          'x': (column - 1.5) * spec['pitch'], 'y': row['y'],
                          'size': spec['keycaps'][row['cap']], 'cap': row['cap'], 'side': 'F'})
    items.append({'name': 'display', 'kind': 'display', 'x': module.get('display_x', 0), 'y': module['display_y'],
                  'size': module.get('display_size', spec['display']['size']), 'side': module.get('display_side', spec['display']['side'])})
    if 'trackpad_y' in module:
        items.append({'name': 'trackpad', 'kind': 'trackpad', 'x': module.get('trackpad_x', 0), 'y': module['trackpad_y'],
                      'size': spec['trackpad']['size'], 'side': spec['trackpad']['side']})
    return items


def validate(spec, name):
    errors = []
    items = interactions(spec, name)
    outline = spec['outline']
    width, height, radius = (outline[k] for k in ('width', 'height', 'corner'))
    if not (70 <= width <= 85 and 70 <= height <= 90):
        errors.append('Outline is outside the agreed approximate half-phone size range')
    cap_w, cap_h = spec['keycaps']['portrait_1_5u']
    if not (15 <= cap_w <= 19 and 24 <= cap_h <= 29):
        errors.append('Portrait 1.5U keycap dimensions are outside the supported envelope range')
    if sum(i.get('cap') == 'portrait_1_5u' for i in items) < 4:
        errors.append('At least four portrait 1.5U keys are required')
    if name == 'module1':
        rows = spec['modules'][name]['rows']
        if len(rows) != 3 or [r['cap'] for r in sorted(rows, key=lambda r: -r['y'])] != ['portrait_1_5u', 'one_u', 'portrait_1_5u'] or any(r['columns'] != [0, 1, 2, 3] for r in rows):
            errors.append('Module 1 requires twelve keys: four 1U keys between two rows of four 1.5U keys')
    for item in items:
        required_side = 'B' if name == 'module1' and item['kind'] == 'display' else 'F'
        if item['side'] != required_side:
            errors.append(f'{item["name"]}: must be on the {"underside" if required_side == "B" else "top face"}')
        mirrored = any(i['kind'] == item['kind'] and i['size'] == item['size'] and
                       abs(i['x'] + item['x']) < 1e-6 and abs(i['y'] - item['y']) < 1e-6 for i in items)
        asymmetric_allowed = spec['modules'][name].get('allow_asymmetric_interactions', False) and item['kind'] != 'key'
        if not mirrored and not asymmetric_allowed:
            errors.append(f'{item["name"]}: missing mirrored interaction')
        for sx in (-1, 1):
            for sy in (-1, 1):
                x = abs(item['x'] + sx * item['size'][0] / 2)
                y = abs(item['y'] + sy * item['size'][1] / 2)
                dx, dy = max(0, x - width / 2 + radius), max(0, y - height / 2 + radius)
                if x > width / 2 or y > height / 2 or dx * dx + dy * dy > radius * radius + 1e-6:
                    errors.append(f'{item["name"]}: envelope exceeds rounded outline')
    for index, a in enumerate(items):
        for b in items[index + 1:]:
            if a['side'] == b['side'] and abs(a['x'] - b['x']) < (a['size'][0] + b['size'][0]) / 2 and abs(a['y'] - b['y']) < (a['size'][1] + b['size'][1]) / 2:
                errors.append(f'{a["name"]}/{b["name"]}: overlapping interaction envelopes')
    if errors:
        raise ValueError('\n'.join(sorted(set(errors))))
    return items


def configuration(spec, name):
    items = validate(spec, name)
    footprints = yaml.safe_load((SOURCE / 'hardware.yaml').read_text())
    required = {'switches', 'controller', 'display', 'reset', 'power', 'battery_connector', 'mounts'}
    if set(footprints) != required:
        raise ValueError('Required hardware footprints changed')
    footprints['display']['adjust.rotate'] = spec['modules'][name].get('display_rotation', spec['display']['rotation'])
    footprints['display']['params']['side'] = spec['modules'][name].get('display_side', spec['display']['side'])
    footprints['controller']['params']['side'] = spec['controller']['side']
    footprints['controller']['adjust.rotate'] = spec['modules'][name].get('controller_rotation', 0)
    footprints['mounts']['params'].update(hole_size=spec['outline']['mount_diameter'], hole_drill=spec['outline']['mount_diameter'])
    zones = {}

    def point(key, x, y, tags, size=(1, 1)):
        zones[key] = {'anchor': {'shift': [100 + x, -100 + y]},
                      'key': {'tags': tags, 'width': size[0], 'height': size[1]}}

    keys = [i for i in items if i['kind'] == 'key']
    for item in items:
        point(item['name'], item['x'], item['y'], ['switch', item['cap']] if item['kind'] == 'key' else [item['kind']], item['size'])
    if len(keys) > len(PINS):
        raise ValueError('Not enough direct GPIOs')
    for pin, key in zip(PINS, keys):
        footprints['controller']['params'][pin] = key['name']
    for key in ('controller', 'battery'):
        point(key, spec['modules'][name].get(f'{key}_x', spec[key]['x']), spec['modules'][name].get(f'{key}_y', spec[key]['y']), [key])
    point('reset', -32, -12, ['reset'])
    point('power', 0, -34, ['power'])
    point('jst', spec['modules'][name].get('jst_x', 22), spec['modules'][name].get('jst_y', 12), ['jst'])
    if 'trackpad_y' in spec['modules'][name]:
        point('touch_connector', -31, 22, ['touch_connector'])
        footprints['controller']['params'].update(P14='TP_SDA', P15='TP_SCL', P16='TP_RDY', P18='TP_RST')
        footprints['touch_connector'] = {'what': 'local/tps43_connector', 'where': 'touch_connector',
                                       'params': {'side': 'B', 'VCC': '3V3', 'GND': 'GND', 'SDA': 'TP_SDA', 'SCL': 'TP_SCL', 'RDY': 'TP_RDY', 'RST': 'TP_RST'}}
        for index, (net, x, y, value) in enumerate([('TP_SDA', -20, 29, '4.7k'), ('TP_SCL', -20, 24, '4.7k'), ('TP_RDY', -13, 29, '10k'), ('TP_RST', -13, 24, '10k')], 1):
            key = f'pullup_{index}'
            point(key, x, y, [key])
            footprints[key] = {'what': 'local/resistor_0805', 'where': key, 'params': {'side': 'B', 'value': value, 'from': '3V3', 'to': net}}
    o = spec['outline']
    for sx in (-1, 1):
        for sy in (-1, 1):
            point(f'mount_{sx}_{sy}', sx * (o['width'] / 2 - o['mount_inset']), sy * (o['height'] / 2 - o['mount_inset']), ['mount'])
    outlines = {
        'pcb_boundary': [{'what': 'rectangle', 'where': {'shift': [100, -100]}, 'size': [o['width'], o['height']], 'corner': o['corner']}],
        'keycaps': [{'what': 'rectangle', 'where': cap, 'size': size, 'corner': 1} for cap, size in spec['keycaps'].items()],
        'display': [{'what': 'rectangle', 'where': 'display', 'size': spec['modules'][name].get('display_size', spec['display']['size'])}],
        'battery': [{'what': 'rectangle', 'where': 'battery', 'size': spec['battery']['size'][:2][::-1] if spec['modules'][name].get('battery_rotation', 0) == 90 else spec['battery']['size'][:2]}],
        'mount_holes': [{'what': 'circle', 'where': 'mount', 'radius': o['mount_diameter'] / 2}]
    }
    pcb_outlines = {'edge': {'outline': 'pcb_boundary'}, 'caps': {'outline': 'keycaps', 'layer': 'Dwgs.User'},
                    'screen': {'outline': 'display', 'layer': 'B.Fab' if footprints['display']['params']['side'] == 'B' else 'Dwgs.User'}, 'cell': {'outline': 'battery', 'layer': 'B.Fab'}}
    if 'trackpad_y' in spec['modules'][name]:
        outlines['trackpad'] = [{'what': 'rectangle', 'where': 'trackpad', 'size': spec['trackpad']['size'], 'corner': 2}]
        pcb_outlines['touch'] = {'outline': 'trackpad', 'layer': 'Dwgs.User'}
    return {'meta': {'name': name, 'engine': '4.2.1', 'version': '0.2.0'}, 'points': {'zones': zones},
            'outlines': outlines, 'pcbs': {name: {'template': 'kicad8', 'references': True, 'outlines': pcb_outlines, 'footprints': footprints}}}


def preview(spec, name, path):
    items = interactions(spec, name)
    w, h = spec['outline']['width'], spec['outline']['height']
    elements = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-w/2-4} {-h/2-8} {w+8} {h+16}" width="650" height="700">',
                '<rect x="-100" y="-100" width="200" height="200" fill="white"/>',
                f'<rect x="{-w/2}" y="{-h/2}" width="{w}" height="{h}" rx="{spec["outline"]["corner"]}" fill="#ddebe5" stroke="#234" stroke-width="0.2"/>']
    for item in items:
        if item['side'] != 'F':
            continue
        x, y = item['x'], -item['y']
        iw, ih = item['size']
        color = {'key': '#aecbeb', 'display': '#c6b5df', 'trackpad': '#e8cb8a'}[item['kind']]
        elements.append(f'<rect x="{x-iw/2}" y="{y-ih/2}" width="{iw}" height="{ih}" rx="1" fill="{color}" stroke="#234" stroke-width="0.2"/>')
        elements.append(f'<text x="{x}" y="{y}" font-size="2" text-anchor="middle">{html.escape(item["name"])}</text>')
    elements.append(f'<text x="0" y="{-h/2-3}" font-size="2.5" text-anchor="middle">{name}: {w} × {h} mm; PCB REVIEW</text>')
    elements.append('<text x="0" y="42" font-size="2" text-anchor="middle">Nominal interaction envelopes; physical stack unverified</text></svg>')
    path.write_text(''.join(elements))


def check(name):
    spec = design()
    validate(spec, name)
    folder = GENERATED / name
    report = json.loads((folder / 'validation.json').read_text())
    if report['source_sha256'] != digest():
        raise ValueError(f'{name}: stale outputs; rebuild before review')
    for relative, checksum in report['outputs'].items():
        if hashlib.sha256((folder / relative).read_bytes()).hexdigest() != checksum:
            raise ValueError(f'{name}: generated artifact changed: {relative}')
    expected = configuration(spec, name)
    actual = yaml.safe_load((folder / 'source/config.yaml').read_text())
    if actual != expected:
        raise ValueError(f'{name}: generated configuration differs from source')
    points = yaml.safe_load((folder / 'ergogen/points/points.yaml').read_text())
    for item in interactions(spec, name):
        p = points[item['name']]
        if abs(p['x'] - 100 - item['x']) > 1e-6 or abs(p['y'] + 100 - item['y']) > 1e-6:
            raise ValueError(f'{name}: generated point differs: {item["name"]}')
    drc = json.loads((folder / 'drc.json').read_text())
    if any(drc.get(key) for key in ('violations', 'unconnected_items', 'schematic_parity')):
        raise ValueError(f'{name}: routed DRC is not clean')
    routing = json.loads((folder / 'routing.json').read_text())
    if routing['unconnected'] or len(routing['ground_zones']) != 2 or any(z['board_bbox_coverage'] < 0.6 for z in routing['ground_zones']):
        raise ValueError(f'{name}: routing or ground plane verification failed')
    print(f'{name}: layout, hashes, routed DRC and broad ground planes PASS; physical review pending')


def build(name):
    spec = design()
    config = configuration(spec, name)
    GENERATED.mkdir(exist_ok=True)
    destination = GENERATED / name
    if destination.exists() and list(destination.rglob('*.lck')):
        raise ValueError(f'{name}: close KiCad before rebuilding')
    with tempfile.TemporaryDirectory(prefix=f'.{name}-', dir=GENERATED) as temporary:
        stage = Path(temporary)
        source = stage / 'source'
        source.mkdir()
        (source / 'config.yaml').write_text(yaml.safe_dump(config, sort_keys=False))
        shutil.copytree(SOURCE / 'footprints', source / 'footprints')
        for local, upstream in {'nice_nano_extended': 'mcu_nice_nano', 'mounting_hole_npth': 'mounting_hole_npth'}.items():
            target = source / 'footprints/local' / f'{local}.js'
            target.write_text((SOURCE / 'footprints/ceoloide' / f'{upstream}.js').read_text() + '\n' + target.read_text())
        subprocess.run([str(ROOT / 'node_modules/.bin/ergogen'), str(source), '-o', str(stage / 'ergogen'), '--debug', '--svg'], cwd=ROOT, check=True)
        shutil.rmtree(source / 'footprints')
        board = stage / 'ergogen/pcbs' / f'{name}.kicad_pcb'
        cli = kicad_cli()
        shutil.copyfile(SOURCE / 'project.json', board.with_suffix('.kicad_pro'))
        subprocess.run([kicad_python(), str(ROOT / 'scripts/module_pcb.py'), str(board), str(stage / 'electrical.json'), '--display-side', spec['modules'][name].get('display_side', spec['display']['side'])], check=True)
        subprocess.run([cli, 'pcb', 'drc', '--format', 'json', '--severity-all', '-o', str(stage / 'placement-drc.json'), str(board)], check=True)
        subprocess.run([cli, 'pcb', 'export', 'svg', '--layers', 'F.Fab,F.SilkS,Dwgs.User,Edge.Cuts', '--sketch-pads-on-fab-layers', '--page-size-mode', '2', '--exclude-drawing-sheet', '--mode-single', '-o', str(stage / 'pcb.svg'), str(board)], check=True)
        placement_drc = json.loads((stage / 'placement-drc.json').read_text())
        if placement_drc['violations']:
            failure = GENERATED / 'failed' / name
            shutil.copytree(stage, failure, dirs_exist_ok=True)
            raise ValueError(f'{name}: placement conflicts must be fixed before routing; inspect {failure}')
        pcbs = stage / 'pcbs'
        pcbs.mkdir()
        routed = pcbs / f'{name}.kicad_pcb'
        shutil.copyfile(SOURCE / 'project.json', routed.with_suffix('.kicad_pro'))
        try:
            with (stage / 'routing.log').open('w') as log:
                subprocess.run([kicad_python(), str(ROOT / 'scripts/route_modules.py'), str(board), str(routed), str(SOURCE / 'design.json'), '--strategy', spec['modules'][name].get('routing_strategy', 'longest')], stdout=log, stderr=subprocess.STDOUT, check=True, timeout=300)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
            failure = GENERATED / 'failed' / name
            shutil.copytree(stage, failure, dirs_exist_ok=True)
            raise ValueError(f'Routing failed; previous output retained; inspect {failure}') from error
        subprocess.run([cli, 'pcb', 'drc', '--format', 'json', '--severity-all', '--exit-code-violations', '-o', str(stage / 'drc.json'), str(routed)], check=True)
        for side in ('F', 'B'):
            subprocess.run([cli, 'pcb', 'export', 'svg', '--layers', f'{side}.Cu,{side}.SilkS,Edge.Cuts', '--page-size-mode', '2', '--exclude-drawing-sheet', '--mode-single', '-o', str(stage / f'copper-{side}.svg'), str(routed)], check=True)
        preview(spec, name, stage / 'layout.svg')
        report = {'stage': 'routed PCB', 'review': 'pending', 'fabrication_ready': False,
                  'source_sha256': digest(), 'outline': spec['outline'],
                  'key_count': sum(i['kind'] == 'key' for i in interactions(spec, name)),
                  'blockers': ['User PCB review required before fabrication', 'Battery procurement, protection, antenna reservation and mechanical stack unverified'],
                  'outputs': {str(p.relative_to(stage)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(stage.rglob('*')) if p.is_file() and p.suffix not in ('.log', '.kicad_prl', '.lck')}}
        drc = json.loads((stage / 'drc.json').read_text())
        report['drc'] = {key: len(drc.get(key, [])) for key in ('violations', 'unconnected_items', 'schematic_parity')}
        if name == 'module3':
            report['blockers'].append('TPS43 six-signal header follows manufacturer Table 2.1; confirm the physical FPC cable adapter and sensor overlay before fabrication')
        (stage / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
        backup = GENERATED / f'.{name}-previous'
        if backup.exists():
            raise ValueError(f'Recover interrupted build from {backup} before rebuilding')
        if destination.exists():
            destination.rename(backup)
        try:
            stage.rename(destination)
        except BaseException:
            if backup.exists():
                backup.rename(destination)
            raise
        if backup.exists():
            shutil.rmtree(backup)
    check(name)
