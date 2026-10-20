const names = ['D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10', '3V3', 'GND', 'VBUS'];
const parameters = Object.fromEntries(names.map(name => [name, {type: 'net', value: name}]));

module.exports = {
  params: {designator: 'MCU', ...parameters},
  body: p => {
    const contacts = names.map((name, index) => {
      const upper = index < 7;
      const x = upper ? 7.62 - 2.54 * index : -7.62 + 2.54 * (index - 7);
      const y = upper ? -9.8 : 9.8;
      return `(pad ${index + 1} smd roundrect (at ${x.toFixed(2)} ${y} ${p.r}) (size 0.8 1.2) (layers F.Cu F.Mask) (roundrect_rratio 0.125) ${p[name]})`;
    });
    return `(module XIAO_nRF52840_Plus_Coplanar_Edge_Solder (layer F.Cu)
      ${p.at}
      (attr smd)
      (fp_text reference "${p.ref}" (at 0 0) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
      (fp_text value "XIAO nRF52840 Plus edge-soldered" (at 0 0) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
      (fp_text user "XIAO nRF52840 Plus" (at 0 -2) (layer Cmts.User) (effects (font (size 0.9 0.9) (thickness 0.12))))
      (fp_text user "USB >" (at 6 3) (layer Cmts.User) (effects (font (size 0.8 0.8) (thickness 0.1))))
      (fp_line (start -10.5 -8.9) (end 10.5 -8.9) (layer F.Fab) (width 0.12))
      (fp_line (start 10.5 -8.9) (end 10.5 8.9) (layer F.Fab) (width 0.12))
      (fp_line (start 10.5 8.9) (end -10.5 8.9) (layer F.Fab) (width 0.12))
      (fp_line (start -10.5 8.9) (end -10.5 -8.9) (layer F.Fab) (width 0.12))
      (fp_line (start 10.5 -4.5) (end 12 -4.5) (layer F.Fab) (width 0.12))
      (fp_line (start 12 -4.5) (end 12 4.5) (layer F.Fab) (width 0.12))
      (fp_line (start 12 4.5) (end 10.5 4.5) (layer F.Fab) (width 0.12))
      (fp_circle (center 8.57572 -5.7214) (end 9.02572 -5.7214) (layer F.Fab) (width 0.12))
      ${contacts.join('\n')}
    )`;
  }
};
