import concurrent.futures
import time
import bpy
import meshio
from .importer import load_into_ram, update_scene, update_obj, update_mesh, apply_transformation
from bpy.app.handlers import persistent

_executor: concurrent.futures.ThreadPoolExecutor
_init = False

@persistent
def init() -> None:
    global _executor, _init
    _executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)
    _executor.submit(pow, 2, 2)
    _init = True
    print("init")

def _load_data_into_buffer(meshio_mesh, buffer, object: bpy.types.Object):
    buffer_data = object.data.copy()
    update_mesh(meshio_mesh, buffer_data)
    buffer[object.name_full] = buffer_data

class Frame():
    _future: concurrent.futures.Future
    _loading_threads: list[concurrent.futures.Future]
    _buffer_meshes: dict[str, meshio.Mesh]
    _buffer_data: dict[str, bpy.types.Mesh]
    _frame: int = -1
    loading_complete: bool = False

    def _load_buffer_to_data(self, object: bpy.types.Object, meshio_mesh, depsgraph):
        if object.name_full in self._buffer_data:
            object.data = self._buffer_data[object.name_full]
            apply_transformation(meshio_mesh, object, depsgraph)

    def _obj_load(self, obj, scene, depsgraph):
        start_time = time.perf_counter()
        mesh = load_into_ram(obj, scene, depsgraph, target_frame=self._frame)
        if isinstance(mesh, meshio.Mesh):
            self._buffer_meshes[obj.name_full] = mesh
            _load_data_into_buffer(mesh, self._buffer_data, obj)
            end_time = time.perf_counter()
            obj.BSEQ.last_benchmark = (end_time - start_time) * 1000

    def _load_objs(self, scene, depsgraph):
        start = time.perf_counter()
        self._frame = scene.frame_current + scene.frame_step
        self._buffer_meshes = {}
        self._buffer_data = {}
        self._loading_threads = []
        n_loaded = 0
        for obj in bpy.data.objects:
            future = _executor.submit(self._obj_load, obj, scene, depsgraph)
            self._loading_threads.append(future)
        for future in concurrent.futures.as_completed(self._loading_threads):
            n_loaded += 1
            scene.BSEQ.loading_status = f"{n_loaded}/{len(bpy.data.objects)}"
        concurrent.futures.wait(self._loading_threads)
        scene.BSEQ.loading_status = "Complete"
        self._loading_threads.clear()
        end = time.perf_counter()
        print("load_objs() took ", (end - start) * 1000, " ms")

    def _delete_mesh(self, mesh: meshio.Mesh):
        mesh.point_data.clear()
        mesh.cell_data.clear()

        mesh.point_sets.clear()
        mesh.cell_sets.clear()
        mesh.cells.clear()
        mesh.field_data.clear()
        del mesh.points
        if hasattr(mesh, "attributes"):
            mesh.attributes.clear()

    def _clear_buffer(self):
        if not hasattr(self, "_buffer_meshes") or len(self._buffer_meshes) == 0:
            print("buffer empty")
            return
        for name, mesh in self._buffer_meshes.items():
            self._delete_mesh(mesh)
        for _, obj in self._buffer_data.items():
            bpy.data.meshes.remove(obj, do_unlink=False)
        self._buffer_meshes.clear()
        self._buffer_data.clear()

    def flush_buffer(self, scene, depsgraph, *, target_frame: int = -1):
        start_time = time.perf_counter()
        print()
        if target_frame == -1 or self._frame != target_frame:
            self._frame = -1
            update_obj(scene, depsgraph)            
            print("invalidate buffer")
            self._clear_buffer()
            return
        concurrent.futures.wait([self._future])
        for obj in bpy.data.objects:
            if obj.name_full in self._buffer_meshes:
                # update_scene(obj, self._buffer_meshes[obj.name_full], scene, depsgraph)
                self._load_buffer_to_data(obj, self._buffer_meshes[obj.name_full], depsgraph)
        self._clear_buffer()
        end_time = time.perf_counter()
        print("update_scene() took ", (end_time - start_time) * 1000, " ms")
        
    def queue_load(self, scene, depsgraph):
        start = time.perf_counter()
        global _executor, _init
        if not _init:
            init()
        copy_start = time.perf_counter()
        self._buffer = scene.copy()
        
        copy_end = time.perf_counter()
        self._frame = scene.frame_current + scene.frame_step
        start_queue = time.perf_counter()
        self._future = _executor.submit(self._load_objs, scene, depsgraph)
        scene.BSEQ.loading_status = "Queued"
        end = time.perf_counter()
        print("queue_load():\n\ttotal: ", (end - start) * 1000, "\n\tcopy: ", (copy_end - copy_start) * 1000, "\n\tqueuing:", (end - start_queue) * 1000)

_frame = Frame()

def queue_load(scene, depsgraph=None) -> None:
    start_time = time.perf_counter()
    _frame.queue_load(scene, depsgraph)
    print("queue_load() took ", (time.perf_counter() - start_time) * 1000, " ms")

def flush_buffer(scene, depsgraph) -> None:
    _frame.flush_buffer(scene, depsgraph, target_frame=scene.frame_current)

def terminate() -> None:
    global _init
    if not _init:
        return
    _executor.shutdown(wait=False, cancel_futures=True)
    _init = False
    _frame._clear_buffer()
    print("terminated")