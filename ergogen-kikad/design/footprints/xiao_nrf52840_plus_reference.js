module.exports = {
  params: {designator: 'MCU'},
  body: p => {
    const contactMarks = [-7.62, -5.08, -2.54, 0, 2.54, 5.08, 7.62].flatMap(x => [-1, 1].map(side =>
      `(fp_line (start ${x} ${side * 8.65}) (end ${x} ${side * 9.1}) (layer Dwgs.User) (width 0.5))`)).join('\n');
    return `(module XIAO_nRF52840_Plus_Placement_Only (layer F.Cu)
      ${p.at}
      (fp_text reference "${p.ref}" (at 0 0) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
      (fp_text value "XIAO Plus placement only; electrical mount deferred" (at 0 0) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
      (fp_text user "XIAO nRF52840 Plus" (at 0 -2) (layer Cmts.User) (effects (font (size 0.95 0.95) (thickness 0.13))))
      (fp_text user "MOUNT PADS DEFERRED" (at 0 0) (layer Cmts.User) (effects (font (size 0.7 0.7) (thickness 0.1))))
      (fp_text user "USB >" (at 6.6 3.2) (layer Cmts.User) (effects (font (size 0.8 0.8) (thickness 0.12))))
      (fp_line (start -10.5 -8.9) (end 10.5 -8.9) (layer F.Fab) (width 0.12))
      (fp_line (start 10.5 -8.9) (end 10.5 8.9) (layer F.Fab) (width 0.12))
      (fp_line (start 10.5 8.9) (end -10.5 8.9) (layer F.Fab) (width 0.12))
      (fp_line (start -10.5 8.9) (end -10.5 -8.9) (layer F.Fab) (width 0.12))
      (fp_line (start 10.5 -4.5) (end 12 -4.5) (layer F.Fab) (width 0.12))
      (fp_line (start 12 -4.5) (end 12 4.5) (layer F.Fab) (width 0.12))
      (fp_line (start 12 4.5) (end 10.5 4.5) (layer F.Fab) (width 0.12))
      (fp_circle (center 8.573 -5.721) (end 9.023 -5.721) (layer F.Fab) (width 0.12))
      ${contactMarks}
    )`;
  }
};
