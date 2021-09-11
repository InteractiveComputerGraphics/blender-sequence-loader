bl_info = {
    "name": "MeshioImporterTool",
    "description": "Importer for meshio supported mesh files.",
    "author": "Hantao Hui",
    "version": (1, 0),
    "blender": (2, 90, 0),
    "warning": "",
    "support": "COMMUNITY",
    "category": "Import-Export",
}

import bpy
import os
import sys

current_folder = os.path.dirname(os.path.abspath(__file__))
if current_folder not in sys.path:
    print("current directory of addon is:" + current_folder)
    sys.path.append(current_folder)
from meshioimporter import *

classes = [
    importer_properties,
    MESHIO_IMPORT_PT_main_panel,
    meshio_loader_OT_load,
    particle_OT_clear,
    sequence_list_panel,
    SEQUENCE_UL_list,
    color_attribtue,
    imported_seq_properties,
    tool_properties,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.my_tool = bpy.props.PointerProperty(type=tool_properties)
    bpy.app.handlers.load_post.append(load_post)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.my_tool


if __name__ == "__main__":

    # unregister()
    register()