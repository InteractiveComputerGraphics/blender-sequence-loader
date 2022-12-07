import bpy
import fileseq

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



def refresh_obj(obj, scene):
    fs = obj.BSEQ.pattern
    if obj.BSEQ.use_relative:
        fs = bpy.path.abspath(fs, start=scene.BSEQ.root_path)
    fs = fileseq.findSequenceOnDisk(fs)
    fs = fileseq.findSequenceOnDisk(fs.dirname() + fs.basename() + "@" + fs.extension())
    fs = str(fs)
    if obj.BSEQ.use_relative:
        fs = bpy.path.relpath(fs, start=scene.BSEQ.root_path)
    obj.BSEQ.pattern = fs