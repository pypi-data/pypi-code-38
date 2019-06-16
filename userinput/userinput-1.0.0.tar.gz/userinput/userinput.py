from typing import Callable, Union, List
import json
import os
from inspect import isfunction
from .utils import default_validators, closest

def normalize_validators(validator:str)->List[Callable]:
    if validator not in default_validators:
        candidate = closest(validator, default_validators.keys())
        if candidate is None:
            raise ValueError("Given validator callback {validator} is not available.".format(validator=validator))
        raise ValueError("Given validator callback {validator} is invalid, did you mean {candidate}?.".format(
            validator=validator,
            candidate=candidate
        ))
    return default_validators.get(validator)

def userinput(
    name:str, 
    label:str="Please insert {name}",
    default=None,
    always_use_default:bool=False,
    validator:Union[Callable, List[Callable], List[Union[Callable, str]], str, List[str]]=None,
    maximum_attempts:int=None,
    sanitizer:Callable=None,
    cache:bool=True,
    cache_path:str=".userinput")->str:
    defaults = {}
    if cache and os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            defaults = json.load(f)
            default = defaults.get(name, default)
    if isinstance(validator, str) or isfunction(validator):
        validators = [validator]
    else:
        validators = []
    validators = [
        normalize_validators(validator) if isinstance(validator, str) else validator for validator in validators
    ]
    attempts = 0
    while maximum_attempts is None or attempts<maximum_attempts:
        value = None
        if not always_use_default:
            value = input("{label}{default}: ".format(
                label=label.format(name=name),
                default="" if default is None else " [{default}]".format(default=default)
            )).strip()
        if not value:
            value = default
        if not validators or all([v(value) for v in validators]):
            if cache:
                with open(cache_path, "w") as f:
                    defaults[name] = value
                    json.dump(defaults, f)
            return value if sanitizer is None else sanitizer(value)
        attempts+=1
        print("Given value {value} is not valid.".format(value=value))