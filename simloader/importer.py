import bpy
import meshio
import traceback
import fileseq
from .utils import show_message_box, reserved_word_check
import numpy as np
from mathutils import Matrix
import mzd

supported_mesh_format = [ 'triangle', 'quad']

def update_mesh(meshio_mesh, object):
    # extract information from the meshio mesh
    mesh = object.data
    mesh_vertices = meshio_mesh.points

    n_poly = 0
    n_loop = 0
    n_verts = len(mesh_vertices)

    faces_loop_start = np.array([], dtype=np.int32)
    faces_loop_total = np.array([], dtype=np.int32)
    loops_vert_idx = np.array([], dtype=np.int32)
    shade_scheme = False
    if mesh.polygons:
        shade_scheme = mesh.polygons[0].use_smooth
    for cell in meshio_mesh.cells:
        if cell.type not in supported_mesh_format:
            if cell.type!="vertex":
                show_message_box(cell.type + " is unsupported mesh format yet")
            continue
        data = cell.data
        n_poly += len(data)
        n_loop += data.shape[0] * data.shape[1]
        loops_vert_idx = np.append(loops_vert_idx, data.ravel())
        faces_loop_total = np.append(faces_loop_total, np.ones((len(data)), dtype=np.int32) * data.shape[1])
    if faces_loop_total.size>0:
        faces_loop_start = np.cumsum(faces_loop_total)
        # Add a zero as first entry
        faces_loop_start = np.roll(faces_loop_start, 1)
        faces_loop_start[0] = 0


    if  len(mesh.vertices) == n_verts and \
        len(mesh.polygons) == n_poly and \
        len(mesh.loops) == n_loop:
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
        k = reserved_word_check(k)
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
    object.SIMLOADER.use_relative = use_relaitve
    if use_relaitve:
        object.SIMLOADER.pattern = bpy.path.relpath(str(fileseq))
    else:
        object.SIMLOADER.pattern = str(fileseq)
    object.SIMLOADER.init = True
    object.SIMLOADER.enabled = enabled
    object.matrix_world = transform_matrix
    if enabled:
        update_mesh(meshio_mesh, object)
    bpy.context.collection.objects.link(object)


def update_obj(scene, depsgraph=None):
    # TODO if bpy in edit mode, then return

    current_frame = bpy.context.scene.frame_current

    for obj in bpy.data.objects:
        if obj.SIMLOADER.init == False:
            continue
        if obj.SIMLOADER.enabled == False:
            continue

        meshio_mesh = None
        pattern = obj.SIMLOADER.pattern
        if obj.SIMLOADER.use_relative:
            pattern = bpy.path.abspath(pattern)
        fs = fileseq.FileSequence(pattern)

        if obj.SIMLOADER.use_advance and obj.SIMLOADER.script_name:
            script = bpy.data.texts[obj.SIMLOADER.script_name]
            try:
                exec(script.as_string())
            except Exception as e:
                show_message_box(traceback.format_exc(), "running script: " + obj.SIMLOADER.script_name + " failed: " + str(e),
                                 "ERROR")
                continue
            if 'preprocess' not in locals():
                show_message_box('function preprocess not found', "ERROR")
                continue
            user_preprocess = locals()['preprocess']
            meshio_mesh = user_preprocess(fs, current_frame)
            if not isinstance(meshio_mesh, meshio.Mesh):
                show_message_box('function preprocess does not return meshio object', "ERROR")
                continue
        else:
            filepath = fs[current_frame % len(fs)]
            try:
                meshio_mesh = meshio.read(filepath)
            except Exception as e:
                show_message_box("Error when reading: " + filepath + ",\n" + traceback.format_exc(),
                                 "Meshio Loading Error" + str(e),
                                 icon="ERROR")
                continue
        update_mesh(meshio_mesh, obj)
