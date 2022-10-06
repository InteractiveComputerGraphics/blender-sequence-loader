# Build and install the addon


## Build from source


1. Clone the project to download both project and dependencies

```shell
git clone https://github.com/InteractiveComputerGraphics/blender-sequence-loader.git  --recurse-submodules
```

2.  Build the installable .zip file by simply running the following command. This should produce a file called `blender_sequence_loader_{date}.zip`, where `{date}` is replaced with todays date. No other dependency other than standard python3 libraries are needed to build the addon.

```python
python3 build_addon.py
```


## Download from release page

Or you can simply download the latest `.zip` file from the [release](https://github.com/InteractiveComputerGraphics/blender-sequence-loader/releases) page

## Install the zip file

You can check [here](https://docs.blender.org/manual/en/latest/editors/preferences/addons.html#installing-add-ons) for installing and enabling the addon.

## For developers

If you want to develop this addon, using soft link (on Linux/macOS) / [Symlinks](https://blogs.windows.com/windowsdeveloper/2016/12/02/symlinks-windows-10/) (on Windows) can be very helpful.

### *-nix Users

Once you have cloned the project, go to the root directory of this addon, you can create symlink as follows
```bash
ln -s extern/meshio/src/meshio meshio
ln -s extern/rich/rich/ rich
ln -s extern/fileseq/src/fileseq fileseq
ln -s extern/python-future/src/future/ future
```

Then create a soft link to link from the [blender addon directory](https://docs.blender.org/manual/en/latest/advanced/blender_directory_layout.html)[^1] to the directory where you download and unzip the files. For example,
```bash
ln -s ~/Downloads/blender-sequence-loader ~/Library/Application Support/Blender/3.1/scripts/addons/blender-sequence-loader-dev
```

[^1]: By default, `{USER}/scripts/addons`, `{USER}`: Location of configuration files (typically in the user’s home directory). 


### Windows Users

You can use [mklink](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/mklink) to do the same things as *-nix users. [^2]

[^2]: You will need either administrator permission, or [developer mode](https://learn.microsoft.com/en-us/windows/apps/get-started/enable-your-device-for-development).

