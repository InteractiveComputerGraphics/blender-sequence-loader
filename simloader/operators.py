import bpy
import fileseq
from .importer_manager import *
import traceback
from .importer import create_obj


#  Here are load and delete operations
class SIMLOADER_OT_load(bpy.types.Operator):
    '''
    This operator loads a sequnce
    '''
    bl_label = "Load Sequences"
    bl_idname = "sequence.load"
    bl_options = {"UNDO"}

    def execute(self, context):
        scene = context.scene
        importer_prop = scene.SIMLOADER

        if importer_prop.relative and not bpy.data.is_saved:
            #  use relative but file not saved
            show_message_box("When using relative path, please save file before using it", icon="ERROR")
            return {"CANCELLED"}

        fs = importer_prop.fileseq
        use_pattern = importer_prop.use_pattern

        if not use_pattern and (not fs or fs == "None"):
            # fs is none
            return {'CANCELLED'}
        if use_pattern:
            if not importer_prop.pattern:
                show_message_box("Pattern is empty", icon="ERROR")
                return {"CANCELLED"}
            fs = importer_prop.path + '/' + importer_prop.pattern

        #  pattern means the name of directory
        #  fs means fileseq object
        pattern = fs
        if importer_prop.relative:
            pattern = bpy.path.relpath(fs)

        try:
            fs = fileseq.findSequenceOnDisk(fs)
        except Exception as e:
            show_message_box(traceback.format_exc(), "Can't find sequence: " + str(fs), "ERROR")
            return {"CANCELLED"}

        create_obj(fs, pattern, importer_prop.relative)
        return {"FINISHED"}


class SIMLOADER_OT_edit(bpy.types.Operator):
    '''
    This operator changes a sequnce
    '''
    bl_label = "Edit Sequences Path"
    bl_idname = "sequence.edit"
    bl_options = {"UNDO"}

    def execute(self, context):
        scene = context.scene
        importer_prop = scene.SIMLOADER

        if importer_prop.relative and not bpy.data.is_saved:
            #  use relative but file not saved
            show_message_box("When using relative path, please save file before using it", icon="ERROR")
            return {"CANCELLED"}

        fs = importer_prop.fileseq
        use_pattern = importer_prop.use_pattern

        if not use_pattern and (not fs or fs == "None"):
            # fs is none
            return {'CANCELLED'}
        if use_pattern:
            if not importer_prop.pattern:
                show_message_box("Pattern is empty", icon="ERROR")
                return {"CANCELLED"}
            fs = importer_prop.path + '/' + importer_prop.pattern

        #  pattern means the name of directory
        #  fs means fileseq object
        pattern = fs
        if importer_prop.relative:
            pattern = bpy.path.relpath(fs)

        try:
            fs = fileseq.findSequenceOnDisk(fs)
        except Exception as e:
            show_message_box(traceback.format_exc(), "Can't find sequence: " + str(fs), "ERROR")
            return {"CANCELLED"}

        collection = bpy.data.collections['SIMLOADER'].objects
        sim_loader = context.scene.SIMLOADER
        #  it seems quite simple task, no need to create a function(for now)
        if len(collection) > 0 and sim_loader.selected_obj_num < len(collection):
            obj = collection[sim_loader.selected_obj_num]
            obj.SIMLOADER.pattern = pattern
            obj.SIMLOADER.use_relative = importer_prop.relative
            return {"FINISHED"}
        return {"CANCELLED"}
