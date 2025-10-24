import concurrent.futures
import time
import bpy
from .importer import update_obj
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

def terminate() -> None:
    global _init
    if not _init:
        return
    _executor.shutdown(wait=False, cancel_futures=True)
    _init = False
    print("terminated")

class Frame():
    _future: concurrent.futures.Future
    _buffer: bpy.types.Scene
    _frame: int = -1

    def flush_buffer(self, scene, depsgraph, *, target_frame: int = -1):
        print()
        if target_frame == -1 or self._frame + 1 != target_frame:
            self._frame = -1
            update_obj(scene, depsgraph)
            print("invalidate buffer")
            return
        print("future done flush?: ", self._future.done())
        concurrent.futures.wait([self._future])
        print("future done wait?: ", self._future.done())
        scene = self._buffer
        
    def queue_load(self, scene, depsgraph):
        start = time.perf_counter()
        global _executor, _init
        if not _init:
            init()
        copy_start = time.perf_counter()
        self._buffer = scene.copy()
        copy_end = time.perf_counter()
        self._frame = scene.frame_current
        start_queue = time.perf_counter()
        end_construct = time.perf_counter()
        self._future = _executor.submit(update_obj, self._buffer, depsgraph)
        print("future done enqueue?: ", self._future.done())
        end_submit = time.perf_counter()
        end = time.perf_counter()
        print("queue_load():\n\ttotal: ", (end - start) * 1000, "\n\tcopy: ", (copy_end - copy_start) * 1000, "\n\tqueuing:", (end - start_queue) * 1000)
        print("\t\tconstructor: ", (end_construct - start_queue) * 1000, "\n\t\tsubmit: ", (end_submit - end_construct) * 1000)

_frame = Frame()

def queue_load(scene, depsgraph=None) -> None:
    _frame.queue_load(scene, depsgraph)
    return

def flush_buffer(scene, depsgraph) -> None:
    _frame.flush_buffer(scene, depsgraph, target_frame=scene.frame_current)
    return