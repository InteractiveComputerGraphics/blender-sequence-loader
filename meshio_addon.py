import bpy
import meshio
import numpy as np
import importlib
import particle_importer
import fileseq

importlib.reload(particle_importer)
from particle_importer import particle_importer


#  some static variables, need to be used in different part of this addon
importer = None
file_seq_items = []
file_seq = []


def ShowMessageBox(message="", title="Message Box", icon="INFO"):
    def draw(self, context):
        self.layout.label(text=message)

    print(message)
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


def update_path(self, context):
    global file_seq_items
    global file_seq
    file_seq_items = [("Manual", "Manual, use pattern above", "")]
    p = context.scene.my_tool.path
    f = fileseq.findSequencesOnDisk(p)
    if not f:
        ShowMessageBox("animation sequences not detected", icon="ERROR")
        print("animation sequences not detected")
        return
    if len(f) >= 20:
        message = "There is something wrong in this folder, too many file sequences detected.\n\
        The problem could be the pattern is not recognized correctly, please sepcify the pattern manually."
        ShowMessageBox("message", icon="ERROR")
        print(message)
        return
    for seq in f:
        file_seq_items.append((seq.basename(), seq.basename(), ""))
        file_seq.append(seq)


def render_attribute_callback(self, context):
    attr_items = [("None", "None", "")]
    if importer and importer.get_render_attribute():
        attrs = importer.get_render_attribute()
        for a in attrs:
            attr_items.append((a, a, ""))
    return attr_items


def set_color_fields(self, context):
    scene = context.scene
    mytool = scene.my_tool
    if mytool.render != "None":
        importer.set_render_attribute(mytool.render)
    else:
        importer.set_render_attribute(None)


def file_seq_callback(self, context):
    return file_seq_items


def file_seq_update(self, context):
    file_seq_items_name = context.scene.my_tool.fileseq
    ind = 0
    p = context.scene.my_tool.path
    global file_seq

    f = None
    if file_seq_items_name == "Manual":
        try:
            pattern = context.scene.my_tool.pattern
            f = fileseq.findSequenceOnDisk(p + "\\" + pattern)
        except:
            ShowMessageBox("can't find this sequence: " + pattern, icon="ERROR")
    else:
        for i, files in enumerate(file_seq):
            if file_seq_items_name == files.basename():
                f = files
                break

    if f:
        name = f.basename()
        start = f.start()
        end = f.end()
        extension = f.extension()

        #  pre-check the content of file content
        try:
            mesh = meshio.read(p + name + str(start) + extension)
            if len(mesh.cells) > 1:
                print("unsupport multi-cell files")
                return

            context.scene.my_tool.name = f.basename()
            context.scene.my_tool.start = f.start()
            context.scene.my_tool.end = f.end()
            context.scene.my_tool.extension = f.extension()
            if mesh.cells[0].type == "vertex":
                context.scene.my_tool.type = "particle"
            else:
                print("todo: it should be triangle mesh here")
                context.scene.my_tool.type = "mesh"
        except:
            print("can't find mesh info from the file: ")
            print(p + name + str(start) + extension)
    return


class MyProperties(bpy.types.PropertyGroup):

    path: bpy.props.StringProperty(
        name="Path",
        default="C:\\Users\\hui\\Desktop\\output\\DamBreakModel\\vtk\\",
        subtype="DIR_PATH",
        update=update_path,
    )
    fileseq: bpy.props.EnumProperty(
        name="File Sequences",
        description="Please choose the file sequences you want",
        items=file_seq_callback,
        update=file_seq_update,
    )
    pattern: bpy.props.StringProperty(name="Pattern")
    name: bpy.props.StringProperty(name="Name")
    extension: bpy.props.StringProperty(name="Extension")
    start: bpy.props.IntProperty(name="start", default=0)
    end: bpy.props.IntProperty(name="end", default=0)
    type: bpy.props.EnumProperty(
        name="Type",
        description="choose particles or mesh",
        items=[("mesh", "Add Mesh", ""), ("particle", "Add Particles", "")],
    )
    # used_type: bpy.props.IntProperty(name="used_type",min=0,max=3,default=0)
    render: bpy.props.EnumProperty(
        name="Color Field",
        description="choose attributes used for rendering",
        items=render_attribute_callback,
        update=set_color_fields,
    )

    min_value:bpy.props.FloatProperty(
        name= "Min",
        description = "min value of this property"
    )
    max_value:bpy.props.FloatProperty(
        name= "Max",
        description = "max value of this property"
    )



