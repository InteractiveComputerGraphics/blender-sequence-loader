# bl_info = {
#     "name": "MeshioImporterTool",
#     "description": "Importer for meshio supported mesh files.",
#     "author": "Hantao Hui",
#     "version": (1, 0),
#     "blender": (2, 90, 0),
#     "warning": "",
#     "support": "COMMUNITY",
#     "category": "Import-Export",
# }

import bpy
import bmesh
import numpy as np
from bpy.app.handlers import persistent
import meshio
import fileseq

'''
====================Utility Functions=====================================
'''

def show_message_box(message="", title="Message Box", icon="INFO"):
    '''
    It shows a small window to display the error message and also print it the console
    '''
    def draw(self, context):
        self.layout.label(text=message)

    print(message)
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)

def clear_screen():
    import os
    os.system("cls")

def check_type(fs):
    mesh=meshio.read(fs)
    if mesh.cells[0].type == "vertex":
        return "particle"
    elif mesh.cells[0].type == "triangle":
        return "mesh"

'''
====================Importer Classes=====================================
'''

class particle_importer:
    def __init__(self, fileseq, rotation= np.array([[1, 0, 0], [0, 0, 1], [0, 1, 0]]),emitter_obj_name=None,sphere_obj_name=None,material_name=None):

        # self.path=path
        self.fileseq=fileseq
        self.rotation=rotation
        self.render_attributes = []  # all the possible attributes, and type
        self.used_render_attribute = None  # the attribute used for rendering
        self.min_v = 0 # the min value of this attribute
        self.max_v = 0 # the max value of this attribute
        self.emitterObject =None
        self.sphereObj = None
        if not emitter_obj_name or not sphere_obj_name or not material_name:
            self.init_particles()
        else:
            self.emitterObject=bpy.data.objects[emitter_obj_name]
            self.sphereObj=bpy.data.objects[sphere_obj_name]
            self.material=bpy.data.materials[material_name]
  
    def init_particles(self):
        # create emitter object
        bpy.ops.mesh.primitive_cube_add(enter_editmode=False, location=(0, 0, 0))
        self.emitterObject = bpy.context.active_object
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
        # self.emitterObject.particle_systems[0].settings.instance_object = bpy.data.objects[self.sphereObj.name]
        self.emitterObject.particle_systems[0].settings.instance_object = self.sphereObj

        self.read_first_frame()

    def init_materials(self):
        nodes = self.material.node_tree.nodes
        links = self.material.node_tree.links
        nodes.clear()
        links.clear()

        output = nodes.new(type="ShaderNodeOutputMaterial")
        diffuse = nodes.new(type="ShaderNodeBsdfDiffuse")
        link = links.new(diffuse.outputs["BSDF"], output.inputs["Surface"])
        particleInfo = nodes.new(type="ShaderNodeParticleInfo")

        vecMath = nodes.new(type="ShaderNodeVectorMath")
        vecMath.operation = "DOT_PRODUCT"

        math1 = nodes.new(type="ShaderNodeMath")
        math1.operation = "SQRT"
        math2 = nodes.new(type="ShaderNodeMath")
        math2.operation = "MULTIPLY"
        math2.inputs[1].default_value = 0.1
        # math2.use_clamp = True

        ramp = nodes.new(type="ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].color = (0, 0, 1, 1)

        link = links.new(particleInfo.outputs["Velocity"], vecMath.inputs[0])
        link = links.new(particleInfo.outputs["Velocity"], vecMath.inputs[1])

        link = links.new(vecMath.outputs["Value"], math1.inputs[0])
        link = links.new(math1.outputs["Value"], math2.inputs[0])
        link = links.new(math2.outputs["Value"], ramp.inputs["Fac"])
        link = links.new(ramp.outputs["Color"], diffuse.inputs["Color"])

    def read_first_frame(self):
        try:
            mesh = meshio.read(
                self.fileseq[0]
            )
        except Exception as e:
            show_message_box("Can't read first frame file",icon="ERROR")
            print(str(e))

        self.emitterObject.particle_systems[0].settings.count = len(mesh.points)

        depsgraph = bpy.context.evaluated_depsgraph_get()
        particle_systems = self.emitterObject.evaluated_get(depsgraph).particle_systems
        particles = particle_systems[0].particles

        points_pos = mesh.points @ self.rotation

        particles.foreach_set("location", points_pos.ravel())

        if mesh.point_data:
            for k in mesh.point_data.keys():
                self.render_attributes.append(k)
        else:
            show_message_box(
                "no attributes avaible, all particles will be rendered as the same color"
            )
        # particles.foreach_set("velocity", [0]*3*len(mesh.points))

    def __call__(self, scene, depsgraph=None):
        frame_number = scene.frame_current
        frame_number = frame_number % len(self.fileseq) - 1
        try:
            mesh = meshio.read(
                self.fileseq[frame_number]
            )
        except:
            print("file: ", end="")
            print(self.fileseq[frame_number])
            print(" does not exist, this file will be skipped")
            return
        

        #  update location info
        particle_num = len(mesh.points)
        self.emitterObject.particle_systems[0].settings.count = particle_num

        if depsgraph is None:
            #  wish this line will never be executed
            print("it shouldn't happen")
            depsgraph = bpy.context.evaluated_depsgraph_get()

        particle_systems = self.emitterObject.evaluated_get(depsgraph).particle_systems
        particles = particle_systems[0].particles
        points_pos = mesh.points @ self.rotation
        particles.foreach_set("location", points_pos.ravel())


        # update rendering and color(velocity) info
        scaling_node = self.material.node_tree.nodes.get("Math.001").inputs[1]
        if self.used_render_attribute:
            att_str = self.used_render_attribute
            att_data = mesh.point_data[att_str]
            if len(att_data.shape) >= 3:
                #  normally, this one shouldn't happen
                show_message_box("attribute error: higher than 3 dimenion of attribute",icon="ERROR")
            elif len(att_data.shape) == 2:
                a, b = att_data.shape
                if b > 3:
                    show_message_box(
                        "attribute error: currently unsupport attributes more than 3 column",icon="ERROR"
                    )
                else:
                    #  The attribute as a vector with 1-3 elements
                    #  extend the attribute to 3-element np array, and store it in velocity attribute
                    vel_att = np.zeros((particle_num, 3))
                    vel_att[:, :b] = att_data

                    self.min_v = np.min(np.linalg.norm(vel_att, axis=1))
                    self.max_v = np.max(np.linalg.norm(vel_att, axis=1))

                    particles.foreach_set("velocity", vel_att.ravel())
                    scaling_node.default_value = 1.0 / self.max_v
            elif len(att_data.shape) == 1:
                # The attribute as a plain scalar value
                #  extend the attribute to 3-element np array, and store it in velocity attribute
                point_data_reshape = np.reshape(
                    att_data, (particle_num, -1)
                )
                vel_att = np.zeros((particle_num, 3))
                vel_att[:, :1] = point_data_reshape

                self.min_v = np.min(np.linalg.norm(vel_att, axis=1))
                self.max_v = np.max(np.linalg.norm(vel_att, axis=1))
                particles.foreach_set("velocity", vel_att.ravel())

                scaling_node.default_value = 1.0 / self.max_v

        # self.emitterObject.particle_systems[0].settings.frame_end = 0 # !! so velocity has no effect on the position any more, and velocity can be used for rendering

    def get_color_attribute(self):
        return self.render_attributes

    def set_color_attribute(self, attribute_str):
        if not attribute_str:
            return
        if attribute_str in self.render_attributes:
            self.used_render_attribute = attribute_str
        else:
            print(
                "attributes error: this attributs is not available in 1st frame of file"
            )

    def get_minmax(self):
        return self.min_v, self.max_v

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

    def set_radius(self,r ):
        self.emitterObject.particle_systems[0].settings.particle_size = r

class mesh_importer:
    def __init__(self,fileseq,rotation=np.array([[1,0,0],[0,0,1],[0,1,0]])):
        # self.path = path
        self.name=fileseq.basename()+"@"+fileseq.extension()
        self.fileseq = fileseq
        self.rotation = rotation
        self.mesh= None
        self.obj = None
        self.init_mesh()


    def create_face_data(self,meshio_cells):
        # todo: support other mesh structure, such as tetrahedron
        return meshio_cells[0][1]


    def load_mesh(self,total_path):
        try:
            meshio_mesh=meshio.read(total_path)
        except:
            print("file is missing : ",total_path)
            return 
        
        mesh_vertices=meshio_mesh.points
        vertices_count=len(meshio_mesh.points)
        mesh_faces=self.create_face_data(meshio_mesh.cells)

        if self.mesh:
            # remove all the vertices from the mesh
            bm=bmesh.new()
            bm.from_mesh(self.mesh)
            bm.clear()    
            bm.to_mesh(self.mesh)
            bm.free()
        else:
            self.mesh=bpy.data.meshes.new(name=self.name)
            new_object = bpy.data.objects.new(self.name, self.mesh)
            bpy.data.collections[0].objects.link(new_object)
            self.obj=new_object

        self.mesh.vertices.add(vertices_count)
 
        pos=meshio_mesh.points @ self.rotation

        self.mesh.vertices.foreach_set("co",pos.ravel())
            
        # code from ply impoter of blender, https://github.com/blender/blender-addons/blob/master/io_mesh_ply/import_ply.py#L363
        loops_vert_idx = []
        faces_loop_start = []
        faces_loop_total = []
        lidx = 0
        for f in mesh_faces:
            nbr_vidx = len(f)
            loops_vert_idx.extend(f)
            faces_loop_start.append(lidx)
            faces_loop_total.append(nbr_vidx)
            lidx += nbr_vidx

        self.mesh.loops.add(len(loops_vert_idx))
        self.mesh.polygons.add(len(mesh_faces))

        self.mesh.loops.foreach_set("vertex_index", loops_vert_idx)
        self.mesh.polygons.foreach_set("loop_start", faces_loop_start)
        self.mesh.polygons.foreach_set("loop_total", faces_loop_total)

        self.mesh.update()
        self.mesh.validate()

    def init_mesh(self):
        total_path=self.fileseq[0]
        self.load_mesh(total_path)
        
    def __call__(self, scene, depsgraph=None ):
        frame_number=scene.frame_current
        frame_number=frame_number % len(self.fileseq)
        total_path=self.fileseq[frame_number]
        self.load_mesh(total_path)
    def get_color_attribute(self):
        pass
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
        


'''
====================Addon Static Memory=====================================
'''

importer = None
importer_list= []
file_seq = []

'''
====================Addon Update and Callback Functions=====================================
'''

def callback_render_attribute(self, context):
    attr_items = [("None", "None", "")]
    if importer and importer.get_color_attribute():
        attrs = importer.get_color_attribute()
        for a in attrs:
            attr_items.append((a, a, ""))
    return attr_items

def callback_fileseq(self, context):
    return file_seq

def update_path(self, context):
    global file_seq
    p = context.scene.my_tool.importer.path
    f = fileseq.findSequencesOnDisk(p)
    if not f:
        show_message_box("animation sequences not detected", icon="ERROR")
        return
    if len(f) >= 20:
        message = "There is something wrong in this folder, too many file sequences detected.\n\
        The problem could be the pattern is not recognized correctly, please sepcify the pattern manually."
        show_message_box("message", icon="ERROR")
        print(message)
        file_seq = [("Manual", "Manual, use pattern above", "")]
        return
    for seq in f:
        file_seq=[]
        file_seq.append((str(seq), seq.basename()+"@"+seq.extension(), ""))

def update_color_fields(self, context):
    scene = context.scene
    importer_prop = scene.my_tool.importer
    if importer_prop.render != "None":
        importer.set_color_attribute(importer_prop.render)
    else:
        importer.set_color_attribute(None)

def update_fileseq(self, context):
    file_seq_items_name = context.scene.my_tool.importer.fileseq
    ind = 0
    p = context.scene.my_tool.importer.path
    global file_seq

    f = None
    if file_seq_items_name == "Manual":
        try:
            pattern = context.scene.my_tool.importer.pattern
            f = fileseq.findSequenceOnDisk(p + "\\" + pattern)
        except:
            show_message_box("can't find this sequence: " + pattern, icon="ERROR")
    else:
        
        f=fileseq.findSequenceOnDisk(file_seq_items_name)

    if f:
        # name = f.basename()
        start = f.start()
        end = f.end()
        # extension = f.extension()

        #  pre-check the content of file content
        try:
            mesh = meshio.read(f[0])
            if len(mesh.cells) > 1:
                print("unsupport multi-cell files")
                return

            # context.scene.my_tool.importer.name = f.basename()
            # context.scene.my_tool.importer.start = f.start()
            # context.scene.my_tool.importer.end = f.end()
            # context.scene.my_tool.importer.extension = f.extension()
            if mesh.cells[0].type == "vertex":
                context.scene.my_tool.importer.type = "particle"
            else:
                # print("todo: it should be triangle mesh here")
                context.scene.my_tool.importer.type = "mesh"
        except:
            show_message_box("can't find mesh info from the file: "+p[0])
    return

def update_particle_radius(self,context):
    global importer
    if not isinstance(importer, particle_importer):
        show_message_box("The importer is not correct")
    r = context.scene.my_tool.importer.particle_radius
    importer.set_radius(r) 



'''
====================Addon Properties=====================================
'''

class importer_properties(bpy.types.PropertyGroup):

    path: bpy.props.StringProperty(
        name="Path",
        default="C:\\Users\\hui\\Desktop\\output\\DamBreakModel\\vtk\\",
        subtype="DIR_PATH",
        update=update_path,
    )
    fileseq: bpy.props.EnumProperty(
        name="File Sequences",
        description="Please choose the file sequences you want",
        items=callback_fileseq,
        update=update_fileseq,
    )
    pattern: bpy.props.StringProperty(name="Pattern")
    # name: bpy.props.StringProperty(name="Name")
    # extension: bpy.props.StringProperty(name="Extension")
    # start: bpy.props.IntProperty(name="start", default=0)
    # end: bpy.props.IntProperty(name="end", default=0)
    type: bpy.props.EnumProperty(
        name="Type",
        description="choose particles or mesh",
        items=[("mesh", "Add Mesh", ""), ("particle", "Add Particles", "")],
    )
    render: bpy.props.EnumProperty(
        name="Color Field",
        description="choose attributes used for rendering",
        items=callback_render_attribute,
        update=update_color_fields,
    )

    min_value: bpy.props.FloatProperty(
        name="Min", description="min value of this property"
    )
    max_value: bpy.props.FloatProperty(
        name="Max", description="max value of this property"
    )
    particle_radius: bpy.props.FloatProperty(
        name="radius", description="radius of particles",default=0.01,update=update_particle_radius,min=0,precision=6
    )

    # the final used fileseq, needed when reloading the .blender file
    init: bpy.props.BoolProperty(name="Initlized",default=False)
    used_fs :bpy.props.StringProperty(name="Used File Sequence") 
    
    particle_emitter_obj_name: bpy.props.StringProperty(name="Particle Emitter Obj Name") 
    particle_sphere_obj_name: bpy.props.StringProperty(name="Particle Sphere Obj Name") 
    particle_material_name : bpy.props.StringProperty(name="Particle Material Obj Name")


def update_min_max(self, context):
    global importer
    if not importer:
        return
    min_v, max_v = importer.get_minmax()
    context.scene.my_tool.importer.min_value = min_v
    context.scene.my_tool.importer.max_value = max_v


class color_attribtue(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name='color attr')



class imported_seq_properties(bpy.types.PropertyGroup):
    pattern: bpy.props.StringProperty(name='pattern', description="pattern, using absolute path",default='test')
    used_color_attribute: bpy.props.PointerProperty(type=color_attribtue)
    all_attributes: bpy.props.CollectionProperty(type=color_attribtue)
    start : bpy.props.IntProperty(name='start', description='start frame number')
    end : bpy.props.IntProperty(name='end', description='end frame number')
    length: bpy.props.IntProperty(name='length', description='total frame number')
    attribute_count: bpy.props.IntProperty(name='attribute count',description='the number of all avaiable attributes')

class tool_properties(bpy.types.PropertyGroup):
    importer: bpy.props.PointerProperty(type=importer_properties)
    imported: bpy.props.CollectionProperty(type=imported_seq_properties)
    imported_num: bpy.props.IntProperty(name='imported count',description='the number of all imported sequences',default=0)









'''
====================Addon Panels=====================================
'''

class SEQUENCE_UL_list(bpy.types.UIList):
    # The draw_item function is called for each item of the collection that is visible in the list.
    #   data is the RNA object containing the collection,
    #   item is the current drawn item of the collection,
    #   icon is the "computed" icon for the item (as an integer, because some objects like materials or textures
    #   have custom icons ID, which are not available as enum items).
    #   active_data is the RNA object containing the active property for the collection (i.e. integer pointing to the
    #   active item of the collection).
    #   active_propname is the name of the active property (use 'getattr(active_data, active_propname)').
    #   index is index of the current item in the collection.
    #   flt_flag is the result of the filtering process for this item.
    #   Note: as index and flt_flag are optional arguments, you do not have to use/declare them here if you don't
    #         need them.
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ob = data
        slot = item
        ma=item
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # You should always start your row layout by a label (icon + text), or a non-embossed text field,
            # this will also make the row easily selectable in the list! The later also enables ctrl-click rename.
            # We use icon_value of label, as our given icon is an integer value, not an enum ID.
            # Note "data" names should never be translated!
            if ma:
                layout.prop(ma, "pattern",text='Pattern: ',emboss=False)
                # , emboss=False, icon_value=icon)
                # , )
            else:
                layout.label(text="", translate=False, icon_value=icon)
    #     # 'GRID' layout type should be as compact as possible (typically a single icon!).
    #     #  deal with this later
    #     # elif self.layout_type in {'GRID'}:
    #     #     layout.alignment = 'CENTER'
    #     #     layout.label(text="", icon_value=icon)






class sequence_list_panel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Sequences"
    bl_idname = "SEQUENCES_PT_list"
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"
    bl_category = "Meshio Importer"
    bl_parent_id = "MESHIO_IMPORT_PT_panel"



    def draw(self, context):
        layout = self.layout

        # imported = context.scene.my_tool.imported
        imported_num = context.scene.my_tool.imported_num
        # template_list now takes two new args.
        # The first one is the identifier of the registered UIList to use (if you want only the default list,
        # with no custom draw code, use "UI_UL_list").
        layout.template_list("SEQUENCE_UL_list", "", context.scene.my_tool, 'imported', context.scene.my_tool, "imported_num")
                                            # data ,  item, icon,          active_data,    active_propname              
        # The second one can usually be left as an empty string.
        # It's an additional ID used to distinguish lists in case you
        # use the same list several times in a given area.








class MESHIO_IMPORT_PT_main_panel(bpy.types.Panel):
    bl_label = "Import Panel"
    bl_idname = "MESHIO_IMPORT_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Meshio Importer"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        importer_prop = scene.my_tool.importer

        layout.prop(importer_prop, "path")
        layout.prop(importer_prop, "pattern")
        layout.prop(importer_prop, "fileseq")

        # layout.prop(importer_prop, "start",emboss=False)
        # layout.prop(importer_prop, "end",emboss=False)
        layout.prop(importer_prop, "type")

        layout.operator("sequence.load")
        layout.operator("sequence.clear")
        layout.operator("test.test")


# class PARTICLE_PT_panel(bpy.types.Panel):
#     bl_label = "Particles Settings"
#     bl_idname = "PARTICLE_PT_panel"
#     bl_space_type = "VIEW_3D"
#     bl_region_type = "UI"
#     bl_category = "Meshio Importer"
#     bl_parent_id = "MESHIO_IMPORT_PT_panel"

#     def draw(self, context):
#         t = context.scene.my_tool.importer.type
#         if t != "particle":
#             return
#         else:
#             scene = context.scene
#             importer_prop = scene.my_tool.importer
#             layout = self.layout
#             layout.prop(importer_prop, "render")
#             layout.prop(importer_prop, "min_value")
#             layout.prop(importer_prop, "max_value")
#             layout.prop(importer_prop, "particle_radius")



# class MESH_PT_panel(bpy.types.Panel):
#     bl_label = "Mesh Settings"
#     bl_idname = "MESH_PT_panel"
#     bl_space_type = "VIEW_3D"
#     bl_region_type = "UI"
#     bl_category = "Meshio Importer"
#     bl_parent_id = "MESHIO_IMPORT_PT_panel"

#     def draw(self, context):
#         t = context.scene.my_tool.importer.type
#         if t != "Mesh":
#             pass
#         else:
#             print("todo: mesh settins")
#             pass

'''
====================Addon Operators=====================================
'''

class particle_OT_clear(bpy.types.Operator):
    bl_label = "Remove Sequence"
    bl_idname = "sequence.clear"

    def execute(self, context):
        global importer
        if importer:
            importer.clear()
        bpy.app.handlers.frame_change_post.clear()
        importer=None
        context.scene.my_tool.importer.init=False
        return {"FINISHED"}



class DUMMY_OT_test(bpy.types.Operator):
    bl_label = "A button for testing"
    bl_idname = "test.test"

    def execute(self, context):
        print('?')
        i= context.scene.my_tool.imported
        i.add()
        context.scene.my_tool.imported_num+=1
        return {"FINISHED"}





class meshio_loader_OT_load(bpy.types.Operator):
    bl_label = "Load Sequences"
    bl_idname = "sequence.load"

    def execute(self, context):
        global count
        global importer
        scene = context.scene
        importer_prop = scene.my_tool.importer
        imported_prop= scene.my_tool.imported
        imported_prop_num= scene.my_tool.imported_num
        fs=importer_prop.fileseq
        if fs=="Manual":
            fs=importer_prop.path+'\\'+importer_prop.pattern
        # save the status when reopen the .blend file
        # importer_prop.used_fs = fs
        
        fs=fileseq.findSequenceOnDisk(fs)

        if importer_prop.type == "particle":
            if importer:
                importer_list.append(importer)
                importer=None
             
            importer = particle_importer(fs)

            importer_prop.particle_emitter_obj_name=importer.emitterObject.name
            importer_prop.particle_sphere_obj_name=importer.sphereObj.name
            importer_prop.particle_material_name=importer.material.name
            
            imported_prop.add()
            imported_prop[imported_prop_num].pattern=fs.dirname()+fs.basename()+"@"+fs.extension()
            scene.my_tool.imported_num+=1




            bpy.app.handlers.frame_change_post.append(importer)
            # bpy.app.handlers.frame_change_post.append(update_min_max)

        if importer_prop.type == "mesh":
            if importer:
                importer_list.append(importer)
                importer=None
            importer = mesh_importer(fs)
            imported_prop.add()
            imported_prop[imported_prop_num].pattern=fs.dirname()+fs.basename()+"@"+fs.extension()
            scene.my_tool.imported_num+=1
            bpy.app.handlers.frame_change_post.append(importer)
        
        importer_prop.init=True
        return {"FINISHED"}




'''
====================Main Fun=====================================
'''



classes = [
    importer_properties,
    MESHIO_IMPORT_PT_main_panel,
    meshio_loader_OT_load,
    # PARTICLE_PT_panel,
    # MESH_PT_panel,
    particle_OT_clear,
    sequence_list_panel,
    SEQUENCE_UL_list,
    color_attribtue,
    imported_seq_properties,
    tool_properties,
    DUMMY_OT_test,

]

@persistent
def load_post(scene):
    importer_prop = bpy.context.scene.my_tool.importer
    global importer
    if importer_prop.init:
        fs=fileseq.findSequenceOnDisk(importer_prop.used_fs)
        if importer:
            bpy.ops.sequence.clear()
        file_type=check_type(fs[0])
        if file_type=='particle':
            importer=particle_importer(fs,emitter_obj_name=importer_prop.particle_emitter_obj_name,sphere_obj_name=importer_prop.particle_sphere_obj_name,material_name=importer_prop.particle_material_name)
            bpy.app.handlers.frame_change_post.append(importer)
            bpy.app.handlers.frame_change_post.append(update_min_max)
        elif file_type=='mesh':
            importer=mesh_importer(fs)
            bpy.app.handlers.frame_change_post.append(importer)

        

    importer_prop.init=True
    



def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.my_tool = bpy.props.PointerProperty(type=tool_properties)
    bpy.app.handlers.load_post.append(load_post)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.my_tool


if __name__ == "__main__":
    register()
    # unregister()
