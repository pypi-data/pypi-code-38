"""
Copyright (c) 2019, Matt Pewsey
"""

from functools import wraps
from weakref import WeakKeyDictionary

__all__ = [
    'Collector',
    'collect',
    'fcollect',
]


class Collector(object):
    """
    A context manager for initiating value collection. When the context manager
    closes, the class dictionaries used for value collection will be set
    to empty values rather than being cleared. Therefore, if you have an active
    variable pointed to any of the dictionaries, those dictionaries will
    still be available outside of the context manager until your pointer
    falls out of scope.

    Examples
    --------
    Class method collection:
    .. literalinclude:: ../../examples/collector_ex1.py

    Function collection:
    .. literalinclude:: ../../examples/collector_ex2.py
    """
    CLASS_DICT = WeakKeyDictionary()
    FUNC_DICT = {}
    IS_ACTIVE = False

    @classmethod
    def __enter__(cls):
        """
        Activates collection on decorated functions and methods. If collection
        is already active, raises an exception.
        """
        if cls.IS_ACTIVE:
            raise ValueError('Collector is already active.')

        cls.IS_ACTIVE = True
        return cls

    @classmethod
    def __exit__(cls, type, value, traceback):
        """
        Deactivates collection and sets the collection dictionaries to empty
        values.
        """
        cls.IS_ACTIVE = False
        cls.CLASS_DICT = WeakKeyDictionary()
        cls.FUNC_DICT = {}

        return False

    @classmethod
    def set_fdict(cls, func, value):
        """
        If collection is active, adds the value to the function dictionary.

        Parameters
        ----------
        func : function
            The function to which the value corresponds.
        value
            The result of the method.
        """
        if cls.IS_ACTIVE:
            func = '{}.{}'.format(func.__module__, func.__name__)
            cls.FUNC_DICT[func] = value

    @classmethod
    def set_dict(cls, obj, func, value):
        """
        If collection is active, adds the value to the class dictionary.

        Parameters
        ----------
        obj : object
            The object under which the values will be stored.
        func : method
            The object method to which the value corresponds.
        value
            The result of the method.
        """
        if cls.IS_ACTIVE:
            odict = cls.CLASS_DICT

            if obj not in odict:
                odict[obj] = {}

            odict[obj][func.__name__] = value

    @classmethod
    def get_fdict(cls):
        """
        Returns the function dictionary.
        """
        return cls.FUNC_DICT

    @classmethod
    def get_dict(cls):
        """
        Returns the class dictionary.
        """
        return cls.CLASS_DICT

    @classmethod
    def fget(cls, obj, *default):
        """
        Returns the value contained in the function dictionary.

        Parameters
        ----------
        obj : function
            The function to acquire the value for.
        default
            The default value to return if the function is not found.
        """
        odict = cls.FUNC_DICT
        obj = '{}.{}'.format(obj.__module__, obj.__name__)

        if obj in odict:
            return odict[obj]
        elif default:
            return default[0]
        else:
            raise KeyError('Key {!r} does not exist.'.format(obj))

    @classmethod
    def get(cls, obj, *default):
        """
        Returns the value contained in the class dictoinary.

        Parameters
        ----------
        obj : object
            The object to acquire values for.
        default
            The default value to return if the object is not found.
        """
        odict = cls.CLASS_DICT

        if obj in odict:
            return odict[obj]
        elif default:
            return default[0]
        else:
            raise KeyError('Key {!r} does not exist.'.format(obj))


def collect(func):
    """
    A decorator that collects values returned by class methods if the
    :class:`.Collector` context manager is active.

    Examples
    --------
    .. literalinclude:: ../../examples/collector_ex1.py
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        value = func(self, *args, **kwargs)
        Collector.set_dict(self, func, value)
        return value
    return wrapper


def fcollect(func):
    """
    A decorator that collects values returned by functions if the
    :class:`.Collector` context manager is active.

    Examples
    --------
    .. literalinclude:: ../../examples/collector_ex2.py
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        value = func(*args, **kwargs)
        Collector.set_fdict(func, value)
        return value
    return wrapper
