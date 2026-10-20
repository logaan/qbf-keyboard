module.exports = {
  params: {designator: 'WELL', length: 58.1, width: 11.1, corner: 0.5},
  body: p => {
    const x = p.length / 2, y = p.width / 2, r = p.corner;
    const points = [[-x + r, -y], [x - r, -y], [x, -y + r], [x, y - r],
      [x - r, y], [-x + r, y], [-x, y - r], [-x, -y + r]];
    const edges = points.map((start, i) => {
      const end = points[(i + 1) % points.length];
      return `(fp_line (start ${start.join(' ')}) (end ${end.join(' ')}) (layer Edge.Cuts) (width 0.05))`;
    }).join('\n');
    return `(module Battery_Well (layer F.Cu)
      ${p.at}
      (fp_text reference "${p.ref}" (at 0 0) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
      (fp_text value "Battery well ${p.length}x${p.width}" (at 0 0) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
      ${edges}
    )`;
  }
};
