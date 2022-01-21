from .operators import SIMLOADER_OT_load
from .properties import SIMLOADER_scene_property, SIMLOADER_obj_property
from .panels import SIMLOADER_UL_List, SIMLOADER_List_Panel, SIMLOADER_Settings, SIMLOADER_Import, SIMLOADER_Templates, draw_template
from .importer_manager import subscribe_to_selected, unsubscribe_to_selected
import bpy
from bpy.app.handlers import persistent
from .importer import update_obj


@persistent
def SIMLOADER_initilize(scene):
    #  create the collection for all objects
    if "SIMLOADER" not in bpy.data.collections:
        collection = bpy.data.collections.new("SIMLOADER")
        bpy.context.scene.collection.children.link(collection)

    if update_obj not in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.append(update_obj)
    subscribe_to_selected()


__all__ = [
    "SIMLOADER_OT_load",
    "SIMLOADER_obj_property",
    "SIMLOADER_initilize",
    "SIMLOADER_Import",
    "SIMLOADER_List_Panel",
    "SIMLOADER_UL_List",
    "SIMLOADER_scene_property",
    "SIMLOADER_Templates",
    "SIMLOADER_Settings",
    "subscribe_to_selected",
    "draw_template",
    "unsubscribe_to_selected",
]
