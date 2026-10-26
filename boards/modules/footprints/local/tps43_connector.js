module.exports = {
  params: {
    designator: 'TP', side: 'B', VCC: {type: 'net', value: '3V3'},
    GND: {type: 'net', value: 'GND'}, SDA: {type: 'net', value: 'TP_SDA'},
    SCL: {type: 'net', value: 'TP_SCL'}, RDY: {type: 'net', value: 'TP_RDY'},
    RST: {type: 'net', value: 'TP_RST'}
  },
  body: p => `
    (footprint "TPS43_Cable_Header_1x06_P2.54" (layer "${p.side}.Cu") ${p.at}
      (property "Reference" "${p.ref}" (at 0 -2.5 ${p.r}) (layer "${p.side}.Fab")
        (effects (font (size 1 1) (thickness 0.15)) (justify mirror)))
      (property "Value" "TPS43 cable adapter" (at 0 15 ${p.r}) (layer "${p.side}.Fab")
        (effects (font (size 1 1) (thickness 0.15)) (justify mirror)))
      (fp_rect (start -1.8 -1.8) (end 1.8 14.5) (stroke (width 0.05) (type default)) (fill none) (layer "${p.side}.CrtYd"))
      ${[p.RDY, p.RST, p.GND, p.VCC, p.SCL, p.SDA].map((net, i) => `
        (pad "${i + 1}" thru_hole ${i ? 'circle' : 'rect'} (at 0 ${i * 2.54} ${p.r})
          (size 1.7 1.7) (drill 1) (layers "*.Cu" "*.Mask") ${net.str})`).join('')}
    )`
};
