import inspect
import sys
from collections import OrderedDict


class ArgsInspect(object):
    __slots__ = "args", "varargs", "keywords", "defaults"

    def __init__(self, args, varargs, keywords, defaults):
        self.args, self.varargs, self.keywords, self.defaults = args, varargs, keywords, defaults

    def __repr__(self):
        """in a classic way at this time """
        args = ["%s=%r" % (f, getattr(self, f)) for f in self.__slots__]
        return "%s(%s)" % (self.__class__.__name__, ", ".join(args))

    def __len__(self):
        """ number of arguments (vararg and kwarg are count as single arg) """
        return len(self.args) + bool(self.varargs) + bool(self.keywords)

    def __iter__(self):
        """ names of arguments """
        for a in self.args:
            yield a
        if self.varargs:
            yield self.varargs
        if self.keywords:
            yield self.keywords

    @classmethod
    def from_type(cls, class_or_type):
        try:
            inspect.getfile(class_or_type.__init__)
        except TypeError:
            # plain object or builtin
            fields = getattr(class_or_type, "_fields", None)
            if not fields:
                # not a namedtuple neither
                raise TypeError("The class {} does not implement constructor.".format(class_or_type.__name__))

            return cls(fields, None, None, None)

        return cls.from_callable(class_or_type.__init__)

    @classmethod
    def from_callable(cls, callable_object):
        if sys.version[0] < '3':
            a = inspect.getargspec(callable_object)
            unsupported = ()
            keywords = a.keywords

        else:
            a = inspect.getfullargspec(callable_object)
            keywords = a.varkw
            unsupported = "kwonlyargs", "kwonlydefaults"

        for kind in unsupported:
            if getattr(a, kind, False):
                TypeError("renew does not support syntax containing '%s'." % kind)
        p_args = a.args[1:] if a.args[0] == "self" else a.args
        return cls(p_args, a.varargs, keywords, a.defaults)

    def cls_arguments(self, object_instance):
        """ Generate name-value pairs according to constructor's interface.
        Keys are names come form constructor arguments specification,
        Values are corresponding attribute value of object_instance.
        """

        any_skipped_already = False
        for argument_name, has_default, default_value in self._bind_defaults():
            value = _get_attribute_or_raise(object_instance, argument_name)
            if has_default:
                if value == default_value:
                    any_skipped_already = True
                elif any_skipped_already:
                    yield argument_name, value
                else:
                    yield None, value
            else:
                yield None, value

        if self.varargs:
            variadic_arg = _get_attribute_or_raise(object_instance, self.varargs)
            if isinstance(variadic_arg, set):
                # order doesn't matter for a set, but its presentation
                # needs to be kept always in the same order
                try:
                    variadic_arg = sorted(variadic_arg)
                except TypeError:
                    pass
            else:
                if not isinstance(variadic_arg, (tuple, list, OrderedDict)):
                    msg = "Variadic arg has to be stored as a tuple, list or OrderedDict, got {}"
                    raise TypeError(msg.format(type(object_instance).__name__))

            if isinstance(variadic_arg, OrderedDict):
                variadic_arg = variadic_arg.items()

            for attribute_object in variadic_arg:
                yield None, attribute_object

        if self.keywords:
            kw_attribute = _get_kw_attribute_or_raise(object_instance, self.keywords)
            # order doesn't matter for a set, but its presentation
            # needs to be kept always in the same order
            for keyword, value in sorted(kw_attribute.items()):
                yield keyword, value

    def _bind_defaults(self):
        """ return tuple of triplets so that each contains:
            (<argument name>: str, <has a default>: bool, <default value>: Any)
        """
        if not self.defaults:
            return tuple((name, False, None) for name in self.args)
        defaults_len = len(self.defaults or ())
        blanks_len = len(self.args) - defaults_len
        has_default = (False,) * blanks_len + (True,) * defaults_len
        defaults = (None,) * blanks_len + self.defaults
        return tuple(zip(self.args, has_default, defaults))


def _get_attribute_or_raise(object_, name):
    if not hasattr(object_, name):
        msg = "{} has no '{}' attribute. Constructor args have to be named same as class attributes."
        raise AttributeError(msg.format(object_.__class__.__name__, name))
    return getattr(object_, name)


def _get_kw_attribute_or_raise(object_, name):
    kw_attribute = _get_attribute_or_raise(object_, name)
    if not isinstance(kw_attribute, (dict, OrderedDict)):
        msg = "Expecting {}.{} attribute to be a dict or OrderedDict, got {}."
        raise AttributeError(msg.format(object_.__class__.__name__, name, type(kw_attribute).__name__))
    return kw_attribute
