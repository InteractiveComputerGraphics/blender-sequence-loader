import bpy
import meshio
import fileseq
import numpy as np
from .utils import *
from mathutils import Matrix
import traceback


class particle_importer:
    def __init__(self, fileseq, transform_matrix=Matrix([[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0, 1]]), emitter_obj_name=None, sphere_obj_name=None, material_name=None, tex_image_name=None, mesh_name=None, radius=0.01):

        # self.path=path
        self.fileseq = fileseq
        self.name = fileseq.basename()+"@"+fileseq.extension()
        self.transform_matrix = transform_matrix
        self.render_attributes = []  # all the possible attributes, and type
        self.used_render_attribute = None  # the attribute used for rendering
        self.min_value = 0  # the min value of this attribute
        self.max_value = 0  # the max value of this attribute
        self.emitterObject = None
        self.sphereObj = None
        self.mesh = None
        self.tex_image = None
        self.particle_num = 0
        if not emitter_obj_name or not sphere_obj_name or not material_name:
            self.init_particles()
        else:
            self.emitterObject = bpy.data.objects[emitter_obj_name]
            self.sphereObj = bpy.data.objects[sphere_obj_name]
            self.material = bpy.data.materials[material_name]
            self.particle_num = self.emitterObject.particle_systems[0].settings.count

    def init_particles(self):
        # create emitter object
        bpy.ops.mesh.primitive_cube_add(
            enter_editmode=False, location=(0, 0, 0))
        self.emitterObject = bpy.context.active_object
        self.emitterObject.name = self.name
        self.emitterObject.matrix_world = self.transform_matrix
        self.emitterObject.hide_viewport = False
        self.emitterObject.hide_render = False
        self.emitterObject.hide_select = False

        bpy.ops.object.modifier_add(type="PARTICLE_SYSTEM")
        #  turn off the gravity
        bpy.data.particles["ParticleSettings"].effector_weights.gravity = 0
        # make the cube invincible
        bpy.context.object.show_instancer_for_render = False
        bpy.context.object.show_instancer_for_viewport = False
        # basic settings for the particles
        self.emitterObject.particle_systems[0].settings.frame_start = 0
        self.emitterObject.particle_systems[0].settings.frame_end = 0
        self.emitterObject.particle_systems[0].settings.lifetime = 1000
        self.emitterObject.particle_systems[0].settings.particle_size = 0.01

        # create instance object
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=1, enter_editmode=False, location=(0, 0, 0)
        )
        bpy.ops.object.shade_smooth()
        self.sphereObj = bpy.context.active_object
        self.sphereObj.name = self.name + "_sphere"
        self.sphereObj.hide_set(True)
        self.sphereObj.hide_viewport = False
        self.sphereObj.hide_render = True
        self.sphereObj.hide_select = True
        #  create new material
        self.material = bpy.data.materials.new("particle_material")
        self.material.use_nodes = True

        self.init_materials()

        self.emitterObject.active_material = self.material
        self.sphereObj.active_material = self.material

        self.emitterObject.particle_systems[0].settings.render_type = "OBJECT"
        self.emitterObject.particle_systems[0].settings.instance_object = self.sphereObj

        self.read_first_frame()

        #  useless init, only used to be compatible with new_particle_importer.py
        self.mesh = self.emitterObject.data
        self.tex_image = bpy.data.images.new(
            'not_used', width=self.particle_num, height=1)

    def init_materials(self):
        nodes = self.material.node_tree.nodes
        links = self.material.node_tree.links
        nodes.clear()
        links.clear()

        particleInfo = nodes.new(type="ShaderNodeParticleInfo")

        diffuse = nodes.new(type="ShaderNodeBsdfDiffuse")
        diffuse.location.x = 300
        output = nodes.new(type="ShaderNodeOutputMaterial")
        output.location.x = 600
        link = links.new(diffuse.outputs["BSDF"], output.inputs["Surface"])
        link = links.new(
            particleInfo.outputs["Velocity"], diffuse.inputs["Color"])

        # recover the real attribute value

        s_xyz = nodes.new(type="ShaderNodeSeparateXYZ")
        math3 = nodes.new(type="ShaderNodeMath")
        math4 = nodes.new(type="ShaderNodeMath")
        math5 = nodes.new(type="ShaderNodeMath")

        math3.location.y = 900
        math4.location.x = 300*2
        math4.location.y = 600
        math5.location.x = 300*2
        math5.location.y = 300

        math3.operation = "MULTIPLY"
        math4.operation = "MULTIPLY"
        math5.operation = "MULTIPLY"

        math3.inputs[1].default_value = self.max_value - self.min_value
        math4.inputs[1].default_value = self.max_value - self.min_value
        math5.inputs[1].default_value = self.max_value - self.min_value

        math6 = nodes.new(type="ShaderNodeMath")
        math7 = nodes.new(type="ShaderNodeMath")
        math8 = nodes.new(type="ShaderNodeMath")

        math6.operation = "ADD"
        math7.operation = "ADD"
        math8.operation = "ADD"

        math6.inputs[1].default_value = self.min_value
        math7.inputs[1].default_value = self.min_value
        math8.inputs[1].default_value = self.min_value

        math6.location.x = 300*3
        math6.location.y = 900
        math7.location.x = 300*3
        math7.location.y = 600
        math8.location.x = 300*3
        math8.location.y = 300

        math3.location.x = 300*2

        link = links.new(
            particleInfo.outputs["Velocity"], s_xyz.inputs["Vector"])
        link = links.new(s_xyz.outputs["X"], math3.inputs[0])
        link = links.new(s_xyz.outputs["Y"], math4.inputs[0])
        link = links.new(s_xyz.outputs["Z"], math5.inputs[0])

        link = links.new(math3.outputs["Value"], math6.inputs[0])
        link = links.new(math4.outputs["Value"], math7.inputs[0])
        link = links.new(math5.outputs["Value"], math8.inputs[0])

    def read_first_frame(self):
        try:
            mesh = meshio.read(
                self.fileseq[0]
            )
        except Exception as e:
            show_message_box("Can't read first frame file", icon="ERROR")
            traceback.print_exc()

        self.particle_num = len(mesh.points)
        self.emitterObject.particle_systems[0].settings.count = self.particle_num
        if self.particle_num > 50000:
            self.emitterObject.particle_systems[0].settings.display_method = 'DOT'

        depsgraph = bpy.context.evaluated_depsgraph_get()
        particle_systems = self.emitterObject.evaluated_get(
            depsgraph).particle_systems
        particles = particle_systems[0].particles

        points_pos = np.zeros((self.particle_num, 4))
        points_pos[:, -1] = 1
        points_pos[:, :3] = mesh.points
        transform_matrix = np.array(self.emitterObject.matrix_world)
        points_pos = points_pos @ np.transpose(transform_matrix)
        points_pos = points_pos[:, :3]

        particles.foreach_set("location", points_pos.ravel())

        if mesh.point_data:
            for k in mesh.point_data.keys():
                self.render_attributes.append(k)
        else:
            show_message_box(
                "no attributes avaible, all particles will be rendered as the same color"
            )
        # particles.foreach_set("velocity", [0]*3*len(mesh.points))

        self.max_value = self.particle_num

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
            self.emitterObject.particle_systems[0].settings.count = self.particle_num

        #  update location info
        if depsgraph is None:
            #  wish this line will never be executed
            show_message_box("it shouldn't happen")
            depsgraph = bpy.context.evaluated_depsgraph_get()

        particle_systems = self.emitterObject.evaluated_get(
            depsgraph).particle_systems
        particles = particle_systems[0].particles

        points_pos = np.zeros((self.particle_num, 4))
        points_pos[:, -1] = 1
        points_pos[:, :3] = mesh.points
        transform_matrix = np.array(self.emitterObject.matrix_world)
        points_pos = points_pos @ np.transpose(transform_matrix)
        points_pos = points_pos[:, :3]
        particles.foreach_set("location", points_pos.ravel())

        # update rendering and color(velocity) info
        if self.used_render_attribute:
            att_str = self.used_render_attribute
            att_data = mesh.point_data[att_str]
            if len(att_data.shape) >= 3:
                #  normally, this one shouldn't happen
                show_message_box(
                    "attribute error: higher than 3 dimenion of attribute", icon="ERROR")
            else:
                if len(att_data.shape) == 1:
                    att_data = np.expand_dims(att_data, axis=1)
                a, b = att_data.shape
                if b > 3:
                    show_message_box(
                        "attribute error: higher than 3 dimenion of attribute", icon="ERROR")
                vel_att = np.zeros((self.particle_num, 3))
                vel_att[:, :b] = att_data
                vel_att[:, :b] = np.clip(
                    vel_att[:, :b], self.min_value, self.max_value)
                vel_att[:, :b] -= self.min_value
                vel_att /= (self.max_value-self.min_value)
                particles.foreach_set("velocity", vel_att.ravel())
        else:
            vel = [0] * 3*self.particle_num
            particles.foreach_set("velocity", vel)

        # self.emitterObject.particle_systems[0].settings.frame_end = 0 # !! so velocity has no effect on the position any more, and velocity can be used for rendering

    def get_color_attribute(self):
        return self.render_attributes

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
        if self.sphereObj:
            bpy.data.meshes.remove(self.sphereObj.data)
            # This doesn't work
            # self.sphereObj.select_set(True)
            # bpy.ops.object.delete()
            self.sphereObj = None

        for p in bpy.data.particles:
            if p.users == 0:
                bpy.data.particles.remove(p)
        for m in bpy.data.meshes:
            if m.users == 0:
                bpy.data.meshes.remove(m)
        for m in bpy.data.materials:
            if m.users == 0:
                bpy.data.materials.remove(m)

    def __del__(self):
        self.clear()

    def set_radius(self, r):
        self.emitterObject.particle_systems[0].settings.particle_size = r
        self.emitterObject.particle_systems[0].settings.display_size = r

    def set_max_value(self, r):
        self.max_value = r
        self.material.node_tree.nodes[4].inputs[1].default_value = self.max_value - self.min_value
        self.material.node_tree.nodes[5].inputs[1].default_value = self.max_value - self.min_value
        self.material.node_tree.nodes[6].inputs[1].default_value = self.max_value - self.min_value

    def set_min_value(self, r):
        self.min_value = r

        self.material.node_tree.nodes[7].inputs[1].default_value = self.min_value
        self.material.node_tree.nodes[8].inputs[1].default_value = self.min_value
        self.material.node_tree.nodes[9].inputs[1].default_value = self.min_value

        self.material.node_tree.nodes[4].inputs[1].default_value = self.max_value - self.min_value
        self.material.node_tree.nodes[5].inputs[1].default_value = self.max_value - self.min_value
        self.material.node_tree.nodes[6].inputs[1].default_value = self.max_value - self.min_value

    def update_display(self, method):
        self.emitterObject.particle_systems[0].settings.display_method = method
