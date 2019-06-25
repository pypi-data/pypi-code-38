# coding: utf-8
from __future__ import absolute_import

import inspect


def _name_class(clazz):
    """
    :param clazz: Класс
    :type clazz: type
    :return: Генерация имени для класса
    :rtype: str
    """
    return '%s/%s' % (
        inspect.getmodule(clazz).__package__, clazz.__name__)


def name_action(action, pack_name=None):
    """
    :param action: Экшен
    :type action: objectpack.BaseAction
    :param pack_name: Имя пака (если не указано - генерится)
    :type pack_name: str
    :return: Генерация полного имени для :code:`action`
    :rtype: str
    """
    pack_name = pack_name or _name_class(action.parent.__class__)
    # имя будет иметь вид "пакет/КлассПака/КлассAction"
    return '%s/%s' % (pack_name, action.__class__.__name__)
