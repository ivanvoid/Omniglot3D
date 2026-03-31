# import cairosvg
import io
import os
import shapely
import trimesh
import trimesh
import trimesh
import numpy as np
import numpy as np
from PIL import Image
from skimage import measure
from shapely.ops import orient
from svgpathtools import svg2paths
from shapely.ops import unary_union
from shapely.geometry import Polygon
from trimesh.creation import extrude_polygon
# import matplotlib.pyplot as plt


def path_to_polygon(path):
    points = [(seg.start.real, seg.start.imag) for seg in path]
    if len(points) < 3:
        return None
    # Fix loop if needed
    if points[0] != points[-1]:
        points.append(points[0])
    polygon = Polygon(points)
    if not polygon.is_valid:
        polygon = polygon.buffer(0)  # fixes self-intersections
    return orient(polygon, sign=1.0)# CCW orientation

# def assign_holes(polygons):
#     used = set()
#     results = []

#     for i, outer in enumerate(polygons):
#         if i in used or outer.is_empty:continue
#         holes = []
#         for j, inner in enumerate(polygons):
#             if i == j or inner.is_empty:continue
#             if outer.contains(inner):
#                 holes.append(inner.exterior.coords)
#                 used.add(j)
#         results.append(Polygon(outer.exterior.coords, holes))
#     return results

def assign_holes(polygons):
    # Flatten MultiPolygons into Polygons
    flat = []
    for poly in polygons:
        if poly.is_empty:
            continue
        if poly.geom_type == "MultiPolygon":
            flat.extend(list(poly.geoms))
        elif poly.geom_type == "Polygon":
            flat.append(poly)

    results = []
    used = set()

    for i, outer in enumerate(flat):
        if i in used or outer.is_empty or outer.geom_type != "Polygon":
            continue

        holes = []
        for j, inner in enumerate(flat):
            if i == j or inner.is_empty or inner.geom_type != "Polygon":
                continue

            if outer.contains(inner):
                # Count nesting depth: how many polygons contain this inner?
                depth = sum(1 for k, p in enumerate(flat)
                            if k != j and p.contains(inner))

                if depth % 2 == 1:  
                    # odd depth = treat as hole
                    holes.append(inner.exterior.coords)
                    used.add(j)
                # even depth = solid island, don't add as hole

        results.append(Polygon(outer.exterior.coords, holes))

    return results


def svg2glb(svg_src, glb_dst):
    # Example: get path from SVG
    paths, attributes = svg2paths(svg_src)
    paths = sorted(paths, key=lambda x: len(x), reverse=True)
    # if "Alphabet_of_the_Magi/character12" in svg_src:
    # import pdb;pdb.set_trace()
    print(f'Number of path lines: {len(paths)}')
    polygons=[]
    meshes = []
    # Convert path to polygon points (approximate)
    for path in paths:
        poly = path_to_polygon(path)
        if poly.geom_type == "MultiPolygon":
            polygons.extend(list(poly.geoms))
        else:
            polygons.append(poly)
        # polygons.append(poly)  
    
    # assign holes
    polygons_with_holes = assign_holes(polygons)

    for poly in polygons_with_holes:
        if poly.geom_type == "Polygon":
            mesh = extrude_polygon(poly, height=10.0)
        elif poly.geom_type == "MultiPolygon":
            for poly in poly.geoms:
                mesh = extrude_polygon(poly, height=10.0)
        else:
            print(f'Error extrude: {poly}')
        mesh.vertex_normals = None
        trimesh.repair.fix_winding(mesh)
        trimesh.repair.broken_faces(mesh)
        trimesh.repair.fix_inversion(mesh)
        trimesh.repair.fix_normals(mesh)
        meshes+= [mesh]
    # holes_in_polygons = assign_holes(polygons)
    # print('Poly holes:',holes_in_polygons)

    combined_mesh = trimesh.util.concatenate(meshes)
    combined_mesh.rezero()# recenters mesh
    print("Face normals shape:", combined_mesh.face_normals.shape)
    print("Unique normals:", len(np.unique(combined_mesh.face_normals.round(4), axis=0)))
    # Export GLB
    combined_mesh.export(glb_dst)


# root = 'svgs'
root = "./processed_data/svgs"
glb_savedir = "./processed_data/broken_glbs"
import os
os.makedirs(glb_savedir, exist_ok=True)
language_paths = [os.path.join(root,path) for path in sorted(os.listdir(root))]
for lang_path in language_paths:
    letters_paths = [os.path.join(lang_path,path) for path in sorted(os.listdir(lang_path))]
    for l_path in letters_paths:
        save_dir = os.path.join(glb_savedir, '/'.join(l_path.split('/')[-2:]))
        os.makedirs(save_dir, exist_ok=True)
        file_names = os.listdir(l_path)
        for fn in file_names:
            src = os.path.join(l_path, fn)
            dst = os.path.join(save_dir, fn.replace('.svg', '.glb'))
            print(src)
            print(dst)
            print()
            svg2glb(src, dst)

exit()
















