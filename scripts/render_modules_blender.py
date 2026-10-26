import argparse
import json
import math
from pathlib import Path
import re
import sys

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--pair', nargs=2, type=int)
parser.add_argument('--module', type=int)
parser.add_argument('--view', choices=['angled', 'cap-free', 'underside'], default='angled')
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
settings = json.loads((ROOT / 'anime-render/scene.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.resolution_x = settings['image']['width']
scene.render.resolution_y = settings['image']['height']
scene.render.resolution_percentage = 100
scene.render.film_transparent = True
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.view_settings.view_transform = 'AgX'
scene.world = bpy.data.worlds.new('Soft study ambience')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.7, 0.77, 0.9, 1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.45
materials = {}
meshes = {}


def material(color, metallic=0):
    key = tuple(color), metallic
    if key not in materials:
        mat = bpy.data.materials.new('CAD material ' + str(key))
        mat.use_nodes = True
        shader = mat.node_tree.nodes.get('Principled BSDF')
        shader.inputs['Base Color'].default_value = (*color[:3], 1)
        shader.inputs['Roughness'].default_value = 0.42
        shader.inputs['Metallic'].default_value = metallic
        materials[key] = mat
    return materials[key]


def vrml_parts(relative, override):
    key = relative, tuple(override) if override else None
    if key in meshes:
        return meshes[key]
    source = (ROOT / relative).read_text()
    parts = []
    for block in source.split('Shape {')[1:]:
        color_match = re.search(r'diffuseColor\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)', block)
        vertices_match = re.search(r'point\s*\[([^]]+)\]', block)
        indices_match = re.search(r'coordIndex\s*\[([^]]+)\]', block)
        if not all((color_match, vertices_match, indices_match)):
            raise ValueError(f'Unsupported reference VRML geometry in {relative}')
        values = [float(v) for v in re.findall(r'[-+]?\d*\.?\d+(?:[Ee][-+]?\d+)?', vertices_match.group(1))]
        vertices = [tuple(values[j + i] * 0.00254 for i in range(3)) for j in range(0, len(values), 3)]
        indices = [int(v) for v in re.findall(r'-?\d+', indices_match.group(1))]
        faces, face = [], []
        for index in indices:
            if index == -1:
                if face:
                    faces.append(face)
                face = []
            else:
                face.append(index)
        color = override or [float(v) for v in color_match.groups()]
        mesh = bpy.data.meshes.new(Path(relative).stem)
        mesh.from_pydata(vertices, [], faces)
        mesh.update()
        mesh.materials.append(material(color))
        parts.append(mesh)
    if not parts:
        raise ValueError(f'No reference geometry in {relative}')
    meshes[key] = parts
    return parts


def add_module(number, center, top_z, hide_caps=False):
    folder = ROOT / 'anime-render/generated/native' / f'module{number}'
    previous = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(folder / 'board.glb'))
    imported = set(bpy.data.objects) - previous
    for obj in imported:
        if obj.parent is None:
            obj.location += Vector((center[0] / 1000, center[1] / 1000, (top_z - 1.6) / 1000))
    instances = json.loads((folder / 'components.json').read_text())['instances']
    for item in instances:
        if hide_caps and item['name'].endswith('_cap'):
            continue
        position = Vector(((item['position_mm'][0] + center[0]) / 1000,
                           (item['position_mm'][1] + center[1]) / 1000,
                           (item['position_mm'][2] + top_z) / 1000))
        if item['kind'] == 'vrml':
            parent = bpy.data.objects.new(f'module{number}_{item["name"]}', None)
            scene.collection.objects.link(parent)
            parent.location = position
            parent.rotation_euler = [math.radians(v) for v in item['rotation_degrees']]
            parent.scale = item['scale']
            for mesh in vrml_parts(item['source'], item.get('color')):
                obj = bpy.data.objects.new(item['name'], mesh)
                scene.collection.objects.link(obj)
                obj.parent = parent
        elif item['kind'] == 'box':
            bpy.ops.mesh.primitive_cube_add(size=1, location=position)
            obj = bpy.context.object
            obj.name = item['name']
            obj.dimensions = [v / 1000 for v in item['size_mm']]
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            bevel = obj.modifiers.new('Nominal edge radius', 'BEVEL')
            bevel.width = item.get('bevel_mm', 0.3) / 1000
            bevel.segments = 3
            obj.data.materials.append(material(item['color']))
        else:
            bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=item['radius_mm'] / 1000,
                                               depth=item['height_mm'] / 1000, location=position)
            bpy.context.object.name = item['name']
            bpy.context.object.data.materials.append(material(item['color'], 0.65))


camera = bpy.data.cameras.new('40 mm full-frame camera')
obj = bpy.data.objects.new('Camera', camera)
scene.collection.objects.link(obj)
scene.camera = obj
camera.lens = settings['camera']['lens_mm']
camera.sensor_width = settings['camera']['sensor_width_mm']
camera.sensor_height = settings['camera']['sensor_height_mm']
camera.sensor_fit = 'HORIZONTAL'
camera.clip_start = 0.001
camera.clip_end = 100
if args.pair:
    board = settings['board']
    add_module(args.pair[0], board['left_center_mm'], board['pcb_top_z_mm'])
    add_module(args.pair[1], board['right_center_mm'], board['pcb_top_z_mm'])
    position, target = settings['camera']['position_mm'], settings['camera']['target_mm']
    bpy.ops.mesh.primitive_plane_add(size=3, location=(0, 0, 0))
    bpy.context.object.is_shadow_catcher = True
    bpy.context.object.data.materials.append(material([0.55, 0.36, 0.2]))
else:
    add_module(args.module, [0, 0], 0, args.view == 'cap-free')
    position = [0, -125, -150] if args.view == 'underside' else [0, -125, 150]
    target = [0, 0, 0]
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 1000
obj.location = Vector(position) / 1000
obj.rotation_euler = (Vector(target) / 1000 - obj.location).to_track_quat('-Z', 'Y').to_euler()
light_spec = settings['light']
light = bpy.data.lights.new('Large warm desk light', 'AREA')
light.energy = light_spec['energy_watts']
light.color = light_spec['color']
light.shape = 'DISK'
light.size = light_spec['size_mm'] / 1000
lamp = bpy.data.objects.new('Desk lamp illumination', light)
scene.collection.objects.link(lamp)
lamp.location = Vector(light_spec['position_mm']) / 1000
lamp.rotation_euler = (-lamp.location).to_track_quat('-Z', 'Y').to_euler()
if args.view == 'underside' and not args.pair:
    lamp.location.z *= -1
    lamp.rotation_euler = (-lamp.location).to_track_quat('-Z', 'Y').to_euler()
args.output.parent.mkdir(parents=True, exist_ok=True)
scene.render.filepath = str(args.output)
bpy.ops.render.render(write_still=True)
