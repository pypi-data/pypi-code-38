# coding: utf-8
from __future__ import absolute_import

from datetime import datetime


class TemplateTags(object):
    """
    Шаблонные теги

    Используется для того, чтобы задавать константы в шаблоне.
    Например, текущая дата будет задаваться через константу DATE_TIME,
    произвольные константы можно передавать через конструктор

    """

    def __init__(self, **kw):
        """
        Формируется словарь шаблонных тегов из переданных параметров
        """
        self.tags = {'DATE_NOW': datetime.now()}

        self.tags.update(kw)

    def get(self, key):
        """
         Получение значений из словаря тегов
        :param key: ключ словаря
        :result: значение словаря
        """
        return self.tags[key]
