import bpy
import fileseq
from .messenger import *
import traceback
from .utils import show_message_box
from .importer import create_obj
import numpy as np


#  Here are load and delete operations
class BSEQ_OT_load(bpy.types.Operator):
    '''This operator loads a sequnce'''
    bl_label = "Load Sequence"
    bl_idname = "sequence.load"
    bl_options = {"UNDO"}

    def execute(self, context):
        scene = context.scene
        importer_prop = scene.BSEQ

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

        try:
            fs = fileseq.findSequenceOnDisk(fs)
        except Exception as e:
            show_message_box(traceback.format_exc(), "Can't find sequence: " + str(fs), "ERROR")
            return {"CANCELLED"}

        create_obj(fs, importer_prop.relative)
        return {"FINISHED"}


class BSEQ_OT_edit(bpy.types.Operator):
    '''This operator changes a sequnce'''
    bl_label = "Edit Sequences Path"
    bl_idname = "sequence.edit"
    bl_options = {"UNDO"}

    def execute(self, context):
        scene = context.scene
        importer_prop = scene.BSEQ

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

        try:
            fs = fileseq.findSequenceOnDisk(fs)
        except Exception as e:
            show_message_box(traceback.format_exc(), "Can't find sequence: " + str(fs), "ERROR")
            return {"CANCELLED"}

        sim_loader = context.scene.BSEQ

        # logic here
        #  it seems quite simple task, no need to create a function(for now)
        obj = sim_loader.edit_obj
        if not obj:
            return {"CANCELLED"}
        if importer_prop.relative:
            obj.BSEQ.pattern = bpy.path.relpath(str(fs))
        else:
            obj.BSEQ.pattern = str(fs)
        obj.BSEQ.use_relative = importer_prop.relative
        return {"FINISHED"}


class BSEQ_OT_resetpt(bpy.types.Operator):
    '''This operator reset the geometry nodes of the sequence as a point cloud'''
    bl_label = "Reset Geometry Nodes as Point Cloud"
    bl_idname = "bseq.resetpt"
    bl_options = {"UNDO"}

    def execute(self, context):
        sim_loader = context.scene.BSEQ
        obj = bpy.data.objects[sim_loader.selected_obj_num]
        warn = False
        for modifier in obj.modifiers:
            if modifier.type == "NODES":
                warn = True
                obj.modifiers.remove(modifier)
        if warn:
            show_message_box("Exising geoemtry nodes of {} has been removed".format(obj.name), "Warning")
        gn = obj.modifiers.new("BSEQ_GeometryNodse", "NODES")
        # change starting from blender 3.2
        # https://developer.blender.org/rB08b4b657b64f
        if bpy.app.version >= (3,2,0):
            bpy.ops.node.new_geometry_node_group_assign()
        gn.node_group.nodes.new('GeometryNodeMeshToPoints')
        set_material = gn.node_group.nodes.new('GeometryNodeSetMaterial')
        set_material.inputs[2].default_value = context.scene.BSEQ.material

        node0 = gn.node_group.nodes[0]
        node1 = gn.node_group.nodes[1]
        node2 = gn.node_group.nodes[2]
        gn.node_group.links.new(node0.outputs[0], node2.inputs[0])
        gn.node_group.links.new(node2.outputs[0], set_material.inputs[0])
        gn.node_group.links.new(set_material.outputs[0], node1.inputs[0])
        bpy.ops.object.modifier_move_to_index(modifier=gn.name, index=0)
        return {"FINISHED"}


class BSEQ_OT_resetmesh(bpy.types.Operator):
    '''This operator reset the geometry nodes of the sequence as a point cloud'''
    bl_label = "Reset Geometry Nodes as Mesh"
    bl_idname = "bseq.resetmesh"
    bl_options = {"UNDO"}

    def execute(self, context):
        sim_loader = context.scene.BSEQ
        obj = bpy.data.objects[sim_loader.selected_obj_num]
        warn = False
        for modifier in obj.modifiers:
            if modifier.type == "NODES":
                warn = True
                obj.modifiers.remove(modifier)
        if warn:
            show_message_box("Exising geoemtry nodes of {} has been removed".format(obj.name), "Warning")
        gn = obj.modifiers.new("BSEQ_GeometryNodse", "NODES")
        # change starting from blender 3.2
        # https://developer.blender.org/rB08b4b657b64f
        if bpy.app.version >= (3,2,0):
            bpy.ops.node.new_geometry_node_group_assign()
        bpy.ops.object.modifier_move_to_index(modifier=gn.name, index=0)
        return {"FINISHED"}


