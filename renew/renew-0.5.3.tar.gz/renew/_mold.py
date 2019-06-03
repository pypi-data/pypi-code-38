from collections import OrderedDict

import six

from . import _inspection


class MoldMeta(type):
    """
    The purpose is to:
    #. check constructor interface and detect if a new slot would be required
    #. update list of all fields (slots) used for comparing and unpacking
    #. automatically assign class' __slots__ if new ones appear in given constructor interface
    (need to know what's already been defined to avoid duplications, order doesn't matter)
    #. collect constructor interface to be able to generate its calls that match its argument's spec
    """

    def __new__(mcs, name, bases, cls_dict):
        """ The __new__ method it most probably the only place to define class' __slots__.
        Everything that happen here is just to do that
        """
        constructor = cls_dict.get("__init__")
        extra_slots = _tuplize(cls_dict.get("_extra_slots", ()))
        make_slots_setting = cls_dict.get("_cls_make_slots", next(_get_inherited_auto_slots_setting(bases), None))
        props = set(_get_inherited_properties(bases))
        props.update(name for name, value in cls_dict.items() if isinstance(value, property))

        if not all(isinstance(s, six.string_types) for s in extra_slots):
            raise TypeError("Expecting _extra_slots to be a single string or a tuple containing strings only.")

        if constructor:
            constructor_parameters = _inspection.ArgsInspect.from_callable(constructor)
            cls_dict['_cls_constructor_spec'] = constructor_parameters
            if make_slots_setting:
                slots_candidates = ("_" + f if f in props else f for f in constructor_parameters)
                slots = tuple(field for field in slots_candidates if field not in set(_get_inherited_slots(bases)))
                cls_dict['__slots__'] = slots + extra_slots
        elif make_slots_setting:
            cls_dict['__slots__'] = () + extra_slots

        return type.__new__(mcs, name, bases, cls_dict)

    def __init__(cls, name, bases, cls_dict):
        """ In order to use reliable MRO rest of init is done here instead of __new__. """
        inherited_fields = _unique_in_order(f for base in cls.__mro__ for f in getattr(base, "_cls_fields", ()))
        extra_fields = set(_get_ignored_slots(cls, cls_dict))

        props_slots = {"_" + name: name for name, value in cls_dict.items() if isinstance(value, property)}
        new_fields = _unique_in_order(
            props_slots.get(slot, slot) for slot in getattr(cls, "__slots__", ())
            if slot not in inherited_fields and slot not in extra_fields
        )
        cls._cls_fields = new_fields + inherited_fields

        _get_str_or_none_or_raise(cls, "_cls_dependency")
        _get_str_or_none_or_raise(cls, "_cls_namespace")
        cls._get_str_or_none_or_raise = classmethod(_get_str_or_none_or_raise)

        super(MoldMeta, cls).__init__(name, bases, cls_dict)


def _get_str_or_none_or_raise(cls, attr_name):
    requirement = getattr(cls, attr_name, None)
    if requirement is not None:
        if not isinstance(requirement, six.string_types) or not requirement:
            msg = "{}.{} has to be a nonempty string or None, got '{}'."
            raise ValueError(msg.format(cls.__name__, attr_name, type(requirement).__name__))
    return requirement


def _get_from_bases(bases, attribute_name):
    for top_base in bases:
        for sub_base in top_base.__mro__:
            if hasattr(sub_base, attribute_name):
                yield getattr(sub_base, attribute_name)


def _get_inherited_slots(bases):
    for tuple_or_str in _get_from_bases(bases, "__slots__"):
        if isinstance(tuple_or_str, six.string_types):
            yield tuple_or_str  # in case of a forgotten colon - single slot
        else:
            for slot in tuple_or_str:
                yield slot


def _get_inherited_properties(bases):
    for cls_dict in _get_from_bases(bases, "__dict__"):
        for name, value in cls_dict.items():
            if isinstance(value, property):
                yield name


def _get_inherited_auto_slots_setting(bases):
    for cls_dict in _get_from_bases(bases, "__dict__"):
        for name, value in cls_dict.items():
            if name == "_cls_make_slots":
                yield value


def _tuplize(item):
    return (item,) if not isinstance(item, tuple) else item


def _get_ignored_slots(cls, cls_dict):
    for f in _tuplize(cls_dict.get("_extra_slots", ())):
        yield f
    for base in cls.__mro__:
        ignored_slots = getattr(base, "_extra_slots", ())
        for f in _tuplize(ignored_slots):
            yield f


def _unique_in_order(iterable):
    return tuple(OrderedDict.fromkeys(iterable))
