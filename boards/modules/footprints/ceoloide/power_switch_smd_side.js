// Copyright (c) 2023 Marco Massarelli

// SPDX-License-Identifier: CC-BY-NC-SA-4.0

// To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/4.0/























































module.exports = {
  params: {
    designator: 'PWR',
    side: 'F',
    reversible: false,
    invert_behavior: false,
    include_silkscreen: true,
    include_courtyard: false,
    switch_3dmodel_filename: '',
    switch_3dmodel_xyz_offset: [0, 0, 0],
    switch_3dmodel_xyz_rotation: [0, 0, 0],
    switch_3dmodel_xyz_scale: [1, 1, 1],
    from: { type: 'net', value: 'BAT_P' },
    to: { type: 'net', value: 'RAW' },
  },
  body: p => {
    const common_start = `
  (footprint "ceoloide:power_switch_smd_side"
    (layer "${p.side}.Cu")
    ${p.at}
    (property "Reference" "${p.ref}"
      (at -3.6 0 ${-90 + p.r})
      (layer "${p.side}.SilkS")
      ${p.ref_hide}
      (effects (font (size 1 1) (thickness 0.15)))
    )
    (attr smd)
    `
    const silkscreen_front = `
    (fp_text user "ON" (at 0 ${p.invert_behavior ? '-' : ''}5 ${p.r}) (layer "F.SilkS")
      (effects (font (size 1 1) (thickness 0.15)))
    )
    (fp_text user "OFF" (at 0 ${p.invert_behavior ? '' : '-'}5 ${p.r}) (layer "F.SilkS")
      (effects (font (size 1 1) (thickness 0.15)))
    )
    (fp_line (start 0.415 -3.45) (end -0.375 -3.45) (layer "F.SilkS") (stroke (width 0.12) (type solid)))
    (fp_line (start -0.375 3.45) (end 0.415 3.45) (layer "F.SilkS") (stroke (width 0.12) (type solid)))
    (fp_line (start -1.425 1.6) (end -1.425 -0.1) (layer "F.SilkS") (stroke (width 0.12) (type solid)))
    (fp_line (start 1.425 2.85) (end 1.425 -2.85) (layer "F.SilkS") (stroke (width 0.12) (type solid)))
    (fp_line (start -1.425 -1.4) (end -1.425 -1.6) (layer "F.SilkS") (stroke (width 0.12) (type solid)))
    `
    const silkscreen_back = `
    (fp_text user "${p.ref}" (at -3.5 0 ${90 + p.r}) (layer "B.SilkS") ${p.ref_hide}
      (effects (font (size 1 1) (thickness 0.15)) (justify mirror))
    )
    (fp_text user "ON" (at 0 ${p.invert_behavior ? '-' : ''}5 ${p.r}) (layer "B.SilkS")
      (effects (font (size 1 1) (thickness 0.15)) (justify mirror))
    )
    (fp_text user "OFF" (at 0 ${p.invert_behavior ? '' : '-'}5 ${p.r}) (layer "B.SilkS")
      (effects (font (size 1 1) (thickness 0.15)) (justify mirror))
    )
    (fp_line (start -1.425 1.4) (end -1.425 1.6) (layer "B.SilkS") (stroke (width 0.12) (type solid)))
    (fp_line (start 0.415 3.45) (end -0.375 3.45) (layer "B.SilkS") (stroke (width 0.12) (type solid)))
    (fp_line (start -0.375 -3.45) (end 0.415 -3.45) (layer "B.SilkS") (stroke (width 0.12) (type solid)))
    (fp_line (start -1.425 -1.6) (end -1.425 0.1) (layer "B.SilkS") (stroke (width 0.12) (type solid)))
    (fp_line (start 1.425 -2.85) (end 1.425 2.85) (layer "B.SilkS") (stroke (width 0.12) (type solid)))
    `
    const courtyard_front = `
    (fp_line (start 1.795 4.4) (end -2.755 4.4) (layer "F.CrtYd") (stroke (width 0.05) (type solid)))
    (fp_line (start 1.795 1.65) (end 1.795 4.4) (layer "F.CrtYd") (stroke (width 0.05) (type solid)))
    (fp_line (start 3.095 1.65) (end 1.795 1.65) (layer "F.CrtYd") (stroke (width 0.05) (type solid)))
    (fp_line (start 3.095 -1.65) (end 3.095 1.65) (layer "F.CrtYd") (stroke (width 0.05) (type solid)))
    (fp_line (start 1.795 -1.65) (end 3.095 -1.65) (layer "F.CrtYd") (stroke (width 0.05) (type solid)))
    (fp_line (start 1.795 -4.4) (end 1.795 -1.65) (layer "F.CrtYd") (stroke (width 0.05) (type solid)))
    (fp_line (start -2.755 -4.4) (end 1.795 -4.4) (layer "F.CrtYd") (stroke (width 0.05) (type solid)))
    (fp_line (start -2.755 4.4) (end -2.755 -4.4) (layer "F.CrtYd") (stroke (width 0.05) (type solid)))
    `
    const courtyard_back = `
    (fp_line (start -2.755 -4.4) (end -2.755 4.4) (layer "B.CrtYd") (stroke (width 0.05) (type solid)))
    (fp_line (start 3.095 1.65) (end 3.095 -1.65) (layer "B.CrtYd") (stroke (width 0.05) (type solid)))
    (fp_line (start 1.795 1.65) (end 3.095 1.65) (layer "B.CrtYd") (stroke (width 0.05) (type solid)))
    (fp_line (start 1.795 -4.4) (end -2.755 -4.4) (layer "B.CrtYd") (stroke (width 0.05) (type solid)))
    (fp_line (start 1.795 -1.65) (end 1.795 -4.4) (layer "B.CrtYd") (stroke (width 0.05) (type solid)))
    (fp_line (start 3.095 -1.65) (end 1.795 -1.65) (layer "B.CrtYd") (stroke (width 0.05) (type solid)))
    (fp_line (start 1.795 4.4) (end 1.795 1.65) (layer "B.CrtYd") (stroke (width 0.05) (type solid)))
    (fp_line (start -2.755 4.4) (end 1.795 4.4) (layer "B.CrtYd") (stroke (width 0.05) (type solid)))
    `

    const pads_front = `
    (fp_line (start -1.305 -3.35) (end -1.305 3.35) (layer "F.Fab") (stroke (width 0.1) (type solid)))
    (fp_line (start 1.295 -3.35) (end -1.305 -3.35) (layer "F.Fab") (stroke (width 0.1) (type solid)))
    (fp_line (start 1.295 3.35) (end 1.295 -3.35) (layer "F.Fab") (stroke (width 0.1) (type solid)))
    (fp_line (start -1.305 3.35) (end 1.295 3.35) (layer "F.Fab") (stroke (width 0.1) (type solid)))
    (fp_line (start 2.595 0.1) (end 1.295 0.1) (layer "F.Fab") (stroke (width 0.1) (type solid)))
    (fp_line (start 2.645 0.15) (end 2.595 0.1) (layer "F.Fab") (stroke (width 0.1) (type solid)))
    (fp_line (start 2.845 0.35) (end 2.645 0.15) (layer "F.Fab") (stroke (width 0.1) (type solid)))
    (fp_line (start 2.845 1.2) (end 2.845 0.35) (layer "F.Fab") (stroke (width 0.1) (type solid)))
    (fp_line (start 2.645 1.4) (end 2.845 1.2) (layer "F.Fab") (stroke (width 0.1) (type solid)))
    (fp_line (start 1.345 1.4) (end 2.645 1.4) (layer "F.Fab") (stroke (width 0.1) (type solid)))
    (pad "" smd rect (at 1.125 -3.65 ${90 + p.r}) (size 1 0.8) (layers "F.Cu" "F.Paste" "F.Mask"))
    (pad "" smd rect (at -1.085 -3.65 ${90 + p.r}) (size 1 0.8) (layers "F.Cu" "F.Paste" "F.Mask"))
    (pad "" smd rect (at -1.085 3.65 ${90 + p.r}) (size 1 0.8) (layers "F.Cu" "F.Paste" "F.Mask"))
    (pad "" smd rect (at 1.125 3.65 ${90 + p.r}) (size 1 0.8) (layers "F.Cu" "F.Paste" "F.Mask"))
    (pad "1" smd rect (at -1.735 2.25 ${90 + p.r}) (size 0.7 1.5) (layers "F.Cu" "F.Paste" "F.Mask") ${p.invert_behavior ? '' : p.from.str})
    (pad "2" smd rect (at -1.735 -0.75 ${90 + p.r}) (size 0.7 1.5) (layers "F.Cu" "F.Paste" "F.Mask") ${p.to.str})
    (pad "3" smd rect (at -1.735 -2.25 ${90 + p.r}) (size 0.7 1.5) (layers "F.Cu" "F.Paste" "F.Mask") ${p.invert_behavior ? p.from.str : ''})
    `
    const pads_back = `
    (fp_line (start 2.595 -0.1) (end 1.295 -0.1) (layer "B.Fab") (stroke (width 0.1) (type solid)))
    (fp_line (start -1.305 3.35) (end -1.305 -3.35) (layer "B.Fab") (stroke (width 0.1) (type solid)))
    (fp_line (start 2.645 -0.15) (end 2.595 -0.1) (layer "B.Fab") (stroke (width 0.1) (type solid)))
    (fp_line (start 2.845 -1.2) (end 2.845 -0.35) (layer "B.Fab") (stroke (width 0.1) (type solid)))
    (fp_line (start 1.345 -1.4) (end 2.645 -1.4) (layer "B.Fab") (stroke (width 0.1) (type solid)))
    (fp_line (start 2.845 -0.35) (end 2.645 -0.15) (layer "B.Fab") (stroke (width 0.1) (type solid)))
    (fp_line (start 2.645 -1.4) (end 2.845 -1.2) (layer "B.Fab") (stroke (width 0.1) (type solid)))
    (fp_line (start 1.295 -3.35) (end 1.295 3.35) (layer "B.Fab") (stroke (width 0.1) (type solid)))
    (fp_line (start 1.295 3.35) (end -1.305 3.35) (layer "B.Fab") (stroke (width 0.1) (type solid)))
    (fp_line (start -1.305 -3.35) (end 1.295 -3.35) (layer "B.Fab") (stroke (width 0.1) (type solid)))
    (pad "" smd rect (at -1.085 -3.65 ${270 + p.r}) (size 1 0.8) (layers "B.Cu" "B.Paste" "B.Mask"))
    (pad "" smd rect (at 1.125 -3.65 ${270 + p.r}) (size 1 0.8) (layers "B.Cu" "B.Paste" "B.Mask"))
    (pad "" smd rect (at -1.085 3.65 ${270 + p.r}) (size 1 0.8) (layers "B.Cu" "B.Paste" "B.Mask"))
    (pad "" smd rect (at 1.125 3.65 ${270 + p.r}) (size 1 0.8) (layers "B.Cu" "B.Paste" "B.Mask"))
    (pad "1" smd rect (at -1.735 -2.25 ${270 + p.r}) (size 0.7 1.5) (layers "B.Cu" "B.Paste" "B.Mask") ${p.invert_behavior ? p.from.str : ''})
    (pad "2" smd rect (at -1.735 0.75 ${270 + p.r}) (size 0.7 1.5) (layers "B.Cu" "B.Paste" "B.Mask") ${p.to.str})
    (pad "3" smd rect (at -1.735 2.25 ${270 + p.r}) (size 0.7 1.5) (layers "B.Cu" "B.Paste" "B.Mask") ${p.invert_behavior ? '' : p.from.str})
    `
    const common_end = `
    (pad "" np_thru_hole circle (at 0.025 -1.5 ${90 + p.r}) (size 0.9 0.9) (drill 0.9) (layers "*.Cu" "*.Mask"))
    (pad "" np_thru_hole circle (at 0.025 1.5 ${90 + p.r}) (size 0.9 0.9) (drill 0.9) (layers "*.Cu" "*.Mask"))
  )
    `

    const switch_3dmodel = `
    (model ${p.switch_3dmodel_filename}
      (offset (xyz ${p.switch_3dmodel_xyz_offset[0]} ${p.switch_3dmodel_xyz_offset[1]} ${p.switch_3dmodel_xyz_offset[2]}))
      (scale (xyz ${p.switch_3dmodel_xyz_scale[0]} ${p.switch_3dmodel_xyz_scale[1]} ${p.switch_3dmodel_xyz_scale[2]}))
      (rotate (xyz ${p.switch_3dmodel_xyz_rotation[0]} ${p.switch_3dmodel_xyz_rotation[1]} ${p.switch_3dmodel_xyz_rotation[2]}))
    )
    `

    let final = common_start;
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

    if (p.switch_3dmodel_filename) {
      final += switch_3dmodel
    }

    final += common_end;
    return final;
  }
}
