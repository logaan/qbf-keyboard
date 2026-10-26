module.exports = {
  params: {designator: 'RST', reset: {type: 'net', value: 'RST'}, GND: {type: 'net', value: 'GND'}},
  body: p => `(module SW_PUSH_6mm_H4_3mm (layer F.Cu)
    ${p.at}
    (fp_text reference "${p.ref}" (at 0 0) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
    (fp_text value "6mm top-actuated tactile" (at 0 0) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
    (fp_line (start -3 -3) (end 3 -3) (layer F.Fab) (width 0.12))
    (fp_line (start 3 -3) (end 3 3) (layer F.Fab) (width 0.12))
    (fp_line (start 3 3) (end -3 3) (layer F.Fab) (width 0.12))
    (fp_line (start -3 3) (end -3 -3) (layer F.Fab) (width 0.12))
    (pad 1 thru_hole circle (at -3.25 -2.25) (size 2 2) (drill 1.1) (layers *.Cu *.Mask) ${p.reset})
    (pad 1 thru_hole circle (at 3.25 -2.25) (size 2 2) (drill 1.1) (layers *.Cu *.Mask) ${p.reset})
    (pad 2 thru_hole circle (at -3.25 2.25) (size 2 2) (drill 1.1) (layers *.Cu *.Mask) ${p.GND})
    (pad 2 thru_hole circle (at 3.25 2.25) (size 2 2) (drill 1.1) (layers *.Cu *.Mask) ${p.GND})
  )`
};
