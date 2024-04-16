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