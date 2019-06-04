from __future__ import absolute_import
from __future__ import unicode_literals
from threading import local
from contextlib import contextmanager
import six

class Bunch(dict):

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

class LazyProperty(object):

    def __init__(self, func):
        self._func = func
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__

    def __get__(self, obj, klass=None):
        if obj is None: return None
        result = obj.__dict__[self.__name__] = self._func(obj)
        return result

@contextmanager
def push_context(obj, **kw):
    '''Temporarily add attributes to 'obj', restoring 'obj' to its original
    state on __exit__
    '''
    new_keys = [ k for k in kw if not hasattr(obj, k) ]
    saved_items = [
        (k, getattr(obj, k)) for k in kw
        if hasattr(obj, k) ]
    for k,v in six.iteritems(kw):
        setattr(obj, k, v)
    yield obj
    for nk in new_keys:
        delattr(obj, nk)
    for k,v in saved_items:
        setattr(obj, k, v)

class NameListItem(object):
    '''An item that 'remembers' its order of instantiation within a thread'''
    _local = local()

    def __init__(self):
        self._ordinal = getattr(NameListItem._local, '_ordinal', 0)
        NameListItem._local._ordinal = self._ordinal + 1

class _NameListMeta(type):
    def __new__(meta, name, bases, dct):
        if bases == (list,):
            return type.__new__(meta, name, bases, dct)
        lst = []
        for k,v in six.iteritems(dct):
            if isinstance(v, NameListItem):
                if getattr(v, 'name') is None:
                    v.name = k
                lst.append(v)
        # Maintain declaration order
        lst.sort(key=lambda x:x._ordinal)
        return NameList(lst, dct)

class NameList(six.with_metaclass(_NameListMeta, list)):
    '''Simple class to let you create a list of widgets declaratively'''

    def __init__(self, iterator=None, index=None):
        if iterator is None: iterator = []
        super(NameList, self).__init__(iterator)
        if index is None:
            index = dict(
                (v.name, v) for v in self
                if hasattr(v, 'name'))
        self._index = index

    def __getitem__(self, index):
        if isinstance(index, six.string_types):
            return self._index[index]
        return super(NameList, self).__getitem__(index)

    def __getattr__(self, name):
        try:
            return self._index[name]
        except KeyError:
            raise AttributeError(name)

    def append(self, item):
        if hasattr(item, 'name'):
            self._index[item.name] = item
        super(NameList, self).append(item)

class NoDefault(tuple): pass

def Instance(cls):
    '''Crazy metaclass magic to create a named instance of a class with kwargs
    defined by the class dict. Use like this:

    >>> from ew import Instance
    >>> class foo(Instance(dict)):
    ...     a=5
    ...     b=6
    ... 
    >>> foo
    {'a': 5, 'b': 6, 'name': 'foo'}

    Yeah. I know.
    '''
    class _Instance(object):
        class __metaclass__(type):
            def __new__(meta, name, bases, dct):
                if name == '_Instance':
                    return type.__new__(meta, name, bases, dct)
                else:
                    dct.pop('__module__', None)
                    return cls(name=name, **dct)
    return _Instance
        
def safe_getitem(dct, key, item):
    '''Return either dct[key][item],  dct[key].item, or None, whichever
    is appropriate
    '''
    if key not in dct: return None
    value = dct[key]
    try:
        result = value[item]
    except TypeError:
        if isinstance(item, str):
            result = getattr(value, item, None)
        else:
            result = None
    except (KeyError, IndexError) as ex:
        result = None
    return result



