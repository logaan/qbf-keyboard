// Copyright (c) 2023 Marco Massarelli

// SPDX-License-Identifier: CC-BY-NC-SA-4.0

// To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/4.0/















































































































































































module.exports = {
  params: {
    designator: 'S',
    side: 'B',
    reversible: false,
    hotswap_pads_same_side: false,
    include_traces_vias: true,
    trace_width: 0.2,
    via_size: 0.6,
    via_drill: 0.3,
    locked_traces_vias: false,
    hotswap: true,
    include_plated_holes: false,
    include_stabilizer_nets: false,
    include_centerhole_net: false,
    solder: false,
    outer_pad_width_front: 2.6,
    outer_pad_width_back: 2.6,
    include_keycap: false,
    keycap_width: 18,
    keycap_height: 18,
    include_corner_marks: false,
    include_choc_v1_led_cutout_marks: false,
    include_choc_v2_led_cutout_marks: false,
    include_stabilizer_pad: true,
    oval_stabilizer_pad: false,
    choc_v1_support: true,
    choc_v2_support: true,
    choc_v1_stabilizers_diameter: 1.9,
    center_hole_diameter: 0.0,
    allow_soldermask_bridges: true,
    switch_3dmodel_filename: '',
    switch_3dmodel_xyz_offset: [0, 0, 0],
    switch_3dmodel_xyz_rotation: [0, 0, 0],
    switch_3dmodel_xyz_scale: [1, 1, 1],
    hotswap_3dmodel_filename: '',
    hotswap_3dmodel_xyz_offset: [0, 0, 0],
    hotswap_3dmodel_xyz_rotation: [0, 0, 0],
    hotswap_3dmodel_xyz_scale: [1, 1, 1],
    keycap_3dmodel_filename: '',
    keycap_3dmodel_xyz_offset: [0, 0, 0],
    keycap_3dmodel_xyz_rotation: [0, 0, 0],
    keycap_3dmodel_xyz_scale: [1, 1, 1],
    from: undefined,
    to: undefined,
    CENTERHOLE: { type: 'net', value: 'GND'},
    LEFTSTAB: { type: 'net', value: 'D1' },
    RIGHTSTAB: { type: 'net', value: 'D2' }
  },
  body: p => {
    const center_hole_diameter = p.center_hole_diameter > 0 ? p.center_hole_diameter : (p.choc_v2_support ? 5 : 3.4);
    const common_top = `
  (footprint "ceoloide:switch_choc_v1_v2"
    (layer "${p.side}.Cu")
    ${p.at}
    (property "Reference" "${p.ref}"
      (at 0 8.8 ${p.r})
      (layer "${p.side}.SilkS")
      ${p.ref_hide}
      (effects (font (size 1 1) (thickness 0.15)))
    )
    (attr exclude_from_pos_files exclude_from_bom${p.allow_soldermask_bridges ? ' allow_soldermask_bridges' : ''})

    ${''}
    ${p.include_plated_holes ? `
    (pad "" thru_hole circle (at 0 0 ${p.r}) (size ${center_hole_diameter + 0.3} ${center_hole_diameter + 0.3}) (drill ${center_hole_diameter}) (layers "*.Cu" "*.Mask") ${p.include_centerhole_net ? p.CENTERHOLE : ''})
    `: `
    (pad "" np_thru_hole circle (at 0 0 ${p.r}) (size ${center_hole_diameter} ${center_hole_diameter}) (drill ${center_hole_diameter}) (layers "*.Cu" "*.Mask"))
    `}
    `

    const choc_v1_stabilizers = `
    ${p.include_plated_holes ? `
    (pad "" thru_hole circle (at 5.5 0 ${p.r}) (size ${p.choc_v1_stabilizers_diameter + 0.3} ${p.choc_v1_stabilizers_diameter + 0.3}) (drill ${p.choc_v1_stabilizers_diameter}) (layers "*.Cu" "*.Mask"))
    (pad "" thru_hole circle (at -5.5 0 ${p.r}) (size ${p.choc_v1_stabilizers_diameter + 0.3} ${p.choc_v1_stabilizers_diameter + 0.3}) (drill ${p.choc_v1_stabilizers_diameter}) (layers "*.Cu" "*.Mask"))
    `: `
    (pad "" np_thru_hole circle (at 5.5 0 ${p.r}) (size ${p.choc_v1_stabilizers_diameter} ${p.choc_v1_stabilizers_diameter}) (drill ${p.choc_v1_stabilizers_diameter}) (layers "*.Cu" "*.Mask"))
    (pad "" np_thru_hole circle (at -5.5 0 ${p.r}) (size ${p.choc_v1_stabilizers_diameter} ${p.choc_v1_stabilizers_diameter}) (drill ${p.choc_v1_stabilizers_diameter}) (layers "*.Cu" "*.Mask"))
    `}
    `

    const corner_marks = `
    ${''}
    (fp_line (start -7 -6) (end -7 -7) (layer "Dwgs.User") (stroke (width 0.15) (type solid)))
    (fp_line (start -7 7) (end -6 7) (layer "Dwgs.User") (stroke (width 0.15) (type solid)))
    (fp_line (start -6 -7) (end -7 -7) (layer "Dwgs.User") (stroke (width 0.15) (type solid)))
    (fp_line (start -7 7) (end -7 6) (layer "Dwgs.User") (stroke (width 0.15) (type solid)))
    (fp_line (start 7 6) (end 7 7) (layer "Dwgs.User") (stroke (width 0.15) (type solid)))
    (fp_line (start 7 -7) (end 6 -7) (layer "Dwgs.User") (stroke (width 0.15) (type solid)))
    (fp_line (start 6 7) (end 7 7) (layer "Dwgs.User") (stroke (width 0.15) (type solid)))
    (fp_line (start 7 -7) (end 7 -6) (layer "Dwgs.User") (stroke (width 0.15) (type solid)))
    `

    const keycap_xo = 0.5 * p.keycap_width
    const keycap_yo = 0.5 * p.keycap_height
    const keycap_marks = `
    (fp_rect (start ${keycap_xo} ${keycap_yo}) (end ${-keycap_xo} ${-keycap_yo}) (layer "Dwgs.User") (stroke (width 0.15) (type solid)) (fill none))
    `

    const choc_v1_led_cutout_marks = `
    (fp_rect (start -2.65 6.325) (end 2.65 3.075) (layer "Dwgs.User") (width 0.15) (stroke (width 0.15) (type solid)) (fill none))
    `

    const choc_v2_led_cutout_marks = `
    (fp_rect (start -2.75 6.405) (end 2.75 3.455) (layer "Dwgs.User") (width 0.15) (stroke (width 0.15) (type solid)) (fill none))
    `

    const hotswap_common = `
    ${'' }
    ${p.include_plated_holes ? `
    (pad ${p.reversible ? '""' : '"1"'} thru_hole circle (at 0 -5.95 ${p.r}) (size 3.3 3.3) (drill 3) (layers "*.Cu" "*.Mask") ${p.reversible ? '' : p.from.str})
    `: `
    (pad "" np_thru_hole circle (at 0 -5.95 ${p.r}) (size 3 3) (drill 3) (layers "*.Cu" "*.Mask"))
    `}
    `

    const hotswap_back_pads_plated = `
    (pad "1" smd roundrect (at -2.648 -5.95 ${p.r}) (size 3.8 2.15) (layers "B.Cu") (roundrect_rratio 0.1) ${p.from.str})
    (pad "" smd roundrect (at -3.248 -5.95 ${p.r}) (size 2.6 2.15) (layers "B.Paste" "B.Mask") (roundrect_rratio 0.1))
    (pad "2" smd roundrect (at ${7.6475 - (2.6 - p.outer_pad_width_back) / 2} -3.75 ${p.r}) (size ${p.outer_pad_width_back + 1.2} 2.15) (layers "B.Cu") (roundrect_rratio 0.1) ${p.to.str})
    (pad "" smd roundrect (at ${8.2475 - (2.6 - p.outer_pad_width_back) / 2} -3.75 ${p.r}) (size ${p.outer_pad_width_back} 2.15) (layers "B.Paste" "B.Mask") (roundrect_rratio ${(2.15 / p.outer_pad_width_back) <= 1 ? 0.1 : 0.1 * (2.15 / p.outer_pad_width_back)}))
    `

    const hotswap_front_pads_plated = `
    (pad "1" smd roundrect (at 2.648 -5.95 ${p.r}) (size 3.8 2.15) (layers "F.Cu") (roundrect_rratio 0.1) ${p.from.str})
    (pad "" smd roundrect (at 3.248 -5.95 ${p.r}) (size 2.6 2.15) (layers "F.Paste" "F.Mask") (roundrect_rratio 0.1)) 
    (pad "2" smd roundrect (at ${-7.6475 + (2.6 - p.outer_pad_width_front) / 2} -3.75 ${p.r}) (size ${p.outer_pad_width_front + 1.2} 2.15) (layers "F.Cu") (roundrect_rratio 0.1) ${p.to.str})
    (pad "" smd roundrect (at ${-8.2475 + (2.6 - p.outer_pad_width_front) / 2} -3.75 ${p.r}) (size ${p.outer_pad_width_front} 2.15) (layers "F.Paste" "F.Mask") (roundrect_rratio ${(2.15 / p.outer_pad_width_front) <= 1 ? 0.1 : 0.1 * (2.15 / p.outer_pad_width_front)}))
    `

    const hotswap_back_pads_plated_reversible = `
    (pad "1" smd roundrect (at -3.245 -5.95 ${p.r}) (size 2.65 2.15) (layers "B.Cu" "B.Paste" "B.Mask") (roundrect_rratio 0.1) ${p.from.str})
    (pad "2" smd roundrect (at ${7.6475 - (2.6 - p.outer_pad_width_back) / 2} -3.75 ${p.r}) (size ${p.outer_pad_width_back + 1.2} 2.15) (layers "B.Cu") (roundrect_rratio 0.1) ${p.to.str})
    (pad "" smd roundrect (at ${8.2475 - (2.6 - p.outer_pad_width_back) / 2} -3.75 ${p.r}) (size ${p.outer_pad_width_back} 2.15) (layers "B.Paste" "B.Mask") (roundrect_rratio ${(2.15 / p.outer_pad_width_back) <= 1 ? 0.1 : 0.1 * (2.15 / p.outer_pad_width_back)}))
    `

    const hotswap_front_pads_plated_reversible = `
    (pad "2" smd roundrect (at 3.245 -5.95 ${p.r}) (size 2.65 2.15) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.1) ${p.to.str})
    (pad "1" smd roundrect (at ${-7.6475 + (2.6 - p.outer_pad_width_front) / 2} -3.75 ${p.r}) (size ${p.outer_pad_width_front + 1.2} 2.15) (layers "F.Cu") (roundrect_rratio 0.1) ${p.from.str})
    (pad "" smd roundrect (at ${-8.2475 + (2.6 - p.outer_pad_width_front) / 2} -3.75 ${p.r}) (size ${p.outer_pad_width_front} 2.15) (layers "F.Paste" "F.Mask") (roundrect_rratio ${(2.15 / p.outer_pad_width_front) <= 1 ? 0.1 : 0.1 * (2.15 / p.outer_pad_width_front)}))
    `

    const hotswap_front_pad_cutoff = `
    (pad "1" smd roundrect
      (at 3.275 -5.95 ${p.r})
      (size 2.6 2.6)
      (layers "F.Cu" "F.Paste" "F.Mask")
      (roundrect_rratio 0)
			(chamfer_ratio 0.455)
			(chamfer bottom_right)
      ${p.from.str}
    )
    `

    const hotswap_front_pad_full = `
    (pad "1" smd rect (at 3.275 -5.95 ${p.r}) (size 2.6 2.6) (layers "F.Cu" "F.Paste" "F.Mask") ${p.from.str})
    `

    const hotswap_back_pad_cutoff = `
    (pad "1" smd roundrect
      (at -3.275 -5.95 ${p.r})
      (size 2.6 2.6)
      (layers "B.Cu" "B.Paste" "B.Mask")
      (roundrect_rratio 0)
			(chamfer_ratio 0.455)
			(chamfer bottom_left)
      ${p.hotswap_pads_same_side ? p.to.str : p.from.str}
    )
    `

    const hotswap_back_pad_full = `
    (pad "1" smd rect (at -3.275 -5.95 ${p.r}) (size 2.6 2.6) (layers "B.Cu" "B.Paste" "B.Mask") ${p.from.str})
    `

    const hotswap_back = `
    ${'' }
    ${'' }
    (fp_line (start -1.5 -8.2) (end -2 -7.7) (layer "B.SilkS") (stroke (width 0.15) (type solid)))
    (fp_line (start 1.5 -8.2) (end -1.5 -8.2) (layer "B.SilkS") (stroke (width 0.15) (type solid)))
    (fp_line (start 2 -7.7) (end 1.5 -8.2) (layer "B.SilkS") (stroke (width 0.15) (type solid)))
    (fp_line (start 2 -7.7) (end 2 -6.78) (layer "B.SilkS") (stroke (width 0.15) (type solid)))
    (fp_line (start 2.52 -6.2) (end 7 -6.2) (layer "B.SilkS") (stroke (width 0.15) (type solid)))
    (fp_line (start 7 -6.2) (end 7 -5.6) (layer "B.SilkS") (stroke (width 0.15) (type solid)))
    (fp_arc (start 2.52 -6.2) (mid 2.139878 -6.382304) (end 2 -6.78) (layer "B.SilkS") (stroke (width 0.15) (type solid)))
  
    ${'' }
    (fp_line (start -1.5 -3.7) (end -2 -4.2) (layer "B.SilkS") (stroke (width 0.15) (type solid)))
    (fp_line (start 0.8 -3.7) (end -1.5 -3.7) (layer "B.SilkS") (stroke (width 0.15) (type solid)))
    (fp_line (start 2.5 -1.5) (end 2.5 -2.2) (layer "B.SilkS") (stroke (width 0.15) (type solid)))
    (fp_line (start 7 -1.5) (end 2.5 -1.5) (layer "B.SilkS") (stroke (width 0.15) (type solid)))
    (fp_line (start 7 -2) (end 7 -1.5) (layer "B.SilkS") (stroke (width 0.15) (type solid)))
    (fp_arc (start 0.8 -3.7) (mid 1.956518 -3.312082) (end 2.5 -2.22) (layer "B.SilkS") (stroke (width 0.15) (type solid)))

    ${p.include_plated_holes ? `
    ${'' }
      ${p.reversible ? `
      (pad "2" thru_hole circle (at 5 -3.75 ${195 + p.r}) (size 3.3 3.3) (drill 3) (layers "*.Cu" "*.Mask") ${p.to.str})
      ${'' }
      ${hotswap_back_pads_plated_reversible}
      `:`
      (pad "2" thru_hole circle (at 5 -3.75 ${195 + p.r}) (size 3.3 3.3) (drill 3) (layers "*.Cu" "*.Mask") ${p.to.str})
      ${'' }
      ${hotswap_back_pads_plated}
      `}
    `: `
    ${'' }
    ${p.reversible ? hotswap_back_pad_cutoff : hotswap_back_pad_full}

    ${'' }
    (pad "2" smd rect (at ${8.275 - (2.6 - p.outer_pad_width_back) / 2} -3.75 ${p.r}) (size ${p.outer_pad_width_back} 2.6) (layers "B.Cu" "B.Paste" "B.Mask") ${p.hotswap_pads_same_side ? p.from.str : p.to.str})

    ${'' }
    (pad "" np_thru_hole circle (at 5 -3.75 ${195 + p.r}) (size 3 3) (drill 3) (layers "*.Cu" "*.Mask"))
    `}
    `

    const hotswap_front = `
    ${'' }
    ${'' }
    (fp_line (start -7 -5.6) (end -7 -6.2) (layer "F.SilkS") (stroke (width 0.15) (type solid)))
    (fp_line (start -7 -6.2) (end -2.52 -6.2) (layer "F.SilkS") (stroke (width 0.15) (type solid)))
    (fp_line (start -2 -6.78) (end -2 -7.7) (layer "F.SilkS") (stroke (width 0.15) (type solid)))
    (fp_line (start -1.5 -8.2) (end -2 -7.7) (layer "F.SilkS") (stroke (width 0.15) (type solid)))
    (fp_line (start 1.5 -8.2) (end -1.5 -8.2) (layer "F.SilkS") (stroke (width 0.15) (type solid)))
    (fp_line (start 2 -7.7) (end 1.5 -8.2) (layer "F.SilkS") (stroke (width 0.15) (type solid)))
    (fp_arc (start -2 -6.78) (mid -2.139878 -6.382304) (end -2.52 -6.2) (layer "F.SilkS") (stroke (width 0.15) (type solid)))
  
    ${'' }
    (fp_line (start -7 -1.5) (end -7 -2) (layer "F.SilkS") (stroke (width 0.15) (type solid)))
    (fp_line (start -2.5 -1.5) (end -7 -1.5) (layer "F.SilkS") (stroke (width 0.15) (type solid)))
    (fp_line (start -2.5 -2.2) (end -2.5 -1.5) (layer "F.SilkS") (stroke (width 0.15) (type solid)))
    (fp_line (start 1.5 -3.7) (end -0.8 -3.7) (layer "F.SilkS") (stroke (width 0.15) (type solid)))
    (fp_line (start 2 -4.2) (end 1.5 -3.7) (layer "F.SilkS") (stroke (width 0.15) (type solid)))
    (fp_arc (start -2.5 -2.22) (mid -1.956518 -3.312082) (end -0.8 -3.7) (layer "F.SilkS") (stroke (width 0.15) (type solid)))
    
    ${p.include_plated_holes ? `
    ${'' }
    ${p.reversible ? `
    (pad "1" thru_hole circle (at -5 -3.75 ${195 + p.r}) (size 3.3 3.3) (drill 3) (layers "*.Cu" "*.Mask") ${p.from.str})
    ${'' }
    ${hotswap_front_pads_plated_reversible}
    `:`
    (pad "2" thru_hole circle (at -5 -3.75 ${195 + p.r}) (size 3.3 3.3) (drill 3) (layers "*.Cu" "*.Mask") ${p.to.str})
    ${'' }
    ${hotswap_front_pads_plated}
    `}
    `: `
    ${'' }
    (pad "" np_thru_hole circle (at -5 -3.75 ${195 + p.r}) (size 3 3) (drill 3) (layers "*.Cu" "*.Mask"))

    ${'' }
    ${p.reversible ? hotswap_front_pad_cutoff : hotswap_front_pad_full}

    ${'' }
    (pad "2" smd rect (at ${-8.275 + (2.6 - p.outer_pad_width_front) / 2} -3.75 ${p.r}) (size ${p.outer_pad_width_front} 2.6) (layers "F.Cu" "F.Paste" "F.Mask") ${p.to.str})
    `}
    `

    
    
    
    
    let solder_offset_x_front = '-'
    let solder_offset_x_back = ''
    let solder_offset_y = '-'
    let stab_offset_x_front = ''
    let stab_offset_x_back = '-'
    let stab_offset_y = ''
    if (p.hotswap && p.solder) {
      solder_offset_x_front = ''
      solder_offset_x_back = '-'
      solder_offset_y = ''
      stab_offset_x_front = '-'
      stab_offset_x_back = ''
      stab_offset_y = ''
    }

    const solder_common = `
    (pad "2" thru_hole circle (at 0 ${solder_offset_y}5.9 ${195 + p.r}) (size 2.032 2.032) (drill 1.27) (layers "*.Cu" "*.Mask") ${p.from.str})
    `

    const solder_front = `
    (pad "1" thru_hole circle (at ${solder_offset_x_front}5 ${solder_offset_y}3.8 ${195 + p.r}) (size 2.032 2.032) (drill 1.27) (layers "*.Cu" "*.Mask") ${p.to.str})
    `
    
    const solder_back = `
    (pad "1" thru_hole circle (at ${solder_offset_x_back}5 ${solder_offset_y}3.8 ${195 + p.r}) (size 2.032 2.032) (drill 1.27) (layers "*.Cu" "*.Mask") ${p.to.str})
    `

    const oval_corner_stab_front = `
    (pad "" thru_hole oval (at ${stab_offset_x_front}5 ${stab_offset_y}5.15 ${p.r}) (size 2.4 1.2) (drill oval 1.6 0.4) (layers "*.Cu" "*.Mask") ${p.solder && p.hotswap ? p.to.str : p.include_stabilizer_nets ? p.RIGHTSTAB : ''})
    `

    const oval_corner_stab_back = `
    (pad "" thru_hole oval (at ${stab_offset_x_back}5 ${stab_offset_y}5.15 ${p.r}) (size 2.4 1.2) (drill oval 1.6 0.4) (layers "*.Cu" "*.Mask") ${p.solder && p.hotswap ? p.to.str : p.include_stabilizer_nets ? p.LEFTSTAB : ''})
    `

    const round_corner_stab_front = `
    (pad "" thru_hole circle (at ${stab_offset_x_front}5.00 ${stab_offset_y}5.15 ${p.r}) (size 1.9 1.9) (drill 1.6) (layers "*.Cu" "*.Mask") ${p.solder && p.hotswap ? p.to.str : p.include_stabilizer_nets ? p.RIGHTSTAB : ''})
    `

    const round_corner_stab_back = `
    (pad "" thru_hole circle (at ${stab_offset_x_back}5.00 ${stab_offset_y}5.15 ${p.r}) (size 1.9 1.9) (drill 1.6) (layers "*.Cu" "*.Mask") ${p.solder && p.hotswap ? p.to.str : p.include_stabilizer_nets ? p.LEFTSTAB : ''})
    `

    const switch_3dmodel = `
    (model ${p.switch_3dmodel_filename}
      (offset (xyz ${p.switch_3dmodel_xyz_offset[0]} ${p.switch_3dmodel_xyz_offset[1]} ${p.switch_3dmodel_xyz_offset[2]}))
      (scale (xyz ${p.switch_3dmodel_xyz_scale[0]} ${p.switch_3dmodel_xyz_scale[1]} ${p.switch_3dmodel_xyz_scale[2]}))
      (rotate (xyz ${p.switch_3dmodel_xyz_rotation[0]} ${p.switch_3dmodel_xyz_rotation[1]} ${p.switch_3dmodel_xyz_rotation[2]}))
    )
    `

    const hotswap_3dmodel = `
    (model ${p.hotswap_3dmodel_filename}
      (offset (xyz ${p.hotswap_3dmodel_xyz_offset[0]} ${p.hotswap_3dmodel_xyz_offset[1]} ${p.hotswap_3dmodel_xyz_offset[2]}))
      (scale (xyz ${p.hotswap_3dmodel_xyz_scale[0]} ${p.hotswap_3dmodel_xyz_scale[1]} ${p.hotswap_3dmodel_xyz_scale[2]}))
      (rotate (xyz ${p.hotswap_3dmodel_xyz_rotation[0]} ${p.hotswap_3dmodel_xyz_rotation[1]} ${p.hotswap_3dmodel_xyz_rotation[2]}))
    )
	  `

    const keycap_3dmodel = `
    (model ${p.keycap_3dmodel_filename}
      (offset (xyz ${p.keycap_3dmodel_xyz_offset[0]} ${p.keycap_3dmodel_xyz_offset[1]} ${p.keycap_3dmodel_xyz_offset[2]}))
      (scale (xyz ${p.keycap_3dmodel_xyz_scale[0]} ${p.keycap_3dmodel_xyz_scale[1]} ${p.keycap_3dmodel_xyz_scale[2]}))
      (rotate (xyz ${p.keycap_3dmodel_xyz_rotation[0]} ${p.keycap_3dmodel_xyz_rotation[1]} ${p.keycap_3dmodel_xyz_rotation[2]}))
    )
	  `

    const common_bottom = `
  )
    `

    const hotswap_routes_unplated = `
	(segment
		(start ${p.eaxy(3.275, -5.95)})
		(end ${p.eaxy(1.2, -3.875)})
		(width ${p.trace_width})
    (locked ${p.locked_traces_vias ? 'yes' : 'no'})
		(layer "F.Cu")
		(net ${p.from.index})
	)
	(segment
		(start ${p.eaxy(1.2, -3.875)})
		(end ${p.eaxy(0, -3.875)})
		(width ${p.trace_width})
    (locked ${p.locked_traces_vias ? 'yes' : 'no'})
		(layer "F.Cu")
		(net ${p.from.index})
	)
	(via
		(at ${p.eaxy(0, -3.875)})
		(size ${p.via_size})
    (drill ${p.via_drill})
		(layers "F.Cu" "B.Cu")
    (locked ${p.locked_traces_vias ? 'yes' : 'no'})
		(net ${p.from.index})
	)
	(segment
		(start ${p.eaxy(-1.2, -3.875)})
		(end ${p.eaxy(0, -3.875)})
		(width ${p.trace_width})
    (locked ${p.locked_traces_vias ? 'yes' : 'no'})
		(layer "B.Cu")
		(net ${p.from.index})
	)
	(segment
		(start ${p.eaxy(-3.275, -5.95)})
		(end ${p.eaxy(-1.2, -3.875)})
		(width ${p.trace_width})
    (locked ${p.locked_traces_vias ? 'yes' : 'no'})
		(layer "B.Cu")
		(net ${p.from.index})
	)
	(segment
		(start ${p.eaxy(-6.421, -1.896)})
		(end ${p.eaxy(-2.154, -1.896)})
		(width ${p.trace_width})
    (locked ${p.locked_traces_vias ? 'yes' : 'no'})
		(layer "F.Cu")
		(net ${p.to.index})
	)
	(segment
		(start ${p.eaxy(-0.975, -3.075)})
		(end ${p.eaxy(0, -3.075)})
		(width ${p.trace_width})
    (locked ${p.locked_traces_vias ? 'yes' : 'no'})
		(layer "F.Cu")
		(net ${p.to.index})
	)
	(segment
		(start ${p.eaxy(-8.275 + (2.6 - p.outer_pad_width_front) / 2, -3.75)})
		(end ${p.eaxy(-6.421, -1.896)})
		(width ${p.trace_width})
    (locked ${p.locked_traces_vias ? 'yes' : 'no'})
		(layer "F.Cu")
		(net ${p.to.index})
	)
	(segment
		(start ${p.eaxy(-2.154, -1.896)})
		(end ${p.eaxy(-0.975, -3.075)})
		(width ${p.trace_width})
    (locked ${p.locked_traces_vias ? 'yes' : 'no'})
		(layer "F.Cu")
		(net ${p.to.index})
	)
	(via
		(at ${p.eaxy(0, -3.075)})
		(size ${p.via_size})
    (drill ${p.via_drill})
		(layers "F.Cu" "B.Cu")
    (locked ${p.locked_traces_vias ? 'yes' : 'no'})
		(net ${p.to.index})
	)
	(segment
		(start ${p.eaxy(2.140166, -1.896)})
		(end ${p.eaxy(0.961166, -3.075)})
		(width ${p.trace_width})
    (locked ${p.locked_traces_vias ? 'yes' : 'no'})
		(layer "B.Cu")
		(net ${p.to.index})
	)
	(segment
		(start ${p.eaxy(6.421, -1.896)})
		(end ${p.eaxy(2.140166, -1.896)})
		(width ${p.trace_width})
    (locked ${p.locked_traces_vias ? 'yes' : 'no'})
		(layer "B.Cu")
		(net ${p.to.index})
	)
	(segment
		(start ${p.eaxy(0.961166, -3.075)})
		(end ${p.eaxy(0, -3.075)})
		(width ${p.trace_width})
    (locked ${p.locked_traces_vias ? 'yes' : 'no'})
		(layer "B.Cu")
		(net ${p.to.index})
	)
	(segment
		(start ${p.eaxy(8.275 - (2.6 - p.outer_pad_width_back) / 2, -3.75)})
		(end ${p.eaxy(6.421, -1.896)})
		(width ${p.trace_width})
    (locked ${p.locked_traces_vias ? 'yes' : 'no'})
		(layer "B.Cu")
		(net ${p.to.index})
	)
    `

    
    const hotswap_routes_same_side = `
  (segment
		(start ${p.eaxy(3.275, -5.95)})
		(end ${p.eaxy(7.775, -5.95)})
		(width ${p.trace_width})
    (locked ${p.locked_traces_vias ? 'yes' : 'no'})
		(layer "F.Cu")
		(net ${p.from.index})
	)
	(via
		(at ${p.eaxy(7.775, -5.95)})
		(size ${p.via_size})
    (drill ${p.via_drill})
		(layers "F.Cu" "B.Cu")
    (locked ${p.locked_traces_vias ? 'yes' : 'no'})
		(net ${p.from.index})
	)
	(segment
		(start ${p.eaxy(7.775, -3.75)})
		(end ${p.eaxy(7.775, -5.95)})
		(width ${p.trace_width})
    (locked ${p.locked_traces_vias ? 'yes' : 'no'})
		(layer "B.Cu")
		(net ${p.from.index})
	)
	(segment
		(start ${p.eaxy(-7.775, -3.75)})
		(end ${p.eaxy(-7.775, -5.95)})
		(width ${p.trace_width})
    (locked ${p.locked_traces_vias ? 'yes' : 'no'})
		(layer "F.Cu")
		(net ${p.to.index})
	)
	(via
		(at ${p.eaxy(-7.775, -5.95)})
		(size ${p.via_size})
    (drill ${p.via_drill})
		(layers "F.Cu" "B.Cu")
    (locked ${p.locked_traces_vias ? 'yes' : 'no'})
		(net ${p.to.index})
	)
	(segment
		(start ${p.eaxy(-3.275, -5.95)})
		(end ${p.eaxy(-7.775, -5.95)})
		(width ${p.trace_width})
    (locked ${p.locked_traces_vias ? 'yes' : 'no'})
		(layer "B.Cu")
		(net ${p.to.index})
	)
  ${p.outer_pad_width_back === 1.6 ? '' : `
  (segment
    (start ${p.eaxy(8.275 - (2.6 - p.outer_pad_width_back) / 2, -3.75)})
    (end ${p.eaxy(7.775, -3.75)})
    (width ${p.trace_width})
    (locked ${p.locked_traces_vias ? 'yes' : 'no'})
    (layer "B.Cu")
    (net ${p.from.index})
  )
  `}
  ${p.outer_pad_width_front === 1.6 ? '' : `
  (segment
    (start ${p.eaxy(-8.275 + (2.6 - p.outer_pad_width_front) / 2, -3.75)})
    (end ${p.eaxy(-7.775, -3.75)})
    (width ${p.trace_width})
    (locked ${p.locked_traces_vias ? 'yes' : 'no'})
    (layer "F.Cu")
    (net ${p.to.index})
  )
  `}
    `

    let final = common_top
    if (p.choc_v1_support) {
      final += choc_v1_stabilizers
    }
    if (p.include_corner_marks) {
      final += corner_marks;
    }
    if (p.include_keycap) {
      final += keycap_marks
    }
    if (p.include_stabilizer_pad && p.choc_v2_support) {
      if (p.reversible || p.side == "F") {
        if (p.oval_stabilizer_pad) {
          final += oval_corner_stab_front
        } else {
          final += round_corner_stab_front
        }
      }
      if (p.reversible || p.side == "B") {
        if (p.oval_stabilizer_pad) {
          final += oval_corner_stab_back
        } else {
          final += round_corner_stab_back
        }
      }
    }
    if (p.include_choc_v1_led_cutout_marks) {
      final += choc_v1_led_cutout_marks
    }
    if (p.include_choc_v2_led_cutout_marks) {
      final += choc_v2_led_cutout_marks
    }
    if (p.hotswap) {
      final += hotswap_common
      if (p.reversible || p.side == "F") {
        final += hotswap_front
      }
      if (p.reversible || p.side == "B") {
        final += hotswap_back
      }
      if (p.hotswap_3dmodel_filename) {
        final += hotswap_3dmodel
      }
    }
    if (p.solder) {
      final += solder_common
      if (p.reversible || p.side == "F") {
        final += solder_front
      }
      if (p.reversible || p.side == "B") {
        final += solder_back
      }
    }

    if (p.switch_3dmodel_filename) {
      final += switch_3dmodel
    }

    if (p.keycap_3dmodel_filename) {
      final += keycap_3dmodel
    }

    final += common_bottom

    if (p.reversible && p.hotswap && p.include_traces_vias && !p.include_plated_holes) {
      if(p.hotswap_pads_same_side){
        final += hotswap_routes_same_side
      } else {
        final += hotswap_routes_unplated
      }
    }

    return final;
  }
}
