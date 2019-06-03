import inspect
import sys

import six


def reproducible(namespace=None):
    """
        Simplifies creating such a class which instance can be reproduced by evaluating
        a string returned by call result of reproduction function or its __repr__ method.
        I.e.:

        >>> @reproducible(namespace="my_pkg")
        ... class ThatNiceClass(object):
        ...     # manual implementation of __init__ is needed. Constructor_arguments
        ...     # have to be actual names of this class attributes
        ...     def __init__(self, f_a, f_b, *f_c):
        ...         self.f_a, self.f_b, self.f_c = f_a, f_b, f_c


        >>> ThatNiceClass(1, None)
        my_pkg.ThatNiceClass(1, None)

        >>> nice = ThatNiceClass(1, 2, 3.14159, "four")
        >>> repr(nice)
        "my_pkg.ThatNiceClass(1, 2, 3.14159, 'four')"

        Limitations:
        * constructor arguments have to get exactly same name as instance attributes
        * given object have to be fully reproduced with single constructor call
        * each constructor argument used - have to implement __repr__ in reproducible flavor
        * no keyword-arguments are supported
        * dictionaries get single indent level no mather what (just ugly but syntax valid)
    """

    def decorator(decorated_class):
        _check_and_evaluate_arguments_specification(decorated_class)
        decorated_class.__repr__ = reproduction
        decorated_class._py_name = classmethod(_eval_py_name(namespace))
        return decorated_class

    return decorator


def reproduction(object_):
    """ Tries to return a reproducible repr for given object_
        Falls back to native repr, so the reproducibility is not guaranteed.

        >>> class ThatNiceClass(object):
        ...     # manual implementation of __init__ is needed. Constructor_arguments
        ...     # have to be actual names of this class attributes
        ...     def __init__(self, f_a, f_b, *f_c):
        ...         self.f_a, self.f_b, self.f_c = f_a, f_b, f_c

        >>> nice = ThatNiceClass(1, 2, 3.14159, "four")
        >>> reproduction(nice)
        "ThatNiceClass(1, 2, 3.14159, 'four')"
        >>> reproduction([10, 20, nice, 40.5])
        "[10, 20, ThatNiceClass(1, 2, 3.14159, 'four'), 40.5]"
    """
    return "".join(_repr_dispatcher(object_, True))


def _repr_dispatcher(object_, top_level=False):
    is_nicely_reproducible = hasattr(object_, "_py_name")
    correct_ctor_args = _implements_constructor(object_.__class__)

    if is_nicely_reproducible:
        items_reprs = [(kw, list(_repr_dispatcher(value))) for kw, value in
                       _collect_attributes(object_, correct_ctor_args)]
        for element in _make_a_markup("%s(" % object_._py_name(), items_reprs, ")"):
            yield element
    elif correct_ctor_args:
        items_reprs = [(kw, list(_repr_dispatcher(value))) for kw, value in
                       _collect_attributes(object_, correct_ctor_args)]
        for element in _make_a_markup("%s(" % object_.__class__.__name__, items_reprs, ")"):
            yield element
    elif isinstance(object_, list):
        items_reprs = [(None, list(_repr_dispatcher(item))) for item in object_]
        for element in _make_a_markup("[", items_reprs, "]"):
            yield element
    elif isinstance(object_, tuple) and not hasattr(object_, '_fields'):
        items_reprs = [(None, list(_repr_dispatcher(item))) for item in object_]
        for element in _make_a_markup("(", items_reprs, ")"):
            yield element
    elif isinstance(object_, set):
        items_reprs = [(None, list(_repr_dispatcher(item))) for item in sorted(object_)]
        for element in _make_a_markup("{", items_reprs, "}"):
            yield element
    elif isinstance(object_, dict):
        items_reprs = [(kw, list(_repr_dispatcher(value)))
                       for kw, value in sorted(object_.items(), key=lambda x: str(x[0]))]
        for element in _make_a_markup("{", items_reprs, "}", as_dict=True):
            yield element
    elif isinstance(object_, six.string_types) and len(object_) > 80:
        if top_level:
            yield "(\n"
            indent = "    "
        else:
            indent = ""
        for line in _split_long_string(object_):
            yield indent + repr(line) + "\n"
        if top_level:
            yield ")"

    else:
        yield repr(object_)


def _make_a_markup(begin, items_reprs, end, item_delimiter=",", as_dict=False):
    single_line_body = ", ".join(_form_single_line(items_reprs, as_dict))
    single_line_reproduction = begin + single_line_body + end
    if len(single_line_reproduction) <= 100 or not items_reprs:
        yield single_line_reproduction
    else:
        yield begin + "\n"
        for element in _form_multi_line(items_reprs, item_delimiter, as_dict):
            yield element
        yield end


