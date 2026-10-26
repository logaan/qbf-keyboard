module.exports = {
  params: {designator: 'PWR', source: {type: 'net', value: 'BAT_POS'}, output: {type: 'net', value: 'VBAT'}},
  body: p => {
    const tabs = [[-3.65, -0.78], [-3.65, 1.43], [3.65, -0.78], [3.65, 1.43]].map(([x, y]) =>
      `(pad "" smd rect (at ${x} ${y} ${p.r}) (size 1 0.8) (layers F.Cu F.Mask F.Paste))`).join('\n');
    const pegs = [-1.5, 1.5].map(x =>
      `(pad "" np_thru_hole circle (at ${x} 0.33) (size 0.9 0.9) (drill 0.9) (layers *.Cu *.Mask))`).join('\n');
    return `(module CK_PCM12SMTR (layer F.Cu)
      ${p.at}
      (attr smd)
      (fp_text reference "${p.ref}" (at 0 0) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
      (fp_text value "PCM12SMTR side power" (at 0 0) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
      (fp_line (start -3.35 -1) (end 3.35 -1) (layer F.Fab) (width 0.12))
      (fp_line (start 3.35 -1) (end 3.35 1.6) (layer F.Fab) (width 0.12))
      (fp_line (start 3.35 1.6) (end -3.35 1.6) (layer F.Fab) (width 0.12))
      (fp_line (start -3.35 1.6) (end -3.35 -1) (layer F.Fab) (width 0.12))
      (fp_line (start -1.6 1.6) (end -1.6 3.15) (layer F.Fab) (width 0.12))
      (fp_line (start -1.6 3.15) (end -0.1 3.15) (layer F.Fab) (width 0.12))
      (fp_line (start -0.1 3.15) (end -0.1 1.6) (layer F.Fab) (width 0.12))
      (fp_line (start -4.4 -2.45) (end 4.4 -2.45) (layer F.CrtYd) (width 0.05))
      (fp_line (start 4.4 -2.45) (end 4.4 2.1) (layer F.CrtYd) (width 0.05))
      (fp_line (start 4.4 2.1) (end -4.4 2.1) (layer F.CrtYd) (width 0.05))
      (fp_line (start -4.4 2.1) (end -4.4 -2.45) (layer F.CrtYd) (width 0.05))
      (pad 1 smd rect (at -2.25 -1.43 ${p.r}) (size 0.7 1.5) (layers F.Cu F.Mask F.Paste))
      (pad 2 smd rect (at 0.75 -1.43 ${p.r}) (size 0.7 1.5) (layers F.Cu F.Mask F.Paste) ${p.output})
      (pad 3 smd rect (at 2.25 -1.43 ${p.r}) (size 0.7 1.5) (layers F.Cu F.Mask F.Paste) ${p.source})
      ${tabs}
      ${pegs}
    )`;
  }
};
