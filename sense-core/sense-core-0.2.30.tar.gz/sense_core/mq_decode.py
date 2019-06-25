from collections import defaultdict


def list_queues(queues_list):
    _res = []
    for _queues in queues_list:
        _res.append({
            'name': _queues['name'],
            'messages': _queues['messages']
        })
    return _res


def dict_queues(queues_list):
    _res = {}
    for _queues in queues_list:
        _res[_queues['name']] = _queues['messages']
    return _res


def list_consumers(queues_list):
    _res = defaultdict(int)
    for _queues in queues_list:
        _res[_queues['queue']['name']] += 1
    return _res