import bpy
import os


class SIMLOADER_UL_Obj_List(bpy.types.UIList):
    '''
    This controls the list of imported sequneces.
    '''

    def filter_items(self, context, data, property):
        objs = getattr(data, property)
        flt_flags = []
        #  not sure if I understand correctly about this
        #  see reference from https://docs.blender.org/api/current/bpy.types.UIList.html#advanced-uilist-example-filtering-and-reordering
        for o in objs:
            if o.SIMLOADER.init:
                flt_flags.append(self.bitflag_filter_item)
            else:
                flt_flags.append(0)
        flt_neworder = []
        return flt_flags, flt_neworder

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            layout.prop(item, "name", text='Name ', emboss=False)
        else:
            # actually, I guess this line of code won't be executed?
            layout.label(text="", translate=False, icon_value=icon)



class SIMLOADER_UL_Att_List(bpy.types.UIList):
    '''
    This controls the list of attributes available for this sequence
    '''
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            layout.enabled = False
            layout.prop(item, "name", text='Name ', emboss=False)
            obj = bpy.data.objects[context.scene.SIMLOADER.selected_obj_num]
            mesh = obj.data
            if mesh.SIMLOADER.split_norm_att_name and mesh.SIMLOADER.split_norm_att_name ==item.name:
                layout.label(text="using as split norm")

        else:
            # actually, I guess this line of code won't be executed?
            layout.label(text="", translate=False, icon_value=icon)


class SIMLOADER_List_Panel(bpy.types.Panel):
    '''
    This is the panel of imported sequences, bottom part of images/9.png
    '''
    bl_label = "Sequences Imported"
    bl_idname = "SIMLOADER_PT_list"
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"
    bl_category = "Sim Loader"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        sim_loader = context.scene.SIMLOADER
        row = layout.row()
        row.template_list("SIMLOADER_UL_Obj_List", "", bpy.data, "objects", sim_loader, "selected_obj_num", rows=2)
        layout.operator("sequence.edit")


class SIMLOADER_Settings(bpy.types.Panel):
    '''
    This is the panel of settings of selected sequence
    '''
    bl_label = "Settings"
    bl_idname = "SIMLOADER_PT_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"
    bl_category = "Sim Loader"
    bl_context = "objectmode"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        sim_loader = context.scene.SIMLOADER
        if sim_loader.selected_obj_num>=len(bpy.data.objects):
            return
        obj = bpy.data.objects[sim_loader.selected_obj_num]
        if not obj.SIMLOADER.init:
            return
        layout.label(text="Reset Geometry Nodes")
        box = layout.box()
        split = box.split()
        col1 = split.column()
        col1.alignment = 'RIGHT'
        col2 = split.column()
        col1.label(text="Material")
        col2.prop_search(sim_loader, 'material', bpy.data, 'materials', text="")
        box.label(text='Reset Geometry Nodes as')

        split = box.split()
        col1 = split.column()
        col2 = split.column()
        col3 = split.column()
        col1.operator('SIMLOADER.resetpt', text="Point Cloud")
        col2.operator('SIMLOADER.resetmesh', text="Mesh")
        col3.operator('SIMLOADER.resetins', text="Instances")


        # path settings
        layout.label(text="Path Information")
        box = layout.box()

        split = box.split()
        col1 = split.column()
        col1.alignment = 'RIGHT'
        col2 = split.column(align=False)

        col2.enabled = False
        col1.label(text='Relative')
        col2.prop(obj.SIMLOADER, 'use_relative', text="")
        col1.label(text='Pattern')
        col2.prop(obj.SIMLOADER, 'pattern', text="")
        

        # attributes settings
        layout.label(text="Attributes Settings")
        box = layout.box()
        row = box.row()
        row.template_list("SIMLOADER_UL_Att_List", "", obj.data, "attributes", sim_loader, "selected_attribute_num", rows=2)
        box.operator("SIMLOADER.setsplitnorm")
        box.operator("SIMLOADER.removesplitnorm",text="remove split norm")

        # advance settings
        layout.label(text="Advance Settings")
        box = layout.box()
        split = box.split()
        col1 = split.column()
        col1.alignment = 'RIGHT'
        col2 = split.column(align=False)
        col1.label(text="Enable Advance")
        col2.prop(obj.SIMLOADER, 'use_advance', text="")
        if obj.SIMLOADER.use_advance:
            col1.label(text='Script')
            col2.prop_search(obj.SIMLOADER, 'script_name', bpy.data, 'texts', text="")
            col1.label(text='Enabled')
            col2.prop(obj.SIMLOADER, 'enabled', text="")


class SIMLOADER_Import(bpy.types.Panel):
    '''
    This is the panel of main addon interface. see  images/1.jpg
    '''
    bl_label = "Sim Loader"
    bl_idname = "SIMLOADER_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Sim Loader"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        importer_prop = scene.SIMLOADER

        layout.label(text="Basic Import Settings")
        box = layout.box()
        split = box.split()
        col1 = split.column()
        col1.alignment = 'RIGHT'
        col2 = split.column(align=False)

        col1.label(text="Directory")
        col2.prop(importer_prop, "path", text="")

        col1.label(text="File Sequqence")
        col2.prop(importer_prop, "fileseq", text="")

        col1.label(text="Use Relative Path")
        col2.prop(importer_prop, "relative", text="")

        layout.label(text="Pattern")
        box = layout.box()
        split = box.split()

        col1 = split.column()
        col1.alignment = 'RIGHT'
        col2 = split.column(align=False)

        col1.label(text="Use Pattern")
        col2.prop(importer_prop, "use_pattern", text="")
        if importer_prop.use_pattern:
            col1.label(text="Pattern")
            col2.prop(importer_prop, "pattern", text="")

        layout.operator("sequence.load")

        layout.label(text="Extra Settings")
        box = layout.box()
        split = box.split()
        col1 = split.column()
        col1.alignment = 'RIGHT'
        col2 = split.column(align=False)

        col1.label(text="Print Information when render")
        col2.prop(importer_prop, "print", text="")


class SIMLOADER_Templates(bpy.types.Menu):
    '''
    Here is the template panel, shown in the text editor -> templates
    '''
    bl_label = "Sim Loader"
    bl_idname = "SIMLOADER_MT_template"

    def draw(self, context):
        current_folder = os.path.dirname(os.path.abspath(__file__))
        self.path_menu(
            # it goes to current folder -> parent folder -> template folder
            [current_folder + '/../template'],
            "text.open",
            props_default={"internal": True},
        )


def draw_template(self, context):
    '''
    Here it function call to integrate template panel into blender template interface
    '''
    layout = self.layout
    layout.menu(SIMLOADER_Templates.bl_idname)