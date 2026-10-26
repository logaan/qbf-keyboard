const upstream = module.exports;
module.exports = {
  ...upstream,
  body: p => {
    if (p.reversible || p.include_extra_pins) {
      throw new Error('Extended battery headers require single-side, no extra GPIO pads');
    }
    const inverted = (p.side === 'B' && !p.reverse_mount) || (p.side === 'F' && p.reverse_mount);
    const left = inverted ? p.RAW : p.GND;
    const right = inverted ? p.GND : p.RAW;
    const extension = `
      (pad "25" thru_hole circle (at -7.62 -15.24 ${p.r}) (size 1.7 1.7) (drill 1) (layers "*.Cu" "*.Mask") ${left.str})
      (pad "26" thru_hole circle (at 7.62 -15.24 ${p.r}) (size 1.7 1.7) (drill 1) (layers "*.Cu" "*.Mask") ${right.str})
    `;
    return upstream.body(p).replace(/\)\s*$/, extension + '\n)');
  }
};
