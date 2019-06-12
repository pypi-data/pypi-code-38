# -*- coding: utf-8 -*-

"""
Sys_Update_Log
~~~~~~~~~~~~~

系统更新日志
Created on 2017-07-19
@author: linkeddt.com
"""

from __future__ import unicode_literals

from django import forms

from bigtiger.forms.forms import BaseForm, OrderForm
from bigtiger.contrib.admin.models.sys_update_log import SysUpdateLogModel


class SysUpdateLogSearchForm(OrderForm):
    """
    text = forms.CharField(label='文字：', required=False)
    list = forms.ChoiceField(label='下拉框：')
    datetiem = forms.DateField(label='日期：', required=False, widget=forms.TextInput(attrs={'class': 'form-control input-sm','onClick':'WdatePicker()'}))
    """

    def __init__(self, *args, **kwargs):
        super(SysUpdateLogSearchForm, self).__init__(*args, **kwargs)


class SysUpdateLogEditForm(BaseForm):
    _id = forms.CharField(required=False, widget=forms.HiddenInput)

    version_number = forms.CharField(label='版本号', required=True, max_length=50)
    public_date = forms.DateTimeField(label='发布时间', required=True, widget=forms.TextInput(
        attrs={'class': 'form_text from_datetime', 'onClick': 'WdatePicker()'}))
    update_content = forms.CharField(label='更新内容', required=True, )
    remark = forms.CharField(label='备注', required=False, max_length=200,
                             widget=forms.Textarea(attrs={'rows': 2, 'cols': 100}))

    def __init__(self, *args, **kwargs):
        super(SysUpdateLogEditForm, self).__init__(*args, **kwargs)

    def clean_version_number(self):
        version_number = str(self.cleaned_data['version_number'])
        if version_number != self.cleaned_data['_id']:
            service = SysUpdateLogModel()
            d = service.get_one(version_number)
            if d is not None:
                raise forms.ValidationError('版本号已存在。')
        return version_number


class SysUpdateLogEditFormAdmin(object):
    fieldsets = (
        ('基础信息', {'fields': ('version_number', 'public_date', 'update_content',
                             'remark', ), 'classes': ('col-sm-12', 'form-horizontal',)}),
        ('隐藏域', {'fields': ('_id',), 'classes': ('col-sm-12', 'hidefield',)}),
    )
    readonly_fields = ()


class SysUpdateLogCreateFormAdmin(object):
    pass