# import numpy as np
# from skimage import measure
# # import cairosvg
# from PIL import Image
# import io
# import os
# import trimesh
# from shapely.geometry import Polygon
# from shapely.ops import unary_union
# import trimesh
# from trimesh.creation import extrude_polygon
# from svgpathtools import svg2paths
# import trimesh
# from shapely.ops import orient
# import numpy as np
# import matplotlib.pyplot as plt
# def path_to_polygon(path):
#     points = [(seg.start.real, seg.start.imag) for seg in path]
#     if len(points) < 3:
#         return None
#     # Fix loop if needed
#     if points[0] != points[-1]:
#         points.append(points[0])
#     polygon = Polygon(points)
#     if not polygon.is_valid:
#         polygon = polygon.buffer(0)  # fixes self-intersections
#     return orient(polygon, sign=1.0)# CCW orientation
# def svg2glb(svg_src, glb_dst):
#     # Example: get path from SVG
#     paths, attributes = svg2paths(svg_src)
#     print(f'Number of path lines: {len(paths)}')
#     import pdb;pdb.set_trace()
#     polygons=[]
#     meshes = []
#     # Convert path to polygon points (approximate)
#     for path in paths:
#         poly = path_to_polygon(path)
#         # if poly is not None and not poly.is_empty:
#             # polygons.append(poly)
#         # points = [(seg.start.real, seg.start.imag) for seg in path]
#         # if points[0] != points[-1]:
#         #     points.append(points[0])
        
#         # polygon = Polygon(points)
#         # if not polygon.is_valid:
#         #     polygon = polygon.buffer(0)  # fixes self-intersections
#         # polygon = orient(polygon, sign=1.0)  # CCW orientation
#     # merged_polygon = unary_union(polygons)
#     import shapely
#     merged_polygon = shapely.ops.cascaded_union(polygons)
    
#     # plt.figure()
#     # if merged_polygon.geom_type == "Polygon":
#     #     plt.plot(merged_polygon.exterior.xy[0], merged_polygon.exterior.xy[1])
#     # elif merged_polygon.geom_type == "MultiPolygon":
#     #     for poly in merged_polygon.geoms:
#     #         plt.plot(poly.exterior.xy[0], poly.exterior.xy[1])
    
#     # plt.show()
#     # print(merged_polygon)
#     # exit()
#     if merged_polygon.geom_type == "Polygon":
#         mesh = extrude_polygon(merged_polygon, height=10.0)
#     elif merged_polygon.geom_type == "MultiPolygon":
#         for poly in merged_polygon.geoms:
#             mesh = extrude_polygon(poly, height=10.0)
#     else:
#         print(merged_polygon)
#     # mesh = extrude_polygon(merged_polygon, height=10.0)
#     mesh.vertex_normals = None
#     trimesh.repair.fix_winding(mesh)
#     trimesh.repair.broken_faces(mesh)
#     trimesh.repair.fix_inversion(mesh)
#     trimesh.repair.fix_normals(mesh)
#     meshes+= [mesh]
#     combined_mesh = trimesh.util.concatenate(meshes)
#     combined_mesh.rezero()# recenters mesh
#     print("Face normals shape:", combined_mesh.face_normals.shape)
#     print("Unique normals:", len(np.unique(combined_mesh.face_normals.round(4), axis=0)))
#     # Export GLB
#     # combined_mesh.export('0709_01.gltf')
#     mesh.export(glb_dst)
# root = 'svgs'
# glb_savedir = "broken_glbs"
# import os
# os.makedirs(glb_savedir, exist_ok=True)
# language_paths = [os.path.join(root,path) for path in sorted(os.listdir(root))]
# for lang_path in language_paths:
#     letters_paths = [os.path.join(lang_path,path) for path in sorted(os.listdir(lang_path))]
#     for l_path in letters_paths:
#         save_dir = os.path.join(glb_savedir, '/'.join(l_path.split('/')[-2:]))
#         os.makedirs(save_dir, exist_ok=True)
#         file_names = os.listdir(l_path)
#         for fn in file_names:
#             src = os.path.join(l_path, fn)
#             dst = os.path.join(save_dir, fn.replace('.svg', '.glb'))
#             print(src)
#             print(dst)
#             print()
#             svg2glb(src, dst)
# ##
# ## OLD CODE
# ##
# """
# def svg_to_3d_glb(path, output_glb_path, extrude_depth=20, png_size=105):
    
#     # Converts a 2D SVG into a 3D mesh (extruded along Z) and saves as GLB.
    
#     # Parameters:
#     #     svg_path: str, path to SVG file
#     #     output_glb_path: str, path to save GLB
#     #     extrude_depth: int, thickness in voxels
#     #     png_size: int, size of rasterized PNG for better resolution
    
#     # 1. Rasterize SVG to PNG in memory (square PNG)
#     # png_bytes = cairosvg.svg2png(url=svg_path, output_width=png_size, output_height=png_size)
#     img = Image.open(path).convert("L")
#     img = np.array(img)
    
#     # 2. Binarize
#     binary_mask = (img > 128).astype(np.uint8)
    
#     # 3. Create 3D volume by stacking along Z-axis
#     volume = np.stack([binary_mask]*extrude_depth, axis=-1)
    
#     # 4. Run marching cubes
#     verts, faces, normals, values = measure.marching_cubes(volume, level=0.2)
    
#     # 5. Create trimesh object
#     mesh_obj = trimesh.Trimesh(vertices=verts, faces=faces, vertex_normals=normals, process=True)
#     mesh_obj.export(output_glb_path)
#     # 6. Export to GLB
#     # mesh_obj.export(output_glb_path)
#     print(f"Saved 3D GLB to {output_glb_path}")
# # Example usage
# # pngs_folder = "pngs"
# # output_folder = "meshes_glb"
# # os.makedirs(output_folder, exist_ok=True)
# # for file in os.listdir(pngs_folder):
# #     if file.endswith(".png"):
# #         png_path = os.path.join(pngs_folder, file)
# #         glb_path = os.path.join(output_folder, file.replace(".png", ".glb"))
# #         svg_to_3d_glb(png_path, glb_path, extrude_depth=20, png_size=512)
# # file = '0709_01.png'
# # png_path = os.path.join(pngs_folder, file)
# # glb_path = os.path.join(output_folder, file.replace(".png", ".glb"))
# # svg_to_3d_glb(png_path, glb_path, extrude_depth=20, png_size=105)
# """