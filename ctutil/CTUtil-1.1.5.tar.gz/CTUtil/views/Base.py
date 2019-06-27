from django.http import HttpRequest, HttpResponse
from CTUtil.Response.response import resp_error_json, resp_to_json
from typing import Dict, Union, Any, List
from functools import wraps
from django.conf.urls import url
import inspect


def exclude(func):
    @wraps(func)
    def _exclude(*args, **kwargs):
        return func(*args, **kwargs)
    setattr(_exclude, 'view', False)
    return _exclude


class BaseViewMeta(type):
    def __new__(cls, clsname, bases, clsdict: Dict[str, Any]):
        if clsdict.setdefault('abstract', False) is False:
            must_argv: List[str] = ['model_name', 'route_name']
            for argv in must_argv:
                if bases and not clsdict.setdefault(argv, None):
                    raise ValueError('Views must be model_name and route_name')
            route_name: str = clsdict.setdefault('route_name', None)
            if route_name:
                clsdict['route_name'] = f'{route_name}/' if not route_name.endswith('/') else route_name
        return super().__new__(cls, clsname, bases, clsdict)


class BaseView(metaclass=BaseViewMeta):

    model_name = None
    route_name = None
    abstract = True
    process_request = []
    page_key = 'pageNo'
    size_key = 'pageSize'

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def reqall(self) -> dict:
        if getattr(self, '_reqall', None) is None:
            self._reqall = self.process_request_post(self.request)
        return self._reqall

    @property
    def page(self):
        if getattr(self, '_page', None) is None:
            self._page = int(self.reqall.setdefault(self.page_key, 1))
        return self._page

    @property
    def size(self):
        if getattr(self, '_size', None) is None:
            _size = int(self.reqall.setdefault(self.size_key, 20))
            if _size > 40:
                _size = 40
            self._size = _size
        return self._size

    @exclude
    def process_request_post(
            self, request: HttpRequest) -> Dict[str, Union[str, int]]:
        data = request.POST.copy()
        _data: Dict[str, str] = {}
        for key in data:
            _data[key] = data.setdefault(key, '')
        return _data

    def query(self, request: HttpRequest) -> HttpResponse:
        return_data = {
            'state': 0,
            'data': list(self.model_name.objects.all()),
        }
        return resp_to_json(return_data)

    def delete(self, request: HttpRequest) -> HttpResponse:
        reqall: Dict[str, str] = self.process_request_post(request)
        _id: int = int(reqall.get('id', 0))
        if not _id:
            return resp_error_json('id不允许为空')
        query = self.model_name.objects.filter(id=_id)
        if not query:
            return resp_error_json('数据不存在')
        query.delete()
        return_data: Dict[str, Union[str, int]] = {
            'state': 0,
            'data': '删除成功',
        }
        return resp_to_json(return_data)

    def update(self, request: HttpRequest) -> HttpResponse:
        reqall: Dict[str, str] = self.process_request_post(request)
        _id: int = int(reqall.setdefault('id', 0))
        if not _id:
            return resp_error_json('id不允许为空')
        reqall.pop('id')
        query = self.model_name.objects.filter(id=_id)
        if not query:
            return resp_error_json('数据不存在')
        query.update(**reqall)
        return_data: Dict[str, Union[str, int]] = {
            'state': 0,
            'data': '修改成功',
        }
        return resp_to_json(return_data)

    def add(self, request: HttpRequest) -> HttpResponse:
        reqall: Dict[str, Union[str, int]] = self.process_request_post(request)
        if 'id' in reqall:
            del reqall['id']
        self.model_name.objects.create(**reqall)
        return_data: Dict[str, Union[str, int]] = {
            'state': 0,
            'data': '新增成功',
        }
        return resp_to_json(return_data)

    @classmethod
    def as_views(cls, method_name: str, **init):
        def view(reqeust: HttpRequest, *args, **kwargs):
            init['request'] = reqeust
            self = cls(**init)
            return self.dispatch(method_name, reqeust, *args, **kwargs)
        return view

    def dispatch(self, method_name: str, request, *args, **kwargs):
        handle = getattr(self, method_name)
        for func in self.process_request:
            handle = func(handle)
        return handle(request, *args, **kwargs)

    @classmethod
    def as_urls(cls, django_url_list):
        for k, v in cls.__dict__.items():
            if inspect.isfunction(v):
                if not getattr(v, 'view', True):
                    continue
                sig: inspect.Signature = inspect.signature(v)
                if str(sig.return_annotation) == str(HttpResponse) or sig.return_annotation == sig.empty:
                    name: str = k.replace('_', '-')
                    path = f'{name}-{cls.route_name}'
                    django_url_list.append(url(path, cls.as_views(k)))
