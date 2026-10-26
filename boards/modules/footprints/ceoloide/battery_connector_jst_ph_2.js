// Copyright (c) 2023 Marco Massarelli

// SPDX-License-Identifier: MIT



// Author: @ceoloide



















































module.exports = {
  params: {
    designator: 'JST',
    side: 'F',
    reversible: false,
    include_traces: true,
    use_rectangular_jumpers: false,
    trace_width: 0.250,
    include_silkscreen: true,
    include_fabrication: true,
    include_courtyard: true,
    battery_connector_3dmodel_filename: '',
    battery_connector_3dmodel_xyz_offset: [0, 0, 0],
    battery_connector_3dmodel_xyz_rotation: [0, 0, 0],
    battery_connector_3dmodel_xyz_scale: [1, 1, 1],
    BAT_P: { type: 'net', value: 'BAT_P' },
    BAT_N: { type: 'net', value: 'GND' },
  },
  body: p => {
    let local_nets = [
      p.local_net("1"),
      p.local_net("2"),
    ];

    const standard_opening = `
    (footprint "ceoloide:battery_connector_jst_ph_2"
        (layer "${p.side}.Cu")
        ${p.at}
        (property "Reference" "${p.ref}"
            (at 0 4.8 ${p.r})
            (layer "${p.side}.SilkS")
            ${p.ref_hide}
            (effects (font (size 1 1) (thickness 0.15)))
        )
        `
    const front_fabrication = `
        (fp_line (start -2.95 -1.35) (end -2.95 6.25) (stroke (width 0.1) (type solid)) (layer "F.Fab"))
        (fp_line (start -2.95 6.25) (end 2.95 6.25) (stroke (width 0.1) (type solid)) (layer "F.Fab"))
        (fp_line (start -2.25 -1.35) (end -2.95 -1.35) (stroke (width 0.1) (type solid)) (layer "F.Fab"))
        (fp_line (start -2.25 0.25) (end -2.25 -1.35) (stroke (width 0.1) (type solid)) (layer "F.Fab"))
        (fp_line (start 2.25 -1.35) (end 2.25 0.25) (stroke (width 0.1) (type solid)) (layer "F.Fab"))
        (fp_line (start 2.25 0.25) (end -2.25 0.25) (stroke (width 0.1) (type solid)) (layer "F.Fab"))
        (fp_line (start 2.95 -1.35) (end 2.25 -1.35) (stroke (width 0.1) (type solid)) (layer "F.Fab"))
        (fp_line (start 2.95 6.25) (end 2.95 -1.35) (stroke (width 0.1) (type solid)) (layer "F.Fab"))
        `
    const front_courtyard = `
        (fp_line (start -3.45 -1.85) (end -3.45 10.5) (stroke (width 0.05) (type solid)) (layer "F.CrtYd"))
        (fp_line (start -3.45 10.5) (end 3.45 10.5) (stroke (width 0.05) (type solid)) (layer "F.CrtYd"))
        (fp_line (start 3.45 -1.85) (end -3.45 -1.85) (stroke (width 0.05) (type solid)) (layer "F.CrtYd"))
        (fp_line (start 3.45 10.5) (end 3.45 -1.85) (stroke (width 0.05) (type solid)) (layer "F.CrtYd"))
        `
    const front_silkscreen = `
        (fp_line (start -1.5 7.40) (end -0.5 7.40) (stroke (width 0.1) (type solid)) (layer "F.SilkS"))
        (fp_line (start 1.5 7.40) (end 0.5 7.40) (stroke (width 0.1) (type solid)) (layer "F.SilkS"))
        (fp_line (start 1 6.90) (end 1 7.90) (stroke (width 0.1) (type solid)) (layer "F.SilkS"))
        (fp_line (start -2.06 -1.46) (end -3.06 -1.46) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
        (fp_line (start -3.06 -1.46) (end -3.06 -0.46) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
        (fp_line (start 2.14 -1.46) (end 3.06 -1.46) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
        (fp_line (start 3.06 -1.46) (end 3.06 -0.46) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
        (fp_line (start -2.14 6.36) (end -3.06 6.36) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
        (fp_line (start -3.06 6.36) (end -3.06 5.36) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
        (fp_line (start 2.14 6.36) (end 3.06 6.36) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
        (fp_line (start 3.06 6.36) (end 3.06 5.36) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
        `
    const back_fabrication = `
        (fp_line (start -2.95 -1.35) (end -2.25 -1.35) (stroke (width 0.1) (type solid)) (layer "B.Fab"))
        (fp_line (start -2.95 6.25) (end -2.95 -1.35) (stroke (width 0.1) (type solid)) (layer "B.Fab"))
        (fp_line (start -2.25 -1.35) (end -2.25 0.25) (stroke (width 0.1) (type solid)) (layer "B.Fab"))
        (fp_line (start -2.25 0.25) (end 2.25 0.25) (stroke (width 0.1) (type solid)) (layer "B.Fab"))
        (fp_line (start 2.25 -1.35) (end 2.95 -1.35) (stroke (width 0.1) (type solid)) (layer "B.Fab"))
        (fp_line (start 2.25 0.25) (end 2.25 -1.35) (stroke (width 0.1) (type solid)) (layer "B.Fab"))
        (fp_line (start 2.95 -1.35) (end 2.95 6.25) (stroke (width 0.1) (type solid)) (layer "B.Fab"))
        (fp_line (start 2.95 6.25) (end -2.95 6.25) (stroke (width 0.1) (type solid)) (layer "B.Fab"))
        `
    const back_courtyard = `
        (fp_line (start -3.45 -1.85) (end -3.45 10.5) (stroke (width 0.05) (type solid)) (layer "B.CrtYd"))
        (fp_line (start -3.45 10.5) (end 3.45 10.5) (stroke (width 0.05) (type solid)) (layer "B.CrtYd"))
        (fp_line (start 3.45 -1.85) (end -3.45 -1.85) (stroke (width 0.05) (type solid)) (layer "B.CrtYd"))
        (fp_line (start 3.45 10.5) (end 3.45 -1.85) (stroke (width 0.05) (type solid)) (layer "B.CrtYd"))
        `
    const back_silkscreen = `
        (fp_line (start 1.5 7.40) (end 0.5 7.40) (stroke (width 0.1) (type solid)) (layer "B.SilkS"))
        (fp_line (start -1.5 7.40) (end -0.5 7.40) (stroke (width 0.1) (type solid)) (layer "B.SilkS"))
        (fp_line (start -1 6.90) (end -1 7.90) (stroke (width 0.1) (type solid)) (layer "B.SilkS"))
        (fp_line (start -2.06 -1.46) (end -3.06 -1.46) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
        (fp_line (start -3.06 -1.46) (end -3.06 -0.46) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
        (fp_line (start 2.14 -1.46) (end 3.06 -1.46) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
        (fp_line (start 3.06 -1.46) (end 3.06 -0.46) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
        (fp_line (start -2.14 6.36) (end -3.06 6.36) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
        (fp_line (start -3.06 6.36) (end -3.06 5.36) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
        (fp_line (start 2.14 6.36) (end 3.06 6.36) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
        (fp_line (start 3.06 6.36) (end 3.06 5.36) (stroke (width 0.12) (type solid)) (layer "B.SilkS"))
        `
    const front_pads = `
        (pad "1" thru_hole roundrect (at -1 0 ${p.r}) (size 1.2 1.75) (drill 0.75) (layers "*.Cu" "*.Mask") (roundrect_rratio 0.20) ${p.BAT_N.str})
        (pad "2" thru_hole oval (at 1 0 ${p.r}) (size 1.2 1.75) (drill 0.75) (layers "*.Cu" "*.Mask") ${p.BAT_P.str})
        `
    const back_pads = `
        (pad "1" thru_hole roundrect (at 1 0 ${p.r}) (size 1.2 1.75) (drill 0.75) (layers "*.Cu" "*.Mask") (roundrect_rratio 0.20) ${p.BAT_N.str})
        (pad "2" thru_hole oval (at -1 0 ${p.r}) (size 1.2 1.75) (drill 0.75) (layers "*.Cu" "*.Mask") ${p.BAT_P.str})
        `
    const reversible_pads = `
        (pad "11" thru_hole oval (at -1 0 ${p.r}) (size 1.2 1.75) (drill 0.75) (layers "*.Cu" "*.Mask") ${local_nets[0].str})
        (pad "12" thru_hole oval (at 1 0 ${p.r}) (size 1.2 1.75) (drill 0.75) (layers "*.Cu" "*.Mask") ${local_nets[1].str})
        `
    const reversible_chevron_jumpers = `
        (pad "21" smd custom (at -1 1.8 ${180 + p.r}) (size 0.1 0.1) (layers "F.Cu" "F.Mask" "F.Paste")
            (clearance 0.1) (zone_connect 0)
            (options (clearance outline) (anchor rect))
            (primitives
                (gr_poly
                    (pts
                        (xy 0.6 0.4)
                        (xy -0.6 0.4)
                        (xy -0.6 0.2)
                        (xy 0 -0.4)
                        (xy 0.6 0.2)
                    )   
                    (width 0)
                    (fill yes)
                )
            )
            ${local_nets[0]}
        )
        (pad "31" smd custom (at -1 1.8 ${180 + p.r}) (size 0.1 0.1) (layers "B.Cu" "B.Mask" "B.Paste")
            (clearance 0.1) (zone_connect 0)
            (options (clearance outline) (anchor rect))
            (primitives
                (gr_poly
                    (pts
                        (xy 0.6 0.4)
                        (xy -0.6 0.4)
                        (xy -0.6 0.2)
                        (xy 0 -0.4)
                        (xy 0.6 0.2)
                    )
                    (width 0)
                    (fill yes)
                )
            )
            ${local_nets[0]}
        )
        (pad "22" smd custom (at 1 1.8 ${180 + p.r}) (size 0.1 0.1) (layers "F.Cu" "F.Mask" "F.Paste")
            (clearance 0.1) (zone_connect 0)
            (options (clearance outline) (anchor rect))
            (primitives
                (gr_poly
                    (pts
                        (xy 0.6 0.4)
                        (xy -0.6 0.4)
                        (xy -0.6 0.2)
                        (xy 0 -0.4)
                        (xy 0.6 0.2)
                    )
                    (width 0)
                    (fill yes)
                )
            )
            ${local_nets[1]}
        )
        (pad "32" smd custom (at 1 1.8 ${180 + p.r}) (size 0.1 0.1) (layers "B.Cu" "B.Mask" "B.Paste")
            (clearance 0.1) (zone_connect 0)
            (options (clearance outline) (anchor rect))
            (primitives
                (gr_poly
                    (pts
                        (xy 0.6 0.4)
                        (xy -0.6 0.4)
                        (xy -0.6 0.2)
                        (xy 0 -0.4)
                        (xy 0.6 0.2)
                    )
                    (width 0)
                    (fill yes)
                )
            )
            ${local_nets[1]}
        )
        (pad "1" smd custom (at -1 2.816 ${180 + p.r}) (size 1.2 0.5) (layers "F.Cu" "F.Mask" "F.Paste") ${p.BAT_P.str}
            (clearance 0.1) (zone_connect 0)
            (options (clearance outline) (anchor rect))
            (primitives
                (gr_poly
                    (pts
                        (xy 0.6 0)
                        (xy -0.6 0)
                        (xy -0.6 1)
                        (xy 0 0.4)
                        (xy 0.6 1)
                    )
                    (width 0)
                    (fill yes)
                )
            )
        )
        (pad "1" smd custom (at 1 2.816 ${180 + p.r}) (size 1.2 0.5) (layers "B.Cu" "B.Mask" "B.Paste") ${p.BAT_P.str}
            (clearance 0.1) (zone_connect 0)
            (options (clearance outline) (anchor rect))
            (primitives
                (gr_poly
                    (pts
                        (xy 0.6 0)
                        (xy -0.6 0)
                        (xy -0.6 1)
                        (xy 0 0.4)
                        (xy 0.6 1)
                    )
                    (width 0)
                    (fill yes)
                )
            )
        )
        (pad "2" smd custom (at -1 2.816 ${180 + p.r}) (size 1.2 0.5) (layers "B.Cu" "B.Mask" "B.Paste") ${p.BAT_N.str}
            (clearance 0.1) (zone_connect 0)
            (options (clearance outline) (anchor rect))
            (primitives
                (gr_poly
                    (pts
                        (xy 0.6 0)
                        (xy -0.6 0)
                        (xy -0.6 1)
                        (xy 0 0.4)
                        (xy 0.6 1)
                    )
                    (width 0)
                    (fill yes)
                )
            )
        )
        (pad "2" smd custom (at 1 2.816 ${180 + p.r}) (size 1.2 0.5) (layers "F.Cu" "F.Mask" "F.Paste") ${p.BAT_N.str}
            (clearance 0.1) (zone_connect 0)
            (options (clearance outline) (anchor rect))
            (primitives
                (gr_poly
                    (pts
                        (xy 0.6 0)
                        (xy -0.6 0)
                        (xy -0.6 1)
                        (xy 0 0.4)
                        (xy 0.6 1)
                    )
                    (width 0)
                    (fill yes)
                )
            ) 
        )
        `

    const reversible_rectangular_jumpers = `
        (pad "21" smd rect (at -1 1.8 ${90 + p.r}) (size 0.6 1.2) (layers "F.Cu" "F.Paste" "F.Mask") ${local_nets[0].str})
        (pad "31" smd rect (at -1 1.8 ${90 + p.r}) (size 0.6 1.2) (layers "B.Cu" "B.Paste" "B.Mask") ${local_nets[0].str})
        (pad "22" smd rect (at 1 1.8 ${90 + p.r}) (size 0.6 1.2) (layers "F.Cu" "F.Paste" "F.Mask") ${local_nets[1].str})
        (pad "32" smd rect (at 1 1.8 ${90 + p.r}) (size 0.6 1.2) (layers "B.Cu" "B.Paste" "B.Mask") ${local_nets[1].str})
        (pad "1" smd rect (at -1 2.7 ${90 + p.r}) (size 0.6 1.2) (layers "F.Cu" "F.Paste" "F.Mask") ${p.BAT_P.str})
        (pad "1" smd rect (at 1 2.7 ${90 + p.r}) (size 0.6 1.2) (layers "B.Cu" "B.Paste" "B.Mask") ${p.BAT_P.str})
        (pad "2" smd rect (at -1 2.7 ${90 + p.r}) (size 0.6 1.2) (layers "B.Cu" "B.Paste" "B.Mask") ${p.BAT_N.str})
        (pad "2" smd rect (at 1 2.7 ${90 + p.r}) (size 0.6 1.2) (layers "F.Cu" "F.Paste" "F.Mask") ${p.BAT_N.str})
        `

    const standard_closing = `
    )
        `

    const reversible_traces = ` 
    (segment (start ${p.eaxy(-1, 1.8)}) (end ${p.eaxy(-1, 0)}) (width ${p.trace_width}) (layer "F.Cu") (net ${local_nets[0].index}))
    (segment (start ${p.eaxy(-1, 1.8)}) (end ${p.eaxy(-1, 0)}) (width ${p.trace_width}) (layer "B.Cu") (net ${local_nets[0].index}))
    (segment (start ${p.eaxy(1, 1.8)}) (end ${p.eaxy(1, 0)}) (width ${p.trace_width}) (layer "F.Cu") (net ${local_nets[1].index}))
    (segment (start ${p.eaxy(1, 1.8)}) (end ${p.eaxy(1, 0)}) (width ${p.trace_width}) (layer "B.Cu") (net ${local_nets[1].index}))
        `

    const battery_connector_3dmodel = `
    (model ${p.battery_connector_3dmodel_filename}
      (offset (xyz ${p.battery_connector_3dmodel_xyz_offset[0]} ${p.battery_connector_3dmodel_xyz_offset[1]} ${p.battery_connector_3dmodel_xyz_offset[2]}))
      (scale (xyz ${p.battery_connector_3dmodel_xyz_scale[0]} ${p.battery_connector_3dmodel_xyz_scale[1]} ${p.battery_connector_3dmodel_xyz_scale[2]}))
      (rotate (xyz ${p.battery_connector_3dmodel_xyz_rotation[0]} ${p.battery_connector_3dmodel_xyz_rotation[1]} ${p.battery_connector_3dmodel_xyz_rotation[2]}))
    )
    `

    let final = standard_opening;

    if (p.side == "F" || p.reversible) {
      if (p.include_fabrication) {
        final += front_fabrication;
      }
      if (p.include_courtyard) {
        final += front_courtyard;
      }
      if (p.include_silkscreen) {
        final += front_silkscreen;
      }
    }
    if (p.side == "B" || p.reversible) {
      if (p.include_fabrication) {
        final += back_fabrication;
      }
      if (p.include_courtyard) {
        final += back_courtyard;
      }
      if (p.include_silkscreen) {
        final += back_silkscreen;
      }
    }
    if (p.reversible) {
      final += reversible_pads;
      if (p.use_rectangular_jumpers) {
        final += reversible_rectangular_jumpers;
      } else {
        final += reversible_chevron_jumpers;
      }
    } else if (p.side == "F") {
      final += front_pads;
    } else if (p.side == "B") {
      final += back_pads;
    }
    if (p.battery_connector_3dmodel_filename) {
      final += battery_connector_3dmodel
    }
    final += standard_closing;
    if (p.reversible && p.include_traces) {
      final += reversible_traces;
    }
    return final;
  }
}