def _form_single_line(items_representations, as_dict):
    kw_delimiter = ": " if as_dict else "="
    for keyword, value_reps in items_representations:
        if keyword:
            if as_dict:
                keyword = repr(keyword)
            preamble = keyword + kw_delimiter
        else:
            preamble = ""
        yield preamble + "".join(value_reps)


def _form_multi_line(items_reprs, item_delimiter, as_dict):
    kw_delimiter = ": " if as_dict else "="
    indent = "    "
    for keyword, value_reps in items_reprs:
        is_first = True
        for argument_reproduction in value_reps:
            if is_first and keyword is not None:
                if as_dict:
                    keyword = repr(keyword)
                preamble = keyword + kw_delimiter
            else:
                preamble = ""
            optional_break = (item_delimiter + "\n") if not argument_reproduction.endswith("\n") else ""
            is_first = False
            yield indent + preamble + argument_reproduction + optional_break


def _check_and_evaluate_arguments_specification(decorated_class):
    try:
        inspect.getfile(decorated_class.__init__)
    except TypeError:
        fields = getattr(decorated_class, "_fields", None)
        if not fields:
            raise TypeError("The class {} does not implement constructor.".format(decorated_class.__name__))
        return inspect.ArgSpec(*fields)

    if sys.version[0] < '3':
        args_spec = inspect.getargspec(decorated_class.__init__)
        unsupported = "keywords",
    else:
        args_spec = inspect.getfullargspec(decorated_class.__init__)
        unsupported = "varkw", "kwonlyargs", "kwonlydefaults"

    for kind in unsupported:
        if getattr(args_spec, kind, None):
            TypeError("pytocopy does not support syntax containing '%s'." % kind)
    return args_spec


def _implements_constructor(given_class):
    try:
        return _check_and_evaluate_arguments_specification(given_class)
    except TypeError:
        return


def _bind_defaults(spec_):
    if not spec_.defaults:
        return tuple((name, False, None) for name in spec_.args)
    defaults_len = len(spec_.defaults or ())
    blanks_len = len(spec_.args) - defaults_len
    has_default = (False,) * blanks_len + (True,) * defaults_len
    defaults = (None,) * blanks_len + spec_.defaults
    return tuple(zip(spec_.args, has_default, defaults))


def _get_attribute_or_raise(object_, name):
    if not hasattr(object_, name):
        msg = "{} has no '{}' attribute. Constructor args have to be named same as class attributes."
        raise AttributeError(msg.format(object_.__class__.__name__, name))
    return getattr(object_, name)


def _eval_py_name(namespace=None):
    if namespace is None:
        def make_name(cls):
            return "%s.%s" % (cls.__module__, getattr(cls, "__qualname__", cls.__name__))

    elif namespace == "":
        def make_name(cls):
            return cls.__name__

    elif isinstance(namespace, str):
        def make_name(cls):
            return "%s.%s" % (namespace, getattr(cls, "__qualname__", cls.__name__))
    else:
        raise ValueError("Namespace has to be string or None, got {}.".format(type(namespace).__name__))
    return make_name


def _collect_attributes(object_, spec_):
    any_skipped_already = False
    for argument_name, has_default, default_value in _bind_defaults(spec_)[1:]:
        value = _get_attribute_or_raise(object_, argument_name)
        if has_default:
            if value == default_value:
                any_skipped_already = True
            elif any_skipped_already:
                yield argument_name, value
            else:
                yield None, value
        else:
            yield None, value

    if spec_.varargs:
        variadic_arg = _get_attribute_or_raise(object_, spec_.varargs)
        if isinstance(variadic_arg, set):
            # order doesn't matter for a set, but its presentation needs to be kept always in the same order
            variadic_arg = sorted(variadic_arg)

        for attribute_object in variadic_arg:
            yield None, attribute_object


def _split_long_string(long_string, max_line_width=80):
    lines = long_string.split("\n")
    if not any(len(line) > max_line_width for line in lines):
        for not_last, line in enumerate(lines, 1 - len(lines)):
            yield line + ("\n" if not_last else "")
    else:
        words = long_string.split(" ")
        if not any(len(word) > max_line_width for word in words):
            line, pos = "", 0
            for not_last, word in enumerate(words, 1 - len(words)):
                word += " " if not_last else ""
                line += word
                pos += len(word)
                if pos >= 80:
                    yield line
                    line, pos = "", 0
            if line:
                yield line
        else:
            pos = 0
            while pos < len(long_string):
                yield long_string[pos:pos + max_line_width]
                pos += max_line_width
