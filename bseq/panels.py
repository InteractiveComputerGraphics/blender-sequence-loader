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
            if o.BSEQ.init and len(o.users_collection)>0 and len(o.users_scene)>0:
                flt_flags.append(self.bitflag_filter_item)
            else:
                flt_flags.append(0)
        flt_neworder = []
        return flt_flags, flt_neworder

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            split = layout.split(factor=0.4)
            col1 = split.column()
            col2 = split.column()
            split2 = col2.split(factor=0.25)
            col2 = split2.column()
            col3 = split2.column()
            split3 = col3.split(factor=0.5)
            col3 = split3.column()
            col4 = split3.column()
            col4.alignment = 'EXPAND'
            start_frame = item.BSEQ.start_end_frame[0]
            end_frame = item.BSEQ.start_end_frame[1]

            col1.prop(item, "name", text='', emboss=False)
            if item.BSEQ.enabled:
                col2.prop(item.BSEQ, "enabled", text="", icon="PLAY")
                col3.prop(item.BSEQ, "frame", text="")
                col4.label(text=str(start_frame) + '-' + str(end_frame))
            else:
                col2.prop(item.BSEQ, "enabled", text ="", icon="PAUSE")
                col3.label(text="", icon="BLANK1")
                col4.label(text=str(start_frame) + '-' + str(end_frame))
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
            layout.prop(item, "name", text='', emboss=False)
            obj = bpy.data.objects[context.scene.BSEQ.selected_obj_num]
            mesh = obj.data
            if mesh.BSEQ.split_norm_att_name and mesh.BSEQ.split_norm_att_name == item.name:
                layout.label(text="Use as split norm.")

        else:
            # actually, I guess this line of code won't be executed?
            layout.label(text="", translate=False, icon_value=icon)

class BSEQ_Panel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"
    bl_category = "Sequence Loader"
    bl_context = "objectmode"

class BSEQ_Globals_Panel(BSEQ_Panel, bpy.types.Panel):
    bl_label = "Global Settings"
    bl_idname = "BSEQ_PT_global"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        sim_loader = context.scene.BSEQ
        split = layout.split()
        col1 = split.column()
        col1.alignment = 'RIGHT'
        col2 = split.column()

        col1.label(text="Root Directory")
        col2.prop(sim_loader, "root_path", text="")
        col1.label(text="Print Sequence Information")
        col2.prop(sim_loader, "print", text="")
        col1.label(text="Auto Refresh Active")
        col2.prop(sim_loader, "auto_refresh_active", text="")
        col1.label(text="Auto Refresh All")
        col2.prop(sim_loader, "auto_refresh_all", text="")

class BSEQ_Advanced_Panel(BSEQ_Panel, bpy.types.Panel):
    bl_label = "Advanced Settings"
    bl_idname = "BSEQ_PT_advanced"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        sim_loader = context.scene.BSEQ

        split = layout.split()
        col1 = split.column()
        col2 = split.column()

        if sim_loader.selected_obj_num >= len(bpy.data.objects):
            return
        obj = bpy.data.objects[sim_loader.selected_obj_num]
        if not obj.BSEQ.init:
            return

        # geometry nodes settings
        layout.label(text="Geometry Nodes (select sequence first)")

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


class BSEQ_List_Panel(BSEQ_Panel, bpy.types.Panel):
    '''
    This is the panel of imported sequences, bottom part of images/9.png
    '''
    bl_label = "Sequences"
    bl_idname = "BSEQ_PT_list"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        sim_loader = context.scene.BSEQ
        row = layout.row()
        row.template_list("BSEQ_UL_Obj_List", "", bpy.data, "objects", sim_loader, "selected_obj_num", rows=2)
        row = layout.row()
        row.operator("bseq.enableselected", text="Activate")
        row.operator("bseq.disableselected", text="Deactivate")
        row.operator("bseq.refresh", text="Refresh")
        row = layout.row()
        row.operator("bseq.enableall", text="Activate All")
        row.operator("bseq.disableall", text="Deactivate All")
        row.operator("bseq.set_start_end_frames", text="Set timeline")

