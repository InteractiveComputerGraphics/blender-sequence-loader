# SimLoader
Loading animation sequences with meshio and fileseq


## 1. Clone the project
`git clone https://www.graphics.rwth-aachen.de:9000/hhui/blendertool  --recurse-submodules` to download both project and dependencies


## 2. Build & Install

1. Build manually

    Clone the project as mentioned above, then run `python3 build_addon.py`, no additional dependency required, only python3 standard library.

2. Or download directly the addon from [release](https://graphics.rwth-aachen.de:9000/hhui/blendertool/-/releases) page. 


After getting the .zip file, install and enable it using blender addon system. See [here](https://docs.blender.org/manual/en/latest/editors/preferences/addons.html#installing-add-ons) for more details.


Note: 
1. You need to restart blender after enabling, otherwise some functionality may not work well.
2. don't forget to remove the old version of this addon (if present), before adding new version of this addon to blender. (Actually, I not very sure if it's necessary, but I think this would be better)


### 2.1 Complicated way

If you want to keep developing on this addon, it would be easier to create a soft link(or Symlinks on windows) at the root directory to the dependencies.


## 3. How to use

After installing addon, you can find it here. (Or simply press `n` key)

![start](images/0.png)

Then you can find it here.

![homepage](images/1.png)

### 3. Load the animation sequence you want.

#### 3.1
you can select the directory through GUI, by clicking the rightmost icon. It will pop up the default blender file explorer. Then you can go to the directory you want, for example, like image showed below. **You only need to go to the directory, then select nothing, just click "Accept"**.

![selecticon](images/2.png)

Then the addon will automatically detect the sequencens it finds in this directory, then you simply select the sequence you want.

![after_selecting](images/3.png)

##### 3.1.1
There is a small checkbox about whether using `relative path` or not.

when toggling on, then you must save the blender file first, before load the sequence. Then this sequence will be loaded using relative path, from the .blend file. Also if you move the .blend file and data altogether to another directory, it still works.

If not toggling on, it will use abosulte path to load the sequence. And you don't need to save the .blend file.

![relative_path](images/4.png)


#### 3.2

After the sequence being imported, it will be available in the `Sequences Imported` panel, and more details will be available in `Settings` panel.

![settings](images/5.png)

Now, you can play/render the animation as usual.

Note: when render the animation, please turn on the `Lock Interface`. 

![lock interface](images/6.png)

##### 3.2.1 Enable/ Disable

By `enable` means, that the sequence will be updated for each frame, and `disable` means that the sequence won't be updated for each frame, so it can save some computational resources if needed.

##### 3.2.1 Refresh Sequence

`Refresh Sequence` can be usefull, when you import the sequence, while the data is still being generated, and not finished yet. Refresh can detect the frames added after being imported.

#### 3.3 Settings

#### 3.3.1 Geometry Nodes

We provide some basic templates for the geometry nodes, especially for the particeles/vertices-only data. 

Applying `Point Cloud` geometry nodes, can convert the the vertices of the mesh to point clouds, which can be rendered only by [cycles](https://docs.blender.org/manual/en/latest/render/cycles/introduction.html).

Applying `Instances` geometry nodes, can convert the the vertices of the mesh to cubes, or others by adjusting the geometry nodes, which can be rendered by both [eevee](https://docs.blender.org/manual/en/latest/render/eevee/index.html) and [cycles](https://docs.blender.org/manual/en/latest/render/cycles/introduction.html).


Applying `Mesh` geometry nodes, will use the default geoemtry ndoes.

Note: 
1. `Instances` is super memory hungry compared with `Point Cloud`.
2. After applying `Point Cloud` or `Instances` geoemtry nodes, you need to assign the material inside the geometry nodes. So to save your work, you can simply assign the material here, then apply the `Point Cloud` or `Instances` geoemtry nodes.

![material](images/7.png)


#### 3.3.2 Path Information

Here shows the path of this sequence, however it's not editable.

#### 3.3.3 Attributes Settings

Here shows the available **Vertex Attributes**, it's not editable.

Note: in order to avoid the conflication with blender built-in attributes, so all the attributes names are renamed by adding a `2` at the end. For example, `id` -> `id2`. 

#### 3.3.4 Split Norm per Vertex

For more details, you can find it [here](https://docs.blender.org/manual/en/latest/modeling/meshes/structure.html#modeling-meshes-normals-custom). This is an easy way to set the selected vertex attribute as this split normal.

Note: the addon does not check if the selected attribute is suitable for normals or not. E.g. if the data type of the attribute is int, then it will give a runtime error.