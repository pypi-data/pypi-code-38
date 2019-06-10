from . import _hext

try:
    _swig_property = property
except NameError:
    pass  # Python < 2.2 doesn't have 'property'.

try:
    import builtins as __builtin__
except ImportError:
    import __builtin__

def _swig_setattr_nondynamic(self, class_type, name, value, static=1):
    if (name == "thisown"):
        return self.this.own(value)
    if (name == "this"):
        if type(value).__name__ == 'SwigPyObject':
            self.__dict__[name] = value
            return
    method = class_type.__swig_setmethods__.get(name, None)
    if method:
        return method(self, value)
    if (not static):
        if _newclass:
            object.__setattr__(self, name, value)
        else:
            self.__dict__[name] = value
    else:
        raise AttributeError("You cannot add attributes to %s" % self)


def _swig_setattr(self, class_type, name, value):
    return _swig_setattr_nondynamic(self, class_type, name, value, 0)


def _swig_getattr(self, class_type, name):
    if (name == "thisown"):
        return self.this.own()
    method = class_type.__swig_getmethods__.get(name, None)
    if method:
        return method(self)
    raise AttributeError("'%s' object has no attribute '%s'" % (class_type.__name__, name))


def _swig_repr(self):
    try:
        strthis = "proxy of " + self.this.__repr__()
    except __builtin__.Exception:
        strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis,)

try:
    _object = object
    _newclass = 1
except __builtin__.Exception:
    class _object:
        pass
    _newclass = 0

class SwigPyIterator(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, SwigPyIterator, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, SwigPyIterator, name)

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined - class is abstract")
    __repr__ = _swig_repr
    __swig_destroy__ = _hext.delete_SwigPyIterator
    __del__ = lambda self: None

    def value(self):
        return _hext.SwigPyIterator_value(self)

    def incr(self, n=1):
        return _hext.SwigPyIterator_incr(self, n)

    def decr(self, n=1):
        return _hext.SwigPyIterator_decr(self, n)

    def distance(self, x):
        return _hext.SwigPyIterator_distance(self, x)

    def equal(self, x):
        return _hext.SwigPyIterator_equal(self, x)

    def copy(self):
        return _hext.SwigPyIterator_copy(self)

    def next(self):
        return _hext.SwigPyIterator_next(self)

    def __next__(self):
        return _hext.SwigPyIterator___next__(self)

    def previous(self):
        return _hext.SwigPyIterator_previous(self)

    def advance(self, n):
        return _hext.SwigPyIterator_advance(self, n)

    def __eq__(self, x):
        return _hext.SwigPyIterator___eq__(self, x)

    def __ne__(self, x):
        return _hext.SwigPyIterator___ne__(self, x)

    def __iadd__(self, n):
        return _hext.SwigPyIterator___iadd__(self, n)

    def __isub__(self, n):
        return _hext.SwigPyIterator___isub__(self, n)

    def __add__(self, n):
        return _hext.SwigPyIterator___add__(self, n)

    def __sub__(self, *args):
        return _hext.SwigPyIterator___sub__(self, *args)
    def __iter__(self):
        return self
SwigPyIterator_swigregister = _hext.SwigPyIterator_swigregister
SwigPyIterator_swigregister(SwigPyIterator)

class Html(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, Html, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, Html, name)
    __repr__ = _swig_repr

    def __init__(self, html):
        this = _hext.new_Html(html)
        try:
            self.this.append(this)
        except __builtin__.Exception:
            self.this = this
    __swig_destroy__ = _hext.delete_Html
    __del__ = lambda self: None
Html_swigregister = _hext.Html_swigregister
Html_swigregister(Html)

class Rule(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, Rule, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, Rule, name)
    __repr__ = _swig_repr

    def __init__(self, hext):
        this = _hext.new_Rule(hext)
        try:
            self.this.append(this)
        except __builtin__.Exception:
            self.this = this

    def extract(self, html):
        return _hext.Rule_extract(self, html)
    __swig_destroy__ = _hext.delete_Rule
    __del__ = lambda self: None
Rule_swigregister = _hext.Rule_swigregister
Rule_swigregister(Rule)

# This file is compatible with both classic and new-style classes.


