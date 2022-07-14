Here you can find an example if you want to import customized file formats.

1. create an `example.py`
2. implement a function as following
```python
def read_func(filepath):
    # open the filepath linked file
    # construct the meshio object
    return meshio.Mesh
```
3. call `meshio.register_format("name", [".extenstion"], read_func, {".extenstion": None})`in global environment
4. add `from . import example` in `__init__.py`

You can check `bgeo.py` as an example, which reads the partiles-only [.bgeo](https://github.com/wdas/partio) file.

For more details how to construct the `meshio.Mesh` object, you can check [here](https://github.com/nschloe/meshio/wiki/meshio-Mesh()-data-structure) for the details about the data strucutre, and [here](https://github.com/nschloe/meshio/wiki/Node-ordering-in-cells) more details about the vertex ordering.
