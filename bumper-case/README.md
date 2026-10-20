# Two-part QBF bumper case

A new FreeCAD design for one populated QBF main PCB and its matching blank baseplate. The boards are each 1.6 mm thick and touch directly. The case stops at the baseplate underside; four 10 × 20 × 2 mm rubber feet remain below that plane. The earlier `mechanical/` carrier is a separate design.

The left piece forms the switch plate for t1–t4/b1–b4. The right piece carries t5/b5 and covers the nice!nano and nice!view, with an open display window, USB access, and access to the upward-facing power and reset controls. The right edge beside the thumb keys drops to the PCB ledge height. Six M2 screws enter from underneath both boards, with plain M2 hex nuts above the printed supports. The outer pair straddles the case seam and clamps both pieces. The printed holes have no threads.

## Design inputs

- Use the current KiCad board, component placements, and 3D models as the assembly reference.
- Outside walls: 1 mm. Nominal PCB-to-wall clearance: 0.2 mm.
- Choc v1 plate: 1.2 mm thick, top 2.2 mm above the main PCB top; 14 mm nominal switch aperture, with a small printing allowance.
- Check 3 mm downward key travel against the existing cap mesh and a conservative rectangular cap envelope.
- PETG is the initial material assumption. The specified 2 mm nozzle cannot conventionally resolve the requested 1 mm walls or 1.2 mm plate; use a suitably smaller nozzle for these exports or agree a revised design with the print provider. No silent change to the wall requirement is made.
- The current component models are approximations. No physical fit or durability test has been performed.

The switch datum and travel reference is the [Kailh PG1350 drawing and specification](https://cdn-shop.adafruit.com/product-files/5114/5114_CPG135001D03.pdf). The current model limitations are recorded in `../ergogen-kikad/design/models/README.md`.

All case sources, reference captures, verification reports, and generated outputs live in this folder. Rebuilding the case does not regenerate or modify the electronics or the existing carrier.
