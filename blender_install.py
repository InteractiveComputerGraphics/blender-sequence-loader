import bpy
import addon_utils
from datetime import date
import time
import os
import importlib
from sys import platform

bpy.ops.script.reload()

addon_module = [m for m in addon_utils.modules() if m.bl_info.get('name') == "Sequence Loader"] # get module
# uninstall old version
if addon_module:
	#addon_utils.disable("blendersequenceloader")
	bpy.ops.preferences.addon_disable(module="blendersequenceloader")
	bpy.ops.preferences.addon_remove(module="blendersequenceloader")

fp = ''
today = str(date.today())
if platform == "linux" or platform == "linux2":
	fp = f'/servers/karl/ssd-home2/jstotz/blender-sequence-loader/blender_sequence_loader_{today}.zip'
	os.system("python /servers/karl/ssd-home2/jstotz/blender-sequence-loader/build_addon.py")
elif platform == "win32" or platform == "cygwin" or platform == "msys":
	fp = f'C:\\code\\work\\blender-sequence-loader\\blender_sequence_loader_{today}.zip'
	os.system("python C:\\code\\work\\blender-sequence-loader\\build_addon.py")

# install new version
bpy.ops.preferences.addon_install(filepath=fp)
time.sleep(2)
bpy.ops.preferences.addon_enable(module="blendersequenceloader")
#addon_utils.enable("blendersequenceloader")
time.sleep(1)
os.system("blender")