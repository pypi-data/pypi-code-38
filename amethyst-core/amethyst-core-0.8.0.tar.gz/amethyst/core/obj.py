# -*- coding: utf-8 -*-
"""
***************************
Generic serializable object
***************************

.. |br| raw:: html

   <br />

SYNOPSIS
========

::

    from amethyst.core import Object, Attr

    class MyObject(Object):
        # Attr() defines properties and will include in serialization.
        foo = Attr(int)
        bar = Attr(str).strip()

        # foo and bar will be automatically extracted from kwargs.
        # .other will not be serialized by .toJSON()
        def __init__(self, other=None, **kwargs):
            super().__init__(**kwargs)
            self.other = other


    # ...
    myobj = MyObject(foo=23, other="Hello")
    myobj.toJSON()   # { "__my.module.MyObject__": { "foo": 23 } }

    myobj = MyObject()
    myobj.fromJSON('{ "foo": 23, "bar": " plugh  " }')
    print(myobj.bar)      # "plugh"  (no spaces)



DESCRIPTION
===========

Implements the dictionary interface and stores everything in self.dict.

Subclasses can define :py:class:`Attr` which will have properties defined
as shortcuts to read and write keys in the dictionary.

By storing all attributes in a dict, we can be trivially serialized.
toJSON() and fromJSON() methods exist to help with this, and should be used
for all JSON serialization since they will correctly handle `set()` and
other values (see the :py:func:`Object.JSONEncoder` and
:py:func:`Object.JSONObjectHook` methods). Additionally, the JSON methods
will perform automatic validation based on type information passed to the
:py:class:`Attr` objects and will ensure that it is loading data for the
correct class and that no unexpected keys are present.
"""
# SPDX-License-Identifier: LGPL-3.0
from __future__ import division, absolute_import, print_function, unicode_literals

__all__ = """
Object
Attr
AmethystException
  DuplicateAttributeException
  ImmutableObjectException
register_amethyst_type
amethyst_deflate
amethyst_inflate
""".split()

import json
import numbers
import six

from .util import coalesce, smartmatch


class AmethystException(Exception): pass
class ImmutableObjectException(AmethystException): pass
class DuplicateAttributeException(AmethystException): pass


