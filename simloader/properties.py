import bpy
from .callback import *


class SIMLOADER_scene_property(bpy.types.PropertyGroup):
    path: bpy.props.StringProperty(name="Directory",
                                   subtype="DIR_PATH",
                                   description="You need to go to the folder with the sequence, then click \"Accept\". ",
                                   update=update_path)
    relative: bpy.props.BoolProperty(name='Use relative path', description="whether or not to use reletive path", default=False)
    fileseq: bpy.props.EnumProperty(
        name="File Sequences",
        description="Please choose the file sequences you want",
        items=callback_fileseq,
    )
    use_pattern: bpy.props.BoolProperty(name='Use pattern',
                                        description="whether or not to use manually typed pattern",
                                        default=False)
    pattern: bpy.props.StringProperty(name="Pattern",
                                      description="You can specify the pattern here, in case the sequence can't be deteced.")
    selected_obj_num: bpy.props.IntProperty(name='imported count',
                                            description='the number of imported sequence, when selecting from ui list',
                                            default=0,
                                            update=update_selected_obj_num)
    selected_attribute_num: bpy.props.IntProperty(
        default=0,
        #   update=update_imported_num
    )


class SIMLOADER_obj_property(bpy.types.PropertyGroup):
    # stopped: bpy.props.BoolProperty(default= False,description="When true, the object will stop animation")
    radius: bpy.props.FloatProperty(default=0.05, update=update_radius, min=0, precision=6)
    use_advance: bpy.props.BoolProperty(default=False)
    script_name: bpy.props.StringProperty()
    use_relative: bpy.props.BoolProperty(default=False)
    pattern: bpy.props.StringProperty()
