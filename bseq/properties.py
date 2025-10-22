import bpy
from .callback import *
from mathutils import Matrix

class BSEQ_scene_property(bpy.types.PropertyGroup):
    path: bpy.props.StringProperty(name="Directory",
                                   subtype="DIR_PATH",
                                   description="You need to go to the folder with the sequence, then click \"Accept\"",
                                   update=update_path,
                                   options={'PATH_SUPPORTS_BLEND_RELATIVE' if bpy.app.version >= (4, 5, 0) else ''}
                                   )
    
    use_relative: bpy.props.BoolProperty(name='Relative Paths', 
                                     description="Toggle relative paths on/off", 
                                     default=False,
                                     )
    
    use_imported_normals: bpy.props.BoolProperty(name='Import Normals',
                                                description="Use normals from imported mesh (see README for details)",
                                                default=False,
                                                )

    root_path: bpy.props.StringProperty(name="Root Directory",
                                        subtype="DIR_PATH",
                                        description="Select root folder for all relative paths. If empty, root is folder of the Blender file",
                                        update=update_path,
                                        default="",
                                        options={'PATH_SUPPORTS_BLEND_RELATIVE' if bpy.app.version >= (4, 5, 0) else ''}
                                        )
    
    fileseq: bpy.props.EnumProperty(
        name="File Sequences",
        description="Select a file sequence",
        items=item_fileseq,
    )

    use_pattern: bpy.props.BoolProperty(name='Custom Pattern',
                                        description="Use manually typed pattern. Useful if the sequence can't be deteced",
                                        default=False,
                                        )
    
    pattern: bpy.props.StringProperty(name="Pattern",
                                      description="Custom pattern. Use @ for frame number. Example: file_@.obj",
                                      )
    
    selected_obj_deselectall_flag: bpy.props.BoolProperty(default=True,
                                                          description="Flag that determines whether to deselect all items or not",
                                                          )
    
    selected_obj_num: bpy.props.IntProperty(name='Sequences List',
                                            default=0,
                                            update=update_selected_obj_num,
                                            )
    
    selected_attribute_num: bpy.props.IntProperty(name="Select Vertex Attribute",default=0)

    material: bpy.props.PointerProperty(
        name="Material",
        type=bpy.types.Material,
        poll=poll_material,
    )

    edit_obj: bpy.props.PointerProperty(
        type=bpy.types.Object,
        poll=poll_edit_obj,
    )

    print: bpy.props.BoolProperty(name='Print Sequence Information',
                                  description="Print useful information during rendering to file in same folder as render output",
                                  default=True,
                                  )

    auto_refresh_active: bpy.props.BoolProperty(name='Auto Refresh Active Sequences',
                                         description="Auto refresh all active sequences every frame",
                                         default=False,
                                         )

    auto_refresh_all: bpy.props.BoolProperty(name='Auto Refresh All Sequences',
                                         description="Auto refresh all sequences every frame",
                                         default=False,
                                         )
    
    preload_next_frame: bpy.props.BoolProperty(name='Preload next frame while rendering',
                                             description="Starts loading the next sequence frame into the RAM while rendering the current frame",
                                             default=False,
                                             update=update_preloader
                                         )
        
    use_custom_transform: bpy.props.BoolProperty(name='Custom Transform', 
                                                 description="Use a custom transformation matrix when importing", 
                                                 default=False,
                                                 )

    custom_location: bpy.props.FloatVectorProperty(name='Custom Location', 
                                                   description='Set custom location vector', 
                                                   size=3, 
                                                   subtype="TRANSLATION",
                                                   )
    
    custom_rotation: bpy.props.FloatVectorProperty(name='Custom Rotation', 
                                                   description='Set custom Euler angles', 
                                                   size=3, 
                                                   subtype="EULER", 
                                                   default=[0,0,0],
                                                   )
    
    custom_scale: bpy.props.FloatVectorProperty(name='Custom Scale', 
                                                description='Set custom scaling vector', 
                                                size=3, 
                                                subtype="COORDINATES", 
                                                default=[1,1,1],
                                                )
    
    use_blender_obj_import: bpy.props.BoolProperty(name='Blender .obj import',
                                                   description="Use Blender's built-in .obj import function (or meshio's .obj import function)",
                                                   default=True,
                                                   )
    
    filter_string: bpy.props.StringProperty(name='Filter String',
                                            description='Filter string for file sequences',
                                            default='',
                                            )
    
class BSEQ_obj_property(bpy.types.PropertyGroup):
    init: bpy.props.BoolProperty(default=False)
    enabled: bpy.props.BoolProperty(default=True,
                                    name="Activate/Deactivate",
                                    description="If deactivated, sequence won't be updated each frame")
    use_advance: bpy.props.BoolProperty(default=False)
    script_name: bpy.props.StringProperty(name="Script name")
    path: bpy.props.StringProperty(name="Path of sequence", subtype="DIR_PATH", options={'PATH_SUPPORTS_BLEND_RELATIVE' if bpy.app.version >= (4, 5, 0) else ''})
    pattern: bpy.props.StringProperty(name="Pattern of sequence")
    current_file: bpy.props.StringProperty(description="File of sequence that is currently loaded")
    frame: bpy.props.IntProperty(name="Frame")
    start_end_frame: bpy.props.IntVectorProperty(name="Start and end frames", size=2, default=(0, 0))
    match_frames: bpy.props.BoolProperty(default=False, 
                                         name="Match Blender frame numbers",
                                         description="Show only frames that match the current frame number",
                                         )
    last_benchmark: bpy.props.FloatProperty(name="Last loading time")

# set this property for mesh, not object (maybe change later?)
class BSEQ_mesh_property(bpy.types.PropertyGroup):
    split_norm_att_name: bpy.props.StringProperty(default="")
