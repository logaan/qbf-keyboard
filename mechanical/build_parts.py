"""Generate the reversible two-board carrier and its four printed edge bumpers.

Uses the OpenCascade Python binding bundled with FreeCAD.  Dimensions are mm.
The companion FreeCAD macro rebuilds the same solids in a native document.
"""

from pathlib import Path

from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from OCC.Core.BRepCheck import BRepCheck_Analyzer
from OCC.Core.BRepGProp import brepgprop
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCC.Core.GProp import GProp_GProps
from OCC.Core.STEPControl import STEPControl_AsIs, STEPControl_Writer
from OCC.Core.StlAPI import StlAPI_Writer
from OCC.Core.gp import gp_Ax2, gp_Dir, gp_Pnt


OUT = Path(__file__).resolve().parent / "generated"
BOARD_W = 73.65
BOARD_H = 60.5
BOARD_GAP = 4.0
HOLE_X = (3.5, 70.15)
HOLE_Y = (2.75, 57.75)
RAIL_W = 9.0
RAIL_OVERHANG = 2.5
RAIL_THICKNESS = 4.0
PEG_DIAMETER = 2.0  # locates in the board's 2.2 mm M2 holes
PEG_HEIGHT = 1.4    # stays below the upper face of a 1.6 mm board
CASE_FLOOR = 2.5
SLOT_BOTTOM = 17.0
SLOT_TOP = 21.5
CASE_TOP = 22.2


def box(x, y, z, dx, dy, dz):
    return BRepPrimAPI_MakeBox(gp_Pnt(x, y, z), dx, dy, dz).Shape()


def cylinder(x, y, z, radius, height):
    return BRepPrimAPI_MakeCylinder(
        gp_Ax2(gp_Pnt(x, y, z), gp_Dir(0, 0, 1)), radius, height
    ).Shape()


def fuse(a, b):
    operation = BRepAlgoAPI_Fuse(a, b)
    operation.Build()
    if not operation.IsDone():
        raise RuntimeError("CAD fuse failed")
    return operation.Shape()


def cut(a, b):
    operation = BRepAlgoAPI_Cut(a, b)
    operation.Build()
    if not operation.IsDone():
        raise RuntimeError("CAD cut failed")
    return operation.Shape()


def rail(upper):
    y0 = BOARD_H - 6.5 if upper else -RAIL_OVERHANG
    shape = box(0, y0, 0, BOARD_W, RAIL_W, RAIL_THICKNESS)
    hole_y = HOLE_Y[1 if upper else 0]
    for x in HOLE_X:
        shape = fuse(shape, cylinder(x, hole_y, RAIL_THICKNESS,
                                     PEG_DIAMETER / 2, PEG_HEIGHT))
    outer_y = BOARD_H + RAIL_OVERHANG if upper else -RAIL_OVERHANG
    for x in (6.0, BOARD_W - 6.0):
        if upper:
            notch = box(x - 1.1, outer_y - 0.85, -0.1, 2.2, 0.95, 4.2)
        else:
            notch = box(x - 1.1, outer_y - 0.1, -0.1, 2.2, 0.95, 4.2)
        shape = cut(shape, notch)
    return shape


def case():
    length = 2 * BOARD_W + BOARD_GAP
    shape = box(-3, -5, 0, length + 6, BOARD_H + 10, CASE_FLOOR)
    for y in (-5, BOARD_H + 0.4):
        shape = fuse(shape, box(-3, y, CASE_FLOOR,
                                length + 6, 4.6, CASE_TOP - CASE_FLOOR))
    # Each groove opens at the outward end and stops in the middle web.
    for x0, x1 in ((-3.1, BOARD_W + 0.2),
                   (BOARD_W + BOARD_GAP - 0.2, length + 3.1)):
        for y0 in (-3.0, BOARD_H + 0.4):
            shape = cut(shape, box(x0, y0, SLOT_BOTTOM,
                                   x1 - x0, 2.6, SLOT_TOP - SLOT_BOTTOM))
    # The web separates the bays but stays below protected keycaps.
    shape = fuse(shape, box(BOARD_W + 1, 0, CASE_FLOOR,
                            BOARD_GAP - 2, BOARD_H, 5.5))
    # Small printed detents meet the two notches in each bumper rail.
    for x in (6.0, length - 6.0):
        for y in (-3.0, BOARD_H + 2.1):
            shape = fuse(shape, box(x - 0.35, y, 18.35, 0.7, 0.9, 1.8))
    return shape


def save(name, shape):
    if not BRepCheck_Analyzer(shape).IsValid():
        raise RuntimeError(f"Invalid solid: {name}")
    volume = GProp_GProps()
    brepgprop.VolumeProperties(shape, volume)
    if volume.Mass() <= 0:
        raise RuntimeError(f"Empty solid: {name}")
    step = STEPControl_Writer()
    step.Transfer(shape, STEPControl_AsIs)
    if step.Write(str(OUT / f"{name}.step")) != 1:
        raise RuntimeError(f"STEP export failed: {name}")
    BRepMesh_IncrementalMesh(shape, 0.12, False, 0.35, True)
    stl = StlAPI_Writer()
    stl.SetASCIIMode(False)
    stl.Write(shape, str(OUT / f"{name}.stl"))
    print(f"{name}: {volume.Mass():.1f} mm^3")


def main():
    OUT.mkdir(exist_ok=True)
    save("bumper_lower", rail(False))
    save("bumper_upper", rail(True))
    save("two_board_case", case())


if __name__ == "__main__":
    main()
