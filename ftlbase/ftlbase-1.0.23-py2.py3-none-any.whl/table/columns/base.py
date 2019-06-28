#!/usr/bin/env python
# coding: utf-8

from django.utils.formats import localize
from django.utils.html import escape
from django.utils.safestring import mark_safe

from table.utils import Accessor, AttributesDict


class Column(object):
    """ Represents a single column.
    """

    instance_order = 0

    def __init__(self, field=None, header=None, attrs=None, header_attrs=None,
                 header_row_order=0, sortable=True, searchable=True, safe=False,
                 visible=True, space=True, render_format=None, totals=False, decimal_places=2, footer=None):
        self.field = field
        self.attrs = attrs or {}
        self.sortable = sortable
        self.searchable = searchable
        self.safe = safe
        self.visible = visible
        # Acho que informa se uma coluna é um simples espaço ou é um campo real,
        # não gera searchable, orderable, visible no javascript
        self.space = space
        self.renderFormat = render_format
        self.decimal_places = decimal_places
        self.totals = totals  # Se totaliza ou não no rodapé da table
        self.footer = footer  # Mensagem no footer se ele aparecer

        self.header = ColumnHeader(header, header_attrs, header_row_order)

        self.instance_order = Column.instance_order
        Column.instance_order += 1

    def __str__(self):
        return self.header.text

    def render(self, obj):
        text = Accessor(self.field).resolve(obj)
        if text:
            # text = "%s" % Accessor(self.field).resolve(obj)
            text = "%s" % text
            text = localize(text, use_l10n=True)
            # text = localize(Accessor(self.field).resolve(obj), use_l10n=True)
            # if isinstance(text, str):
            #     text = ugettext_lazy(text)
            # text = ugettext_lazy(text)
            # print(self.field)
            # print(obj)
            # if isinstance(getattr(obj, self.field), Decimal):
            #     print(getattr(obj, self.field))
            #     print(text)
            # print(_(text))
        else:
            text = ''
        if self.safe:
            return mark_safe(text)
        return escape(text)


class BoundColumn(object):
    """ A run-time version of Column. The difference between
        BoundColumn and Column is that BoundColumn objects include the
        relationship between a Column and a object. In practice, this
        means that a BoundColumn knows the "field value" given to the
        Column when it was declared on the Table.
    """

    def __init__(self, obj, column):
        self.obj = obj
        self.column = column
        self.base_attrs = column.attrs.copy()

        # copy non-object-related attributes to self directly
        self.field = column.field
        self.sortable = column.sortable
        self.searchable = column.searchable
        self.safe = column.safe
        self.visible = column.visible
        self.header = column.header

    @property
    def html(self):
        text = self.column.render(self.obj)
        if text is None:
            return ''
        else:
            return text

    @property
    def attrs(self):
        attrs = {}
        for attr_name, attr in self.base_attrs.items():
            if callable(attr):
                attrs[attr_name] = attr(self.obj, self.field)
            elif isinstance(attr, Accessor):
                attrs[attr_name] = attr.resolve(self.obj)
            else:
                attrs[attr_name] = attr
        return AttributesDict(attrs).render()


class ColumnHeader(object):
    def __init__(self, text=None, attrs=None, row_order=0):
        self.text = text
        self.base_attrs = attrs or {}
        self.row_order = row_order

    @property
    def attrs(self):
        return AttributesDict(self.base_attrs).render()
