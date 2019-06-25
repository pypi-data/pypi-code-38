# coding: utf-8
"""
Классы исключений, обрабатываемых ObjectPack
"""
from __future__ import absolute_import

from itertools import chain

from six import python_2_unicode_compatible
from six import text_type
from six.moves import map


@python_2_unicode_compatible
class OverlapError(Exception):
    """
    Исключние пересечения интервальных моделей
    """
    def __init__(self, objects,
                 header=u'Имеются пересечения со следующими записями:'):
        assert objects, u'Не указаны объекты, с которыми произошло пересечение'

        self._header = header
        self._objects = objects

    def __str__(self):
        return text_type('\n- ').join(chain(
            (self._header,),
            map(text_type, self._objects)
        ))


class ValidationError(Exception):
    """
    Исключение валидации
    """
    def __init__(self, text):
        assert text, u'Не указан текст сообщения'
        super(ValidationError, self).__init__(text)
