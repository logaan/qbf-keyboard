module.exports = {
  params: {designator: 'J', positive: {type: 'net', value: 'BAT_POS'}, negative: {type: 'net', value: 'GND'}},
  body: p => `(module JST_PH_B2B_PH_K_Vertical (layer F.Cu)
    ${p.at}
    (fp_text reference "${p.ref}" (at 0 0) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
    (fp_text value "JST-PH B2B-PH-K-S" (at 0 0) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
    (fp_line (start -2.95 -1.7) (end 2.95 -1.7) (layer F.Fab) (width 0.12))
    (fp_line (start 2.95 -1.7) (end 2.95 2.8) (layer F.Fab) (width 0.12))
    (fp_line (start 2.95 2.8) (end -2.95 2.8) (layer F.Fab) (width 0.12))
    (fp_line (start -2.95 2.8) (end -2.95 -1.7) (layer F.Fab) (width 0.12))
    (fp_text user "+" (at -1 -3) (layer F.SilkS) (effects (font (size 1 1) (thickness 0.15))))
    (fp_text user "-" (at 1 -3) (layer F.SilkS) (effects (font (size 1 1) (thickness 0.15))))
    (pad 1 thru_hole oval (at -1 0) (size 1.2 1.75) (drill 0.75) (layers *.Cu *.Mask) ${p.positive})
    (pad 2 thru_hole oval (at 1 0) (size 1.2 1.75) (drill 0.75) (layers *.Cu *.Mask) ${p.negative})
  )`
};
