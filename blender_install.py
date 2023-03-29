import bpy
import addon_utils
from datetime import date
import time
import os
import importlib

bpy.ops.script.reload()

addon_module = [m for m in addon_utils.modules() if m.bl_info.get('name') == "Sequence Loader"] # get module
# uninstall old version
if addon_module:
	#addon_utils.disable("blendersequenceloader")
	bpy.ops.preferences.addon_remove(module="blendersequenceloader")

os.system("python C:\\code\\work\\blender-sequence-loader\\build_addon.py")

time.sleep(1)
# install new version
today = str(date.today())
fp = f'C:\\code\\work\\blender-sequence-loader\\blender_sequence_loader_{today}.zip'
bpy.ops.preferences.addon_install(filepath=fp, overwrite=True)
time.sleep(1)
bpy.ops.preferences.addon_enable(module="blendersequenceloader")
addon_utils.enable("blendersequenceloader")
time.sleep(1)
os.system("blender")