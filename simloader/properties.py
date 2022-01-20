import bpy
from .callback import *

# Structure:
# tool_properties:
#    1. importer (importer_properties object)
#    2. imported:
#       2.1 imported_seq_properties
#           2.1.1 color_attribute


class importer_properties(bpy.types.PropertyGroup):
    '''
    This is all the properties showed on main panel
    '''
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




class imported_seq_properties(bpy.types.PropertyGroup):
    # name: bpy.props.StringProperty(name='name', description="name of the sequence, can be modified by user", update=update_name)
    # pattern: bpy.props.StringProperty(name='pattern', description="the (absolutoe or relative) path of the sequence")
    # relative: bpy.props.BoolProperty(name='Use relative path', description="whether or not to use reletive path")
    # type: bpy.props.IntProperty(name='type',
    #                             description='type of this sequence, particle or mesh, or other',
    #                             default=0,
    #                             min=0,
    #                             max=1)
    # used_color_attribute: bpy.props.PointerProperty(type=color_attribtue)
    # all_attributes: bpy.props.CollectionProperty(type=color_attribtue)
    # all_attributes_enum: bpy.props.EnumProperty(
    #     name="Color Field",
    #     description="choose attributes used for coloring",
    #     items=callback_color_attribute,
    #     update=update_color_attribute,
    # )

    # # general
    # max_value: bpy.props.FloatProperty(name='Clamped by max value',
    #                                    description='max value to clamp the field',
    #                                    update=update_max_value)
    # min_value: bpy.props.FloatProperty(name='Clamped by min value',
    #                                    description='min value to clamp the field',
    #                                    default=0,
    #                                    update=update_min_value)
    # use_real_value: bpy.props.BoolProperty(name='Use original attribute value',
    #                                        description="Wheter to use real attribute value or not",
    #                                        default=False,
    #                                        update=update_use_real_value)

    # ref_max_value: bpy.props.FloatProperty(name='Max (norm) value in current frame',
    #                                        description='max value in current frame',
    #                                        get=get_ref_max_value)
    # ref_min_value: bpy.props.FloatProperty(name='Min (norm) value in current frame',
    #                                        description='min value in current frame',
    #                                        get=get_ref_min_value)

    # use_clamped_value: bpy.props.BoolProperty(name='Use clamped attribute value',
    #                                           description="Wheter to use clamped attribute value or not",
    #                                           default=True,
    #                                           update=update_use_clamped_value)

    # #  because now, importer list has different size with property imported.
    # #  when using imported_num, this can directly lead to the index of property imported, but not index of importer list
    # #  so I created this additional property importer_list_index
    # importer_list_index: bpy.props.IntProperty(name='importer_list_index', default=0, min=0)


    # # mesh only
    # mesh_name: bpy.props.StringProperty()

    # # particles only
    # particle_settings_name: bpy.props.StringProperty()
    # display: bpy.props.EnumProperty(
    #     name="display method",
    #     description="the way to display particles in viewport, rendered or point",
    #     items=[('DOT', 'Point', ''), ("RENDER", "Rendered", "")],
    #     update=update_display,
    # )
    pass


class tool_properties(bpy.types.PropertyGroup):
    importer: bpy.props.PointerProperty(type=importer_properties)
    imported: bpy.props.CollectionProperty(type=imported_seq_properties)
    imported_num: bpy.props.IntProperty(name='imported count',
                                        description='the number of imported sequence, when selecting from ui list',
                                        default=0,
                                        update=update_imported_num)
    imported_num2: bpy.props.IntProperty(name='imported count',
                                        description='the number of imported sequence, when selecting from ui list',
                                        default=0,
                                        update=update_imported_num)


class SIMLOADER_obj_property(bpy.types.PropertyGroup):
    # stopped: bpy.props.BoolProperty(default= False,description="When true, the object will stop animation")
    radius: bpy.props.FloatProperty(default=0.05,update = update_radius, min=0,precision=6)
    use_advance: bpy.props.BoolProperty(default=False)
    script_name: bpy.props.StringProperty()
    use_relative: bpy.props.BoolProperty(default=False)
    pattern: bpy.props.StringProperty()
