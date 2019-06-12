# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms

from bigtiger.forms.forms import BaseForm, OrderForm
from bigtiger.contrib.admin.widgets import TreeView
from bigtiger.contrib.admin.models.auth_group import AuthGroupModel


class AuthGroupSearchForm(OrderForm):
    group_name = forms.CharField(label='角色名称', required=False)

    def __init__(self, *args, **kwargs):
        super(AuthGroupSearchForm, self).__init__(*args, **kwargs)


class AuthGroupEditForm(BaseForm):
    _id = forms.CharField(required=False, widget=forms.HiddenInput)

    id = forms.CharField(label='Id', required=False, max_length=36)
    name = forms.CharField(label='角色名称', required=True, max_length=50)
    type = forms.CharField(label='组分类', required=True, max_length=2)
    remark = forms.CharField(label='角色说明', required=False, max_length=200,
                             widget=forms.Textarea(attrs={'rows': 2, 'cols': 100}))
    permissions = forms.CharField(
        label='', widget=TreeView(attrs={}), required=False)

    def __init__(self, *args, **kwargs):
        super(AuthGroupEditForm, self).__init__(*args, **kwargs)
        self.fields['type'].initial = '01'

    def clean_id(self):
        _id = str(self.cleaned_data['id'])
        if _id != self.cleaned_data['_id']:
            service = AuthGroupModel()
            d = service.get_one(_id)
            if d is not None:
                raise forms.ValidationError('Id已存在。')
        return _id


class AuthGroupEditFormAdmin(object):
    fieldsets = (
        ('基础信息', {'fields': ('name', 'remark', ),
                  'classes': ('col-sm-12', 'form-horizontal',)}),
        ('角色权限', {'fields': ('permissions', ),
                  'classes': ('col-sm-12', 'form-horizontal',)}),
        ('隐藏域', {'fields': ('_id', 'id', 'type',),
                 'classes': ('col-sm-12', 'hidefield',)}),
    )
    readonly_fields = ()


class AuthGroupCreateFormAdmin(object):
    pass
