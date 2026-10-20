module.exports = {
  params: {designator: 'BAT', model: '301055', length: 57.5, width: 10.5, thickness: 3.5, capacity: 220, bottom_z: -1.4},
  body: p => `(module Protected_${p.model}_Battery_Envelope (layer F.Cu)
    ${p.at}
    (fp_text reference "${p.ref}" (at 0 0) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
    (fp_text value "${p.model} ${p.capacity}mAh max ${p.length}x${p.width}x${p.thickness} z=${p.bottom_z}" (at 0 0) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
    (fp_text user "${p.model} ${p.capacity}mAh" (at 0 -1) (layer Cmts.User) (effects (font (size 1.2 1.2) (thickness 0.15))))
    (fp_text user "${p.length} x ${p.width} x ${p.thickness} MAX" (at 0 1.5) (layer Cmts.User) (effects (font (size 0.9 0.9) (thickness 0.13))))
    (fp_line (start ${-p.length / 2} ${-p.width / 2}) (end ${p.length / 2} ${-p.width / 2}) (layer Cmts.User) (width 0.12))
    (fp_line (start ${p.length / 2} ${-p.width / 2}) (end ${p.length / 2} ${p.width / 2}) (layer Cmts.User) (width 0.12))
    (fp_line (start ${p.length / 2} ${p.width / 2}) (end ${-p.length / 2} ${p.width / 2}) (layer Cmts.User) (width 0.12))
    (fp_line (start ${-p.length / 2} ${p.width / 2}) (end ${-p.length / 2} ${-p.width / 2}) (layer Cmts.User) (width 0.12))
  )`
};
