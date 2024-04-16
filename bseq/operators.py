import bpy
from mathutils import Matrix
import fileseq
from .messenger import *
import traceback
from .utils import refresh_obj, show_message_box, get_relative_path
from .importer import create_obj, create_meshio_obj
import numpy as np
import os

addon_name = "blendersequenceloader"

def relative_path_error():
    show_message_box("When using relative path, please save file before using it", icon="ERROR")
    return {"CANCELLED"}

def get_transform_matrix(importer_prop):
    if importer_prop.use_custom_transform:
        return Matrix.LocRotScale(importer_prop.custom_location, importer_prop.custom_rotation, importer_prop.custom_scale)
    else:
        return Matrix.Identity(4)
    
def create_obj_wrapper(seq, importer_prop):
    create_obj(seq, importer_prop.use_relative, importer_prop.root_path, transform_matrix=get_transform_matrix(importer_prop))

# Legacy import operator (this is what the "Import from folder" button does)
class BSEQ_OT_load(bpy.types.Operator):
    '''Load selected sequence'''
    bl_label = "Load Sequence"
    bl_idname = "sequence.load"
    bl_options = {"UNDO"}

    def execute(self, context):
        scene = context.scene
        importer_prop = scene.BSEQ

        if importer_prop.use_relative and not bpy.data.is_saved:
            return relative_path_error()

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

        create_obj_wrapper(fs, importer_prop)
        return {"FINISHED"}


class BSEQ_OT_edit(bpy.types.Operator):
    '''Edit Sequence'''
    bl_label = "Edit the path of the sequence"
    bl_idname = "sequence.edit"
    bl_options = {"UNDO"}

    def execute(self, context):
        scene = context.scene
        importer_prop = scene.BSEQ

        if importer_prop.use_relative and not bpy.data.is_saved:
            #  use relative but file not saved
            return relative_path_error()

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
        if importer_prop.use_relative:
            if importer_prop.root_path != "":
                object.BSEQ.pattern = bpy.path.relpath(str(fileseq), start=importer_prop.root_path)
            else:
                object.BSEQ.pattern = bpy.path.relpath(str(fileseq))

        else:
            obj.BSEQ.pattern = str(fs)
        return {"FINISHED"}


class BSEQ_OT_resetpt(bpy.types.Operator):
    '''This operator resets the geometry nodes of the sequence as a point cloud'''
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
        if bpy.app.version >= (3, 2, 0):
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
    '''This operator resets the geometry nodes of the sequence as a point cloud'''
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
        if bpy.app.version >= (3, 2, 0):
            bpy.ops.node.new_geometry_node_group_assign()
        bpy.ops.object.modifier_move_to_index(modifier=gn.name, index=0)
        return {"FINISHED"}


class BSEQ_OT_resetins(bpy.types.Operator):
    '''This operator resets the geometry nodes of the sequence as a point cloud'''
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
        if bpy.app.version >= (3, 2, 0):
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
    '''Set vertex attribute as vertex split normals'''
    bl_label = "Set as split normal per vertex"
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
    '''Remove vertex attribute as vertex split normals'''
    bl_label = "Remove split normal per vertex"
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
    '''Deactivate selected sequences'''
    bl_label = "Deactivate sequence"
    bl_idname = "bseq.disableselected"
    bl_options = {"UNDO"}

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.BSEQ.init and obj.BSEQ.enabled:
                obj.BSEQ.enabled = False
        return {"FINISHED"}


class BSEQ_OT_enable_selected(bpy.types.Operator):
    '''Activate selected sequences'''
    bl_label = "Activate sequence"
    bl_idname = "bseq.enableselected"
    bl_options = {"UNDO"}

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.BSEQ.init and not obj.BSEQ.enabled:
                obj.BSEQ.enabled = True
        return {"FINISHED"}


class BSEQ_OT_refresh_seq(bpy.types.Operator):
    '''Refresh selected sequences'''
    bl_label = "Refresh sequence"
    bl_idname = "bseq.refresh"

    def execute(self, context):
        scene = context.scene
        obj = bpy.data.objects[scene.BSEQ.selected_obj_num]
        refresh_obj(obj, scene)

        return {"FINISHED"}

