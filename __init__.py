bl_info = {
    "name": "MeshioImporterTool",
    "description": "Importer for meshio supported mesh files.",
    "author": "Hantao Hui",
    "version": (1, 0),
    "blender": (2, 90, 0),
    "warning": "",
    "support": "COMMUNITY",
    "category": "Import-Export",
}

import bpy
import bmesh
import numpy as np
from bpy.app.handlers import persistent
import meshio
import fileseq
import os
import sys

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
    os.system("cls")

def check_type(fs):
    try:
        mesh=meshio.read(fs)
        if mesh.cells[0].type == "vertex":
            return "particle"
        elif mesh.cells[0].type == "triangle":
            return "mesh"
    except:
        show_message_box("can't find mesh info from the file: "+fs)

# you can write your own color function here
# input: attributes you want to use for coloring, 
# the shape of input:  number of particles * dimension of attribute e.g. (6859,3) 6859 particles and each particle has a 3-d attribute 
# output: np array of color information, the same length as number of particles, the value should be normalized to [0,1]
def calculate_color(att_data:np.array) :
    #  here is my implementation
    if len(att_data.shape) >= 3:
#         #  normally, this one shouldn't happen
        show_message_box("attribute error: higher than 3 dimenion of attribute",icon="ERROR")

    elif len(att_data.shape) == 2:
        a, b = att_data.shape
        res=np.zeros(a,dtype=np.float32)
        res=np.linalg.norm(att_data, axis=1)
        res/=np.max(res)
        return res
    elif len(att_data.shape) == 1:
        res=np.copy(att_data)
        res/=np.max(res)
        return res

