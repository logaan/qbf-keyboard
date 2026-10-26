module.exports = {
  params: {designator: 'J', positive: {type: 'net', value: 'BAT_POS'}, negative: {type: 'net', value: 'GND'}},
  body: p => `(module JST_PH_S2B_PH_K_Horizontal (layer F.Cu)
    ${p.at}
    (fp_text reference "${p.ref}" (at 0 0) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
    (fp_text value "JST-PH S2B-PH-K-S" (at 0 0) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
    (fp_line (start -2.95 -1.35) (end 2.95 -1.35) (layer F.Fab) (width 0.12))
    (fp_line (start 2.95 -1.35) (end 2.95 6.25) (layer F.Fab) (width 0.12))
    (fp_line (start 2.95 6.25) (end -2.95 6.25) (layer F.Fab) (width 0.12))
    (fp_line (start -2.95 6.25) (end -2.95 -1.35) (layer F.Fab) (width 0.12))
    (fp_line (start -2.95 6.25) (end -2.95 12.25) (layer Cmts.User) (width 0.12))
    (fp_line (start -2.95 12.25) (end 2.95 12.25) (layer Cmts.User) (width 0.12))
    (fp_line (start 2.95 12.25) (end 2.95 6.25) (layer Cmts.User) (width 0.12))
    (fp_text user "JST-PH" (at 0 3 0) (layer Cmts.User) (effects (font (size 0.7 0.7) (thickness 0.12))))
    (fp_text user "+" (at -1 3) (layer F.SilkS) (effects (font (size 1 1) (thickness 0.15))))
    (fp_text user "-" (at 1 3) (layer F.SilkS) (effects (font (size 1 1) (thickness 0.15))))
    (pad 1 thru_hole oval (at -1 0 ${p.r}) (size 1.2 1.75) (drill 0.75) (layers *.Cu *.Mask) ${p.positive})
    (pad 2 thru_hole oval (at 1 0 ${p.r}) (size 1.2 1.75) (drill 0.75) (layers *.Cu *.Mask) ${p.negative})
  )`
};
