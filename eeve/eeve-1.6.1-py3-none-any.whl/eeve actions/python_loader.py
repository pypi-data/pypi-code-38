import importlib
from eeve.variable import Variable


def load_script(var, script_path):
    # TODO: get script path and add to path environment variable
    script_name = script_path
    mod = importlib.import_module(script_name)
    if type(var) is Variable:
        var.value = mod
    else:
        return {var: mod}


def call_func(script_ref, func_name, *args, **kwargs):
    return {'result': getattr(script_ref, func_name)(*args, **kwargs)}


actions = {'load script': {'run': load_script}, 'call function': {'run': call_func}}
