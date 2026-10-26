import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

import numpy as np
from PIL import Image, ImageFilter

from modules import check
from toolchain import kicad_cli, kicad_python

ROOT = Path(__file__).resolve().parents[1]
SCENE = ROOT / 'anime-render/scene.json'
OUT = ROOT / 'anime-render/generated'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def signature(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def run(command, logfile):
    logfile.parent.mkdir(parents=True, exist_ok=True)
    with logfile.open('w') as log:
        result = subprocess.run([str(v) for v in command], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(f'Command failed; inspect {logfile}')


def renderer():
    executable = os.environ.get('BLENDER') or shutil.which('blender')
    if not executable and Path('/Applications/Blender.app/Contents/MacOS/Blender').exists():
        executable = '/Applications/Blender.app/Contents/MacOS/Blender'
    if not executable:
        raise ValueError('Blender is missing. Select setup and install system tools in scripts/start.command.')
    return executable


def prepare(number):
    name = f'module{number}'
    check(name)
    native = OUT / 'native' / name
    native.mkdir(parents=True, exist_ok=True)
    board = ROOT / f'boards/modules/generated/{name}/pcbs/{name}.kicad_pcb'
    components = native / 'components.json'
    run([kicad_python(), ROOT / 'scripts/prepare_module_render.py', name, components], native / 'prepare.log')
    stamp = native / 'pcb.sha256'
    if not (native / 'board.glb').exists() or not stamp.exists() or stamp.read_text() != sha(board):
        run([kicad_cli(), 'pcb', 'export', 'glb', '--force', '--board-only', '--include-tracks', '--include-pads',
             '--include-zones', '--include-soldermask', '--user-origin', '100x100mm', '-o', native / 'board.glb', board], native / 'export.log')
        stamp.write_text(sha(board))
    return signature({'board': sha(board), 'glb': sha(native / 'board.glb'), 'components': sha(components)})


def render(output, arguments, identity):
    stamp = output.with_suffix('.json')
    if output.exists() and stamp.exists():
        prior = json.loads(stamp.read_text())
        if prior.get('identity') == identity and prior.get('sha256') == sha(output):
            return
    print(f'Rendering {output.name}', flush=True)
    run([renderer(), '-b', '--python', ROOT / 'scripts/render_modules_blender.py', '--', *arguments, '--output', output], output.with_suffix('.log'))
    stamp.write_text(json.dumps({'identity': identity, 'sha256': sha(output)}, indent=2) + '\n')


def grade(image, spec):
    rgba = np.asarray(image.convert('RGBA'), dtype=np.float32) / 255
    rgb = rgba[:, :, :3]
    shadow = (np.max(rgb, axis=2) < 0.12) & (rgba[:, :, 3] < 0.999)
    shadow_alpha = np.where(shadow, rgba[:, :, 3], 0)
    rgba[:, :, 3][shadow] = 0
    luminance = np.sum(rgb * np.array([0.2126, 0.7152, 0.0722]), axis=2, keepdims=True)
    rgb = luminance + (rgb - luminance) * spec['saturation']
    rgb = (rgb - 0.5) * spec['contrast'] + 0.5
    rgb *= np.array(spec['warmth_rgb'])
    rgba[:, :, :3] = np.clip(rgb, 0, 1)
    foreground = Image.fromarray(np.uint8(np.clip(rgba, 0, 1) * 255))
    shadow_mask = Image.fromarray(np.uint8(shadow_alpha * 255 * spec['shadow_opacity'])).filter(ImageFilter.GaussianBlur(2.2))
    shadow_layer = Image.new('RGBA', image.size, (22, 14, 8, 0))
    shadow_layer.putalpha(shadow_mask)
    return Image.alpha_composite(shadow_layer, foreground)


def main():
    parser = argparse.ArgumentParser(description='Render CAD boards and composite all four pairs onto the single reusable anime background.')
    parser.add_argument('--native-only', action='store_true')
    parser.add_argument('--module', type=int, choices=[1, 2, 3])
    parser.add_argument('--composite-only', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    settings = json.loads(SCENE.read_text())
    if args.check:
        manifest = json.loads((OUT / 'manifest.json').read_text())
        for relative, checksum in manifest['sources'].items():
            if sha(ROOT / relative) != checksum:
                raise ValueError(f'Stale anime render source: {relative}')
        for relative, checksum in manifest['outputs'].items():
            if sha(OUT / relative) != checksum:
                raise ValueError(f'Changed anime render: {relative}')
        for number in (1, 2, 3):
            check(f'module{number}')
        print('Anime render sources, four composites and PCB checks PASS')
        return
    selected = [args.module] if args.native_only and args.module else [1, 2, 3]
    identifiers = {number: prepare(number) for number in selected}
    source = ROOT / 'scripts/render_modules_blender.py'
    camera_scene = {key: value for key, value in settings.items() if key not in ('grading', 'background', 'pairs')}
    for number in selected:
        if args.composite_only:
            break
        for view in ('angled', 'cap-free', 'underside'):
            identity = signature([identifiers[number], sha(source), camera_scene, view])
            render(OUT / 'native' / f'module{number}' / f'{view}.png', ['--module', str(number), '--view', view], identity)
    if args.native_only:
        return
    background_path = ROOT / 'anime-render' / settings['background']
    if not background_path.exists():
        raise ValueError('Reusable anime background is missing; restore the committed asset or request image generation through Codex.')
    provenance = json.loads((ROOT / 'anime-render/background-provenance.json').read_text())
    if provenance['output']['sha256'] != sha(background_path):
        raise ValueError('Background changed without matching generation provenance')
    for key in ('lens_mm', 'position_mm', 'target_mm'):
        if provenance['camera'][key] != settings['camera'][key]:
            raise ValueError(f'Camera {key} differs from the reusable background request; review alignment before regenerating')
    background = Image.open(background_path).convert('RGBA').resize((settings['image']['width'], settings['image']['height']), Image.Resampling.LANCZOS)
    composites = []
    for left, right in settings['pairs']:
        raw = OUT / 'raw' / f'{left}-{right}.png'
        identity = signature([identifiers[left], identifiers[right], sha(source), camera_scene])
        if args.composite_only:
            stamp = json.loads(raw.with_suffix('.json').read_text())
            if stamp['identity'] != identity or stamp['sha256'] != sha(raw):
                raise ValueError(f'Stale CAD render {raw}; run the full anime render first')
        else:
            render(raw, ['--pair', str(left), str(right)], identity)
        graded = grade(Image.open(raw), settings['grading'])
        (OUT / 'graded').mkdir(exist_ok=True)
        graded.save(OUT / 'graded' / raw.name)
        result = Image.alpha_composite(background, graded).convert('RGB')
        target = OUT / f'pair-{left}-{right}.png'
        result.save(target)
        composites.append(target)
        print(f'Composited {target.relative_to(ROOT)}', flush=True)
    sheet = Image.new('RGB', (1920, 1280), '#ede0ca')
    for index, path in enumerate(composites):
        thumb = Image.open(path).resize((960, 640), Image.Resampling.LANCZOS)
        sheet.paste(thumb, ((index % 2) * 960, (index // 2) * 640))
    sheet.save(OUT / 'contact-sheet.png')
    sources = [SCENE, background_path, ROOT / 'anime-render/background-provenance.json', source,
               Path(__file__), ROOT / 'scripts/attach_models.py', ROOT / 'boards/modules/design.json']
    for number in (1, 2, 3):
        sources.append(ROOT / f'boards/modules/generated/module{number}/pcbs/module{number}.kicad_pcb')
        data = json.loads((OUT / 'native' / f'module{number}' / 'components.json').read_text())
        sources.extend(ROOT / relative for relative in data['sources'])
    outputs = sorted(p for p in OUT.rglob('*.png'))
    manifest = {'sources': {str(p.relative_to(ROOT)): sha(p) for p in sorted(set(sources))},
                'outputs': {str(p.relative_to(OUT)): sha(p) for p in outputs},
                'background_generations': 1, 'pairs': settings['pairs'], 'camera': settings['camera'],
                'limitations': ['CAD camera uses an actual 40 mm lens; generated background perspective remains approximate.',
                                'Background tablet framing is an artistic compromise recorded in its provenance.',
                                'Component reference meshes and nominal envelopes are not a physical assembly clearance proof.']}
    (OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    main()
