// Kailh Choc v1 (PG1350), through-hole, with a 1.5U cap outline.
// Rotate this footprint 90 degrees in config.yaml for portrait keycaps.
// The cap clearance uses the common MBK 1.5U size: 26.5 x 16.5 mm.
module.exports = {
  params: {
    designator: 'S',
    from: undefined,
    to: undefined
  },
  body: p => `
    (module PG1350_1_5U (layer F.Cu)
      ${p.at}
      (fp_text reference "${p.ref}" (at 0 0) (layer F.SilkS) ${p.ref_hide}
        (effects (font (size 1 1) (thickness 0.15))))
      (fp_text value "Choc v1 1.5U" (at 0 0) (layer F.Fab) hide
        (effects (font (size 1 1) (thickness 0.15))))
      (fp_line (start -13.25 -8.25) (end 13.25 -8.25) (layer Dwgs.User) (width 0.15))
      (fp_line (start 13.25 -8.25) (end 13.25 8.25) (layer Dwgs.User) (width 0.15))
      (fp_line (start 13.25 8.25) (end -13.25 8.25) (layer Dwgs.User) (width 0.15))
      (fp_line (start -13.25 8.25) (end -13.25 -8.25) (layer Dwgs.User) (width 0.15))
      (fp_line (start -7 -7) (end 7 -7) (layer F.Fab) (width 0.12))
      (fp_line (start 7 -7) (end 7 7) (layer F.Fab) (width 0.12))
      (fp_line (start 7 7) (end -7 7) (layer F.Fab) (width 0.12))
      (fp_line (start -7 7) (end -7 -7) (layer F.Fab) (width 0.12))
      (pad "" np_thru_hole circle (at 0 0) (size 3.429 3.429) (drill 3.429) (layers *.Cu *.Mask))
      (pad "" np_thru_hole circle (at 5.5 0) (size 1.7018 1.7018) (drill 1.7018) (layers *.Cu *.Mask))
      (pad "" np_thru_hole circle (at -5.5 0) (size 1.7018 1.7018) (drill 1.7018) (layers *.Cu *.Mask))
      (pad 1 thru_hole circle (at 5 -3.8) (size 2.032 2.032) (drill 1.27) (layers *.Cu *.Mask) ${p.from})
      (pad 2 thru_hole circle (at 0 -5.9) (size 2.032 2.032) (drill 1.27) (layers *.Cu *.Mask) ${p.to})
    )`
};
