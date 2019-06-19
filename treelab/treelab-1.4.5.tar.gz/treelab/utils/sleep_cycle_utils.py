"""

@Auther : Mason
@Date   : 
"""
import grpc
import time
from treelab.config import sleep_time, sleep_number
from functools import wraps


def cycle(event_name):
    """
    Query event GRPC error loop query
    :param event_name:
    :return:
    """

    def wrapper(func):
        @wraps(func)
        def inner_wrapper(*args, **kwargs):
            for i in range(sleep_number):
                value = ''
                try:
                    if event_name == 'workspace':
                        value = kwargs['workspace_id']
                        return func(args[0], workspace_id=value)
                    elif event_name == 'core':
                        value = args[1]
                        return func(args[0], core_id=value, workspace=args[2])
                    elif event_name == 'table':
                        value = args[1]
                        return func(args[0], table_id=value, core=args[2])
                    elif event_name == 'update_data':
                        table = kwargs['table'] if kwargs else args[0]
                        value = table.id
                        return func(table=table)
                    elif event_name == 'get_all_cores':
                        return func(args[0])
                    elif event_name == 'get_all_tables':
                        return func(args[0])
                    else:
                        raise ValueError('not event_name')
                except grpc.RpcError:
                    print(_out_message(value, event_name))
                    time.sleep(sleep_time + i)
                if i >= sleep_number - 1:
                    raise ValueError(_out_message(value, event_name))

        return inner_wrapper

    return wrapper


def _out_message(value, event_name):
    if value:
        return 'can not get data from {} by {}'.format(event_name, value)
    else:
        return 'can not add data from {} '.format(event_name)


def dormancy(event_name):
    """
    Put the update operation to sleep
    :param event_name:
    :return:
    """

    def wrapper(func):
        @wraps(func)
        def inner_wrapper(*args, **kwargs):
            time.sleep(sleep_time)
            if event_name == 'cell_update':
                return func(args[0], value=kwargs['value'])

        return inner_wrapper

    return wrapper
