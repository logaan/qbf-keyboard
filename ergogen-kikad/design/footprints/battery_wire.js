module.exports = {
  params: {designator: 'BW', positive: {type: 'net', value: 'VBAT'}},
  body: p => `(module XIAO_Underside_BAT_Wire_Landing (layer B.Cu)
    ${p.at}
    (attr smd)
    (fp_text reference "${p.ref}" (at 0 0) (layer B.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
    (fp_text value "Insulated lead to XIAO BAT+ underside" (at 0 0) (layer B.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
    (fp_text user "XIAO BAT+" (at -2 0 90) (layer B.Fab) (effects (font (size 0.7 0.7) (thickness 0.1)) (justify mirror)))
    (pad 1 smd roundrect (at 0 0 ${p.r}) (size 1.4 1.4) (layers B.Cu B.Mask) (roundrect_rratio 0.2) ${p.positive})
  )`
};
