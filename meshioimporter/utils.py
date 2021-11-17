import bpy
import os
import meshio


def show_message_box(message="", title="Message Box", icon="INFO"):
    '''
    It shows a small window to display the error message and also print it the console
    '''

    def draw(self, context):
        self.layout.label(text=message)

    print(message)
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)

def check_type(fs):
    '''
    It checkes the type of the file, it could be either a triangle mesh or particles.
    
    Can be extended to other cases.
    '''
    mesh = meshio.read(fs)
    if mesh.cells[0].type == "vertex":
        return "particle"
    elif mesh.cells[0].type == "triangle":
        return "mesh"

# list is the iteratible things, like bpy.data.objects, or bpy.data.meshes
def find_next_name(old_name,list):
    i=1
    while old_name+str(i) in list:
        i+=1
    return old_name+str(i)