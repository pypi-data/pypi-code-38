"""
Data Convert Library
"""
from types import SimpleNamespace


def dict2obj(data):
    """将字典对象转换为可访问的对象属性"""
    if not isinstance(data, dict):
        raise ValueError('data must be dict object.')

    def _d2o(d):
        _d = {}
        for key, item in d.items():
            if isinstance(item, dict):
                _d[key] = _d2o(item)
            else:
                _d[key] = item
        return SimpleNamespace(**_d)

    return _d2o(data)
