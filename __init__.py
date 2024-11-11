# bl_info = {
#     "name": "Sequence Loader",
#     "description": "Loader for meshio supported mesh files/ simulation sequences",
#     "author": "Interactive Computer Graphics",
#     "version": (0, 3, 2),
#     "blender": (4, 0, 0),
#     "warning": "",
#     "support": "COMMUNITY",
#     "category": "Import-Export",
# }

import bpy
import os
import sys

# current_folder = os.path.dirname(os.path.abspath(__file__))
# if current_folder not in sys.path:
#     sys.path.append(current_folder)
# # add paths of external libraries to sys.path
# if os.path.exists(os.path.join(current_folder, "extern")):
#     external_libs = ["fileseq/src", "meshio/src", "python-future/src", "rich"]
#     for lib in external_libs:
#         lib_path = os.path.join(current_folder, "extern", lib)
#         if lib_path not in sys.path:
#             sys.path.append(lib_path)


# if bpy.context.preferences.filepaths.use_relative_paths == True:
#     bpy.context.preferences.filepaths.use_relative_paths = False

from bseq import *
from bseq.operators import menu_func_import, add_keymap, delete_keymap

classes = [
    BSEQ_obj_property,
    BSEQ_scene_property,
    BSEQ_mesh_property,
    BSEQ_OT_load,
    BSEQ_OT_edit,
    BSEQ_OT_resetpt,
    BSEQ_OT_resetins,
    BSEQ_OT_resetmesh,
    BSEQ_PT_Import,
    BSEQ_PT_Import_Child1,
    BSEQ_PT_Import_Child2,
    BSEQ_Globals_Panel,
    BSEQ_List_Panel,
    BSEQ_UL_Obj_List,
    BSEQ_Settings,
    BSEQ_Advanced_Panel,
    BSEQ_Templates,
    BSEQ_UL_Att_List,
    BSEQ_OT_set_as_split_norm,
    BSEQ_OT_remove_split_norm,
    BSEQ_OT_disable_selected,
    BSEQ_OT_enable_selected,
    BSEQ_OT_refresh_seq,
    BSEQ_OT_disable_all,
    BSEQ_OT_enable_all,
    BSEQ_OT_refresh_sequences,
    BSEQ_OT_set_start_end_frames,
    BSEQ_OT_batch_sequences,
    BSEQ_PT_batch_sequences_settings,
    BSEQ_OT_meshio_object,
    # BSEQ_OT_import_zip,
    # BSEQ_OT_delete_zips,
    # BSEQ_addon_preferences,
    BSEQ_OT_load_all,
    BSEQ_OT_load_all_recursive
]

def register():
    bpy.app.handlers.load_post.append(BSEQ_initialize)
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TEXT_MT_templates.append(draw_template)
    bpy.types.Scene.BSEQ = bpy.props.PointerProperty(type=BSEQ_scene_property)
    bpy.types.Object.BSEQ = bpy.props.PointerProperty(type=BSEQ_obj_property)
    bpy.types.Mesh.BSEQ = bpy.props.PointerProperty(type=BSEQ_mesh_property)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    add_keymap()

    # manually call this function once
    # so when addon being installed, it can run correctly
    # because scene is not used, so pass None into it
    BSEQ_initialize(None)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.TEXT_MT_templates.remove(draw_template)
    del bpy.types.Scene.BSEQ
    del bpy.types.Object.BSEQ
    bpy.app.handlers.load_post.remove(BSEQ_initialize)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    delete_keymap()
    unsubscribe_to_selected()

if __name__ == "__main__":
    # unregister()
    register()