'''
====================Importer Classes=====================================
'''
class particle_importer:
    def __init__(self, fileseq, rotation= np.array([[1, 0, 0], [0, 0, 1], [0, 1, 0]]),emitter_obj_name=None,sphere_obj_name=None,material_name=None,tex_image_name=None,mesh_name=None):

        # self.path=path
        self.fileseq=fileseq
        self.name=fileseq.basename()+"@"+fileseq.extension()
        self.rotation=rotation
        self.render_attributes = []  # all the possible attributes, and type
        self.used_render_attribute = None  # the attribute used for rendering
        self.emitterObject =None
        self.sphereObj = None
        if not emitter_obj_name or not sphere_obj_name or not material_name or not tex_image or not mesh_name:
            self.init_particles()
        else:
            self.mesh=bpy.data.meshes[mesh_name]
            self.emitterObject=bpy.data.objects[emitter_obj_name]
            self.sphereObj=bpy.data.objects[sphere_obj_name]
            self.material=bpy.data.materials[material_name]
            self.tex_image=bpy.data.images[tex_image_name]
  
    def init_particles(self):
        try:
            meshio_mesh=meshio.read(self.fileseq[0])
        except:
            show_message_box("file is missing : "+self.fileseq[0],icon="ERROR")
            return 

        if meshio_mesh.point_data:
            for k in meshio_mesh.point_data.keys():
                self.render_attributes.append(k)
        else:
            show_message_box(
                "no attributes avaible, all particles will be rendered as the same color"
            )

        
        self.mesh=bpy.data.meshes.new(name=self.name+"_mesh")
        mesh_vertices=meshio_mesh.points
        self.particle_num = len(meshio_mesh.points)
        
        self.mesh.vertices.add(self.particle_num)
 
        pos=meshio_mesh.points @ self.rotation

        self.mesh.vertices.foreach_set("co",pos.ravel())
        new_object = bpy.data.objects.new(self.name, self.mesh)
        bpy.data.collections[0].objects.link(new_object)
        self.emitterObject=new_object

        bpy.context.view_layer.objects.active = self.emitterObject

        bpy.ops.object.particle_system_add()

        # basic settings for the particles
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

        output = nodes.new(type="ShaderNodeOutputMaterial")
        diffuse = nodes.new(type="ShaderNodeBsdfDiffuse")
        particleInfo = nodes.new(type="ShaderNodeParticleInfo")
        math1 = nodes.new(type="ShaderNodeMath")
        math1.operation = "ADD"
        math1.inputs[1].default_value = 0.5
        math2 = nodes.new(type="ShaderNodeMath")
        math2.operation = "DIVIDE"
        math2.inputs[1].default_value = self.particle_num # this should be the number of particles       
        combine=nodes.new(type="ShaderNodeCombineXYZ")
        combine.inputs[1].default_value = 0
        combine.inputs[2].default_value = 0
        tex=nodes.new(type="ShaderNodeTexImage")
        
        link = links.new(particleInfo.outputs["Index"], math1.inputs[0])
        link = links.new(math1.outputs["Value"], math2.inputs[0])
        link = links.new(math2.outputs["Value"], combine.inputs[0])
        link = links.new(combine.outputs["Vector"], tex.inputs["Vector"])
        link = links.new(tex.outputs["Color"], diffuse.inputs["Color"])
        link = links.new(diffuse.outputs["BSDF"], output.inputs["Surface"])
        self.tex_image=bpy.data.images.new('particle_tex_image',width=self.particle_num,height=1)
        tex.image=self.tex_image

    def __call__(self, scene,depsgraph=None):
        frame_number = scene.frame_current
        frame_number = frame_number % len(self.fileseq) 
        try:
            mesh = meshio.read(
                self.fileseq[frame_number]
            )
        except:
            show_message_box("file is missing : "+self.fileseq[frame_number],icon="ERROR")
            return 

        if len(mesh.points)!=self.particle_num: 
            self.particle_num=len(mesh.points)
            self.tex_image.generated_width=self.particle_num
        bm=bmesh.new()
        bm.from_mesh(self.mesh)
        bm.clear()    
        bm.to_mesh(self.mesh)
        bm.free()
        self.mesh.vertices.add(self.particle_num)
        pos=mesh.points @ self.rotation
        self.mesh.vertices.foreach_set("co",pos.ravel())

        if self.used_render_attribute:
            att_str = self.used_render_attribute
            att_data = mesh.point_data[att_str]
            color=calculate_color(att_data)
            pixels=np.zeros((self.particle_num,4),dtype=np.float32)
            pixels[:,0]=color
            pixels[:,3]=1 
            self.tex_image.pixels.foreach_set( pixels.ravel())
        else:
            pixels=[0] * 4*self.particle_num
            self.tex_image.pixels.foreach_set( pixels)


    def get_color_attribute(self):
        return self.render_attributes

    def set_color_attribute(self, attribute_str):
        if not attribute_str:
            self.used_render_attribute=None
            return
        if attribute_str in self.render_attributes:
            self.used_render_attribute = attribute_str
        else:
            show_message_box(
                "attributes error: this attributs is not available in 1st frame of file"
            )

    def clear(self):
        bpy.ops.object.select_all(action="DESELECT")
        if self.emitterObject :
            self.emitterObject.select_set(True)
            bpy.ops.object.delete()
            self.emitterObject = None
            bpy.data.meshes.remove(self.mesh)
            self.mesh=None
        if self.sphereObj:
            bpy.data.meshes.remove(self.sphereObj.data)
            self.sphereObj = None
        for p in bpy.data.particles:
            if p.users == 0:
                bpy.data.particles.remove(p)
        if self.material:
            bpy.data.materials.remove(self.material)
            self.material=None
        if self.tex_image:
            bpy.data.images.remove(self.tex_image)
            self.tex_image=None

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
        self.material = None
        self.v_col=None
        self.used_color_attribute= None
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
        shade_scheme=False
        if self.mesh.polygons:
            shade_scheme=self.mesh.polygons[0].use_smooth
        bm=bmesh.new()
        bm.from_mesh(self.mesh)
        bm.clear()    
        bm.to_mesh(self.mesh)
        bm.free()

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
        self.mesh.polygons.foreach_set("use_smooth", [shade_scheme]*len(faces_loop_total))
        
        #  it will be extended to real data
        v_col=self.mesh.vertex_colors.new() # because everytime clear the vertices using bmesh, vertex color will be lost, and it has to be created again
        print(len(v_col.data))
        mesh_colors=[]
        r_min=np.min(meshio_mesh.points[:,0])
        r_max=np.max(meshio_mesh.points[:,0])
        r_slope=1/(r_max-r_min)
        g_min=np.min(meshio_mesh.points[:,1])  
        g_max=np.max(meshio_mesh.points[:,1])
        g_slope=1/(g_max-g_min)
        b_min=np.min(meshio_mesh.points[:,2])
        b_max=np.max(meshio_mesh.points[:,2])
        b_slope=1/(b_max-b_min)
        for index in mesh_faces:  # for each face
            for i in index:    # for each vertex in the face 
                mesh_colors.append( r_slope*(meshio_mesh.points[i][0]-r_min) )  # red color
                mesh_colors.append( g_slope *( meshio_mesh.points[i][1] -g_min))  # green color
                mesh_colors.append( b_slope*(meshio_mesh.points[i][2] -b_min))   # blue color
            
                    
        for i, col in enumerate(v_col.data):
            col.color=mesh_colors[i*3],0,0,1

        self.mesh.update()
        self.mesh.validate()

    def init_mesh(self):

        self.mesh=bpy.data.meshes.new(name=self.name)
        # create vertex_color and material

        self.material = bpy.data.materials.new(self.name+"_material")
        self.material.use_nodes = True
        nodes = self.material.node_tree.nodes
        links = self.material.node_tree.links
        nodes.clear()
        links.clear()
        output = nodes.new(type="ShaderNodeOutputMaterial")
        diffuse = nodes.new(type="ShaderNodeBsdfDiffuse") 
        link = links.new(diffuse.outputs["BSDF"], output.inputs["Surface"])
        vertex_color_node = nodes.new(type="ShaderNodeVertexColor")
        link = links.new(vertex_color_node.outputs["Color"], diffuse.inputs["Color"])
        #  create object
        new_object = bpy.data.objects.new(self.name, self.mesh)
        bpy.data.collections[0].objects.link(new_object)
        self.obj=new_object
        self.obj.active_material=self.material

        total_path=self.fileseq[0]
        self.load_mesh(total_path)
        
    def __call__(self, scene, depsgraph=None ):
        frame_number=scene.frame_current
        frame_number=frame_number % len(self.fileseq)
        total_path=self.fileseq[frame_number]
        self.load_mesh(total_path)
    def get_color_attribute(self):
        return self.color_attribtues
    def set_corlor_attribute(self,attr_name):
        if attr_name and attr_name in self.color_attribtues:
            self.used_color_attribute=attr_name

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
# file_seq = []

