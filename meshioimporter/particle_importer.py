import bpy
import meshio
import fileseq
import numpy as np
from .utils import *
from mathutils import Matrix
import traceback


class particle_importer:
    def __init__(self, fileseq, transform_matrix=Matrix([[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0, 1]]),
    particle_settings_name=None, radius=0.01):

        # self.path=path
        self.fileseq = fileseq
        self.name = fileseq.basename()+"@"+fileseq.extension()
        self.transform_matrix = transform_matrix
        self.render_attributes = []  # all the (name of ) color attributes
        self.used_render_attribute = None  # the attribute used for rendering
        self.min_value = 0  # the min value of this attribute
        self.max_value = 0  # the max value of this attribute, will be initlized as number of particles
        self.start = 0
        self.end = 500
        self.particle_num = 0
        self.particle_settings_name = None
        if not particle_settings_name:
            self.init_particles()
        else:
            self.particle_settings_name = particle_settings_name
            self.particle_num = bpy.data.particles[self.particle_settings_name].count

    def init_particles(self):
        # create emitter object
        bpy.ops.mesh.primitive_cube_add(
            enter_editmode=False, location=(0, 0, 0))
        emitter_object = bpy.context.active_object

        emitter_object.name = "Emitter_"+self.name 
        emitter_object.matrix_world = self.transform_matrix
        emitter_object.hide_viewport = False
        emitter_object.hide_render = False
        emitter_object.hide_select = False

        bpy.ops.object.modifier_add(type="PARTICLE_SYSTEM")
        #  turn off the gravity
        bpy.data.particles["ParticleSettings"].effector_weights.gravity = 0
        # make the cube invincible
        bpy.context.object.show_instancer_for_render = False
        bpy.context.object.show_instancer_for_viewport = False
        # basic settings for the particles

        self.particle_settings_name  =emitter_object.particle_systems[0].settings.name

        emitter_object.particle_systems[0].settings.frame_start = 0
        emitter_object.particle_systems[0].settings.frame_end = 0
        emitter_object.particle_systems[0].settings.lifetime = 1000
        emitter_object.particle_systems[0].settings.particle_size = 0.01
        emitter_object.particle_systems[0].settings.display_size = 0.01


        bpy.ops.object.select_all(action="DESELECT")
        # create instance object
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=1,enter_editmode=False, location=(0, 0, 0)
        )
        bpy.ops.object.shade_smooth()
        sphere_obj = bpy.context.active_object
        # same as emitter_obj, blender will change name
        sphere_obj.name = "Sphere_"+self.name 
        sphere_obj.hide_set(True)
        sphere_obj.hide_viewport = False
        sphere_obj.hide_render = True
        sphere_obj.hide_select = True
        
        #  create new material
        material = bpy.data.materials.new("Material_"+self.name)
        material.use_nodes = True
        # self.material_name = material.name

        #  init nodes and links of material
        #  because I want to set self.max_value as particles number by default, so I read frame first, then create material(it needs this self.max_value when setting default value for math node)
        self.read_first_frame()
        self.init_materials(material.name)

        emitter_object.active_material = material
        sphere_obj.active_material = material

        emitter_object.particle_systems[0].settings.render_type = "OBJECT"
        emitter_object.particle_systems[0].settings.instance_object = sphere_obj

    def read_first_frame(self):
        particle_settings = bpy.data.particles[self.particle_settings_name]
        try:
            mesh = meshio.read(
                self.fileseq[0]
            )
        except Exception as e:
            show_message_box("Can't read first frame file", icon="ERROR")
            traceback.print_exc()

        self.particle_num = len(mesh.points)
        particle_settings.count = self.particle_num

        if mesh.point_data:
            for k in mesh.point_data.keys():
                self.render_attributes.append(k)
        else:
            show_message_box(
                "no attributes avaible, all particles will be rendered as the same color"
            )

        self.max_value = self.particle_num


    def init_materials(self, material_name):
        material = bpy.data.materials[material_name]
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        nodes.clear()
        links.clear()

        particleInfo = nodes.new(type="ShaderNodeParticleInfo")
        vecMath = nodes.new( type = 'ShaderNodeVectorMath' )
        vecMath.operation = 'DOT_PRODUCT'
        # math1 = nodes.new( type = 'ShaderNodeMath' )
        # math1.operation = 'SQRT'
        # math2 = nodes.new( type = 'ShaderNodeMath' )
        # math2.operation = 'SUBTRACT'
        # math2.inputs[1].default_value = self.min_value
        # math3 = nodes.new( type = 'ShaderNodeMath' )
        # math3.operation = 'MULTIPLY'
        # math3.inputs[1].default_value = 1.0/(self.max_value-self.min_value)
        # math3.use_clamp = True
        ramp = nodes.new( type = 'ShaderNodeValToRGB' )
        ramp.color_ramp.elements[0].color = (0, 0, 1, 1)
        diffuse = nodes.new(type="ShaderNodeBsdfDiffuse")   
        output = nodes.new(type="ShaderNodeOutputMaterial")

        for i,n in enumerate(nodes):
            n.location.x = i*300

        
        link = links.new(particleInfo.outputs["Velocity"],vecMath.inputs[0])
        link = links.new(particleInfo.outputs["Velocity"],vecMath.inputs[1])
        link = links.new(vecMath.outputs["Value"],ramp.inputs['Fac'])
        link = links.new(ramp.outputs["Color"], diffuse.inputs["Color"])
        link = links.new(diffuse.outputs["BSDF"], output.inputs["Surface"])
    

    def __call__(self, scene, depsgraph=None):
        if not self.check_valid():
            return
        frame_number = scene.frame_current
        frame_number = max(frame_number,self.start)
        frame_number = min(frame_number,self.end)
        frame_number -= self.start
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
        emitter_object = self.get_obj()
        if len(mesh.points) != self.particle_num:
            self.particle_num = len(mesh.points)
            emitter_object.particle_systems[0].settings.count = self.particle_num

        #  update location info
        if depsgraph is None:
            #  wish this line will never be executed
            show_message_box("it shouldn't happen")
            depsgraph = bpy.context.evaluated_depsgraph_get()

        particle_systems = emitter_object.evaluated_get(
            depsgraph).particle_systems
        particles = particle_systems[0].particles

        points_pos = np.zeros((self.particle_num, 4))
        points_pos[:, -1] = 1
        points_pos[:, :3] = mesh.points
        transform_matrix = np.array(emitter_object.matrix_world)
        points_pos = points_pos @ np.transpose(transform_matrix)
        points_pos = points_pos[:, :3]
        particles.foreach_set("location", points_pos.ravel())

        # update rendering and color(velocity) info
        #  The idea here is to use velocity of particles to store the information of color attributes, because particles position are manually set, so the velocity has no visual effect. And later, use velocity in particle_shading_node, to draw the color. 
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
        
        name = self.get_sphere_obj_name()
        if name and  name in bpy.data.objects:
            sphere_obj = bpy.data.objects[name]
            sphere_obj.hide_set(False)
            sphere_obj.hide_viewport = False
            sphere_obj.hide_select = False
            sphere_obj.select_set(True)
            bpy.ops.object.delete()
        bpy.ops.object.select_all(action="DESELECT")

        name = self.get_obj_name()
        if name and  name in bpy.data.objects:
            bpy.data.objects[name].select_set(True)
            bpy.ops.object.delete()
        bpy.ops.object.select_all(action="DESELECT")
        # if self.sphere_obj_name in bpy.data.objects:
        #     sphere_obj = bpy.data.objects[self.sphere_obj_name]
        #     sphere_obj.hide_set(False)
        #     sphere_obj.hide_viewport = False
        #     sphere_obj.hide_select = False
        #     sphere_obj.select_set(True)
        #     bpy.ops.object.delete() 

    def set_radius(self, r):
        particles_setting = bpy.data.particles[self.particle_settings_name]
        particles_setting.particle_size = r
        particles_setting.display_size = r

    def set_max_value(self, r):
        self.max_value = r
        # material = bpy.data.materials[self.material_name]
        # material.node_tree.nodes[4].inputs[1].default_value = 1/ (self.max_value - self.min_value)

    def set_min_value(self, r):
        self.min_value = r
        # material = bpy.data.materials[self.material_name]
        # material.node_tree.nodes[3].inputs[1].default_value = self.min_value
        # material.node_tree.nodes[4].inputs[1].default_value = 1/ (self.max_value - self.min_value)

    def update_display(self, method):
        particles_setting = bpy.data.particles[self.particle_settings_name]
        particles_setting.display_method = method
    
    def get_obj(self):
        name = self.get_obj_name()
        if name:
            return bpy.data.objects[name]
        return None
    
    def check_valid(self):
        if not self.get_obj_name():
            return False
        return True
    
    def get_obj_name(self):
        for obj in bpy.data.objects:
            if obj.type =="MESH" and len(obj.particle_systems)>0 and obj.particle_systems[0].settings.name ==self.particle_settings_name:
                    return obj.name
        return None

    def get_sphere_obj_name(self):
        particles_setting = bpy.data.particles[self.particle_settings_name]
        if particles_setting.instance_object:
            return particles_setting.instance_object.name
        return None