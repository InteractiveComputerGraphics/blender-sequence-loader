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


def clear_screen():
    os.system("cls")


def check_type(fs):
    mesh = meshio.read(fs)
    if mesh.cells[0].type == "vertex":
        return "particle"
    elif mesh.cells[0].type == "triangle":
        return "mesh"
