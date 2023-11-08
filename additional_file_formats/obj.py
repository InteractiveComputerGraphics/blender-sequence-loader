"""
I/O for the Wavefront .obj file format, cf.
<https://en.wikipedia.org/wiki/Wavefront_.obj_file>.
"""
import datetime

import numpy as np

# from ..__about__ import __version__
# from .._exceptions import WriteError
# from .._files import open_file
# from .._helpers import register_format
# from .._mesh import CellBlock, Mesh

import meshio


def read(filename):
    with open_file(filename, "r") as f:
        mesh = read_buffer(f)
    return mesh


def read_buffer(f):
    points = []
    vertex_normals = []
    texture_coords = []
    face_groups = []
    face_normals = []
    face_texture_coords = []
    face_group_ids = []
    face_group_id = -1
    while True:
        line = f.readline()

        if not line:
            # EOF
            break

        strip = line.strip()

        if len(strip) == 0 or strip[0] == "#":
            continue

        split = strip.split()

        if split[0] == "v":
            points.append([float(item) for item in split[1:]])
        elif split[0] == "vn":
            vertex_normals.append([float(item) for item in split[1:]])
        elif split[0] == "vt":
            texture_coords.append([float(item) for item in split[1:]])
        elif split[0] == "s":
            # "s 1" or "s off" controls smooth shading
            pass
        elif split[0] == "f":
            # old: dat = [int(item.split("/")[0]) for item in split[1:]]
            # A face in obj has one of the following formats: 1, 1/2, 1//3, 1/2/3
            # We want to support all formats now amd store the texture and normal indices in other arrays
            face_indices = []
            face_texture_indices = []
            face_normal_indices = []

            for item in split[1:]:
                indices = item.split("/")
                face_indices.append(int(indices[0]))
                if len(indices) > 1 and indices[1] != "":
                    face_texture_indices.append(int(indices[1]))
                if len(indices) > 2:
                    face_normal_indices.append(int(indices[2]))

            if len(face_groups) == 0 or (
                len(face_groups[-1]) > 0 and len(face_groups[-1][-1]) != len(face_indices)
            ):
                face_groups.append([])
                face_group_ids.append([])
                face_texture_coords.append([])
                face_normals.append([])
            face_groups[-1].append(face_indices)
            face_group_ids[-1].append(face_group_id)
            if face_texture_indices:
                face_texture_coords[-1].append(face_texture_indices)
            if face_normal_indices:
                face_normals[-1].append(face_normal_indices)
        elif split[0] == "g":
            # new group
            face_groups.append([])
            face_group_ids.append([])
            face_texture_coords.append([])
            face_normals.append([])
            face_group_id += 1
        else:
            # who knows
            pass

    # There may be empty groups, too. <https://github.com/nschloe/meshio/issues/770>
    # Remove them.
    face_groups = [f for f in face_groups if len(f) > 0]
    face_group_ids = [g for g in face_group_ids if len(g) > 0]
    face_normals = [n for n in face_normals if len(n) > 0]
    face_texture_coords = [t for t in face_texture_coords if len(t) > 0]

    # convert to numpy arrays and remove
    points = np.array(points)
    face_groups = [np.array(f) for f in face_groups]
    texture_coords = [np.array(t) for t in texture_coords]
    vertex_normals = [np.array(n) for n in vertex_normals]
    point_data = {}
    cell_data = {}
    field_data = {}

    if face_texture_coords and len(texture_coords) == max([max(max(face)) for face in face_texture_coords]):
        field_data["obj:vt"] = texture_coords
        cell_data["obj:vt_face_idx"] = face_texture_coords
    elif len(texture_coords) == len(points):
        point_data["obj:vt"] = texture_coords

    if face_normals and len(vertex_normals) == max([max(max(face)) for face in face_normals]):
        field_data["obj:vn"] = vertex_normals
        cell_data["obj:vn_face_idx"] = face_normals
    elif len(vertex_normals) == len(points):
        point_data["obj:vn"] = vertex_normals

    cell_data["obj:group_ids"] = []
    cells = []
    for f, gid in zip(face_groups, face_group_ids):
        if f.shape[1] == 3:
            cells.append(CellBlock("triangle", f - 1))
        elif f.shape[1] == 4:
            cells.append(CellBlock("quad", f - 1))
        else:
            cells.append(CellBlock("polygon", f - 1))
        cell_data["obj:group_ids"].append(gid)

    return Mesh(points, cells, point_data=point_data, cell_data=cell_data, field_data=field_data)


def write(filename, mesh):
    for c in mesh.cells:
        if c.type not in ["triangle", "quad", "polygon"]:
            raise WriteError(
                "Wavefront .obj files can only contain triangle or quad cells."
            )

    with open_file(filename, "w") as f:
        f.write(
            "# Created by meshio v{}, {}\n".format(
                __version__, datetime.datetime.now().isoformat()
            )
        )
        for p in mesh.points:
            f.write(f"v {p[0]} {p[1]} {p[2]}\n")

        if "obj:vn" in mesh.point_data:
            dat = mesh.point_data["obj:vn"]
            fmt = "vn " + " ".join(["{}"] * dat.shape[1]) + "\n"
            for vn in dat:
                f.write(fmt.format(*vn))

        if "obj:vt" in mesh.point_data:
            dat = mesh.point_data["obj:vt"]
            fmt = "vt " + " ".join(["{}"] * dat.shape[1]) + "\n"
            for vt in dat:
                f.write(fmt.format(*vt))

        for cell_block in mesh.cells:
            fmt = "f " + " ".join(["{}"] * cell_block.data.shape[1]) + "\n"
            for c in cell_block.data:
                f.write(fmt.format(*(c + 1)))


register_format("obj", [".obj"], read, {"obj": write})
