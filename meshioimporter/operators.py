import bpy
import fileseq
import os
from .importer_manager import *
from .particle_importer import *
from .mesh_importer import *
from .callback import get_index

#  Here are load and delete operations


class particle_OT_clear(bpy.types.Operator):
    '''
    This operator delete a sequnce
    '''
    bl_label = "Remove Sequence"
    bl_idname = "sequence.remove"
    bl_options = {"UNDO"}

    def execute(self, context):
        global importer_list
        if not importer_list:
            return {"CANCELLED"}
        mytool = context.scene.my_tool
        idx = mytool.imported_num
        importer_list_index = mytool.imported[idx].importer_list_index

        mytool.imported.remove(idx)
        #  don't need to delete, only remove the object, so it can be undone
        importer_list[importer_list_index].clear()
        mytool.imported_num = max(mytool.imported_num - 1, 0)
        return {"FINISHED"}


class meshio_loader_OT_load(bpy.types.Operator):
    '''
    This operator loads a sequnce
    '''
    bl_label = "Load Sequences"
    bl_idname = "sequence.load"
    bl_options = {"UNDO"}

    def execute(self, context):
        global importer_list
        scene = context.scene
        importer_prop = scene.my_tool.importer
        imported_prop = scene.my_tool.imported

        if importer_prop.relative and not bpy.data.is_saved:
            show_message_box("When using relative path, please save file before using it", icon="ERROR")
            return {"CANCELLED"}

        fs = importer_prop.fileseq
        if not fs or fs == "None":
            return {'CANCELLED'}
        if fs == "Manual":
            if not importer_prop.pattern:
                show_message_box("Pattern is empty", icon="ERROR")
                return {"CANCELLED"}
            fs = importer_prop.path + '/' + importer_prop.pattern

        pattern = fs
        if importer_prop.relative:
            pattern = os.path.relpath(fs, os.path.dirname(bpy.data.filepath))

        fs = fileseq.findSequenceOnDisk(fs)

        data_type = None
        color_attributes = None
        try:
            data_type, color_attributes = pre_check(fs[0])
        except Exception as e:
            # self.report({"ERROR_INVALID_INPUT"},
            #             "loading: " + str(fs) + " failed, here is the error:,\n" + traceback.format_exc())
            # print("loading: " + str(fs) + " failed, here is the error:,\n" + traceback.format_exc())
            show_message_box()
            return {"CANCELLED"}

        if data_type == 'particle':
            importer = particle_importer(fs)
            importer_list.append(importer)
            #  save information, will be used when restart .blender file
            imported_prop.add()
            #  better put this as first line of code, otherwise, when setting imported_prop[-1].max_value, update_max will be called, and it will call sequence remove, because importer_list_index is zero, and this sequence may or may not exist
            imported_prop[-1].importer_list_index = len(importer_list) - 1

            imported_prop[-1].pattern = pattern
            imported_prop[-1].relative = importer_prop.relative
            imported_prop[-1].type = 0
            imported_prop[-1].max_value = importer.max_value
            for co_at in color_attributes:
                importer.color_attributes.append(co_at)
                imported_prop[-1].all_attributes.add()
                imported_prop[-1].all_attributes[-1].name = co_at
            imported_prop[-1].name = importer.get_obj_name()
            # imported_prop[-1].sphere_obj_name = importer.sphere_obj_name
            imported_prop[-1].particle_settings_name = importer.particle_settings_name
            # imported_prop[-1].material_name = importer.material_name
            bpy.app.handlers.frame_change_post.append(importer)

        elif data_type == "mesh":

            importer = mesh_importer(fs)
            importer_list.append(importer)
            #  save information, will be used when restart .blender file
            imported_prop.add()
            imported_prop[-1].importer_list_index = len(importer_list) - 1
            imported_prop[-1].pattern = pattern
            imported_prop[-1].relative = importer_prop.relative
            imported_prop[-1].type = 1

            imported_prop[-1].mesh_name = importer.mesh_name
            # imported_prop[-1].material_name = importer.material_name
            imported_prop[-1].name = importer.get_obj_name()
            imported_prop[-1].max_value = importer.max_value
            for co_at in color_attributes:
                importer.color_attributes.append(co_at)
                imported_prop[-1].all_attributes.add()
                imported_prop[-1].all_attributes[-1].name = co_at
            #  add importer to blender animation system
            bpy.app.handlers.frame_change_post.append(importer)
        return {"FINISHED"}


class sequence_OT_edit(bpy.types.Operator):
    '''
    This operator edits a sequnce
    '''
    bl_label = "Edit Sequences"
    bl_idname = "sequence.edit"

    def execute(self, context):
        global importer_list
        scene = context.scene
        importer_prop = scene.my_tool.importer
        imported_prop = scene.my_tool.imported

        if importer_prop.relative and not bpy.data.is_saved:
            show_message_box("When using relative path, please save file before using it", icon="ERROR")
            return {"CANCELLED"}

        fs = importer_prop.fileseq
        if not fs or fs == "None":
            return {'CANCELLED'}
        if fs == "Manual":
            if not importer_prop.pattern:
                show_message_box("Pattern is empty", icon="ERROR")
                return {"CANCELLED"}
            fs = importer_prop.path + '/' + importer_prop.pattern

        pattern = fs
        if importer_prop.relative:
            pattern = os.path.relpath(fs, os.path.dirname(bpy.data.filepath))

        fs = fileseq.findSequenceOnDisk(fs)

        idx, importer_list_index = get_index(context)
        importer = importer_list[importer_list_index]
        if importer_prop.type != importer.type():
            show_message_box("You are editing with a different type of sequences", icon="ERROR")
            return {"CANCELLED"}
        if importer.type() == "particle":
            importer.fileseq = fs
            importer.render_attributes = []
            importer.used_render_attribute = None
            importer.read_first_frame()
            imported_prop[idx].all_attributes.clear()
            imported_prop[idx].all_attributes_enum = "None"
            for co_at in importer.color_attribute:
                imported_prop[idx].all_attributes.add()
                imported_prop[idx].all_attributes[-1].name = co_at
            imported_prop[idx].used_color_attribute.name = ""
            imported_prop[idx].pattern = pattern
            imported_prop[idx].relative = importer_prop.relative
        else:
            importer.fileseq = fs
            importer.render_attributes = []
            importer.used_render_attribute = None
            importer.load_mesh(fs[0])
            imported_prop[idx].all_attributes.clear()
            imported_prop[idx].all_attributes_enum = "None"
            for co_at in importer.color_attribute:
                imported_prop[idx].all_attributes.add()
                imported_prop[idx].all_attributes[-1].name = co_at
            imported_prop[idx].used_color_attribute.name = ""
            imported_prop[idx].pattern = pattern
            imported_prop[idx].relative = importer_prop.relative
        return {"FINISHED"}
