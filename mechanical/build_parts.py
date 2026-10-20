import FreeCAD as App
import MeshPart

from pathlib import Path
import runpy


ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'generated'


def main():
    OUT.mkdir(exist_ok=True)
    result = runpy.run_path(str(ROOT / 'QBF_carrier.FCMacro'))
    document = result['doc']
    names = {'BumperLower': 'bumper_lower', 'BumperUpper': 'bumper_upper',
             'Case': 'two_board_case'}
    for name, filename in names.items():
        shape = document.getObject(name).Shape
        if not shape.isValid() or len(shape.Solids) != 1 or shape.Volume <= 0:
            raise RuntimeError(f'Invalid solid: {name}')
        step_path = OUT / f'{filename}.step'
        shape.exportStep(str(step_path))
        step_path.write_text('\n'.join(line.rstrip() for line in step_path.read_text().splitlines()) + '\n')
        mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.05,
                                     AngularDeflection=0.15, Relative=False)
        if not mesh.isSolid():
            raise RuntimeError(f'Non-solid mesh: {name}')
        mesh.write(str(OUT / f'{filename}.stl'))
        print(f'Generated {filename}: valid solid, {mesh.CountFacets} facets')
    App.closeDocument(document.Name)


if __name__ == '__main__':
    main()
