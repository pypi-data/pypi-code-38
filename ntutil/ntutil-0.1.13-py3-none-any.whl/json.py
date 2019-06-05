#!/usr/bin/env python3
#-*- coding: utf-8 -*-

'''
JSON
----

Author:

* Rony Novianto (rony@novianto.tech)

Copyright © Novianto.tech
'''

import json, os

def load_file(filename, *args, on_error=None, **kwargs):
    expanded = os.path.expandvars(filename)
    with open(expanded) as f:
        try:
            return json.load(f, *args, **kwargs)
        except json.decoder.JSONDecodeError as error:
            if on_error:
                on_error(expanded, error)
            else:
                raise
                
def load_files(filenames, *args, on_error=None, **kwargs):
    merged_data = {}
    for filename in filenames:
        unmerged_data = load_file(filename, *args, on_error=on_error, **kwargs) or {}
        merged_data.update(unmerged_data)
    return merged_data
    
    
class JSON(object):
    def load_file(self, filename, *args, on_error=None, **kwargs):
        return load_file(filename, *args, on_error=on_error, **kwargs)
        
    def load_files(self, filenames, *args, on_error=None, **kwargs):
        return load_files(filenames, *args, on_error=on_error, **kwargs)