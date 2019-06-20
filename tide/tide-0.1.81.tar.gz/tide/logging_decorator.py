import os
import datetime
import inspect
import json
import types
import config_source as Cs

DEBUG_SETTINGS = Cs.CONFIG_OBJECT["settings"]["debugging"]
DEBUG_KEYS = DEBUG_SETTINGS.keys()
LOG_FILENAME = DEBUG_SETTINGS["log_filename"]
LOG_TO_FILE = DEBUG_SETTINGS["log_to_file"]

try:
    os.remove(LOG_FILENAME)
except OSError:
    pass

def make_class_decorator(function_decorator):

    def class_decorator(cls):

        def is_function(attr_value):
            return hasattr(attr_value, '__call__') and isinstance(attr_value, types.FunctionType)

        if is_function(cls):
            return function_decorator(cls)

        for attr_name in dir(cls):
            attr_value = getattr(cls, attr_name)
            if is_function(attr_value):
                setattr(cls, attr_name, function_decorator(attr_value))

        return cls

    return class_decorator

@make_class_decorator
def logging(func):

    def wrapper(*args, **kwargs):

        def can_process_object():
            for debug_key in DEBUG_KEYS:
                if debug_key.startswith('debug_'):
                    temp_key = debug_key.replace('debug_', '')
                    debug_this_object = DEBUG_SETTINGS[debug_key]
                    if not debug_this_object and (temp_key.lower() == func.__module__.lower()):
                        return False
            return True

        def get_start_write_object():
            write_object = {}
            write_object["timestamp_utc"] = str(datetime.datetime.utcnow())
            write_object["func_point"] = "start"
            write_object["func_module"] = func.__module__
            write_object["func_object"] = str(func)
            write_object["func_signature"] = str(inspect.signature(func))
            if args:
                write_object["func_args"] = str(list(args))
            if kwargs:
                write_object["func_kwargs"] = str(kwargs)
            return write_object

        def get_end_write_object(func_result):
            write_object = {}
            write_object["timestamp_utc"] = str(datetime.datetime.utcnow())
            write_object["func_point"] = "end"
            write_object["func_module"] = func.__module__
            write_object["func_object"] = str(func)
            write_object["func_result"] = str(func_result)
            return write_object

        def write_to_log():
            start_write_object = get_start_write_object()
            func_result = func(*args, **kwargs)
            end_write_object = get_end_write_object(func_result)
            json_string = json.dumps(start_write_object)
            json_string += json.dumps(end_write_object)
            with open(LOG_FILENAME, 'a+') as file_handle:
                file_handle.write(json_string)
            return func_result

        if LOG_TO_FILE and can_process_object():
            return write_to_log()
        return func(*args, **kwargs)

    return wrapper
