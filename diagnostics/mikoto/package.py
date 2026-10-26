import hashlib
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"


def main():
    application = ROOT / "firmware/supermini"
    runtime = DIST / "supermini-circuitpython-10.3.1.uf2"
    with zipfile.ZipFile(DIST / "supermini-install.zip", "w", zipfile.ZIP_DEFLATED) as bundle:
        bundle.write(runtime, runtime.name)
        for name in ("boot.py", "code.py", "fixture.py"):
            bundle.write(application / name, "CIRCUITPY/" + name)
        for name in ("BUILD.json", "west-frozen.yml"):
            bundle.write(DIST / name, name)
        for path in sorted((DIST / "LICENSES").iterdir()):
            if path.is_file():
                bundle.write(path, "LICENSES/" + path.name)
    paths = sorted([*DIST.glob("*.uf2"), DIST / "supermini-install.zip"])
    (DIST / "SHA256SUMS").write_text("".join(
        hashlib.sha256(path.read_bytes()).hexdigest() + "  " + path.name + "\n"
        for path in paths))


if __name__ == "__main__":
    main()
