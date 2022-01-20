import bpy
import fileseq
import os
from .importer_manager import *
from .particle_importer import *
from .mesh_importer import *

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
        importer_prop = scene.sim_loader.importer

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
            # TODO using blender relative path
            pattern = os.path.relpath(fs, os.path.dirname(bpy.data.filepath))

        try:
            fs = fileseq.findSequenceOnDisk(fs)
        except Exception as e:
            show_message_box(traceback.format_exc(), "Can't find sequence: " + str(fs), "ERROR")
            return {"CANCELLED"}

        from .importer import create_obj
        create_obj(fs,pattern,importer_prop.relative)
        return {"FINISHED"}

