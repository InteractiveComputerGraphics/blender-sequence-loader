from bseq.utils import refresh_obj
from .operators import BSEQ_OT_load, BSEQ_OT_edit, BSEQ_OT_resetpt, BSEQ_OT_resetmesh, BSEQ_OT_resetins, BSEQ_OT_set_as_split_norm, BSEQ_OT_remove_split_norm, BSEQ_OT_disable_selected, BSEQ_OT_enable_selected, BSEQ_OT_refresh_seq, BSEQ_OT_disable_all, BSEQ_OT_enable_all, BSEQ_OT_refresh_sequences, BSEQ_OT_set_start_end_frames, BSEQ_OT_batch_sequences, BSEQ_PT_batch_sequences_settings, BSEQ_OT_meshio_object, BSEQ_OT_import_zip, BSEQ_OT_delete_zips, BSEQ_addon_preferences, BSEQ_OT_load_all, BSEQ_OT_load_all_recursive
from .properties import BSEQ_scene_property, BSEQ_obj_property, BSEQ_mesh_property
from .panels import BSEQ_UL_Obj_List, BSEQ_List_Panel, BSEQ_Settings, BSEQ_PT_Import, BSEQ_PT_Import_Child1, BSEQ_PT_Import_Child2, BSEQ_Globals_Panel, BSEQ_Advanced_Panel, BSEQ_Templates, BSEQ_UL_Att_List, draw_template
from .messenger import subscribe_to_selected, unsubscribe_to_selected
import bpy
from bpy.app.handlers import persistent
from .importer import update_obj
from .globals import *    


@persistent
def BSEQ_initialize(scene):
    if update_obj not in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.append(update_obj)
    if auto_refresh_active not in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.append(auto_refresh_active)
    if auto_refresh_all not in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.append(auto_refresh_all)
    if clean_unused_bseq_data not in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.append(clean_unused_bseq_data)
    subscribe_to_selected()
    if print_information not in bpy.app.handlers.render_init:
        bpy.app.handlers.render_init.append(print_information)


__all__ = [
    "BSEQ_OT_edit",
    "BSEQ_OT_load",
    "BSEQ_obj_property",
    "BSEQ_initialize",
    "BSEQ_PT_Import",
    "BSEQ_PT_Import_Child1",
    "BSEQ_PT_Import_Child2",
    "BSEQ_Globals_Panel",
    "BSEQ_List_Panel",
    "BSEQ_UL_Obj_List",
    "BSEQ_scene_property",
    "BSEQ_Templates",
    "BSEQ_Settings",
    "BSEQ_Advanced_Panel",
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
    "BSEQ_OT_refresh_sequences",
    "BSEQ_OT_set_start_end_frames",
    "BSEQ_OT_batch_sequences",
    "BSEQ_PT_batch_sequences_settings",
    "BSEQ_OT_meshio_object",
    "BSEQ_OT_import_zip",
    "BSEQ_OT_delete_zips",
    "BSEQ_addon_preferences",
    "BSEQ_OT_load_all",
    "BSEQ_OT_load_all_recursive"
]