class Attr(object):
    """
    Base class for Amethyst Object Attributes

    Attribute descriptions primarily consist of a function which takes in a
    value and either returns a (possibly modified) value or else raises a
    :py:exc:`ValueError`. Python's standard object constructors generally work well,
    though beware that `str` will generally accept anything. ::

        foo = Attr(int)                   # Coerce to int (strict parsing)
        foo = Attr(float).int()           # Parse via float, but then integerize
        foo = 0 < Attr(int)               # Positive integer
        foo = (0 <= Attr(int)) <= 200     # Alas, parens are necessary!

        # Stringify, then strip whitespace
        foo = Attr(str).strip()

        # Python 3: Accept bytes or str, decoding if possible (only decodes
        # bytes since decode not a method of str)
        foo = Attr(isa=(bytes, str)).decode("UTF-8")

        # Coerce to a list via .split()
        foo = Attr(isa=(list, str)).split()

    Anything based off of Amethyst's :py:class:`Object` class generally will work as well::

        class MyClass(amethyst.core.Object):
            ...

        class MyClass2(amethyst.core.Object):
            foo = Attr(MyClass)

    :ivar name: Attribute name when assigned to an Object (auto-set by metaclass).
    """
    def __init__(self, convert=None, verify=None, isa=None, default=None, builder=None, fget=None, fset=None, fdel=None, doc=None, OVERRIDE=False):
        """
        :param convert: Attribute converter. At this time, only callables
           are supported. Callable should accept a single argument, the
           value, and should return a canonicalized value. Invalid values
           should raise a ValueError(). If converter is `None`, values will
           be passed unmodified.

        :param isa: Called after conversion but before verification,
           ensures that the value is one of the passed types. Is a shortcut
           for `verify=lambda val: isinstance(val, isa)`

        :param verify: Attribute verifier. Called after conversion, this
           callable should return a truthy result if the value is acceptable.

        :param default: Default value applied at object creation time. If
           default is a callable, it will be called to produce the default
           (e.g., `list`).

            .. note::
              The default value (or result of callable) is assumed valid
              and will not pass through conversion or verification.

        :param builder: Callable which will lazily build a default value
           when the attribute is first used.

        :param fget:
        :param fset:
        :param fdel: If any of fget, fset, or fdel are defined, they will
           be used to construct the object property. If all three are none
           (the default), then the functions which get/set/del the
           appropriate key in the object dictionary will be defined.

        :param doc: Documentation to be attached to the property.

        :param OVERRIDE: When true, allow attribute to replace an existing
           attribute (from a parent class).
        """
        if verify is not None and not callable(verify):
            raise TypeError("Unknown 'verify' type")
        if convert is not None and not callable(convert):
            raise TypeError("Unknown 'convert' type")
        self.convert = convert
        self.isa     = isa
        self.verify  = verify
        self.fget    = fget
        self.fset    = fset
        self.fdel    = fdel
        self.doc     = doc
        self.default = default
        self.builder = builder
        self.OVERRIDE = OVERRIDE

    def build_property(self, name):
        """ """
        if self.fget is None and self.fset is None and self.fdel is None:

            def fget(obj):
                try:
                    return obj.dict[name]
                except KeyError:
                    # default happens before builder
                    if self.default is not None:
                        obj.dict[name] = self(self.get_default(), name)
                        return obj.dict[name]
                    if self.builder is not None:
                        obj.dict[name] = self(self.builder(), name)
                        return obj.dict[name]
                return None

            def fset(obj, value):
                obj.amethyst_assert_mutable()
                obj.dict[name] = self(value, name)

            def fdel(obj):
                obj.amethyst_assert_mutable()
                del obj.dict[name]

            return property(fget, fset, fdel, self.doc)

        else:
            return property(self.fget, self.fset, self.fdel, self.doc)

    def get_default(self):
        """ """
        if callable(self.default):
            return self.default()
        else:
            return self.default

    def copy_meta(self, *others):
        """
        Copy metadata from another Attr object. This method is used when
        defining derived attributes (e.g., :py:meth:`strip`) to copy
        documentation and the OVERRIDE flag. Returns the object itself for
        chaining.
        """
        for attr in others:
            if (not self.OVERRIDE) and hasattr(attr, "OVERRIDE"): self.OVERRIDE = attr.OVERRIDE
            if (not self.doc)      and hasattr(attr, "doc"):      self.doc = attr.doc
        return self

    def __call__(self, value, key=None):
        """ """
        if self.convert:
            value = self.convert(value)
        if self.isa:
            if not isinstance(value, self.isa):
                raise ValueError("Value of '{}' is not an instance of {}".format(key, str(self.isa)))
        if self.verify:
            if not self.verify(value):
                raise ValueError("Value of '{}' does not satisfy verification callback".format(key))
        return value

    def __and__(self, other):
        """ """
        return self.__class__(lambda v: other(self(v))).copy_meta(self, other)
    def __rand__(self, other):
        """ """
        return self.__class__(lambda v: self(other(v))).copy_meta(self, other)

    def __or__(self, other):
        """ """
        def convert(value):
            try:
                return self(value)
            except ValueError as err:
                if callable(other):
                    return other(value)
                elif value == other:
                    return other
                else:
                    raise err
        return self.__class__(convert).copy_meta(self, other)

    def __ror__(self, other):
        """ """
        def convert(value):
            try:
                if callable(other):
                    return other(value)
                elif value == other:
                    return other
                else:
                    raise ValueError("Invalid value")
            except ValueError:
                return self(value)
        return self.__class__(convert).copy_meta(self, other)

    def __eq__(self, other):
        """
        Tests via :py:func:`amethyst.core.util.smartmatch`

        .. WARNING::
           Hash lookups must be idempotent (looking up the result of
           a previous lookup had better return the same thing) since we offer
           no guarantees that validation may not happen more than once.

           GOOD:: :code:`{ "a": "A", "b": "B",  "A": "A", "B": "B" }`

           BAD:: :code:`{ "a": "A", "b": "B" }  # will fail on repeated validation since "A" and "B" are not keys`
        """
        return self.__class__(lambda v: smartmatch(self(v), other)).copy_meta(self)
    def __ne__(self, other):
        """Ensure no smartmatch"""
        def convert(value):
            val = self(value)
            try:
                # If we do not match the other value, this raises an
                # exception (thus we can return val).
                smartmatch(val, other)
            except ValueError:
                return val
            # otherwise, we've matched the smartmatch, this we match what
            # we don't want to be - raise a value error.
            raise ValueError("Invalid Value")
        return self.__class__(convert).copy_meta(self)

    # This is starting to get cute:
    def __lt__(self, other):
        """ """
        def convert(value):
            val = self(value)
            if val < other: return val
            raise ValueError("Invalid Value")
        return self.__class__(convert).copy_meta(self)
    def __le__(self, other):
        """ """
        def convert(value):
            val = self(value)
            if val <= other: return val
            raise ValueError("Invalid Value")
        return self.__class__(convert).copy_meta(self)
    def __ge__(self, other):
        """ """
        def convert(value):
            val = self(value)
            if val >= other: return val
            raise ValueError("Invalid Value")
        return self.__class__(convert).copy_meta(self)
    def __gt__(self, other):
        """ """
        def convert(value):
            val = self(value)
            if val > other: return val
            raise ValueError("Invalid Value")
        return self.__class__(convert).copy_meta(self)

    # These modifiers make no sense unless they are idempotent since we may
    # validate multiple times. Thus, we only define those whose semantics
    # swing that way.
    def __mod__(self, other):
        """ """
        return self.__class__(lambda v: self(v) % other).copy_meta(self)
    def __pos__(self):
        """ """
        return self.__class__(lambda v: +self(v)).copy_meta(self)
    def __abs__(self):
        """ """
        return self.__class__(lambda v: abs(self(v))).copy_meta(self)

    # I don't see much use for float() since it is the first thing you
    # would want to do. However, int() could be useful since
    # Attr(float).int() is a more flexible converter (integerizing stringy
    # floats rather than raising an exception). Just for completeness, we
    # include complex too.
    def float(self):
        """ """
        return self.__class__(lambda v: float(self(v))).copy_meta(self)
    def int(self):
        """ """
        return self.__class__(lambda v: int(self(v))).copy_meta(self)
    def complex(self):
        """ """
        return self.__class__(lambda v: complex(self(v))).copy_meta(self)

    # Can also define a handful of common methods one might wish to call,
    # and call them if present. Happy duck-typing.
    def strip(self, chars=None):
        """Return a new attribute which strips whitespace if applicable (duck typing)."""
        def convert(value):
            value = self(value)
            return value.strip(chars) if hasattr(value, "strip") else value
        return self.__class__(convert).copy_meta(self)
    def rstrip(self, chars=None):
        """Return a new attribute which strips whitespace from the right side if applicable (duck typing)."""
        def convert(value):
            value = self(value)
            return value.rstrip(chars) if hasattr(value, "rstrip") else value
        return self.__class__(convert).copy_meta(self)
    def lstrip(self, chars=None):
        """Return a new attribute which strips whitespace from the left side if applicable (duck typing)."""
        def convert(value):
            value = self(value)
            return value.lstrip(chars) if hasattr(value, "lstrip") else value
        return self.__class__(convert).copy_meta(self)

    def encode(self, encoding="UTF-8", errors="strict"):
        """Return a new attribute which encodes value if applicable (duck typing). Defaults to UTF-8 encoding."""
        def convert(value):
            value = self(value)
            return value.encode(encoding, errors) if hasattr(value, "encode") else value
        return self.__class__(convert).copy_meta(self)
    def decode(self, encoding="UTF-8", errors="strict"):
        """Return a new attribute which decodes value if applicable (duck typing). Defaults to UTF-8 encoding."""
        def convert(value):
            value = self(value)
            return value.decode(encoding, errors) if hasattr(value, "decode") else value
        return self.__class__(convert).copy_meta(self)

    def lower(self):
        """Return a new attribute which lower-cases value if applicable (duck typing)."""
        def convert(value):
            value = self(value)
            return value.lower() if hasattr(value, "lower") else value
        return self.__class__(convert).copy_meta(self)
    def upper(self):
        """Return a new attribute which upper-cases value if applicable (duck typing)."""
        def convert(value):
            value = self(value)
            return value.upper() if hasattr(value, "upper") else value
        return self.__class__(convert).copy_meta(self)
    def title(self):
        """Return a new attribute which title-cases value if applicable (duck typing)."""
        def convert(value):
            value = self(value)
            return value.title() if hasattr(value, "title") else value
        return self.__class__(convert).copy_meta(self)
    def capitalize(self):
        """Return a new attribute which capitalizes value if applicable (duck typing)."""
        def convert(value):
            value = self(value)
            return value.capitalize() if hasattr(value, "capitalize") else value
        return self.__class__(convert).copy_meta(self)
    def casefold(self):
        """Return a new attribute which casefolds value if applicable (duck typing)."""
        def convert(value):
            value = self(value)
            return value.casefold() if hasattr(value, "casefold") else value
        return self.__class__(convert).copy_meta(self)

    def split(self, sep=None, maxsplit=-1):
        """Return a new attribute which splits its value if applicable (duck typing)."""
        def convert(value):
            value = self(value)
            return value.split(sep, maxsplit) if hasattr(value, "split") else value
        return self.__class__(convert).copy_meta(self)


