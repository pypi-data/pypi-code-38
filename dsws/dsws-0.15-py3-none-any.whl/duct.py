"""
Data Science Work Space - Duct

Duct provides a single class oject that is intended to consolidate
all analytical source data connection patterns.
'duct' was deliberately chosen to consolidate the collection of connection
components, but avoid names like pipe, connection, stream to avoid naming
confusion as well as to not limit the types of work space components included

To use duct:

```python
from dsws.duct import Duct
duct_conf = {'hive': {'class': 'ws_impyla',
                      'magic_handle': 'hive',
                      'kwargs': {'host': 'node01.ratiocinate.com',
                                 'port': 10000,
                                 'auth_mechanism': 'PLAIN'},
                      'command': 'beeline -u "jdbc:hive2://node01.ratiocinate.com:10000"'}
duct = Duct(duct_conf)
```
"""

import os
from os                 import environ
from pydoc              import locate
from IPython.core.magic import register_line_cell_magic
from dsws.util          import sp
from IPython.display    import HTML
from dsws.util          import launch_term

def get_cls(ws_str):
    """
    get_cls - helper function to return the primary class
    object within a dsws submodule. Requires two nameing 
    conventions to be true of the submodule:
     - The module is lower_case with the second '_' split
     matching the name of the class
     - The class name is capitalized
    """
    cap=ws_str.split("_")[1].capitalize()
    return locate('.'.join(['dsws',ws_str,cap]))

def register_magic(handle,cls):
    """
    register_magic - helper function that standardizes
    classes registered magics with the follwoing 
    conventions:
     - An unargumented magic launches a cli session
     - An argumented magic accepts sql and returns
     a display of results. Intended for very concise
     iterations or summary results.
    """
    @register_line_cell_magic(handle)
    def tmp(line='', cell=''):
        qry=str('\n'.join([line,cell]).strip())
        if qry=='':
            launch_term(cls.command)
        else: 
            cls.qry(qry, "disp")
    del tmp
    
class Duct:
    """
    Duct - A class that holds workspaces defined within duct_conf.

    During instantiation the wrokspaces are defined as well as 
    magics are created according to dsws conventions:
     - An unargumented magic launches a cli session
     - An argumented magic accepts sql and returns
     a display of results. Intended for very concise
     iterations or summary results.
    """
    def __init__(self,duct_conf={}):
        for k,v in duct_conf.items():
            kwargs={j:w for j,w in v.items() if j in ('kwargs','command')}
            setattr(self, k, get_cls(v["class"])(**kwargs))
            if 'magic_handle' in v.keys():
                register_magic(v['magic_handle'],getattr(self, k))
