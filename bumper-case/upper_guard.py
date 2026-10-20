import FreeCAD as App
import Part


V = App.Vector


def _box(x, y, z, dx, dy, dz):
    return Part.makeBox(dx, dy, dz, V(x, y, z))


def _cylinder(x, y, z, radius, height):
    return Part.makeCylinder(radius, height, V(x, y, z))


def _rounded(x, y, z, dx, dy, dz, radius):
    shape = _box(x, y, z, dx, dy, dz)
    edges = [edge for edge in shape.Edges if edge.BoundBox.ZLength > dz - 0.001]
    return shape.makeFillet(radius, edges)


def _sloping_end(x0, x1, y, depth, bottom, low, high):
    curve = Part.BezierCurve()
    span = x1 - x0
    curve.setPoles([V(x1, y, low), V(x1 - span * 0.35, y, low),
                    V(x0 + span * 0.35, y, high), V(x0, y, high)])
    edges = [Part.makeLine(V(x0, y, bottom), V(x1, y, bottom)),
             Part.makeLine(V(x1, y, bottom), V(x1, y, low)), curve.toShape(),
             Part.makeLine(V(x0, y, high), V(x0, y, bottom))]
    return Part.Face(Part.Wire(edges)).extrude(V(0, depth, 0))


def guard_mount_specs(parameters, reference):
    top = parameters['plate_top']
    return [dict(reference=mount['reference'], x=mount['x'], y=mount['y'],
                 flange_bottom=top, nut_seat=top + 0.4, nut_thickness=1.2, recess_radius=0.0,
                 flange_radius=2.6, screw_clearance=parameters['screw_clearance_diameter'])
            for mount in reference['footprints']
            if mount['reference'].startswith('H') and mount['x'] < parameters['seam_x']]


def guard_dimensions(parameters, reference):
    top = parameters.get('upper_guard_top', 10.9691)
    battery = parameters['upper_battery_envelope']
    roof_bottom = max(parameters['plate_top'], battery[2] + battery[5] + parameters.get('upper_battery_roof_clearance', 0.2))
    roof_top = roof_bottom + parameters.get('upper_battery_roof_thickness', 1.0)
    end_x = parameters['seam_x'] - parameters['seam_gap'] / 2
    return dict(mating_plane_mm=parameters['plate_top'], wall_top_mm=top,
                wall_mm=parameters['wall'], upright_rail_width_mm=0.0,
                internal_upright_walls=False,
                upright_exclusion_layout_bounds_mm=[0.0, 0.0, reference['width'], reference['height']],
                perimeter_drop_length_mm=12.0,
                perimeter_drop_start_x_mm=end_x - 12.0,
                perimeter_drop_end_x_mm=end_x,
                perimeter_drop_end_z_mm=parameters['plate_top'] + parameters['plate_thickness'],
                perimeter_drop_shape='Cubic Bezier with horizontal tangents at both ends',
                battery_roof_edge_fillet_mm=0.2,
                battery_roof_print_plane_offset_mm=roof_bottom - parameters['plate_top'],
                battery_roof_bridge_span_mm=11.7,
                battery_envelope_mm=battery,
                battery_roof_underside_mm=roof_bottom, battery_roof_top_mm=roof_top,
                battery_roof_thickness_mm=parameters.get('upper_battery_roof_thickness', 1.0),
                battery_clearance_mm=parameters.get('upper_battery_roof_clearance', 0.2),
                cap_sweep_clearance_mm=0.15,
                mount_flange_thickness_mm=0.4,
                switch_shoulder_aperture_mm=15.3,
                switch_shoulder_relief_top_mm=3.1,
                mounts=guard_mount_specs(parameters, reference),
                battery_cover='Continuous roof over the complete protected battery envelope; connector remains outside the roof.')


