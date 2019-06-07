# coding: utf-8
from __future__ import absolute_import

import six


def convert_dict(dictionary):
    """
    Конвертирует значения из словаря в пригодные для записи в rtf-файл
    """
    new_dictionary = {}
    for key, value in dictionary.items():
        #if not isinstance(value, basestring):
        try:
            value = six.text_type(value)
        except Exception:
            continue
        res = []
        for v in value:
            u_code = ord(v)
            res.append('\\u%s\\\'3f' % str(u_code).rjust(4, '0'))

        new_dictionary[key] = ''.join(res)
    return new_dictionary


def do_replace(text, params):
    """
    Ищет знаки '#' в тексте rtf-шаблона и подставляет значения из словаря
    """
    for key_param, value in params.items():
        if key_param in text:
            text = text.replace('#%s#' % key_param, value)
    return text
