const signals = ['LCD_SI', 'LCD_CLK', '3V3', 'GND', 'LCD_CS'];
const nets = Object.fromEntries(signals.map(name => [name, {type: 'net', value: name}]));

module.exports = {
  params: {designator: 'LCD', ...nets},
  body: p => {
    const pads = signals.map((net, index) => `(pad ${index + 1} thru_hole ${index === 0 ? 'rect' : 'circle'} (at -16.7 ${((index - 2) * 2.54).toFixed(2)}) (size 1.8 1.8) (drill 1) (layers *.Cu *.Mask) ${p[net]})`);
    return `(module Nice_View_Socketed_Module (layer F.Cu)
      ${p.at}
      (fp_text reference "${p.ref}" (at -16.7 0) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
      (fp_text value "nice!view" (at 0 0) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
      (fp_text user "nice!view" (at 1 -2) (layer Cmts.User) (effects (font (size 1.1 1.1) (thickness 0.15))))
      (fp_text user "LCD1 SOCKET" (at -14.5 0 90) (layer Cmts.User) (effects (font (size 0.8 0.8) (thickness 0.12))))
      (fp_line (start -18 -7) (end 18 -7) (layer Cmts.User) (width 0.12))
      (fp_line (start 18 -7) (end 18 7) (layer Cmts.User) (width 0.12))
      (fp_line (start 18 7) (end -18 7) (layer Cmts.User) (width 0.12))
      (fp_line (start -18 7) (end -18 -7) (layer Cmts.User) (width 0.12))
      (fp_line (start -17.97 -6.35) (end -15.43 -6.35) (layer F.Fab) (width 0.12))
      (fp_line (start -15.43 -6.35) (end -15.43 6.35) (layer F.Fab) (width 0.12))
      (fp_line (start -15.43 6.35) (end -17.97 6.35) (layer F.Fab) (width 0.12))
      (fp_line (start -17.97 6.35) (end -17.97 -6.35) (layer F.Fab) (width 0.12))
      ${pads.join('\n')}
    )`;
  }
};
