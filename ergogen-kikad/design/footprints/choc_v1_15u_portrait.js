module.exports = {
  params: {
    designator: 'S',
    from: undefined,
    to: undefined,
    label: '',
    label_offset: 0,
    cap_length: 26.5
  },
  body: p => `
    (module PG1350_${p.cap_length == 17.5 ? '1U' : '1_5U'} (layer F.Cu)
      ${p.at}
      (fp_text reference "${p.ref}" (at 0 0) (layer F.SilkS) ${p.ref_hide}
        (effects (font (size 1 1) (thickness 0.15))))
      (fp_text value "Choc v1 ${p.cap_length == 17.5 ? '1U' : '1.5U'}" (at 0 0) (layer F.Fab) hide
        (effects (font (size 1 1) (thickness 0.15))))
      (fp_text user "${p.label}" (at ${p.label_offset} 0) (layer F.SilkS)
        (effects (font (size 1 1) (thickness 0.15))))
      (fp_line (start ${-p.cap_length / 2} -8.25) (end ${p.cap_length / 2} -8.25) (layer Dwgs.User) (width 0.15))
      (fp_line (start ${p.cap_length / 2} -8.25) (end ${p.cap_length / 2} 8.25) (layer Dwgs.User) (width 0.15))
      (fp_line (start ${p.cap_length / 2} 8.25) (end ${-p.cap_length / 2} 8.25) (layer Dwgs.User) (width 0.15))
      (fp_line (start ${-p.cap_length / 2} 8.25) (end ${-p.cap_length / 2} -8.25) (layer Dwgs.User) (width 0.15))
      (fp_line (start -7 -7) (end 7 -7) (layer F.Fab) (width 0.12))
      (fp_line (start 7 -7) (end 7 7) (layer F.Fab) (width 0.12))
      (fp_line (start 7 7) (end -7 7) (layer F.Fab) (width 0.12))
      (fp_line (start -7 7) (end -7 -7) (layer F.Fab) (width 0.12))
      (pad "" np_thru_hole circle (at 0 0) (size 3.429 3.429) (drill 3.429) (layers *.Cu *.Mask))
      (pad "" np_thru_hole circle (at 5.5 0) (size 1.7018 1.7018) (drill 1.7018) (layers *.Cu *.Mask))
      (pad "" np_thru_hole circle (at -5.5 0) (size 1.7018 1.7018) (drill 1.7018) (layers *.Cu *.Mask))
      (pad 1 thru_hole circle (at 5 -3.8) (size 2.4 2.4) (drill 1.6) (layers *.Cu *.Mask) ${p.from})
      (pad 2 thru_hole circle (at 0 -5.9) (size 2.4 2.4) (drill 1.6) (layers *.Cu *.Mask) ${p.to})
    )`
};
