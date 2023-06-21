import bpy
from .callback import *
from mathutils import Matrix

class BSEQ_scene_property(bpy.types.PropertyGroup):
    path: bpy.props.StringProperty(name="Directory",
                                   subtype="DIR_PATH",
                                   description="You need to go to the folder with the sequence, then click \"Accept\". ",
                                   update=update_path)
    relative: bpy.props.BoolProperty(name='Use relative path', description="whether or not to use reletive path", default=False)
    root_path: bpy.props.StringProperty(name="Root Directory",
                                        subtype="DIR_PATH",
                                        description="Select a root folder for all relative paths. When not set the current filename is used.",
                                        update=update_path)
    fileseq: bpy.props.EnumProperty(
        name="File Sequences",
        description="Please choose the file sequences you want",
        items=item_fileseq,
    )
    use_pattern: bpy.props.BoolProperty(name='Use pattern',
                                        description="whether or not to use manually typed pattern",
                                        default=False)
    pattern: bpy.props.StringProperty(name="Pattern",
                                      description="You can specify the pattern here, in case the sequence can't be deteced.")
    
    file_paths: bpy.props.StringProperty(name="File",
                                        subtype="FILE_PATH",
                                        description="Select a root folder for all relative paths. When not set the current filename is used.")

    selected_obj_deselectall_flag: bpy.props.BoolProperty(default=True,
                                                          description="the flag to determine whether call deselect all or not ")
    selected_obj_num: bpy.props.IntProperty(name='imported count',
                                            description='the number of imported sequence, when selecting from ui list',
                                            default=0,
                                            update=update_selected_obj_num)
    selected_attribute_num: bpy.props.IntProperty(default=0)

    material: bpy.props.PointerProperty(
        type=bpy.types.Material,
        poll=poll_material,
    )

    edit_obj: bpy.props.PointerProperty(
        type=bpy.types.Object,
        poll=poll_edit_obj,
    )

    print: bpy.props.BoolProperty(name='print',
                                  description="whether or not to print additional information when rendering",
                                  default=True)

    auto_refresh: bpy.props.BoolProperty(name='auto refresh',
                                         description="whether or not to auto refresh all the sequence every frame",
                                         default=False)
    
    use_custom_transform: bpy.props.BoolProperty(name='Use custom transformation matrix', 
                                                 description="Whether or not to use a custom transformation matrix", 
                                                 default=False)

    custom_location: bpy.props.FloatVectorProperty(name='Custom Location', 
                                                   description='Set custom location vector', 
                                                   size=3, 
                                                   subtype="TRANSLATION")
    
    custom_rotation: bpy.props.FloatVectorProperty(name='Custom Rotation', 
                                                   description='Set custom rotation vector', 
                                                   size=3, 
                                                   subtype="EULER", 
                                                   default=[0,0,0])
    
    custom_scale: bpy.props.FloatVectorProperty(name='Custom Scale', 
                                                description='Set custom scaling vector', 
                                                size=3, 
                                                subtype="COORDINATES", 
                                                default=[1,1,1])
    
    use_blender_obj_import: bpy.props.BoolProperty(name='Use Blender Object Import',
                                                   description="Whether or not to use Blender's built-in object import function",
                                                   default=True)

class BSEQ_obj_property(bpy.types.PropertyGroup):
    init: bpy.props.BoolProperty(default=False)
    enabled: bpy.props.BoolProperty(default=True,
                                    description="When disbaled, the sequence won't be updated at each frame. Enabled by default")
    use_advance: bpy.props.BoolProperty(default=False)
    script_name: bpy.props.StringProperty()
    use_relative: bpy.props.BoolProperty(default=False)
    pattern: bpy.props.StringProperty()
    frame: bpy.props.IntProperty()
    start_end_frame: bpy.props.IntVectorProperty(name="Start and End Frames", size=2, default=(0, 0))
    last_benchmark: bpy.props.FloatProperty(name="Last Loading Time")

# set this property for mesh, not object (maybe change later?)
class BSEQ_mesh_property(bpy.types.PropertyGroup):
    split_norm_att_name: bpy.props.StringProperty(default="")
