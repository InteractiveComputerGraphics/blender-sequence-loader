import fileseq
import meshio
import numpy as np

def preprocess(fileseq: fileseq.FileSequence, frame_number: int) -> meshio.Mesh:   
    # this renders all the faces(both surface and inside)
    # by default, the addon only renders the surface faces  
    frame_number = frame_number % len(fileseq)
    mesh = meshio.read(fileseq[frame_number])
    new_cells = []
    for cell in mesh.cells:
        if cell.type=="tetra":
            faces = []
            for d in cell.data:
                faces.append([d[0],d[1],d[2]])
                faces.append([d[0],d[1],d[3]])
                faces.append([d[0],d[2],d[3]])
                faces.append([d[1],d[2],d[3]])
            new_cells.append(('triangle',np.array(faces, dtype=np.int32)))
        else:
            new_cells.append((cell.type,cell.data))
    return meshio.Mesh(mesh.points,new_cells,mesh.point_data)