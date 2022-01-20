from .mesh_importer import mesh_importer
from .particle_importer import particle_importer
import fileseq
import bpy
from bpy.app.handlers import persistent
from .utils import show_message_box
import os

importer_list = []


def selected_callback():
    if not bpy.context.view_layer.objects.active:
        return
    name = bpy.context.active_object.name
    idx = bpy.data.collections['SIMLOADER'].objects.find(name)
    if idx >= 0:
        bpy.context.scene.sim_loader.imported_num = idx


def subscribe_to_selected():
    # A known problem of this function,
    # This function will not be executed, when the first time this addon is installed.
    # It will start to work, e.g. restart the blender, then in `load_post` function, this function will be called and start to work
    import simloader
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.LayerObjects, 'active'),
        #  don't know why it needs this owner, so I set owner to this module `meshioimporter`
        owner=simloader,
        #  no args
        args=(()),
        notify=selected_callback,
    )


def unsubscribe_to_selected():
    import simloader
    bpy.msgbus.clear_by_owner(simloader)


@persistent
def load_post(scene):
    '''
    When everytime saved .blender file starts, this function here will read the information from .blender file, and initialize all the importers.
    '''
    imported_list = bpy.context.scene.sim_loader.imported
    for l in imported_list:
        # particle importer
        if l.type == 0:
            fs = None
            path = None
            if l.relative:
                path = os.path.dirname(bpy.data.filepath) + "/" + l.pattern
            else:
                path = l.pattern
            try:
                fs = fileseq.findSequenceOnDisk(path)
            except:
                show_message_box("Can't find sequence: " + path + "  please edit the path or remove it", icon="ERROR")
            Pi = particle_importer(fileseq=fs, particle_settings_name=l.particle_settings_name)
            importer_list.append(Pi)
            l.importer_list_index = len(importer_list) - 1
            for all_att in l.all_attributes:
                Pi.color_attributes.append(all_att.name)
            Pi.script_name = l.script_name
            Pi.set_color_attribute(l.used_color_attribute.name)
            Pi.max_value = l.max_value
            Pi.min_value = l.min_value

            bpy.app.handlers.frame_change_post.append(Pi)
        # mesh importer
        elif l.type == 1:
            fs = None
            path = None
            if l.relative:
                path = os.path.dirname(bpy.data.filepath) + "/" + l.pattern
            else:
                path = l.pattern
            try:
                fs = fileseq.findSequenceOnDisk(path)
            except:
                show_message_box("Can't find sequence: " + path + "  please editing the path or remove it", icon="ERROR")
            Mi = mesh_importer(fileseq=fs, mesh_name=l.mesh_name)
            importer_list.append(Mi)
            l.importer_list_index = len(importer_list) - 1

            for all_att in l.all_attributes:
                Mi.color_attributes.append(all_att.name)
            Mi.script_name = l.script_name
            Mi.set_color_attribute(l.used_color_attribute.name)
            Mi.max_value = l.max_value
            Mi.min_value = l.min_value
            bpy.app.handlers.frame_change_post.append(Mi)
    subscribe_to_selected()
