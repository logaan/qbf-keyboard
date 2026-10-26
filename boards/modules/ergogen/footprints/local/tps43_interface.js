// Azoteq TPS43 (Toucan2) mechanical envelope and ABSTRACT breakout interface.
// NOT the manufacturer's FPC connector or pinout. Use an appropriate adapter
// and verify voltage, connector orientation and wiring before manufacturing.
module.exports = {
  params: {
    designator: 'TP', side: 'F', VCC: {type: 'net', value: '3V3'},
    GND: {type: 'net', value: 'GND'}, SDA: {type: 'net', value: 'TP_SDA'},
    SCL: {type: 'net', value: 'TP_SCL'}, RDY: {type: 'net', value: 'TP_RDY'},
    RST: {type: 'net', value: 'TP_RST'},
  },
  body: p => `
  (footprint "local:TPS43_abstract_interface" (layer "${p.side}.Cu") ${p.at}
    (property "Reference" "${p.ref}" (at 0 -24 ${p.r}) (layer "${p.side}.SilkS")
      (effects (font (size 1 1) (thickness 0.15))))
    (fp_text user "TPS43 43mm - ADAPTER REQUIRED" (at 0 0 ${p.r})
      (layer "${p.side}.Fab") (effects (font (size 1 1) (thickness 0.15))))
    (fp_rect (start -21.5 -21.5) (end 21.5 21.5) (stroke (width 0.15) (type default))
      (fill none) (layer "${p.side}.Fab"))
    ${[['VCC',p.VCC],['GND',p.GND],['SDA',p.SDA],['SCL',p.SCL],['RDY',p.RDY],['RST',p.RST]].map(([label,net],i) => `
    (pad "${i+1}" smd rect (at ${-6.35+i*2.54} 24 ${p.r}) (size 1.5 2)
      (layers "${p.side}.Cu" "${p.side}.Paste" "${p.side}.Mask") ${net.str})
    (fp_text user "${label}" (at ${-6.35+i*2.54} 27 ${p.r}) (layer "${p.side}.Fab")
      (effects (font (size 0.6 0.6) (thickness 0.1))))`).join('')}
  )`
};
