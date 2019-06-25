import collections

def request_handler(func):
    func.is_request_handler = True
    return func

def get_request_handlers(cls, name_only=False):
    request_handlers = []
    for name in cls.__dict__.keys():
        if hasattr(cls.__dict__[name], "is_request_handler"):
            if name_only:
                request_handlers.append(name)
            else:
                request_handlers.append((name, cls.__dict__[name]))
    return request_handlers


class HyperParameterConfig():

    def __init__(self, config=None, callback_generate_next_config_list=None):
        self._config = config
        self._callback = callback_generate_next_config_list
        
    def get_config(self):
        return self._config

    def get_next_config(self, train_result_dict):
        if self._callback is None:
            return None
        else:
            return self._callback(self._config, train_result_dict)

class HyperParameterTuner():

    def __init__(self):
        pass

    def get_hyper_parameter_config_list(self):
        return None
        
    def get_key_func_for_max_scores(self):
        return None
        
class Service():

    def __init__(self):
        pass


def make_func_args(args_tuple):
    args = []
    kwargs = {}
    i = 0
    while i < len(args_tuple):
        if args_tuple[i][0] == ':' and i is not len(args_tuple):
            kwargs[args_tuple[i][1:]] = args_tuple[i+1]
            i += 1
        else:
            args.append(args_tuple[i])
        i += 1
    return args, kwargs
        
def recur_getattr(obj, obj_name_list):
    if len(obj_name_list) == 0:
        return None
    attr = getattr(obj, obj_name_list[0])
    if len(obj_name_list) == 1:
        return attr
    return recur_getattr(attr, obj_name_list[1])

class Model():

    def __init__(self):
        pass

    # multiple update function?
    def update(self):
        pass
    
    def train(self):
        pass

    def test(self):
        pass
    
    def commit(self):
        pass


    def run_ordered_dict_as_procedure(self, ordered_dict, more_args_dict={}):

        for key  in ordered_dict:
            func_name = key
            args_tuple = ordered_dict[key]
            args, kwargs = make_func_args(args_tuple)
            try:
                if type(more_args_dict[func_name]) == dict:
                    kwargs = {**more_args_dict[func_name], **kwargs}
                elif type(more_args_dict[func_name]) == list:
                    args = args + more_args_dict[func_name]
            except KeyError:
                pass
            obj_name_list = func_name.split('.')
            obj = eval(obj_name_list[0])
            if len(obj_name_list) >= 2:
                func = recur_getattr(obj, obj_name_list[1:])
            else:
                func = obj
            func(*args, **kwargs)

class Data():

    def __init__(self):
        pass

        
