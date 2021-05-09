import bpy
import meshio
import numpy as np
import importlib
import particle_importer
import fileseq

importlib.reload(particle_importer)
from particle_importer import particle_importer


def update_path(self, context):
    p = context.scene.my_tool.path
    f = fileseq.findSequencesOnDisk(p)
    if not f:
        print("animation sequences not detected")
        return
    if len(f) != 1:
        print(
            "multiple animation sequences detected, currently unsupport yet, only use the first sequence for now"
        )
        print(
            "or it could be unsupported filename format, fileseq use format like ' nama + number + extenion', e.g. ' a1.vtk, a2.vtk, ... a10.vtk '"
        )
    context.scene.my_tool.name = f[0].basename()
    context.scene.my_tool.start = f[0].start()
    context.scene.my_tool.end = f[0].end()
    context.scene.my_tool.extension = f[0].extension()


importer = None


def call_back(self, context):
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


class MyProperties(bpy.types.PropertyGroup):

    path: bpy.props.StringProperty(
        name="Path",
        default="C:\\Users\\hui\\Desktop\\output\\DamBreakModel\\vtk\\",
        subtype="DIR_PATH",
        update=update_path,
    )
    name: bpy.props.StringProperty(name="Name")
    extension: bpy.props.StringProperty(name="Extension")
    start: bpy.props.IntProperty(name="start", default=0)
    end: bpy.props.IntProperty(name="end", default=0)
    type: bpy.props.EnumProperty(
        name="Type",
        description="choose particles or mesh",
        items=[("mesh", "Add Mesh", ""), ("particle", "Add Particles", "")],
    )
    render: bpy.props.EnumProperty(
        name="render",
        description="choose attributes used for rendering",
        items=call_back,
        update=set_color_fields,
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
        layout.prop(mytool, "name")
        layout.prop(mytool, "start")
        layout.prop(mytool, "end")
        layout.prop(mytool, "extension")
        layout.prop(mytool, "type")

        layout.operator("meshio_loader.load")
        layout.prop(mytool, "render")
        layout.operator("meshio_loader.render")



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

        if mytool.type == "type1":
            #  For now only used to test how it works
            pass
        return {"FINISHED"}


class meshio_loader_OT_render(bpy.types.Operator):
    bl_label = "Render Sequences"
    bl_idname = "meshio_loader.render"

    def execute(self, context):
        return {"FINISHED"}


classes = [
    MyProperties,
    MESHIO_IMPORT_PT_main_panel,
    meshio_loader_OT_load,
    meshio_loader_OT_render,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

        bpy.types.Scene.my_tool = bpy.props.PointerProperty(type=MyProperties)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.my_tool


if __name__ == "__main__":
    register()
    # unregister()
