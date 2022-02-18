# This is the template specifically show how to load mzd files.
# For more information about mzd, you can find at https://github.com/InteractiveComputerGraphics/MayaMeshTools/tree/main/extern/mzd
# For general information about how to write template, please look at the template.py


import meshio
import fileseq
import bpy
import mzd


# In general we suggest to directly use process for performance and compatibility reason, 
# meshio does not support face corner attributes
# However, if you want an easy way to modify the mesh, then meshio.mesh could be the choice

def process(fileseq: fileseq.FileSequence, frame_number: int, mesh:bpy.types.Mesh):
    frame_number = frame_number % len(fileseq)
    mzd.readMZD_to_bpymesh(fileseq[frame_number],mesh)

# this will be ignored
def preprocess(fileseq: fileseq.FileSequence, frame_number: int) -> meshio.Mesh:
   frame_number = frame_number % len(fileseq)
   mesh = mzd.readMZD_to_meshio(fileseq[frame_number])
   return mesh