global_amethyst_encoders = dict()
global_amethyst_hooks = dict()
def register_amethyst_type(cls, encode, decode, name=None, overwrite=False, wrap_encode=True):
    """
    Adds a type to the global list (:py:data:`global_amethyst_encoders`)
    for object encoding and decoding. Subclasses of :py:class:`Object` are
    automatically registered, so you should only need to register external
    objects that you use.

    :param class cls: Class to register

    :param callable encode: Callable which will transform the object into a "dumb"
        structure of primitive objects (dict, list, str, int, float).

    :param callable decode: Callable which will transform the "dumb" structure of
        primitive objects back into the object.

    :param str name: Globally unique string identifying the class. This
        name should be something which won't appear as a dictionary key in
        normal data. Defaults to "__MODULENAME.CLASSNAME__"

    :param bool overwrite: By default, this function will raise an error if
        a class or name is aready registered. Pass True to override any
        existing registrations.

    :param bool wrap_encode: By default, the encoded object will be wrapped
        in a single-key dict: :code:`{ name: ENCODED_OBJECT }` so that the
        decoder can be called when inflating a structure containing the
        object. Pass True in this parameter in order to avoid wrapping the
        encoded structure.

        |br|

        You might want to set this parameter if your object is naturally
        expressed as a basic object and you are certain that all uses after
        inflation will automatically coerce the value to your desired
        object when needed. For instance, a URL object where all functions
        and methods which accept the URL object also accept a plain string.
        You could pass an encoder which deflates to plain strings and set
        :code:`wrap_encode=False` and then URLs would appear as plain strings in
        your exported structures, which may be easier to work with in
        external applications.

        |br|

        This option also offers an escape hatch for hypothetical cases
        where you may need to wrap your encoded object in your encoder
        itself.

    .. seealso:: :py:func:`amethyst_deflate` and :py:func:`amethyst_inflate`

    """
    if name is None:
        if isinstance(cls, BaseObject):
            name = cls._dundername
        else:
            name = "__{}.{}__".format(cls.__module__, cls.__name__)
    if cls in global_amethyst_encoders and not overwrite:
        raise ValueError("Class encoder '{}' already reqistered".format(cls))
    if name in global_amethyst_hooks and not overwrite:
        raise ValueError("Class hook '{}' already reqistered".format(name))
    if wrap_encode:
        global_amethyst_encoders[cls] = lambda obj: { name: encode(obj) }
    else:
        global_amethyst_encoders[cls] = encode
    global_amethyst_hooks[name] = decode


