import bpy
import mathutils
import re
import os
import struct
import meshio
from math import radians

def readBIN_to_meshio(filepath):
    firstFile = open(filepath, 'rb')

    # read number of bodies
    bytes = firstFile.read()
    firstFile.close()

    # currently assume that numBodies is always 1
    (numBodies,), bytes = struct.unpack('i', bytes[:4]), bytes[4:]

    # determine length of file name string
    (strLength,), bytes = struct.unpack('i', bytes[:4]), bytes[4:]

    # read file name
    objFile, bytes = bytes[:strLength], bytes[strLength:]
    objFileString = objFile.decode('ascii')
    print(objFileString)

    field_data = {}
    field_data["translation"] = None
    field_data["scaling"] = None
    field_data["rotation"] = None
    field_data["transformation_matrix"] = None

    # Read scaling factors in first file
    (sx,), bytes = struct.unpack('f', bytes[:4]), bytes[4:]
    (sy,), bytes = struct.unpack('f', bytes[:4]), bytes[4:]
    (sz,), bytes = struct.unpack('f', bytes[:4]), bytes[4:]

    field_data["scaling"] = (sx, sy, sz)

    (isWall,), bytes = struct.unpack('?', bytes[:1]), bytes[1:]
    (colr,), bytes = struct.unpack('f', bytes[:4]), bytes[4:]
    (colg,), bytes = struct.unpack('f', bytes[:4]), bytes[4:]
    (colb,), bytes = struct.unpack('f', bytes[:4]), bytes[4:]
    (cola,), bytes = struct.unpack('f', bytes[:4]), bytes[4:]

    # if the object name is empty, then we know that it is not a "first file"
    # and we just simply reopen it and start from the beginning
    if len(objFileString) == 0:
        otherFile = open(filepath, 'rb')

        # reopen same file
        bytes = otherFile.read()
        otherFile.close()

        # since there is no object referenced, create empty mesh
        mesh = meshio.Mesh([], [])
    else:
        # create mesh from referenced object
        dirPath = os.path.dirname(filepath)
        objPath = os.path.join(dirPath, objFileString)

        mesh = meshio.read(objPath)


    # Read translation in first file
    (x,), bytes = struct.unpack('f', bytes[:4]), bytes[4:]
    (y,), bytes = struct.unpack('f', bytes[:4]), bytes[4:]
    (z,), bytes = struct.unpack('f', bytes[:4]), bytes[4:]

    field_data["translation"] = (x, y, z)

    # Read rotation in first file
    r = []
    for _ in range(0,9):
        (value,), bytes = struct.unpack('f', bytes[:4]), bytes[4:]
        r.append(value)

    rotationMatrix = mathutils.Matrix()
    rotationMatrix[0][0:3] = r[0], r[3], r[6]
    rotationMatrix[1][0:3] = r[1], r[4], r[7]
    rotationMatrix[2][0:3] = r[2], r[5], r[8]

    field_data["rotation"] = rotationMatrix.to_quaternion()

    field_data["transformation_matrix"] = mathutils.Matrix.LocRotScale(field_data["translation"],>

    print(field_data["translation"])
    print(field_data["rotation"])
    print(field_data["scaling"])
    print(field_data["transformation_matrix"])

    #print(filepath)
    #print(dirPath)
    #print(objFileString)
    #print(objPath)

    mesh.field_data = field_data
    return mesh

    #print("-----------------------")
    #print(objPath)
    #print("-----------------------")
    bpy.ops.import_scene.obj(filepath=objPath)

    return meshio.Mesh([], [], field_data=field_data)

# no need for write function
meshio.register_format("bin", [".bin"], readBIN_to_meshio, {".bin": None})