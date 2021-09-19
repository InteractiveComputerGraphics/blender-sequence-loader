import bpy
import fileseq


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
        ma = item
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if ma:
                layout.prop(ma, "pattern", text='Pattern: ', emboss=False)
            else:
                layout.label(text="", translate=False, icon_value=icon)


class sequence_list_panel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
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
            info_part.prop(item, 'length')
            info_part.prop(item, 'min_value')
            info_part.prop(item, 'max_value')
            info_part.prop(item, 'all_attributes_enum')

            if item.type == 0:
                info_part.prop(item, 'radius')
                info_part.prop(item, 'display')


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
