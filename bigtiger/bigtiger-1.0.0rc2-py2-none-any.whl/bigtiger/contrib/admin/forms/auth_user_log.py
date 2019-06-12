# -*- coding: utf-8 -*-

"""
用户管理|用户日志
Created on 2017-07-19
@author: linkeddt.com
"""
from __future__ import unicode_literals

from django import forms

from bigtiger.forms.forms import BaseForm, OrderForm
from bigtiger.contrib.admin.widgets import QuickDateSelectorField
from bigtiger.contrib.admin.models.auth_user_log import AuthUserLogModel


class AuthUserLogSearchForm(OrderForm):
    action_flag = forms.ChoiceField(label='动作标志：')
    status = forms.ChoiceField(label='执行状态：')
    daterange = QuickDateSelectorField(label='操作时间：', required=False)
    action_class = forms.CharField(label='操作类名：', required=False)

    def __init__(self, *args, **kwargs):
        super(AuthUserLogSearchForm, self).__init__(*args, **kwargs)
        self.fields['action_flag'].choices = (
            (-1, '全部'), (0, '登陆'), (1, '其他'),)
        self.fields['status'].choices = ((0, '全部'), (1, '成功'), (2, '失败'),)


class AuthUserLogEditForm(BaseForm):
    _id = forms.CharField(required=False, widget=forms.HiddenInput)

    id = forms.CharField(label='Id', required=True, max_length=36)
    user_id = forms.CharField(label='操作用户', required=True, max_length=36)
    action_flag = forms.ChoiceField(label='动作标志', required=True)
    action_time = forms.DateTimeField(label='操作时间', required=True, widget=forms.TextInput(
        attrs={'class': 'form_text from_datetime', 'onClick': 'WdatePicker()'}))
    ip = forms.CharField(label='IP', required=True, max_length=32)
    action_class = forms.CharField(label='操作类名', required=True, )
    action_object = forms.CharField(label='操作对象', required=True, )
    action_handler = forms.CharField(
        label='执行处理器', required=True, max_length=200, widget=forms.Textarea(attrs={'rows': 2, 'cols': 100}))
    status = forms.ChoiceField(label='执行状态', required=True)
    status_note = forms.CharField(label='状态说明', required=False, )

    def __init__(self, *args, **kwargs):
        super(AuthUserLogEditForm, self).__init__(*args, **kwargs)
        self.fields['action_flag'].choices = ((0, '登陆'), (1, '其他'),)
        self.fields['status'].choices = ((1, '成功'), (2, '失败'),)


class AuthUserLogEditFormAdmin(object):
    fieldsets = (
        ('基础信息', {'fields': ('action_flag', 'ip', 'action_class', 'action_object',
                             'action_handler', 'status', 'status_note', ), 'classes': ('col-sm-12', 'form-horizontal',)}),
        ('隐藏域', {'fields': ('_id', 'id', 'user_id', 'action_time',),
                 'classes': ('col-sm-12', 'hidefield',)}),
    )
    readonly_fields = ()


class AuthUserLogCreateFormAdmin(object):
    pass
