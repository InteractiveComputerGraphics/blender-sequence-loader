import bpy
import fileseq
from .utils import show_message_box
from .importer_manager import importer_list

#  Code here are mostly about the callback functions and update functions used in properties.py

def update_path(self, context):
    # When the path has been changed, reset the selected sequence to None
    context.scene.sim_loader.importer.fileseq = "None"
    context.scene.sim_loader.importer.use_pattern = False
    context.scene.sim_loader.importer.pattern = ""


def callback_fileseq(self, context):
    '''
    Detects all the file sequences in the directory
    '''

    p = context.scene.sim_loader.importer.path
    try:
        f = fileseq.findSequencesOnDisk(p)
    except:
        return [("None", "No sequence detected", "")]

    if not f:
        return [("None", "No sequence detected", "")]
    file_seq = []
    if len(f) >= 20:
        file_seq.append(("None", "Too much sequence detected, could be false detection, please use pattern below", ""))
    else:
        file_seq.append(("None", "Please select the pattern", ""))
        for seq in f:
            file_seq.append((str(seq), seq.basename() + "@" + seq.extension(), ""))
    return file_seq


def update_radius(self, context):
    '''
    This function here updates the radius of selected particle sequence.
    '''
    idx = context.scene.sim_loader.imported_num
    collection = bpy.data.collections['SIMLOADER'].objects
    obj = collection[idx]
    node = obj.modifiers[0].node_group.nodes[2]
    node.inputs[3].default_value = obj.SIMLOADER.radius


def update_imported_num(self, context):
    # Here is when select sequences, then change the corresponding object to active object
    collection = bpy.data.collections['SIMLOADER']
    index = context.scene.sim_loader.imported_num
    obj = collection.objects[index]
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    context.view_layer.objects.active = obj
