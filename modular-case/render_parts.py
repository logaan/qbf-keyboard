from pathlib import Path
import math
import struct

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'generated'


def triangles(path):
    data = path.read_bytes()
    count = struct.unpack_from('<I', data, 80)[0]
    dtype = np.dtype([('normal', '<f4', (3,)), ('v', '<f4', (3, 3)), ('attr', '<u2')])
    return np.frombuffer(data, dtype=dtype, count=count, offset=84)['v'].astype(float)


def unit(vector):
    vector = np.array(vector, dtype=float)
    return vector / np.linalg.norm(vector)


def render(name, camera, items, print_layout=False):
    scale = 2
    width, height = 2000 * scale, 1100 * scale
    image = Image.new('RGB', (width, height), (242, 244, 246))
    view = unit(camera)
    right = unit(np.cross((0, 0, 1), view))
    up = unit(np.cross(view, right))
    combined, colors = [], []
    palette = {'tray':(31,87,102),'rim':(46,125,140),'cover':(219,120,48),'bridge':(230,135,54)}
    for part, offset, rotate in items:
        mesh = triangles(OUT / (part + ('_print.stl' if print_layout else '_assembly.stl')))
        if rotate:
            mesh[:, :, 0] = 98.5-mesh[:, :, 0]
            mesh[:, :, 1] = 96-mesh[:, :, 1]
        mesh += np.array(offset)
        combined.append(mesh)
        colors.extend([palette[part]] * len(mesh))
    vertices = np.concatenate(combined)
    colors = np.array(colors)
    flat = vertices.reshape(-1, 3)
    px = flat @ right
    py = flat @ up
    factor = min((width - 200 * scale) / np.ptp(px), (height - 200 * scale) / np.ptp(py))
    cx, cy = (px.min() + px.max()) / 2, (py.min() + py.max()) / 2
    projected = np.column_stack(((px - cx) * factor + width / 2, -(py - cy) * factor + height / 2)).reshape(-1, 3, 2)
    depths = vertices @ view
    normals = np.cross(vertices[:, 1] - vertices[:, 0], vertices[:, 2] - vertices[:, 0])
    lengths = np.linalg.norm(normals, axis=1)
    normals /= np.maximum(lengths, 1e-10)[:, None]
    light = unit(view + np.array((-0.3, -0.4, 1.4)))
    shade = 0.56 + 0.44 * np.maximum(0, normals @ light)
    pixels = np.array(image)
    zbuffer = np.full((height, width), -np.inf, dtype=np.float32)
    for i in range(len(vertices)):
        if np.dot(normals[i], view) < -0.001:
            continue
        tri = projected[i]
        x0 = max(0, math.floor(tri[:, 0].min()))
        x1 = min(width - 1, math.ceil(tri[:, 0].max()))
        y0 = max(0, math.floor(tri[:, 1].min()))
        y1 = min(height - 1, math.ceil(tri[:, 1].max()))
        a, b, c = tri
        den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(den) < 1e-8 or x1 < x0 or y1 < y0:
            continue
        xx, yy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        u = ((b[1] - c[1]) * (xx - c[0]) + (c[0] - b[0]) * (yy - c[1])) / den
        v = ((c[1] - a[1]) * (xx - c[0]) + (a[0] - c[0]) * (yy - c[1])) / den
        w = 1 - u - v
        depth = u * depths[i, 0] + v * depths[i, 1] + w * depths[i, 2]
        subz = zbuffer[y0:y1 + 1, x0:x1 + 1]
        mask = (u >= -1e-7) & (v >= -1e-7) & (w >= -1e-7) & (depth > subz)
        subz[mask] = depth[mask]
        pixels[y0:y1 + 1, x0:x1 + 1][mask] = (colors[i] * shade[i]).astype(np.uint8)
    image = Image.fromarray(pixels)
    image.resize((2000, 1100), Image.Resampling.LANCZOS).save(OUT / (name + '.png'))


def main():
    render('case_parts', (1,-1.6,1.7), [('tray',(0,0,0),False),('rim',(0,0,14),False),('cover',(0,0,35),False),('bridge',(30,0,-12),False)])
    render('bridge_underside', (1,-1.6,-2), [('tray',(0,0,0),False),('tray',(107.7,0,0),True),('bridge',(0,0,-6),False)])
    render('print_orientation', (.7,-1.5,2), [('tray',(0,0,0),False),('rim',(110,0,0),False),('cover',(0,75,0),False),('bridge',(130,85,0),False)], print_layout=True)
    print('Rendered exported case meshes and print orientations')


if __name__ == '__main__':
    main()
