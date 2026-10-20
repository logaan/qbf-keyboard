module.exports = {
  params: {designator: 'BAT', length: 57.5, width: 10.5, thickness: 3.5, capacity: 220},
  body: p => `(module Protected_301055_Battery_Envelope (layer F.Cu)
    ${p.at}
    (fp_text reference "${p.ref}" (at 0 0) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
    (fp_text value "301055 ${p.capacity}mAh max ${p.length}x${p.width}x${p.thickness}" (at 0 0) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
    (fp_text user "301055 220mAh" (at 0 -1) (layer Cmts.User) (effects (font (size 1.2 1.2) (thickness 0.15))))
    (fp_text user "57.5 x 10.5 x 3.5 MAX" (at 0 1.5) (layer Cmts.User) (effects (font (size 0.9 0.9) (thickness 0.13))))
    (fp_line (start ${-p.length / 2} ${-p.width / 2}) (end ${p.length / 2} ${-p.width / 2}) (layer Cmts.User) (width 0.12))
    (fp_line (start ${p.length / 2} ${-p.width / 2}) (end ${p.length / 2} ${p.width / 2}) (layer Cmts.User) (width 0.12))
    (fp_line (start ${p.length / 2} ${p.width / 2}) (end ${-p.length / 2} ${p.width / 2}) (layer Cmts.User) (width 0.12))
    (fp_line (start ${-p.length / 2} ${p.width / 2}) (end ${-p.length / 2} ${-p.width / 2}) (layer Cmts.User) (width 0.12))
  )`
};
