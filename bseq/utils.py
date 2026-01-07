import bpy
import fileseq
import os
import meshio
import traceback

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
        rel_path = bpy.path.relpath(path, start=bpy.path.abspath(root_path))
    else:
        rel_path = bpy.path.relpath(path)    
    return rel_path

# convert relative path to absolute path
def convert_to_absolute_path(path, root_path):
    # Additional call to os.path.abspath removes any "/../"" in the path (can be a problem on Windows)
    if root_path != "":
        path = os.path.abspath(bpy.path.abspath(path, start=bpy.path.abspath(root_path)))
    else:
        path = os.path.abspath(bpy.path.abspath(path))
    return path

def get_absolute_path(obj, scene):
    full_path = os.path.join(bpy.path.native_pathsep(obj.BSEQ.path), obj.BSEQ.pattern)
    full_path = convert_to_absolute_path(full_path, scene.BSEQ.root_path)
    return full_path

def refresh_obj(obj, scene):
    is_relative = obj.BSEQ.path.startswith("//")
    fs = get_absolute_path(obj, scene)
    fs = fileseq.findSequenceOnDisk(fs)
    #fs = fileseq.findSequenceOnDisk(fs.dirname() + fs.basename() + "@" + fs.extension())

    full_path = str(fs)
    path = os.path.dirname(full_path)
    pattern = os.path.basename(full_path)
    if is_relative:
        path = get_relative_path(path, scene.BSEQ.root_path)

    obj.BSEQ.path = path
    obj.BSEQ.pattern = pattern
    obj.BSEQ.start_end_frame = (fs.start(), fs.end())

def load_meshio_from_path(fileseq, filepath, obj = None):
    try:
        meshio_mesh = meshio.read(filepath)
        if obj is not None:
            try:
                obj.BSEQ.current_file = filepath
            except AttributeError:
                pass
    except Exception as e:
        show_message_box("Error when reading: " + filepath + ",\n" + traceback.format_exc(),
                        "Meshio Loading Error" + str(e),
                        icon="ERROR")
        meshio_mesh = meshio.Mesh([], [])
    return meshio_mesh