class BSEQ_OT_resetins(bpy.types.Operator):
    '''This operator reset the geometry nodes of the sequence as a point cloud'''
    bl_label = "Reset Geometry Nodes as Instances"
    bl_idname = "bseq.resetins"
    bl_options = {"UNDO"}

    def execute(self, context):
        sim_loader = context.scene.BSEQ
        obj = bpy.data.objects[sim_loader.selected_obj_num]
        warn = False
        for modifier in obj.modifiers:
            if modifier.type == "NODES":
                warn = True
                obj.modifiers.remove(modifier)
        if warn:
            show_message_box("Exising geoemtry nodes of {} has been removed".format(obj.name), "Warning")
        gn = obj.modifiers.new("BSEQ_GeometryNodse", "NODES")
        # change starting from blender 3.2
        # https://developer.blender.org/rB08b4b657b64f
        if bpy.app.version >= (3,2,0):
            bpy.ops.node.new_geometry_node_group_assign()
        nodes = gn.node_group.nodes
        links = gn.node_group.links
        input_node = nodes[0]
        output_node = nodes[1]

        instance_on_points = nodes.new('GeometryNodeInstanceOnPoints')
        cube = nodes.new('GeometryNodeMeshCube')
        realize_instance = nodes.new('GeometryNodeRealizeInstances')
        set_material = nodes.new('GeometryNodeSetMaterial')

        instance_on_points.inputs['Scale'].default_value = [
            0.05,
            0.05,
            0.05,
        ]
        set_material.inputs[2].default_value = context.scene.BSEQ.material

        links.new(input_node.outputs[0], instance_on_points.inputs['Points'])
        links.new(cube.outputs[0], instance_on_points.inputs['Instance'])
        links.new(instance_on_points.outputs[0], realize_instance.inputs[0])
        links.new(realize_instance.outputs[0], set_material.inputs[0])
        links.new(set_material.outputs[0], output_node.inputs[0])

        bpy.ops.object.modifier_move_to_index(modifier=gn.name, index=0)
        return {"FINISHED"}


class BSEQ_OT_set_as_split_norm(bpy.types.Operator):
    '''This operator set the vertex attribute as vertex split normals'''
    bl_label = "Set as split normal per Vertex"
    bl_idname = "bseq.setsplitnorm"
    bl_options = {"UNDO"}

    def execute(self, context):
        sim_loader = context.scene.BSEQ
        obj = bpy.data.objects[sim_loader.selected_obj_num]
        mesh = obj.data
        attr_index = sim_loader.selected_attribute_num
        if attr_index >= len(mesh.attributes):
            show_message_box("Please select the attribute")
            return {"CANCELLED"}
        mesh.BSEQ.split_norm_att_name = mesh.attributes[attr_index].name

        return {"FINISHED"}


class BSEQ_OT_remove_split_norm(bpy.types.Operator):
    '''This operator remove the vertex attribute as vertex split normals'''
    bl_label = "Remove split normal per Vertex"
    bl_idname = "bseq.removesplitnorm"
    bl_options = {"UNDO"}

    def execute(self, context):
        sim_loader = context.scene.BSEQ
        obj = bpy.data.objects[sim_loader.selected_obj_num]
        mesh = obj.data
        if mesh.BSEQ.split_norm_att_name:
            mesh.BSEQ.split_norm_att_name = ""

        return {"FINISHED"}


class BSEQ_OT_disable_selected(bpy.types.Operator):
    '''This operator disable all selected sequence'''
    bl_label = "Disable Selected Sequence"
    bl_idname = "bseq.disableselected"
    bl_options = {"UNDO"}

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.BSEQ.init and obj.BSEQ.enabled:
                obj.BSEQ.enabled = False
        return {"FINISHED"}


class BSEQ_OT_enable_selected(bpy.types.Operator):
    '''This operator enable all selected sequence'''
    bl_label = "Enable Selected Sequence"
    bl_idname = "bseq.enableselected"
    bl_options = {"UNDO"}

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.BSEQ.init and not obj.BSEQ.enabled:
                obj.BSEQ.enabled = True
        return {"FINISHED"}


class BSEQ_OT_refresh_seq(bpy.types.Operator):
    '''This operator refresh the sequence'''
    bl_label = "Refresh Sequence"
    bl_idname = "bseq.refresh"

    def execute(self, context):
        scene = context.scene
        obj = bpy.data.objects[scene.BSEQ.selected_obj_num]

        fs = obj.BSEQ.pattern
        if obj.BSEQ.use_relative:
            fs = bpy.path.abspath(fs)
        fs = fileseq.findSequenceOnDisk(fs)
        fs = fileseq.findSequenceOnDisk(fs.dirname() + fs.basename() + "@" + fs.extension())
        fs = str(fs)
        if obj.BSEQ.use_relative:
            fs = bpy.path.relpath(fs)
        obj.BSEQ.pattern = fs

        return {"FINISHED"}
