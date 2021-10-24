import bpy
import fileseq
import os
from .importer_manager import *
from .particle_importer import *
from .mesh_importer import *

#  Here are load and delete operations 

class particle_OT_clear(bpy.types.Operator):
    '''
    This operator delete a sequnce
    '''
    bl_label = "Remove Sequence"
    bl_idname = "sequence.remove"

    def execute(self, context):
        global importer
        global importer_list
        if not importer_list:
            return {"CANCELLED"}
        mytool = context.scene.my_tool
        idx = mytool.imported_num
        mytool.imported.remove(idx)
        bpy.app.handlers.frame_change_post.remove(importer_list[idx])
        if importer == importer_list[idx]:
            importer = None
        importer_list[idx].clear()
        del importer_list[idx]
        mytool.imported_num = max(mytool.imported_num-1, 0)
        return {"FINISHED"}


class meshio_loader_OT_load(bpy.types.Operator):
    '''
    This operator loads a sequnce
    '''
    bl_label = "Load Sequences"
    bl_idname = "sequence.load"

    def execute(self, context):
        

        global importer
        global importer_list
        scene = context.scene
        importer_prop = scene.my_tool.importer
        imported_prop = scene.my_tool.imported

        if importer_prop.relative and  not bpy.data.is_saved:
            show_message_box("When using relative path, please save file before using it", icon="ERROR")
            return {"CANCELLED"}

        fs = importer_prop.fileseq
        if not fs or fs == "None":
            return {'CANCELLED'}
        if fs == "Manual":
            if not importer_prop.pattern:
                show_message_box("Pattern is empty", icon="ERROR")
                return {"CANCELLED"}
            fs = importer_prop.path+'/'+importer_prop.pattern
        
        pattern = fs
        if importer_prop.relative:
            pattern = os.path.relpath(fs, os.path.dirname(bpy.data.filepath))



        fs = fileseq.findSequenceOnDisk(fs)


        if importer_prop.type == "particle":
            if importer:
                importer = None

            importer = particle_importer(fs)
            importer_list.append(importer)
            #  save information, will be used when restart .blender file
            imported_prop.add()
            imported_prop[-1].pattern = pattern
            imported_prop[-1].relative = importer_prop.relative
            imported_prop[-1].type = 0
            imported_prop[-1].max_value = importer.particle_num
            for co_at in importer.get_color_attribute():
                imported_prop[-1].all_attributes.add()
                imported_prop[-1].all_attributes[-1].name = co_at
            imported_prop[-1].mesh_name = importer.mesh.name
            imported_prop[-1].obj_name = importer.emitterObject.name
            imported_prop[-1].sphere_obj_name = importer.sphereObj.name
            imported_prop[-1].material_name = importer.material.name
            imported_prop[-1].tex_image_name = importer.tex_image.name
            #  add importer to blender animation system
            bpy.app.handlers.frame_change_post.append(importer)

        if importer_prop.type == "mesh":
            if importer:
                importer = None
            importer = mesh_importer(fs)
            importer_list.append(importer)
            #  save information, will be used when restart .blender file
            imported_prop.add()
            imported_prop[-1].pattern = pattern
            imported_prop[-1].relative = importer_prop.relative
            imported_prop[-1].type = 1
            imported_prop[-1].mesh_name = importer.mesh.name
            imported_prop[-1].obj_name = importer.obj.name
            imported_prop[-1].material_name = importer.material.name
            imported_prop[-1].max_value = 100
            for co_at in importer.get_color_attribute():
                imported_prop[-1].all_attributes.add()
                imported_prop[-1].all_attributes[-1].name = co_at
            #  add importer to blender animation system
            bpy.app.handlers.frame_change_post.append(importer)
        return {"FINISHED"}
