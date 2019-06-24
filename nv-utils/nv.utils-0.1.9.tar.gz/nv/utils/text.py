"""
Helpers to manipulate text.
"""

import re
import unicodedata


__all__ = ['remove_accents', 'remove_line_breaks', 'remove_non_digits', 'concatenate', 'underscorize', 'camelize', 'humanize']


def remove_accents(text):
    """
    Remove accents from string.
    :param text: input string.
    :returns: The processed String.
    """
    text = unicodedata.normalize('NFC', text)
    text = text.encode('ascii', 'ignore')
    text = text.decode("utf-8")
    return str(text)


def remove_line_breaks(text):
    """
    Remove line breaks from a text.
    :param text: text
    :return: text with no line breaks
    """
    return "".join(text.splitlines())


def remove_non_digits(text):
    """
    Eliminates any non-digit character from a text via regEx matching.
    :param text: original text.
    :return: original text excluding any non-digits.
    """
    resp, _ = re.subn("[^\d]", "", text)
    return resp


def concatenate(lst, sep=' '):
    """
    Concatenate all non-null / non-blank items of a list separated by a single sep.
    :param lst: list
    :param sep: separator
    :return:
    """
    return sep.join(str(el) for el in lst if el)


"""
The utilities below were based, with some small modifications, on:
https://github.com/jpvanhal/inflection/blob/master/inflection.py

Copyright (C) 2012-2015 Janne Vanhala

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

def underscorize(text):
    """
    Make an underscored, lowercase form from the expression in the string.
    Example::
        >>> underscore("DeviceType")
        "device_type"
    As a rule of thumb you can think of :func:`underscore` as the inverse of
    :func:`camelize`, though there are cases where that does not hold::
        >>> camelize(underscore("IOError"))
        "IoError"
    """
    text = re.sub(r"([A-Z]+)([A-Z][a-z])", r'\1_\2', text)
    text = re.sub(r"([a-z\d])([A-Z])", r'\1_\2', text)
    text = text.replace("-", "_")
    return text.lower()


def camelize(text, uppercase_first_letter=False, exceptions=None):
    """
    Convert strings to CamelCase.
    Examples::
        >>> camelize("device_type")
        "DeviceType"
        >>> camelize("device_type", False)
        "deviceType"
    :func:`camelize` can be thought of as a inverse of :func:`underscore`,
    although there are some cases where that does not hold::
        >>> camelize(underscorize("IOError"))
        "IoError"
    :param uppercase_first_letter: if set to `True` :func:`camelize` converts
        strings to UpperCamelCase. If set to `False` :func:`camelize` produces
        lowerCamelCase. Defaults to `True`.
    """
    exceptions = exceptions or set()
    text = text.upper()
    if uppercase_first_letter:
        return "".join(s if s.upper() in exceptions else s.title() for s in text.split("_"))
        # return re.sub(r"(?:^|_)(.)", lambda m: m.group(1).upper(), text)
    else:
        return text[0].lower() + camelize(text, uppercase_first_letter=True)[1:]


def humanize(text):
    """
    Capitalize the first word and turn underscores into spaces creating pretty output.
    Examples::
        >>> humanize("employee_salary")
        "Employee salary"
    """
    text = text.replace('_', ' ')
    text = re.sub(r"(?i)([a-z\d]*)", lambda m: m.group(1).lower(), text)
    text = re.sub(r"^\w", lambda m: m.group(0).upper(), text)
    return text
