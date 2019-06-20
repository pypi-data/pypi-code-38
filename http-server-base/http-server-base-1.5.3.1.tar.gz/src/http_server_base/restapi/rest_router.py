import inspect
from functools import wraps
from typing import List, Union, Dict, Type, Tuple, Any, Pattern, Callable, TypeVar, Optional

import parse
import re

from http_server_base import Logged_RequestHandler
from http_server_base.restapi.extras import DEFAULT_ALLOWED_METHODS
from http_server_base.tools import RegExpType, ReDict
from http_server_base.restapi import ArgumentError, ArgumentType, MethodNotAllowedError, ArgumentListType, CanonicalArgumentListType, CanonicalArgumentType

from logging import getLogger

from tornado.routing import Router
logger = getLogger('http_server_base.restapi.helper')

class RestRouter(Router):
    # Dictionary: class_full_name (with module) -> method_lower -> regular -> rest_method scope dict
    
    method_mapper: Dict[str, Dict[str, ReDict[Dict[str, Any]]]] = dict()
    
    @staticmethod
    def get_class_name(cls:type) -> str:
        _m = inspect.getmodule(cls)
        _class_name = cls.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0]
        return f'{_m.__name__}.{_class_name}'
    
    @staticmethod
    def get_function_parent_class(func) -> Optional[type]:
        if (inspect.ismethod(func)):
            for cls in inspect.getmro(func.__self__.__class__):
                if (cls.__dict__.get(func.__name__) is func):
                    return cls
            func = func.__func__  # fallback to __qualname__ parsing
    
        if (inspect.isfunction(func)):
            _m = inspect.getmodule(func)
            _class_name = func.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0]
            return getattr(_m, _class_name)
    
        return None  # not required since None would have been implicitly returned anyway

    @staticmethod
    def get_function_parent_class_name(func) -> Optional[str]:
        if (inspect.ismethod(func)):
            for cls in inspect.getmro(func.__self__.__class__):
                if (cls.__dict__.get(func.__name__) is func):
                    return RestRouter.get_class_name(cls)
            func = func.__func__  # fallback to __qualname__ parsing
    
        if (inspect.isfunction(func)):
            _m = inspect.getmodule(func)
            _class_name = func.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0]
            return f'{_m.__name__}.{_class_name}'
    
        return None  # not required since None would have been implicitly returned anyway
    
    @staticmethod
    def convert_to_tuple(x):
        if (isinstance(x, tuple)):
            return x
        return (x, )
    
    PARAMETER_PATTERNS = \
    {
        str: r'\w\s-]+',
        int: r'[0-9]+',
        float: r'[0-9]+(\.[0-9]*)?',
        bool: r'true|false',
        None: r'[^/?#]+',
    }
    
    DEFAULT_ARG = object()

    @staticmethod
    def get_class_mapper(x:Union[Type, str]) -> Dict[str, ReDict]:
        class_name = None
        if (isinstance(x, type)):
            class_name = RestRouter.get_class_name(x)
        elif (isinstance(x, str)):
            class_name = x
        
        class_dict = RestRouter.method_mapper.get(class_name) or ReDict()
        return class_dict

    @staticmethod
    def remove_base_path(path:str, base_path:str):
        if (path.startswith(base_path)):
            path = path[len(base_path):]
            if (not path.startswith('/')):
                path = '/' + path

        return path

    @staticmethod
    def get_mapper_func(x:Union[Type, str]) -> Callable[[str, str, str], Tuple[str, Callable]]:
        class_dict = RestRouter.get_class_mapper(x)
        def func(method:str, path:str, base_path:str= '') -> Tuple[str, Callable]:
            method = method.lower()
            if (not method in class_dict):
                raise MethodNotAllowedError(f"Method {method.upper()} is not allowed")

            path = RestRouter.remove_base_path(path, base_path)
            _func = class_dict[method][path]['action']
            return path, _func
        return func
    
    @classmethod
    def get_canonical_form_of_argument(cls, arg:ArgumentType) -> CanonicalArgumentType:
        """
        Extracts the argument info from the free argument description form
        :param arg:
        Either str or tuple
        Str: argument_name. Any type. No default. Mandatory
        
        Tuple:
            (argument_name): the same
            (argument_name, argument_type): No default. Mandatory.
            (argument_name, argument_types, argument_default): Optional.
        
        Where:
            argument_name: str. Can have leading '?', marking argument as an optional (None will be returned if no default). Can have '=', making everything behind it the argument_default.
            argument_types: Type or Tuple of Types. Types used for strict type checks. 'None' is any type.
            argument_default: any legal type. The default value is returned if the argument itself is missing.
        :return:
        
        Tuple:
            (argument_name:str, argument_types:Tuple[Type+], argument_default, mandatory:bool)
        
        Where:
            mandatory: True if argument is mandatory, False if optional.
        """
        
        arg = RestRouter.convert_to_tuple(arg)
        required: bool = True
        param_name: str = arg[0]
    
        if (len(arg) > 1):
            param_types = RestRouter.convert_to_tuple(arg[1])
            if (any(not isinstance(__arg, type) and not __arg is None for __arg in list(param_types))):
                if (len(param_types) == 1):
                    param_types = set(list(param_types)[0])
                else:
                    param_types = set(param_types)
        else:
            param_types: Tuple[Type] = (None,)
    
        if (len(arg) > 2):
            param_default = arg[2]
            required = False
        elif ('=' in param_name):
            param_name, _, param_default = param_name.partition('=')
            required = False
        else:
            param_default = RestRouter.DEFAULT_ARG
    
        if (param_name.startswith('?')):
            param_name = param_name[1:]
            if (not None in param_types):
                param_types = param_types + (None,)
            required = False
        
        return param_name, param_types, param_default, required
    @classmethod
    def get_canonical_form_of_argument_list(cls, args:ArgumentListType) -> CanonicalArgumentListType:
        if (args is None):
            return list()

        return [ cls.get_canonical_form_of_argument(arg) for arg in args]
    
    @staticmethod
    def patternize(uri:str, url_args:ArgumentListType=DEFAULT_ARG) -> Tuple[str, List[str]]:
        result = re.escape(uri)
        
        if (url_args is None):
            keys = list()
        
        elif (url_args is RestRouter.DEFAULT_ARG):
            result = result.replace('\\{', '{').replace('\\}', '}')
            parameters = parse.parse(result, result).named
            for _param_name in parameters:
                _pattern = RestRouter.PARAMETER_PATTERNS[None]
                _pattern = rf'(?P<{_param_name}>{_pattern})'
                result = result.replace(parameters[_param_name], _pattern)
            keys = parameters.keys()
            
        else:
            keys = list()
            for _arg in url_args:
                _pattern = RestRouter.PARAMETER_PATTERNS[None]

                _arg = RestRouter.convert_to_tuple(_arg)
                _param_name = _arg[0]
                if (len(_arg) > 1):
                    if (isinstance(_arg[1], set)):
                        _pattern = rf"({r')|('.join(re.escape(str(_x)) for _x in _arg[1])})"
                    
                    else:
                        _param_types = RestRouter.convert_to_tuple(_arg[1])
                        _patterns = list()
                        for _param_type in _param_types:
                            _p = RestRouter.PARAMETER_PATTERNS.get(_param_type, RestRouter.DEFAULT_ARG)
                            if (not _p is RestRouter.DEFAULT_ARG):
                                _patterns.append(_p)
                        
                        if (len(_patterns) > 0):
                            _pattern = rf"({r')|('.join(_patterns)})"
                        
                result = result.replace(f'\\{{{_param_name}\\}}', rf"(?P<{_param_name}>{_pattern})")
                keys.append(_param_name)
        
        return r'^' + result + r'/?(\?.+)?$', keys
    
    @staticmethod
    def get_path_regular(*, path:str, path_regular:Union[str,Pattern[str]], path_args:ArgumentListType, **kwargs) -> Tuple[RegExpType, ArgumentListType]:
        if (path_regular is None):
            if (not path is None):
                _regular_s, _url_params = RestRouter.patternize(path, path_args)
                if (path_args == RestRouter.DEFAULT_ARG):
                    path_args = _url_params
                _regular = re.compile(_regular_s, flags=re.IGNORECASE)
            else:
                raise ValueError("Either uri or uri_regular must be presented")
        else:
            if (isinstance(path_regular, str)):
                _regular = re.compile(path_regular, flags=re.IGNORECASE)
        
            elif (isinstance(path_regular, RegExpType)):
                _regular = path_regular
        
            else:
                raise TypeError(f"uri_regular must be either str, compiled regular or None; but not {type(path_regular)}")
            
            if (path_args == RestRouter.DEFAULT_ARG):
                path_args = None
        
        return _regular, path_args
        
    @staticmethod
    def rest_method \
    (
        path:str= '/', path_regular:Union[str,Pattern[str]]=None,
        method:Union[str, List[str], Tuple[str]]='GET',
        *,
        path_args:ArgumentListType=DEFAULT_ARG,
        body_args:ArgumentListType=None,
        query_args:ArgumentListType=None,
        header_args:ArgumentListType=None,
        support_arguments_capitalization_style_switch:bool=False,
        simple_return:bool=False,
        
        class_name:str=None,
        return_method_info:bool = False,
        **kwargs,
    ):
        if (method == '*'):
            method = DEFAULT_ALLOWED_METHODS
        
        _regular, path_args = RestRouter.get_path_regular(**locals())
        logger.debug(f"Rest method registrator generator is called for the method {str(method).upper()}: {_regular}")

        path_args = RestRouter.get_canonical_form_of_argument_list(path_args)
        body_args = RestRouter.get_canonical_form_of_argument_list(body_args)
        query_args = RestRouter.get_canonical_form_of_argument_list(query_args)
        header_args = RestRouter.get_canonical_form_of_argument_list(header_args)

        # This will NOT decorate a function
        # It only registers it
        def rest_method__registrator(func, http_method=None):
            if (http_method is None):
                http_method = method
            if (isinstance(http_method, (list, tuple))):
                _results = list()
                for _method in http_method:
                    _method = _method.lower()
                    _results.append(rest_method__registrator(func, http_method=_method))
                if (return_method_info):
                    return _results
                else:
                    return func
            elif (isinstance(http_method, str)):
                _method = http_method.lower()
            else:
                raise TypeError(f"http_method must be either str, List[str] or Tuple[str], not {type(http_method)}")

            _class_name = class_name or RestRouter.get_function_parent_class_name(func)
            logger.debug(f"Rest registrator is called on the '{_class_name}' / {func.__name__}")
            
            async def rest_method__registrator__action(self: Logged_RequestHandler, url, *parsed_path_args, **parsed_path_kwargs):
                try:
                    path_kwargs   = self.get_args(_regular.match(url).groupdict(), path_args, source_type='path',    support_capitalization_style_switch=support_arguments_capitalization_style_switch)
                    body_kwargs   = self.get_args(self.request.body_arguments, body_args,     source_type='body',    support_capitalization_style_switch=support_arguments_capitalization_style_switch)
                    query_kwargs  = self.get_args(self.request.query_arguments, query_args,   source_type='query',   support_capitalization_style_switch=support_arguments_capitalization_style_switch)
                    header_kwargs = self.get_args(self.request.headers, header_args,          source_type='headers', support_capitalization_style_switch=support_arguments_capitalization_style_switch)
                except ArgumentError:
                    return
                
                result = func(self, **path_kwargs, **body_kwargs, **query_kwargs, **header_kwargs)
                if (inspect.isawaitable(result)):
                    result = await result
                
                if (simple_return):
                    if (not self._finished):
                        self.resp_success(result=result)
            
            if (not _class_name in RestRouter.method_mapper):
                RestRouter.method_mapper[_class_name] = dict()
            if (not _method in RestRouter.method_mapper[_class_name]):
                RestRouter.method_mapper[_class_name][_method] = ReDict()
            
            paths = (path, path_regular)
            RestRouter.method_mapper[_class_name][_method][_regular] = locals()
            RestRouter.method_mapper[_class_name][_method][_regular]['action'] = rest_method__registrator__action
            
            if (return_method_info):
                return RestRouter.method_mapper[_class_name][_method][_regular]
            else:
                return func
        
        return rest_method__registrator
    
    @staticmethod
    def extract_args \
    (
        *,
        body_args:ArgumentListType=None,
        query_args:ArgumentListType=None,
        header_args:ArgumentListType=None,
        support_arguments_capitalization_style_switch:bool=False,
        
        class_name:str=None,
        **kwargs
    ):
        
        body_args = RestRouter.get_canonical_form_of_argument_list(body_args)
        query_args = RestRouter.get_canonical_form_of_argument_list(query_args)
        header_args = RestRouter.get_canonical_form_of_argument_list(header_args)
        
        def extract_args__decorator(func):
            _class_name = class_name or RestRouter.get_function_parent_class_name(func)
            logger.debug(f"Rest argument extractor generator is called on the {_class_name} / {func.__name__}")
            
            @wraps(func)
            def extract_args__decorator__wrapper(self, *args, **kwargs):
                try:
                    body_kwargs   = self.get_args(self.request.body_arguments, body_args,     source_type='body',    support_capitalization_style_switch=support_arguments_capitalization_style_switch)
                    query_kwargs  = self.get_args(self.request.query_arguments, query_args,   source_type='query',   support_capitalization_style_switch=support_arguments_capitalization_style_switch)
                    header_kwargs = self.get_args(self.request.headers, header_args,          source_type='headers', support_capitalization_style_switch=support_arguments_capitalization_style_switch)
                except ArgumentError:
                    return
                
                result = func(self, *args, **kwargs, **body_kwargs, **query_kwargs, **header_kwargs)
                return result
            return extract_args__decorator__wrapper
        return extract_args__decorator
    
    def find_handler(self, request, **kwargs):
        pass