'''
====================Addon Update and Callback Functions=====================================
'''

def callback_color_attribute(self, context):
    attr_items=[('None','None','')]
    mytool=context.scene.my_tool
    item = mytool.imported[mytool.imported_num]
    for i in  item.all_attributes:
        attr_items.append((i.name,i.name,''))
        pass
    return attr_items


def update_color_attribute(self, context):
    mytool = context.scene.my_tool
    idx=mytool.imported_num

    importer=importer_list[idx]
    item=mytool.imported[idx]
    if item.all_attributes_enum != "None":
        importer.set_color_attribute(item.all_attributes_enum)
        item.used_color_attribute.name=item.all_attributes_enum
    else:
        importer.set_color_attribute(None)
        item.used_color_attribute.name='None'

def callback_fileseq(self, context):
    p = context.scene.my_tool.importer.path
    f = fileseq.findSequencesOnDisk(p)
    
    if not f:
        show_message_box("animation sequences not detected", icon="ERROR")
        return
    file_seq = [("Manual", "Manual, use pattern above", "")]
    if len(f) >= 20:
        message = "There is something wrong in this folder, too many file sequences detected.\n\
        The problem could be the pattern is not recognized correctly, please sepcify the pattern manually."
        # show_message_box(message, icon="ERROR")
    else:
        for seq in f:
            file_seq.append((str(seq), seq.basename()+"@"+seq.extension(), ""))
    return file_seq    


#  this function precheck and set the type of this sequence
def update_fileseq(self, context):
    file_seq_items_name = context.scene.my_tool.importer.fileseq
    f = None
    if file_seq_items_name == "Manual":
        try:
            p = context.scene.my_tool.importer.path
            pattern = context.scene.my_tool.importer.pattern
            f = fileseq.findSequenceOnDisk(p + "\\" + pattern)
        except:
            show_message_box("can't find this sequence: " + pattern, icon="ERROR")
    else:
        f=fileseq.findSequenceOnDisk(file_seq_items_name)
    if f:
        context.scene.my_tool.importer.type = check_type(f[0])


def update_particle_radius(self,context):
    idx =context.scene.my_tool.imported_num
    r = context.scene.my_tool.imported[idx].radius
    importer = importer_list[idx]
    importer.set_radius(r) 



'''
====================Addon Properties=====================================
'''

class importer_properties(bpy.types.PropertyGroup):
    path: bpy.props.StringProperty(
        name="Directory",
        default="C:\\Users\\hui\\Desktop\\output\\DamBreakModel\\vtk\\",
        subtype="DIR_PATH",
        description = "You need to go to the folder with the sequence, then click \"Accept\". ",
    )
    fileseq: bpy.props.EnumProperty(
        name="File Sequences",
        description="Please choose the file sequences you want",
        items=callback_fileseq,
        update=update_fileseq,
    )
    pattern: bpy.props.StringProperty(name="Pattern")
    type: bpy.props.EnumProperty(
        name="Type",
        description="choose particles or mesh",
        items=[("mesh", "Add Mesh", ""), ("particle", "Add Particles", "")],
    )

class color_attribtue(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name='color attr')



