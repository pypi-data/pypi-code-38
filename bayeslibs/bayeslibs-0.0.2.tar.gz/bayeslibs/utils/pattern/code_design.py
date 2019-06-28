"""
@project:medical_robot_backend
@language:python3
@create:2019/4/27
@author:qianyang@aibayes.com
@description:none
"""


def singleton(cls):
    _instance = {}

    def decorator(*args, **kwargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwargs)
        return _instance[cls]

    return decorator
