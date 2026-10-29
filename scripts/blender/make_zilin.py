# 字靈大師：第一批 3D 樣品（勇者、音靈三段、形靈三段）
# 用法：blender -b --factory-startup --python scripts/blender/make_zilin.py -- <輸出資料夾>
# 每個模型輸出成一個 GLB，原點在腳底中央，面向 +Y（glTF 轉成 -Z 朝前…three.js 預設看 -Z，所以模型臉朝鏡頭方向 +Z 需要轉，見 export 前的旋轉）。
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

OUT = Path(sys.argv[sys.argv.index('--') + 1])
OUT.mkdir(parents=True, exist_ok=True)


# ---------- 共用工具 ----------
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def mat(name, color, metal=0.0, rough=0.55, emit=None, strength=0.0):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Metallic'].default_value = metal
    b.inputs['Roughness'].default_value = rough
    if emit:
        b.inputs['Emission Color'].default_value = (*emit, 1)
        b.inputs['Emission Strength'].default_value = strength
    return m


def hexc(h):
    h = h.lstrip('#')
    srgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb)


def link(obj, m, smooth=True):
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(m)
    for p in obj.data.polygons:
        p.use_smooth = smooth
    return obj


def sphere(name, loc, r, m, scale=(1, 1, 1), seg=24, rings=16, smooth=True):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=r)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = link(bpy.data.objects.new(name, me), m, smooth)
    o.location, o.scale = loc, scale
    return o


def ico(name, loc, r, m, scale=(1, 1, 1), sub=1):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = link(bpy.data.objects.new(name, me), m, False)
    o.location, o.scale = loc, scale
    return o


def cone(name, loc, r1, r2, h, m, rot=(0, 0, 0), seg=16, smooth=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r1, radius2=r2, depth=h)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = link(bpy.data.objects.new(name, me), m, smooth)
    o.location, o.rotation_euler = loc, rot
    return o


