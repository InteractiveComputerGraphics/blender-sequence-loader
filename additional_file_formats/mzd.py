## TODO: use dictionary as cells is going to be deprecated, should use list instead

head = b"    MZD-File-Format    \x00"  # c string has \x00 as end
end = b"   >> END OF FILE <<   \x00"  # c string has \x00 as end
import bpy
import numpy as np
import meshio
from .table import table

num_nodes_to_name = {3: 'triangle', 4: 'quad'}


def readMZD_to_meshio(filepath):
    out_numVertices = None
    out_numPolygons = None
    out_vertPositions = None
    out_numNodes = None  # number of loops
    out_polyVIndicesNum = None  # faces_loop_total
    out_polyVIndices = None  #loops_vert_idx
    cells = {}
    point_data = {}

    with open(filepath, 'rb') as file:
        byte = file.read(24)
        if byte != head:
            return -4
        while 1:
            # check if it reach the end
            byte = file.read(24)
            if byte == end:
                break
            else:
                # if not reach the end, rewind the pointer back 24 bytes
                file.seek(-24, 1)

            byte = file.read(4)
            chunkID = int.from_bytes(byte, byteorder='little')

            byte = file.read(24)
            name = byte

            byte = file.read(4)
            size = int.from_bytes(byte, byteorder='little')

            if chunkID == 0x0ABC0001:  # vertices and polygons.

                byte = file.read(4)
                out_numVertices = int.from_bytes(byte, byteorder='little')
                if out_numVertices < 0:
                    return -127
                if out_numVertices == 0:
                    break

                byte = file.read(12 * out_numVertices)
                out_vertPositions = np.frombuffer(byte, dtype=np.float32)

                byte = file.read(4)
                out_numPolygons = int.from_bytes(byte, byteorder='little')

                byte = file.read(out_numPolygons)
                out_polyVIndicesNum = np.frombuffer(byte, dtype=np.uint8)
                out_numNodes = out_polyVIndicesNum.sum(dtype=np.int32)

                byte = file.read(4)
                numBytesPerPolyVInd = int.from_bytes(byte, byteorder='little')

                if numBytesPerPolyVInd == 4:
                    #  int
                    byte = file.read(out_numNodes * numBytesPerPolyVInd)
                    out_polyVIndices = np.frombuffer(byte, dtype=np.int32)
                elif numBytesPerPolyVInd == 2:
                    #  unsigned short
                    byte = file.read(out_numNodes * numBytesPerPolyVInd)
                    # WARNING: not sure if it's correct
                    # uncovered branch from test data
                    out_polyVIndices = np.frombuffer(byte, dtype=np.uint16)
                else:
                    return -127
                start_polyVIndicesNum = 0
                start_polyVIndices = 0
                breaks = np.where(out_polyVIndicesNum[:-1] != out_polyVIndicesNum[1:])[0] + 1
                breaks = np.append(breaks, len(out_polyVIndicesNum))
                for b in breaks:
                    poly_nodes_num = out_polyVIndicesNum[start_polyVIndicesNum]  # 3(triangle) or 4 (quad)
                    end_polyVIndices = start_polyVIndices + poly_nodes_num * (b - start_polyVIndicesNum)
                    cells[num_nodes_to_name[poly_nodes_num]] = out_polyVIndices[start_polyVIndices:end_polyVIndices].reshape(
                        ((b - start_polyVIndicesNum), poly_nodes_num))
                    start_polyVIndices = end_polyVIndices
                    start_polyVIndicesNum = b

                faces_copy = np.copy(cells['triangle'])
                faces_copy.sort(axis=1)
                _, indxs, count = np.unique(faces_copy, axis=0, return_index=True, return_counts=True)
                faces = cells['triangle'][indxs]
                cells['triangle'] = faces

                faces_copy = np.copy(cells['quad'])
                faces_copy.sort(axis=1)
                _, indxs, count = np.unique(faces_copy, axis=0, return_index=True, return_counts=True)
                faces = cells['quad'][indxs]
                cells['quad'] = faces

            elif chunkID == 0xDA7A0001:  # vertex normals.
                byte = file.read(4)
                out_numVerticeAttributes = int.from_bytes(byte, byteorder='little')
                if out_numVerticeAttributes != out_numVertices:
                    return -127

                byte = file.read(out_numVerticeAttributes * 6)
                out_vertAttribute = np.frombuffer(byte, dtype=np.uint16)
                out_vertAttribute = table[out_vertAttribute]
                point_data['normal'] = out_vertAttribute.reshape((out_numVerticeAttributes, 3))

            elif chunkID == 0xDA7A0002:  # vertex motions
                byte = file.read(4)
                out_numVerticeAttributes = int.from_bytes(byte, byteorder='little')
                if out_numVerticeAttributes != out_numVertices:
                    return -127

                byte = file.read(out_numVerticeAttributes * 6)
                out_vertAttribute = np.frombuffer(byte, dtype=np.uint16)
                out_vertAttribute = table[out_vertAttribute]
                point_data['velocity'] = out_vertAttribute.reshape((out_numVerticeAttributes, 3))

            elif chunkID == 0xDA7A0003:  # vertex colors
                byte = file.read(4)
                out_numVerticeAttributes = int.from_bytes(byte, byteorder='little')
                if out_numVerticeAttributes != out_numVertices:
                    return -127

                byte = file.read(out_numVerticeAttributes * 8)
                out_vertAttribute = np.frombuffer(byte, dtype=np.uint16)
                out_vertAttribute = table[out_vertAttribute]
                point_data['color'] = out_vertAttribute.reshape((out_numVerticeAttributes, 3))

            elif chunkID == 0xDA7A0004:  # vertex UVWs.
                byte = file.read(4)
                out_numVerticeAttributes = int.from_bytes(byte, byteorder='little')
                if out_numVerticeAttributes != out_numVertices:
                    return -127

                byte = file.read(out_numVerticeAttributes * 12)
                out_vertAttribute = np.frombuffer(byte, dtype=np.float32)
                point_data['uvw_map'] = out_vertAttribute.reshape((out_numVerticeAttributes, 3))

            # For the rest of attributes, because meshio doest not support attributes on nodes, (equivalent to face cornder in blender)
            # So the attributes data will be skipped
            elif chunkID == 0xDA7A0011:  # node normals.
                file.seek(size, 1)
                pass
            elif chunkID == 0xDA7A0013:  # node colors.
                file.seek(size, 1)
                pass
            elif chunkID == 0xDA7A0014:  # node UVWs.
                file.seek(size, 1)
                pass
            else:
                file.seek(size, 1)
                pass
    return meshio.Mesh(out_vertPositions.reshape((out_numVertices, 3)), cells, point_data)


