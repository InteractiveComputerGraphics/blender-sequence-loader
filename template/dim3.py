# Here is an template to load 3-d mesh
# By default, the addon only renders the surface faces
# The template here will render all the faces, including the fase inside the mesh

# NOTE: this might break the `shade smooth` in blender 
import fileseq
import meshio
import numpy as np


def preprocess(fileseq: fileseq.FileSequence, frame_number: int) -> meshio.Mesh:
    frame_number = frame_number % len(fileseq)
    mesh = meshio.read(fileseq[frame_number])
    new_cells = []
    for cell in mesh.cells:
        if cell.type == "tetra":
            faces = []
            for d in cell.data:
                faces.append([d[1], d[0], d[2]])
                faces.append([d[0], d[1], d[3]])
                faces.append([d[0], d[3], d[2]])
                faces.append([d[1], d[2], d[3]])
            new_cells.append(('triangle', np.array(faces, dtype=np.uint64)))
        elif cell.type == "hexahedron":
            faces = []
            for d in cell.data:
                faces.append([d[0], d[3], d[2], d[1]])
                faces.append([d[1], d[2], d[6], d[5]])
                faces.append([d[1], d[5], d[4], d[0]])
                faces.append([d[4], d[5], d[6], d[7]])
                faces.append([d[2], d[3], d[7], d[6]])
                faces.append([d[0], d[4], d[7], d[3]])
            new_cells.append(('quad', np.array(faces, dtype=np.uint64)))
        else:
            new_cells.append((cell.type, cell.data))
    return meshio.Mesh(mesh.points, new_cells, mesh.point_data)
