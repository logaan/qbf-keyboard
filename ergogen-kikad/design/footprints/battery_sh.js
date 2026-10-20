module.exports = {
  params: {designator: 'J', positive: {type: 'net', value: 'BAT_POS'}, negative: {type: 'net', value: 'GND'}},
  body: p => `(module JST_SH_SM02B_SRSS_TB_Horizontal (layer F.Cu)
    ${p.at}
    (attr smd)
    (fp_text reference "${p.ref}" (at 0 0) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
    (fp_text value "JST-SH 2-pin horizontal" (at 0 0) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
    (fp_line (start -2 -1.675) (end 2 -1.675) (layer F.Fab) (width 0.12))
    (fp_line (start 2 -1.675) (end 2 2.575) (layer F.Fab) (width 0.12))
    (fp_line (start 2 2.575) (end -2 2.575) (layer F.Fab) (width 0.12))
    (fp_line (start -2 2.575) (end -2 -1.675) (layer F.Fab) (width 0.12))
    (fp_line (start -3 6.325) (end 3 6.325) (layer Cmts.User) (width 0.12))
    (fp_line (start 3 6.325) (end 3 -1.675) (layer Cmts.User) (width 0.12))
    (fp_line (start 3 -1.675) (end -3 -1.675) (layer Cmts.User) (width 0.12))
    (fp_line (start -3 -1.675) (end -3 6.325) (layer Cmts.User) (width 0.12))
    (fp_text user "JST-SH ALLOWANCE" (at 0 4 90) (layer Cmts.User) (effects (font (size 0.65 0.65) (thickness 0.1))))
    (pad 1 smd roundrect (at -0.5 -2 ${p.r}) (size 0.6 1.55) (layers F.Cu F.Mask F.Paste) (roundrect_rratio 0.25) ${p.positive})
    (pad 2 smd roundrect (at 0.5 -2 ${p.r}) (size 0.6 1.55) (layers F.Cu F.Mask F.Paste) (roundrect_rratio 0.25) ${p.negative})
    (pad MP smd roundrect (at -1.8 1.875 ${p.r}) (size 1.2 1.8) (layers F.Cu F.Mask F.Paste) (roundrect_rratio 0.208333))
    (pad MP smd roundrect (at 1.8 1.875 ${p.r}) (size 1.2 1.8) (layers F.Cu F.Mask F.Paste) (roundrect_rratio 0.208333))
  )`
};
