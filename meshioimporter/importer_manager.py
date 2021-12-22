from .mesh_importer import *
from .particle_importer import *
import fileseq
import bpy
from bpy.app.handlers import persistent
importer_list = []

from .callback import selected_callback



def subscribe_to_selected():
    import meshioimporter       
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.LayerObjects, 'active'),
        #  don't know why it needs this owner, so I set owner to this module `meshioimporter`
        owner=meshioimporter,
        #  no args
        args = (()),
        notify=selected_callback,
        )



@persistent
def load_post(scene):
    '''
    When everytime saved .blender file starts, this function here will read the information from .blender file, and initialize all the importers.
    '''
    global importer_list
    imported_list = bpy.context.scene.my_tool.imported
    for l in imported_list:
        # particle importer
        if l.type == 0:
            fs=None
            path = None
            if l.relative:
                path = os.path.dirname(bpy.data.filepath)+"/"+l.pattern
            else:
                path = l.pattern
            try:
                fs = fileseq.findSequenceOnDisk(path)
            except:
                show_message_box("Can't find sequence: "+ path+ "  please editing the path or remove it",icon = "ERROR")
            Pi = particle_importer(fileseq=fs, particle_settings_name=l.particle_settings_name, radius=l.radius)
            importer_list.append(Pi)
            l.importer_list_index = len(importer_list)-1
            for all_att in l.all_attributes:
                Pi.color_attributes.append(all_att.name)
            Pi.script_name = l.script_name
            Pi.set_color_attribute(l.used_color_attribute.name)
            Pi.set_max_value(l.max_value)
            Pi.set_min_value(l.min_value)

            bpy.app.handlers.frame_change_post.append(Pi)
        # mesh importer
        elif l.type == 1:
            fs=None
            path = None
            if l.relative:
                path = os.path.dirname(bpy.data.filepath)+"/"+l.pattern
            else:
                path = l.pattern
            try:
                fs = fileseq.findSequenceOnDisk(path)
            except:
                show_message_box("Can't find sequence: "+ path+ "  please editing the path or remove it",icon = "ERROR")
            Mi = mesh_importer(
                fileseq=fs, mesh_name=l.mesh_name)
            importer_list.append(Mi)
            l.importer_list_index = len(importer_list)-1

            for all_att in l.all_attributes:
                Mi.color_attributes.append(all_att.name)
            Mi.script_name = l.script_name
            Mi.set_color_attribute(l.used_color_attribute.name)
            Mi.set_max_value(l.max_value)
            Mi.set_min_value(l.min_value)
            bpy.app.handlers.frame_change_post.append(Mi)
    subscribe_to_selected()