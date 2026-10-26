"""Validate the review deliverables and record their measured dimensions.

Known placement clashes and remaining DRC findings are reported, not hidden.
Requires KiCad's pcbnew Python module.
"""
from collections import Counter
import json
from pathlib import Path

import pcbnew as pcb

ROOT = Path(__file__).resolve().parents[1]
geometry = json.loads((ROOT / "kicad/geometry.json").read_text())
board = pcb.LoadBoard(str(ROOT / "kicad/braille_review_routed.kicad_pcb"))
footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}
switches = [fp for fp in footprints.values()
            if fp.GetFPID().GetLibItemName() == "switch_choc_v1_v2"]
controller = footprints["MCU1"]
assert len(switches) == 12
assert len(list(controller.Pads())) == 26
assert len(list(board.GetTracks())) > 0

for item in geometry["footprints"]:
    fp = footprints[item["reference"]]
    x, y = item["position"]
    assert abs(pcb.ToMM(fp.GetPosition().x) - x) < 0.00001
    assert abs(pcb.ToMM(fp.GetPosition().y) - y) < 0.00001
    assert abs(fp.GetOrientationDegrees() - item["angle"]) < 0.00001

controller_pads = {pad.GetNumber(): pad for pad in controller.Pads()}
assert controller_pads["25"].GetNetname() == "GND"
assert controller_pads["26"].GetNetname() == "VBAT"
key_nets = set()
for fp in switches:
    nets = {pad.GetNetname() for pad in fp.Pads() if pad.GetNetname()}
    assert "GND" in nets and len(nets) == 2
    key_net = (nets - {"GND"}).pop()
    assert key_net not in key_nets
    key_nets.add(key_net)
    assert sum(p.GetNetname() == key_net for p in controller.Pads()) == 1

def nets(reference):
    return {p.GetNetname() for p in footprints[reference].Pads() if p.GetNetname()}

assert nets("JST1") == {"BAT_P", "GND"}
assert nets("PWR1") == {"BAT_P", "VBAT"}
assert nets("RST1") == {"GND", "RST"}
assert {"DISPLAY_CS", "DISPLAY_MOSI", "DISPLAY_SCK", "3V3", "GND"} == nets("DISP1")
for reference in ["MCU1", "DISP1", "PWR1", "RST1", "JST1"]:
    assert footprints[reference].GetLayer() == pcb.B_Cu

boundary = geometry["board"]
xmin, ymin = boundary["xmin"], boundary["ymin"]
xmax, ymax = xmin + boundary["width"], ymin + boundary["height"]
edge_points = []
for graphic in board.GetDrawings():
    if graphic.GetClass() == "PCB_SHAPE" and graphic.GetLayer() == pcb.Edge_Cuts:
        for point in [graphic.GetStart(), graphic.GetEnd()]:
            edge_points.append((pcb.ToMM(point.x), pcb.ToMM(point.y)))
assert abs(min(x for x, _ in edge_points) - xmin) < 0.00001
assert abs(max(x for x, _ in edge_points) - xmax) < 0.00001
assert abs(min(y for _, y in edge_points) - ymin) < 0.00001
assert abs(max(y for _, y in edge_points) - ymax) < 0.00001

# Measure physical drawing lines without adding their display stroke widths.
extent = [xmin, ymin, xmax, ymax]
usb = geometry["usb_envelope_from_library"]
assert usb["bottom"] <= ymin + 0.00001
extent[0] = min(extent[0], usb["left"])
extent[1] = min(extent[1], usb["top"])
extent[2] = max(extent[2], usb["right"])
extent[3] = max(extent[3], usb["bottom"])
for reference, layer in [("RST1", pcb.Dwgs_User), ("PWR1", pcb.B_Fab)]:
    for graphic in footprints[reference].GraphicalItems():
        if graphic.GetClass() == "PCB_SHAPE" and graphic.GetLayer() == layer:
            for point in [graphic.GetStart(), graphic.GetEnd()]:
                x, y = pcb.ToMM(point.x), pcb.ToMM(point.y)
                extent = [min(extent[0], x), min(extent[1], y),
                          max(extent[2], x), max(extent[3], y)]

drc = json.loads((ROOT / "kicad/drc-routed.json").read_text())
assert not any(v["type"] in {"shorting_items", "tracks_crossing"}
               for v in drc["violations"])
assembly = json.loads((ROOT / "models/assembly-parameters.json").read_text())
summary = {
    "status": "Review draft with accepted clashes and outstanding DRC findings",
    "pcb_mm": [boundary["width"], boundary["height"], 1.6],
    "acrylic_mm": [boundary["width"], boundary["height"], geometry["units"]["acrylic_thickness"]],
    "assembly_xy_including_usb_and_controls_mm": [round(extent[2] - extent[0], 4),
                                                  round(extent[3] - extent[1], 4)],
    "illustrated_assembly_height_mm": assembly["illustrated_height_mm"],
    "assembly_height_status": "Provisional envelopes; real keycaps, sockets, ring and stack need confirmation",
    "key_spacing_status": "Provisional 19.05 mm units; spoken reference board remains unidentified",
    "switches": len(switches),
    "independent_key_inputs": len(key_nets),
    "controller_socket_contacts": len(controller_pads),
    "track_and_via_items": len(list(board.GetTracks())),
    "accepted_header_clearances": len(geometry["accepted_header_clearances"]),
    "unconnected_items": drc["unconnected_items"],
    "drc_types": dict(Counter(v["type"] for v in drc["violations"])),
    "sources_match_routed_placements": True,
    "manufacturer_component_models": False,
}
(ROOT / "kicad/review-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print("Verified twelve independent keys, battery/power/reset nets, 26 controller contacts, and source/PCB agreement.")
print("PCB/acrylic:", summary["pcb_mm"][:2], "mm")
print("Assembly including USB and controls:", summary["assembly_xy_including_usb_and_controls_mm"], "mm")
print("Illustrated height:", summary["illustrated_assembly_height_mm"], "mm (provisional)")
print("Remaining unconnected items:", len(summary["unconnected_items"]))
print("DRC findings:", summary["drc_types"])
