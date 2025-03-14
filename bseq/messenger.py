import bpy


def selected_callback():

    # seems like that this is not necessary
    # if not bpy.context.view_layer.objects.active:
    #     return
    
    if not bpy.context.active_object:
        return
    
    name = bpy.context.active_object.name
    idx = bpy.data.objects.find(name)
    if idx >= 0:
        bpy.context.scene.BSEQ.selected_obj_deselectall_flag = False
        bpy.context.scene.BSEQ.selected_obj_num = idx
        bpy.context.scene.BSEQ.selected_obj_deselectall_flag = True
    if bpy.context.active_object.BSEQ.init:
        bpy.context.scene.BSEQ.edit_obj = bpy.context.active_object

def subscribe_to_selected():
    # import bseq
    bseq = __loader__
    
    # because current implementation may subscribe twice
    # so clear once to avoid duplication
    bpy.msgbus.clear_by_owner(bseq)

    bpy.msgbus.subscribe_rna(
        key=(bpy.types.LayerObjects, 'active'),
        #  don't know why it needs this owner, so I set owner to this module `bseq`
        owner=bseq,
        #  no args
        args=(()),
        notify=selected_callback,
    )


def unsubscribe_to_selected():
    # import bseq
    bseq = __loader__
    bpy.msgbus.clear_by_owner(bseq)
