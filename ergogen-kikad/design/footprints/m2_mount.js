// Shared non-plated M2 fastening hole for the circuit board and base plate.
module.exports = {
  params: { designator: 'H' },
  body: p => `
    (module M2_Mount (layer F.Cu)
      ${p.at}
      (fp_text reference "${p.ref}" (at 0 0) (layer F.Fab) hide
        (effects (font (size 1 1) (thickness 0.15))))
      (fp_text value "M2 mount" (at 0 0) (layer F.Fab) hide
        (effects (font (size 1 1) (thickness 0.15))))
      (pad "" np_thru_hole circle (at 0 0) (size 2.2 2.2) (drill 2.2) (layers *.Cu *.Mask))
    )`
};
