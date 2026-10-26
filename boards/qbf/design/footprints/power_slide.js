module.exports = {
  params: {designator: 'PWR', source: {type: 'net', value: 'BAT_POS'}, output: {type: 'net', value: 'VBAT'}},
  body: p => `(module CK_OS102011MS2QN1 (layer F.Cu)
    ${p.at}
    (fp_text reference "${p.ref}" (at 0 0) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
    (fp_text value "OS102011MS2QN1" (at 0 0) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
    (fp_line (start -4.3 -2.15) (end 4.3 -2.15) (layer F.Fab) (width 0.12))
    (fp_line (start 4.3 -2.15) (end 4.3 2.15) (layer F.Fab) (width 0.12))
    (fp_line (start 4.3 2.15) (end -4.3 2.15) (layer F.Fab) (width 0.12))
    (fp_line (start -4.3 2.15) (end -4.3 -2.15) (layer F.Fab) (width 0.12))
    (pad 1 thru_hole rect (at -2 0 ${p.r}) (size 1.5 2.5) (drill 0.8) (layers *.Cu *.Mask) ${p.source})
    (pad 2 thru_hole oval (at 0 0 ${p.r}) (size 1.5 2.5) (drill 0.8) (layers *.Cu *.Mask) ${p.output})
    (pad 3 thru_hole oval (at 2 0 ${p.r}) (size 1.5 2.5) (drill 0.8) (layers *.Cu *.Mask))
    (pad "" thru_hole oval (at -4.1 0 ${p.r}) (size 2.2 3.5) (drill 1.5) (layers *.Cu *.Mask) )
    (pad "" thru_hole oval (at 4.1 0 ${p.r}) (size 2.2 3.5) (drill 1.5) (layers *.Cu *.Mask) )
  )`
};
