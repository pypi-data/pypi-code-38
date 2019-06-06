# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

import re
from importlib import import_module

from django.core.exceptions import ImproperlyConfigured
from django.utils.six.moves import zip

"""Помойка функций для работы со строками"""


kb_layout = {
    'en': "`~!@#$%^&qwertyuiop[]asdfghjkl;'zxcvbnm,./QWERTYUIOP{}ASDFGHJKL:\"|ZXCVBNM<>?",
    'ru': "ёЁ!\"№;%:?йцукенгшщзхъфывапролджэячсмитьбю.ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭ/ЯЧСМИТЬБЮ,",
}
def change_kb_layout(input_str, frm='en', to='ru'):
    """Переключает неправильную раскладку RUS<->ENG"""
    if frm == to: return input_str
    try:
        frm_l = list(kb_layout[frm])
    except KeyError:
        raise ValueError("Unknown frm keyboard layout: %s." % (str(frm),))
    try:
        to_l = list(kb_layout[to])
    except KeyError:
        raise ValueError("Unknown to keyboard layout: %s." % (str(to),))
    table = dict((ord(char), to_l[ frm_l.index(char) ]) for char in frm_l if char in input_str)
    return input_str.translate(table)


def load_class_from_string(model_path):
    """
    Load by import a class or function by a string path like: 'module.models.MyModel'.
    This mecanizm allows extension and customization of the Entry model class.
    """
    dot = model_path.rindex('.')
    module_name = model_path[:dot]
    class_name = model_path[dot + 1:]
    try:
        _class = getattr(import_module(module_name), class_name)
        return _class
    except (ImportError, AttributeError):
        raise ImproperlyConfigured('%s cannot be imported' % model_path)


def autocorrect_email(email):
    """Попытка автоисправления адреса e-mail на основе самых частых ошибок"""
    def email_with_at(email):
        # user@@mail.ru -> user@mail.ru
        email = re.sub(r'@{2,}', '@', email)
        # множественное повторение адреса (видимо нервный копи-паст)
        # 'user@mail.ruuser@mail.ru'
        if email.count('@') > 1:
            # ['user@mail.ru', 'user@mail.ru']
            email_parts = list(map(''.join, list(zip(*[iter(email)]*(len(email)//email.count('@'))))))
            if len(set(email_parts)) == 1:  # все элементы равны
                email = email_parts[0]
        
        # начинают вводить с русской "с", потом переключают на латиницу, но "с" оставляют русской
        email = re.sub(r'^с([^а-яА-Я]{4,})$', r'c\1', email, count=1)
    
        # точки не могут быть по сторонам от .@.
        email = re.sub(r'[\s\.]*\@[\s\.]*', '@', email, count=1)
        # tld иногда c опечаткой - ".ry", ".r"
        email = re.sub(r'\s*\.+\s*(?:ry|r)$', '.ru', email, count=1)
        # tld часто отделяют пробелом или другим знаком препинания, а не точкой
        # SELECT REVERSE(LEFT(REVERSE(email),LOCATE('.',REVERSE(email)) - 1)) as tld, COUNT(id) as cnt
        # FROM subscription_digest WHERE is_active=1 GROUP BY tld ORDER BY cnt DESC;
        tlds = r"(ru|com|ua|net|lv|by|de|it|bg|cz|kz|il|fm|lt|ee|fr|gr|ca|uk|es|pl|su|be|nl|uz|org|se|ge|md|az|no|at|info|au|fi|jp|am|eu|hu|biz|sk|biz)"
        email = re.sub(r'[\s\,\.\;\:\/]+'+tlds+r'$', r".\1", email, count=1)
        # теперь смело сносим все остальные пробелы (а их тоже часто ставят)
        email = re.sub(r'\s+', '', email)
    
        # дописываем домен за юзеров
        email = re.sub(r"\@gmail?$", r"@gmail.com", email, count=1)
        email = re.sub(r"\@m[ae]il?$", r"@mail.ru", email, count=1)
        email = re.sub(r"\@list$", r"@list.ru", email, count=1)
        email = re.sub(r"\@inbo(?:x|ks)$", r"@inbox.ru", email, count=1)
        email = re.sub(r"\@bk$", r"@bk.ru", email, count=1)
        email = re.sub(r"\@yandex$", r"@yandex.ru", email, count=1)
        email = re.sub(r"\@rambler$", r"@rambler.ru", email, count=1)
        # в почтовом домене должна быть точка, а ее нет - додумаем, хуже не будет
        # user@ramblerru -> user@rambler.ru
        email = re.sub(r"\@([a-z0-9\-]+)"+tlds+r"$", r"@\1.\2", email, count=1)
        
        return email
    
    def email_without_at(email):
        # 'usermail.ru' -> 'user@mail.ru'
        # на основе выборки самых популярных доменов из нашей базы
        # SELECT SUBSTRING_INDEX(email,'@',-1) AS host, COUNT(id) AS cnt
        # FROM subscription_digest WHERE is_active=1 GROUP BY host ORDER BY cnt DESC LIMIT 25;
        email_services = ('mail.ru', 'yandex.ru', 'gmail.com', 'bk.ru',
                          'rambler.ru', 'list.ru', 'inbox.ru', 'ukr.net',
                          'yandex.ua', 'ya.ru', 'inbox.lv', 'yahoo.com',
                          'mail.ua', 'i.ua', 'tut.by', 'hotmail.com',
                          'icloud.com', 'bigmir.net', 'yandex.by',
                          'meta.ua', 'yandex.com', 'abv.bg', 'web.de', 'ngs.ru',
                          'lenta.ru',)
        email = re.sub(
            r'(' + "|".join([re.escape(x) for x in email_services]) + r')$',
            r'@\1', email, count=1
        )
        return email_with_at(email) if '@' in email else email
    
    # базовая обработка строки
    email = email.strip()
    email = email.lower()
    # убираем знаки препинания в конце строки адреса
    email = re.sub(r'\s*[^a-z0-9а-я]+$', '', email, count=1)
    
    if '@' in email:
        return email_with_at(email)
    else:
        return email_without_at(email)
