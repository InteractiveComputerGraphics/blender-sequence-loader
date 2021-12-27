import bpy
import os
import meshio


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
    print()
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


def pre_check(fs):
    '''
    Do some pre-checking of animation sequences, while clicking on the 'load sequence' button
    '''
    mesh = meshio.read(fs)
    color_attributes = mesh.point_data.keys()
    if mesh.cells[0].type == "vertex":
        return "particle", color_attributes
    elif mesh.cells[0].type == "triangle":
        return "mesh", color_attributes
    elif mesh.cells[0].type == "quad":
        return "mesh", color_attributes


def find_next_name(old_name, list):
    '''
    Find the next name in the given list, e.g. bpy.data.objects, bpy.data.meshes and so on
    '''
    i = 1
    while old_name+str(i) in list:
        i += 1
    return old_name+str(i)
