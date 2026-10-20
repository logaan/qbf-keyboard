module.exports = {
  params: {designator: 'BAT'},
  body: p => `(module Protected_301230_Battery_Envelope (layer F.Cu)
    ${p.at}
    (fp_text reference "${p.ref}" (at 0 0) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
    (fp_text value "301230 110mAh max 32.5x12.5x3.2" (at 0 0) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
    (fp_line (start -16.25 -6.25) (end 16.25 -6.25) (layer Cmts.User) (width 0.12))
    (fp_line (start 16.25 -6.25) (end 16.25 6.25) (layer Cmts.User) (width 0.12))
    (fp_line (start 16.25 6.25) (end -16.25 6.25) (layer Cmts.User) (width 0.12))
    (fp_line (start -16.25 6.25) (end -16.25 -6.25) (layer Cmts.User) (width 0.12))
  )`
};
