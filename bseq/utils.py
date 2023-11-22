import bpy
import fileseq
import os

def show_message_box(message="", title="Message Box", icon="INFO"):
    '''
    It shows a small window to display the error message and also print it the console
    '''

    def draw(self, context):
        lines = message.splitlines()
        for line in lines:
            self.layout.label(text=line)

    print("Information: ", title)
    print(message)
    print('End of bseq message box')
    print()
    stop_animation()
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


def stop_animation():
    if bpy.context.screen.is_animation_playing:
        #  if playing animation, then stop it, otherwise it will keep showing message box
        bpy.ops.screen.animation_cancel()

def get_relative_path(path, root_path):
    if root_path != "":
        path = bpy.path.relpath(path, start=root_path)
    else:
        path = bpy.path.relpath(path)    
    return path

# convert relative path to absolute path
def convert_to_absolute_path(path, root_path):
    if root_path != "":
        path = bpy.path.abspath(path, start=root_path)
    else:
        path = bpy.path.abspath(path)    
    return path

def get_absolute_path(obj, scene):
    full_path = os.path.join(bpy.path.native_pathsep(obj.BSEQ.path), obj.BSEQ.pattern)
    full_path = convert_to_absolute_path(full_path, scene.BSEQ.root_path)
    return full_path


def refresh_obj(obj, scene):
    is_relative = obj.BSEQ.path.startswith("//")
    print("is_relative: ", is_relative)
    fs = get_absolute_path(obj, scene)
    fs = fileseq.findSequenceOnDisk(fs)
    fs = fileseq.findSequenceOnDisk(fs.dirname() + fs.basename() + "@" + fs.extension())
    obj.BSEQ.start_end_frame = (fs.start(), fs.end())
    fs = str(fs)
    if is_relative:
        fs = get_relative_path(fs, scene.BSEQ.root_path)
    obj.BSEQ.path = os.path.dirname(fs)
    obj.BSEQ.pattern = os.path.basename(fs)
