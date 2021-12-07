import bpy
import fileseq


class SEQUENCE_UL_list(bpy.types.UIList):
    '''
    This controls the list of imported sequneces.
    '''
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ob = data
        slot = item
        ma = item
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if ma:
                layout.prop(ma, "name", text='Name: ', emboss=False)
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
    bl_category = "Meshio Importer"
    bl_parent_id = "MESHIO_IMPORT_PT_panel"

    def draw(self, context):
        layout = self.layout
        mytool = context.scene.my_tool
        row = layout.row()
        row.template_list("SEQUENCE_UL_list", "", context.scene.my_tool,
                          'imported', context.scene.my_tool, "imported_num")

        col = row.column(align=True)
        col.operator("sequence.remove", icon='REMOVE', text="")

        if len(mytool.imported) > 0:
            item = mytool.imported[mytool.imported_num]

            info_part = layout.column()
            info_part.prop(item, 'start')
            info_part.prop(item, 'end')
            info_part.prop(item, 'use_real_value')
            if not item.use_real_value:
                info_part.prop(item, 'min_value')
                info_part.prop(item, 'max_value')
            info_part.prop(item, 'all_attributes_enum')

            if item.type == 0:
                info_part.prop(item, 'radius')
                info_part.prop(item, 'display')


class MESHIO_IMPORT_PT_main_panel(bpy.types.Panel):
    '''
    This is the panel of main addon interface. see  images/1.jpg
    '''
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
        layout.prop(importer_prop, "relative")
        layout.prop(importer_prop, "pattern")
        layout.prop(importer_prop, "fileseq")
        layout.prop(importer_prop, "type")
        layout.operator("sequence.load")
