import bpy
import meshio
import fileseq
import bmesh
import numpy as np
import bmesh
from mathutils import Matrix
import traceback
from .utils import *


class mesh_importer:
    def __init__(self, fileseq, transform_matrix=Matrix([[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0, 1]]), mesh_name=None):
        self.name = fileseq.basename()+"@"+fileseq.extension() 
        self.fileseq = fileseq
        self.transform_matrix = transform_matrix
        self.render_attributes = []  # all the possible attributes, and type
        self.used_render_attribute = None  # the attribute used for rendering
        self.start = 0
        self.end = 500
        self.min_value = 0
        self.max_value = 100
        self.mesh_name = None
        if not mesh_name:
            self.init_mesh()
        else:
            self.mesh_name = mesh_name

    def create_face_data(self, meshio_cells):
        # todo: support other mesh structure, such as tetrahedron
        return meshio_cells[0][1]

    def load_mesh(self, total_path):
        '''
        load the mesh in each frame
        '''
        try:
            meshio_mesh = meshio.read(total_path)
        except Exception as e:
            show_message_box("meshio error when reading: "+total_path +
                             ",\n please check console for more details", icon="ERROR")
            traceback.print_exc()
            return

        mesh_vertices = meshio_mesh.points
        vertices_count = len(meshio_mesh.points)
        mesh_faces = self.create_face_data(meshio_mesh.cells)
        shade_scheme = False
        mesh = bpy.data.meshes[self.mesh_name]
        if mesh.polygons:
            shade_scheme = mesh.polygons[0].use_smooth

        #  delete the old mesh, if it has
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.clear()
        bm.to_mesh(mesh)
        bm.free()
        # then create a new mesh

        # load the vertices 
        mesh.vertices.add(vertices_count)
        mesh.vertices.foreach_set("co", meshio_mesh.points.ravel())

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

        #  optimized from code above
        # Check if there are any faces at all
        if len(mesh_faces) > 0:
            # Assume the same polygonal connectivity (e.g. all are triangles, then nploy =3 ) for all faces
            npoly = mesh_faces.shape[1]
            loops_vert_idx = mesh_faces.ravel()
            faces_loop_total = np.ones(
                (len(mesh_faces)), dtype=np.int32) * npoly
            faces_loop_start = np.cumsum(faces_loop_total)

            # Add a zero as first entry
            faces_loop_start = np.roll(faces_loop_start, 1)

            if len(faces_loop_start) > 0:
                faces_loop_start[0] = 0

            mesh.loops.add(len(loops_vert_idx))
            mesh.polygons.add(len(mesh_faces))

            mesh.loops.foreach_set("vertex_index", loops_vert_idx)
            mesh.polygons.foreach_set("loop_start", faces_loop_start)
            mesh.polygons.foreach_set("loop_total", faces_loop_total)
            # settings about if use shade_smooth or shade_flat
            mesh.polygons.foreach_set(
                "use_smooth", [shade_scheme]*len(faces_loop_total))

        if not self.render_attributes:
            for n in meshio_mesh.point_data.keys():
                self.render_attributes.append(n)
        # because everytime using bmesh.clear(), vertex color will be lost, and it has to be created again
        if self.used_render_attribute:
            v_col = mesh.vertex_colors.new()
            att_data = meshio_mesh.point_data[self.used_render_attribute]
            mesh_colors = None
            if len(att_data.shape) >= 3:
                show_message_box(
                    "attribute error: this shouldn't happen", icon="ERROR")
            else:
                # if it's 1-d vector, extend it to a nx1 matrix
                if len(att_data.shape) == 1:
                    att_data = np.expand_dims(att_data, axis=1)

                # a should be number of vertices, b should be dim of color attribute, e.g. velocity will have b=3
                a, b = att_data.shape
                if b > 3:
                    show_message_box(
                        "attribute error: higher than 3 dimenion of attribute", icon="ERROR")
                
                #  4-dim, rgba
                mesh_colors = np.zeros((len(mesh_faces)*3, 4))
                # copy the data from 0-b dims
                mesh_colors[:, :b] = att_data[mesh_faces.ravel()]
                mesh_colors[:, :b] = np.clip(
                    mesh_colors[:, :b], self.min_value, self.max_value)
                mesh_colors[:, :b] -= self.min_value
                mesh_colors /= (self.max_value-self.min_value)

                # set alpha channel to 1
                mesh_colors[:, 3] = 1 
                v_col.data.foreach_set('color', mesh_colors.ravel())

        mesh.update()
        mesh.validate()

    def init_mesh(self):

        mesh = bpy.data.meshes.new(name="Mesh_"+ self.name)
        self.mesh_name = mesh.name
        
        # init material
        material = bpy.data.materials.new("Material_" + self.name)
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        nodes.clear()
        links.clear()
        output = nodes.new(type="ShaderNodeOutputMaterial")
        diffuse = nodes.new(type="ShaderNodeBsdfDiffuse")
        link = links.new(diffuse.outputs["BSDF"], output.inputs["Surface"])
        vertex_color_node = nodes.new(type="ShaderNodeVertexColor")
        link = links.new(
            vertex_color_node.outputs["Color"], diffuse.inputs["Color"])
        
        #  create object
        new_object = bpy.data.objects.new("Obj_"+self.name, mesh)
        bpy.data.collections[0].objects.link(new_object)
        new_object.matrix_world = self.transform_matrix
        new_object.active_material = material

        total_path = self.fileseq[0]
        self.load_mesh(total_path)

    def __call__(self, scene, depsgraph=None):
        if not self.check_valid():
            return
        frame_number = scene.frame_current
        frame_number = max(frame_number,self.start)
        frame_number = min(frame_number,self.end)
        frame_number -= self.start
        frame_number = frame_number % len(self.fileseq)
        total_path = self.fileseq[frame_number]
        self.load_mesh(total_path)

    def get_color_attribute(self):
        return self.render_attributes

    def set_color_attribute(self, attr_name):
        if attr_name and attr_name in self.render_attributes:
            self.used_render_attribute = attr_name
        else:
            self.used_render_attribute = None

    def clear(self):
        bpy.ops.object.select_all(action="DESELECT")
        obj_name = self.get_obj_name()
        if obj_name and obj_name in bpy.data.objects:
            bpy.data.objects[obj_name].select_set(True)
            bpy.ops.object.delete()

    def set_max_value(self, r):
        self.max_value = r

    def set_min_value(self, r):
        self.min_value = r
    def get_obj(self):
        name=  self.get_obj_name()
        if name:
            return bpy.data.objects[name]
    
    def check_valid(self):
        if self.mesh_name not in bpy.data.meshes or not self.get_obj_name() :
            return False
        return True
    
    def get_obj_name(self):
        for obj in bpy.data.objects:
            if obj.type =="MESH" and obj.data.name ==self.mesh_name:
                    return obj.name
        return None