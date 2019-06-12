# -*- coding: utf-8 -*-

"""
Sys_Cover
~~~~~~~~~~~~~

系统封面
Created on 2017-07-19
@author: linkeddt.com
"""

from __future__ import unicode_literals

from django import forms

from bigtiger.forms.forms import BaseForm, OrderForm
from bigtiger.forms.widgets import UploadFile

from bigtiger.contrib.admin.models.sys_cover import SysCoverModel


class SysCoverSearchForm(OrderForm):
    cover_title = forms.CharField(label='封面标题', required=False)

    def __init__(self, *args, **kwargs):
        super(SysCoverSearchForm, self).__init__(*args, **kwargs)


class SysCoverEditForm(BaseForm):
    _id = forms.CharField(required=False, widget=forms.HiddenInput)

    id = forms.CharField(label='Id', required=False, max_length=36)
    cover_title = forms.CharField(label='封面标题', required=True, max_length=20)
    cover_summary = forms.CharField(label='封面介绍', required=True, )
    cover_image = forms.CharField(
        label='封面图片', max_length=300, required=True, widget=UploadFile)
    cover_thumbnail = forms.CharField(
        label='封面缩略图', required=False, max_length=200, widget=forms.Textarea(attrs={'rows': 2, 'cols': 100}))
    upload_date = forms.DateTimeField(label='上传时间', required=False, widget=forms.TextInput(
        attrs={'class': 'form_text from_datetime', 'onClick': 'WdatePicker()'}))
    upload_user = forms.CharField(label='上传人', required=True, max_length=20)
    order_number = forms.IntegerField(
        label='排序号', required=True, max_value=99, min_value=0)
    remark = forms.CharField(label='备注', required=False, max_length=200,
                             widget=forms.Textarea(attrs={'rows': 2, 'cols': 100}))

    def __init__(self, *args, **kwargs):
        super(SysCoverEditForm, self).__init__(*args, **kwargs)


class SysCoverEditFormAdmin(object):
    fieldsets = (
        ('基础信息', {'fields': ('cover_title', 'cover_summary', 'cover_image',
                             'upload_user', 'order_number', ), 'classes': ('col-sm-12', 'form-horizontal',)}),
        ('隐藏域', {'fields': ('_id', 'id', 'cover_thumbnail', 'upload_date', 'remark', ),
                 'classes': ('col-sm-12', 'hidefield',)}),
    )
    readonly_fields = ()


class SysCoverCreateFormAdmin(object):
    pass
