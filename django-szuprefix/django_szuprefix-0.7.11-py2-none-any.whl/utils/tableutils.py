# -*- coding:utf-8 -*-
from django.db.models import Model

from .datautils import queryset2dictlist

__author__ = 'denishuang'


def column_outout(v):
    if isinstance(v, Model):
        return str(v)
    if hasattr(v, 'update_or_create'):  # a Relative Manager ?
        return ";".join([str(a) for a in v.all()])
    return v


def table2dict(table):
    d = {}
    d['columns'] = [
        dict(name=c.name,
             orderable=c.orderable,
             default=c.default,
             verbose_name=c.verbose_name,
             header=c.header
             )
        for c in table.columns
        ]
    if hasattr(table, 'page'):
        page = table.page
        rows = page.object_list
        d['pager'] = dict(current=page.number, total=page.paginator.count, per_page=page.paginator.per_page)
    else:
        rows = table.rows
    bcs = table.base_columns
    d['data'] = [dict([(c, column_outout(r.get_cell(c))) for c in bcs.keys()]) for r in rows]
    return d
