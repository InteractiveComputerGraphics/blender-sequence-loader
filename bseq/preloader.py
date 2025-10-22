import concurrent.futures
import bpy

_executor: concurrent.futures.ThreadPoolExecutor
_init = False

def init() -> None:
    global _executor, _init
    _executor = concurrent.futures.ThreadPoolExecutor()
    if _executor._initializer_failed():
        print("init failed")
    _init = True
    print("init")

def terminate() -> None:
    global _init
    if not _init:
        return
    _executor.shutdown(wait=False, cancel_futures=True)
    _init = False
    print("terminated")
    
def is_init() -> bool:
    return _init

def queue_load(scene, depsgraph=None) -> None:
    global _executor, _init
    if not _init:
        raise AttributeError(_executor, "_executor")