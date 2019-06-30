import json
from functools import wraps

from django.http import HttpRequest

from .param import Param
from .packing import Packing
from .error import ErrorCenter, E
from .arg import get_arg_dict


class AnalyseError(ErrorCenter):
    TMP_METHOD_NOT_MATCH = E("请求方法错误", hc=400)
    TMP_REQUEST_TYPE = E('请求体类型错误', hc=400)


AnalyseError.register()


class Analyse:
    @staticmethod
    @Packing.pack
    def _validate_params(param_list, param_dict):
        result = dict()
        if not param_list:
            return result
        for param in param_list:
            if isinstance(param, Param):
                value = param_dict.get(param.name)
                ret = param.run(value)
                if not ret.ok:
                    return ret
                result[param.name] = ret.body
        return result

    @classmethod
    def params(cls, *param_list):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                param_dict = get_arg_dict(func, args, kwargs)
                ret = cls._validate_params(param_list, param_dict)
                if not ret.ok:
                    return ret
                return func(**param_dict)
            return wrapper
        return decorator

    @classmethod
    def r(cls, b=None, q=None, a=None, method=None):
        def decorator(func):
            @wraps(func)
            def wrapper(request, *args, **kwargs):
                if not isinstance(request, HttpRequest):
                    return AnalyseError.TMP_REQUEST_TYPE
                if method and method != request.method:
                    return AnalyseError.TMP_METHOD_NOT_MATCH
                param_dict = dict()

                request.a_dict = get_arg_dict(func, args, kwargs)
                ret = cls._validate_params(a, request.a_dict)
                if not ret.ok:
                    return ret
                param_dict.update(ret.body or {})

                request.q_dict = request.GET.dict() or {}
                ret = cls._validate_params(q, request.q_dict)
                if not ret.ok:
                    return ret
                param_dict.update(ret.body or {})

                try:
                    request.b_dict = json.loads(request.body.decode())
                except json.JSONDecodeError:
                    request.b_dict = {}
                ret = cls._validate_params(b, request.b_dict)
                if not ret.ok:
                    return ret
                param_dict.update(ret.body or {})
                request.d = Param.Classify(param_dict)
                return func(request, *args, **kwargs)

            return wrapper

        return decorator