def readMZD_to_bpymesh(filepath, mesh):
    shade_scheme = False
    if mesh.polygons:
        shade_scheme = mesh.polygons[0].use_smooth

    if len(mesh.vertices) > 0:
        mesh.clear_geometry()

    out_numVertices = None
    out_numPolygons = None
    out_vertPositions = None
    out_numNodes = None  # number of loops
    out_polyVIndicesNum = None  # faces_loop_total
    out_polyVIndices = None  #loops_vert_idx

    with open(filepath, 'rb') as file:
        byte = file.read(24)
        if byte != head:
            return -4
        while 1:
            # check if it reach the end
            byte = file.read(24)
            if byte == end:
                break
            else:
                # if not reach the end, rewind the pointer back 24 bytes
                file.seek(-24, 1)

            byte = file.read(4)
            chunkID = int.from_bytes(byte, byteorder='little')

            byte = file.read(24)
            name = byte

            byte = file.read(4)
            size = int.from_bytes(byte, byteorder='little')

            if chunkID == 0x0ABC0001:  # vertices and polygons.

                byte = file.read(4)
                out_numVertices = int.from_bytes(byte, byteorder='little')
                if out_numVertices < 0:
                    return -127
                if out_numVertices == 0:
                    break

                byte = file.read(12 * out_numVertices)
                out_vertPositions = np.frombuffer(byte, dtype=np.float32)

                byte = file.read(4)
                out_numPolygons = int.from_bytes(byte, byteorder='little')

                byte = file.read(out_numPolygons)
                out_polyVIndicesNum = np.frombuffer(byte, dtype=np.uint8)
                out_numNodes = out_polyVIndicesNum.sum(dtype=np.int32)

                byte = file.read(4)
                numBytesPerPolyVInd = int.from_bytes(byte, byteorder='little')

                if numBytesPerPolyVInd == 4:
                    #  int
                    byte = file.read(out_numNodes * numBytesPerPolyVInd)
                    out_polyVIndices = np.frombuffer(byte, dtype=np.int32)
                elif numBytesPerPolyVInd == 2:
                    #  unsigned short
                    byte = file.read(out_numNodes * numBytesPerPolyVInd)
                    # WARNING: not sure if it's correct
                    # uncovered branch from test data
                    out_polyVIndices = np.frombuffer(byte, dtype=np.uint16)
                else:
                    return -127

                mesh.vertices.add(out_numVertices)
                mesh.vertices.foreach_set('co', out_vertPositions)

                mesh.loops.add(out_numNodes)
                mesh.loops.foreach_set('vertex_index', out_polyVIndices)

                mesh.polygons.add(out_numPolygons)
                mesh.polygons.foreach_set('loop_total', out_polyVIndicesNum)
                faces_loop_start = None

                if out_polyVIndicesNum.size > 0:
                    faces_loop_start = np.cumsum(out_polyVIndicesNum)
                    faces_loop_start = np.roll(faces_loop_start, 1)
                    faces_loop_start[0] = 0
                mesh.polygons.foreach_set('loop_start', faces_loop_start)
                mesh.polygons.foreach_set("use_smooth", [shade_scheme] * out_numPolygons)
                mesh.update()
                mesh.validate()

            elif chunkID == 0xDA7A0001:  # vertex normals.
                byte = file.read(4)
                out_numVerticeAttributes = int.from_bytes(byte, byteorder='little')
                if out_numVerticeAttributes != out_numVertices:
                    return -127

                byte = file.read(out_numVerticeAttributes * 6)
                out_vertAttribute = np.frombuffer(byte, dtype=np.uint16)
                out_vertAttribute = table[out_vertAttribute]
                # point_data['normal'] = out_vertAttribute.reshape((out_numVerticeAttributes, 3))

            elif chunkID == 0xDA7A0002:  # vertex motions
                byte = file.read(4)
                out_numVerticeAttributes = int.from_bytes(byte, byteorder='little')
                if out_numVerticeAttributes != out_numVertices:
                    return -127

                byte = file.read(out_numVerticeAttributes * 6)
                out_vertAttribute = np.frombuffer(byte, dtype=np.uint16)
                out_vertAttribute = table[out_vertAttribute]
                # point_data['velocity'] = out_vertAttribute.reshape((out_numVerticeAttributes, 3))

            elif chunkID == 0xDA7A0003:  # vertex colors
                byte = file.read(4)
                out_numVerticeAttributes = int.from_bytes(byte, byteorder='little')
                if out_numVerticeAttributes != out_numVertices:
                    return -127

                byte = file.read(out_numVerticeAttributes * 8)
                out_vertAttribute = np.frombuffer(byte, dtype=np.uint16)
                out_vertAttribute = table[out_vertAttribute]
                # point_data['color'] = out_vertAttribute.reshape((out_numVerticeAttributes, 3))

            elif chunkID == 0xDA7A0004:  # vertex UVWs.
                byte = file.read(4)
                out_numVerticeAttributes = int.from_bytes(byte, byteorder='little')
                if out_numVerticeAttributes != out_numVertices:
                    return -127

                byte = file.read(out_numVerticeAttributes * 12)
                out_vertAttribute = np.frombuffer(byte, dtype=np.float32)
                # point_data['uvw_map'] = out_vertAttribute.reshape((out_numVerticeAttributes, 3))

            elif chunkID == 0xDA7A0011:  # node normals.
                file.seek(size, 1)
                print(6)
                pass
            elif chunkID == 0xDA7A0013:  # node colors.
                file.seek(size, 1)
                print(7)
                pass
            elif chunkID == 0xDA7A0014:  # node UVWs.
                file.seek(size, 1)
                print(8)
                pass
            else:
                # print(name)
                file.seek(size, 1)
                pass


# no need for write function
meshio.register_format("mzd", [".mzd"], readMZD_to_meshio, {".mzd": None})