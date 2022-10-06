# Description

This is an addon for Blender 3.1+ (might work with 2.8+ but has not been tested) that enables loading of file sequences. The addon comes bundled together with [meshio](https://github.com/nschloe/meshio) which enables the loading of geometric data from a multitude of [file formats](./format.md).

All data is loaded *just-in-time* when the Blender frame changes, in order to avoid excessive memory consumption. By default, the addon is able to load vertices, lines, triangles and quads. It is also able to automatically extract triangle and quad surface meshes from tetrahedral and hexahedral volume meshes. Scalar and vector attributes on vertices are also imported for visualization purposes. 

## Basic usage

Here is a gif to show the basic usage of this addon. In this gif, it shows how to load and render a sequence of particles data

![usage](../images/usage.gif)

## Affected Blender Settings

This addon will change the value of `Preferences`->`Save & Load` ->`Default To` ->`Relative Paths` to `false`. Default value is `true`. For information can be found [here](https://docs.blender.org/manual/en/latest/editors/preferences/save_load.html#blend-files).


## Dependencies

|name | link | license| description|
|---|---|---|---|
|meshio | [link](https://github.com/nschloe/meshio) | MIT| import the mesh|
|fileseq | [link](https://github.com/justinfx/fileseq) | MIT | detect and load file sequences|
| rich | [link](https://github.com/Textualize/rich) | MIT| dependency of meshio |
| python-future | [link](https://github.com/PythonCharmers/python-future) | MIT|  dependency of fileseq|

## License

MIT License

Copyright (c) 2022 Interactive Computer Graphics 

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.