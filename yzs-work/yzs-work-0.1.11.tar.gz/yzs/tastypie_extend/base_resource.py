from django.conf.urls import url
from django.http import JsonResponse, HttpResponse
from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash
import functools

from yzs.tastypie_extend.response_code import resource_code_manage


def querydict_to_dict(querydict):
    data_dict = {}
    for key in querydict:
        value = querydict.getlist(key)
        data_dict[key] = value[0] if len(value) == 1 else value
    return data_dict


def api_view(url_path: str = None, url_name: str = None, auth: bool = False, allowed_methods: list = None,
             single_api: bool = False):
    """
    自动包装一个url映射
    url_path: api视图的backend的最后一个路径的名称, 默认为视图方法名称(替换下划线为横线)
    url_name: api视图对应的url定义中的name, 默认为资源类名称+视图方法名称
    auth: 指定是否需要用户验证
    allowed_methods: 用来制定自定义视图允许的请求方法列表
    single_api: 该方法是否对单个对象使用
    """

    def view_decorator(view_func):
        view_func._is_api = True
        view_func._url_path = url_path
        view_func._url_name = url_name
        view_func._single_api = single_api

        default_allowed_methods = ['get', 'options', 'head']
        final_methods = allowed_methods or default_allowed_methods

        @functools.wraps(view_func)
        def view_wrapper(self, request, *args, **kwargs):
            if auth:
                self.is_authenticated(request)
            self.method_check(request, final_methods)
            return view_func(self, request, *args, **kwargs)

        return view_wrapper

    return view_decorator


class BaseModelResource(ModelResource):
    CONTENT_TYPE_FIELD = 'CONTENT_TYPE'
    FORM_URLENCODED_CONTENT_TYPE = 'application/x-www-form-urlencoded'
    MULTIPART_CONTENT_TYPE = 'multipart/form-data'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._handel_api_view()

    def _handel_api_view(self):
        """
        处理api_view装饰器
        """
        self.prepend_url_list = []
        for attr_name in (attr_name for attr_name in dir(self) if attr_name not in dir(BaseModelResource)):
            attr_value = getattr(self, attr_name)
            if not callable(attr_value) or not hasattr(attr_value, '_is_api'):
                continue

            api_url_path = getattr(attr_value, '_url_path', None) or attr_name
            api_url_name = getattr(attr_value, '_url_name', None) or self._meta.resource_name + '_' + attr_name
            if hasattr(attr_value, '_single_api') and getattr(attr_value, '_single_api') is True:
                self.prepend_url_list.append(
                    url(r'^(?P<resource_name>{})/(?P<pk>\w[\w/-]*)/{}{}'.format(self._meta.resource_name, api_url_path,
                                                                                trailing_slash()),
                        self.wrap_view(attr_name), name=api_url_name)
                )
            else:
                self.prepend_url_list.append(
                    url(r'^(?P<resource_name>{})/{}{}'.format(self._meta.resource_name, api_url_path, trailing_slash()),
                        self.wrap_view(attr_name), name=api_url_name)
                )

    def prepend_urls(self):
        """
        自动生成prepend_urls
        :return:
        """
        return self.prepend_url_list or super().prepend_urls()

    def create_response(self, request, code: int = 0, message: str = '', data=None, response_class=HttpResponse,
                        **response_kwargs):
        if data is None:
            data = {}
        if isinstance(data, dict):
            if '_code' not in data:
                data['_code'] = code
            if '_message' not in data:
                data['_message'] = resource_code_manage.get_message(code)
        return super().create_response(request, data, response_class=HttpResponse, **response_kwargs)

    def deserialize(self, request, data=None, content_type=None):
        content_type = content_type or request.META.get(self.CONTENT_TYPE_FIELD, 'application/json')

        if self.FORM_URLENCODED_CONTENT_TYPE in content_type:
            return querydict_to_dict(request.POST)

        if self.MULTIPART_CONTENT_TYPE in content_type:
            data = querydict_to_dict(request.POST)
            data.update(request.FILES)
            return data

        return super().deserialize(request, data or request.body.decode(), content_type)
