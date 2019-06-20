from typing import Callable, Any, Dict, List, TypeVar

from .string_processor import camel_case_to_underscore, underscore_to_camel_case

T = Dict[str, Any]
TList = TypeVar('TList', List[T], List[Any])
TArg = TypeVar('TArg', str, T, List[T], List[Any])
class _ObjectProcessor():
    def __init__(self, func: Callable[[str], str], recursive: bool, **options):
        self.func = func
        self.recursive = recursive
        self.options = options
    
    def process_str(self, obj: str) -> str:
        # noinspection PyArgumentList
        return self.func(obj, **self.options)
    
    def process_dict(self, obj: T) -> T:
        result = dict()
        
        for key in obj:
            new_key = key
            new_obj = obj[key]
            
            if (isinstance(key, str)):
                new_key = self.process_str(new_key)
            if (self.recursive):
                new_obj = self.process_object(new_obj)
            
            result[new_key] = new_obj
        
        return result
    
    def process_list(self, obj: TList) -> TList:
        result = list()
        
        for new_obj in obj:
            if (self.recursive):
                new_obj = self.process_object(new_obj)
            
            result.append(new_obj)
        
        return result
    
    def process_object(self, obj: TArg) -> TArg:
        if (isinstance(obj, dict)):
            return self.process_dict(obj)
        if (isinstance(obj, list)):
            return self.process_list(obj)
        return obj
    
    def process(self, obj: TArg) -> TArg:
        if (not isinstance(obj, (str, dict, list))):
            raise ValueError("Argument must be either str, dict, or list; not '{}'".format(type(obj)))
        if (isinstance(obj, str)):
            return self.process_str(obj)
        else:
            return self.process_object(obj)

def dict_keys_underscore_to_camel_case(dict_object: TArg, recursive=False, leading_upper_if_not_private: bool = None) -> TArg:
    options = dict(leading_upper_if_not_private=leading_upper_if_not_private)
    options = dict(filter(lambda pair: pair[1] is not None, options.items()))
    processor = _ObjectProcessor(underscore_to_camel_case, recursive=recursive, **options)
    return processor.process(dict_object)

def dict_keys_camel_case_to_underscore(dict_object: TArg, recursive=False, leading_lower_is_private: bool = None, process_acronyms: bool = None) -> TArg:
    options = dict(leading_lower_is_private=leading_lower_is_private, process_acronyms=process_acronyms)
    options = dict(filter(lambda pair: pair[1] is not None, options.items()))
    processor = _ObjectProcessor(camel_case_to_underscore, recursive=recursive, **options)
    return processor.process(dict_object)
