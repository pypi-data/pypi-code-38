"""
Option class represents a single option in a list of options/enum

DEPRECATED from v1.1.0 version.
"""
import six
from datetime import datetime, date, time
from .mysix import is_identifier


class Option(object):
    """ A single option with code, name and text"""

    NOT_DEFINED = None
    """Not defined option."""

    NUMBER_TYPES = six.integer_types + (float, )
    DATE_TYPES = ()    # (datetime, date, time)

    AVAILABLE_CODE_TYPES = six.string_types + NUMBER_TYPES + DATE_TYPES
    AVAILABLE_CODE_TYPES_STR = ', '.join(t.__name__ for t in AVAILABLE_CODE_TYPES)

    def __init__(self, code, name, text=None):
        """
        Initialize an option
        :param code: The real value of an option or enum entry.
        :param name: The readable name of an option or enum entry. It can also be used as dot annotation.
                        It is alphanumeric or "_"  in uppercase and start with alphabet.
        :param text: The description of the option/enum entry. It's used to display. Can be i18n.
        """

        if not (code is None or isinstance(code, self.AVAILABLE_CODE_TYPES)):
            raise TypeError('Option code must be one of %s' % self.AVAILABLE_CODE_TYPES_STR)

        if name is not None:
            if not isinstance(name, six.string_types):
                raise ValueError('Option name must be string type.')

            if not (name[0].isalpha() and is_identifier(name) and name.isupper()):
                raise ValueError('Option name must be alphanumeric or "_"  in uppercase and start with alphabet.')

        if not ((code is None and name is None and text is None) or (code is not None and name is not None)):
            raise ValueError('Option code and name must be not None unless code, name and text are all None.')

        self.__code = code
        self.__name = name
        self.__text = text

        self.__code_type = type(code)

    @property
    def code(self):
        """The real value of an option or enum entry."""
        return self.__code

    @property
    def name(self):
        """
        The readable string of an option or enum entry. It's commonly uppercase.
        It can also be used as dot annotation.
        """
        return self.__name

    @property
    def text(self):
        """The description of the option/enum entry. It's used to display. Can be i18n."""
        return self.__text

    def get_text(self):
        """
        Returns `text` of the option. If `text` is None, returns `name` in lower case as text.
        If name is also None, return `None` object converted string.
        """
        return str(None) if self.name is None else self.name.lower() if self.text is None else self.text

    def __repr__(self):
        return "<%s code=%s name=%s text=%s>" % (self.__class__.__name__, self.code, self.name, self.text)

    def __str__(self):
        return str(self.code)

    # Compare Operators

    def __op_cmp_check__(self, op, other):
        """
        Check if self is compatible with `other` on operation `op`
        :param op: operation such as "+", "-" and so on
        :param other: The other value of the operation to be compared with self.
        :return: void.  (raise error directly if not compatible)
        """
        other_is_option = False
        if isinstance(other, Option):
            other = other.code
            other_is_option = True
        type_other = type(other)

        if isinstance(other, self.NUMBER_TYPES + self.DATE_TYPES) and isinstance(self.code, self.NUMBER_TYPES + self.DATE_TYPES):
            pass
        elif isinstance(other, six.string_types) and isinstance(self.code, six.string_types):
            pass
        elif other is None or self.code is None or self == Option.NOT_DEFINED:
            pass
        else:
            raise TypeError("'%s' not supported between instances of 'Option(%s)' and '%s'" % (
                op, self.__code_type.__name__,
                'Option(%s)' % type_other.__name__ if other_is_option else type_other.__name__
            ))

    # if six.PY2:
    #     def __cmp__(self, other):
    #         self.__op_cmp_check__('==', other)
    #
    #         if isinstance(other, Option):
    #             if self.code == other.code and self.name == other.name and self.text == other.text:
    #                 return 0
    #             elif self.code < other.code:
    #                 return -1
    #             else:
    #                 return 1
    #         else:
    #             return self.code.__cmp__(other)

    def __eq__(self, other):
        self.__op_cmp_check__('==', other)

        if isinstance(other, Option):
            return self.code == other.code and self.name == other.name and self.text == other.text
        else:
            return self.code == other

    def __hash__(self):
        """return hash of `code` to ensure key access to `set`, `dict` or other hash based collection"""
        # return super(Option, self).__hash__()
        return self.code.__hash__()

    def __lt__(self, other):
        self.__op_cmp_check__('<', other)

        return self.code < (other.code if isinstance(other, Option) else other)

    def __le__(self, other):
        self.__op_cmp_check__('<=', other)

        return self.code <= (other.code if isinstance(other, Option) else other)

    def __gt__(self, other):
        self.__op_cmp_check__('>', other)

        return self.code > (other.code if isinstance(other, Option) else other)

    def __ge__(self, other):
        self.__op_cmp_check__('>=', other)

        return self.code >= (other.code if isinstance(other, Option) else other)

    # Math Operators

    def __op_math_check__(self, op, other):
        """
        Check if self is compatible with `other` on math operation `op`
        :param op: operation such as "+", "-" and so on
        :param other: The other value of the operation to be compared with self.
        :return: void.  (raise error directly if not compatible)
        """
        other_is_option = False
        if isinstance(other, Option):
            other = other.code
            other_is_option = True
        type_other = type(other)

        if isinstance(other, self.NUMBER_TYPES) and isinstance(self.code, self.NUMBER_TYPES):
            pass
        elif isinstance(other, six.string_types) and isinstance(self.code, six.string_types):
            pass
        elif isinstance(other, self.DATE_TYPES) and isinstance(self.code, self.DATE_TYPES):
            pass
        else:
            raise TypeError("'%s' not supported between instances of 'Option(%s)' and '%s'" % (
                op, self.__code_type.__name__,
                'Option(%s)' % type_other.__name__ if other_is_option else type_other.__name__
            ))

    def __op_num_check__(self, op, val):

        val, val_is_option = (val.code, True) if isinstance(val, Option) else (val, False)
        type_val = type(val)
        type_str = 'Option(%s)' % type_val.__name__ if val_is_option else type_val.__name__

        if not isinstance(val, self.NUMBER_TYPES):
            raise TypeError("'%s' not supported on instances of '%s'" % (op, type_str))

    def __op_int_check__(self, op, val):

        val, val_is_option = (val.code, True) if isinstance(val, Option) else (val, False)
        type_val = type(val)
        type_str = 'Option(%s)' % type_val.__name__ if val_is_option else type_val.__name__

        if not isinstance(val, six.integer_types):
            raise TypeError("'%s' not supported on instances of '%s'" % (op, type_str))

    def __neg__(self):
        self.__op_num_check__('-(negative)', self)

        return - self.code

    def __pos__(self):
        self.__op_num_check__('+(positive)', self)

        return + self.code

    def __abs__(self):
        self.__op_num_check__('abs', self)

        return abs(self.code)

    def __int__(self):
        return int(self.code)

    def __float__(self):
        return float(self.code)

    def __invert__(self):
        self.__op_int_check__('~', self)

        return ~ self.code

    def __lshift__(self, other):
        self.__op_int_check__('<<', self)
        self.__op_int_check__('<<', other)

        return self.code << other

    def __rlshift__(self, other):
        self.__op_int_check__('<<', self)
        self.__op_int_check__('<<', other)

        return other << self.code

    def __rshift__(self, other):
        self.__op_int_check__('>>', self)
        self.__op_int_check__('>>', other)

        return self.code >> other

    def __rrshift__(self, other):
        self.__op_int_check__('>>', self)
        self.__op_int_check__('>>', other)

        return other >> self.code

    def __add__(self, other):
        self.__op_math_check__('+', other)

        return self.code + (other.code if isinstance(other, Option) else other)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        self.__op_math_check__('-', other)

        return self.code - (other.code if isinstance(other, Option) else other)

    def __rsub__(self, other):
        self.__op_math_check__('-', other)

        return (other.code if isinstance(other, Option) else other) - self.code

    def __mul__(self, other):
        self.__op_num_check__('*', other)

        return self.code * (other.code if isinstance(other, Option) else other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        self.__op_num_check__('/', self)
        self.__op_num_check__('/', other)

        return self.code.__truediv__(other.code if isinstance(other, Option) else other)

    def __rtruediv__(self, other):
        self.__op_num_check__('/', self)
        self.__op_num_check__('/', other)

        return self.code.__rtruediv__(other.code if isinstance(other, Option) else other)

    def __floordiv__(self, other):
        self.__op_num_check__('//', self)
        self.__op_num_check__('//', other)

        return self.code.__floordiv__(other.code if isinstance(other, Option) else other)

    def __rfloordiv__(self, other):
        self.__op_num_check__('//', self)
        self.__op_num_check__('//', other)

        return self.code.__rfloordiv__(other.code if isinstance(other, Option) else other)

    # compatible with PY2 without "from __future__ import division"
    def __div__(self, other):
        self.__op_num_check__('/', self)
        self.__op_num_check__('/', other)

        return self.code.__div__(other.code if isinstance(other, Option) else other)

    def __rdiv__(self, other):
        self.__op_num_check__('/', self)
        self.__op_num_check__('/', other)

        return self.code.__rdiv__(other.code if isinstance(other, Option) else other)

    def __divmod__(self, other):
        self.__op_num_check__('%', self)
        self.__op_num_check__('%', other)

        return self.code.__divmod__(other.code if isinstance(other, Option) else other)

    def __rdivmod__(self, other):
        self.__op_num_check__('%', self)
        self.__op_num_check__('%', other)

        return self.code.__rdivmod__(other.code if isinstance(other, Option) else other)

    def __mod__(self, other):

        self.__op_num_check__('%', self)
        self.__op_num_check__('%', other)

        return self.code.__mod__(other.code if isinstance(other, Option) else other)

    def __rmod__(self, other):
        self.__op_num_check__('%', self)
        self.__op_num_check__('%', other)

        return self.code.__rmod__(other.code if isinstance(other, Option) else other)


Option.NOT_DEFINED = Option(None, None, None)


__all__ = ('Option', )
