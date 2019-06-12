# -*- coding: utf-8 -*-

"""
Sys_Book
~~~~~~~~~~~~~

系统数据字典
Created on 2017-07-19
@author: linkeddt.com
"""

from __future__ import unicode_literals

from django import forms

from bigtiger.forms.forms import BaseForm, OrderForm
from bigtiger.contrib.admin.models.sys_book import SysBookModel


class SysBookSearchForm(OrderForm):
    class_code = forms.CharField(label='分类编码', required=False)
    code = forms.CharField(label='字典编码', required=False)
    text = forms.CharField(label='字典名称', required=False)
    remark = forms.CharField(label='备注', required=False)

    def __init__(self, *args, **kwargs):
        super(SysBookSearchForm, self).__init__(*args, **kwargs)


class SysBookEditForm(BaseForm):
    _id = forms.CharField(required=False, widget=forms.HiddenInput)

    id = forms.CharField(label='Id', required=False, max_length=36)
    class_code = forms.CharField(label='分类编码', required=True, max_length=20)
    code = forms.CharField(label='字典编码', required=True, max_length=50)
    text = forms.CharField(label='字典名称', required=True, max_length=50)
    order_number = forms.IntegerField(
        label='排序号', required=True, max_value=99, min_value=0)
    is_enable = forms.ChoiceField(
        label='启用状态', required=True)
    remark = forms.CharField(label='备注', required=False, max_length=200,
                             widget=forms.Textarea(attrs={'rows': 2, 'cols': 100}))

    def __init__(self, *args, **kwargs):
        super(SysBookEditForm, self).__init__(*args, **kwargs)
        self.fields['is_enable'].choices = ((1, '是'), (0, '否'))


class SysBookEditFormAdmin(object):
    fieldsets = (
        ('基础信息', {'fields': ('class_code', 'code', 'text', 'order_number',
                             'is_enable', 'remark', ), 'classes': ('col-sm-12', 'form-horizontal',)}),
        ('隐藏域', {'fields': ('_id', 'id',),
                 'classes': ('col-sm-12', 'hidefield',)}),
    )
    readonly_fields = ()


class SysBookCreateFormAdmin(object):
    pass
