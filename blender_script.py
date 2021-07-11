# This stub runs a python script relative to the currently open
# blend file, useful when editing scripts externally.



#  This is modified from blender template, so you can just run this file in blender, and it will automatically load other scripts to blender

import bpy
import os
import sys

#  change the filepath here, 
path = "C:\\Users\\hui\\Desktop\\blendertool\\" 

#  add the direction to sys.path, so it can find dependencies
if path not in sys.path:
    sys.path.append(path)

filepath = path + "__init__.py"

global_namespace = {"__file__": filepath, "__name__": "__main__"}
with open(filepath, 'rb') as file:
    exec(compile(file.read(), filepath, 'exec'), global_namespace)
