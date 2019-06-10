import string
from django import template
from django.template.defaultfilters import stringfilter


register = template.Library()


@register.filter(is_safe=True)
@stringfilter
def capwords(value, sep=None):
    """
    Split the argument into words using str.split(), capitalize each word using
    str.capitalize(), and join the capitalized words using str.join(). If the
    optional second argument sep is absent or None, runs of whitespace characters
    are replaced by a single space and leading and trailing whitespace are
    removed, otherwise sep is used to split and join the words.
    """
    return string.capwords(value, sep=sep)


@register.filter(is_safe=True)
@stringfilter
def capitalize(value):
    """ Return a copy of the string with its first character capitalized and the rest lowercased. """
    return value.capitalize()


@register.filter(is_safe=False)
@stringfilter
def count(value, sub, start=None, end=None):
    """
    Return the number of non-overlapping occurrences of substring sub in the range [start, end].
    Optional arguments start and end are interpreted as in slice notation.
    """
    return value.count(sub, start, end)


@register.filter(is_safe=False)
def endswith(value, suffix, start=None, end=None):
    return value.endswith(suffix, start, end)


@register.filter(is_safe=True)
@stringfilter
def swapcase(value):
    return value.swapcase()


@register.filter
@stringfilter
def strip(value, chars=None):
    return value.strip(chars=chars)


@register.filter(is_safe=False)
@stringfilter
def startswith(value, prefix, start=None, end=None):
    return value.startswith(prefix, start, end)


@register.filter(is_safe=False)
@stringfilter
def index(value, sub, start=None, end=None):
    return value.index(sub, start, end)


@register.filter(is_safe=False)
@stringfilter
def isalnum(value):
    return value.isalnum()


@register.filter(is_safe=False)
@stringfilter
def isalpha(value):
    return value.isalpha()


@register.filter(is_safe=False)
@stringfilter
def isascii(value):
    return value.isascii()


@register.filter(is_safe=False)
@stringfilter
def isdecimal(value):
    return value.isdecimal()


@register.filter(is_safe=False)
@stringfilter
def isdigit(value):
    return value.isdigit()


@register.filter(is_safe=False)
@stringfilter
def isidentifier(value):
    return value.isidentifier()


@register.filter(is_safe=False)
@stringfilter
def islower(value):
    return value.islower()


@register.filter(is_safe=False)
@stringfilter
def isnumeric(value):
    return value.isnumeric()


@register.filter(is_safe=False)
@stringfilter
def isprintable(value):
    return value.isprintable()


@register.filter(is_safe=False)
@stringfilter
def isspace(value):
    return value.isspace()


@register.filter(is_safe=False)
@stringfilter
def istitle(value):
    return value.istitle()


@register.filter(is_safe=False)
@stringfilter
def isupper(value):
    return value.isupper()


@register.filter(is_safe=True)
@stringfilter
def lstrip(value, chars=None):
    return value.lstrip(chars)


@register.filter
@stringfilter
def partition(value, sep):
    return value.partition(sep)


@register.filter
@stringfilter
def rindex(value, sub, start=None, end=None):
    return value.rindex(sub, start, end)


@register.filter
@stringfilter
def rpartition(value, sep):
    return value.rpartition(sep=sep)


@register.filter
@stringfilter
def rsplit(value, sep=None, maxsplit=-1):
    return value.rsplit(sep=sep, maxsplit=maxsplit)


@register.filter
@stringfilter
def rstrip(value, chars=None):
    return value.rstrip(chars)


@register.filter
@stringfilter
def split(value, sep=None, maxsplit=-1):
    return value.split(sep=sep, maxsplit=maxsplit)


@register.filter
@stringfilter
def splitlines(value, keepends=False):
    return value.splitlines(keepends=keepends)


@register.filter
@stringfilter
def title(value):
    return value.title()


@register.filter
@stringfilter
def translate(value, table):
    return value.translate(table)
