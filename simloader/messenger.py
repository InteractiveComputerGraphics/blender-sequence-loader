import bpy


def selected_callback():
    if not bpy.context.view_layer.objects.active:
        return
    name = bpy.context.active_object.name
    idx = bpy.data.objects.find(name)
    if idx >= 0:
        bpy.context.scene.SIMLOADER.selected_obj_deselectall_flag = False
        bpy.context.scene.SIMLOADER.selected_obj_num = idx
        bpy.context.scene.SIMLOADER.selected_obj_deselectall_flag = True


def subscribe_to_selected():
    import simloader
    
    # because current implementation may subscribe twice
    # so clear once to avoid duplication
    bpy.msgbus.clear_by_owner(simloader)

    bpy.msgbus.subscribe_rna(
        key=(bpy.types.LayerObjects, 'active'),
        #  don't know why it needs this owner, so I set owner to this module `simloader`
        owner=simloader,
        #  no args
        args=(()),
        notify=selected_callback,
    )


def unsubscribe_to_selected():
    import simloader
    bpy.msgbus.clear_by_owner(simloader)
