import concurrent.futures
import time
import bpy
import meshio
from .importer import load_into_ram, update_scene, update_obj
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

class Frame():
    _future: concurrent.futures.Future
    _buffer_objs: dict[str, meshio.Mesh]
    _frame: int = -1

    def _load_objs(self, scene, depsgraph):
        start = time.perf_counter()
        self._frame = scene.frame_current + scene.frame_step
        self._buffer_objs = {}
        for obj in bpy.data.objects:
            # TODO: Select next frame (currently seems to load the current frame again)
            mesh = load_into_ram(obj, scene, depsgraph, target_frame = self._frame)
            if isinstance(mesh, meshio.Mesh):
                self._buffer_objs[obj.name_full] = mesh
        end = time.perf_counter()
        print("load_objs() took ", (end - start) * 1000, " ms")

    def _delete_mesh(self, mesh: meshio.Mesh):
        mesh.point_data.clear()
        mesh.cell_data.clear()
        mesh.point_sets.clear()
        mesh.cell_sets.clear()
        mesh.cells.clear()
        mesh.field_data.clear()
        if hasattr(mesh, "attributes"):
            mesh.attributes.clear()

    def _clear_buffer(self):
        if not hasattr(self, "_buffer_objs") or len(self._buffer_objs) == 0:
            print("buffer empty")
            return
        for name, mesh in self._buffer_objs.items():
            self._delete_mesh(mesh)
        self._buffer_objs.clear()

    def flush_buffer(self, scene, depsgraph, *, target_frame: int = -1):
        print()
        if target_frame == -1 or self._frame != target_frame:
            self._frame = -1
            update_obj(scene, depsgraph)            
            print("invalidate buffer")
            self._clear_buffer()
            return
        print("future done flush?: ", self._future.done())
        concurrent.futures.wait([self._future])
        print("future done wait?: ", self._future.done())
        start_time = time.perf_counter()
        for obj in bpy.data.objects:
            if obj.name_full in self._buffer_objs:
                update_scene(obj, self._buffer_objs[obj.name_full], scene, depsgraph)
        end_time = time.perf_counter()
        print("update_scene() took ", (end_time - start_time) * 1000, " ms")
        self._clear_buffer()
        
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
        end_submit = time.perf_counter()
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