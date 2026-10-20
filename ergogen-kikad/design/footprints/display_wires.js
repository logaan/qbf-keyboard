const pins = ['LCD_CLK', 'LCD_SI', 'LCD_CS', 'LCD_COM', 'LCD_EN'];
const nets = Object.fromEntries(pins.map(name => [name, {type: 'net', value: name}]));
module.exports = {
  params: {designator: 'W', ...nets},
  body: p => `(module XIAO_Plus_Underside_Wires (layer F.Cu)
    ${p.at}
    (fp_text reference "${p.ref}" (at 0 0) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
    (fp_text value "Plus underside jumpers" (at 0 0) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
    ${pins.map((name, index) => `(pad ${index + 1} thru_hole circle (at 0 ${(index * 1.27).toFixed(3)}) (size 0.9 0.9) (drill 0.5) (layers *.Cu *.Mask) ${p[name]})`).join('\n')}
  )`
};
