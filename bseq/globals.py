# here are the implementations of global settings

import bpy
from datetime import datetime
import os
from .utils import refresh_obj

def print_information(scene):
    if not bpy.context.scene.BSEQ.print:
        return
    now = datetime.now()
    path = bpy.context.scene.render.filepath
    path = bpy.path.abspath(path)
    if not os.path.isdir(path):
        # by default, path is '/tmp', and it does not exist on windows system
        return
    filepath = path + '/bseq_' + now.strftime("%Y-%m-%d_%H-%M")
    with open(filepath, 'w') as file:
        file.write("Render Time: {}\n".format(now.strftime("%Y-%m-%d_%H-%M")))
        file.write("bseq Objects in the scene:\n\n")
        for obj in bpy.data.objects:
            bseq_prop = obj.BSEQ
            if bseq_prop.init:
                file.write("Object name: {}\n".format(obj.name))
                file.write("Is it being animated: {}\n".format(bseq_prop.enabled))
                file.write("Filepath: {}\n".format(bseq_prop.pattern))
                file.write("Is it relative path: {}\n".format(bseq_prop.use_relative))
                file.write("\n\n")


def auto_refresh(scene, depsgraph=None):
    if not bpy.context.scene.BSEQ.auto_refresh:
        return
    for obj in bpy.data.objects:
        if obj.BSEQ.init == False:
            continue
        if obj.BSEQ.enabled == False:
            continue
        if obj.mode != "OBJECT":
            continue
        refresh_obj(obj, scene)