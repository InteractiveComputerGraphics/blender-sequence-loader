import meshio
import numpy as np
import bpy
import bmesh

class mesh_importer:
    def __init__(self, path,name, start_file_num,end_file_num,extension):
        self.path = path
        self.name = name
        
        self.start_file_num=start_file_num
        self.end_file_num = end_file_num
        self.extension = extension
        self.init_mesh()


    def create_face_data(self,meshio_cells):
#    todo: support other mesh structure, such as tetrahedron
        return meshio_cells[0][1]


    def load_mesh(self,total_path):

        try:
            meshio_mesh=meshio.read(total_path)
        except:
            print("file is missing : ",total_path)
            return 
        
        
        mesh_vertices=meshio_mesh.points
        vertices_count=len(meshio_mesh.points)
        mesh_faces=self.create_face_data(meshio_mesh.cells)

        blender_mesh=None
        if name in bpy.data.meshes:
            blender_mesh=bpy.data.meshes[name]
            
    #        remove all the vertices from the mesh
            bm=bmesh.new()
            bm.from_mesh(blender_mesh)
            bm.clear()    
            bm.to_mesh(blender_mesh)
            bm.free()


        else:
            blender_mesh=bpy.data.meshes.new(name=name)
            
            new_object = bpy.data.objects.new("new_object", blender_mesh)
            bpy.data.collections[0].objects.link(new_object)



        blender_mesh.vertices.add(vertices_count)
    #     todo: using foreachset 
        pos=meshio_mesh.points @ np.array([[1,0,0],[0,0,1],[0,1,0]])
        blender_mesh.vertices.foreach_set("co",pos.ravel())
            
    #   code from ply impoter of blender, https://github.com/blender/blender-addons/blob/master/io_mesh_ply/import_ply.py#L363
        loops_vert_idx = []
        faces_loop_start = []
        faces_loop_total = []
        lidx = 0
        for f in mesh_faces:
            nbr_vidx = len(f)
            loops_vert_idx.extend(f)
            faces_loop_start.append(lidx)
            faces_loop_total.append(nbr_vidx)
            lidx += nbr_vidx

        blender_mesh.loops.add(len(loops_vert_idx))
        blender_mesh.polygons.add(len(mesh_faces))

        blender_mesh.loops.foreach_set("vertex_index", loops_vert_idx)
        blender_mesh.polygons.foreach_set("loop_start", faces_loop_start)
        blender_mesh.polygons.foreach_set("loop_total", faces_loop_total)

        blender_mesh.update()
        blender_mesh.validate()

    def init_mesh(self):
        total_path=self.path+str(self.start_file_num)+self.name+self.extension
        self.load_mesh(total_path)
        


    def __call__(self, scene, depsgraph=None ):
        frame_number=scene.frame_current
        frame_number=frame_number % frame_end
        total_path=self.path+str(frame_number)+self.name+self.extension
        self.load_mesh(total_path)