def build_upper_guard(parameters, reference, lower_left_shape):
    p, r = parameters, reference
    base = p['plate_top']
    top = p.get('upper_guard_top', 10.9691)
    wall = p['wall']
    extra = wall + p['layout_edge_offset']
    height = r['height']
    xmax = p['seam_x'] - p['seam_gap'] / 2
    thickness = p['plate_thickness']
    dimensions = guard_dimensions(p, r)
    battery = dimensions['battery_envelope_mm']
    roof_bottom = dimensions['battery_roof_underside_mm']
    roof_top = dimensions['battery_roof_top_mm']
    travel_bottom = p['cap_rest_underside'] - p['key_travel']
    if roof_top > travel_bottom - 0.2 + 0.00001:
        raise RuntimeError('Battery and continuous roof need at least 0.2 mm cap travel clearance')
    if battery[0] + battery[3] + 0.4 > 65.95:
        raise RuntimeError('Battery roof would obstruct the JST connector keepout')
    bottom = base - thickness
    blank = lower_left_shape.common(_box(-3, -3, bottom, xmax + 6, height + 6, thickness))
    blank.translate(V(0, 0, thickness))
    rim = _rounded(-extra, -extra, base, xmax + extra, height + 2 * extra, top - base, 1.5 + extra)
    inner_right = xmax - wall
    rim = rim.cut(_rounded(-p['layout_edge_offset'], -p['layout_edge_offset'], base - 0.1,
                          inner_right + p['layout_edge_offset'], height + 2 * p['layout_edge_offset'],
                          top - base + 0.2, 1.5 + p['layout_edge_offset']))
    rim = rim.cut(_rounded(0, 0, base - 0.1, r['width'], height, top - base + 0.2, 1.5))
    drop_start = xmax - 12.0
    full_height = _box(-extra - 0.1, -extra - 0.1, base - 0.1,
                       drop_start + extra + 0.1, height + 2 * extra + 0.2, top - base + 0.2)
    lowered_end = _sloping_end(drop_start, xmax, -extra - 0.1,
                               height + 2 * extra + 0.2, base - 0.1, base + thickness, top)
    rim = rim.common(full_height.fuse(lowered_end))
    shapes = [blank, rim]
    roof = _rounded(-extra, min(21.45, battery[1] - 0.4), roof_bottom,
                    battery[0] + battery[3] + 0.4 + extra,
                    max(33.55, battery[1] + battery[4] + 0.4) - min(21.45, battery[1] - 0.4),
                    roof_top - roof_bottom, 0.3)
    roof_edges = [edge for edge in roof.Edges
                  if abs(edge.BoundBox.ZMin - roof_top) < 0.00001
                  and abs(edge.BoundBox.ZMax - roof_top) < 0.00001]
    roof = roof.makeFillet(0.2, roof_edges)
    shapes.append(roof)
    guard = shapes[0].fuse(shapes[1:]).removeSplitter()
    guard = guard.cut(_box(p['cover_left'] - 0.2, p['cover_bottom'] - 0.2, base - 0.1,
                           xmax - p['cover_left'] + 1, p['cover_top_y'] - p['cover_bottom'] + 0.4,
                           top - base + 0.2))
    guard = guard.cut(_box(74.48, 20.95, base - 0.1, 3.0, 13.1, 9.2 - base + 0.1))
    for mount in guard_mount_specs(p, r):
        x, y = mount['x'], mount['y']
        guard = guard.cut(_cylinder(x, y, base - 1, mount['flange_radius'] - 0.1, top - base + 2))
        flange = _cylinder(x, y, mount['flange_bottom'], mount['flange_radius'], 0.4)
        guard = guard.fuse(flange)
        guard = guard.cut(_cylinder(x, y, base - 1, p['screw_clearance_diameter'] / 2, top - base + 2))
    for switch in r['footprints']:
        if not switch['reference'].startswith('S') or switch['x'] > p['seam_x']:
            continue
        s = p['switch_aperture']
        guard = guard.cut(_rounded(switch['x'] - s / 2, switch['y'] - s / 2,
                                  base - 1, s, s, 4.95 - base + 1, 0.15))
        shoulder = 15.3
        guard = guard.cut(_rounded(switch['x'] - shoulder / 2, switch['y'] - shoulder / 2,
                                  base - 0.1, shoulder, shoulder, 3.1 - base + 0.1, 0.15))
        cw, ch = (26.5, 16.5) if switch['rotation'] == 0 else (16.5, 26.5)
        guard = guard.cut(_box(switch['x'] - cw / 2 - 0.15, switch['y'] - ch / 2 - 0.15,
                               p['cap_rest_underside'] - p['key_travel'] - 0.2,
                               cw + 0.3, ch + 0.3, top + 1))
    guard = guard.removeSplitter()
    if not guard.isValid() or len(guard.Solids) != 1:
        raise RuntimeError('Upper guard must be one valid connected solid')
    return guard
