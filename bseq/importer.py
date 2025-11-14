import bpy
import mathutils
import meshio
import traceback
import fileseq
import os
from .utils import show_message_box, get_relative_path, get_absolute_path, load_meshio_from_path
import numpy as np
from mathutils import Matrix
import time
# this import is not useless
from .additional_file_formats import *
from typing import Optional

def extract_edges(cell: meshio.CellBlock):
    if cell.type == "line":
        return cell.data.astype(np.uint64)
    return np.array([])

def extract_faces(cell: meshio.CellBlock):
    if cell.type == "triangle":
        return cell.data.astype(np.uint64)
    elif cell.type == "triangle6":
        pass
    elif cell.type == "triangle7":
        pass
    elif cell.type == "quad":
        return cell.data.astype(np.uint64)
    elif cell.type == "quad8":
        pass
    elif cell.type == "quad9":
        pass
    elif cell.type == "tetra":
        data = cell.data.astype(np.uint64)
        faces = data[:, [0, 2, 1]]
        faces = np.append(faces, data[:, [0, 3, 2]], axis=0)
        faces = np.append(faces, data[:, [0, 1, 3]], axis=0)
        faces = np.append(faces, data[:, [1, 2, 3]], axis=0)
        faces_copy = np.copy(faces)
        faces_copy.sort(axis=1)
        _, indxs, count = np.unique(faces_copy, axis=0, return_index=True, return_counts=True)
        faces = faces[indxs[count == 1]]
        return faces
    elif cell.type == "hexahedron":
        data = cell.data.astype(np.uint64)
        faces = data[:, [0, 3, 2, 1]]
        faces = np.append(faces, data[:, [1, 5, 4, 0]], axis=0)
        faces = np.append(faces, data[:, [4, 5, 6, 7]], axis=0)
        faces = np.append(faces, data[:, [3, 7, 6, 2]], axis=0)
        faces = np.append(faces, data[:, [1, 2, 6, 5]], axis=0)
        faces = np.append(faces, data[:, [0, 4, 7, 3]], axis=0)
        faces_copy = np.copy(faces)
        faces_copy.sort(axis=1)
        _, indxs, count = np.unique(faces_copy, axis=0, return_index=True, return_counts=True)
        faces = faces[indxs[count == 1]]
        return faces
    elif cell.type == "vertex":
        return np.array([])
    elif cell.type == "line":
        return np.array([])
    show_message_box(cell.type + " is unsupported mesh format yet")
    return np.array([])

def has_keyframe(obj, attr):
    animdata = obj.animation_data
    if animdata is not None and animdata.action is not None:
        for fcurve in animdata.action.fcurves:
            if fcurve.data_path == attr:
                return len(fcurve.keyframe_points) > 0
    return False

def apply_transformation(meshio_mesh, obj, depsgraph):
    # evaluate the keyframe animation system
    eval_location = obj.evaluated_get(depsgraph).location if has_keyframe(obj, "location") else obj.location
    eval_scale = obj.evaluated_get(depsgraph).scale if has_keyframe(obj, "scale") else obj.scale

    if has_keyframe(obj, "rotation_quaternion"):
        eval_rotation = obj.evaluated_get(depsgraph).rotation_quaternion
    elif has_keyframe(obj, "rotation_axis_angle"):
        eval_rotation = obj.evaluated_get(depsgraph).rotation_axis_angle
    elif has_keyframe(obj, "rotation_euler"):
        eval_rotation = obj.evaluated_get(depsgraph).rotation_euler
    else:
        eval_rotation = obj.rotation_euler

    eval_transform_matrix = mathutils.Matrix.LocRotScale(eval_location, eval_rotation, eval_scale)

    # evaluate the rigid body transformations (only relevant for .bin format)
    rigid_body_transformation = mathutils.Matrix.Identity(4)
    if meshio_mesh is not None:
        if "transformation_matrix" in meshio_mesh.field_data:
            rigid_body_transformation = meshio_mesh.field_data["transformation_matrix"]

    # multiply everything together (with custom transform matrix)
    obj.matrix_world = rigid_body_transformation @ eval_transform_matrix

