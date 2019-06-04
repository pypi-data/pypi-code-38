# coding: utf-8
 
# The MIT License (MIT)

# Copyright (c) «2015-2019» «Shibzukhov Zaur, szport at gmail dot com»

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software - recordclass library - and associated documentation files 
# (the "Software"), to deal in the Software without restriction, including 
# without limitation the rights to use, copy, modify, merge, publish, distribute, 
# sublicense, and/or sell copies of the Software, and to permit persons to whom 
# the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from .dataobject import dataobject, datatuple, dataslotgetset, astuple
from .dataobject import enable_gc, _dataobject_type_init
from .dataobject import _add_dict, _set_hashable, _set_iterable, _add_weakref, _collection_protocol

from .utils import make_new_function, check_names, dataslot_offset, dataitem_offset
from .utils import fields_from_bases, defaults_from_bases, annotations_from_bases

import sys as _sys
_PY3 = _sys.version_info[0] >= 3
_PY36 = _PY3 and _sys.version_info[1] >= 6

if _PY3:
    _intern = _sys.intern
    if _PY36:
        from typing import _type_check
    else:
        def _type_check(t, msg):
            if isinstance(t, (type, str)):
                return t
            else:
                raise TypeError('invalid type annotation', t)    
else:
    from __builtin__ import intern as _intern
    def _type_check(t, msg):
        return t
    
__all__ = ('datatype', 'make_class', 'make_dataclass', 'make_arrayclass', 'asdict',
           'collection_protocol', 'add_dict', 'add_weakref', 'hashable', 'enable_gc')

int_type = type(1)

def collection_protocol(sequence=False, mapping=False, readonly=False):
    def func(cls, sequence=sequence, mapping=mapping, readonly=readonly):
        _collection_protocol(cls, sequence, mapping, readonly)
        return cls
    return func

def add_dict(state=True):
    def func(cls, state=state):
        _add_dict(cls, state)
        return cls
    return func

def hashable(state=True):
    def func(cls, state=state):
        _set_hashable(cls, state)
        return cls
    return func

def iterable(state=True):
    def func(cls, state=state):
        _set_iterable(cls, state)
        return cls
    return func

def add_weakref(state=True):
    def func(cls, state=state):
        _add_weakref(cls, state)
        return cls
    return func

def make_dataclass(typename, fields=None, bases=None, namespace=None, 
                   varsize=False,  use_dict=False, use_weakref=False, hashable=True,
                   sequence=False, mapping=False, iterable=False, readonly=False, gc=False,
                   defaults=None, module=None, argsonly=False):

    annotations = {}
    if isinstance(fields, str):
        fields = fields.replace(',', ' ').split()
    else:
        msg = "new_datatype('Name', [(f0, t0), (f1, t1), ...]); each t must be a type"
        field_names = []
        if isinstance(fields, dict):
            for fn, tp in fields.items():
                tp = _type_check(tp, msg)
                annotations[fn] = tp
                field_names.append(fn)
        else:
            for fn in fields:
                if type(fn) is tuple:
                    fn, tp = fn
                    tp = _type_check(tp, msg)
                    annotations[fn] = tp
                field_names.append(fn)
        fields = field_names

    typename, fields = check_names(typename, fields)

    if defaults is not None:
        n_fields = len(fields)
        defaults = tuple(defaults)
        n_defaults = len(defaults)
        if n_defaults > n_fields:
            raise TypeError('Got more default values than fields')
    else:
        defaults = None

    options = {
        'dict':use_dict, 'weakref':use_weakref,
        'hashable':hashable, 'varsize':varsize,
        'sequence':sequence, 'mapping':mapping, 'iterable':iterable, 'readonly':readonly,
        'defaults':defaults, 'argsonly':argsonly,
    }

    if namespace is None:
        ns = {}
    else:
        ns = namespace

    if defaults:
        for i in range(-n_defaults, 0):
            fname = fields[i]
            val = defaults[i]
            ns[fname] = val

    ns['__options__'] = options
    ns['__fields__'] = fields
    if annotations:
        ns['__annotations__'] = annotations

    cls = datatype(typename, bases, ns)

    if gc:
        cls = enable_gc(cls)

    if module is None:
        try:
            module = _sys._getframe(1).f_globals.get('__name__', '__main__')
        except (AttributeError, ValueError):
            module = None
    if module is not None:
        cls.__module__ = module

    return cls

make_class = make_dataclass

