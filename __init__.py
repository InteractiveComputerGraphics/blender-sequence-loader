bl_info = {
    "name": "Sim Loader",
    "description": "Loader for meshio supported mesh files/ simulation sequences",
    "author": "Hantao Hui",
    "version": (1, 0),
    "blender": (3, 0, 0),
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

from simloader import *

classes = [
    importer_properties,
    meshio_loader_OT_load,
    particle_OT_clear,
    SIMLOADER_Import,
    SIMLOADER_List_Panel,
    SIMLOADER_UL_List,
    color_attribtue,
    imported_seq_properties,
    tool_properties,
    SIMLOADER_Settings,
    # SIMLOADER_Edit,
    sequence_OT_edit,
    SIMLOADER_Templates,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TEXT_MT_templates.append(draw_template)
    bpy.types.Scene.sim_loader = bpy.props.PointerProperty(type=tool_properties)
    bpy.app.handlers.load_post.append(load_post)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.TEXT_MT_templates.remove(draw_template)
    del bpy.types.Scene.sim_loader
    bpy.app.handlers.load_post.remove(load_post)
    unsubscribe_to_selected


if __name__ == "__main__":

    # unregister()
    register()