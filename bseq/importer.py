import bpy
import meshio
import traceback
import fileseq
from .utils import show_message_box
import numpy as np
from mathutils import Matrix
# this import is not useless
import additional_file_formats


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
    show_message_box(cell.type + " is unsupported mesh format yet")
    return np.array([])


def update_mesh(meshio_mesh, mesh):
    # extract information from the meshio mesh
    mesh_vertices = meshio_mesh.points

    n_poly = 0
    n_loop = 0
    n_verts = len(mesh_vertices)

    faces_loop_start = np.array([], dtype=np.uint64)
    faces_loop_total = np.array([], dtype=np.uint64)
    loops_vert_idx = np.array([], dtype=np.uint64)
    shade_scheme = False
    if mesh.polygons:
        shade_scheme = mesh.polygons[0].use_smooth
    for cell in meshio_mesh.cells:
        data = extract_faces(cell)
        # np array can't be simply written as `if not data:`,
        if not data.any():
            continue
        n_poly += len(data)
        n_loop += data.shape[0] * data.shape[1]
        loops_vert_idx = np.append(loops_vert_idx, data.ravel())
        faces_loop_total = np.append(faces_loop_total, np.ones((len(data)), dtype=np.uint64) * data.shape[1])
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
        mesh.loops.add(n_loop)
        mesh.polygons.add(n_poly)

    mesh.vertices.foreach_set("co", mesh_vertices.ravel())
    mesh.loops.foreach_set("vertex_index", loops_vert_idx)
    mesh.polygons.foreach_set("loop_start", faces_loop_start)
    mesh.polygons.foreach_set("loop_total", faces_loop_total)
    mesh.polygons.foreach_set("use_smooth", [shade_scheme] * len(faces_loop_total))

    mesh.update()
    mesh.validate()

    #  copy attributes
    attributes = mesh.attributes
    for k, v in meshio_mesh.point_data.items():
        k = "bseq_" + k
        attribute = None
        if k not in attributes:
            if len(v.shape) == 1:
                # one dimensional attribute
                attribute = mesh.attributes.new(k, "FLOAT", "POINT")
            if len(v.shape) == 2:
                dim = v.shape[1]
                if dim > 3:
                    show_message_box('higher than 3 dimensional attribue, ignored')
                    continue
                if dim == 1:
                    attribute = mesh.attributes.new(k, "FLOAT", "POINT")
                if dim == 2:
                    attribute = mesh.attributes.new(k, "FLOAT2", "POINT")
                if dim == 3:
                    attribute = mesh.attributes.new(k, "FLOAT_VECTOR", "POINT")
            if len(v.shape) > 2:
                show_message_box('more than 2 dimensional tensor, ignored')
                continue
        else:
            attribute = attributes[k]
        name_string = None
        if attribute.data_type == "FLOAT":
            name_string = "value"
        else:
            name_string = 'vector'

        attribute.data.foreach_set(name_string, v.ravel())

        # set as split norm
        if mesh.BSEQ.split_norm_att_name and mesh.BSEQ.split_norm_att_name == k:
            mesh.use_auto_smooth = True
            mesh.normals_split_custom_set_from_vertices(v)


def create_obj(fileseq, use_relaitve, transform_matrix=Matrix([[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0, 1]])):

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

    #  create the object
    name = fileseq.basename() + "@" + fileseq.extension()
    mesh = bpy.data.meshes.new(name)
    object = bpy.data.objects.new(name, mesh)
    object.BSEQ.use_relative = use_relaitve
    if use_relaitve:
        object.BSEQ.pattern = bpy.path.relpath(str(fileseq))
    else:
        object.BSEQ.pattern = str(fileseq)
    object.BSEQ.init = True
    object.BSEQ.enabled = enabled
    object.matrix_world = transform_matrix
    if enabled:
        update_mesh(meshio_mesh, object.data)
    bpy.context.collection.objects.link(object)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = object


def update_obj(scene, depsgraph=None):
    # TODO if bpy in edit mode, then return

    current_frame = bpy.context.scene.frame_current

    for obj in bpy.data.objects:
        if obj.BSEQ.init == False:
            continue
        if obj.BSEQ.enabled == False:
            continue

        meshio_mesh = None
        pattern = obj.BSEQ.pattern
        if obj.BSEQ.use_relative:
            pattern = bpy.path.abspath(pattern)
        # in case the blender file was created on windows system, but opened in linux system
        pattern = bpy.path.native_pathsep(pattern)
        fs = fileseq.FileSequence(pattern)

        if obj.BSEQ.use_advance and obj.BSEQ.script_name:
            script = bpy.data.texts[obj.BSEQ.script_name]
            try:
                exec(script.as_string())
            except Exception as e:
                show_message_box(traceback.format_exc(), "running script: " + obj.BSEQ.script_name + " failed: " + str(e),
                                 "ERROR")
                continue

        if 'process' in locals():
            user_process = locals()['process']
            try:
                user_process(fs, current_frame, obj.data)
            except Exception as e:
                show_message_box("Error when calling user process: " + traceback.format_exc(), icon="ERROR")
            del locals()['process']
            # this continue means if process exist, all the remaining code will be ignored, whethere or not error occurs
            continue

        elif 'preprocess' in locals():
            user_preprocess = locals()['preprocess']
            try:
                meshio_mesh = user_preprocess(fs, current_frame)
            except Exception as e:
                show_message_box("Error when calling user preprocess: " + traceback.format_exc(), icon="ERROR")
                # this continue means only if error occures, then goes to next bpy.object
                continue
            finally:
                del locals()['preprocess']
        else:
            filepath = fs[current_frame % len(fs)]
            try:
                meshio_mesh = meshio.read(filepath)
            except Exception as e:
                show_message_box("Error when reading: " + filepath + ",\n" + traceback.format_exc(),
                                 "Meshio Loading Error" + str(e),
                                 icon="ERROR")
                continue

        if not isinstance(meshio_mesh, meshio.Mesh):
            show_message_box('function preprocess does not return meshio object', "ERROR")
            continue
        update_mesh(meshio_mesh, obj.data)
