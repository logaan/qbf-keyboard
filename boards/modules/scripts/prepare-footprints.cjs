// Preserve upstream geometry and notices; generate the two small local adapters.
const fs = require('fs');
const path = require('path');
const root = path.join(__dirname, '../ergogen/footprints');
fs.mkdirSync(path.join(root, 'local'), {recursive: true});
const read = name => fs.readFileSync(path.join(root, 'ceoloide', name), 'utf8');
const extension = `
// Local change: add the nice!nano v2's top B-/B+ row, one 2.54 mm step
// above the library's standard 12 rows. Verified against official v2 pinout.
// No extra GPIO pins; this is a non-reversible 2x13 socket footprint.
// Upstream license and attribution above apply to this derived footprint.
const originalBody = module.exports.body;
module.exports.body = p => {
  if (p.reversible || p.include_extra_pins) {
    throw new Error('Extended battery headers require single-side, no extra GPIO pads');
  }
  const inverted = (p.side === 'B' && !p.reverse_mount) ||
                   (p.side === 'F' && p.reverse_mount);
  const left = inverted ? p.RAW : p.GND;
  const right = inverted ? p.GND : p.RAW;
  const extension = \`
    (pad "25" thru_hole circle (at -7.62 -15.24 \${p.r}) (size 1.7 1.7) (drill 1) (layers "*.Cu" "*.Mask") \${left.str})
    (pad "26" thru_hole circle (at 7.62 -15.24 \${p.r}) (size 1.7 1.7) (drill 1) (layers "*.Cu" "*.Mask") \${right.str})
    (fp_text user "B- / B+ EXTENDED SOCKETS" (at 0 -15.24 \${p.r})
      (layer "Dwgs.User") (effects (font (size 0.6 0.6) (thickness 0.1))))
  \`;
  const source = originalBody(p);
  return source.replace(/\\)\\s*$/, extension + '\\n)');
};
`;
fs.writeFileSync(path.join(root, 'local/nice_nano_extended.js'), read('mcu_nice_nano.js') + extension);
// Upstream uses strings for these parameters; use numeric Ergogen expressions
// without altering its mounting-hole geometry.
fs.writeFileSync(path.join(root, 'local/mounting_hole_npth.js'), read('mounting_hole_npth.js') + '\nmodule.exports.params.hole_size = 2.2;\nmodule.exports.params.hole_drill = 2.2;\n');
console.log('Prepared library-based extended controller and mounting-hole adapters.');
