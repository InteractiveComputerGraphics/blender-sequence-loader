from .operators import SIMLOADER_OT_load
from .properties import importer_properties, imported_seq_properties, tool_properties,SIMLOADER_obj_property
from .panels import SIMLOADER_UL_List, SIMLOADER_List_Panel, SIMLOADER_Settings, SIMLOADER_Import, SIMLOADER_Templates, draw_template
from .importer_manager import load_post, subscribe_to_selected, unsubscribe_to_selected
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

__all__ = [
    "SIMLOADER_OT_load",
    "SIMLOADER_obj_property",
    "SIMLOADER_initilize",
    "importer_properties",
    "SIMLOADER_Import",
    "SIMLOADER_List_Panel",
    "SIMLOADER_UL_List",
    "imported_seq_properties",
    "tool_properties",
    "load_post",
    "subscribe_to_selected",
    "SIMLOADER_Templates",
    "draw_template",
    "unsubscribe_to_selected",
    "SIMLOADER_Settings",
]
