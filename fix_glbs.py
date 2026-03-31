import bpy
import os
import sys

# Clear default cube, light, camera
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)


def resave_glb(in_path, out_path):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    # Import GLB
    bpy.ops.import_scene.gltf(filepath=in_path)

    # Select all meshes and recalc normals if needed
    # for obj in bpy.context.scene.objects:
    #     if obj.type == 'MESH':
    #         bpy.context.view_layer.objects.active = obj
    #         bpy.ops.object.mode_set(mode='EDIT')
    #         bpy.ops.mesh.select_all(action='SELECT')
    #         bpy.ops.mesh.normals_make_consistent(inside=False)
    #         bpy.ops.object.mode_set(mode='OBJECT')

    # Export GLB with Blender's exporter
    bpy.ops.export_scene.gltf(
        filepath=out_path,
        export_format='GLB',
        export_apply=True
    )

    print(f"Re-exported {fn} → {out_path}")

# Change these paths to your folders
# INPUT_DIR = "./broken_glbs"
# OUTPUT_DIR = "./fixed_glbs"
INPUT_DIR = "./processed_data/broken_glbs"
OUTPUT_DIR = "./processed_data/fixed_glbs"
os.makedirs(OUTPUT_DIR, exist_ok=True)
language_paths = [os.path.join(INPUT_DIR,path) for path in sorted(os.listdir(INPUT_DIR))]
for lang_path in language_paths:
    letters_paths = [os.path.join(lang_path,path) for path in sorted(os.listdir(lang_path))]
    for l_path in letters_paths:
        save_dir = os.path.join(OUTPUT_DIR, '/'.join(l_path.split('/')[-2:]))
        os.makedirs(save_dir, exist_ok=True)
        file_names = sorted(os.listdir(l_path))
        for fn in file_names:
            if not fn.lower().endswith(".glb"):continue
            src = os.path.join(l_path, fn)
            dst = os.path.join(save_dir, fn)
            # print(src)
            # print(dst)
            # print()
            resave_glb(src, dst)







