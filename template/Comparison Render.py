import bpy

# Utilities for comparison rendering
def toggle_on_single(obj):
    obj.hide_render = False
    if isinstance(obj, bpy.types.Object) and obj.BSEQ.init:
        obj.BSEQ.enabled = True

def toggle_on(objs):
    if type(objs) == list:
        for obj in objs:
            if isinstance(obj, bpy.types.Collection):
                toggle_on_single(obj)
                for child in obj.all_objects:
                    toggle_on_single(child)
            else:
                toggle_on_single(obj)
    else:
        if isinstance(objs, bpy.types.Collection):
            toggle_on_single(objs)
            for child in objs.all_objects:
                toggle_on_single(child)
        else:
            toggle_on_single(objs)

def toggle_off_single(obj):
    obj.hide_render = True
    if isinstance(obj, bpy.types.Object) and obj.BSEQ.init:
        obj.BSEQ.enabled = False

def toggle_off(objs):
    if type(objs) == list:
        for obj in objs:
            toggle_off_single(obj)
            if isinstance(obj, bpy.types.Collection):
                for child in obj.all_objects:
                    toggle_off_single(child)
    else:
        toggle_off_single(objs)
        if isinstance(objs, bpy.types.Collection):
            for child in objs.all_objects:
                toggle_off_single(child)
            
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
comparison_objects = list(bpy.data.collections[comparison_collection].children)
orig_path = bpy.context.scene.render.filepath
for obj in comparison_objects:
    toggle_off(comparison_objects)
    toggle_on(obj)
    bpy.context.scene.render.filepath = f"{orig_path}/{obj.name}/"
#    bpy.ops.render.render(write_still=True)
    bpy.ops.render.render(animation=True)
    
bpy.context.scene.render.filepath = orig_path