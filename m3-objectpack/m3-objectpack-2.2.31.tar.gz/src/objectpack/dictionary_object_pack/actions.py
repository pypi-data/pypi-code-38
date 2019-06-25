# coding: utf-8
from __future__ import absolute_import

from objectpack.actions import ObjectPack
from objectpack.ui import ModelEditWindow
import six


class DictionaryObjectPack(ObjectPack):
    """
    Набор действий для простых справочников
    """
    add_to_menu = True

    columns = [
        {
            'data_index': 'code',
            'header': u'код',
            'searchable': True
        },
        {
            'data_index': '__unicode__' if six.PY2 else '__str__',
            'header': u'наименование',
            'searchable': True
        },
    ]

    def __init__(self, *args, **kwargs):
        """
        Инициализация
        """
        if not any([self.edit_window, self.add_window]):
            self.edit_window = self.add_window = (
                ModelEditWindow.fabricate(self.model)
            )
        super(DictionaryObjectPack, self).__init__(*args, **kwargs)

    def extend_menu(self, menu):
        """
        Интеграция в Главное Меню
        """
        if self.add_to_menu:
            return menu.dicts(menu.Item(self.title, self))