# function to create a single custom Blender mesh attribute
def create_or_retrieve_attribute(mesh, k, v):
    if k not in mesh.attributes:
        if len(v) == 0:
            return mesh.attributes.new(k, "FLOAT", "POINT")
        if len(v.shape) == 1:
            # one dimensional attribute
            return mesh.attributes.new(k, "FLOAT", "POINT")
        if len(v.shape) == 2:
            dim = v.shape[1]
            if dim > 3:
                # show_message_box('higher than 3 dimensional attribue, ignored')
                return None
            if dim == 1:
                return mesh.attributes.new(k, "FLOAT", "POINT")
            if dim == 2:
                return mesh.attributes.new(k, "FLOAT2", "POINT")
            if dim == 3:
                return mesh.attributes.new(k, "FLOAT_VECTOR", "POINT")
        if len(v.shape) > 2:
            # show_message_box('more than 2 dimensional tensor, ignored')
            return None
    else:
        return mesh.attributes[k]

def update_mesh(meshio_mesh, mesh):
    # extract information from the meshio mesh
    mesh_vertices = meshio_mesh.points

    n_poly = 0
    n_loop = 0
    n_verts = len(mesh_vertices)
    if n_verts == 0:
        mesh.clear_geometry()
        mesh.update()
        mesh.validate()
        return
    edges = np.array([], dtype=np.uint64)
    faces_loop_start = np.array([], dtype=np.uint64)
    faces_loop_total = np.array([], dtype=np.uint64)
    loops_vert_idx = np.array([], dtype=np.uint64)
    shade_scheme = False
    if mesh.polygons:
        shade_scheme = mesh.polygons[0].use_smooth

    for cell in meshio_mesh.cells:
        edge_data = extract_edges(cell)
        face_data = extract_faces(cell)

        if edge_data.any():
            edges = np.append(edges, edge_data)

        if face_data.any():
            n_poly += len(face_data)
            n_loop += face_data.shape[0] * face_data.shape[1]
            loops_vert_idx = np.append(loops_vert_idx, face_data.ravel())
            faces_loop_total = np.append(faces_loop_total, np.ones((len(face_data)), dtype=np.uint64) * face_data.shape[1])

    if faces_loop_total.size > 0:
        faces_loop_start = np.cumsum(faces_loop_total)
        # Add a zero as first entry
        faces_loop_start = np.roll(faces_loop_start, 1)
        faces_loop_start[0] = 0
    
    if len(mesh.vertices) == n_verts and len(mesh.polygons) == n_poly and len(mesh.loops) == n_loop:
        pass
    else:
        mesh.clear_geometry()
        mesh.vertices.add(n_verts)
        mesh.edges.add(len(edges))
        mesh.loops.add(n_loop)
        mesh.polygons.add(n_poly)

    mesh.vertices.foreach_set("co", mesh_vertices.ravel())
    mesh.edges.foreach_set("vertices", edges)
    mesh.loops.foreach_set("vertex_index", loops_vert_idx)
    mesh.polygons.foreach_set("loop_start", faces_loop_start)
    mesh.polygons.foreach_set("loop_total", faces_loop_total)
    mesh.polygons.foreach_set("use_smooth", [shade_scheme] * len(faces_loop_total))
    # newer function but is about 4 times slower
    # mesh.clear_geometry()
    # mesh.from_pydata(mesh_vertices, edge_data, face_data)

    mesh.update()
    mesh.validate()

    if bpy.context.scene.BSEQ.use_imported_normals:
        if "obj:vn" in meshio_mesh.point_data:
            mesh.BSEQ.split_norm_att_name = "bseq_obj:vn"
        elif "normals" in meshio_mesh.point_data and len(meshio_mesh.point_data["normals"]) == len(mesh.vertices):
            mesh.BSEQ.split_norm_att_name = "bseq_normals"
        elif "obj:vn" in meshio_mesh.field_data and "obj:vn_face_idx" in meshio_mesh.cell_data:
            mesh.BSEQ.split_norm_att_name = "obj:vn"

    #  copy attributes
    for k, v in meshio_mesh.point_data.items():
        k = "bseq_" + k
        attribute = create_or_retrieve_attribute(mesh, k, v)
        if attribute is None:
            
            continue
        name_string = None
        if attribute.data_type == "FLOAT":
            name_string = "value"
        else:
            name_string = 'vector'

        attribute.data.foreach_set(name_string, v.ravel())

        # set as split normal per vertex
        if mesh.BSEQ.split_norm_att_name and mesh.BSEQ.split_norm_att_name == k:
            # If blender version is greater than 4.1.0, then don't set auto smooth.
            # It has been removed and normals will be used automatically if they are set.
            # https://developer.blender.org/docs/release_notes/4.1/python_api/#mesh
            if bpy.app.version < (4, 1, 0):
                mesh.use_auto_smooth = True
            mesh.normals_split_custom_set_from_vertices(v)

    for k, v in meshio_mesh.field_data.items():
        if k not in mesh.attributes:
            attribute = create_or_retrieve_attribute(mesh, k, [])
        
        # set split normal per loop per vertex
        if mesh.BSEQ.split_norm_att_name and mesh.BSEQ.split_norm_att_name == k:
            if bpy.app.version < (4, 1, 0):
                mesh.use_auto_smooth = True
            # currently hard-coded for .obj files
            indices = [item for sublist in meshio_mesh.cell_data["obj:vn_face_idx"][0] for item in sublist]
            mesh.normals_split_custom_set([meshio_mesh.field_data["obj:vn"][i - 1] for i in indices])

