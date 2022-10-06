# List View

By default, all supported file formats are simply imported as geometry (a collection of vertices, lines, triangles and quads). As such, you should be able to directly play/render the animation if it contains geometry.

Note: When rendering the animation, please turn on the [Lock Interface](https://docs.blender.org/manual/en/latest/interface/window_system/topbar.html?#render-menu)[^1]. This will prevent artifacts from occurring, especially if the user continues to operate the Blender interface during the render process.

![lock](../images/lock.png)

[^1]: Or maybe not, I am not 100% percent sure about this.

## Imported Sequence

Here you can have an overview of all the sequence imported by this addon. And you can select either one of them, it will change [active object](https://docs.blender.org/manual/en/latest/scene_layout/object/selecting.html#selections-and-the-active-object) to it as well. When [active object](https://docs.blender.org/manual/en/latest/scene_layout/object/selecting.html#selections-and-the-active-object) changes, it will change the selection in this list view as well.

![list](../images/list.png)

## Enable & Disable

It is possible to individually enable and disable sequences from updating when the animation frame changes. This is very useful when working with very large files or many sequences as it reduces the computational overhead of loading these sequences. Enabled means, that the sequence will be updated on frame change, and Disabled means that the sequence won't be updated on frame change.

To change individual sequence, you can click on the `ENABLED` or `DISABLED` button in the list view.

![enable](../images/enable.png)

### Enable Selected & Disable Selected

When you want to enable or disable multiple sequences. You can [select](https://docs.blender.org/manual/en/latest/scene_layout/object/selecting.html) multiple objects, then click `Enable Selected` or `Disable Selected` to enable/disable all selected objects.


## Current Frame

`Current Frame` shows the current frame of sequence being loaded. By default, the value is [blender current frame](https://docs.blender.org/manual/en/latest/editors/timeline.html#frame-controls). For advanced usage, you can find it [here](./frame.md).

## Refresh

Refresh Sequence can be useful when the sequence is imported while the data is still being generated and not yet complete. Refreshing the sequence can detect the frames added after being imported.
