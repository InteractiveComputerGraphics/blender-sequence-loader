# This is the template specifically show how to load mzd files.
# For more information about mzd, you can find at https://github.com/wdas/partio and https://github.com/digitalillusions/BlenderPartioTools/tree/master/extern/partio
# and python bind at https://github.com/digitalillusions/BlenderPartioTools/tree/master/partio_extension_pybind
# For general information about how to write template, please look at the template.py

import meshio
import fileseq
import bpy
import numpy as np


def preprocess(fileseq: fileseq.FileSequence, frame_number: int) -> meshio.Mesh:
    # type the path to the partio binary file
    partio_pybind_path = ''
    # here is an example
    # partio_pybind_path = '/home/hui/Desktop/BlenderPartioTools/partio_extension_pybind/partio_pybind.cpython-39-x86_64-linux-gnu.so'

    
    # load partio_pybind module
    import importlib
    spec = importlib.util.spec_from_file_location('partio_pybind', partio_pybind_path)
    partio_pybind = importlib.util.module_from_spec(spec)

    # read particle data from file
    frame_number = frame_number % len(fileseq)
    file = fileseq[frame_number]
    particle = partio_pybind.read(file)


    # construct meshio.mesh
    points = None
    n_particles = particle.numParticles()
    point_data = {}
    for i in range(particle.numAttributes()):
        attr = particle.attributeInfo(i)
        attr_data = np.array(particle.data_buffer(attr), copy=True)
        if attr.name == 'position':
            points = attr_data
        else:
            point_data[attr.name] = attr_data
    
    
    # release memory
    particle.release()

    return meshio.Mesh(
        points,
        # the cells is not important here, 
        # Inside simloader, cells with vertex type will be ignored 
        cells=[('vertex',[])],
        point_data=point_data)
