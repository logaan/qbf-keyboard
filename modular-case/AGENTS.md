# Modular case

1. This is the active case for the recessed XIAO board. The older `bumper-case/` and `mechanical/` directories are historical.
2. Work sequentially after the reviewed electronics and firmware stages. Read `ergogen-kikad/generated/assembly-contract.json`; never silently bypass stale source hashes.
3. Edit `build.py` and `parameters.json`, then run `./scripts/generate-mechanical.sh`. Keep valid single solids, closed meshes, pre-oriented print STL files, native FreeCAD and STEP outputs, validation and source geometry together. Do not add code comments. Commit as work progresses.
4. Keep four mounts, 2 mm rim walls, 0.25 mm cap edge clearance, full key travel, battery roof and all operational clearances. The controller, battery, boards and switches are fixed inputs.
5. Both halves must function independently and join flat with controllers inward. Covers and the bridge must be removable without tools. Do not introduce a hinge or require paired use. Assembly screws are permitted for initial installation.
6. Keep 3D assignments in `scripts/attach_models.py`. Run `./modular-case/render.sh`, then `./modular-case/present.sh`. Inspect assembled, cap-free, joined, protected and print views. Cap-free inspection may hide only the ten keycaps; retain every other component.
7. Native render preparation must not modify production boards. Document clearances separately from untested physical loads, elastic performance and printer tolerance. Do not claim prototypes or slicing checks that have not happened.
8. Update the guide, dimension drawing, print bundle and validation when geometry or hardware changes. Use case-specific M2 hardware; the electronics-only fastener reference is different.