class BSEQ_OT_disable_all(bpy.types.Operator):
    '''Deactivate all sequences'''
    bl_label = "Deactivate all sequences"
    bl_idname = "bseq.disableall"
    bl_options = {"UNDO"}

    def execute(self, context):
        for obj in bpy.context.scene.collection.all_objects:
            if obj.BSEQ.init and obj.BSEQ.enabled:
                obj.BSEQ.enabled = False
        return {"FINISHED"}

class BSEQ_OT_enable_all(bpy.types.Operator):
    '''Activate all sequences'''
    bl_label = "Activate all sequences"
    bl_idname = "bseq.enableall"
    bl_options = {"UNDO"}

    def execute(self, context):
        for obj in bpy.context.scene.collection.all_objects:
            if obj.BSEQ.init and not obj.BSEQ.enabled:
                obj.BSEQ.enabled = True
        return {"FINISHED"}

class BSEQ_OT_refresh_sequences(bpy.types.Operator):
    '''Refresh all sequences'''
    bl_label = "Reloads everything in selected folder"
    bl_idname = "bseq.refreshall"
    bl_options = {"UNDO"}

    def execute(self, context):
        scene = context.scene
        # call the update function of path by setting it to its own value
        scene.BSEQ.path = scene.BSEQ.path

        return {"FINISHED"}
    
class BSEQ_OT_set_start_end_frames(bpy.types.Operator):
    '''This operator changes the timeline start and end frames to the length of a specific sequence'''
    bl_label = "Set timeline"
    bl_idname = "bseq.set_start_end_frames"
    bl_options = {"UNDO"}

    def execute(self, context):
        scene = context.scene
        obj = bpy.data.objects[scene.BSEQ.selected_obj_num]
        (start, end) = obj.BSEQ.start_end_frame
        scene.frame_start = 0
        scene.frame_end = end - start

        return {"FINISHED"}

from pathlib import Path
import meshio
from bpy_extras.io_utils import ImportHelper

# This is what the button "Import Sequences" does
class BSEQ_OT_batch_sequences(bpy.types.Operator, ImportHelper):
    """Import one or multiple sequences"""
    bl_idname = "wm.seq_import_batch"
    bl_label = "Import Sequences"
    bl_options = {'PRESET', 'UNDO'}

    def update_filter_glob(self, context):
        bpy.ops.wm.seq_import_batch('INVOKE_DEFAULT')

    filter_string: bpy.props.StringProperty(
        default="*.obj",
        options={'HIDDEN'},
        update=update_filter_glob,
    )

    filename_ext=''
    filter_glob: bpy.props.StringProperty(
        default='*.obj',
        options={'HIDDEN', 'LIBRARY_EDITABLE'},
    )

    files: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    
    def invoke(self, context, event):
        scene = context.scene
        if scene.BSEQ.filter_string:
            self.filter_glob = scene.BSEQ.filter_string
        else:
            self.filter_glob = "*"

        context.window_manager.fileselect_add(self)

        return {'RUNNING_MODAL'}

    def execute(self, context):
        scene = context.scene
        importer_prop = scene.BSEQ

        if importer_prop.use_relative and not bpy.data.is_saved:
            return relative_path_error()

        self.filter_glob = '*'

        folder = Path(self.filepath)
        used_seqs = set()

        for selection in self.files:
            # Check if there exists a matching file sequence for every selection
            fp = str(Path(folder.parent, selection.name))
            seqs = fileseq.findSequencesOnDisk(str(folder.parent))
            matching_seq = [s for s in seqs if fp in list(s) and str(s) not in used_seqs]

            if matching_seq:
                matching_seq = matching_seq[0]
                used_seqs.add(str(matching_seq))

                create_obj_wrapper(matching_seq, importer_prop)
        return {'FINISHED'}

    def draw(self, context):
        pass

