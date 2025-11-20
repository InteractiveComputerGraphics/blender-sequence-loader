import concurrent.futures
import time
import bpy
import meshio
from .importer import load_into_ram, update_obj, update_mesh, apply_transformation
from bpy.app.handlers import persistent

_executor: concurrent.futures.ThreadPoolExecutor
_init = False

# decorator for timing analysis
def timing(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        func(*args, **kwargs)
        end = time.perf_counter()
        print(func.__name__, "took", (end - start) * 1000, "ms")
    return wrapper

# This needs to be persistent to keep the executor
@persistent
def init() -> None:
    global _executor, _init
    _executor = concurrent.futures.ThreadPoolExecutor()
    _init = True

class Frame():
    _future: concurrent.futures.Future
    _loading_threads: list[concurrent.futures.Future]
    _buffer_meshes: dict[str, meshio.Mesh]
    _buffer_data: dict[str, bpy.types.Mesh]
    _buffer_timings: dict[str, float]
    _buffer_file_path: dict[str, str]
    _frame: int = -1

    def __init__(self):
        self._buffer_meshes = {}
        self._buffer_data = {}
        self._buffer_timings = {}
        self._loading_threads = []
        self._buffer_file_path = {}

    def _load_data_into_buffer(self, meshio_mesh, object: bpy.types.Object):
        """ Applies the meshio data to a copy of the object mesh """
        buffer_data = object.data.copy()
        update_mesh(meshio_mesh, buffer_data)
        self._buffer_data[object.name_full] = buffer_data

    def _load_buffer_to_data(self, object: bpy.types.Object, meshio_mesh, depsgraph):
        """ Swaps the object mesh with the buffered mesh """
        if object.name_full in self._buffer_data:
            old_mesh = object.data
            object.data = self._buffer_data[object.name_full]
            # We remove the old mesh data to prevent memory leaks
            bpy.data.meshes.remove(old_mesh, do_unlink=False)
            apply_transformation(meshio_mesh, object, depsgraph)

    @timing
    def _obj_load(self, obj, scene, depsgraph):
        """ Buffering Obj Job for the executor """
        start_time = time.perf_counter()
        mesh = load_into_ram(obj, scene, depsgraph, target_frame=self._frame, filepath_buffer=self._buffer_file_path)
        if isinstance(mesh, meshio.Mesh):
            self._buffer_meshes[obj.name_full] = mesh
            self._load_data_into_buffer(mesh, obj)
            end_time = time.perf_counter()
            # move to main threaded
            self._buffer_timings[obj.name_full] = (end_time - start_time) * 1000

    @timing
    def _load_objs(self, scene, depsgraph):
        """ Job which submits all object buffering jobs
            Also updates the buffering status in the UI
        """
        self._frame = scene.frame_current + scene.frame_step
        self._buffer_meshes = {}
        self._buffer_data = {}
        self._buffer_timings = {}
        self._loading_threads = []
        self._buffer_file_path = {}
        n_loaded = 0
        for obj in bpy.data.objects:
            future = _executor.submit(self._obj_load, obj, scene, depsgraph)
            self._loading_threads.append(future)
        for future in concurrent.futures.as_completed(self._loading_threads):
            n_loaded += 1
            # Due to multithreading, Blender may forbid writing to the loading status while rendering
            # In this case, we just skip the update as it is only a progress indication anyway
            try:
                scene.BSEQ.loading_status = f"{n_loaded}/{len(bpy.data.objects)}"
            except Exception as e:
                pass

        concurrent.futures.wait(self._loading_threads)
        scene.BSEQ.loading_status = "Complete"
        self._loading_threads.clear()

    def _clear_buffer(self):
        if not hasattr(self, "_buffer_meshes") or len(self._buffer_meshes) == 0:
            return
        self._buffer_meshes.clear()
        self._buffer_data.clear()
        self._buffer_timings.clear()
        self._buffer_file_path.clear()

    @timing
    def flush_buffer(self, scene, depsgraph, *, target_frame: int = -1):
        """ Applies the buffer to the scene and clears the buffer afterwards
        
            target_frame -- indicates the current frame which is to be loaded, 
            '-1' indicates do not use buffered frame

            If target_frame does not coincide with the buffered frame, the buffer will be
            invalidated and the scene is loaded without pre-buffering  
        
        """
        # if no target_frame is specified or if the target_frame does not coincide
        # with the buffered frame, invalidate the buffer and update the scene serially
        if target_frame == -1 or self._frame != target_frame:
            self._frame = -1
            update_obj(scene, depsgraph)
            for _, obj in self._buffer_data.items():
                bpy.data.meshes.remove(obj, do_unlink=False)
            self._clear_buffer()
            return
        # Barrier to wait until loading is actually completed
        concurrent.futures.wait([self._future])
        for obj in bpy.data.objects:
            if obj.name_full in self._buffer_meshes:
                self._load_buffer_to_data(obj, self._buffer_meshes[obj.name_full], depsgraph)
                obj.BSEQ.last_benchmark = self._buffer_timings[obj.name_full]
                obj.BSEQ.current_file = self._buffer_file_path[obj.name_full]

        self._clear_buffer()
    
    def queue_load(self, scene, depsgraph):
        """ Queues the next frame which is determined by the current frame and the set frame step

            Also initialises the executor if not initialized already        
        """
        start = time.perf_counter()
        global _executor, _init
        if not _init:
            init()

        self._frame = scene.frame_current + scene.frame_step
        self._future = _executor.submit(self._load_objs, scene, depsgraph)
        scene.BSEQ.loading_status = "Queued"

_frame = Frame()

def queue_load(scene, depsgraph=None) -> None:
    _frame.queue_load(scene, depsgraph)

def flush_buffer(scene, depsgraph) -> None:
    _frame.flush_buffer(scene, depsgraph, target_frame=scene.frame_current)

def terminate() -> None:
    global _init
    if not _init:
        return
    _executor.shutdown(wait=False, cancel_futures=True)
    _init = False
    for _, obj in _frame._buffer_data.items():
        bpy.data.meshes.remove(obj, do_unlink=False)
    _frame._clear_buffer()