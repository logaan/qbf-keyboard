from pathlib import Path
import argparse
import html
import json

import pcbnew as pcb


def position(point):
    return pcb.ToMM(point.x), pcb.ToMM(point.y)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    board = pcb.LoadBoard(str(args.output / 'pcbs/macropad.kicad_pcb'))
    geometry = json.loads((args.output / 'board_geometry.json').read_text())
    edges = [position(point) for drawing in board.GetDrawings() if drawing.GetLayer() == pcb.Edge_Cuts
             for point in (drawing.GetStart(), drawing.GetEnd())]
    left, top = min(x for x, y in edges), min(y for x, y in edges)
    width, height = geometry['width'], geometry['height']
    items = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="1300" viewBox="-7 -8 {width + 14} {height + 45}">',
             '<rect x="-7" y="-8" width="150" height="110" fill="white"/>',
             '<g font-family="Helvetica" fill="#253448">']
    def rectangle(x, y, w, h, fill, stroke, radius=0.5, dash=''):
        items.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="0.15" stroke-dasharray="{dash}"/>')
    def label(x, y, text, size=2, anchor='middle', color='#253448'):
        items.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" fill="{color}">{html.escape(text)}</text>')
    rectangle(0, 0, width, height, '#ffffff', '#83909e', 1.5)
    label(width / 2, -3.5, f'QBF · {width:g} × {height:g} mm', 2.7)
    switches = [footprint for footprint in board.GetFootprints() if footprint.GetReference().startswith('S')]
    xs = sorted({round(position(footprint.GetPosition())[0], 3) for footprint in switches})
    for footprint in switches:
        x, y = position(footprint.GetPosition())
        x, y = x - left, y - top
        cap_height = 17.5 if footprint.GetValue() == 'Choc v1 1U' else 26.5
        rectangle(x - 8.25, y - cap_height / 2, 16.5, cap_height, '#f4f6f9', '#8594a5')
        rectangle(x - 7, y - 7, 14, 14, 'none', '#d5dde5', 0)
        row = 't' if y < height / 2 else 'b'
        column = xs.index(round(x + left, 3)) + 1
        label(x, y + 0.7, f'{row}{column}', 3)
        label(x, y + 3.6, '1U' if cap_height == 17.5 else '1.5U', 1.7, color='#788697')
    for footprint in board.GetFootprints():
        x, y = position(footprint.GetPosition())
        x, y = x - left, y - top
        if footprint.GetReference().startswith('MCU'):
            rectangle(x - 10.5, y - 8.9, 21, 17.8, '#eef0f3', '#a4adb7', dash='0.7 0.5')
        if footprint.GetReference().startswith('H'):
            items.append(f'<circle cx="{x}" cy="{y}" r="1.1" fill="white" stroke="#bf7b22" stroke-width="0.25"/>')
    display = geometry['display']
    dx, dy = display['x'], height - display['y']
    rectangle(dx - 12.75, dy - 9, 25.5, 18, '#dceaf5', '#427fba')
    rectangle(dx - 12.005, dy - 6.2275, 24.01, 12.455, '#e9f4f2', '#689593', 0)
    rectangle(dx - 10.605, dy - 4.8276, 19.3104, 9.6552, '#d1e6de', '#689593', 0)
    label(dx - 0.8, dy - 0.2, 'JDI memory LCD', 1.65)
    label(dx - 0.8, dy + 2.4, '144 × 72 · no backlight', 1.2)
    label(width / 2, height + 4.5, '1 mm between the 1.5U rows · aligned outer cap edges · internal M2 holes', 1.8)
    base_y = height + 23
    side_x = width / 2 - 28
    rectangle(side_x, base_y, 34, 1.6, '#7a9b86', '#547d61', 0)
    rectangle(side_x + 3, base_y - 6.8, 21, 6.8, '#d7dce3', '#9aa6b4', 0)
    rectangle(side_x, base_y - 8.8, 25.5, 0.8, '#c4daeb', '#427fba', 0)
    rectangle(side_x + 0.745, base_y - 9.744, 24.01, 0.944, '#d1e6de', '#689593', 0)
    label(side_x - 3, base_y - 4, 'Side view', 1.8, 'end')
    label(side_x + 37, base_y - 8.8, 'Display on 0.8 mm adapter', 1.5, 'start')
    label(side_x + 37, base_y - 5, 'Socketed XIAO Plus below', 1.5, 'start')
    label(side_x + 37, base_y - 1.2, '8 mm to adapter underside', 1.5, 'start')
    label(width / 2, height + 29, 'Placement drawing · stack and ribbon fit require a physical prototype', 1.55, color='#788697')
    items.append('</g></svg>')
    (args.output / 'layout.svg').write_text('\n'.join(items))


if __name__ == '__main__':
    main()