# function to create a single meshio object (not a sequence, this just inports some file using meshio)
def create_meshio_obj(filepath):
    meshio_mesh = None
    try:
        meshio_mesh = meshio.read(filepath)
    except Exception as e:
        show_message_box("Error when reading: " + filepath + ",\n" + traceback.format_exc(),
                         "Meshio Loading Error" + str(e),
                         icon="ERROR")
        return
    #  create the object
    name = os.path.basename(filepath) 
    mesh = bpy.data.meshes.new(name)
    object = bpy.data.objects.new(name, mesh)
    update_mesh(meshio_mesh, object.data)
    bpy.context.collection.objects.link(object)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = object

def create_obj(fileseq, use_relative, root_path, transform_matrix=Matrix.Identity(4)):

    current_frame = bpy.context.scene.frame_current
    filepath = fileseq[current_frame % len(fileseq)]

    meshio_mesh = None
    enabled = True
    try:
        meshio_mesh = meshio.read(filepath)
    except Exception as e:
        show_message_box("Error when reading: " + filepath + ",\n" + traceback.format_exc(),
                        "Meshio Loading Error" + str(e),
                        icon="ERROR")
        enabled = False

    name = fileseq.basename() + "@" + fileseq.extension()
    mesh = bpy.data.meshes.new(name)
    object = bpy.data.objects.new(name, mesh)

    #  create the object
    full_path = str(fileseq)
    path = os.path.dirname(full_path)
    pattern = os.path.basename(full_path)
    if use_relative:
        path = get_relative_path(path, root_path)
    # path is only the directory in which the file is located
    object.BSEQ.path = path
    object.BSEQ.pattern = pattern
    object.BSEQ.current_file = filepath
    object.BSEQ.init = True
    object.BSEQ.enabled = enabled
    object.BSEQ.start_end_frame = (fileseq.start(), fileseq.end())
    object.matrix_world = transform_matrix
    driver = object.driver_add("BSEQ.frame")
    driver.driver.expression = 'frame'
    if enabled:
        update_mesh(meshio_mesh, object.data)
    bpy.context.collection.objects.link(object)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = object


