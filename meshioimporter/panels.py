import bpy
import os


class SEQUENCE_UL_list(bpy.types.UIList):
    '''
    This controls the list of imported sequneces.
    '''

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            layout.prop(item, "name", text='Name ', emboss=False)
        else:
            layout.label(text="", translate=False, icon_value=icon)


class sequence_list_panel(bpy.types.Panel):
    '''
    This is the panel of imported sequences, bottom part of images/9.png
    '''
    bl_label = "Sequences Imported"
    bl_idname = "SEQUENCES_PT_list"
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"
    bl_category = "Sim Loader"

    # bl_parent_id = "MESHIO_IMPORT_PT_panel"

    def draw(self, context):
        layout = self.layout
        mytool = context.scene.my_tool
        row = layout.row()
        row.template_list("SEQUENCE_UL_list",
                          "",
                          context.scene.my_tool,
                          'imported',
                          context.scene.my_tool,
                          "imported_num",
                          rows=2)

        col = row.column(align=True)
        col.operator("sequence.remove", icon='REMOVE', text="")


class SimLoader_Settings(bpy.types.Panel):
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
        mytool = context.scene.my_tool
        if len(mytool.imported) > 0:
            item = mytool.imported[mytool.imported_num]

            layout.label(text="Attributes Settings")
            box = layout.box()

            box.prop(item, 'all_attributes_enum')
            split = box.split()
            col1 = split.column()
            col1.alignment = 'RIGHT'
            col2 = split.column(align=False)

            col1.prop(item, 'use_real_value', text="Use original value ")
            col2.prop(item, 'use_clamped_value', text="Use clamped value")
            col1.label(text="Min norm: " + "{:.3f}".format((item.ref_min_value)))
            col2.label(text="Max norm: " + "{:.3f}".format(item.ref_max_value))
            if not item.use_real_value:
                col1.prop(item, 'min_value')
                col2.prop(item, 'max_value')

            if item.type == 0:
                layout.label(text="Particles Settings")
                box = layout.box()
                split = box.split()
                col1 = split.column()
                col1.alignment = 'RIGHT'
                col2 = split.column(align=False)
                col1.label(text="Radius")
                col2.prop(item, 'radius', text="")
                col1.label(text="Display Method")
                col2.prop(item, 'display', text="")
            else:
                layout.label(text="Mesh Settings")
                box = layout.box()
                box.label(text="currently nothing here")

            layout.label(text="Advance")
            box = layout.box()
            split = box.split()
            col1 = split.column()
            col1.alignment = 'RIGHT'
            col2 = split.column(align=False)
            col1.label(text="Use Advance")
            col2.prop(item, "use_advance", text="")
            if item.use_advance:
                col1.label(text="Customized Script")
                col2.prop_search(item, 'script_name', bpy.data, 'texts', text="")


class edit_sequence_panel(bpy.types.Panel):
    '''
    This is the panel when trying to edit the path of existed sequence
    '''
    bl_label = "Edit Sequence Path"
    bl_idname = "EDIT_PT_sequence"
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"
    bl_category = "Sim Loader"
    # bl_parent_id = "SEQUENCES_PT_list"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        mytool = context.scene.my_tool
        if len(mytool.imported) > 0:
            importer_prop = mytool.importer

            layout.prop(importer_prop, "path")
            layout.prop(importer_prop, "relative")
            layout.prop(importer_prop, "pattern")
            layout.prop(importer_prop, "fileseq")
            layout.operator("sequence.edit")
            item = mytool.imported[mytool.imported_num]
            layout.label(text="use relative: " + str(item.relative))
            layout.label(text="current path: " + item.pattern)


class MESHIO_IMPORT_PT_main_panel(bpy.types.Panel):
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
        importer_prop = scene.my_tool.importer

        layout.label(text="Basic Settings")
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


class TEXT_MT_templates_meshioimporter(bpy.types.Menu):
    '''
    Here is the template panel, shown in the text editor -> templates
    '''
    bl_label = "Sim Loader"
    bl_idname = "OBJECT_MT_simloader_template"

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
    layout.menu(TEXT_MT_templates_meshioimporter.bl_idname)