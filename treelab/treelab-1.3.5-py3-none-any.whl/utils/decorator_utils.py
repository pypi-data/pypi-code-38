import asyncio
from functools import wraps
from sys import version_info
from typing import List

import grpc
from rx import Observable

from treelab.rxmq_treelab.rxmq import Rxmq


def async_run(fn):
    """
    Wrapper that makes async run (the developers' lives as well) easier
    :param fn:
    :return:
    """

    @wraps(fn)
    def wrapped(*args, **kwargs):
        if version_info.major == 3:
            if version_info.minor >= 7:
                return asyncio.run(fn(*args, **kwargs))
            else:
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(fn(*args, **kwargs))
        else:
            raise ValueError("Python 2 is not currently supported")

    return wrapped


def wait(event_name):
    """
    Wrapper for taking care of asynchronous grpc calls
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, workspace_id: str = None, wait_till_complete: bool = True, name_spaces: List[str] = None):
            if not workspace_id and event_name != 'WorkspaceCreated':
                raise ValueError('workspace_id can be None only under the case when event_name == WorkspaceCreated')
            if not name_spaces:
                name_spaces = []
            grpc_api, grpc_input, meta_data = fn(*args)
            if wait_till_complete:
                response = grpc_api(grpc_input, metadata=meta_data)
                complete_event_name = '.'.join(name_spaces + [response.id, event_name])
                if event_name != 'WorkspaceCreated':
                    wait_for_first_event(workspace_id, complete_event_name)
                return response
            else:
                future: grpc.Future = grpc_api.future(grpc_input)
                return future

        return wrapper

    return decorator


def wait_for_first_event(workspace_id: str, event_name: str) -> Observable:
    """
    Listening for the first event with topic under workspace with workspace_id
    :param workspace_id:
    :param event_name:
    :return:
    """
    return Rxmq.channel(workspace_id).observe(event_name)
