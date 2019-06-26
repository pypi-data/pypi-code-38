import inspect
import json
import urllib.parse as urlparse
from typing import List, Union, Callable, Iterable, TypeVar, Any, Dict, Tuple, Type, Set, Optional

from camel_case_switcher import dict_keys_camel_case_to_underscore, camel_case_to_underscore, underscore_to_camel_case

from http_server_base import Logged_RequestHandler
from http_server_base.restapi import ArgumentValueError, ArgumentTypeError, MethodNotAllowedError, ArgumentListType, ArgumentType, CanonicalArgumentType, CanonicalArgumentListType
from http_server_base.restapi import RestRouter
from http_server_base.tools import ReDict, JsonSerializable

class Rest_RequestHandler(Logged_RequestHandler):
    
    base_path: str = '/'
    return_405: bool = True
    generate_options: bool = True
    class_name: str = None
    
    method_mapper_func: Callable[[str, str, str], Callable]
    method_mapper_dict: Dict[str, ReDict[Callable]]
    
    def initialize(self, class_name=None,
            base_path:str=None, return_405:bool=None, generate_options:bool=None,
            **kwargs):
        super().initialize(**kwargs)
        
        if (not class_name is None):
            self.class_name = class_name
        if (self.class_name is None):
            cls = type(self)
        else:
            cls = self.class_name
        
        if (not base_path is None):
            self.base_path = base_path
        if (not return_405 is None):
            self.return_405 = return_405
        if (not generate_options is None):
            self.generate_options = generate_options
        
        for _method_name in self.SUPPORTED_METHODS:
            _method_lower = _method_name.lower()
            if (_method_lower == 'options' and self.generate_options):
                setattr(self, _method_lower, self.options_handler)
            else:
                _original_method = getattr(self, _method_lower, self.method_handler)
                setattr(self, _method_lower, self.method_handler)
                setattr(self, f"_{_method_lower}", _original_method)
        
        self.method_mapper_dict = RestRouter.get_class_mapper(cls)
        self.method_mapper_func = RestRouter.get_mapper_func(cls)
    
    def prepare(self):
        self.parse_body_args()
        super().prepare()
    
    @classmethod
    def type_check(cls, source_type, param_name, value, types:Union[Tuple[Type], Set[Any]], param_default) -> Tuple[bool, str, Any]:
        success = False
        reason = None
        
        # Predefined list of values
        if (isinstance(types, set)):
            success = value in types
            if (not success):
                reason = f"Argument '{param_name}' from {source_type} value must be one of the set: {types}, but not '{value}'"
        
        else:
            for _param_type in types:
                if (_param_type is None):
                    success = True
                    break
                
                elif (value is param_default or value == param_default):
                    success = True
                    break
                
                elif (isinstance(value, _param_type)):
                    if (isinstance(value, list)):
                        value = [ _arg.decode() if isinstance(_arg, bytes) else _arg for _arg in value ] 
                    success = True
                    break
                
                elif (isinstance(value, str)):
                    try:
                        if (False): pass
                        elif (_param_type == bool):
                            value = value.lower() == 'true'
                        elif (_param_type in (dict, list, int, float)):
                            value = json.loads(value)
                        else:
                            value = _param_type(value)
                    except:
                        pass
                    else:
                        success = True
                        break
            
            if (not success):
                reason = f"Argument '{param_name}' from {source_type} must be any of '{types}', but not '{type(value)}'."
        
        return success, reason, value
    def get_argument_value(self, param_name:str, param_types:Tuple[Type], param_default, required:bool, source: dict, source_type:str, support_capitalization_style_switch:bool) -> Any:
        value = source.get(param_name.lower(), param_default)
        if (value is RestRouter.DEFAULT_ARG and support_capitalization_style_switch):
            value = source.get(underscore_to_camel_case(param_name).lower(), param_default)
            if (value is RestRouter.DEFAULT_ARG):
                value = source.get(camel_case_to_underscore(param_name).lower(), param_default)
        
        if (value is RestRouter.DEFAULT_ARG):
            if (required):
                message = f"Argument '{param_name}' is mandatory in {source_type}."
                self.resp_error(400, message)
                raise ArgumentValueError(message)
            else:
                value = None
        
        if (isinstance(value, list) and len(value) == 1 and not list in param_types):
            value = value[0]
        
        if (isinstance(value, bytes)):
            value = value.decode('utf8')
        
        if (isinstance(value, str)):
            value = value.strip()
        
        _success, _reason, value = self.type_check(source_type=source_type, param_name=param_name, value=value, types=param_types, param_default=param_default)
        if (not _success):
            self.resp_error(400, _reason)
            raise ArgumentTypeError(_reason)
        
        return value
    def parse_body_args(self):
        if (not self.request.body or self.request.body_arguments):
            self.logger.trace("Will not decode body arguments - body is empty")
            return
        
        if (self.request.headers.get('content-type') == 'application/json'):
            self.logger.trace("Trying to decode application/json data from body: {0}", self.request.body)
            _test = self.parse_body_args__application_json()
            if (_test is None):
                self.logger.trace("Body is invalid application/json")
                self.invalid_body_handler('application/json')
            else:
                self.logger.trace("Body is valid application/json")
                self.request.body_arguments = _test
            return
    
    def parse_body_args__application_json(self) -> Optional[dict]:
        try:
            _args = json.loads(self.request.body)
        except json.JSONDecodeError:
            return None
        else:
            if (isinstance(_args, dict)):
                return _args
            else:
                return { 'value': _args }
    
    def get_args(self, source: dict, args_description:CanonicalArgumentListType, source_type:str, support_capitalization_style_switch:bool):
        result = dict()
        source = { key.lower(): source[key] for key in source }
        if (not args_description is None):
            for param_name, param_types, param_default, required in args_description:
                value = self.get_argument_value(param_name, param_types, param_default, required, source, source_type, support_capitalization_style_switch)
                result[param_name] = value
        
        if (support_capitalization_style_switch):
            result = dict_keys_camel_case_to_underscore(result)
        return result
    
    def invalid_body_handler(self, content_type):
        self.resp_error(400, f"Request body is invalid {content_type}")
    
    async def method_handler(self, *path_args, **path_kwargs):
        if (self.request.method.upper() in self.SUPPORTED_METHODS):
            try:
                _path:str = self.request.path
                _path, _func = self.method_mapper_func(self.request.method, _path, self.base_path)
            except KeyError:
                self.resp_error(404, message='Requested method not found')
            except MethodNotAllowedError:
                if (self.return_405):
                    self.resp_error(405, message='Method not supported')
                else:
                    getattr(self, f"_{self.request.method.lower()}")(*path_args, **path_kwargs)
            else:
                result = _func(self, _path, *path_args, **path_kwargs)
                if (inspect.isawaitable(result)):
                    result = await result
        
        else:
            self.resp_error(405, message='Method not supported')
    
    def options_handler(self, *path_args, **path_kwargs):
        _url:str = RestRouter.remove_base_path(self.request.uri, self.base_path)
        methods = [ key.upper() for key in self.method_mapper_dict if _url in self.method_mapper_dict[key] ]
        methods = ', '.join(methods)

        self.set_header('Allow', methods)
        self.set_header('Access-Control-Allow-Methods', methods)
        self.resp(200, 'Headers responded')

    T = TypeVar('T')
    RespondableType = Union[JsonSerializable, bytes]
    def resp_paging(self,
            result_keys:List[T], result_values:Union[List[Union[JsonSerializable, bytes]], Callable[[T], Union[JsonSerializable, bytes]]],
            page:int=None, per_page:int=None, *,
            arg_name_page:str= 'page', arg_name_per_page:str= 'per_page', result_name='results',
            code:int=200, message=None, url_template=None,
    ):
        
        if (page is None):
            page = int(self.get_query_argument(arg_name_page, 1))
        if (per_page is None):
            per_page = int(self.get_query_argument(arg_name_per_page, 100))
        
        if (url_template is None):
            qs = urlparse.parse_qs(self.request.query)
            
            rand_page = self.generate_random_string(16)
            rand_per_page = self.generate_random_string(16)
            qs[arg_name_page] = [ rand_page ]
            qs[arg_name_per_page] = [ rand_per_page ]
            
            qs_encoded = urlparse.urlencode(self.remove_lists_from_query(qs)) \
                .replace(rand_page, '{page}') \
                .replace(rand_per_page, '{per_page}') \
            ;
            req = self.request
            url_template = f"{req.protocol}://{req.host}{req.path}?{qs_encoded}"
        
        self.resp(code, message)
        self.add_header('Content-Type', 'application/json')

        total_elements = len(result_keys)
        total_pages = total_elements // per_page
        page_start = (page - 1) * per_page
        page_end = min(total_elements, page * per_page) - 1

        paging = \
        {
            "page": page,
            "totalPages": total_pages,
            "perPage": per_page,
            "totalElements": total_elements,
            "pageStart": page_start,
            "pageEnd": page_end
        }
        if (page < 1 or page > total_pages):
            del paging["pageStart"]
            del paging["pageEnd"]
            del paging["page"]

        navigation = \
        {
            "nextPage": { "uri": url_template.format(page=page + 1, per_page=per_page), },
            "previousPage": { "uri": url_template.format(page=page - 1, per_page=per_page), },
            "firstPage": { "uri": url_template.format(page=1, per_page=per_page), },
            "lastPage": { "uri": url_template.format(page=total_pages, per_page=per_page), },
        }
        if (page <= 1):
            del navigation["previousPage"]
        if (page > total_pages):
            del navigation["nextPage"]

        resp = f"""{{
            "uri": "{url_template.format(page=page, per_page=per_page)}",
            "{result_name}": [
        """.encode('utf8')
        self.write(resp)

        for i in range(page_start, page_end + 1):
            if (callable(result_values)):
                resp = result_values(result_keys[i])
            else:
                resp = result_values[i]
            
            if (not isinstance(resp, bytes)):
                resp = json.dumps(resp, indent=4, sort_keys=True).encode('utf8')
            self.write(resp)
            if (i < page_end):
                self.write(b',')

        resp = f"""
            ],
            "paging": {json.dumps(paging)},
            "navigation": {json.dumps(navigation)}
        }}""".encode('utf8')
        self.write(resp)

        self.finish()
    
    @classmethod
    def remove_lists_from_query(cls, query_with_lists:Dict[str, List[Any]]) -> Dict:
        return { key: query_with_lists[key][0] for key in query_with_lists }
