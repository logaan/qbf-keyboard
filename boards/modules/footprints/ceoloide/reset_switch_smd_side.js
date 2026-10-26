// Copyright (c) 2023 Marco Massarelli

// SPDX-License-Identifier: MIT



// Author: @ceoloide









































module.exports = {
  params: {
    designator: 'RST',
    side: 'F',
    reversible: false,
    include_bosses: false,
    include_silkscreen: true,
    include_courtyard: false,
    reset_switch_3dmodel_filename: '',
    reset_switch_3dmodel_xyz_offset: [0, 0, 0],
    reset_switch_3dmodel_xyz_rotation: [0, 0, 0],
    reset_switch_3dmodel_xyz_scale: [1, 1, 1],
    from: { type: 'net', value: 'GND' },
    to: { type: 'net', value: 'RST' },
  },
  body: p => {
    const common_start = `
  (footprint "ceoloide:reset_switch_smd_side"
    (layer "${p.side}.Cu")
    ${p.at}
    (property "Reference" "${p.ref}"
      (at 0 0 ${p.r})
      (layer "${p.side}.SilkS")
      ${p.ref_hide}
      (effects (font (size 1 1) (thickness 0.15)))
    )
    (attr smd)
    (fp_line (start -2.35 -1.75) (end -2.35 1.75) (stroke (width 0.1) (type solid)) (layer "Dwgs.User"))
    (fp_line (start -2.35 -1.75) (end 2.35 -1.75) (stroke (width 0.1) (type solid)) (layer "Dwgs.User"))
    (fp_line (start -2.35 1.75) (end 2.35 1.75) (stroke (width 0.1) (type solid)) (layer "Dwgs.User"))
    (fp_line (start -1.3 -2.75) (end -1.3 -1.75) (stroke (width 0.1) (type solid)) (layer "Dwgs.User"))
    (fp_line (start -1.3 -2.75) (end 1.3 -2.75) (stroke (width 0.1) (type solid)) (layer "Dwgs.User"))
    (fp_line (start 1.3 -2.75) (end 1.3 -1.75) (stroke (width 0.1) (type solid)) (layer "Dwgs.User"))
    (fp_line (start 2.35 -1.75) (end 2.35 1.75) (stroke (width 0.1) (type solid)) (layer "Dwgs.User"))
    `
    const silkscreen_front = `
    (fp_line (start -2.35 -1.5) (end -2.35 -1.75) (stroke (width 0.1) (type solid)) (layer "F.SilkS"))
    (fp_line (start -2.35 1.5) (end -2.35 1.75) (stroke (width 0.1) (type solid)) (layer "F.SilkS"))
    (fp_line (start -2.1 -1.75) (end -2.35 -1.75) (stroke (width 0.1) (type solid)) (layer "F.SilkS"))
    (fp_line (start -2.1 1.75) (end -2.35 1.75) (stroke (width 0.1) (type solid)) (layer "F.SilkS"))
    (fp_line (start 2.1 -1.75) (end 2.35 -1.75) (stroke (width 0.1) (type solid)) (layer "F.SilkS"))
    (fp_line (start 2.1 1.75) (end 2.35 1.75) (stroke (width 0.1) (type solid)) (layer "F.SilkS"))
    (fp_line (start 2.35 -1.5) (end 2.35 -1.75) (stroke (width 0.1) (type solid)) (layer "F.SilkS"))
    (fp_line (start 2.35 1.5) (end 2.35 1.75) (stroke (width 0.1) (type solid)) (layer "F.SilkS"))
    `
    const silkscreen_back = `
    (fp_line (start -2.35 -1.5) (end -2.35 -1.75) (stroke (width 0.1) (type solid)) (layer "B.SilkS"))
    (fp_line (start -2.35 1.5) (end -2.35 1.75) (stroke (width 0.1) (type solid)) (layer "B.SilkS"))
    (fp_line (start -2.1 -1.75) (end -2.35 -1.75) (stroke (width 0.1) (type solid)) (layer "B.SilkS"))
    (fp_line (start -2.1 1.75) (end -2.35 1.75) (stroke (width 0.1) (type solid)) (layer "B.SilkS"))
    (fp_line (start 2.1 -1.75) (end 2.35 -1.75) (stroke (width 0.1) (type solid)) (layer "B.SilkS"))
    (fp_line (start 2.1 1.75) (end 2.35 1.75) (stroke (width 0.1) (type solid)) (layer "B.SilkS"))
    (fp_line (start 2.35 -1.5) (end 2.35 -1.75) (stroke (width 0.1) (type solid)) (layer "B.SilkS"))
    (fp_line (start 2.35 1.5) (end 2.35 1.75) (stroke (width 0.1) (type solid)) (layer "B.SilkS"))
    `
    const pads_front = `
    (pad "1" smd rect (at 2.625 -0.85 ${180 + p.r}) (size 1.55 1) (layers "F.Cu" "F.Paste" "F.Mask") ${p.from.str})
    (pad "2" smd rect (at 2.625 0.85 ${180 + p.r}) (size 1.55 1) (layers "F.Cu" "F.Paste" "F.Mask") ${p.to.str})
    (pad "3" smd rect (at -2.625 -0.85 ${180 + p.r}) (size 1.55 1) (layers "F.Cu" "F.Paste" "F.Mask") ${p.from.str})
    (pad "4" smd rect (at -2.625 0.85 ${180 + p.r}) (size 1.55 1) (layers "F.Cu" "F.Paste" "F.Mask") ${p.to.str})
    `
    const pads_back = `
    (pad "1" smd rect (at -2.625 -0.85 ${180 + p.r}) (size 1.55 1) (layers "B.Cu" "B.Paste" "B.Mask") ${p.from.str})
    (pad "2" smd rect (at -2.625 0.85 ${180 + p.r}) (size 1.55 1) (layers "B.Cu" "B.Paste" "B.Mask") ${p.to.str})
    (pad "3" smd rect (at 2.625 -0.85 ${180 + p.r}) (size 1.55 1) (layers "B.Cu" "B.Paste" "B.Mask") ${p.from.str})
    (pad "4" smd rect (at 2.625 0.85 ${180 + p.r}) (size 1.55 1) (layers "B.Cu" "B.Paste" "B.Mask") ${p.to.str})
    `
    const courtyard_front = `
    (fp_rect (start 2.36 1.75) (end -2.36 -1.75) (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd"))
    `
    const courtyard_back = `
    (fp_rect (start 2.36 1.75) (end -2.36 -1.75) (stroke (width 0.05) (type solid)) (fill none) (layer "B.CrtYd"))
    `
    const bosses = `
    (pad "" np_thru_hole circle (at 0 -1.375 ${180 + p.r}) (size 0.75 0.75) (drill 0.75) (layers "*.Cu" "*.Mask"))
    (pad "" np_thru_hole circle (at 0 1.375 ${180 + p.r}) (size 0.75 0.75) (drill 0.75) (layers "*.Cu" "*.Mask"))
    `

    const reset_switch_3dmodel = `
    (model ${p.reset_switch_3dmodel_filename}
      (offset (xyz ${p.reset_switch_3dmodel_xyz_offset[0]} ${p.reset_switch_3dmodel_xyz_offset[1]} ${p.reset_switch_3dmodel_xyz_offset[2]}))
      (scale (xyz ${p.reset_switch_3dmodel_xyz_scale[0]} ${p.reset_switch_3dmodel_xyz_scale[1]} ${p.reset_switch_3dmodel_xyz_scale[2]}))
      (rotate (xyz ${p.reset_switch_3dmodel_xyz_rotation[0]} ${p.reset_switch_3dmodel_xyz_rotation[1]} ${p.reset_switch_3dmodel_xyz_rotation[2]}))
    )
    `

    const common_end = `
  )
    `

    let final = common_start;
    if (p.include_bosses) {
      final += bosses
    }
    if (p.side == "F" || p.reversible) {
      final += pads_front
      if (p.include_silkscreen) {
        final += silkscreen_front
      }
      if (p.include_courtyard) {
        final += courtyard_front
      }
    }
    if (p.side == "B" || p.reversible) {
      final += pads_back
      if (p.include_silkscreen) {
        final += silkscreen_back
      }
      if (p.include_courtyard) {
        final += courtyard_back
      }
    }
    if (p.reset_switch_3dmodel_filename) {
      final += reset_switch_3dmodel
    }

    final += common_end;

    return final;
  }
}
