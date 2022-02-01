import bpy
import fileseq
from .importer_manager import *
import traceback
from .utils import show_message_box
from .importer import create_obj


#  Here are load and delete operations
class SIMLOADER_OT_load(bpy.types.Operator):
    '''
    This operator loads a sequnce
    '''
    bl_label = "Load Sequences"
    bl_idname = "sequence.load"
    bl_options = {"UNDO"}

    def execute(self, context):
        scene = context.scene
        importer_prop = scene.SIMLOADER

        if importer_prop.relative and not bpy.data.is_saved:
            #  use relative but file not saved
            show_message_box("When using relative path, please save file before using it", icon="ERROR")
            return {"CANCELLED"}

        fs = importer_prop.fileseq
        use_pattern = importer_prop.use_pattern

        if not use_pattern and (not fs or fs == "None"):
            # fs is none
            return {'CANCELLED'}
        if use_pattern:
            if not importer_prop.pattern:
                show_message_box("Pattern is empty", icon="ERROR")
                return {"CANCELLED"}
            fs = importer_prop.path + '/' + importer_prop.pattern

        #  pattern means the name of directory
        #  fs means fileseq object
        pattern = fs
        if importer_prop.relative:
            pattern = bpy.path.relpath(fs)

        try:
            fs = fileseq.findSequenceOnDisk(fs)
        except Exception as e:
            show_message_box(traceback.format_exc(), "Can't find sequence: " + str(fs), "ERROR")
            return {"CANCELLED"}

        create_obj(fs, pattern, importer_prop.relative)
        return {"FINISHED"}


class SIMLOADER_OT_edit(bpy.types.Operator):
    '''
    This operator changes a sequnce
    '''
    bl_label = "Edit Sequences Path"
    bl_idname = "sequence.edit"
    bl_options = {"UNDO"}

    def execute(self, context):
        scene = context.scene
        importer_prop = scene.SIMLOADER

        if importer_prop.relative and not bpy.data.is_saved:
            #  use relative but file not saved
            show_message_box("When using relative path, please save file before using it", icon="ERROR")
            return {"CANCELLED"}

        fs = importer_prop.fileseq
        use_pattern = importer_prop.use_pattern

        if not use_pattern and (not fs or fs == "None"):
            # fs is none
            return {'CANCELLED'}
        if use_pattern:
            if not importer_prop.pattern:
                show_message_box("Pattern is empty", icon="ERROR")
                return {"CANCELLED"}
            fs = importer_prop.path + '/' + importer_prop.pattern

        #  pattern means the name of directory
        #  fs means fileseq object
        pattern = fs
        if importer_prop.relative:
            pattern = bpy.path.relpath(fs)

        try:
            fs = fileseq.findSequenceOnDisk(fs)
        except Exception as e:
            show_message_box(traceback.format_exc(), "Can't find sequence: " + str(fs), "ERROR")
            return {"CANCELLED"}

        collection = bpy.data.collections['SIMLOADER'].objects
        sim_loader = context.scene.SIMLOADER
        #  it seems quite simple task, no need to create a function(for now)
        if len(collection) > 0 and sim_loader.selected_obj_num < len(collection):
            obj = collection[sim_loader.selected_obj_num]
            obj.SIMLOADER.pattern = pattern
            obj.SIMLOADER.use_relative = importer_prop.relative
            return {"FINISHED"}
        return {"CANCELLED"}


class SIMLOADER_OT_resetpt(bpy.types.Operator):
    '''
    This operator reset the geometry nodes of the sequence as a point cloud
    '''
    bl_label = "Reset Geometry Nodes as Point Cloud"
    bl_idname = "simloader.resetpt"
    bl_options = {"UNDO"}

    def execute(self, context):
        sim_loader = context.scene.SIMLOADER
        obj = bpy.data.objects[sim_loader.selected_obj_num]
        for modifier in obj.modifiers:
            if modifier.type == "NODES":
                obj.modifiers.remove(modifier)
        gn = obj.modifiers.new("SIMLOADER_GeometryNodse", "NODES")
        gn.node_group.nodes.new('GeometryNodeMeshToPoints')
        node0 = gn.node_group.nodes[0]
        node1 = gn.node_group.nodes[1]
        node2 = gn.node_group.nodes[2]
        gn.node_group.links.new(node0.outputs[0], node2.inputs[0])
        gn.node_group.links.new(node2.outputs[0], node1.inputs[0])
        bpy.ops.object.modifier_move_to_index(modifier=gn.name, index=0)
        return {"FINISHED"}


class SIMLOADER_OT_resetmesh(bpy.types.Operator):
    '''
    This operator reset the geometry nodes of the sequence as a point cloud
    '''
    bl_label = "Reset Geometry Nodes as Mesh"
    bl_idname = "simloader.resetmesh"
    bl_options = {"UNDO"}

    def execute(self, context):
        sim_loader = context.scene.SIMLOADER
        obj = bpy.data.objects[sim_loader.selected_obj_num]
        for modifier in obj.modifiers:
            if modifier.type == "NODES":
                obj.modifiers.remove(modifier)
        gn = obj.modifiers.new("SIMLOADER_GeometryNodse", "NODES")
        bpy.ops.object.modifier_move_to_index(modifier=gn.name, index=0)
        return {"FINISHED"}


class SIMLOADER_OT_resetins(bpy.types.Operator):
    '''
    This operator reset the geometry nodes of the sequence as a point cloud
    '''
    bl_label = "Reset Geometry Nodes as Instances"
    bl_idname = "simloader.resetins"
    bl_options = {"UNDO"}

    def execute(self, context):
        sim_loader = context.scene.SIMLOADER
        obj = bpy.data.objects[sim_loader.selected_obj_num]
        for modifier in obj.modifiers:
            if modifier.type == "NODES":
                obj.modifiers.remove(modifier)
        gn = obj.modifiers.new("SIMLOADER_GeometryNodse", "NODES")
        nodes = gn.node_group.nodes
        links = gn.node_group.links
        input_node  = nodes[0]
        output_node  = nodes[1]

        instance_on_points = nodes.new('GeometryNodeInstanceOnPoints')
        cube = nodes.new('GeometryNodeMeshCube')
        realize_instance = nodes.new('GeometryNodeRealizeInstances')
        set_material = nodes.new('GeometryNodeSetMaterial')

        instance_on_points.inputs['Scale'].default_value = [0.05,0.05,0.05,]
        # set_material.inputs['2'].default_value = 


        links.new(input_node.outputs[0],instance_on_points.inputs['Points'])
        links.new(cube.outputs[0],instance_on_points.inputs['Instance'])
        links.new(instance_on_points.outputs[0],realize_instance.inputs[0])
        links.new(realize_instance.outputs[0],set_material.inputs[0])
        links.new(set_material.outputs[0],output_node.inputs[0])

        bpy.ops.object.modifier_move_to_index(modifier=gn.name, index=0)
        return {"FINISHED"}
