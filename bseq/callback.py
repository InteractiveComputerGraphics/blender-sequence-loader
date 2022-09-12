import bpy
import fileseq

#  Code here are mostly about the callback/update/items functions used in properties.py


def update_path(self, context):
    # When the path has been changed, reset the selected sequence to None
    context.scene.BSEQ['fileseq'] = 1
    context.scene.BSEQ.use_pattern = False
    context.scene.BSEQ.pattern = ""


def item_fileseq(self, context):
    '''
    Detects all the file sequences in the directory
    '''

    p = context.scene.BSEQ.path
    try:
        f = fileseq.findSequencesOnDisk(p)
    except:
        return [("None", "No sequence detected", "", 1)]

    if not f:
        return [("None", "No sequence detected", "", 1)]
    file_seq = []
    if len(f) >= 20:
        file_seq.append(("None", "Too much sequence detected, could be false detection, please use pattern below", "", 1))
    else:
        count = 1
        for seq in f:
            file_seq.append((str(seq), seq.basename() + "@" + seq.extension(), "", count))
            count += 1
    return file_seq


def update_selected_obj_num(self, context):

    # Here is when select sequences, then change the corresponding object to active object
    index = context.scene.BSEQ.selected_obj_num
    obj = bpy.data.objects[index]

    if context.scene.BSEQ.selected_obj_deselectall_flag:
        bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    context.view_layer.objects.active = obj


def poll_material(self, material):
    return not material.is_grease_pencil

def poll_edit_obj(self, object):
    return object.BSEQ.init