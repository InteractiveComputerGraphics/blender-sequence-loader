# Blender Tool
Loading animation sequences with meshio and fileseq


## 1. Clone the project
`git clone https://www.graphics.rwth-aachen.de:9000/hhui/blendertool  --recurse-submodules` to download both project and dependency

### 1.1 Windows Users

Before go ahead, please delete the `meshio`, `future` and `fileseq` file, they should be a symlink to the extern folder, but it doesn't work on windows. 

Then you need to create the symlink again, by following command

```Batchfile
mklink /d meshio extern\meshio\src\meshio 
mklink /d fileseq extern\fileseq\src\fileseq 
mklink /d future extern\python-future\src\
```
Note: You may need to run this with administrator, or using delevoper mode. For more details, please find [here](https://blogs.windows.com/windowsdeveloper/2016/12/02/symlinks-windows-10/).

> There is no change in how to call mklink.  For users who have Developer Mode enabled, the mklink command will now successfully create a symlink if the user is not running as an administrator.

Something else: I have tried the command `git clone -c core.symlinks=true` to clone the project directly with symlink, but it seems it will create a symlink to a **file**, but in this case, it is linked to a **folder**, so is not what I want. If you have find any better solution with this, please let me know.

### 1.2 Linux & Mac Users

It should work without any problems.


## 2. Build & Install

Then you can create a zip file of this entire folder, it should work fine. Then you can install it by add this zip file to blender add-on system.

## 3. How to use

todo