class imported_seq_properties(bpy.types.PropertyGroup):
    pattern: bpy.props.StringProperty(name='pattern', description="pattern, using absolute path",default='test')
    type: bpy.props.IntProperty(name='type',description='type of this sequence, particle or mesh, or other', default=0, min=0, max=1)
    used_color_attribute: bpy.props.PointerProperty(type=color_attribtue)
    all_attributes: bpy.props.CollectionProperty(type=color_attribtue)
    all_attributes_enum : bpy.props.EnumProperty(
        name="Color Field",
        description="choose attributes used for coloring",
        items=callback_color_attribute,
        update=update_color_attribute,
    )
    start : bpy.props.IntProperty(name='start', description='start frame number')
    end : bpy.props.IntProperty(name='end', description='end frame number')
    length: bpy.props.IntProperty(name='length', description='total frame number')
    attribute_count: bpy.props.IntProperty(name='attribute count',description='the number of all avaiable attributes')
    radius :bpy.props.FloatProperty(name='radius',description='raidus of the particles',default=0.01,update=update_particle_radius,min=0,precision=6)


class tool_properties(bpy.types.PropertyGroup):
    importer: bpy.props.PointerProperty(type=importer_properties)
    imported: bpy.props.CollectionProperty(type=imported_seq_properties)
    imported_num: bpy.props.IntProperty(name='imported count',description='the number of imported sequence, when selecting from ui list',default=0)









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
            if ma:
                layout.prop(ma, "pattern",text='Pattern: ',emboss=False)
            else:
                layout.label(text="", translate=False, icon_value=icon)






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
        mytool=context.scene.my_tool
        # template_list now takes two new args.
        # The first one is the identifier of the registered UIList to use (if you want only the default list,
        # with no custom draw code, use "UI_UL_list").
        row = layout.row()
        row.template_list("SEQUENCE_UL_list", "", context.scene.my_tool, 'imported', context.scene.my_tool, "imported_num")

        col = row.column(align=True)
        col.operator("sequence.remove", icon='REMOVE', text="")

        if len(mytool.imported) >0:
            item = mytool.imported[mytool.imported_num]
            for i in  item.all_attributes:
                # print(i.name)
                pass
            if item.type==0:
                info_part = layout.column()
                info_part.prop(item,'start')
                info_part.prop(item,'end')
                info_part.prop(item,'length')
                info_part.prop(item,'radius')
                info_part.prop(item,'all_attributes_enum')
                # info_part.prop(item,)

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
        layout.prop(importer_prop, "type")
        layout.operator("sequence.load")
'''
====================Addon Operators=====================================
'''

class particle_OT_clear(bpy.types.Operator):
    bl_label = "Remove Sequence"
    bl_idname = "sequence.remove"
    def execute(self, context):
        global importer
        global importer_list
        mytool=context.scene.my_tool
        idx=mytool.imported_num
        mytool.imported.remove(idx)
        bpy.app.handlers.frame_change_post.remove(importer_list[idx])
        if importer==importer_list[idx]:
            importer=None
        importer_list[idx].clear()
        del importer_list[idx]
        mytool.imported_num= max(mytool.imported_num-1,0)
        return {"FINISHED"}


class meshio_loader_OT_load(bpy.types.Operator):
    bl_label = "Load Sequences"
    bl_idname = "sequence.load"

    def execute(self, context):
        global importer
        global importer_list
        scene = context.scene
        importer_prop = scene.my_tool.importer
        imported_prop= scene.my_tool.imported
        fs=importer_prop.fileseq
        if fs=="Manual":
            fs=importer_prop.path+'\\'+importer_prop.pattern
        fs=fileseq.findSequenceOnDisk(fs)
        if importer_prop.type == "particle":
            if importer:
                importer=None
             
            importer = particle_importer(fs)
            importer_list.append(importer)
            
            imported_prop.add()
            imported_prop[-1].pattern=fs.dirname()+fs.basename()+"@"+fs.extension()
            imported_prop[-1].type=0
            imported_prop[-1].start=fs.start()
            imported_prop[-1].end=fs.end()
            imported_prop[-1].type=0
            imported_prop[-1].length=len(fs)
            for co_at in importer.get_color_attribute():
                imported_prop[-1].all_attributes.add()
                imported_prop[-1].all_attributes[-1].name=co_at

            bpy.app.handlers.frame_change_post.append(importer)

        if importer_prop.type == "mesh":
            if importer:
                importer=None
            importer = mesh_importer(fs)
            importer_list.append(importer)
            imported_prop.add()
            imported_prop[-1].pattern=fs.dirname()+fs.basename()+"@"+fs.extension()
            imported_prop[-1].type=1
            bpy.app.handlers.frame_change_post.append(importer)
        return {"FINISHED"}




'''
====================Main Fun=====================================
'''

classes = [
    importer_properties,
    MESHIO_IMPORT_PT_main_panel,
    meshio_loader_OT_load,
    particle_OT_clear,
    sequence_list_panel,
    SEQUENCE_UL_list,
    color_attribtue,
    imported_seq_properties,
    tool_properties,
]

@persistent
def load_post(scene):
    pass



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
