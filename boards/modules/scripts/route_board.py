"""Route the generated review PCB, import copper into KiCad, and report DRC.

Requires Java 25+, Freerouting 2.2.4, and KiCad 9 with its pcbnew module.
"""
import argparse
from pathlib import Path
import shutil
import subprocess

import pcbnew as pcb

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--jar", type=Path, default=ROOT / "tools/freerouting-2.2.4.jar")
bundled_java = ROOT / "tools/jdk-25.0.4.1+1-jre/bin/java"
parser.add_argument("--java", default=str(bundled_java) if bundled_java.is_file() else "java")
parser.add_argument("--import-only", action="store_true", help="Import the existing routing session without rerouting")
args = parser.parse_args()
if not args.import_only:
    if not args.jar.is_file():
        parser.error("Download Freerouting 2.2.4 and provide its JAR with --jar")
    with (ROOT / "kicad/routing.log").open("w") as log:
        subprocess.run([args.java, "-Xmx1200m", "-jar", str(args.jar),
                        "-de", str(ROOT / "kicad/braille_review.dsn"),
                        "-do", str(ROOT / "kicad/braille_review.ses"), "-mp", "5"],
                       cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
board = pcb.LoadBoard(str(ROOT / "kicad/braille_review_unrouted.kicad_pcb"))
if not pcb.ImportSpecctraSES(board, str(ROOT / "kicad/braille_review.ses")):
    raise RuntimeError("KiCad could not import the routing session")
pcb.SaveBoard(str(ROOT / "kicad/braille_review_routed.kicad_pcb"), board)
project = ROOT / "kicad/braille_review_unrouted.kicad_pro"
if project.is_file():
    shutil.copy2(project, ROOT / "kicad/braille_review_routed.kicad_pro")
for variant, report in [("unrouted", "drc-before-routing.json"), ("routed", "drc-routed.json")]:
    subprocess.run(["kicad-cli", "pcb", "drc", "--format", "json", "--severity-all",
                    "--output", str(ROOT / "kicad" / report),
                    str(ROOT / "kicad" / f"braille_review_{variant}.kicad_pcb")], check=True)
subprocess.run(["kicad-cli", "pcb", "drc", "--format", "report", "--severity-all",
                "--output", str(ROOT / "kicad/drc-routed.txt"),
                str(ROOT / "kicad/braille_review_routed.kicad_pcb")], check=True)
print("Imported real copper routing. Review the DRC reports before any fabrication.")
