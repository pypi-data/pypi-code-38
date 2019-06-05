#!/usr/bin/env python3
#-*- coding: utf-8 -*-

'''
Dictionary
----------

Author:

* Rony Novianto (rony@novianto.tech)

Copyright © Novianto.tech
'''

def get_from_keys(dict_object, keys, default=None):
    return [dict_object.get(key, default) for key in keys]
    
def get_from_nested_key(dict_object, nested_key, default=None):
    pointer = dict_object
    for current_key in nested_key:
        if isinstance(pointer, dict) and current_key in pointer:
            pointer = pointer[current_key]
        else:
            pointer = default
            break
    return pointer
    
def get_from_concatenated_key(dict_object, uri, separator='/', default=None):
    stripped = uri.strip(separator)
    if not stripped: return dict_object
    keys = stripped.split(separator)
    pointer = dict_object
    for key in keys:
        if isinstance(pointer, dict) and key in pointer:
            pointer = pointer[key]
        else:
            pointer = default
            break
    return pointer
    
def set_with_concatenated_key(dict_object, uri, value, separator='/'):
    stripped = uri.strip(separator)
    if not stripped: return
    keys = stripped.split(separator)
    last_index = len(keys) - 1
    pointer = dict_object
    for (current_index, key) in enumerate(keys):
        if current_index >= last_index:
            pointer[key] = value
        else:
            if key not in pointer: pointer[key] = {}
            pointer = pointer[key]
            
def nested_update(a, b):
    for (key, value) in b.items():
        if isinstance(value, dict):
            current = a.get(key, {})
            a[key] = nested_update(current, value)
        else:
            a[key] = value
    return a
    
def append(a, b):
    for (key, value) in b.items():
        if isinstance(value, dict):
            current = a.get(key, {})
            a[key] = append(current, value)
        elif key not in a:
            a[key] = value
    return a
    
    
class Dict(dict):
    def get_from_keys(self, keys, default=None):
        return get_from_keys(self, keys, default=default)
        
    def get_from_nested_key(self, nested_key, default=None):
        return get_from_nested_key(self, nested_key, default=default)
        
    def get_from_concatenated_key(self, uri, separator='/', default=None):
        return get_from_concatenated_key(self, uri, separator=separator, default=default)
        
    def set_with_concatenated_key(self, uri, value, separator='/'):
        return set_with_concatenated_key(self, uri, value, separator=separator)
        
    def nested_update(self, dict_object):
        return nested_update(self, dict_object)
        
    def append(self, dict_object):
        return append(self, dict_object)
        
        
class AttributeDict(dict):
    def __init__(self, key_values):
        if isinstance(key_values, dict):
            key_values = key_values.items()
        for (key, value) in key_values:
            self.__setitem__(key, value)
            
    def __setitem__(self, key, value):
        if isinstance(value, dict):
            value = AttributeDict(value)
        super().__setitem__(key, value)
        
    __getattr__ = dict.__getitem__
    __setattr__ = __setitem__
    __delattr__ = dict.__delitem__