class BSEQ_PT_batch_sequences_settings(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Settings Panel"
    bl_options = {'HIDE_HEADER'}
    # bl_parent_id = "FILE_PT_operator" # Optional

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "WM_OT_seq_import_batch"

    def draw(self, context):
        layout = self.layout
        importer_prop = context.scene.BSEQ

        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        # # sfile = context.space_data
        # # operator = sfile.active_operator

        # layout.prop(importer_prop, 'filter_string')

        # layout.alignment = 'LEFT'
        # layout.prop(importer_prop, "relative", text="Relative Path")
        # if importer_prop.use_relative:
        #     layout.prop(importer_prop, "root_path", text="Root Directory")

class BSEQ_addon_preferences(bpy.types.AddonPreferences):
    bl_idname = addon_name

    zips_folder: bpy.props.StringProperty(
            name="Zips Folder",
            subtype='DIR_PATH',
            )

    def draw(self, context):
        # layout = self.layout
        # layout.label(text="Please set a folder to store the extracted zip files")
        # layout.prop(self, "zips_folder", text="Zips Folder")
        pass

zip_folder_name = '/tmp_zips'

class BSEQ_OT_import_zip(bpy.types.Operator, ImportHelper):
    """Import a zip file"""
    bl_idname = "bseq.import_zip"
    bl_label = "Import Zip"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".zip"
    filter_glob: bpy.props.StringProperty(
        default="*.zip",
        options={'HIDDEN', 'LIBRARY_EDITABLE'},
    )

    files: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    
    def execute(self, context):
        importer_prop = context.scene.BSEQ

        import zipfile
        zip_file = zipfile.ZipFile(self.filepath)

        addon_prefs = context.preferences.addons[addon_name].preferences
        # Check if a string is empty:
        if not addon_prefs.zips_folder:
            show_message_box("Please set a folder to store the extracted zip files", icon="ERROR")
            return {"CANCELLED"}
        zips_folder = addon_prefs.zips_folder + zip_folder_name

        valid_files = [info.filename for info in zip_file.infolist() if not info.filename.startswith('__MACOSX/')]
        zip_file.extractall(zips_folder, members=valid_files)
        zip_file.close()    

        folder = str(zips_folder) + '/' + str(Path(self.filepath).name)[:-4]
        print(folder)

        seqs = fileseq.findSequencesOnDisk(str(folder))
        if not seqs:
            show_message_box("No sequences found in the zip file", icon="ERROR")
            return {"CANCELLED"}

        for s in seqs:
            # Import it with absolute paths
            create_obj(s, False, folder, transform_matrix=get_transform_matrix(importer_prop))
        
        # created_folder = context.scene.BSEQ.imported_zips.add()
        # created_folder.path = folder

        return {'FINISHED'}

class BSEQ_OT_delete_zips(bpy.types.Operator):
    """Delete a zip file"""
    bl_idname = "bseq.delete_zips"
    bl_label = "Delete Zip"
    bl_options = {'PRESET', 'UNDO'}

    def execute(self, context):
        # folders = context.scene.BSEQ.imported_zips
        # for folder in folders:

        addon_prefs = context.preferences.addons[addon_name].preferences
        zips_folder = addon_prefs.zips_folder + zip_folder_name

        import shutil
        shutil.rmtree(zips_folder)

        return {'FINISHED'}
    
class BSEQ_OT_load_all(bpy.types.Operator):
    """Load all sequences from selected folder"""
    bl_idname = "bseq.load_all"
    bl_label = "Load All"
    bl_options = {'PRESET', 'UNDO'}

    def execute(self, context):
        importer_prop = context.scene.BSEQ

        if importer_prop.use_relative and not bpy.data.is_saved:
            return relative_path_error()

        dir = importer_prop.path
        seqs = fileseq.findSequencesOnDisk(str(dir))

        for s in seqs:
            print(s)

        for s in seqs:
            create_obj_wrapper(s, importer_prop)
        return {'FINISHED'}

class BSEQ_OT_load_all_recursive(bpy.types.Operator):
    """Load all sequences from selected folder recursively"""
    bl_idname = "bseq.load_all_recursive"
    bl_label = "Load All Recursive"
    bl_options = {'PRESET', 'UNDO'}

    def execute(self, context):
        importer_prop = context.scene.BSEQ

        if importer_prop.use_relative and not bpy.data.is_saved:
            return relative_path_error()

        root_dir = importer_prop.path
        root_coll = bpy.context.scene.collection
        root_layer_collection = bpy.context.view_layer.layer_collection
        unlinked_collections = []
        # Recurse through subdirectories
        for root, dirs, files in os.walk(bpy.path.abspath(root_dir)):
            for dir in sorted(dirs):
                # Process subdirectory
                subdirectory = os.path.join(root, dir)

                seqs = fileseq.findSequencesOnDisk(subdirectory)
                if len(seqs) == 0:
                    continue

                # Get list of directories from the root_dir to the current subdirectory
                coll_list = bpy.path.relpath(subdirectory, start=root_dir).strip("//").split("/")

                # Get or create a nested collection starting from the root
                last_coll = root_coll
                layer_collection = root_layer_collection
                for coll in coll_list:
                    # If it already exists and is not in the children of the last collection, then the prefix has changed
                    cur_coll = bpy.data.collections.get(coll)
                    if cur_coll is not None and last_coll is not None:
                        if cur_coll.name not in last_coll.children:
                            # Get the old parent of the existing collection and move the children to the old parent
                            parent = [c for c in bpy.data.collections if bpy.context.scene.user_of_id(cur_coll) and cur_coll.name in c.children]
                            if len(parent) > 0:
                                for child in cur_coll.children:
                                    parent[0].children.link(child)
                                for obj in cur_coll.objects:
                                    parent[0].objects.link(obj)
                                parent[0].children.unlink(cur_coll)
                                unlinked_collections.append(cur_coll)
                        else:
                            layer_collection = layer_collection.children[cur_coll.name]
                            last_coll = cur_coll


                    # If it was newly created, link it to the last collection
                    if cur_coll is None and last_coll is not None:
                        cur_coll = bpy.data.collections.new(coll)
                        last_coll.children.link(cur_coll)
                        layer_collection = layer_collection.children[cur_coll.name]
                        last_coll = cur_coll

                # Set the last collection as the active collection by recursing through the collections
                context.view_layer.active_layer_collection = layer_collection

                # for s in seqs:
                #     print(s)

                for s in seqs:
                    create_obj_wrapper(s, importer_prop)
            
        # Make sure unused datablocks are freed
        for coll in unlinked_collections:
            bpy.data.collections.remove(coll)
        return {'FINISHED'}
    

class BSEQ_OT_meshio_object(bpy.types.Operator, ImportHelper):
    """Batch Import Meshio Objects"""
    bl_idname = "wm.meshio_import_batch"
    bl_label = "Import Multiple Meshio Objects"
    bl_options = {'PRESET', 'UNDO'}

    files: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
            
    def execute(self, context):
        folder = Path(self.filepath)

        for selection in self.files:
            fp = Path(folder.parent, selection.name)
            create_meshio_obj(str(fp))
        return {'FINISHED'}

def menu_func_import(self, context):
    self.layout.operator(
            BSEQ_OT_meshio_object.bl_idname, 
            text="MeshIO Object")

# Default Keymap Configuration
addon_keymaps = []

def add_keymap():
    wm = bpy.context.window_manager

    # Add new keymap section for BSEQ

    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new("sequence.load", type='F', value='PRESS', shift=True)
        addon_keymaps.append((km, kmi))

        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new("bseq.disableselected", type='D', value='PRESS', shift=True, ctrl=True)
        addon_keymaps.append((km, kmi))

        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new("bseq.enableselected", type='E', value='PRESS', shift=True, ctrl=True)
        addon_keymaps.append((km, kmi))

        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new("bseq.refresh", type='R', value='PRESS', shift=True, ctrl=True)
        addon_keymaps.append((km, kmi))

        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new("bseq.disableall", type='D', value='PRESS', shift=True, alt=True)
        addon_keymaps.append((km, kmi))

        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new("bseq.enableall", type='E', value='PRESS', shift=True, alt=True)
        addon_keymaps.append((km, kmi))

        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new("bseq.refreshall", type='R', value='PRESS', shift=True, alt=True)
        addon_keymaps.append((km, kmi))

        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new("bseq.set_start_end_frames", type='F', value='PRESS', shift=True, ctrl=True)
        addon_keymaps.append((km, kmi))

        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new("wm.seq_import_batch", type='I', value='PRESS', shift=True, ctrl=True)
        addon_keymaps.append((km, kmi))

        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new("wm.meshio_import_batch", type='M', value='PRESS', shift=True, ctrl=True)
        addon_keymaps.append((km, kmi))
        
def delete_keymap():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
