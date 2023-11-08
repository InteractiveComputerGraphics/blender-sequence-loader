import bpy
from .callback import *
from mathutils import Matrix

class BSEQ_ImportedZip(bpy.types.PropertyGroup):
    path: bpy.props.StringProperty(name="Directory",
                                    subtype="DIR_PATH",
                                    )

bpy.utils.register_class(BSEQ_ImportedZip)

class BSEQ_scene_property(bpy.types.PropertyGroup):
    path: bpy.props.StringProperty(name="Directory",
                                   subtype="DIR_PATH",
                                   description="You need to go to the folder with the sequence, then click \"Accept\"",
                                   update=update_path,
                                   )
    
    relative: bpy.props.BoolProperty(name='Use relative path', 
                                     description="Use relative path", 
                                     default=True,
                                     )
    
    use_imported_normals: bpy.props.BoolProperty(name='Use Imported Normals',
                                                description="Use normals from imported mesh",
                                                default=False,
                                                )

    root_path: bpy.props.StringProperty(name="Root Directory",
                                        subtype="DIR_PATH",
                                        description="Select a root folder for all relative paths. If not set, the current filename is used",
                                        update=update_path,
                                        default="",
                                        )
    
    fileseq: bpy.props.EnumProperty(
        name="File Sequences",
        description="Choose file sequences.",
        items=item_fileseq,
    )

    use_pattern: bpy.props.BoolProperty(name='Use pattern',
                                        description="Use manually typed pattern, if the sequence can't be deteced",
                                        default=False,
                                        )
    
    pattern: bpy.props.StringProperty(name="Pattern",
                                      description="Custom pattern.",
                                      )
    
    selected_obj_deselectall_flag: bpy.props.BoolProperty(default=True,
                                                          description="Flag that determines whether to deselect all items or not",
                                                          )
    
    selected_obj_num: bpy.props.IntProperty(name='imported count',
                                            description='Number of imported sequences, when selecting from UI list',
                                            default=0,
                                            update=update_selected_obj_num,
                                            )
    
    selected_attribute_num: bpy.props.IntProperty(default=0)

    material: bpy.props.PointerProperty(
        type=bpy.types.Material,
        poll=poll_material,
    )

    edit_obj: bpy.props.PointerProperty(
        type=bpy.types.Object,
        poll=poll_edit_obj,
    )

    print: bpy.props.BoolProperty(name='Print Sequence Information',
                                  description="Print additional information during rendering to a file in the same folder as the render output",
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
                                                   description='Set custom rotation vector', 
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
    
    imported_zips: bpy.props.CollectionProperty(type=BSEQ_ImportedZip)

class BSEQ_obj_property(bpy.types.PropertyGroup):
    init: bpy.props.BoolProperty(default=False)
    enabled: bpy.props.BoolProperty(default=True,
                                    description="If disabled, the sequence won't be updated each frame")
    use_advance: bpy.props.BoolProperty(default=False)
    script_name: bpy.props.StringProperty()
    pattern: bpy.props.StringProperty()
    frame: bpy.props.IntProperty()
    start_end_frame: bpy.props.IntVectorProperty(name="Start and end frames", size=2, default=(0, 0))
    last_benchmark: bpy.props.FloatProperty(name="Last loading time")

# set this property for mesh, not object (maybe change later?)
class BSEQ_mesh_property(bpy.types.PropertyGroup):
    split_norm_att_name: bpy.props.StringProperty(default="")
