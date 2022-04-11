# This is the template specifically show how to load mzd files.
# For more information about mzd, you can find at https://github.com/InteractiveComputerGraphics/MayaMeshTools/tree/main/extern/mzd
# For general information about how to write template, please look at the template.py


import meshio
import fileseq
import bpy
import additional_file_formats
import numpy as np


# In general we suggest to directly use process for performance and compatibility reason, 
# meshio does not support face corner attributes
# However, if you want an easy way to modify the mesh, then meshio.mesh could be the choice

def process(fileseq: fileseq.FileSequence, frame_number: int, mesh:bpy.types.Mesh):
    frame_number = frame_number % len(fileseq)
    meshio_mesh = additional_file_formats.readMZD_to_meshio_with_split_norm(fileseq[frame_number])
    
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
        if k == 'normal':
            # mesh.vertices.foreach_set("normal", v.ravel())
            mesh.use_auto_smooth = True
            mesh.normals_split_custom_set_from_vertices(v)
            
            continue
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