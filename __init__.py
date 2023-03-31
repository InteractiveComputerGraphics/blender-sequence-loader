bl_info = {
    "name": "Sequence Loader",
    "description": "Loader for meshio supported mesh files/ simulation sequences",
    "author": "Interactive Computer Graphics",
    "version": (0, 1, 5),
    "blender": (3, 4, 0),
    "warning": "",
    "support": "COMMUNITY",
    "category": "Import-Export",
}

import bpy
import os
import sys

current_folder = os.path.dirname(os.path.abspath(__file__))
if current_folder not in sys.path:
    sys.path.append(current_folder)

if bpy.context.preferences.filepaths.use_relative_paths == True:
    bpy.context.preferences.filepaths.use_relative_paths = False

from bseq import *
from bseq.operators import menu_func_import

classes = [
    BSEQ_obj_property,
    BSEQ_scene_property,
    BSEQ_mesh_property,
    BSEQ_OT_load,
    BSEQ_OT_edit,
    BSEQ_OT_resetpt,
    BSEQ_OT_resetins,
    BSEQ_OT_resetmesh,
    BSEQ_Import,
    BSEQ_List_Panel,
    BSEQ_UL_Obj_List,
    BSEQ_Settings,
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
    WM_OT_batchSequences,
    WM_OT_MeshioObject
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
    unsubscribe_to_selected()


if __name__ == "__main__":

    # unregister()
    register()
