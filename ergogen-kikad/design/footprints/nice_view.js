const signals = ['GND', '3V3', 'LCD_CLK', 'LCD_SI', 'LCD_CS'];
const nets = Object.fromEntries(signals.map(name => [name, {type: 'net', value: name}]));

module.exports = {
  params: {designator: 'LCD', ...nets},
  body: p => {
    const pads = signals.map((net, index) => `(pad ${index + 1} thru_hole circle (at 12.3 ${(18.75 + (index - 2) * 2.54).toFixed(2)}) (size 1.8 1.8) (drill 1) (layers *.Cu *.Mask) ${p[net]})`);
    return `(module Nice_View_Wired_Module (layer F.Cu)
      ${p.at}
      (fp_text reference "${p.ref}" (at 12.3 26) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
      (fp_text value "nice!view" (at 0 0) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
      (fp_line (start -18 -7) (end 18 -7) (layer Cmts.User) (width 0.12))
      (fp_line (start 18 -7) (end 18 7) (layer Cmts.User) (width 0.12))
      (fp_line (start 18 7) (end -18 7) (layer Cmts.User) (width 0.12))
      (fp_line (start -18 7) (end -18 -7) (layer Cmts.User) (width 0.12))
      ${pads.join('\n')}
    )`;
  }
};
