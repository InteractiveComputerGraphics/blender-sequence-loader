import bpy
import fileseq
from .utils import *
from .importer_manager import *
import traceback

def callback_color_attribute(self, context):
    attr_items = [('None', 'None', '')]
    mytool = context.scene.my_tool
    item = mytool.imported[mytool.imported_num]
    for i in item.all_attributes:
        attr_items.append((i.name, i.name, ''))
        pass
    return attr_items


def update_color_attribute(self, context):
    mytool = context.scene.my_tool
    idx = mytool.imported_num

    importer = importer_list[idx]
    item = mytool.imported[idx]
    if item.all_attributes_enum != "None":
        importer.set_color_attribute(item.all_attributes_enum)
        item.used_color_attribute.name = item.all_attributes_enum
    else:
        importer.set_color_attribute(None)
        item.used_color_attribute.name = 'None'


def callback_fileseq(self, context):
    p = context.scene.my_tool.importer.path
    f = fileseq.findSequencesOnDisk(p)

    if not f:
        return [("None", "No sequence detected", "")]
    file_seq = []
    if len(f) >= 20:
        file_seq.append(
            ("Manual", "Manual, too much sequence detected, use pattern above", ""))
    else:
        file_seq.append(("Manual", "Manual, use pattern above", ""))
        for seq in f:
            file_seq.append((str(seq), seq.basename()+"@"+seq.extension(), ""))
    return file_seq


#  this function precheck and set the type of this sequence
def update_fileseq(self, context):
    file_seq_items_name = context.scene.my_tool.importer.fileseq
    f = None
    if file_seq_items_name == "Manual":
        try:
            p = context.scene.my_tool.importer.path
            pattern = context.scene.my_tool.importer.pattern
            f = fileseq.findSequenceOnDisk(p + "/" + pattern)
        except:
            show_message_box(
                "can't find this sequence with pattern \"" + pattern+"\"", icon="ERROR")
    else:
        f = fileseq.findSequenceOnDisk(file_seq_items_name)
    if f:
        try:
            context.scene.my_tool.importer.type = check_type(f[0])
        except Exception as e:
            show_message_box("meshio error when reading: " +
                             f[0]+",\n please check console for more details. And please don't load sequence.", icon="ERROR")
            traceback.print_exc()
            return


def update_particle_radius(self, context):
    idx = context.scene.my_tool.imported_num
    r = context.scene.my_tool.imported[idx].radius
    importer = importer_list[idx]
    importer.set_radius(r)


def update_particle_max_value(self, context):
    idx = context.scene.my_tool.imported_num
    max = context.scene.my_tool.imported[idx].max_value
    min = context.scene.my_tool.imported[idx].min_value
    importer = importer_list[idx]
    if max >= min:
        importer.set_max_value(max)
    else:
        show_message_box(
            "max value shoule be larger than min value", icon="ERROR")


def update_particle_min_value(self, context):
    idx = context.scene.my_tool.imported_num
    max = context.scene.my_tool.imported[idx].max_value
    min = context.scene.my_tool.imported[idx].min_value
    importer = importer_list[idx]
    if min <= max:
        importer.set_min_value(min)
    else:
        show_message_box(
            "min value shoule be smaller than max value", icon="ERROR")


def update_display(self, context):
    idx = context.scene.my_tool.imported_num
    method =  context.scene.my_tool.imported[idx].display
    importer = importer_list[idx]
    importer.update_display(method)
    