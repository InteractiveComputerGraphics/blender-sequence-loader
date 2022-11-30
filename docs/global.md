# Global Settings

There are two global settings

1. Print information: default `true`
1. Auto Refresh: default `false`

## Print information

When this button is toggled, it will print information about the sequence imported by this addon, such as name of the object, into a separate file.

The file has the naming pattern `bseq_{time}`, where `{time}` is the time when rendering is started.

The file will be located in the [blender render output directory](https://docs.blender.org/manual/en/latest/editors/preferences/file_paths.html#render). [^1]

![print](../images/print.png)

[^1]: By default the value is `/tmp`, and this directory does not exit on windows system. So when the directory does not exist, it won't print information into file.

## Auto Refresh

When this button is toggled, it will [refresh](./list.md#refresh) **all the sequences whenever a frame change occurs**.

This option can be useful when some of the sequences are imported while the data is still being generated and not yet complete. Refreshing all the sequences can detect the frames that were added after being initially imported.

![auto refresh](../images/auto_refresh.png)