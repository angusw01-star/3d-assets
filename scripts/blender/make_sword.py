# 程式產生「寶劍」：卡通風格、低面數，給孩子的遊戲當寶物。
# 用法：blender -b --factory-startup --python scripts/blender/make_sword.py -- <輸出.glb> [輸出.blend]
# 單位：公尺，劍尖朝 +Z（匯出 glTF 後變成 +Y 朝上），總長約 1 m。
import math
import sys
from pathlib import Path

import bmesh
import bpy

args = sys.argv[sys.argv.index('--') + 1:]
out_glb = Path(args[0])
out_blend = Path(args[1]) if len(args) > 1 else None

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


# ---- 材質 ----
def material(name, color, metallic=0.0, roughness=0.5, emission=None, strength=0.0):
    m = bpy.data.materials.new(name)
    bsdf = m.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    if emission:
        bsdf.inputs['Emission Color'].default_value = (*emission, 1)
        bsdf.inputs['Emission Strength'].default_value = strength
    return m


BLADE = material('Blade', (0.88, 0.93, 1.0), metallic=0.55, roughness=0.22)
GLOW = material('Glow', (0.3, 0.9, 1.0), roughness=0.3, emission=(0.3, 0.9, 1.0), strength=2.5)
GOLD = material('Gold', (1.0, 0.72, 0.18), metallic=1.0, roughness=0.25)
GRIP = material('Grip', (0.36, 0.16, 0.10), roughness=0.8)
RUBY = material('Ruby', (0.9, 0.05, 0.12), roughness=0.05, emission=(1.0, 0.1, 0.15), strength=0.6)
SAPPHIRE = material('Sapphire', (0.1, 0.35, 1.0), roughness=0.05, emission=(0.2, 0.5, 1.0), strength=0.6)


def new_object(name, mesh, mat, smooth=False):
    obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(obj)
    mesh.materials.append(mat)
    for p in mesh.polygons:
        p.use_smooth = smooth
    return obj


# ---- 劍身：六角形斷面沿 Z 放樣，寬度做成略帶葉形，最後收成劍尖 ----
def make_blade(length=0.68, base_w=0.048, thick=0.012, z0=0.0, mat=None, name='Blade'):
    bm = bmesh.new()
    rings, steps = [], 14
    for i in range(steps + 1):
        t = i / steps
        z = z0 + length * t * 0.86                     # 最後 14% 是劍尖
        w = base_w * (1 - 0.18 * t + 0.12 * math.sin(math.pi * t))
        th = thick * (1 - 0.3 * t)
        ring = [bm.verts.new(v) for v in (
            (-w, 0, z), (-w * 0.45, th, z), (w * 0.45, th, z),
            (w, 0, z), (w * 0.45, -th, z), (-w * 0.45, -th, z))]
        rings.append(ring)
    tip = bm.verts.new((0, 0, z0 + length))
    for a, b in zip(rings, rings[1:]):
        for k in range(6):
            bm.faces.new((a[k], a[(k + 1) % 6], b[(k + 1) % 6], b[k]))
    for k in range(6):
        bm.faces.new((rings[-1][k], rings[-1][(k + 1) % 6], tip))
    bm.faces.new(list(reversed(rings[0])))
    mesh = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    return new_object(name, mesh, mat or BLADE)


# ---- 護手：兩端往上翹的金色弧形，用曲線加斷面再轉成網格 ----
def make_guard(z=0.0):
    curve = bpy.data.curves.new('Guard', 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = 0.022
    curve.bevel_resolution = 2
    curve.resolution_u = 8
    spline = curve.splines.new('BEZIER')
    pts = [(-0.17, 0, z + 0.06), (0, 0, z - 0.012), (0.17, 0, z + 0.06)]
    spline.bezier_points.add(len(pts) - 1)
    for bp, co in zip(spline.bezier_points, pts):
        bp.co = co
        bp.handle_left_type = bp.handle_right_type = 'AUTO'
    spline.bezier_points[0].radius = spline.bezier_points[-1].radius = 0.55
    spline.bezier_points[1].radius = 1.4
    obj = bpy.data.objects.new('Guard', curve)
    scene.collection.objects.link(obj)
    curve.materials.append(GOLD)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    obj.select_set(False)
    for p in obj.data.polygons:
        p.use_smooth = True
    # 兩端的金球
    for x in (-0.175, 0.175):
        add_sphere(f'GuardEnd{"L" if x < 0 else "R"}', (x, 0, z + 0.068), 0.022, GOLD)
    return obj


def add_sphere(name, loc, r, mat, faceted=False, scale=(1, 1, 1)):
    bm = bmesh.new()
    if faceted:
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    else:
        bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=10, radius=r)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = new_object(name, mesh, mat, smooth=not faceted)
    obj.location = loc
    obj.scale = scale
    return obj


def add_cylinder(name, z_bottom, height, r, mat, segs=16):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=r, radius2=r, depth=height)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = new_object(name, mesh, mat, smooth=True)
    obj.location = (0, 0, z_bottom + height / 2)
    return obj


def add_torus(name, z, major, minor, mat):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                     major_segments=16, minor_segments=6, location=(0, 0, z))
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


# ---- 組裝 ----
GUARD_Z = 0.0
make_blade(z0=GUARD_Z + 0.01)
# 劍身中央發光的符文槽：較窄、略厚的同形狀，從兩面的稜線透出來
make_blade(length=0.5, base_w=0.011, thick=0.0145, z0=GUARD_Z + 0.04, mat=GLOW, name='Glow')
make_guard(GUARD_Z)
# 護手中央的紅寶石（前後各一顆，切面風格）
for y in (-0.02, 0.02):
    add_sphere(f'Ruby{"F" if y < 0 else "B"}', (0, y, GUARD_Z + 0.004), 0.034, RUBY, faceted=True, scale=(1, 0.5, 1.15))
# 握把與纏繩
add_cylinder('Grip', GUARD_Z - 0.19, 0.19, 0.017, GRIP)
for i in range(5):
    add_torus(f'Wrap{i}', GUARD_Z - 0.03 - i * 0.034, 0.018, 0.0045, GOLD)
# 劍柄末端：金球＋藍寶石
add_sphere('Pommel', (0, 0, GUARD_Z - 0.215), 0.032, GOLD)
for y in (-0.028, 0.028):
    add_sphere(f'Sapphire{"F" if y < 0 else "B"}', (0, y, GUARD_Z - 0.215), 0.014, SAPPHIRE, faceted=True, scale=(1, 0.5, 1))

# 讓整把劍以中心為原點（方便遊戲裡旋轉、漂浮）
objs = [o for o in scene.objects if o.type == 'MESH']
zs = [(o.matrix_world @ v.co).z for o in objs for v in o.data.vertices]
mid = (max(zs) + min(zs)) / 2
for o in objs:
    o.location.z -= mid

tris = sum(len(p.vertices) - 2 for o in objs for p in o.data.polygons)
out_glb.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.export_scene.gltf(filepath=str(out_glb), export_format='GLB', export_apply=True)
if out_blend:
    out_blend.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out_blend))
print(f'SWORD_RESULT {len(objs)} 個物件，{tris:,} 三角面，輸出 {out_glb}')
