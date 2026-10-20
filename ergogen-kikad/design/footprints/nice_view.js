const signals = ['LCD_SI', 'LCD_CLK', '3V3', 'GND', 'LCD_CS'];
const nets = Object.fromEntries(signals.map(name => [name, {type: 'net', value: name}]));

module.exports = {
  params: {designator: 'LCD', ...nets},
  body: p => {
    const pads = signals.map((net, index) => `(pad ${index + 1} thru_hole circle (at 12.3 ${(18.75 + (index - 2) * 2.54).toFixed(2)}) (size 1.8 1.8) (drill 1) (layers *.Cu *.Mask) ${p[net]})`);
    const modulePins = signals.map((net, index) => {
      const y = ((index - 2) * 2.54).toFixed(2);
      const endY = (18.75 + (index - 2) * 2.54).toFixed(2);
      const bendX = -14.5 + index * 0.6;
      const channelY = 8.7 + index * 0.45;
      const rightX = 10.4 + index * 0.3;
      return `(fp_circle (center -16.7 ${y}) (end -16.15 ${y}) (layer Cmts.User) (width 0.12))
        (fp_line (start -16.7 ${y}) (end ${bendX} ${y}) (layer Cmts.User) (width 0.08))
        (fp_line (start ${bendX} ${y}) (end ${bendX} ${channelY}) (layer Cmts.User) (width 0.08))
        (fp_line (start ${bendX} ${channelY}) (end ${rightX} ${channelY}) (layer Cmts.User) (width 0.08))
        (fp_line (start ${rightX} ${channelY}) (end ${rightX} ${endY}) (layer Cmts.User) (width 0.08))
        (fp_line (start ${rightX} ${endY}) (end 12.3 ${endY}) (layer Cmts.User) (width 0.08))`;
    });
    return `(module Nice_View_Wired_Module (layer F.Cu)
      ${p.at}
      (fp_text reference "${p.ref}" (at 12.3 26) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
      (fp_text value "nice!view" (at 0 0) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
      (fp_text user "nice!view" (at 1 -2) (layer Cmts.User) (effects (font (size 1.1 1.1) (thickness 0.15))))
      (fp_text user "5 INSULATED WIRES" (at 1 4.5) (layer Cmts.User) (effects (font (size 0.8 0.8) (thickness 0.12))))
      (fp_text user "LCD1" (at 14.5 18.75 90) (layer Cmts.User) (effects (font (size 0.8 0.8) (thickness 0.12))))
      (fp_line (start -18 -7) (end 18 -7) (layer Cmts.User) (width 0.12))
      (fp_line (start 18 -7) (end 18 7) (layer Cmts.User) (width 0.12))
      (fp_line (start 18 7) (end -18 7) (layer Cmts.User) (width 0.12))
      (fp_line (start -18 7) (end -18 -7) (layer Cmts.User) (width 0.12))
      ${modulePins.join('\n')}
      ${pads.join('\n')}
    )`;
  }
};
