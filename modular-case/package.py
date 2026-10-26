from pathlib import Path
import hashlib
import json
from zipfile import ZipFile, ZIP_DEFLATED

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'generated'
files=[OUT/(name+'_print.stl') for name in ('tray','rim','cover','bridge')]
files += [OUT/'manifest.json',OUT/'validation.json',OUT/'qbf_modular_case.FCStd',OUT/'dimensions.svg']
files += sorted(OUT.glob('*.png')) + sorted(OUT.glob('*.step'))
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
with ZipFile(OUT/'qbf-print-files.zip','w',ZIP_DEFLATED) as archive:
    for path in files:
        info_path='generated/'+path.name
        archive.write(path,info_path)
    archive.writestr('SHA256.json',json.dumps(manifest,indent=2)+'\n')
print('Packaged print bundle with checksums')
