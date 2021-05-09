Structure:

meshio_addon.py: creates the addon in blender, e.g. panel

importer.py: super class of all types of importer

mesh_importer.py: (triangle) mesh importer

particle_importer.py: particles importer



Before run it:
install meshio and fileseq using blender pip 

How to run:

copy the blender_script.py to blender script editor, and edit the corresonding file path

Limitations:
1. structures of filenames
2. multi cells files, e.g. a file with both triangel mesh and quad mesh.

