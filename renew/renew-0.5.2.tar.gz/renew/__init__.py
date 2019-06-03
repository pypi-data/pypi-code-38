import itertools

import six

from . import _mold, _py_lang, _serializer
from ._py_lang import build_py_file_content
from ._serializer import PyStorage, Label, Reference, LiveLabel, LiveReference

__all__ = [
    "Label",
    "LiveLabel",
    "LiveReference",
    "Mold",
    "PyStorage",
    "Reference",
    "build_py_file_content",
    "reproduction",
    "serialize",
    "serialize_in_order",
]


class Mold(six.with_metaclass(_mold.MoldMeta, object)):
    __slots__ = ()
    _cls_fields = ()
    _extra_slots = ()  # define extra fields that are not handled as _cls_fields
    _cls_make_slots = True  # whens set to False - no __slots__ will be made
    _cls_dependency = None
    _cls_namespace = None

    def __repr__(self):
        try:
            return "".join(self.dispatch_repr(None))
        except Exception:
            return object.__repr__(self)

    def dispatch_repr(self, dep_list, references=None):
        references = references or {}
        dependency = self.make_py_import()
        if isinstance(dep_list, list) and dependency not in dep_list:
            dep_list.append(dependency)

        if hasattr(self, "_cls_constructor_spec"):
            params = list(self._cls_constructor_spec.cls_arguments(self))
            items_reprs = [(kw, list(_py_lang.dispatch_repr(value, dep_list, is_last_item=last, references=references)))
                           for (kw, value), last in _py_lang.mark_last(params)]
            for element in _py_lang.make_a_markup("%s(" % self.make_py_reference, items_reprs, ")"):
                yield element
        else:
            # constructor undefined yet
            yield "%s()" % self.make_py_reference

    def __hash__(self):
        """ This makes two equal instances of same type getting the same hash value. """
        return hash(repr(self))

    def __eq__(self, other):
        if self.__class__.__name__ == type(other).__name__:
            if isinstance(other, self.__class__) and self._cls_fields == other._cls_fields:
                return all(getattr(self, f) == getattr(other, f) for f in self._cls_fields)
        return NotImplemented

    def __ne__(self, other):
        """ it's not needed in py3 however we would like to make work also for dinosaurs from py2 era """
        are_equal = self.__eq__(other)
        if are_equal is not NotImplemented:
            return not are_equal
        return NotImplemented

    def __iter__(self):
        return (getattr(self, f) for f in self._cls_fields)

    @property
    def make_py_reference(self):
        cls_name = self.__class__.__name__
        namespace = self._get_str_or_none_or_raise("_cls_namespace")
        if namespace and isinstance(namespace, six.string_types):
            return "%s.%s" % (namespace, cls_name)
        return cls_name

    def make_py_import(self):
        namespace = self._get_str_or_none_or_raise("_cls_namespace")
        dependency = self._get_str_or_none_or_raise("_cls_dependency")

        if dependency is None:
            if namespace is None:
                dependency = self.__class__.__module__

        elif not isinstance(dependency, six.string_types) or dependency == "":
            msg = "Expecting _cls_dependency attribute to be None or nonempty string, got: '{}'"
            raise ValueError(msg.format(type(namespace).__name__))
        if namespace is None:
            # from <dependency or module> import ClassName
            return (dependency or self.__class__.__module__), self.__class__.__name__
        elif namespace and isinstance(namespace, six.string_types):
            # from <dependency> import <namespace>
            # or if _cls_dependency is unspecified:
            # import <namespace>
            return dependency, namespace

        msg = "Expecting _cls_namespace attribute to be None or nonempty string, got: '{}'"
        raise ValueError(msg.format(type(namespace).__name__))


def reproduction(single_object):
    """
    Tries to return a reproducible repr for given object_
    Falls back to native repr, so the reproducibility is not guaranteed.
    """
    return "".join(_py_lang.dispatch_repr(single_object, None, top_level=True, is_last_item=True))


def serialize(output_file_path, *ordered_name_value_pairs, **kw_objects):
    """
    Dumps objects into a python file.
    Objects are ordered alphabetically to make it able to be handled by VCSs.
    """
    all_objects = itertools.chain(ordered_name_value_pairs, sorted(kw_objects.items()))
    return serialize_in_order(output_file_path, *all_objects)


def serialize_in_order(output_file_path, *ordered_name_value_pairs):
    """
    Keep order of serialized values if it matters for you.
    Instead of using kw-arguments, call it with name-value tuples, e.g.:
    serialize_in_order(output_file_path, ('name_1', 'value_1'), ('name_2', 'value_2'))
    """
    content = build_py_file_content(ordered_name_value_pairs)
    _serializer.write_file(output_file_path, content)