class BSEQ_Settings(BSEQ_Panel, bpy.types.Panel):
    '''
    This is the panel of settings of selected sequence
    '''
    bl_label = "Sequence Properties"
    bl_idname = "BSEQ_PT_settings"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        sim_loader = context.scene.BSEQ
        importer_prop = context.scene.BSEQ

        if sim_loader.selected_obj_num >= len(bpy.data.objects):
            return
        obj = bpy.data.objects[sim_loader.selected_obj_num]
        if not obj.BSEQ.init:
            return

        split = layout.split()
        col1 = split.column()
        col1.alignment = 'RIGHT'
        col2 = split.column(align=False)

        col1.label(text='Match Blender frame numbers')
        col2.prop(obj.BSEQ, 'match_frames', text="")

        col1.label(text='Path')
        col2.prop(obj.BSEQ, 'path', text="")
        col1.label(text='Pattern')
        col2.prop(obj.BSEQ, 'pattern', text="")
        # Read-only
        col1.label(text='Current File')
        # make it read-only
        row1 = col2.row()
        row1.enabled = False
        row1.prop(obj.BSEQ, 'current_file', text="")
        col1.label(text='Last loading time (ms)')
        row2 = col2.row()
        row2.enabled = False
        row2.prop(obj.BSEQ, 'last_benchmark', text="", )

        # attributes settings
        layout.label(text="Attributes")
        box = layout.box()
        row = box.row()
        row.template_list("BSEQ_UL_Att_List", "", obj.data, "attributes", sim_loader, "selected_attribute_num", rows=2)
        box.operator("bseq.setsplitnorm", text="Set selected as normal")
        box.operator("bseq.removesplitnorm", text="Clear normal")

class BSEQ_PT_Import(BSEQ_Panel, bpy.types.Panel):
    '''
    This is the panel of main addon interface. see  images/1.jpg
    '''
    bl_label = "Import"
    bl_idname = "BSEQ_PT_panel"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        importer_prop = scene.BSEQ

        row = layout.row()

        row.scale_y = 1.5
        row.operator("wm.seq_import_batch")
        
        split = layout.split()
        col1 = split.column()
        col2 = split.column()

        split = layout.split(factor=0.5)
        col1 = split.column()
        col1.alignment = 'RIGHT'
        col2 = split.column(align=False)

        # col2.prop(importer_prop, "filter_string", text="Filter String")

        col1.label(text="Relative Paths")
        col2.prop(importer_prop, "use_relative", text="")

        if importer_prop.use_relative:
            col1.label(text="Relative Root")
            col2.prop(importer_prop, "root_path", text="")


        col1.label(text="Import Normals")
        col2.prop(importer_prop, "use_imported_normals", text="")

        col1.label(text="Custom Transform")
        col2.prop(importer_prop, "use_custom_transform", text="")

        if importer_prop.use_custom_transform:
            split = layout.split(factor=0.33)
            box_col1 = split.column()
            box_col2 = split.column()
            box_col3 = split.column()

            box_col1.label(text="Location:")
            box_col1.prop(importer_prop, "custom_location", text="")

            box_col2.label(text="Rotation:")
            box_col2.prop(importer_prop, "custom_rotation", text="")

            box_col3.label(text="Scale:")
            box_col3.prop(importer_prop, "custom_scale", text="")

class BSEQ_PT_Import_Child1(BSEQ_Panel, bpy.types.Panel):
    bl_parent_id = "BSEQ_PT_panel"
    bl_label = "Import from folder"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        importer_prop = scene.BSEQ

        split = layout.split()
        col1 = split.column()
        col1.alignment = 'RIGHT'
        col2 = split.column(align=False)

        col1.label(text="Directory")
        col2.prop(importer_prop, "path", text="")

        col1.label(text="Custom Pattern")
        col2.prop(importer_prop, "use_pattern", text="")
        col1.label(text="Sequence Pattern")
        if importer_prop.use_pattern:
            col2.prop(importer_prop, "pattern", text="")
        else:
            split2 = col2.split(factor=0.75)
            col3 = split2.column()
            col4 = split2.column()
            col3.prop(importer_prop, "fileseq", text="")
            col4.operator("bseq.refreshall", text='', icon="FILE_REFRESH")

        split = layout.split(factor=0.5)
        col1 = split.column()
        col2 = split.column()
        col1.operator("sequence.load")
        row = col2.row()
        row.operator("bseq.load_all")
        row.operator("bseq.load_all_recursive")

        # split = layout.split(factor=0.5)
        # col1 = split.column()
        # col2 = split.column()

        # col1.operator("bseq.import_zip", text="Import from zip")
        # col2.operator("bseq.delete_zips", text="Delete created folders")


class BSEQ_PT_Import_Child2(BSEQ_Panel, bpy.types.Panel):
    bl_parent_id = "BSEQ_PT_panel"
    bl_label = "Test"
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        importer_prop = scene.BSEQ

        split = layout.split()
        col1 = split.column()
        col2 = split.column()

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