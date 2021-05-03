Structure:

meshio_addon.py: creates the addon in blender, e.g. panel

importer.py: super class of all types of importer

mesh_importer.py: (triangle) mesh importer

particle_importer.py: particles importer


Current status:

haven't figure out how to import another py file in blender. So I copy the content of particles_importer.py to meshio_addon.py.

Before run it:
install meshio using blender pip 

How to run:

copy all the code from meshio_addon.py to blender script editor and run it.

Limitations:
1. structures of filenames
2. multi cells files, e.g. a file with both triangel mesh and quad mesh.

