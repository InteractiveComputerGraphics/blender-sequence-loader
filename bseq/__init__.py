from bseq.utils import refresh_obj
from .operators import BSEQ_OT_load, BSEQ_OT_edit, BSEQ_OT_resetpt, BSEQ_OT_resetmesh, BSEQ_OT_resetins, BSEQ_OT_set_as_split_norm, BSEQ_OT_remove_split_norm, BSEQ_OT_disable_selected, BSEQ_OT_enable_selected, BSEQ_OT_refresh_seq, BSEQ_OT_disable_all, BSEQ_OT_enable_all, WM_OT_batchWavefront
from .properties import BSEQ_scene_property, BSEQ_obj_property, BSEQ_mesh_property
from .panels import BSEQ_UL_Obj_List, BSEQ_List_Panel, BSEQ_Settings, BSEQ_Import, BSEQ_Templates, BSEQ_UL_Att_List, draw_template
from .messenger import subscribe_to_selected, unsubscribe_to_selected
import bpy
from bpy.app.handlers import persistent
from .importer import update_obj
from .globals import *    


@persistent
def BSEQ_initialize(scene):
    if update_obj not in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.append(auto_refresh)
        bpy.app.handlers.frame_change_post.append(update_obj)
    subscribe_to_selected()
    if print_information not in bpy.app.handlers.render_init:
        bpy.app.handlers.render_init.append(print_information)


__all__ = [
    "BSEQ_OT_edit",
    "BSEQ_OT_load",
    "BSEQ_obj_property",
    "BSEQ_initialize",
    "BSEQ_Import",
    "BSEQ_List_Panel",
    "BSEQ_UL_Obj_List",
    "BSEQ_scene_property",
    "BSEQ_Templates",
    "BSEQ_Settings",
    "BSEQ_UL_Att_List",
    "subscribe_to_selected",
    "BSEQ_OT_resetpt",
    "BSEQ_OT_resetmesh",
    "BSEQ_OT_resetins",
    "draw_template",
    "unsubscribe_to_selected",
    "BSEQ_OT_set_as_split_norm",
    "BSEQ_mesh_property",
    "BSEQ_OT_remove_split_norm",
    "BSEQ_OT_disable_selected",
    "BSEQ_OT_enable_selected",
    "BSEQ_OT_refresh_seq",
    "BSEQ_OT_disable_all",
    "BSEQ_OT_enable_all",
    "WM_OT_batchWavefront"
]
