# When opening this file using blender text editor, you DO NOT need to click the 'run script' button
# just copy the code, or write you own version, and select the file in addon interface
#
# Currently, only the following functions can be customized
# 1. preprocess
# This function reads the file sequence, and frame number in blender
# It returns a meshio object, which will be imported into blender at current frame
# Here is the examples that you can do
# 1. rewrite the mapping between frame number and the mesh you are going to load
# 2. do some mesh processing, e.g. convert a tetrahedra mesh, which is not supported yet, to a triangle mesh
# 3. actually, you can do everything here, as long as you return a mesh object
#
# Here is an example, and this is the default version inside meshioimporter
#
# No need to write import here, only write here to make it clear
# import meshio
# import fileseq
# import bpy
def preprocess(fileseq: fileseq.FileSequence, frame_number: int) -> meshio.Mesh:
    frame_number = frame_number % len(fileseq)
    mesh = meshio.read(fileseq[frame_number])
    return mesh

#  An example to read mzd file
# def preprocess(fileseq: fileseq.FileSequence, frame_number: int) -> meshio.Mesh:
#     frame_number = frame_number % len(fileseq)
#     mesh = mzd.readMZD(fileseq[frame_number])
#     return mesh