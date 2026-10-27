# 在 Blender 背景執行：匯入模型 →（可選）減面 → 匯出 GLB。
# 由 scripts/blender.mjs 呼叫：blender -b --factory-startup --python prep.py -- <輸入> <輸出.glb> [目標三角面數]
import sys
from pathlib import Path

import bpy

args = sys.argv[sys.argv.index('--') + 1:]
src, dst = Path(args[0]), Path(args[1])
target = int(args[2]) if len(args) > 2 else 0

bpy.ops.wm.read_factory_settings(use_empty=True)

ext = src.suffix.lower()
if ext in ('.glb', '.gltf'):
    bpy.ops.import_scene.gltf(filepath=str(src))
elif ext == '.fbx':
    bpy.ops.import_scene.fbx(filepath=str(src))
elif ext == '.obj':
    bpy.ops.wm.obj_import(filepath=str(src))
elif ext == '.stl':
    bpy.ops.wm.stl_import(filepath=str(src))
else:
    sys.exit(f'不支援的格式：{ext}')

meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']


def tri_count():
    deps = bpy.context.evaluated_depsgraph_get()
    total = 0
    for o in meshes:
        m = o.evaluated_get(deps).to_mesh()
        total += sum(len(p.vertices) - 2 for p in m.polygons)
        o.evaluated_get(deps).to_mesh_clear()
    return total


before = tri_count()
if target and before > target:
    ratio = target / before
    for o in meshes:
        mod = o.modifiers.new('Decimate', 'DECIMATE')
        mod.decimate_type = 'COLLAPSE'
        mod.ratio = ratio
        mod.use_collapse_triangulate = True
after = tri_count()

dst.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.export_scene.gltf(filepath=str(dst), export_format='GLB', export_apply=True)
print(f'PREP_RESULT {src.name}: {before:,} → {after:,} 三角面，輸出 {dst}')
