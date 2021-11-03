from .mesh_importer import *
from .particle_importer import *
import fileseq
import bpy
from bpy.app.handlers import persistent
importer = None
importer_list = []
imported_count = 0

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
            if l.relative:
                fs = fileseq.findSequenceOnDisk(
                os.path.dirname(bpy.data.filepath)+"/"+l.pattern)
            else:
                fs = fileseq.findSequenceOnDisk(l.pattern)
            Pi = particle_importer(fileseq=fs, mesh_name=l.mesh_name, emitter_obj_name=l.obj_name, sphere_obj_name=l.sphere_obj_name,
                                   material_name=l.material_name, radius=l.radius)
            importer_list.append(Pi)

            l.obj_name = Pi.emitter_obj_name
            l.sphere_obj_name = Pi.sphere_obj_name
            l.material_name = Pi.material_name
            l.importer_list_index = len(importer_list)-1
            for all_att in l.all_attributes:
                Pi.render_attributes.append(all_att.name)
            Pi.set_color_attribute(l.used_color_attribute.name)
            Pi.set_max_value(l.max_value)
            Pi.set_min_value(l.min_value)

            bpy.app.handlers.frame_change_post.append(Pi)
        # mesh importer
        elif l.type == 1:
            fs=None
            if l.relative:
                fs = fileseq.findSequenceOnDisk(
                os.path.dirname(bpy.data.filepath)+"/"+l.pattern)
            else:
                fs = fileseq.findSequenceOnDisk(l.pattern)
            Mi = mesh_importer(
                fileseq=fs, mesh_name=l.mesh_name, obj_name=l.obj_name, material_name=l.material_name)
            importer_list.append(Mi)
            l.obj_name = Mi.obj_name
            l.mesh_name = Mi.mesh_name
            l.material_name = Mi.material_name
            l.importer_list_index = len(importer_list)-1

            for all_att in l.all_attributes:
                Mi.render_attributes.append(all_att.name)
            Mi.set_color_attribute(l.used_color_attribute.name)
            Mi.set_max_value(l.max_value)
            Mi.set_min_value(l.min_value)
            bpy.app.handlers.frame_change_post.append(Mi)
    subscribe_to_selected()