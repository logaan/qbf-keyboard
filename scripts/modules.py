import copy
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
    paths = [SOURCE / 'design.json', SOURCE / 'hardware.yaml', Path(__file__), ROOT / 'scripts/module_pcb.py', ROOT / 'scripts/toolchain.py', ROOT / 'package-lock.json']
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
    items.append({'name': 'display', 'kind': 'display', 'x': 0, 'y': module['display_y'],
                  'size': spec['display']['size'], 'side': spec['display']['side']})
    if 'trackpad_y' in module:
        items.append({'name': 'trackpad', 'kind': 'trackpad', 'x': 0, 'y': module['trackpad_y'],
                      'size': [spec['trackpad']['diameter']] * 2, 'side': spec['trackpad']['side']})
    return items


def validate(spec, name):
    errors = []
    items = interactions(spec, name)
    outline = spec['outline']
    width, height, radius = (outline[k] for k in ('width', 'height', 'corner'))
    if not (70 <= width <= 85 and 70 <= height <= 90):
        errors.append('Outline is outside the agreed approximate half-phone size range')
    if sum(i.get('cap') == 'portrait_1_5u' for i in items) < 4:
        errors.append('At least four portrait 1.5U keys are required')
    for item in items:
        if item['side'] != 'F':
            errors.append(f'{item["name"]}: interaction must be on the top face')
        mirrored = any(i['kind'] == item['kind'] and i['size'] == item['size'] and
                       abs(i['x'] + item['x']) < 1e-6 and abs(i['y'] - item['y']) < 1e-6 for i in items)
        if not mirrored:
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
            if abs(a['x'] - b['x']) < (a['size'][0] + b['size'][0]) / 2 and abs(a['y'] - b['y']) < (a['size'][1] + b['size'][1]) / 2:
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
    footprints['display']['adjust.rotate'] = spec['display']['rotation']
    footprints['display']['params']['side'] = spec['display']['side']
    footprints['controller']['params']['side'] = spec['controller']['side']
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
        point(key, spec[key]['x'], spec[key]['y'], [key])
    point('reset', -32, 0, ['reset'])
    point('power', 22, -34, ['power'])
    point('jst', 22, -19, ['jst'])
    o = spec['outline']
    for sx in (-1, 1):
        for sy in (-1, 1):
            point(f'mount_{sx}_{sy}', sx * (o['width'] / 2 - o['mount_inset']), sy * (o['height'] / 2 - o['mount_inset']), ['mount'])
    outlines = {
        'pcb_boundary': [{'what': 'rectangle', 'where': {'shift': [100, -100]}, 'size': [o['width'], o['height']], 'corner': o['corner']}],
        'keycaps': [{'what': 'rectangle', 'where': cap, 'size': size, 'corner': 1} for cap, size in spec['keycaps'].items()],
        'display': [{'what': 'rectangle', 'where': 'display', 'size': spec['display']['size']}],
        'battery': [{'what': 'rectangle', 'where': 'battery', 'size': spec['battery']['size'][:2]}],
        'mount_holes': [{'what': 'circle', 'where': 'mount', 'radius': o['mount_diameter'] / 2}]
    }
    pcb_outlines = {'edge': {'outline': 'pcb_boundary'}, 'caps': {'outline': 'keycaps', 'layer': 'Dwgs.User'},
                    'screen': {'outline': 'display', 'layer': 'Dwgs.User'}, 'cell': {'outline': 'battery', 'layer': 'B.Fab'}}
    if 'trackpad_y' in spec['modules'][name]:
        outlines['trackpad'] = [{'what': 'circle', 'where': 'trackpad', 'radius': spec['trackpad']['diameter'] / 2}]
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
        x, y = item['x'], -item['y']
        iw, ih = item['size']
        color = {'key': '#aecbeb', 'display': '#c6b5df', 'trackpad': '#e8cb8a'}[item['kind']]
        if item['kind'] == 'trackpad':
            elements.append(f'<circle cx="{x}" cy="{y}" r="{iw/2}" fill="{color}" stroke="#234" stroke-width="0.2"/>')
        else:
            elements.append(f'<rect x="{x-iw/2}" y="{y-ih/2}" width="{iw}" height="{ih}" rx="1" fill="{color}" stroke="#234" stroke-width="0.2"/>')
        elements.append(f'<text x="{x}" y="{y}" font-size="2" text-anchor="middle">{html.escape(item["name"])}</text>')
    elements.append(f'<text x="0" y="{-h/2-3}" font-size="2.5" text-anchor="middle">{name}: {w} × {h} mm; ERGOGEN REVIEW ONLY</text>')
    elements.append('<text x="0" y="42" font-size="2" text-anchor="middle">No routing, sensor adapter or verified mechanical stack</text></svg>')
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
    print(f'{name}: layout constraints and generated source hashes PASS; Ergogen review pending')


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
        subprocess.run([kicad_python(), str(ROOT / 'scripts/module_pcb.py'), str(board), str(stage / 'electrical.json')], check=True)
        subprocess.run([cli, 'pcb', 'drc', '--format', 'json', '--severity-all', '-o', str(stage / 'placement-drc.json'), str(board)], check=True)
        subprocess.run([cli, 'pcb', 'export', 'svg', '--layers', 'F.Fab,F.SilkS,Dwgs.User,Edge.Cuts', '--sketch-pads-on-fab-layers', '--page-size-mode', '2', '--exclude-drawing-sheet', '--mode-single', '-o', str(stage / 'pcb.svg'), str(board)], check=True)
        preview(spec, name, stage / 'layout.svg')
        report = {'stage': 'ergogen', 'review': 'pending', 'fabrication_ready': False,
                  'source_sha256': digest(), 'outline': spec['outline'],
                  'key_count': sum(i['kind'] == 'key' for i in interactions(spec, name)),
                  'blockers': ['User Ergogen review required before KiCad routing', 'Battery procurement, protection and mechanical stack unverified', 'Firmware and mechanical stages not started'],
                  'outputs': {str(p.relative_to(stage)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(stage.rglob('*')) if p.is_file()}}
        drc = json.loads((stage / 'placement-drc.json').read_text())
        report['drc'] = {key: len(drc.get(key, [])) for key in ('violations', 'unconnected_items', 'schematic_parity')}
        report['blockers'].append('Placement DRC findings must be resolved in the reviewed KiCad stage')
        if name == 'module3':
            report['blockers'].append('Cirque candidate replaces oversized TPS43; sensor connector and electrical interface not implemented')
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
