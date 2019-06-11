import importlib
import inspect


__all__ = ['get_fqn', 'retrieve_object', 'IntrospectMixin', 'PythonRef']


class _NotFound:
    pass


def get_fqn(obj):
    if inspect.ismodule(obj):
        return obj.__name__
    elif inspect.isclass(obj) or inspect.isfunction(obj):
        return f"{obj.__module__}::{obj.__qualname__}"
    elif inspect.ismethod(obj):
        cls = obj.__self__.__class__
        return f"{cls.__module__}::{cls.__qualname__}.{obj.__func__.__name__}"
    elif inspect.ismethoddescriptor(obj):
        cls = obj.__objclass__
        return f"{cls.__module__}::{cls.__qualname__}.{obj.__name__}"

    # Instance of some class
    cls = obj.__class__

    return f"{cls.__module__}::{cls.__qualname__}"


def retrieve_object(fqn, default=None, package=None):
    module_path, *obj_path = fqn.split('::')

    try:
        module = importlib.import_module(module_path, package=package)
    except ModuleNotFoundError:
        caller_frame = inspect.stack(1)
        try:
            module = caller_frame.__module__
        finally:
            del caller_frame

    if not obj_path:
        return module

    obj_path = obj_path[0].split(".")

    obj = module

    for obj_name in obj_path:
        obj = getattr(obj, obj_name, _NotFound)
        if obj is _NotFound:
            break

    if obj is _NotFound:
        if default is None:
            raise AttributeError(f"Unable to locate the object corresponding to '{fqn}'")
        else:
            return default

    return obj


class IntrospectMixin:

    # Serialization helper
    @property
    def _kwargs(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    def deconstruct(self):
        # This should be enough for most objects that do not depend on other complex objects to rebuild themselves
        return get_fqn(self), self._kwargs

    @classmethod
    def construct(cls, configs):
        instance = cls.__new__(cls)
        for k, v in configs.items():
            setattr(instance, k, v)
        return instance


class PythonRef:

    def __init__(self, fqn):
        self._fqn = fqn

    @classmethod
    def from_python(cls, obj):
        return cls(fqn=get_fqn(obj))

    def to_python(self):
        return retrieve_object(self._fqn)

    @property
    def fqn(self):
        return self._fqn

    def __str__(self):
        return self.fqn
