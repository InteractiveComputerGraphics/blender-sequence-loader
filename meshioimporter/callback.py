import bpy
import fileseq
from .utils import show_message_box
from .importer_manager import importer_list

#  Code here are mostly about the callback functions and update functions used in properties.py


def get_index(context):
    # Because in my implementation, when delete/remove the sequence, it only delete the bpy.data.object
    # But it doesn't do anything about particle_importer or mesh_importer
    # Inside the particle_importer, it will always skip the __call__ function, because check_valid returns false
    # So here get_index, returns two indices,
    # The first index is the index of selected sequences among all the existing sequences
    # The second index is the index of importer, among all the importers(some importer may be be not valid)
    # So, in general, the second one is larger than the first one
    # If no sequence has been ever removed, then the second index is equal to the first index
    mytool = context.scene.my_tool
    idx = mytool.imported_num
    imported_obj_list = context.scene.my_tool.imported
    importer_list_index = imported_obj_list[idx].importer_list_index
    return idx, importer_list_index


def callback_color_attribute(self, context):
    '''
    When an imported sequence selected, this function returns all the color attributes it has, such as 'id', 'velocity', etc.
    '''
    attr_items = [('None', 'None', '')]
    mytool = context.scene.my_tool
    item = mytool.imported[mytool.imported_num]
    for i in item.all_attributes:
        attr_items.append((i.name, i.name, ''))
    return attr_items


def update_color_attribute(self, context):
    '''
    When an imported sequence selected, and a new color attribute selected, it will update the importer so the color can be correctly rendered. 
    '''

    idx, importer_list_index = get_index(context)
    importer = importer_list[importer_list_index]
    if not importer.check_valid():
        show_message_box("Sequence has been changed or removed")
        bpy.ops.sequence.remove()
        return
    mytool = context.scene.my_tool
    item = mytool.imported[idx]
    if item.all_attributes_enum != "None":
        importer.set_color_attribute(item.all_attributes_enum)
        # this is used to store the used color attribute
        item.used_color_attribute.name = item.all_attributes_enum
    else:
        importer.set_color_attribute(None)
        item.used_color_attribute.name = 'None'


def update_path(self, context):
    # When the path has been changed, reset the selected sequence to None
    context.scene.my_tool.importer.fileseq = "None"


def callback_fileseq(self, context):
    '''
    Detects all the file sequences in the directory
    '''

    p = context.scene.my_tool.importer.path
    try:
        f = fileseq.findSequencesOnDisk(p)
    except:
        return [("None", "No sequence detected", "")]

    if not f:
        return [("None", "No sequence detected", "")]
    file_seq = []
    if len(f) >= 20:
        file_seq.append(("None", "Please select the pattern", ""))
        file_seq.append(("Manual", "Manual, too much sequence detected, use pattern above", ""))
    else:
        file_seq.append(("None", "Please select the pattern", ""))
        for seq in f:
            file_seq.append((str(seq), seq.basename() + "@" + seq.extension(), ""))
        file_seq.append(("Manual", "Manually set the pattern, use the pattern entered above", ""))
    return file_seq


def update_particle_radius(self, context):
    '''
    This function here updates the radius of selected particle sequence.
    '''
    idx, importer_list_index = get_index(context)
    r = context.scene.my_tool.imported[idx].radius
    importer = importer_list[importer_list_index]
    if not importer.check_valid():
        show_message_box("Sequence has been changed or removed")
        bpy.ops.sequence.remove()
        return
    importer.set_radius(r)


def update_max_value(self, context):
    '''
    When max (or min) value adjusted by user, this function will update it in the importer 
    '''
    idx, importer_list_index = get_index(context)
    max = context.scene.my_tool.imported[idx].max_value
    min = context.scene.my_tool.imported[idx].min_value
    importer = importer_list[importer_list_index]
    if not importer.check_valid():
        show_message_box("Sequence has been changed or removed")
        bpy.ops.sequence.remove()
        return
    if max >= min:
        importer.max_value = max
    else:
        show_message_box("max value shoule be larger than min value", icon="ERROR")


