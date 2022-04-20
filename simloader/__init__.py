from .operators import SIMLOADER_OT_load, SIMLOADER_OT_edit, SIMLOADER_OT_resetpt, SIMLOADER_OT_resetmesh, SIMLOADER_OT_resetins,SIMLOADER_OT_set_as_split_norm,SIMLOADER_OT_remove_split_norm
from .properties import SIMLOADER_scene_property, SIMLOADER_obj_property,SIMLOADER_mesh_property
from .panels import SIMLOADER_UL_Obj_List, SIMLOADER_List_Panel, SIMLOADER_Settings, SIMLOADER_Import, SIMLOADER_Templates, SIMLOADER_UL_Att_List, draw_template
from .messanger import subscribe_to_selected, unsubscribe_to_selected
import bpy
from bpy.app.handlers import persistent
from .importer import update_obj
from datetime import datetime


def print_information(scene):
    if not bpy.context.scene.SIMLOADER.print:
        return
    now = datetime.now()
    path = bpy.context.scene.render.filepath
    path = bpy.path.abspath(path)
    filepath = path + '/simloader_' + now.strftime("%Y-%m-%d_%H-%M")
    with open(filepath, 'w') as file:
        file.write("Render Time: {}\n".format(now.strftime("%Y-%m-%d_%H-%M")))
        file.write("Simloader Objects in the scene:\n\n")
        for obj in bpy.data.objects:
            simloader_prop = obj.SIMLOADER
            if simloader_prop.init:
                file.write("Object name: {}\n".format(obj.name))
                file.write("Is it being animated: {}\n".format(simloader_prop.enabled))
                file.write("Filepath: {}\n".format(simloader_prop.pattern))
                file.write("Is it relative path: {}\n".format(simloader_prop.use_relative))
                file.write("\n\n")


@persistent
def SIMLOADER_initilize(scene):
    if update_obj not in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.append(update_obj)
    subscribe_to_selected()
    if print_information not in bpy.app.handlers.render_init:
        bpy.app.handlers.render_init.append(print_information)


__all__ = [
    "SIMLOADER_OT_edit",
    "SIMLOADER_OT_load",
    "SIMLOADER_obj_property",
    "SIMLOADER_initilize",
    "SIMLOADER_Import",
    "SIMLOADER_List_Panel",
    "SIMLOADER_UL_Obj_List",
    "SIMLOADER_scene_property",
    "SIMLOADER_Templates",
    "SIMLOADER_Settings",
    "SIMLOADER_UL_Att_List",
    "subscribe_to_selected",
    "SIMLOADER_OT_resetpt",
    "SIMLOADER_OT_resetmesh",
    "SIMLOADER_OT_resetins",
    "draw_template",
    "unsubscribe_to_selected",
    "SIMLOADER_OT_set_as_split_norm",
    "SIMLOADER_mesh_property",
    "SIMLOADER_OT_remove_split_norm",
]
