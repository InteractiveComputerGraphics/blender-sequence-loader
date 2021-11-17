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
    path: bpy.props.StringProperty(
        name="Directory",
        subtype="DIR_PATH",
        description="You need to go to the folder with the sequence, then click \"Accept\". ",
    )
    relative: bpy.props.BoolProperty(
        name='Use relative path', description="whether or not to use reletive path")
    fileseq: bpy.props.EnumProperty(
        name="File Sequences",
        description="Please choose the file sequences you want",
        items=callback_fileseq,
        update=update_fileseq,
    )
    pattern: bpy.props.StringProperty(
        name="Pattern", description="You can specify the pattern here, in case the sequence can't be deteced.")
    type: bpy.props.EnumProperty(
        name="Type",
        description="choose particles or mesh",
        items=[("mesh", "Add Mesh", ""), ("particle", "Add Particles", "")],
    )


#  Because I can't create a CollectionProperty of StringProperty, so I have to create a CollectionProperty of PropertyGroup (color attribute), and the PropertyGroup has the only information, which is the name of color attribute.
class color_attribtue(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name='color attr')


class imported_seq_properties(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name='name', description="name of the sequence, can be modified by user", update = update_name, )
    pattern: bpy.props.StringProperty(
        name='pattern', description="the (absolutoe or relative) path of the sequence")
    relative: bpy.props.BoolProperty(
        name='Use relative path', description="whether or not to use reletive path")
    type: bpy.props.IntProperty(
        name='type', description='type of this sequence, particle or mesh, or other', default=0, min=0, max=1)
    used_color_attribute: bpy.props.PointerProperty(type=color_attribtue)
    all_attributes: bpy.props.CollectionProperty(type=color_attribtue)
    all_attributes_enum: bpy.props.EnumProperty(
        name="Color Field",
        description="choose attributes used for coloring",
        items=callback_color_attribute,
        update=update_color_attribute,
    )
    start: bpy.props.IntProperty(
        name='start', description='start frame number',update = update_start,min=0,default = 0)
    end: bpy.props.IntProperty(name='end', description='end frame number',update = update_end,min=1,default = 500)

    # general
    max_value: bpy.props.FloatProperty(
        name='max value', description='max value to clamp the field', update=update_max_value)
    min_value: bpy.props.FloatProperty(
        name='min value', description='min value to clamp the field', default=0, update=update_min_value)
    material_name: bpy.props.StringProperty()

    #  because now, importer list has different size with property imported.
    #  when using imported_num, this can directly lead to the index of property imported, but not index of importer list
    #  so I created this additional property importer_list_index
    importer_list_index: bpy.props.IntProperty(
        name='importer_list_index', default=0, min=0)

    # mesh only
    mesh_name: bpy.props.StringProperty()

    # particles only
    particle_settings_name: bpy.props.StringProperty()
    radius: bpy.props.FloatProperty(name='radius', description='raidus of the particles',
                                    default=0.01, update=update_particle_radius, min=0, precision=6)
    display: bpy.props.EnumProperty(
        name="display method",
        description="the way to display particles in viewport, rendered or point",
        items=[("RENDER", "Rendered", ""), ('DOT', 'Point', '')],
        update=update_display,
    )
    sphere_obj_name: bpy.props.StringProperty()


class tool_properties(bpy.types.PropertyGroup):
    importer: bpy.props.PointerProperty(type=importer_properties)
    imported: bpy.props.CollectionProperty(type=imported_seq_properties)
    imported_num: bpy.props.IntProperty(
        name='imported count', description='the number of imported sequence, when selecting from ui list', default=0,update=update_imported_num)
