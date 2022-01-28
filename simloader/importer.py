import bpy
import meshio
import traceback
import fileseq
from .utils import show_message_box, reserved_word_check
import numpy as np
from mathutils import Matrix


def create_face_data(cells):
    #  TODO, extend this to 3d mesh
    if len(cells) > 1:
        show_message_box("Multi Structure mesh unsupported yet, use first cell only")

    return cells[0].type, cells[0].data


def update_mesh(meshio_mesh, object):
    # extrace information from the meshio mesh
    mesh = object.data
    mesh_vertices = meshio_mesh.points
    type, mesh_faces = create_face_data(meshio_mesh.cells)

    # assume the geometry node is the first modifier
    geometrynode = object.modifiers[0].node_group

    #  if is_pointcloud, can speed up a little bit, for later operations
    is_pointcloud = None

    if type == "triangle" or type == "quad":
        # connect directly to end node
        node1 = geometrynode.nodes[0]
        node2 = geometrynode.nodes[1]
        geometrynode.links.new(node1.outputs[0], node2.inputs[0])
        is_pointcloud = False
    elif type == "vertex":
        # connect via mesh on points node
        node1 = geometrynode.nodes[2]
        node2 = geometrynode.nodes[1]
        geometrynode.links.new(node1.outputs[0], node2.inputs[0])
        is_pointcloud = True
    else:
        #  if unknown, then show as point cloud only
        node1 = geometrynode.nodes[2]
        node2 = geometrynode.nodes[1]
        geometrynode.links.new(node1.outputs[0], node2.inputs[0])
        is_pointcloud = True
        show_message_box("unsupported mesh yet , will use point cloud to show vertices only")

    face_shape = mesh_faces.shape
    n_verts = len(mesh_vertices)
    npoly = face_shape[1]
    n_primitives = face_shape[0]

    # extrace information from the blender mesh
    shade_scheme = False
    if mesh.polygons:
        shade_scheme = mesh.polygons[0].use_smooth

    if not is_pointcloud and \
        len(mesh.vertices) == n_verts and \
        len(mesh.polygons) == n_primitives and \
        len(mesh.loops) == npoly * n_primitives:
        # the strucutre doesn't change, no need to add or remove vertices/ edges/  polygons, then directly go to next step
        # In theory, it could have a bug here, because it doesn't check the number of edges, but it's too hard to do that,
        # because edge data is not stored in files, it has to be calculated from mesh_face manually
        # So the problem is, if existing mesh has more edges than the next mesh, then these extra edges won't be removed,
        # It won't effect the rendered image, because edges won't be rendered
        # but it will look ugly in viewport, especially go into edit mode
        # this can happen only in a very rare case.
        pass
    elif is_pointcloud and len(mesh.vertices) == n_verts and len(mesh.polygons) ==0:
        # len(mesh.polygons)==0, to make sure it was pointcloud as well in the previous frame
        pass
    else:
        # since the structure has been changed, so delete it first, then create a new one
        # and reconstruct some other attributes here(if there are), e.g. uv maps, etc.
        mesh.clear_geometry()
        mesh.vertices.add(n_verts)
        mesh.loops.add(npoly * n_primitives)
        mesh.polygons.add(n_primitives)

    mesh.vertices.foreach_set("co", mesh_vertices.ravel())

    if not is_pointcloud:
        loops_vert_idx = mesh_faces.ravel()

        faces_loop_total = np.ones((len(mesh_faces)), dtype=np.int32) * npoly

        faces_loop_start = np.cumsum(faces_loop_total)
        # Add a zero as first entry
        faces_loop_start = np.roll(faces_loop_start, 1)
        faces_loop_start[0] = 0

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


def create_geometry_nodes(gn):
    #  currently only add an mesh to points node
    gn.nodes.new('GeometryNodeMeshToPoints')

    gn.links.new(gn.nodes[0].outputs[0], gn.nodes[2].inputs[0])


def create_obj(fileseq, pattern, use_relaitve, transform_matrix=Matrix([[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0,
                                                                                                                    1]])):

    current_frame = bpy.context.scene.frame_current
    filepath = fileseq[current_frame % len(fileseq)]

    meshio_mesh = None
    try:
        meshio_mesh = meshio.read(filepath)
    except Exception as e:
        show_message_box("Error when reading: " + filepath + ",\n" + traceback.format_exc(),
                         "Meshio Loading Error" + str(e),
                         icon="ERROR")
        return None

    #  create the object
    name = fileseq.basename() + "@" + fileseq.extension()
    mesh = bpy.data.meshes.new(name)
    object = bpy.data.objects.new(name, mesh)
    object.SIMLOADER.use_relative = use_relaitve
    object.SIMLOADER.pattern = pattern
    object.matrix_world = transform_matrix
    gn = object.modifiers.new("SIMLOADER_GeometryNodse", "NODES")
    create_geometry_nodes(gn.node_group)
    update_mesh(meshio_mesh, object)
    bpy.data.collections['SIMLOADER'].objects.link(object)


def update_obj(scene, depsgraph=None):
    # TODO if bpy in edit mode, then return

    current_frame = bpy.context.scene.frame_current

    for obj in bpy.data.collections['SIMLOADER'].objects:

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
