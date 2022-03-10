# When opening this file using blender text editor, you DO NOT need to click the 'run script' button
# just copy the code, or write you own version, and select the file in addon interface
#
# Currently, only the following functions can be customized
# 1. preprocess
# This function reads the file sequence, and frame number in blender
# It returns a meshio object, which will be imported into blender at current frame
#
# 2. process
# This funciton reads the file sequence, and frame number in blender, and also pass the bpy.types.mesh object
# So you can directly edit the mesh.
# 
#
#
# Note: process has higher priority, which means, when process exists, preprocess will be ignored.
# When preprocess and process both not exist, addon will call the default version.
# 
# In general, we suggest to use preprocess alone, since meshio has a relatively clear and simple data structure, 
# while directly manipulate bpy.types.mesh could be complicated

# Here is an example, and this is the default version inside simloader


import meshio
import fileseq
import bpy

# import your extra packages here


def process(fileseq: fileseq.FileSequence, frame_number: int, mesh: bpy.types.Mesh):
    # However, you can not call preprocess inside process fucntion
    frame_number = frame_number % len(fileseq)
    meshio_mesh = meshio.read(fileseq[frame_number])
    update_mesh(meshio_mesh, mesh)

# because process exists, preprocess here will be ignored
def preprocess(fileseq: fileseq.FileSequence, frame_number: int) -> meshio.Mesh:
    # This is the default version inside simloader
    # frame_number = frame_number % len(fileseq)
    # mesh = meshio.read(fileseq[frame_number])
    # return mesh
    pass



