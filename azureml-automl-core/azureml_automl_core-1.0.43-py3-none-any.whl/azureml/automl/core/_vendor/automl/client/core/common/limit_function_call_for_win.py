# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Helper module to restrict the training time on windows platform."""
from typing import Any, Tuple, Optional
from multiprocessing import Process, Queue, freeze_support
import os
from automl.client.core.common.killable_subprocess \
    import kill_process_tree_in_windows
from automl.client.core.common.limit_function_call_exceptions import TimeoutException


def process_start_fn(fn, queue, **kwargs):
    """
    Process start function used in creating the new windows process.

    :param fn: the actual function to be called
    :param queue:  the queue where result will be placed from the fn.
    :param kwargs:  arguments to the fn
    :return:
    """
    result = None, None
    try:
        result = fn(**kwargs)
    finally:
        queue.put(result)


def kill_process(proc):
    """
    Terminate the process and all its children.

    :param proc:  the process to terminate
    :return:
    """
    try:
        kill_process_tree_in_windows(proc.pid)
    except Exception:
        raise


def enforce_time_limit(max_time_in_sec, fn, kwargs):
    """
    Run the function with a limit on execution time.

    :param max_time_in_sec: allowed time for the fn.
    :param fn:  the fn to be restricted.
    :param kwargs: arguments for the fn.
    :return:
    """
    if __name__ == "__main__":
        freeze_support()
    q = Queue()     # type: Queue[Tuple[Optional[Any], Optional[BaseException]]]
    out = None
    subproc = Process(target=process_start_fn, args=(fn, q), kwargs=kwargs)
    try:
        subproc.start()
        out = q.get(timeout=max_time_in_sec)
    except Exception as e:
        # pid is set only after a process is started successfully.
        try:
            if subproc.pid and os.getpid() != subproc.pid:
                kill_process(subproc)
                subproc.join()
        except Exception:
            raise
        finally:
            if str(e) == "":
                out = None, TimeoutException()
            else:
                out = None, e
            assert (not subproc.is_alive())
    finally:
        return out
