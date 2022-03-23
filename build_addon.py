from zipfile import ZipFile
import os
from datetime import date


addondirectory = 'simloader'
templatedirectory = 'template'
additionaldirectory = 'additional_file_formats'
meshiodirectory = 'extern/meshio/src/meshio'
fileseqdirectory = 'extern/fileseq/src/fileseq'
futuredirectory = 'extern/python-future/src/future'
richdirectory = 'extern/rich/rich'

dirs = {
    addondirectory: addondirectory,
    templatedirectory: templatedirectory,
    meshiodirectory: 'meshio',
    fileseqdirectory: 'fileseq',
    futuredirectory: 'future',
    richdirectory: 'rich',
    additionaldirectory: additionaldirectory,
}

today = str(date.today())
with ZipFile(f'simloader_addon_{today}.zip', 'w') as addonzip:
    #  write all directories
    for k, v in dirs.items():
        for subdir, dirs, files in os.walk(k):
            for file in files:
                if "__pycache__" in subdir:
                    continue
                filepath = os.path.join(subdir, file)
                relative_path = os.path.relpath(filepath, k)
                endpath = os.path.join(v, relative_path)
                endpath = os.path.join('simloaderaddon/', endpath)
                addonzip.write(filepath, endpath)

    # write init.py
    addonzip.write('__init__.py', 'simloaderaddon/__init__.py')
