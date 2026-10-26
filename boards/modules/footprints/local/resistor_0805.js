module.exports = {
  params: {designator: 'R', side: 'B', value: '4.7k', from: {type: 'net', value: '3V3'}, to: {type: 'net', value: 'SDA'}},
  body: p => `
    (footprint "R_0805_2012Metric" (layer "${p.side}.Cu") ${p.at}
      (property "Reference" "${p.ref}" (at 0 -1.5 ${p.r}) (layer "${p.side}.Fab")
        (effects (font (size 0.8 0.8) (thickness 0.12)) (justify mirror)))
      (property "Value" "${p.value}" (at 0 1.5 ${p.r}) (layer "${p.side}.Fab")
        (effects (font (size 0.8 0.8) (thickness 0.12)) (justify mirror)))
      (fp_rect (start -1.65 -0.95) (end 1.65 0.95) (stroke (width 0.05) (type default)) (fill none) (layer "${p.side}.CrtYd"))
      (pad "1" smd roundrect (at -0.9125 0 ${p.r}) (size 1.025 1.4) (layers "${p.side}.Cu" "${p.side}.Paste" "${p.side}.Mask") (roundrect_rratio 0.243902) ${p.from.str})
      (pad "2" smd roundrect (at 0.9125 0 ${p.r}) (size 1.025 1.4) (layers "${p.side}.Cu" "${p.side}.Paste" "${p.side}.Mask") (roundrect_rratio 0.243902) ${p.to.str})
    )`
};