def amethyst_deflate(obj, deflator=None):
    """
    Deflate a structure of amethyst-encodable objects into a "dumb"
    structure of plain dicts, lists, numbers, and strings. The deflated
    structure should be easily serializable by most any reasonable
    serialization library (yaml, lxml, ...)

    Makes use of :py:data:`global_amethyst_encoders` by default. Pass an amethyst
    Object as second argument to make use of any Object-local encoders.

    Note: If your target is JSON, the amethyst object's :py:func:`Object.toJSON` method is
    probably better.
    """
    global global_amethyst_encoders

    if obj is None or isinstance(obj, (six.string_types, six.binary_type, numbers.Number, bool)):
        return obj
    elif isinstance(obj, dict):
        return { six.text_type(k): amethyst_deflate(obj[k], deflator) for k in obj }
    elif isinstance(obj, list):
        return [ amethyst_deflate(k, deflator) for k in obj ]
    elif isinstance(obj, tuple):
        return tuple(amethyst_deflate(k, deflator) for k in obj)
    elif hasattr(deflator, "_jsonencoders") and obj.__class__ in deflator._jsonencoders:
        return deflator._jsonencoders[obj.__class__](obj)
    elif obj.__class__ in global_amethyst_encoders:
        return global_amethyst_encoders[obj.__class__](obj)
    raise TypeError("Can't encode {}".format(repr(obj)))


def amethyst_inflate(obj, inflator=None, maxdepth=None):
    """
    Inflate a "dumb" structure to a structure of objects, the opposite of
    :py:func:`amethyst_deflate`. Allows inflation from arbitrary serialization
    tools, as long as they can produce dicts and lists.

    Makes use of :py:data:`global_amethyst_encoders` by default. Pass an amethyst
    Object as second argument to make use of any Object-local encoders.

    .. note::
      If your source is JSON, the amethyst object's :py:func:`Object.fromJSON()` or
      class :py:func:`Object.newFromJSON()` method is probably better.
    """
    global global_amethyst_hooks
    if maxdepth is not None:
        if maxdepth < 0:
            return obj
        maxdepth -= 1

    if isinstance(obj, dict):
        if 1 == len(obj):
            for key in obj:
                if hasattr(inflator, "_jsonhooks") and key in inflator._jsonhooks:
                    return inflator._jsonhooks[key](obj[key])
                elif key in global_amethyst_hooks:
                    return global_amethyst_hooks[key](obj[key])
        elif maxdepth is None or maxdepth >= 0:
            for key in obj:
                obj[key] = amethyst_inflate(obj[key], inflator, maxdepth=maxdepth)

    elif isinstance(obj, list) and (maxdepth is None or maxdepth >= 0):
        for i, val in enumerate(obj):
            obj[i] = amethyst_inflate(val, inflator, maxdepth=maxdepth)

    return obj


# Python3 moved the builtin modules around, force the name so py3 can talk to py2
register_amethyst_type(set, list, set, name="__set__")
register_amethyst_type(frozenset, list, frozenset, name="__frozenset__")


