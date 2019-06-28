"""

@Auther : Mason
@Date   : 
"""
import grpc
import time
from treelab.config import sleep_time, sleep_number
from functools import wraps
from treelab.utils.misc_utils import get_event_identifier


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


def listen_local_events(event):
    """
    This is used to listen for the end of the API request GRPC
    :param event:
    :return:
    """

    def wrapper(func):
        @wraps(func)
        def inner_wrapper(*args):
            event_name = get_event_identifier(args[1])
            if event_name and event_name.split('.')[-1] == 'ViewAdded' if event == 'TableViewAdded' else event:
                mark = False
                while args[0].id == 'default_id':
                    continue
                if (event in ['CoreCreated', 'CoreUpdated'] and '.'.join([args[0].id, event]) == event_name) \
                        or (event in ['TableCreated', 'TableNameUpdated', 'TableRemoved'] and '.'.join([args[0].core.id, args[0].id, event]) == event_name) \
                        or (event in ['ViewAdded'] and '.'.join([args[0].core.id, args[0].table.id, event]) == event_name and args[0].id == args[1].viewId) \
                        or (event in ['ViewUpdated', 'RowAdded'] and '.'.join([args[0].core.id, args[0].table.id, args[0].id, event]) == event_name) \
                        or (event in ['ColumnAdded', 'ColumnOrderUpdated'] and '.'.join([args[0].core.id, args[0].table.id, args[0].id, event]) == event_name) \
                        or (event in ['CellUpdated'] and '.'.join([args[0].core.id, args[0].table.id, event]) == event_name) \
                        or (event in ['ColumnWidthUpdated', 'RowAddedToView'] and '.'.join([args[0].core.id, args[0].table.id, args[0].view.id, event]) == event_name and args[0].id in [args[1].columnId, args[1].rowId]) \
                        or (event in ['RowOrderUpdated'] and '.'.join([args[0].core.id, args[0].table.id, args[0].view.id, event]) == event_name and args[0].id == args[1].rowId):
                    mark = True
                elif event == 'CoreRemoved':
                    core_remove_events = ['.'.join([core.id, event]) for core in args[0].get_all_cores()]
                    if event_name not in core_remove_events:
                        mark = True
                elif event == 'TableRemoved':
                    table_remove_events = ['.'.join([args[0].id, table.id, event]) for table in args[0].get_all_tables()]
                    if event_name in table_remove_events:
                        mark = True
                elif event in ['ColumnNameUpdated', 'ColumnConfigUpdated'] and event_name in ['.'.join([args[0].core.id, args[0].table.id, args[0].id, 'ColumnNameUpdated']), '.'.join([args[0].core.id, args[0].table.id, args[0].id, 'ColumnConfigUpdated'])]:
                    mark = True
                elif event in ['ViewRemoved', 'RowRemoved', 'ColumnRemoved']:
                    mark = True
                elif event == 'TableViewAdded' and '.'.join([args[0].core.id, args[0].id, 'ViewAdded']) == event_name and args[0].get_views()[0].id == args[1].viewId:
                    mark = True
                if mark:
                    while args[0]._flag:
                        args[0]._flag = False
                        args[0].workspace.dispose()

        return inner_wrapper

    return wrapper
