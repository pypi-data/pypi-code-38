# -*- coding: utf-8 -*-

from django.utils.html import escape

from table.utils import Accessor
from .base import Column


class ChoiceColumn(Column):
    SIM_NAO_C = (('S', 'Sim'), ('N', 'Não'))

    def __init__(self, field, header=None, choices=SIM_NAO_C, **kwargs):
        self.choices = choices
        super().__init__(field, header, **kwargs)

    def render(self, obj):
        obj_data = Accessor(self.field).resolve(obj)
        if obj_data:
            text = [name for val, name in self.choices if obj_data == val]
            try:
                text = text[0]
            except:
                text = ''
        else:
            text = ''
        return escape(text)
