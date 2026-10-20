const left = ['P1', 'P0', 'GND', 'GND', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9'];
const right = ['RAW', 'GND', 'RST', 'VCC', 'P21', 'P20', 'P19', 'P18', 'P15', 'P14', 'P16', 'P10'];
const wired = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10', 'P14', 'P15', 'P16', 'GND', 'VCC', 'RAW', 'RST'];
const nets = Object.fromEntries(wired.map(name => [name, {type: 'net', value: name}]));

module.exports = {
  params: {designator: 'MCU', ...nets},
  body: p => {
    const pads = [];
    for (let i = 0; i < 12; i++) {
      const y = (-13.97 + i * 2.54).toFixed(2);
      for (const [side, pins, number] of [[-1, left, i + 1], [1, right, 24 - i]]) {
        const net = p[pins[i]] || '';
        const label = pins[i] || (side === 1 && i === 0 ? 'RAW' : 'RST');
        pads.push(`(pad ${number} thru_hole circle (at ${side * 7.62} ${y}) (size 1.8 1.8) (drill 1) (layers *.Cu *.Mask) ${net})`);
        pads.push(`(fp_text user "${label}" (at ${side * 5.4} ${y}) (layer F.Fab) (effects (font (size 0.65 0.65) (thickness 0.1))))`);
      }
    }
    return `(module Nice_Nano_V2 (layer F.Cu)
      ${p.at}
      (fp_text reference "${p.ref}" (at 0 0) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
      (fp_text value "nice!nano v2" (at 0 0) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
      (fp_line (start -9.15 -18) (end 9.15 -18) (layer F.Fab) (width 0.12))
      (fp_line (start 9.15 -18) (end 9.15 18) (layer F.Fab) (width 0.12))
      (fp_line (start 9.15 18) (end -9.15 18) (layer F.Fab) (width 0.12))
      (fp_line (start -9.15 18) (end -9.15 -18) (layer F.Fab) (width 0.12))
      (fp_text user "USB" (at 0 -16) (layer F.Fab) (effects (font (size 1 1) (thickness 0.15))))
      ${pads.join('\n')}
    )`;
  }
};