def update_min_value(self, context):
    '''
    When max (or min) value adjusted by user, this function will update it in the importer 
    '''
    idx, importer_list_index = get_index(context)
    max = context.scene.my_tool.imported[idx].max_value
    min = context.scene.my_tool.imported[idx].min_value
    importer = importer_list[importer_list_index]
    if not importer.check_valid():
        show_message_box("Sequence has been changed or removed")
        bpy.ops.sequence.remove()
        return
    if min <= max:
        importer.min_value = min
    else:
        show_message_box("min value shoule be smaller than max value", icon="ERROR")


def update_display(self, context):
    '''
    When particles display method adjusted by user, this function will update it in the importer 
    '''
    idx, importer_list_index = get_index(context)
    method = context.scene.my_tool.imported[idx].display
    importer = importer_list[importer_list_index]
    if not importer.check_valid():
        show_message_box("Sequence has been changed or removed")
        bpy.ops.sequence.remove()
        return
    importer.update_display(method)


def update_imported_num(self, context):
    # Here is when select sequences, then change the corresponding object to active object
    imported_obj_list = context.scene.my_tool.imported
    if bpy.context.active_object:
        if bpy.context.active_object.mode != "OBJECT":
            return
    if imported_obj_list:
        idx = context.scene.my_tool.imported_num
        bpy.ops.object.select_all(action='DESELECT')
        importer = importer_list[imported_obj_list[idx].importer_list_index]
        if importer.check_valid():
            importer.get_obj().select_set(True)
            bpy.context.view_layer.objects.active = importer.get_obj()
        else:
            show_message_box("Sequence has been changed or removed")
            bpy.ops.sequence.remove()


def update_name(self, context):
    # Here is the when update the name of sequence, then update the name of corresponding object
    idx, importer_list_index = get_index(context)
    importer = importer_list[importer_list_index]
    if not importer.check_valid():
        show_message_box("Sequence has been changed or removed")
        bpy.ops.sequence.remove()
        return
    name = context.scene.my_tool.imported[idx].name
    # if name doesn't change
    if importer.get_obj().name == name:
        return
    for obj in bpy.data.objects:
        if name == obj.name:
            show_message_box("Name already exists")
            bpy.ops.ed.undo()
            return
    importer.get_obj().name = name


def update_use_real_value(self, context):
    idx, importer_list_index = get_index(context)
    importer = importer_list[importer_list_index]
    if not importer.check_valid():
        show_message_box("Sequence has been changed or removed")
        bpy.ops.sequence.remove()
        return
    use_real_value = context.scene.my_tool.imported[idx].use_real_value
    context.scene.my_tool.imported[idx].use_clamped_value = not use_real_value
    importer.use_real_value = use_real_value


def update_use_clamped_value(self, context):
    idx, importer_list_index = get_index(context)
    importer = importer_list[importer_list_index]
    if not importer.check_valid():
        show_message_box("Sequence has been changed or removed")
        bpy.ops.sequence.remove()
        return
    if context.scene.my_tool.imported[idx].use_real_value != context.scene.my_tool.imported[idx].use_clamped_value:
        return
    context.scene.my_tool.imported[idx].use_real_value = not context.scene.my_tool.imported[idx].use_real_value


def get_ref_max_value(self):
    idx, importer_list_index = get_index(bpy.context)
    importer = importer_list[importer_list_index]
    return importer.current_max


def get_ref_min_value(self):
    idx, importer_list_index = get_index(bpy.context)
    importer = importer_list[importer_list_index]
    return importer.current_min


def update_script_name(self, context):
    idx, importer_list_index = get_index(bpy.context)
    importer = importer_list[importer_list_index]
    if not importer.check_valid():
        show_message_box("Sequence has been changed or removed")
        bpy.ops.sequence.remove()
        return
    script_name = context.scene.my_tool.imported[idx].script_name
    importer.script_name = script_name
