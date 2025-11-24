"""
This template script allows you to render each sequence in a specified collection. It toggles the visibility of each sequence one at a time, disabling all others and rendering them individually.

This is mainly useful for creating comparison renders of different sequences in a scene, such as for different models of a physical simulation that were run outside of Blender.

The path is automatically set to `<original_path>/<sequence_name>/` for each render, where `<original_path>` is the original render output path set in the scene settings, and `<sequence_name>` is the name of the sequence being rendered.

Usage:
1. Set the `comparison_collection` variable to the name of the collection containing the sequences you want to render.
2. Run the script in Blender's scripting environment.
"""
import bpy

# Utilities for comparison rendering
def toggle_on_single(obj):
    obj.hide_render = False
    if isinstance(obj, bpy.types.Object) and obj.BSEQ.init:
        obj.BSEQ.enabled = True
        for child in obj.children:
            toggle_on_single(child)
    elif isinstance(obj, bpy.types.Collection):
        for child in obj.objects:
            toggle_on_single(child)
        for child in obj.children:
            toggle_on_single(child)

def toggle_on(objs):
    if type(objs) == list:
        for obj in objs:
            toggle_on_single(obj)
    else:
        toggle_on_single(objs)

def toggle_off_single(obj):
    obj.hide_render = True
    if isinstance(obj, bpy.types.Object) and obj.BSEQ.init:
        obj.BSEQ.enabled = False
        for child in obj.children:
            toggle_off_single(child)
    elif isinstance(obj, bpy.types.Collection):
        for child in obj.objects:
            toggle_off_single(child)
        for child in obj.children:
            toggle_off_single(child)

def toggle_off(objs):
    if type(objs) == list:
        for obj in objs:
            toggle_off_single(obj)
    else:
        toggle_off_single(objs)
            
def toggle_off_all():
    for obj in bpy.data.objects:
        toggle_off_single(obj)    
            
def toggle_on_all():
    for obj in bpy.data.objects:
        toggle_on_single(obj)  

# Declare which collection to render comparison for
# Change this to the name of the collection you want to render
comparison_collection = "Sequences"

# Iterate over children in the collection
comparison_objects = list(bpy.data.collections[comparison_collection].children) + list(bpy.data.collections[comparison_collection].objects)
orig_path = bpy.context.scene.render.filepath
for obj in comparison_objects:
    toggle_off(comparison_objects)
    toggle_on(obj)
    bpy.context.scene.render.filepath = f"{orig_path}/{obj.name}/"
#    bpy.ops.render.render(write_still=True)
    bpy.ops.render.render(animation=True)
    
bpy.context.scene.render.filepath = orig_path