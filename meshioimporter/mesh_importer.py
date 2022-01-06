import bpy
import meshio
import fileseq
import numpy as np
from mathutils import Matrix
import traceback
from .utils import *


class mesh_importer:
    def __init__(self, fileseq, transform_matrix=Matrix([[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0, 1]]), mesh_name=None):
        if fileseq:
            self.name = fileseq.basename()+"@"+fileseq.extension()
            self.fileseq = fileseq
        else:
            self.fileseq = None
            self.name = ""
        self.transform_matrix = transform_matrix
        self.color_attributes = []  # all the possible attributes, and type
        self.used_color_attribute = None  # the attribute used for rendering
        self.min_value = 0
        self.max_value = 100
        self.current_min = 0
        self.current_max = 0
        self.mesh_name = None
        self.script_name = None
        self.use_real_value = False
        if not mesh_name:
            self.initilize()
        else:
            self.mesh_name = mesh_name

    def create_face_data(self, meshio_cells):
        # todo: support other mesh structure, such as tetrahedron
        return meshio_cells[0][1]

    #  update the mesh information
    def update_mesh(self, meshio_mesh):

        #  information read from meshio_mesh
        mesh_vertices = meshio_mesh.points

        mesh_faces = self.create_face_data(meshio_mesh.cells)
        face_shape = mesh_faces.shape
        n_verts = len(meshio_mesh.points)
        npoly = mesh_faces.shape[1]
        n_primitives = mesh_faces.shape[0]

        #  inforamtion read from blender mesh
        mesh = bpy.data.meshes[self.mesh_name]
        shade_scheme = False
        if mesh.polygons:
            shade_scheme = mesh.polygons[0].use_smooth

        #  1. Update the number of vertices/ edges/ faces
        if len(mesh.vertices) == n_verts and len(mesh.polygons) == face_shape[0] and len(mesh.loops) == face_shape[0]*face_shape[1]:
            # the strucutre doesn't change, no need to add or remove vertices/ edges/  polygons, then directly go to next step
            # In theory, it could have a bug here, because it doesn't check the number of edges, but it's too hard to do that,
            # because edge data is not stored in files, it has to be calculated from mesh_face manually
            # So the problem is, if existing mesh has more edges than the next mesh, then these extra edges won't be removed,
            # It won't effect the rendered image, because edges won't be rendered
            # but it will look ugly in viewport, especially go into edit mode
            # this can happen only in a very rare case.
            pass
        else:
            # since the structure has been changed, so delete it first, then create a new one
            # and reconstruct some other attributes here(if there are), e.g. uv maps, etc.
            mesh.clear_geometry()
            mesh.vertices.add(n_verts)
            mesh.loops.add(npoly * n_primitives)
            mesh.polygons.add(n_primitives)
            mesh.attributes.new(name="att", type="FLOAT_VECTOR", domain="POINT")

        #  set position of vertices
        mesh.vertices.foreach_set("co", meshio_mesh.points.ravel())

        #  2. Set the connectivity of mesh
        # Only tested for (non-empty) triangle meshes, should be work fine with other mesh strucutres, e.g. quad mesh
        loops_vert_idx = mesh_faces.ravel()

        faces_loop_total = np.ones((len(mesh_faces)), dtype=np.int32) * npoly
        faces_loop_start = np.cumsum(faces_loop_total)

        # Add a zero as first entry
        faces_loop_start = np.roll(faces_loop_start, 1)

        faces_loop_start[0] = 0

        mesh.loops.foreach_set("vertex_index", loops_vert_idx)
        mesh.polygons.foreach_set("loop_start", faces_loop_start)
        mesh.polygons.foreach_set("loop_total", faces_loop_total)

        mesh.update()
        mesh.validate()

        # settings about if use shade_smooth or shade_flat
        mesh.polygons.foreach_set("use_smooth", [shade_scheme]*len(faces_loop_total))

    def update_color_attributes(self, meshio_mesh):
        mesh = bpy.data.meshes[self.mesh_name]
        mesh_faces = self.create_face_data(meshio_mesh.cells)
        v_col = mesh.attributes['att']
        mesh_colors = np.zeros((len(meshio_mesh.points), 3))

        if self.used_color_attribute:     
            att_data = meshio_mesh.point_data[self.used_color_attribute]
            if len(att_data.shape) >= 3:
                show_message_box("attribute error: this shouldn't happen", icon="ERROR")
            else:
                # if it's 1-d vector, extend it to a nx1 matrix
                if len(att_data.shape) == 1:
                    att_data = np.expand_dims(att_data, axis=1)

                # a should be number of vertices, b should be dim of color attribute, e.g. velocity will have b=3
                a, b = att_data.shape
                if b > 3:
                    show_message_box("attribute error: higher than 3 dimenion of attribute", icon="ERROR")
                else:
                    # if not use real value, then use clamped the (norm) value
                    if not self.use_real_value:
                        mesh_colors[:, 0] = np.linalg.norm(att_data, axis=1)
                        self.current_min = np.min(mesh_colors[:, 0])
                        self.current_max = np.max(mesh_colors[:, 0])
                        mesh_colors[:, 0] -= self.min_value
                        mesh_colors[:, 0] /= (self.max_value-self.min_value)
                        mesh_colors[:, 0] = np.clip(mesh_colors[:, 0], 0, 1)
                    else:
                        mesh_colors[:, :b] = att_data
                v_col.data.foreach_set('vector', mesh_colors.ravel())
        else:
            #  if not use any color attributes, then set it to zero    
            v_col.data.foreach_set('vector', mesh_colors.ravel())

    def initilize(self):

        mesh = bpy.data.meshes.new(name="Mesh_" + self.name)
        mesh.attributes.new(name="att", type="FLOAT_VECTOR", domain="POINT")
        self.mesh_name = mesh.name

        # init default material
        material = bpy.data.materials.new("Material_" + self.name)
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        nodes.clear()
        links.clear()

        attribute_node = nodes.new(type="ShaderNodeAttribute")
        attribute_node.attribute_name = "att"
        vecMath = nodes.new(type='ShaderNodeVectorMath')
        vecMath.operation = 'DOT_PRODUCT'
        math1 = nodes.new(type='ShaderNodeMath')
        math1.operation = 'SQRT'
        ramp = nodes.new(type='ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].color = (0, 0, 1, 1)
        diffuse = nodes.new(type="ShaderNodeBsdfDiffuse")
        output = nodes.new(type="ShaderNodeOutputMaterial")

        for i, n in enumerate(nodes):
            n.location.x = i*300

        link = links.new(attribute_node.outputs["Vector"], vecMath.inputs[0])
        link = links.new(attribute_node.outputs["Vector"], vecMath.inputs[1])
        link = links.new(vecMath.outputs["Value"], math1.inputs["Value"])
        link = links.new(math1.outputs["Value"], ramp.inputs['Fac'])
        link = links.new(ramp.outputs["Color"], diffuse.inputs["Color"])
        link = links.new(diffuse.outputs["BSDF"], output.inputs["Surface"])

        #  create object
        new_object = bpy.data.objects.new("Obj_"+self.name, mesh)
        bpy.data.collections[0].objects.link(new_object)
        new_object.matrix_world = self.transform_matrix
        new_object.active_material = material

        total_path = self.fileseq[0]

        meshio_mesh = None
        try:
            meshio_mesh = meshio.read(total_path)
        except Exception as e:
            if bpy.context.screen.is_animation_playing:
                #  if playing animation, then stop it, otherwise it will keep showing message box
                bpy.ops.screen.animation_cancel()
            show_message_box("meshio error when reading: "+total_path +
                             ",\n please check console for more details", icon="ERROR")
            traceback.print_exc()
            return None

        self.update_mesh(meshio_mesh)

    def __call__(self, scene, depsgraph=None):
        if not self.check_valid():
            # The object has been removed
            return
        if not self.fileseq:
            # The sequence data file has been removed, but blender object still there
            if bpy.context.screen.is_animation_playing:
                #  if playing animation, then stop it, otherwise it will keep showing message box
                bpy.ops.screen.animation_cancel()
            show_message_box("file sequence doesn't exist, please edit it or remove it")
            return

        frame_number = scene.frame_current
        meshio_mesh = None
        if self.script_name:
            try:
                def preprocess():
                    # only keep it here to avoid vscode warning for unknown function preprocess
                    pass
                exec(bpy.data.texts[self.script_name].as_string(), globals())
                meshio_mesh = preprocess(self.fileseq, frame_number)
            except Exception as e:
                if bpy.context.screen.is_animation_playing:
                    #  if playing animation, then stop it, otherwise it will keep showing message box
                    bpy.ops.screen.animation_cancel()
                show_message_box("running script"+self.script_name + "failed")
                traceback.print_exc()
                return

        else:
            try:
                frame_number = frame_number % len(self.fileseq)
                total_path = self.fileseq[frame_number]
                meshio_mesh = meshio.read(total_path)
            except Exception as e:
                if bpy.context.screen.is_animation_playing:
                    #  if playing animation, then stop it, otherwise it will keep showing message box
                    bpy.ops.screen.animation_cancel()
                show_message_box("meshio error when reading: "+total_path +
                                 ",\n please check console for more details", icon="ERROR")
                traceback.print_exc()
                return None

        self.update_mesh(meshio_mesh)

        self.update_color_attributes(meshio_mesh)


    def set_color_attribute(self, attr_name):
        if attr_name and attr_name in self.color_attributes:
            self.used_color_attribute = attr_name
        else:
            self.used_color_attribute = None

    def clear(self):
        bpy.ops.object.select_all(action="DESELECT")
        obj_name = self.get_obj_name()
        if obj_name and obj_name in bpy.data.objects:
            bpy.data.objects[obj_name].select_set(True)
            bpy.ops.object.delete()

    def get_obj(self):
        name = self.get_obj_name()
        if name:
            return bpy.data.objects[name]

    def check_valid(self):
        if self.mesh_name not in bpy.data.meshes or not self.get_obj_name():
            return False
        return True

    def get_obj_name(self):
        for obj in bpy.data.objects:
            if obj.type == "MESH" and obj.data.name == self.mesh_name:
                return obj.name
        return None

    def type(self):
        return "mesh"
