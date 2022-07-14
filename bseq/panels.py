import bpy
import os


class BSEQ_UL_Obj_List(bpy.types.UIList):
    '''
    This controls the list of imported sequences.
    '''

    def filter_items(self, context, data, property):
        objs = getattr(data, property)
        flt_flags = []
        #  not sure if I understand correctly about this
        #  see reference from https://docs.blender.org/api/current/bpy.types.UIList.html#advanced-uilist-example-filtering-and-reordering
        for o in objs:
            if o.BSEQ.init:
                flt_flags.append(self.bitflag_filter_item)
            else:
                flt_flags.append(0)
        flt_neworder = []
        return flt_flags, flt_neworder

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row()
            row.prop(item, "name", text='Name ', emboss=False)
            if item.BSEQ.enabled:
                row.prop(item.BSEQ, "enabled", text = "ENABLED", icon="PLAY")
            else:
                row.prop(item.BSEQ, "enabled", text = "DISABLED", icon="PAUSE")
        else:
            # actually, I guess this line of code won't be executed?
            layout.label(text="", translate=False, icon_value=icon)


class BSEQ_UL_Att_List(bpy.types.UIList):
    '''
    This controls the list of attributes available for this sequence
    '''

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            layout.enabled = False
            layout.prop(item, "name", text='Name ', emboss=False)
            obj = bpy.data.objects[context.scene.BSEQ.selected_obj_num]
            mesh = obj.data
            if mesh.BSEQ.split_norm_att_name and mesh.BSEQ.split_norm_att_name == item.name:
                layout.label(text="using as split norm")

        else:
            # actually, I guess this line of code won't be executed?
            layout.label(text="", translate=False, icon_value=icon)


class BSEQ_List_Panel(bpy.types.Panel):
    '''
    This is the panel of imported sequences, bottom part of images/9.png
    '''
    bl_label = "Imported Sequences"
    bl_idname = "BSEQ_PT_list"
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"
    bl_category = "Sequence Loader"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        sim_loader = context.scene.BSEQ
        row = layout.row()
        row.template_list("BSEQ_UL_Obj_List", "", bpy.data, "objects", sim_loader, "selected_obj_num", rows=2)
        row = layout.row()
        row.operator("bseq.enableselected", text="Enable Selected")
        row.operator("bseq.disableselected", text="Disable Selected")
        row = layout.row()
        row.operator("sequence.edit", text="Edit Path")
        row.operator("bseq.refresh", text="Refresh")


class BSEQ_Settings(bpy.types.Panel):
    '''
    This is the panel of settings of selected sequence
    '''
    bl_label = "Sequence Settings"
    bl_idname = "BSEQ_PT_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"
    bl_category = "Sequence Loader"
    bl_context = "objectmode"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        sim_loader = context.scene.BSEQ
        if sim_loader.selected_obj_num >= len(bpy.data.objects):
            return
        obj = bpy.data.objects[sim_loader.selected_obj_num]
        if not obj.BSEQ.init:
            return

        # path settings
        layout.label(text="Sequence Information (read-only)")
        box = layout.box()

        split = box.split()
        col1 = split.column()
        col1.alignment = 'RIGHT'
        col2 = split.column(align=False)

        col2.enabled = False
        col1.label(text='Relative')
        col2.prop(obj.BSEQ, 'use_relative', text="")
        col1.label(text='Pattern')
        col2.prop(obj.BSEQ, 'pattern', text="")

        # geometry nodes settings
        layout.label(text="Geometry Nodes")
        box = layout.box()
        box.label(text="Point Cloud and Instances Material")
        split = box.split()
        col1 = split.column()
        col1.alignment = 'RIGHT'
        col2 = split.column()
        col1.label(text="Material")
        col2.prop_search(sim_loader, 'material', bpy.data, 'materials', text="")
        box.label(text='Reset Geometry Nodes to')

        split = box.split()
        col1 = split.column()
        col2 = split.column()
        col3 = split.column()
        col1.operator('bseq.resetpt', text="Point Cloud")
        col2.operator('bseq.resetmesh', text="Mesh")
        col3.operator('bseq.resetins', text="Instances")


        # attributes settings
        layout.label(text="Attributes")
        box = layout.box()
        row = box.row()
        row.template_list("BSEQ_UL_Att_List", "", obj.data, "attributes", sim_loader, "selected_attribute_num", rows=2)
        box.operator("bseq.setsplitnorm", text="Set selected as normal")
        box.operator("bseq.removesplitnorm", text="Clear normal")

        # advance settings
        layout.label(text="Advanced")
        box = layout.box()
        split = box.split()
        col1 = split.column()
        col1.alignment = 'RIGHT'
        col2 = split.column(align=False)
        col1.label(text="Show Settings")
        col2.prop(obj.BSEQ, 'use_advance', text="")
        if obj.BSEQ.use_advance:
            col1.label(text='Script')
            col2.prop_search(obj.BSEQ, 'script_name', bpy.data, 'texts', text="")


class BSEQ_Import(bpy.types.Panel):
    '''
    This is the panel of main addon interface. see  images/1.jpg
    '''
    bl_label = "Sequence Loader"
    bl_idname = "BSEQ_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Sequence Loader"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        importer_prop = scene.BSEQ

        layout.label(text="Basic Import Settings")
        box = layout.box()
        split = box.split()
        col1 = split.column()
        col1.alignment = 'RIGHT'
        col2 = split.column(align=False)

        col1.label(text="Directory")
        col2.prop(importer_prop, "path", text="")

        col1.label(text="Use Custom Pattern")
        col2.prop(importer_prop, "use_pattern", text="")
        col1.label(text="Sequence Pattern")
        if importer_prop.use_pattern:
            col2.prop(importer_prop, "pattern", text="")
        else:
            col2.prop(importer_prop, "fileseq", text="")

        col1.label(text="Use Relative Path")
        col2.prop(importer_prop, "relative", text="")

        layout.operator("sequence.load")

        layout.label(text="Global Settings")
        box = layout.box()
        split = box.split()
        col1 = split.column()
        col1.alignment = 'RIGHT'
        col2 = split.column(align=False)

        col1.label(text="Print Sequence Information on Render")
        col2.prop(importer_prop, "print", text="")


class BSEQ_Templates(bpy.types.Menu):
    '''
    Here is the template panel, shown in the text editor -> templates
    '''
    bl_label = "Sequence Loader"
    bl_idname = "BSEQ_MT_template"

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
    layout.menu(BSEQ_Templates.bl_idname)