class AttrsMetaclass(type):
    """
    Metaclass for Amethyst Object class descendants. Simply looks at all
    attributes for any which are instances of :py:class:`Attr`. The
    :py:class:`Attr` itself is saved to the :py:attr:`_attr` class
    attribute (a dictionary) and a property created in its place via the
    Attr :py:func:`Attr.build_property` method.
    """
    def __new__(cls, class_name, bases, attrs):
        new_attrs = dict()
        for name in list(attrs.keys()):
            if isinstance(attrs[name], Attr):
                new_attrs[name] = attrs.pop(name)
                new_attrs[name].name = name

        new_cls = super(AttrsMetaclass, cls).__new__(cls, class_name, bases, attrs)

        # Need some bootstrapping
        if class_name != 'BaseObject' and attrs.get("amethyst_register_type", True):
            register_amethyst_type(
                new_cls,
                encode    = (lambda obj: obj.dict),
                decode    = (lambda obj: new_cls(obj)),
                overwrite = False
            )

        # Merge json hooks into the base _json* hooks.
        for jattr in "jsonhooks", "jsonencoders":
            if hasattr(new_cls, jattr):
                _jattr = "_" + jattr
                setattr(new_cls, _jattr, dict(getattr(new_cls, _jattr)))# Shallow clone
                getattr(new_cls, _jattr).update(getattr(new_cls, jattr))
                delattr(new_cls, jattr)

        for name, attr in six.iteritems(new_attrs):
            if not attr.OVERRIDE and hasattr(new_cls, name):
                raise DuplicateAttributeException("Attribute {} in {} already defined in a parent class.".format(name, cls.__name__))
            setattr(new_cls, name, attr.build_property(name))

        new_cls._attrs = new_cls._attrs.copy()
        new_cls._attrs.update(new_attrs)
        new_cls._dundername = "__{}.{}__".format(new_cls.__module__, new_cls.__name__)

        return new_cls


# Manually create a base object so that we can run in both python 2 and 3.
#
#   https://wiki.python.org/moin/PortingToPy3k/BilingualQuickRef#metaclasses
BaseObject = AttrsMetaclass(str('BaseObject'), (), {
    "_attrs": {},
    "_jsonencoders": {},
    "_jsonhooks": {},
})

UNIQUE1 = object()
UNIQUE2 = object()

