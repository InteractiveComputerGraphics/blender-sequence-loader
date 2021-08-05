import bpy
import meshio
import fileseq
import bmesh
import numpy as np
import bmesh
from mathutils import Matrix


class mesh_importer:
    def __init__(self, fileseq, transform_matrix=Matrix([[1, 0, 0,0], [0, 0, -1,0], [0, 1, 0,0],[0,0,0,1]]),mesh_name=None,obj_name=None,material_name=None):
        self.name = fileseq.basename()+"@"+fileseq.extension()
        self.fileseq = fileseq
        self.transform_matrix = transform_matrix
        self.mesh = None
        self.obj = None
        self.material = None
        self.v_col = None
        self.used_color_attribute = None
        if not mesh_name and not obj_name and not material_name:
            self.init_mesh()
        else:
            self.mesh= bpy.data.meshes[mesh_name]
            self.obj= bpy.data.objects[obj_name]
            # self.material = bpy.data.materials[material_name]

    def create_face_data(self, meshio_cells):
        # todo: support other mesh structure, such as tetrahedron
        return meshio_cells[0][1]

    def load_mesh(self, total_path):
        try:
            meshio_mesh = meshio.read(total_path)
        except Exception as e:
            show_message_box("meshio error when reading: "+total_path +
                             ",\n please check console for more details", icon="ERROR")
            logger.exception(e)
            return

        mesh_vertices = meshio_mesh.points
        vertices_count = len(meshio_mesh.points)
        mesh_faces = self.create_face_data(meshio_mesh.cells)
        shade_scheme = False
        if self.mesh.polygons:
            shade_scheme = self.mesh.polygons[0].use_smooth
        bm = bmesh.new()
        bm.from_mesh(self.mesh)
        bm.clear()
        bm.to_mesh(self.mesh)
        bm.free()

        self.mesh.vertices.add(vertices_count)

        # pos = meshio_mesh.points @ self.rotation

        self.mesh.vertices.foreach_set("co", meshio_mesh.points.ravel())

        # code from ply impoter of blender, https://github.com/blender/blender-addons/blob/master/io_mesh_ply/import_ply.py#L363
        # loops_vert_idx = []
        # faces_loop_start = []
        # faces_loop_total = []
        # lidx = 0
        # for f in mesh_faces:
        #     nbr_vidx = len(f)
        #     loops_vert_idx.extend(f)
        #     faces_loop_start.append(lidx)
        #     faces_loop_total.append(nbr_vidx)
        #     lidx += nbr_vidx

        # Check if there are any faces at all
        if len(mesh_faces) > 0:
            # Assume the same polygonal connectivity for all faces
            npoly = mesh_faces.shape[1]
            loops_vert_idx = mesh_faces.ravel()
            faces_loop_total = np.ones((len(mesh_faces)),dtype=np.int32) * npoly
            faces_loop_start = np.cumsum(faces_loop_total)

            # Add a zero as first entry
            faces_loop_start=np.roll(faces_loop_start, 1)

            if len(faces_loop_start) > 0:
                faces_loop_start[0] = 0

            self.mesh.loops.add(len(loops_vert_idx))
            self.mesh.polygons.add(len(mesh_faces))

            self.mesh.loops.foreach_set("vertex_index", loops_vert_idx)
            self.mesh.polygons.foreach_set("loop_start", faces_loop_start)
            self.mesh.polygons.foreach_set("loop_total", faces_loop_total)
            self.mesh.polygons.foreach_set(
                "use_smooth", [shade_scheme]*len(faces_loop_total))

        # Skip coloring the mesh for now
        #  it will be extended to real data
        # because everytime using bmesh.clear(), vertex color will be lost, and it has to be created again
        # v_col = self.mesh.vertex_colors.new()
        # mesh_colors = []
        # r_min = np.min(meshio_mesh.points[:, 0])
        # r_max = np.max(meshio_mesh.points[:, 0])
        # r_slope = 1/(r_max-r_min)
        # g_min = np.min(meshio_mesh.points[:, 1])
        # g_max = np.max(meshio_mesh.points[:, 1])
        # g_slope = 1/(g_max-g_min)
        # b_min = np.min(meshio_mesh.points[:, 2])
        # b_max = np.max(meshio_mesh.points[:, 2])
        # b_slope = 1/(b_max-b_min)
        # for index in mesh_faces:  # for each face
        #     for i in index:    # for each vertex in the face
        #         mesh_colors.append(
        #             r_slope*(meshio_mesh.points[i][0]-r_min))  # red color
        #         mesh_colors.append(
        #             g_slope * (meshio_mesh.points[i][1] - g_min))  # green color
        #         mesh_colors.append(
        #             b_slope*(meshio_mesh.points[i][2] - b_min))   # blue color

        # for i, col in enumerate(v_col.data):
        #     col.color = mesh_colors[i*3], 0, 0, 1

        self.mesh.update()
        self.mesh.validate()

    def init_mesh(self):

        self.mesh = bpy.data.meshes.new(name=self.name)
        # create vertex_color and material

        # self.material = bpy.data.materials.new(self.name+"_material")
        # self.material.use_nodes = True
        # nodes = self.material.node_tree.nodes
        # links = self.material.node_tree.links
        # nodes.clear()
        # links.clear()
        # output = nodes.new(type="ShaderNodeOutputMaterial")
        # diffuse = nodes.new(type="ShaderNodeBsdfDiffuse")
        # link = links.new(diffuse.outputs["BSDF"], output.inputs["Surface"])
        # vertex_color_node = nodes.new(type="ShaderNodeVertexColor")
        # link = links.new(
        #     vertex_color_node.outputs["Color"], diffuse.inputs["Color"])
        #  create object
        new_object = bpy.data.objects.new(self.name, self.mesh)
        bpy.data.collections[0].objects.link(new_object)
        self.obj = new_object
        self.obj.matrix_world = self.transform_matrix
        self.obj.active_material = self.material

        total_path = self.fileseq[0]
        self.load_mesh(total_path)

    def __call__(self, scene, depsgraph=None):
        frame_number = scene.frame_current
        frame_number = frame_number % len(self.fileseq)
        total_path = self.fileseq[frame_number]
        self.load_mesh(total_path)

    def get_color_attribute(self):
        return self.color_attribtues

    def set_color_attribute(self, attr_name):
        if attr_name and attr_name in self.color_attribtues:
            self.used_color_attribute = attr_name

    def clear(self):
        bpy.ops.object.select_all(action="DESELECT")
        if self.obj:
            self.obj.select_set(True)
            bpy.ops.object.delete()
            self.obj = None

        for m in bpy.data.meshes:
            if m.users == 0:
                bpy.data.meshes.remove(m)
        for m in bpy.data.materials:
            if m.users == 0:
                bpy.data.materials.remove(m)
        self.mesh = None

