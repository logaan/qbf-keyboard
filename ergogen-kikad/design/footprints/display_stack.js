const signals = ['LCD_CLK', 'LCD_SI', 'LCD_CS', 'LCD_COM', 'LCD_EN', '3V3', '', 'GND'];
const nets = Object.fromEntries(signals.filter(Boolean).map(name => [name, {type: 'net', value: name}]));
const line = (x1, y1, x2, y2, layer) => `(fp_line (start ${x1} ${y1}) (end ${x2} ${y2}) (layer ${layer}) (width 0.12))`;
const rectangle = (x, y, w, h, layer) => [line(x, y, x + w, y, layer), line(x + w, y, x + w, y + h, layer), line(x + w, y + h, x, y + h, layer), line(x, y + h, x, y, layer)].join('\n');

module.exports = {
  params: {designator: 'LCD', adapter: false, ...nets},
  body: p => {
    const pads = signals.map((net, index) => `(pad ${index + 1} thru_hole circle (at 11.35 ${((index - 3.5) * 1.27).toFixed(3)}) (size 0.9 0.9) (drill 0.5) (layers *.Cu *.Mask) ${net ? p[net] : ''})`);
    if (p.adapter) {
      for (let index = 0; index < 8; index++) {
        const net = signals[index];
        pads.push(`(pad ${index + 9} smd rect (at 4 ${((index - 3.5) * 0.5).toFixed(3)}) (size 1.5 0.3) (layers B.Cu B.Mask B.Paste) ${net ? p[net] : ''})`);
      }
      pads.push(`(pad 17 smd rect (at -2 0) (size 1.2 1.4) (layers B.Cu B.Mask B.Paste) ${p['3V3']})`);
      pads.push(`(pad 19 smd rect (at -2 -3) (size 1.2 1.4) (layers B.Cu B.Mask B.Paste) ${p.LCD_EN})`);
      pads.push(`(pad 20 smd rect (at -4 -3) (size 1.2 1.4) (layers B.Cu B.Mask B.Paste) ${p.GND})`);
      pads.push(`(pad 18 smd rect (at -4 0) (size 1.2 1.4) (layers B.Cu B.Mask B.Paste) ${p.GND})`);
    }
    return `(module JDI_LPM009M360A_Stack (layer F.Cu)
      ${p.at}
      (fp_text reference "${p.ref}" (at 0 0) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
      (fp_text value "JDI LPM009M360A" (at 0 0) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
      ${rectangle(-12.75, -9, 25.5, 18, 'Cmts.User')}
      ${rectangle(-12.005, -6.2275, 24.01, 12.455, 'Cmts.User')}
      ${rectangle(-10.605, -4.8276, 19.3104, 9.6552, 'Cmts.User')}
      ${pads.join('\n')}
    )`;
  }
};