def load_into_ram(obj, scene, depsgraph, *, target_frame = -1, filepath_buffer = None) -> Optional[meshio.Mesh]:
    if obj.BSEQ.init == False:
        return None
    if obj.BSEQ.enabled == False:
        return None
    if obj.mode != "OBJECT":
        return None

    if target_frame != -1:
        current_frame = target_frame
    elif depsgraph is not None:
        current_frame = obj.evaluated_get(depsgraph).BSEQ.frame
    else:
        show_message_box("Warning: Might not be able load the correct frame because the dependency graph is not available.", "BSEQ Warning")
        current_frame = obj.BSEQ.frame
    meshio_mesh = None
        
    # in case the blender file was created on windows system, but opened in linux system
    full_path = get_absolute_path(obj, scene)

    fs = fileseq.FileSequence(full_path)
     
    if obj.BSEQ.use_advance and obj.BSEQ.script_name:
        script = bpy.data.texts[obj.BSEQ.script_name]
        try:
            exec(script.as_string())
        except Exception as e:
            show_message_box(traceback.format_exc(), "running script: " + obj.BSEQ.script_name + " failed: " + str(e),
                             "ERROR")
            return meshio_mesh

    if 'process' in locals():
        user_process = locals()['process']
        try:
            user_process(fs, current_frame, obj.data)
            obj.BSEQ.current_file = "Controlled by user process"
        except Exception as e:
            show_message_box("Error when calling user process: " + traceback.format_exc(), icon="ERROR")
        del locals()['process']
        # this continue means if process exist, all the remaining code will be ignored, whethere or not error occurs
        return meshio_mesh

    elif 'preprocess' in locals():
        user_preprocess = locals()['preprocess']
        try:
            meshio_mesh = user_preprocess(fs, current_frame)
            obj.BSEQ.current_file = "Controlled by user preprocess"
        except Exception as e:
            show_message_box("Error when calling user preprocess: " + traceback.format_exc(), icon="ERROR")
            # this continue means only if error occures, then goes to next bpy.object
            return meshio_mesh
        finally:
            del locals()['preprocess']
    else:
        if obj.BSEQ.match_frames:
            fs_frames = fs.frameSet()
            if current_frame in fs_frames:
                filepath = fs[fs_frames.index(current_frame)]
                filepath = os.path.normpath(filepath)
                if filepath_buffer is not None:
                    # Since multithreaded writes to Blender properties may raise exceptions,
                    # we offload the update to current_file to the flush_buffer() function
                    # Passing None just disables the immediate update
                    meshio_mesh = load_meshio_from_path(fs, filepath, None)
                    filepath_buffer[obj.name_full] = filepath
                else:
                    meshio_mesh = load_meshio_from_path(fs, filepath, obj)
            else:
                meshio_mesh = meshio.Mesh([], [])
        else:
            filepath = fs[current_frame % len(fs)]
            filepath = os.path.normpath(filepath)
            if filepath_buffer is not None:
                # Since multithreaded writes to Blender properties may raise exceptions,
                # we offload the update to current_file to the flush_buffer() function
                # Passing None just disables the immediate update
                meshio_mesh = load_meshio_from_path(fs, filepath, None)
                filepath_buffer[obj.name_full] = filepath
            else:
                meshio_mesh = load_meshio_from_path(fs, filepath, obj)
    if not isinstance(meshio_mesh, meshio.Mesh):
        show_message_box('function preprocess does not return meshio object', "ERROR")
        return None
    
    return meshio_mesh

def update_scene(obj, meshio_mesh, scene, depsgraph):
    update_mesh(meshio_mesh, obj.data)

    apply_transformation(meshio_mesh, obj, depsgraph)

def update_obj(scene, depsgraph=None):
    for obj in bpy.data.objects:
        start_time = time.perf_counter()
        
        mesh = load_into_ram(obj, scene, depsgraph)
        if not isinstance(mesh, meshio.Mesh):
            continue
        update_scene(obj, mesh, scene, depsgraph)

        end_time = time.perf_counter()
        obj.BSEQ.last_benchmark = (end_time - start_time) * 1000
        # print("update_obj(): ", obj.BSEQ.last_benchmark)