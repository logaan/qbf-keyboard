import hashlib,json,subprocess
from pathlib import Path
from PIL import Image,ImageDraw
from anime_render import grade,renderer
from toolchain import kicad_cli,kicad_python
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'boards/module1b'
OUT=BASE/'generated'
NATIVE=OUT/'native/module1b'
NATIVE.mkdir(parents=True,exist_ok=True)
PREV=OUT/'previews';PREV.mkdir(exist_ok=True)
board=BASE/'source/module1b.kicad_pcb'
def run(args,name):
    with (OUT/(name+'.log')).open('w') as f:subprocess.run([str(v) for v in args],stdout=f,stderr=subprocess.STDOUT,check=True,cwd=ROOT)
run([kicad_python(),ROOT/'scripts/module1b_render_components.py'],'render-components')
components=json.loads((NATIVE/'components.json').read_text())
cli=kicad_cli()
run([cli,'pcb','export','glb','--force','--subst-models','--include-tracks','--include-pads','--include-zones','--include-soldermask','--user-origin','100x100mm','-o',NATIVE/'board.glb',board],'glb')
for side in ('top','bottom'):
    run([cli,'pcb','render','--width','1600','--height','1600','--side',side,'--quality','high','--output',PREV/('pcb-'+side+'.png'),board],'render-'+side)
for view in ('angled','cap-free','underside'):
    run([renderer(),'-b','--python',ROOT/'scripts/module1b_render_scene.py','--','--module','1b','--view',view,'--output',PREV/(view+'.png')],'render-'+view)
run([renderer(),'-b','--python',ROOT/'scripts/module1b_render_scene.py','--','--pair','1b','1b','--output',PREV/'pair-layer.png'],'render-pair')
settings=json.loads((ROOT/'anime-render/scene.json').read_text())
background=Image.open(ROOT/'anime-render'/settings['background']).convert('RGBA').resize((settings['image']['width'],settings['image']['height']))
layer=grade(Image.open(PREV/'pair-layer.png'),settings['grading'])
result=Image.alpha_composite(background,layer)
label=ImageDraw.Draw(result);label.rectangle((15,15,835,55),fill=(20,20,20,210));label.text((25,27),'Module1b engineering prototype - illustrative assembly; battery mount not validated',fill='white')
result.convert('RGB').save(PREV/'anime-module1b-pair.png')
(PREV/'manifest.json').write_text(json.dumps({'board_sha256':hashlib.sha256(board.read_bytes()).hexdigest(),'limitations':components['limitations'],'images':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(PREV.glob('*.png'))}},indent=2)+'\n')
print('Module1b native and anime previews rendered; see manifest for model limitations')
