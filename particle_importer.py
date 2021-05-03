import meshio
import numpy as np
import bpy
class particle_importer:
    def __init__(self, path,name, start_file_num,end_file_num,extension):
        self.path = path
        self.name = name
        
        self.start_file_num=start_file_num
        self.end_file_num = end_file_num
        self.extension = extension

        self.init_particles()
        self.render_attributes={}  # all the possible attributes, and type
        self.used_render_attribute=None # the attribute used for rendering



        

    def init_particles(self):
        bpy.ops.mesh.primitive_cube_add(enter_editmode=False, location=(0, 0, 0))

        self.emitterObject = bpy.context.active_object
        self.emitterObject.hide_viewport = False
        self.emitterObject.hide_render = False
        self.emitterObject.hide_select = False
        bpy.ops.object.modifier_add(type='PARTICLE_SYSTEM')
        
        #  turn off the gravity
        bpy.data.particles["ParticleSettings"].effector_weights.gravity = 0


        # make the cube invincible
        bpy.context.object.show_instancer_for_render = False
        bpy.context.object.show_instancer_for_viewport = False


        self.emitterObject.particle_systems[0].settings.frame_start = 0
        self.emitterObject.particle_systems[0].settings.frame_end = 0
        self.emitterObject.particle_systems[0].settings.lifetime = 1000
        # emitterObject.particle_systems[0].settings.particle_size = 0.05
        # emitterObject.particle_systems[0].settings.display_size = 100

        bpy.ops.mesh.primitive_uv_sphere_add(radius=1, enter_editmode=False, location=(0, 0, 0))
        bpy.ops.object.shade_smooth()
        self.sphereObj = bpy.context.active_object
        self.sphereObj.hide_set(True)
        self.sphereObj.hide_viewport = False
        self.sphereObj.hide_render = True
        self.sphereObj.hide_select = True



        # self.material = bpy.data.materials.new( "particle_material" )

        # material.use_nodes = True
        # nodes = material.node_tree.nodes
        # links = material.node_tree.links
        # nodes.clear()
        # links.clear()

        # output = nodes.new( type = 'ShaderNodeOutputMaterial' )
        # diffuse = nodes.new( type = 'ShaderNodeBsdfDiffuse' )
        # link = links.new( diffuse.outputs['BSDF'], output.inputs['Surface'] )
        # particleInfo = nodes.new( type = 'ShaderNodeParticleInfo' )


        # vecMath = nodes.new( type = 'ShaderNodeVectorMath' )
        # vecMath.operation = 'DOT_PRODUCT'

        # math1 = nodes.new( type = 'ShaderNodeMath' )
        # math1.operation = 'SQRT'
        # math2 = nodes.new( type = 'ShaderNodeMath' )
        # math2.operation = 'MULTIPLY'
        # math2.inputs[1].default_value = 0.1  
        # # math2.use_clamp = True


        # ramp = nodes.new( type = 'ShaderNodeValToRGB' )
        # ramp.color_ramp.elements[0].color = (0, 0, 1, 1)

        # link = links.new( particleInfo.outputs['Location'], vecMath.inputs[0] )
        # link = links.new( particleInfo.outputs['Location' ], vecMath.inputs[1] )

        # link = links.new( vecMath.outputs['Value'], math1.inputs[0] )
        # link = links.new( math1.outputs['Value'], math2.inputs[0] )
        # link = links.new( math2.outputs['Value'], ramp.inputs['Fac'] )
        # link = links.new( ramp.outputs['Color'], diffuse.inputs['Color'] )


        # emitterObject.active_material = material
        # sphereObj.active_material = material


        self.emitterObject.particle_systems[0].settings.render_type = 'OBJECT'
        self.emitterObject.particle_systems[0].settings.instance_object = bpy.data.objects[self.sphereObj.name]


        mesh=meshio.read(self.path+self.name+str(self.start_file_num)+self.extension)
        self.emitterObject.particle_systems[0].settings.count = len(mesh.points)


        depsgraph = bpy.context.evaluated_depsgraph_get()
        particle_systems = self.emitterObject.evaluated_get(depsgraph).particle_systems
        particles = particle_systems[0].particles

        points_pos=  mesh.points @ np.array([[1,0,0],[0,0,1],[0,1,0]])
        
        particles.foreach_set("location", points_pos.ravel())
        particles.foreach_set("velocity",[0]*len(mesh.points)*3)
        


    def __call__(self, scene, depsgraph=None ):
        frame_number = scene.frame_current
        frame_number = frame_number % self.end_file_num -1 
        try:
            mesh=meshio.read(self.path+self.name+str(frame_number)+self.extension)
            print(frame_number)
        except:
            print("file: ",end="")
            print(" does not exist, this file will be skipped")
            return 
        

        # self.emitterObject = bpy.data.objects["Cube"]
        self.emitterObject.particle_systems[0].settings.count = len(mesh.points)

        if depsgraph is None:
            depsgraph = bpy.context.evaluated_depsgraph_get()
        particle_systems = self.emitterObject.evaluated_get(depsgraph).particle_systems
        particles = particle_systems[0].particles

        points_pos=  mesh.points @ np.array([[1,0,0],[0,0,1],[0,1,0]])
        
        particles.foreach_set("location", points_pos.ravel())
        particles.foreach_set("velocity",[0]*len(mesh.points)*3)


    def get_render_attribute(self):
        pass
