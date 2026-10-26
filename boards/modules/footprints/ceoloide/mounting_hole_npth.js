// Copyright (c) 2023 Marco Massarelli

// SPDX-License-Identifier: MIT



// Author: @ceoloide














module.exports = {
  params: {
    designator: 'MH',
    side: 'F',
    hole_size: '2.2',
    hole_drill: '2.2',
  },
  body: p => `
  (footprint "ceoloide:mounting_hole_npth"
    (layer "${p.side}.Cu")
    ${p.at}
    (property "Reference" "${p.ref}"
      (at 0 2.55 ${p.r})
      (layer "${p.side}.SilkS")
      ${p.ref_hide}
      (effects (font (size 1 1) (thickness 0.15)))
    )
    (pad "" np_thru_hole circle
      (at 0 0 ${p.r})
      (size ${p.hole_size} ${p.hole_size})
      (drill ${p.hole_drill})
      (layers "*.Cu" "*.Mask")
    )
  )
  `
}