class MESHIO_IMPORT_PT_main_panel(bpy.types.Panel):
    bl_label = "Import Panel"
    bl_idname = "MESHIO_IMPORT_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "New Tab"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool

        layout.prop(mytool, "path")
        layout.prop(mytool, "pattern")
        layout.prop(mytool, "fileseq")


        layout.prop(mytool, "start")
        layout.prop(mytool, "end")
        layout.prop(mytool, "type")

        layout.operator("meshio_loader.load")
       
        # layout.operator("meshio_loader.render")

class PARTICLE_PT_panel(bpy.types.Panel):
    bl_label = "Particles Settings"
    bl_idname = "PARTICLE_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "New Tab"
    bl_parent_id = "MESHIO_IMPORT_PT_panel"

    def draw(self, context):
        t=context.scene.my_tool.type
        if t!="particle":
            return
        else:
            scene = context.scene
            mytool = scene.my_tool
            layout = self.layout
            layout.prop(mytool, "render")
            layout.prop(mytool, "min_value")
            layout.prop(mytool, "max_value")
            layout.operator("particle.clear")
            


class MESH_PT_panel(bpy.types.Panel):
    bl_label = "Mesh Settings"
    bl_idname = "MESH_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "New Tab"
    bl_parent_id = "MESHIO_IMPORT_PT_panel"

    def draw(self, context):
        t=context.scene.my_tool.type
        if t!="Mesh":
            pass
        else:
            print("todo: mesh settins")
            pass


def update_min_max(self, context):
    global importer
    if not importer:
        return
    min_v,  max_v =importer.get_minmax()
    context.scene.my_tool.min_value=min_v
    context.scene.my_tool.max_value=max_v
    


class particle_OT_clear(bpy.types.Operator):
    bl_label = "Remove Sequence"
    bl_idname = "particle.clear"
    def execute(self, context):
        global importer
        if importer:
            importer.clear()
        if len(bpy.app.handlers.frame_change_post)==2:
            bpy.app.handlers.frame_change_post.clear()
        else:
            print("something wrong, it should contain only 2 object in frame change handler.")
        return {"FINISHED"}






class meshio_loader_OT_load(bpy.types.Operator):
    bl_label = "Load Sequences"
    bl_idname = "meshio_loader.load"

    def execute(self, context):
        global count
        global importer
        scene = context.scene
        mytool = scene.my_tool

        path = mytool.path
        name = mytool.name
        extension = mytool.extension
        begin = mytool.start
        end = mytool.end

        if mytool.type == "particle":
            if not importer:
                importer = None
            importer = particle_importer(path, name, begin, end, extension)
            bpy.app.handlers.frame_change_post.append(importer)
            bpy.app.handlers.frame_change_post.append(update_min_max)

        if mytool.type == "type1":
            #  For now only used to test how it works
            pass
        return {"FINISHED"}



classes = [
    MyProperties,
    MESHIO_IMPORT_PT_main_panel,
    meshio_loader_OT_load,
    PARTICLE_PT_panel,
    MESH_PT_panel,
    particle_OT_clear,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.my_tool = bpy.props.PointerProperty(type=MyProperties)
    # bpy.types.Scene.importer = None


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.my_tool
    # del bpy.types.Scene.importer


if __name__ == "__main__":
    register()
    # unregister()