def make_arrayclass(typename, fields=0, bases=None, namespace=None, 
                 varsize=False, use_dict=False, use_weakref=False, hashable=False,
                 readonly=False, gc=False,
                 module=None):

    if not isinstance(fields, int_type):
        raise TypeError("argument fields is not integer")

    options = {
        'dict':use_dict, 'weakref':use_weakref, 'hashable':hashable, 
        'sequence':True, 'iterable':True, 'readonly':readonly, 
        'varsize':varsize, 
    }

    if namespace is None:
        ns = {}
    else:
        ns = namespace

    ns['__options__'] = options
    ns['__fields__'] = fields

    cls = datatype(typename, bases, ns)

    if gc:
        cls = enable_gc(cls)

    if module is None:
        try:
            module = _sys._getframe(1).f_globals.get('__name__', '__main__')
        except (AttributeError, ValueError):
            module = None
    if module is not None:
        cls.__module__ = module

    return cls

class datatype(type):

    def __new__(metatype, typename, bases, ns):        

        options = ns.pop('__options__', {})
        readonly = options.get('readonly', False)
        hashable = options.get('hashable', False)
        sequence = options.get('sequence', False)
        mapping = options.get('mapping', False)
        iterable = options.get('iterable', False)
        varsize = options.get('varsize', False)
        argsonly = options.get('argsonly', False)
        use_dict = options.get('dict', False)
        use_weakref = options.get('weakref', False)

        if not bases:
            if varsize:
                bases = (datatuple,)
            else:
                bases = (dataobject,)

        if issubclass(bases[0], datatuple):
            varsize = True
        elif issubclass(bases[0], dataobject):
            varsize = False
        else:
            raise TypeError("First base class should be instance of dataobject or datatuple")

        annotations = ns.get('__annotations__', {})

        if '__fields__' in ns:
            fields = ns.pop('__fields__')
        else:
            fields = [name for name in annotations]

        has_fields = True
        if isinstance(fields, int_type):
            has_fields = False
            n_fields = fields
            sequence = True
            iterable = True
        else:
            fields = list(fields)

        if varsize:
            sequence = True
            iterable = True
            
        if sequence or mapping:
            iterable = True

        if has_fields:
#             typename, fields = check_names(typename, fields)
            if annotations:
                annotations = {fn:annotations[fn] for fn in fields if fn in annotations}

            if '__dict__' in fields:
                fields.remove('__dict__')
                use_dict = True

            if '__weakref__' in fields:
                fields.remove('__weakref__')
                use_weakref = True

            n_fields = len(fields)

            _fields = fields_from_bases(bases)
            _annotations = annotations_from_bases(bases)
            _defaults = defaults_from_bases(bases)

            defaults = {f:ns[f] for f in fields if f in ns}

            if fields:
                fields = [f for f in fields if f not in _fields]
                n_fields = len(fields)
            fields = _fields + fields
            n_fields += len(_fields)

            _defaults.update(defaults)
            defaults = _defaults

            _annotations.update(annotations)
            annotations = _annotations

            fields = tuple(fields)

            if fields and (not argsonly or defaults) and '__new__' not in ns:
                if fields and defaults:
                    fields2 = [f for f in fields if f not in defaults] + [f for f in fields if f in defaults]
                else:
                    fields2 = fields
                fields2 = tuple(fields2)

                __new__ = make_new_function(typename, fields, fields2, varsize, use_dict)

                if defaults:
                    default_vals = tuple(defaults[f] for f in fields2 if f in defaults)
                    __new__.__defaults__ = default_vals
                if annotations:
                    __new__.__annotations__ = annotations

                ns['__new__'] = __new__

        cls = type.__new__(metatype, typename, bases, ns)

        if fields:
            cls.__fields__ = fields
        if has_fields:
            if defaults:
                cls.__defaults__ = defaults
            if annotations:
                cls.__annotations__ = annotations

        _dataobject_type_init(cls, n_fields, varsize, has_fields)
        _collection_protocol(cls, sequence, mapping, readonly)
        _set_iterable(cls, iterable)
        _add_dict(cls, use_dict)
        _add_weakref(cls, use_weakref)
        _set_hashable(cls, hashable)

        if has_fields:
            if readonly is None or type(readonly) is bool:
                if readonly:
                    readonly_fields = set(fields)
                else:
                    readonly_fields = set()
            else:
                readonly_fields = set(readonly)

            for i, name in enumerate(fields):
                if name in readonly_fields:
                    setattr(cls, name, dataslotgetset(dataslot_offset(cls, i), True))
                else:
                    setattr(cls, name, dataslotgetset(dataslot_offset(cls, i)))

        return cls

def asdict(ob):
    _getattr = getattr
    return {fn:_getattr(ob, fn) for fn in ob.__class__.__fields__}

class DataclassStorage:
    #
    def __init__(self):
        self._storage = {}
    #
    def make_dataclass(self, name, fields):
        fields = tuple(fields)
        key = (name, fields)
        cls = self._storage.get(key, None)
        if cls is None:
            cls = make_dataclass(name, fields)
            self._storage[key] = cls
        return cls
    make_class = make_dataclass

from .dataobject import _fix_type
_fix_type(dataobject, datatype)
_fix_type(datatuple, datatype)
del _fix_type
