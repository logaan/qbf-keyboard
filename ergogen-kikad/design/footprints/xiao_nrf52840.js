// Seeed Studio XIAO nRF52840 mounted on two 1x7 2.54 mm socket strips.
// USB connector is at the top; view is from the PCB component side.
const left = ['D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6'];
const right = ['5V', 'GND', '3V3', 'D10', 'D9', 'D8', 'D7'];
const wired = [...left, 'D7', 'GND'];
const nets = Object.fromEntries(wired.map(name => [name, { type: 'net', value: name }]));

module.exports = {
  params: { designator: 'MCU', ...nets },
  body: p => {
    const pad = (n, x, y, net) =>
      `(pad ${n} thru_hole circle (at ${x} ${y}) (size 1.8 1.8) (drill 1.0) (layers *.Cu *.Mask) ${p[net] || ''})`;
    const label = (name, x, y) =>
      `(fp_text user "${name}" (at ${x} ${y}) (layer F.SilkS) (effects (font (size 0.8 0.8) (thickness 0.12))))`;
    const lines = [];
    for (let i = 0; i < 7; i++) {
      const y = Number((-7.62 + i * 2.54).toFixed(2));
      lines.push(pad(i + 1, -7.62, y, left[i]));
      lines.push(pad(14 - i, 7.62, y, right[i]));
      lines.push(label(left[i], -11.5, y));
      lines.push(label(right[i], 11.5, y));
    }
    return `
      (module Seeed_XIAO_nRF52840 (layer F.Cu)
        ${p.at}
        (fp_text reference "${p.ref}" (at 0 0) (layer F.SilkS) ${p.ref_hide}
          (effects (font (size 1 1) (thickness 0.15))))
        (fp_text value "XIAO nRF52840" (at 0 3.5) (layer F.Fab)
          (effects (font (size 1 1) (thickness 0.15))))
        (fp_line (start -8.9 -10.5) (end 8.9 -10.5) (layer F.Fab) (width 0.12))
        (fp_line (start 8.9 -10.5) (end 8.9 10.5) (layer F.Fab) (width 0.12))
        (fp_line (start 8.9 10.5) (end -8.9 10.5) (layer F.Fab) (width 0.12))
        (fp_line (start -8.9 10.5) (end -8.9 -10.5) (layer F.Fab) (width 0.12))
        ${label('USB', 0, -8)}
        ${lines.join('\n')}
      )`;
  }
};
