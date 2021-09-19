#  this should be a better one, but there is a critical blender bug, so this code only works for a small number of particles, about 10k
#  for more details, please check https://developer.blender.org/T81103
#  and this code is not being used currently
import bpy
import meshio
import fileseq
import bmesh
import numpy as np
import bmesh
from mathutils import Matrix
from .utils import *
import traceback


class particle_importer:
    def __init__(self, fileseq, transform_matrix=Matrix([[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0, 1]]), emitter_obj_name=None, sphere_obj_name=None, material_name=None, tex_image_name=None, mesh_name=None, radius=0.01):

        # self.path=path
        self.fileseq = fileseq
        self.name = fileseq.basename()+"@"+fileseq.extension()
        self.transform_matrix = transform_matrix
        self.render_attributes = []  # all the possible attributes, and type
        self.used_render_attribute = None  # the attribute used for rendering
        self.emitterObject = None
        self.sphereObj = None
        self.max_value = None
        self.min_value = 0
        if not emitter_obj_name or not sphere_obj_name or not material_name or not tex_image_name or not mesh_name:
            self.init_particles()
        else:
            self.mesh = bpy.data.meshes[mesh_name]
            self.emitterObject = bpy.data.objects[emitter_obj_name]
            self.sphereObj = bpy.data.objects[sphere_obj_name]
            self.material = bpy.data.materials[material_name]
            self.tex_image = bpy.data.images[tex_image_name]
            self.particle_num = self.emitterObject.particle_systems[0].settings.count
        self.set_radius(radius)

    def init_particles(self):
        try:
            meshio_mesh = meshio.read(self.fileseq[0])
        except Exception as e:
            show_message_box("meshio error when reading: " +
                             self.fileseq[0]+",\n please check console for more details.", icon="ERROR")
            traceback.print_exc()
            return

        if meshio_mesh.point_data:
            for k in meshio_mesh.point_data.keys():
                self.render_attributes.append(k)
        else:
            show_message_box(
                "no attributes avaible, all particles will be rendered as the same color"
            )

        self.mesh = bpy.data.meshes.new(name=self.name+"_mesh")
        mesh_vertices = meshio_mesh.points
        self.particle_num = len(meshio_mesh.points)
        self.max_value = self.particle_num

        self.mesh.vertices.add(self.particle_num)

        # pos = meshio_mesh.points @ self.rotation

        self.mesh.vertices.foreach_set("co", meshio_mesh.points.ravel())
        new_object = bpy.data.objects.new(self.name, self.mesh)
        bpy.data.collections[0].objects.link(new_object)
        self.emitterObject = new_object

        bpy.context.view_layer.objects.active = self.emitterObject

        bpy.ops.object.particle_system_add()
        self.emitterObject.matrix_world = self.transform_matrix

        # basic settings for the particles
        if self.particle_num > 50000:
            self.emitterObject.particle_systems[0].settings.display_method = 'NONE'
        self.emitterObject.particle_systems[0].settings.frame_start = 0
        self.emitterObject.particle_systems[0].settings.effector_weights.gravity = 0
        self.emitterObject.particle_systems[0].settings.frame_end = 0
        self.emitterObject.particle_systems[0].settings.lifetime = 1000
        self.emitterObject.particle_systems[0].settings.particle_size = 0.01
        self.emitterObject.particle_systems[0].settings.emit_from = 'VERT'
        self.emitterObject.particle_systems[0].settings.count = self.particle_num
        self.emitterObject.particle_systems[0].settings.use_emit_random = False
        self.emitterObject.particle_systems[0].settings.normal_factor = 0

        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=1, enter_editmode=False, location=(0, 0, 0)
        )
        bpy.ops.object.shade_smooth()
        self.sphereObj = bpy.context.active_object
        self.sphereObj.hide_set(True)
        self.sphereObj.hide_viewport = False
        self.sphereObj.hide_render = True
        self.sphereObj.hide_select = True
        #  create new material
        self.material = bpy.data.materials.new(self.name+"particle_material")
        self.material.use_nodes = True
        self.init_materials()

        self.emitterObject.active_material = self.material
        self.sphereObj.active_material = self.material

        self.emitterObject.particle_systems[0].settings.render_type = "OBJECT"
        self.emitterObject.particle_systems[0].settings.instance_object = self.sphereObj

    def init_materials(self):
        nodes = self.material.node_tree.nodes
        links = self.material.node_tree.links
        nodes.clear()
        links.clear()

        #  init node
        particleInfo = nodes.new(type="ShaderNodeParticleInfo")
        math1 = nodes.new(type="ShaderNodeMath")
        math2 = nodes.new(type="ShaderNodeMath")
        combine = nodes.new(type="ShaderNodeCombineXYZ")
        tex = nodes.new(type="ShaderNodeTexImage")
        s_rgb = nodes.new(type="ShaderNodeSeparateRGB")

        math3 = nodes.new(type="ShaderNodeMath")
        math4 = nodes.new(type="ShaderNodeMath")
        math5 = nodes.new(type="ShaderNodeMath")

        math6 = nodes.new(type="ShaderNodeMath")
        math7 = nodes.new(type="ShaderNodeMath")
        math8 = nodes.new(type="ShaderNodeMath")

        diffuse = nodes.new(type="ShaderNodeBsdfDiffuse")
        output = nodes.new(type="ShaderNodeOutputMaterial")

        #  set node location
        math1.location.x = 300
        math2.location.x = 300 * 2
        combine.location.x = 300 * 3
        tex.location.x = 300*4
        s_rgb.location.x = 300*5
        s_rgb.location.y = 300
        math6.location.x = 300*6
        math6.location.y = 900
        math7.location.x = 300*6
        math7.location.y = 600
        math8.location.x = 300*6
        math8.location.y = 300

        math3.location.x = 300*7
        math3.location.y = 900
        math4.location.x = 300*7
        math4.location.y = 600
        math5.location.x = 300*7
        math5.location.y = 300

        diffuse.location.x = 300*5
        output.location.x = 300*7

        #  set node init value

        math1.operation = "ADD"
        math1.inputs[1].default_value = 0.5
        math2.operation = "DIVIDE"
        # this should be the number of particles
        math2.inputs[1].default_value = self.particle_num

        combine.inputs[1].default_value = 0
        combine.inputs[2].default_value = 0

        math3.operation = "ADD"
        math4.operation = "ADD"
        math5.operation = "ADD"

        math3.inputs[1].default_value = self.min_value
        math4.inputs[1].default_value = self.min_value
        math5.inputs[1].default_value = self.min_value

        math6.operation = "MULTIPLY"
        math7.operation = "MULTIPLY"
        math8.operation = "MULTIPLY"

        math6.inputs[1].default_value = self.max_value - self.min_value
        math7.inputs[1].default_value = self.max_value - self.min_value
        math8.inputs[1].default_value = self.max_value - self.min_value

        self.tex_image = bpy.data.images.new(
            'particle_tex_image', width=self.particle_num, height=1)
        tex.image = self.tex_image

        #  set node links

        link = links.new(particleInfo.outputs["Index"], math1.inputs[0])
        link = links.new(math1.outputs["Value"], math2.inputs[0])
        link = links.new(math2.outputs["Value"], combine.inputs[0])
        link = links.new(combine.outputs["Vector"], tex.inputs["Vector"])
        link = links.new(tex.outputs["Color"], s_rgb.inputs["Image"])
        link = links.new(tex.outputs["Color"], diffuse.inputs["Color"])
        link = links.new(s_rgb.outputs["R"], math6.inputs[0])
        link = links.new(s_rgb.outputs["G"], math7.inputs[0])
        link = links.new(s_rgb.outputs["B"], math8.inputs[0])

        link = links.new(math6.outputs["Value"], math3.inputs[0])
        link = links.new(math7.outputs["Value"], math4.inputs[0])
        link = links.new(math8.outputs["Value"], math5.inputs[0])
        link = links.new(diffuse.outputs["BSDF"], output.inputs["Surface"])

    def __call__(self, scene, depsgraph=None):
        frame_number = scene.frame_current
        frame_number = frame_number % len(self.fileseq)
        try:
            mesh = meshio.read(
                self.fileseq[frame_number]
            )
        except Exception as e:
            show_message_box("meshio error when reading: " +
                             self.fileseq[frame_number]+",\n please check console for more details", icon="ERROR")
            traceback.print_exc()
            return

        if len(mesh.points) != self.particle_num:
            self.particle_num = len(mesh.points)
            self.tex_image.generated_width = self.particle_num
            # this should be math2 node
            self.material.node_tree.nodes['Math.001'].inputs[1].default_value = self.particle_num
        bm = bmesh.new()
        bm.from_mesh(self.mesh)
        bm.clear()
        bm.to_mesh(self.mesh)
        bm.free()
        self.mesh.vertices.add(self.particle_num)
        self.mesh.vertices.foreach_set("co", mesh.points.ravel())

        if self.used_render_attribute:
            att_str = self.used_render_attribute
            att_data = mesh.point_data[att_str]
            color = self.calculate_color(att_data)
            pixels = np.zeros((self.particle_num, 4), dtype=np.float32)
            pixels[:, 0:3] = color
            pixels[:, 3] = 1
            self.tex_image.pixels.foreach_set(pixels.ravel())
        else:
            pixels = [0] * 4*self.particle_num
            self.tex_image.pixels.foreach_set(pixels)

    def get_color_attribute(self):
        return self.render_attributes

    #  return a np.array with shape= particle_num, 3
    def calculate_color(self, att_data):
        if len(att_data.shape) >= 3:
            #  normally, this one shouldn't happen
            show_message_box(
                "attribute error: this shouldn't happen", icon="ERROR")
        elif len(att_data.shape) == 2:
            a, b = att_data.shape
            if b > 3:
                show_message_box(
                    "attribute error: higher than 3 dimenion of attribute", icon="ERROR")
            res = np.zeros((a, 3))
            res[:, :b] = att_data
            #  for example, when the vield is velocity, it would rotate the velocity as well
            if b == 3:
                transform_matrix = np.array(self.emitterObject.matrix_world)
                transform_matrix = transform_matrix[:3, :3]
                res = res @ transform_matrix
            res[:, :b] = np.clip(res[:, :b], self.min_value, self.max_value)
            res[:, :b] -= self.min_value
            res /= (self.max_value-self.min_value)
            return res
        elif len(att_data.shape) == 1:
            res = np.zeros((att_data.shape[0], 3))
            res[:, 0] = att_data
            res[:, 0] = np.clip(res[:, 0], self.min_value, self.max_value)
            res[:, 0] = res[:, 0] - self.min_value
            res /= (self.max_value-self.min_value)
            return res

    def set_color_attribute(self, attribute_str):
        if not attribute_str:
            self.used_render_attribute = None
            return
        if attribute_str in self.render_attributes:
            self.used_render_attribute = attribute_str
        else:
            show_message_box(
                "attributes error: this attributs is not available in 1st frame of file"
            )

    def clear(self):
        bpy.ops.object.select_all(action="DESELECT")
        if self.emitterObject:
            self.emitterObject.select_set(True)
            bpy.ops.object.delete()
            self.emitterObject = None
            bpy.data.meshes.remove(self.mesh)
            self.mesh = None
        if self.sphereObj:
            bpy.data.meshes.remove(self.sphereObj.data)
            self.sphereObj = None
        for p in bpy.data.particles:
            if p.users == 0:
                bpy.data.particles.remove(p)
        if self.material:
            bpy.data.materials.remove(self.material)
            self.material = None
        if self.tex_image:
            bpy.data.images.remove(self.tex_image)
            self.tex_image = None

    def __del__(self):
        self.clear()

    def set_radius(self, r):
        self.emitterObject.particle_systems[0].settings.particle_size = r

    def set_max_value(self, r):
        self.max_value = r
        self.material.node_tree.nodes[9].inputs[1].default_value = self.max_value - self.min_value
        self.material.node_tree.nodes[10].inputs[1].default_value = self.max_value - self.min_value
        self.material.node_tree.nodes[11].inputs[1].default_value = self.max_value - self.min_value

    def set_min_value(self, r):
        self.min_value = r

        self.material.node_tree.nodes[6].inputs[1].default_value = self.min_value
        self.material.node_tree.nodes[7].inputs[1].default_value = self.min_value
        self.material.node_tree.nodes[8].inputs[1].default_value = self.min_value

        self.material.node_tree.nodes[9].inputs[1].default_value = self.max_value - self.min_value
        self.material.node_tree.nodes[10].inputs[1].default_value = self.max_value - self.min_value
        self.material.node_tree.nodes[11].inputs[1].default_value = self.max_value - self.min_value