def torus(name, loc, R, r, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=32, minor_segments=8, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(m)
    for p in o.data.polygons:
        p.use_smooth = True
    return o


def lathe(name, prof, m, loc=(0, 0, 0), seg=32):
    """把 (半徑, 高度) 的輪廓繞 Z 軸旋轉成實體。"""
    bm = bmesh.new()
    rings = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        rings.append([bm.verts.new((r * math.cos(a), r * math.sin(a), z)) for r, z in prof])
    for i in range(seg):
        a, b = rings[i], rings[(i + 1) % seg]
        for k in range(len(prof) - 1):
            bm.faces.new((a[k], b[k], b[k + 1], a[k + 1]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = link(bpy.data.objects.new(name, me), m)
    o.location = loc
    return o


def eyes(z, x, y, r, white=None):
    """卡通大眼睛：黑眼珠＋白色反光。臉朝 -Y。"""
    black, shine = mat('EyeBlack', hexc('#1d1a2a'), rough=0.2), mat('EyeShine', (1, 1, 1), emit=(1, 1, 1), strength=1.5)
    for s in (-1, 1):
        if white:
            sphere(f'EyeW{s}', (s * x, y + r * 0.2, z), r * 1.25, white, scale=(1, 0.5, 1.2))
        sphere(f'Eye{s}', (s * x, y, z), r, black, scale=(1, 0.6, 1.25))
        sphere(f'Shine{s}', (s * x + r * 0.35, y - r * 0.5, z + r * 0.45), r * 0.32, shine)


def blush(z, x, y, r):
    m = mat('Blush', hexc('#ff8fa3'), rough=0.8)
    for s in (-1, 1):
        sphere(f'Blush{s}', (s * x, y, z), r, m, scale=(1, 0.35, 0.6))


def export(name):
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    # 腳底對齊 0、水平置中
    zs = [(o.matrix_world @ v.co).z for o in objs for v in o.data.vertices]
    for o in objs:
        o.location.z -= min(zs)
    tris = sum(len(p.vertices) - 2 for o in objs for p in o.data.polygons)
    # Blender 臉朝 -Y；glTF 匯出後 -Y 變成 +Z，正好面向 three.js 的預設鏡頭
    bpy.ops.export_scene.gltf(filepath=str(OUT / f'{name}.glb'), export_format='GLB', export_apply=True)
    print(f'MODEL {name}: {tris:,} tris')


# ---------- 勇者（字靈大師）：男生帥氣、女生漂亮；約 3.5 頭身 ----------
def face_eye(z, x, y, r, iris, lash=False, brow_tilt=0.0, hair_m=None):
    """較細緻的眼睛：眼白＋虹膜＋瞳孔＋兩點反光，可加睫毛與眉毛。臉朝 -Y。"""
    white = mat('EyeWhite', (1, 1, 1), rough=0.3)
    irm = mat('Iris' + iris, hexc(iris), rough=0.25)
    pupil = mat('EyeBlack', hexc('#1d1a2a'), rough=0.2)
    shine = mat('EyeShine', (1, 1, 1), emit=(1, 1, 1), strength=1.5)
    for s in (-1, 1):
        sphere(f'EyeW{s}', (s * x, y + r * 0.35, z), r * 1.05, white, scale=(1.0, 0.45, 1.25))
        sphere(f'Iris{s}', (s * x, y, z - r * 0.05), r * 0.78, irm, scale=(1, 0.5, 1.2))
        sphere(f'Pupil{s}', (s * x, y - r * 0.12, z - r * 0.05), r * 0.42, pupil, scale=(1, 0.5, 1.2))
        sphere(f'ShineA{s}', (s * x + r * 0.3, y - r * 0.3, z + r * 0.35), r * 0.24, shine)
        sphere(f'ShineB{s}', (s * x - r * 0.25, y - r * 0.3, z - r * 0.4), r * 0.12, shine)
        if hair_m:                                        # 眉毛
            b = sphere(f'Brow{s}', (s * x, y + r * 0.2, z + r * 1.75), r * 0.75, hair_m, scale=(1.3, 0.3, 0.22))
            b.rotation_euler = (0, s * brow_tilt, 0)
        if lash:                                          # 外眼角睫毛
            cone(f'Lash{s}', (s * (x + r * 0.95), y + r * 0.2, z + r * 0.9), r * 0.18, 0.0, r * 0.6, pupil,
                 rot=(0, s * 0.9, 0), seg=6)


def cape(name, z_top, z_bot, w_top, w_bot, m, back=0.17, nx=10, nz=8):
    """披風：從肩膀垂到背後，下襬外張、略微彎曲。"""
    bm = bmesh.new()
    grid = []
    for j in range(nz + 1):
        t = j / nz
        z = z_top + (z_bot - z_top) * t
        w = w_top + (w_bot - w_top) * t
        row = []
        for i in range(nx + 1):
            u = i / nx * 2 - 1
            y = back + 0.06 * t + 0.08 * (1 - u * u) * (0.4 + t)
            row.append(bm.verts.new((u * w, y, z)))
        grid.append(row)
    for j in range(nz):
        for i in range(nx):
            bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    m.use_backface_culling = False
    return link(bpy.data.objects.new(name, me), m)


def group(name, loc, rot, parts):
    g = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(g)
    for o in parts:
        o.parent = g
    g.location, g.rotation_euler = loc, rot
    return g


def hero(gender):
    reset()
    boy = gender == 'b'
    skin = mat('Skin', hexc('#ffdcc4'), rough=0.6)
    hair = mat('Hair', hexc('#3b2a22' if boy else '#4a2a5e'), rough=0.45)
    gold = mat('Gold', hexc('#ffcf4a'), metal=0.75, rough=0.3)
    glow = mat('Glow', hexc('#9fe8ff'), emit=hexc('#7fe0ff'), strength=3)
    mouth = mat('Mouth', hexc('#c95b5b'), rough=0.6)
    if boy:
        top, cloth2, capem = mat('Tunic', hexc('#2b5fa8'), rough=0.55), mat('Pants', hexc('#2a3348'), rough=0.7), mat('Cape', hexc('#c0392b'), rough=0.6)
        armor, boot = mat('Armor', hexc('#cfd8e6'), metal=0.7, rough=0.3), mat('Boot', hexc('#5a3520'), rough=0.55)
    else:
        top, cloth2, capem = mat('Bodice', hexc('#fbf7ff'), rough=0.6), mat('Skirt', hexc('#7b5cd6'), rough=0.55), mat('Cape', hexc('#b9a4f0'), rough=0.6)
        armor, boot = mat('Armor', hexc('#fff3fb'), metal=0.3, rough=0.4), mat('Boot', hexc('#f4f0ff'), rough=0.5)

    # 腳與腿
    for s in (-1, 1):
        sphere(f'Toe{s}', (s * 0.09, -0.04, 0.045), 0.065, boot, scale=(0.9, 1.4, 0.7))
        cone(f'BootShaft{s}', (s * 0.09, 0, 0.15), 0.06, 0.068, 0.2, boot)
        torus(f'BootCuff{s}', (s * 0.09, 0, 0.25), 0.068, 0.014, gold)
        cone(f'Leg{s}', (s * 0.09, 0, 0.37), 0.055, 0.062, 0.24, cloth2 if boy else skin)

    if boy:
        # 上衣下襬＋胸甲＋肩甲
        lathe('Tunic', [(0.0, 0.46), (0.21, 0.46), (0.19, 0.56), (0.17, 0.72), (0.19, 0.86), (0.12, 0.93), (0.0, 0.94)], top)
        sphere('Chest', (0, -0.06, 0.78), 0.17, armor, scale=(1.05, 0.75, 0.75))
        ico('ChestGem', (0, -0.19, 0.8), 0.028, glow)
        for s in (-1, 1):
            sphere(f'Pauldron{s}', (s * 0.2, 0, 0.88), 0.09, armor, scale=(1.1, 1.0, 0.7))
            torus(f'PauldronRim{s}', (s * 0.2, 0, 0.85), 0.085, 0.012, gold)
    else:
        # 連身裙：外張裙擺＋白色上身＋泡泡袖
        lathe('Dress', [(0.0, 0.38), (0.3, 0.38), (0.26, 0.48), (0.17, 0.62), (0.14, 0.66), (0.15, 0.8), (0.16, 0.88), (0.1, 0.94), (0.0, 0.95)], cloth2)
        lathe('Bodice', [(0.0, 0.64), (0.155, 0.64), (0.16, 0.8), (0.17, 0.88), (0.105, 0.945), (0.0, 0.955)], top)
        torus('Hem', (0, 0, 0.39), 0.295, 0.016, gold)
        sphere('Brooch', (0, -0.165, 0.84), 0.03, glow)
        for s in (-1, 1):
            sphere(f'Puff{s}', (s * 0.19, 0, 0.87), 0.075, top, scale=(1.1, 1.0, 0.85))
    torus('Belt', (0, 0, 0.6 if boy else 0.65), 0.18 if boy else 0.16, 0.018, gold)

    # 手臂與手
    for s in (-1, 1):
        cone(f'Arm{s}', (s * 0.24, 0, 0.73), 0.042, 0.05, 0.28, top, rot=(0, s * 0.18, 0))
        torus(f'Glove{s}', (s * 0.265, 0, 0.6), 0.045, 0.012, gold)
        sphere(f'Hand{s}', (s * 0.27, -0.01, 0.56), 0.045, skin)

    # 披風
    cape('Cape', 0.9, 0.3 if boy else 0.42, 0.2, 0.3 if boy else 0.26, capem)

    # 脖子、頭、臉
    cone('Neck', (0, 0, 0.97), 0.045, 0.045, 0.08, skin)
    sphere('Head', (0, 0, 1.15), 0.2, skin, scale=(0.95, 0.95, 1.05))
    sphere('Chin', (0, -0.06, 1.03), 0.11, skin, scale=(0.9, 0.9, 0.8))
    face_eye(1.13, 0.072, -0.178, 0.036, '#c9822b' if boy else '#8b5fd6', lash=not boy,
             brow_tilt=-0.25 if boy else 0.1, hair_m=hair)
    sphere('Mouth', (0, -0.185, 1.05), 0.02, mouth, scale=(1.3, 0.4, 0.45))
    if not boy:
        blush(1.08, 0.12, -0.17, 0.028)

    # 頭髮
    sphere('HairCap', (0, 0.025, 1.19), 0.212, hair, scale=(1.0, 1.0, 0.95))
    if boy:
        # 往後翹的刺蝟頭＋側分瀏海＋鬢角
        for i, (ax, az) in enumerate([(-0.5, 0.2), (-0.15, 0.35), (0.2, 0.3), (0.5, 0.15), (-0.3, -0.1), (0.3, -0.1), (0.0, 0.05)]):
            cone(f'Spike{i}', (math.sin(ax) * 0.14, 0.12, 1.28 + az * 0.15), 0.07, 0.0, 0.22, hair, rot=(-1.1 - az, ax * 0.6, 0), seg=6)
        for i, a in enumerate((-0.55, -0.2, 0.15)):
            cone(f'Bang{i}', (math.sin(a) * 0.15 + 0.02, -0.15, 1.28), 0.055, 0.0, 0.16, hair, rot=(2.4, 0, 0.6 + a * 0.5), seg=6)
        for s in (-1, 1):
            cone(f'Side{s}', (s * 0.18, -0.06, 1.12), 0.04, 0.0, 0.14, hair, rot=(math.pi, s * 0.3, 0), seg=6)
        # 背上的劍
        blade = mat('Blade', hexc('#e3ecf7'), metal=0.6, rough=0.2)
        group('BackSword', (0.05, 0.2, 0.62), (0, 0.6, 0), [
            cone('SwBlade', (0, 0, 0.32), 0.035, 0.012, 0.6, blade, seg=4, smooth=False),
            cone('SwGuard', (0, 0, 0.0), 0.1, 0.1, 0.03, gold, rot=(0, math.pi / 2, 0), seg=8),
            cone('SwGrip', (0, 0, -0.1), 0.02, 0.02, 0.16, mat('Grip', hexc('#4a2c12'))),
            sphere('SwPommel', (0, 0, -0.19), 0.03, gold)])
        # 左手拿發光字典
        book = mat('Book', hexc('#7a3fb0'), rough=0.5)
        bk = cone('Book', (-0.31, -0.07, 0.56), 0.08, 0.08, 0.04, book, rot=(1.2, 0, 0.3), seg=4, smooth=False)
        bk.scale = (1.2, 0.8, 1)
        ico('BookRune', (-0.33, -0.13, 0.61), 0.025, glow)
    else:
        # 長髮垂到腰、兩側長鬢、齊瀏海、大蝴蝶結、小皇冠
        sphere('BackHair', (0, 0.1, 0.95), 0.2, hair, scale=(1.05, 0.7, 1.55))
        for s in (-1, 1):
            cone(f'Lock{s}', (s * 0.17, -0.04, 0.98), 0.055, 0.03, 0.34, hair)
            sphere(f'LockEnd{s}', (s * 0.17, -0.04, 0.8), 0.035, hair)
        for i, a in enumerate((-0.6, -0.3, 0.0, 0.3, 0.6)):
            cone(f'Bang{i}', (math.sin(a) * 0.15, -0.15, 1.27), 0.05, 0.0, 0.13, hair, rot=(2.7, 0, a * 0.4), seg=6)
        ribbon = mat('Ribbon', hexc('#ff6fa8'), rough=0.5)
        for s in (-1, 1):
            cone(f'Bow{s}', (s * 0.08, 0.16, 1.3), 0.08, 0.02, 0.14, ribbon, rot=(0, s * math.pi / 2, 0.2 * s), seg=4)
        sphere('BowKnot', (0, 0.17, 1.3), 0.035, ribbon)
        torus('Tiara', (0, -0.02, 1.27), 0.17, 0.01, gold, rot=(0.35, 0, 0))
        ico('TiaraGem', (0, -0.18, 1.3), 0.025, glow)
        # 右手的大毛筆法杖
        group('BrushStaff', (0.29, -0.02, 0.62), (0.08, 0.08, 0), [
            cone('StaffShaft', (0, 0, 0.0), 0.018, 0.018, 0.95, mat('Bamboo', hexc('#c9a26b'), rough=0.6)),
            torus('StaffRing', (0, 0, 0.43), 0.024, 0.008, gold),
            cone('StaffHair', (0, 0, 0.55), 0.045, 0.0, 0.18, mat('InkBrush', hexc('#2b2a6b'), rough=0.4)),
            ico('StaffTip', (0, 0, 0.66), 0.03, glow)])
    export('hero-' + gender)


# ---------- 字靈共用：三段進化 ----------
def spirit_yin(stage):
    """音靈「鈴鈴」：鐘形身體的聲音精靈。stage 1 幼體、2 成長、3 完全體。"""
    reset()
    body = mat('YinBody', hexc(['#5fd3c6', '#38b6c9', '#2a8fd6'][stage - 1]), rough=0.45)
    belly = mat('YinBelly', hexc('#e9fffb'), rough=0.6)
    gold = mat('Gold', hexc('#ffcf4a'), metal=0.7, rough=0.3)
    note = mat('Note', hexc('#ffffff'), emit=hexc('#b9fff4'), strength=2.5)
    s = [0.8, 1.0, 1.15][stage - 1]
    # 鐘形身體
    lathe('Body', [(0.0, 0.0), (0.42 * s, 0.0), (0.44 * s, 0.06 * s), (0.36 * s, 0.25 * s), (0.3 * s, 0.5 * s),
                   (0.26 * s, 0.68 * s), (0.15 * s, 0.8 * s), (0.0, 0.83 * s)], body)
    sphere('Belly', (0, -0.2 * s, 0.25 * s), 0.22 * s, belly, scale=(1, 0.5, 0.9))
    torus('Rim', (0, 0, 0.04 * s), 0.43 * s, 0.035 * s, gold)
    eyes(0.55 * s, 0.11 * s, -0.25 * s, 0.06 * s, white=mat('EyeWhite', (1, 1, 1), rough=0.3))
    blush(0.45 * s, 0.2 * s, -0.22 * s, 0.05 * s)
    # 小腳
    for k in (-1, 1):
        sphere(f'Foot{k}', (k * 0.16 * s, -0.08 * s, 0.03), 0.08 * s, body, scale=(1, 1.3, 0.6))
    # 頭頂：音符觸角
    for k in (-1, 1):
        cone(f'Ant{k}', (k * 0.1 * s, 0, 0.9 * s), 0.015 * s, 0.012 * s, 0.18 * s, gold, rot=(0, k * 0.4, 0))
        sphere(f'AntBall{k}', (k * 0.15 * s, 0, 1.0 * s), 0.05 * s, note)
    if stage >= 2:                                        # 成長：兩側聲波耳鰭
        for k in (-1, 1):
            for j, rr in enumerate((0.12, 0.18, 0.24)):
                t = torus(f'Wave{k}{j}', (k * (0.33 + j * 0.05) * s, 0, 0.5 * s), rr * s, 0.016 * s, note, rot=(0, math.pi / 2, 0))
                t.scale = (1, 1, 0.5)
    if stage >= 3:                                        # 完全體：金鈴王冠＋環繞音環
        for i in range(5):
            a = 2 * math.pi * i / 5
            cone(f'Crown{i}', (math.cos(a) * 0.12 * s, math.sin(a) * 0.12 * s, 0.86 * s), 0.04 * s, 0.0, 0.14 * s, gold, seg=4)
        torus('Halo', (0, 0, 0.45 * s), 0.6 * s, 0.02 * s, note, rot=(0.25, 0, 0))
        for i in range(6):
            a = 2 * math.pi * i / 6
            ico(f'Orb{i}', (math.cos(a) * 0.6 * s, math.sin(a) * 0.6 * s * 0.97, 0.45 * s + math.sin(a) * 0.15 * s), 0.035 * s, note)
    export(f'yin-{stage}')


def spirit_xing(stage):
    """形靈「墨墨」：墨滴形狀的字形精靈，尾巴是毛筆。"""
    reset()
    ink = mat('Ink', hexc(['#4a4f8f', '#3a3f86', '#2b2a6b'][stage - 1]), rough=0.35)
    face = mat('InkFace', hexc('#f5efe0'), rough=0.7)
    brush = mat('Brush', hexc('#c9a26b'), rough=0.7)
    tip = mat('BrushTip', hexc('#1b1b24'), rough=0.6)
    red = mat('Seal', hexc('#d8322d'), rough=0.5)
    glow = mat('InkGlow', hexc('#ffe27a'), emit=hexc('#ffd24a'), strength=2.5)
    s = [0.8, 1.0, 1.15][stage - 1]
    # 墨滴身體（下圓上尖）
    lathe('Body', [(0.0, 0.0), (0.25 * s, 0.03 * s), (0.38 * s, 0.2 * s), (0.36 * s, 0.42 * s), (0.25 * s, 0.62 * s),
                   (0.12 * s, 0.8 * s), (0.0, 0.98 * s)], ink)
    sphere('Face', (0, -0.29 * s, 0.36 * s), 0.24 * s, face, scale=(1.05, 0.4, 0.85))
    eyes(0.4 * s, 0.1 * s, -0.375 * s, 0.055 * s)
    blush(0.31 * s, 0.17 * s, -0.36 * s, 0.045 * s)
    # 額頭朱印
    cone('SealMark', (0, -0.24 * s, 0.64 * s), 0.035 * s, 0.035 * s, 0.02 * s, red, rot=(math.pi / 2, 0, 0), seg=4, smooth=False)
    # 毛筆尾巴
    cone('BrushHandle', (0, 0.36 * s, 0.22 * s), 0.025 * s, 0.025 * s, 0.32 * s, brush, rot=(-1.0, 0, 0))
    cone('BrushHair', (0, 0.52 * s, 0.33 * s), 0.05 * s, 0.0, 0.16 * s, tip, rot=(-1.0, 0, 0))
    # 小手
    for k in (-1, 1):
        sphere(f'Hand{k}', (k * 0.36 * s, -0.05 * s, 0.25 * s), 0.065 * s, ink)
    if stage >= 2:                                        # 成長：兩支毛筆角
        for k in (-1, 1):
            cone(f'Horn{k}', (k * 0.12 * s, 0, 0.92 * s), 0.025 * s, 0.025 * s, 0.22 * s, brush, rot=(0, k * 0.5, 0))
            cone(f'HornTip{k}', (k * 0.19 * s, 0, 1.06 * s), 0.04 * s, 0.0, 0.12 * s, tip, rot=(0, k * 0.5, 0))
    if stage >= 3:                                        # 完全體：卷軸翅膀＋發光筆畫環
        paper = mat('Scroll', hexc('#fff3d0'), rough=0.8)
        for k in (-1, 1):
            w = cone(f'Wing{k}', (k * 0.42 * s, 0.15 * s, 0.6 * s), 0.13 * s, 0.13 * s, 0.025 * s, paper, rot=(math.pi / 2, k * 0.6, 0), seg=4, smooth=False)
            w.scale = (1.3, 1.3, 1)
            for e_ in (-1, 1):
                cone(f'Rod{k}{e_}', (k * 0.42 * s, 0.15 * s, 0.6 * s + e_ * 0.13 * s), 0.018 * s, 0.018 * s, 0.32 * s, brush, rot=(0, math.pi / 2, k * 0.6))
        torus('Stroke', (0, 0, 0.45 * s), 0.48 * s, 0.016 * s, glow, rot=(0.3, 0.2, 0))
    export(f'xing-{stage}')


if __name__ == '__main__':
    hero('b')
    hero('g')
    for st in (1, 2, 3):
        spirit_yin(st)
        spirit_xing(st)
