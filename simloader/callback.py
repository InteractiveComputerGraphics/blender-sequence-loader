import bpy
import fileseq

#  Code here are mostly about the callback functions and update functions used in properties.py


def update_path(self, context):
    # When the path has been changed, reset the selected sequence to None
    context.scene.SIMLOADER.fileseq = "None"
    context.scene.SIMLOADER.use_pattern = False
    context.scene.SIMLOADER.pattern = ""


def callback_fileseq(self, context):
    '''
    Detects all the file sequences in the directory
    '''

    p = context.scene.SIMLOADER.path
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


def update_selected_obj_num(self, context):
    # Here is when select sequences, then change the corresponding object to active object
    collection = bpy.data.collections['SIMLOADER']
    index = context.scene.SIMLOADER.selected_obj_num
    obj = collection.objects[index]
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    context.view_layer.objects.active = obj
