"""Regenerate dimension-envelope meshes and real KiCad 3D review renders."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
subprocess.run([sys.executable, str(ROOT / "scripts/assembly_preview.py")], check=True)
subprocess.run(["node", str(ROOT / "scripts/preview.cjs")], check=True)
for board, side, rotate, filename in [
    ("braille_assembly_preview", "top", "330,0,25", "assembly-top"),
    ("braille_assembly_preview", "bottom", "330,0,25", "assembly-bottom"),
    ("braille_modules_preview", "bottom", "335,0,20", "modules-bottom"),
]:
    with (ROOT / "previews" / f"render-{filename}.log").open("w") as log:
        subprocess.run(["kicad-cli", "pcb", "render", "--width", "1376", "--height", "984",
                        "--side", side, "--rotate", rotate, "--zoom", "0.7",
                        "--quality", "high", "--background", "opaque",
                        "--output", str(ROOT / "previews" / f"{filename}.png"),
                        str(ROOT / "kicad" / f"{board}.kicad_pcb")],
                       stdout=log, stderr=subprocess.STDOUT, check=True)
    print("Rendered", filename)
with (ROOT / "models/step-export.log").open("w") as log:
    subprocess.run(["kicad-cli", "pcb", "export", "step", "--force", "--board-only",
                    "--output", str(ROOT / "models/routed-board.step"),
                    str(ROOT / "kicad/braille_review_routed.kicad_pcb")],
                   stdout=log, stderr=subprocess.STDOUT, check=True)
print("Exported board-only STEP; the assembly previews use labelled VRML envelopes.")
