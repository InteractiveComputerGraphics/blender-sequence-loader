import bpy
import fileseq
from .importer_manager import *
from .particles_importer import *
from .mesh_importer import *


class particle_OT_clear(bpy.types.Operator):
    bl_label = "Remove Sequence"
    bl_idname = "sequence.remove"

    def execute(self, context):
        global importer
        global importer_list
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
    bl_label = "Load Sequences"
    bl_idname = "sequence.load"

    def execute(self, context):
        global importer
        global importer_list
        scene = context.scene
        importer_prop = scene.my_tool.importer
        imported_prop = scene.my_tool.imported
        fs = importer_prop.fileseq
        if fs == "None":
            return {'CANCELLED'}
        if fs == "Manual":
            fs = importer_prop.path+'/'+importer_prop.pattern
        fs = fileseq.findSequenceOnDisk(fs)
        if importer_prop.type == "particle":
            if importer:
                importer = None

            importer = particle_importer(fs)
            importer_list.append(importer)

            imported_prop.add()
            imported_prop[-1].pattern = fs.dirname()+fs.basename() + \
                "@"+fs.extension()
            imported_prop[-1].type = 0
            imported_prop[-1].start = fs.start()
            imported_prop[-1].end = fs.end()
            imported_prop[-1].type = 0
            imported_prop[-1].length = len(fs)
            imported_prop[-1].max_value = importer.particle_num
            for co_at in importer.get_color_attribute():
                imported_prop[-1].all_attributes.add()
                imported_prop[-1].all_attributes[-1].name = co_at
            imported_prop[-1].mesh_name = importer.mesh.name
            imported_prop[-1].obj_name = importer.emitterObject.name
            imported_prop[-1].sphere_obj_name = importer.sphereObj.name
            imported_prop[-1].material_name = importer.material.name
            imported_prop[-1].tex_image_name = importer.tex_image.name
            bpy.app.handlers.frame_change_post.append(importer)

        if importer_prop.type == "mesh":
            if importer:
                importer = None
            importer = mesh_importer(fs)
            importer_list.append(importer)
            imported_prop.add()
            imported_prop[-1].pattern = fs.dirname()+fs.basename() + \
                "@"+fs.extension()
            imported_prop[-1].type = 1
            imported_prop[-1].mesh_name = importer.mesh.name
            imported_prop[-1].obj_name = importer.obj.name
            bpy.app.handlers.frame_change_post.append(importer)
        return {"FINISHED"}