class Object(BaseObject):
    """
    Amethyst Base Object

    :ivar _attr: Dictionary mapping attribute names to :py:class:`Attr`
      objects. Should not be modified, but can be read for introspection of
      an Object.

    :ivar _jsonencoders: Dictionary mapping class objects to callable
      encoders which should produce a JSON-serializable object. These
      functions are called from the JSONEncoder method. Per the json
      documentation, these functions should return an object which is JSON
      serializable or else raise a TypeError. These encoders are specific
      to the class. Use :py:func:`register_amethyst_type` to register a
      class globally.

      .. note::
        _jsonencoders is a lower-level tool than
        :py:func:`register_amethyst_type` and offers direct access to the
        encoders (behaves like `overwrite=True, wrap_encode=False`)

    :ivar _jsonhooks: Dictionary mapping class identifiers (strings of form
      "__MODULENAME.CLASSNAME__") to callable decoders which should inflate
      simple structures to corresponding objects. These functions are
      called from the JSONObjectHook method when inflating data. These
      decoders are specific to the class. Use
      :py:func:`register_amethyst_type` to register a class globally.

      .. note::
        _jsonhooks is a lower-level tool than
        :py:func:`register_amethyst_type` and offers direct access to the
        decoders (behaves like `overwrite=True, wrap_encode=False`)

    """

    amethyst_includeclass  = True
    """
    When True (the default), serialization will include a key "__class__"
    containing the class name of the object which can be used during
    loading to verify that the object is of the correct type.
    """

    amethyst_verifyclass   = True
    """
    When True (the default), loading data from JSON or a dict passed to
    :py:func:`amethyst_load_data()` will check for the "__class__" key described above, and
    an exception will be thrown if it is not found.
    """

    amethyst_import_strategy = "strict"
    """
    When "strict" (the default), then loading data from JSON or a
    dictionary via :py:func:`amethyst_load_data()` requires all keys present in the data
    structure to correspond with keys in the attribute list. If any
    additional keys are present, an exception will be raised. When "loose",
    additional keys will be ignored and not copied into the object
    dictionary. When "sloppy", unknown attributes will be copied unmodified
    into the object dict.
    """

    amethyst_register_type = True
    amethyst_classhint_style = "flat"

    def __init__(self, *args, **kwargs):
        """
        Initializes self.dict with all passed kwargs.
        Object is mutable by default.

        .. warning::
           Passing a single argument that is an instance of the class
           itself is reserved for internal use only and behavior is likely
           to change.
        """
        super(Object, self).__init__()
        self._amethyst_mutable_ = True

        # Special-case of single argument:
        if len(args) == 1 and not kwargs and isinstance(args[0], type(self)):
            # - NOT A COPY! Primary case of Object(Object()) is
            #   re-import by JSON Hook, thus we just need another view
            #   of the same data (returning the same object would also
            #   work, but I don't know how to do that, and isn't really
            #   worth it).
            #
            # - Object already one of our type, no need to merge defaults
            self.dict = args[0].dict
            self._amethyst_mutable_ = args[0]._amethyst_mutable_

        else:
            self.dict = dict()
            data = dict()
            for d in args: data.update(d)
            if kwargs: data.update(kwargs)
            if data:
                self.amethyst_load_data(data, verifyclass=False)

        for name, attr in six.iteritems(self._attrs):
            if attr.default is not None and name not in self.dict:
                self.dict[name] = attr.get_default()

    def amethyst_assert_mutable(self, msg="May not modify, object is immutable"):
        """ """
        if not self._amethyst_mutable_:
            raise ImmutableObjectException(msg)
        return self

    def amethyst_is_mutable(self):
        """ """
        return self._amethyst_mutable_
    def amethyst_make_mutable(self):
        """ """
        self._amethyst_mutable_ = True
        return self
    def amethyst_make_immutable(self):
        """ """
        self._amethyst_mutable_ = False
        return self

    def __str__(self):
        return str(self.dict)
    def __repr__(self):
        return repr(self.dict)

    def __len__(self):
        """ """
        return len(self.dict)
    def __contains__(self, key):
        """ """
        return key in self.dict
    def __iter__(self):
        """ """
        return iter(self.dict)

    def __eq__(self, other):
        """
        Object equality. Tests all :py:func:`Attr()`s and only
        :py:func:`Attr()`s. Other python properties or "garbage" in the
        underlying dict (which may arise from "sloppy" imports) will be
        ignored.
        """
        if self.__class__ != other.__class__:
            return False
        for name, attr in six.iteritems(self._attrs):
            if getattr(self, name, UNIQUE1) != getattr(other, name, UNIQUE2):
                return False
        return True
    def __ne__(self, other):
        return not (self == other)

    def items(self, **kwargs):
        """
        Subclasses: this method may be overridden with an unrelated implementation.
        """
        for name, attr in six.iteritems(self._attrs):
            if name in self.dict:
                yield name, self.dict[name]
    iteritems = items
    def keys(self, **kwargs):
        """
        Subclasses: this method may be overridden with an unrelated implementation.
        """
        for name, attr in six.iteritems(self._attrs):
            if name in self.dict:
                yield name
    def values(self, **kwargs):
        """
        Subclasses: this method may be overridden with an unrelated implementation.
        """
        for name, attr in six.iteritems(self._attrs):
            if name in self.dict:
                yield self.dict[name]

    def __getitem__(self, key):
        """ """
        return self.dict[key]
    def __setitem__(self, key, value):
        """ """
        self.amethyst_assert_mutable()
        attr = self._attrs.get(key)
        if attr is not None:
            self.dict[key] = attr(value, key)
        elif self.amethyst_import_strategy == "strict":
            raise KeyError("key {} not permitted in {} object".format(key, self._dundername))
        elif self.amethyst_import_strategy == "sloppy":
            self.dict[key] = value
    def __delitem__(self, key):
        """ """
        self.amethyst_assert_mutable()
        del self.dict[key]

    def get(self, key, dflt=None):
        """
        Subclasses: this method may be overridden with an unrelated implementation.
        """
        return self.dict.get(key, dflt)

    def set(self, *args, **kwargs):
        """
        Verify then set canonicalized value. Positional args take
        precedence over kwargs. ::

            obj.set(key, val)
            obj.set(foo=val)

        Subclasses: this method may be overridden with an unrelated implementation.
        """
        if 2 == len(args) and not kwargs:
            self[args[0]] = args[1]
            return self
        self.amethyst_assert_mutable()
        for i in range(0, len(args), 2):
            kwargs[args[i]] = args[i+1]
        self.dict.update(self.amethyst_validate_update(kwargs))
        return self

    def setdefault(self, key, value):
        """
        If missing a value, verify then set

        Subclasses: this method may be overridden with an unrelated implementation.
        """
        self.amethyst_assert_mutable()
        if key not in self.dict:
            self.set(key, value)
        return self.dict[key]

    def direct_set(self, *args, **kwargs):
        """
        Set values BYPASSING VALIDATION but respecting mutability.
        Positional args take precedence over kwargs. ::

            obj.direct_set(key, val)
            obj.direct_set(foo=val)

        Subclasses: this method may be overridden with an unrelated implementation.
        """
        self.amethyst_assert_mutable()
        for i in range(0, len(args), 2):
            kwargs[args[i]] = args[i+1]
        self.dict.update(kwargs)
        return self

    def pop(self, key, dflt=None):
        """
        Subclasses: this method may be overridden with an unrelated implementation.
        """
        self.amethyst_assert_mutable()
        return self.dict.pop(key, dflt)

    def update(self, *args, **kwargs):
        """
        Subclasses: this method may be overridden with an unrelated implementation.
        """
        self.amethyst_assert_mutable()
        data = dict()
        for d in args: data.update(d)
        if kwargs: data.update(kwargs)
        self.dict.update(self.amethyst_validate_update(data))
        return self

    def direct_update(self, *args, **kwargs):
        """
        Update internal dictionary BYPASSING VALIDATION but respecting
        mutability.

        Subclasses: this method may be overridden with an unrelated implementation.
        """
        self.amethyst_assert_mutable()
        self.dict.update(*args, **kwargs)
        return self

    def amethyst_validate_update(self, d, import_strategy=None):
        """
        Convert and validate with the intention of updating only some of
        the object's .dict values. Returns a new dictionary with
        canonicalized values, but *does not initialize any missing keys
        with attribute default values* (which distinguishes this from
        :py:func:`amethyst_validate_data`).

        This method does not change the object. Pass the resulting dict to
        the `.update()` method (or `.direct_update()` if you decide to accept
        the changes.
        """
        strategy = coalesce(import_strategy, self.amethyst_import_strategy)
        data = d.copy() if strategy == "sloppy" else dict()
        for key, val in six.iteritems(d):
            attr = self._attrs.get(key)
            if attr is None and strategy == "strict":
                raise KeyError("key {} not permitted in {} object".format(key, self._dundername))
            elif attr is not None:
                data[key] = attr(val, key)
        return data

    def amethyst_validate_data(self, d, import_strategy=None):
        """
        Convert and validate with the intention of replacing all of the
        object's .dict values. Returns a new dictionary with canonicalized
        values, *and defaults inserted* (which distinguishes this from
        :py:func:`amethyst_validate_update`).

        This method does not change the object. Typical usage would look
        like either::

            myobj.dict = myobj.amethyst_validate_data(data)

        or ::

            validated = myobj.amethyst_validate_data(data)
            mynewobj = MyClass(**validated)

        Subclasses of :py:class:`Object` can also use this method to
        inflate specific attibutes at load time. For instance, to inflate
        non-Object objects or ensure objects from hand-written config
        files. Be sure to override :py:func:`amethyst_validate_update` as
        well if programmatic updates may need special inflation rules.
        """
        strategy = coalesce(import_strategy, self.amethyst_import_strategy)
        data = d.copy() if strategy == "sloppy" else dict()
        keys = set(d.keys()) if strategy == "strict" else set()
        for name, attr in six.iteritems(self._attrs):
            keys.discard(name)
            if name in d:
                data[name] = attr(d[name], name)
            elif attr.default is not None:
                data[name] = attr.get_default()
        if keys:
            raise ValueError("keys {} not permitted in {} object".format(keys, self._dundername))
        return data

    def attr_value_ok(self, name, value):
        """
        Validate a single value independently of any others. Just checks
        that the attribute validator does not raise an exception.

        Subclasses: this method may be overridden with an unrelated implementation.
        """
        if name in self._attrs:
            try:
                self._attrs[name](value, name)
                return True
            except ValueError:
                return False
        return False

    def amethyst_load_data(self, data, import_strategy=None, verifyclass=None):
        """
        Loads a data dictionary with validation. Modifies the passed dict
        and replaces current self.dict object with the one passed.

        :param import_strategy: Provides a local override to the :py:attr:`amethyst_import_strategy` class attribute.

        :param verifyclass: Provides a local override to the :py:attr:`amethyst_verifyclass` class attribute.

        This method transparently loads data in either "single-key" or "flat" formats::

            { "__my.module.MyClass__": { ... obj.dict ... } }

            { "__class__": "MyClass", ... obj.dict ... }

        Keep in mind that the default base value for :py:attr:`amethyst_verifyclass` is
        True, so, by default, at least one of the class identification keys
        is expected to be present.
        """
        self.amethyst_assert_mutable()
        verifyclass = coalesce(verifyclass, self.amethyst_verifyclass)

        # We only deal in dicts here
        if isinstance(data, self.__class__):
            verifyclass = False

        if isinstance(data, Object):
            data = data.dict

        if not isinstance(data, dict):
            raise ValueError("expected dictionary object")

        # Accept data in single-key mode. Pop out the inner dict and, if
        # the indicated class name is what we expect, we can bypass the
        # class verification step.
        if 1 == len(data):
            for key in data:
                if key == self._dundername:
                    verifyclass = False# We're good
                    data = data[key]
                    if not isinstance(data, dict):
                        raise ValueError("expected dictionary object")

        # verifyclass may need to be locally overridden if the source is
        # broken. Once we do verify the class, remove it from the dict to
        # make key iteration safe.
        if verifyclass and data.get("__class__") != self._dundername:
            if data.get("__class__") is None:
                raise ValueError("Error validating import data class: __class__ key missing but should be {} (or set verifyclass=False)".format(self._dundername))
            else:
                raise ValueError("Error validating import data class: got {} object, but expected {}".format(data.get("__class__"), self._dundername))
        data.pop("__class__", None)

        # Run the validator
        self.dict = self.amethyst_validate_data(data, import_strategy=import_strategy)
        return self
    load_data = amethyst_load_data
    """
    Alias for amethyst_load_data

    Subclasses: this method may be overridden with an unrelated implementation.
    """

    def JSONEncoder(self, obj):
        """
        Fallback method for JSON encoding.

        If the standard JSONEncoder is unable to encode an object, this
        method will be called. Per the json documentation, it should return
        an object which is JSON serializable or else raise a TypeError.

        This base encoder, looks up an object's class in a dict and calls
        the corresponding function to do the translation. The built-in
        translators map::

            set       => { "__set__": [ ... ] }
            frozenset => { "__frozenset__": [ ... ] }

        Additional translators may be added by creating a class variable
        :py:attr:`jsonencoders` which is a dict mapping classes to a function. These
        translators will merged onto the base translators (silently
        replacing duplicates) by the metaclass at class (not object)
        creation.
        """
        global global_amethyst_encoders

        if obj.__class__ in self._jsonencoders:
            return self._jsonencoders[obj.__class__](obj)
        elif obj.__class__ in global_amethyst_encoders:
            return global_amethyst_encoders[obj.__class__](obj)
        raise TypeError("Can't encode {}".format(repr(obj)))

    def JSONObjectHook(self, obj):
        """
        Object hook for JSON decoding.

        This method is called for every decoded JSON object. If necessary,
        it should return a new or modified object that should be used instead.

        This base encoder, translates single-key dicts into new objects if
        the single-key is a special value. The built-in translators are::

            { "__set__": [ ... ] }       => set
            { "__frozenset__": [ ... ] } => frozenset

        Additional translators may be added by creating a class variable
        :py:attr:`jsonhooks` which is a dict mapping the special key to a function.
        These translators will merged onto the base translators (silently
        replacing duplicates) by the metaclass at class (not object)
        creation.

        Keep in mind that JSON input comes from untrusted sources, so
        translators will need to be robust against malformed structures.
        """
        global global_amethyst_hooks
        if isinstance(obj, dict) and 1 == len(obj):
            for key in obj:
                if key in self._jsonhooks:
                    return self._jsonhooks[key](obj[key])
                elif key in global_amethyst_hooks:
                    return global_amethyst_hooks[key](obj[key])
        return obj

    def toJSON(self, includeclass=None, style=None, **kwargs):
        """
        Paramters are sent directly to json.dumps except:

        :param includeclass: When true, include a class indicator using the
           method requested by the :code:`style` parameter. When `None` (the
           default), defer to the value of the class variable
           :py:attr:`amethyst_includeclass`.

        :param style: When including class, what style to use (root-level
           object only). Options are:

             * "flat" to produce a JSON string in the form::

                { "__class__": "__my.module.MyClass__", ... obj.dict ... }

             * "single-key" to produce a JSON string in the form::

                { "__my.module.MyClass__": { ... obj.dict ... } }

        The default style is taken from the class :py:attr:`amethyst_classhint_style`
        attribute.
        """
        kwargs.setdefault('default', self.JSONEncoder)
        includeclass = coalesce(includeclass, self.amethyst_includeclass)
        style = coalesce(style, self.amethyst_classhint_style)
        popclass = False

        try:
            dump = self.dict
            if includeclass:
                if style == "flat":
                    popclass = True
                    self.dict["__class__"] = self._dundername
                elif style == "single-key":
                    dump = { self._dundername: self.dict }
                else:
                    raise AmethystException("Unknown class style '{}'".format(style))
            rv = json.dumps(dump, **kwargs)
        finally:
            if popclass:
                self.dict.pop("__class__", None)
        return rv

    @classmethod
    def newFromJSON(cls, source, import_strategy=None, verifyclass=None, **kwargs):
        """ """
        self = cls()
        mutable = self.amethyst_is_mutable()# In case some subclass is default immutable
        if not mutable: self.amethyst_make_mutable()
        self.fromJSON(source, import_strategy=import_strategy, verifyclass=verifyclass, **kwargs)
        if not mutable: self.amethyst_make_immutable()
        return self

    def fromJSON(self, source, import_strategy=None, verifyclass=None, **kwargs):
        """
        Paramters are sent directly to json.load or json.loads except:

        :param import_strategy: Provides a local override to the :py:attr:`amethyst_import_strategy` class attribute.

        :param verifyclass: Provides a local override to the :py:attr:`amethyst_verifyclass` class attribute.
        """
        kwargs.setdefault('object_hook', self.JSONObjectHook)
        if isinstance(source, six.string_types):
            data = json.loads(source, **kwargs)
        else:
            data = json.load(source, **kwargs)
        return self.amethyst_load_data(data, import_strategy=import_strategy, verifyclass=verifyclass)

    def deflate_data(self):
        """
        Deflate object into a "dumb" structure of plain dicts, lists,
        numbers, and strings. The deflated structure should be easily
        serializable by most any reasonable serialization library (yaml,
        lxml, ...)

        Subclasses: this method may be overridden with an unrelated implementation.
        """
        return amethyst_deflate(self.dict, self)

    @classmethod
    def inflate_new(cls, obj):
        """
        Inflate a "dumb" structure to a structure of objects, the opposite
        of :py:func:`deflate_data()`. Allows inflation from arbitrary serialization
        tools, as long as they can produce dicts and lists.

        Subclasses: this method may be overridden with an unrelated implementation.
        """
        return cls(amethyst_inflate(obj, cls))
