# -*- coding: utf-8 -*-

"""
用户管理|权限信息
Created on 2017-07-19
@author: linkeddt.com
"""

from __future__ import unicode_literals

from django import forms

from bigtiger.forms.forms import BaseForm, OrderForm
from bigtiger.utils.tree import depth_find_childs
from bigtiger.contrib.admin.models.auth_permission import AuthPermissionModel


class AuthPermissionSearchForm(OrderForm):
    def __init__(self, *args, **kwargs):
        super(AuthPermissionSearchForm, self).__init__(*args, **kwargs)


class AuthPermissionEditForm(BaseForm):
    _id = forms.CharField(required=False, widget=forms.HiddenInput)

    _new_parent_id = forms.CharField(
        label='新上级菜单', required=False, widget=forms.HiddenInput)
    parent_id = forms.ChoiceField(label='上级菜单', required=False)

    id = forms.CharField(label='菜单ID', required=True, max_length=36)
    menu_name = forms.CharField(label='菜单名称', required=True, max_length=100)
    menu_url = forms.CharField(label='菜单URL', required=False, max_length=200,
                               widget=forms.Textarea(attrs={'rows': 2, 'cols': 100}))
    menu_url_alias = forms.CharField(label='菜单URL别名', required=False, max_length=200,
                                     widget=forms.Textarea(attrs={'rows': 2, 'cols': 100}))
    menu_url_debug = forms.CharField(label='菜单URL调试', required=False, max_length=200,
                                     widget=forms.Textarea(attrs={'rows': 2, 'cols': 100}))
    menu_target = forms.ChoiceField(label='菜单目标', required=False)
    fast_url = forms.CharField(label='快捷URL', required=False, max_length=200,
                               widget=forms.Textarea(attrs={'rows': 2, 'cols': 100}))
    big_icon = forms.CharField(label='大图标', required=False, max_length=200,
                               widget=forms.Textarea(attrs={'rows': 2, 'cols': 100}))
    small_icon = forms.CharField(label='小图标', required=False, max_length=200,
                                 widget=forms.Textarea(attrs={'rows': 2, 'cols': 100}))
    is_important = forms.ChoiceField(
        label='是否重要', required=True)
    is_open = forms.ChoiceField(
        label='是否展开', required=True)
    is_enable = forms.ChoiceField(
        label='是否启用', required=True)
    is_cache = forms.ChoiceField(
        label='是否缓存', required=False)
    is_cross = forms.ChoiceField(
        label='是否跨域', required=False)
    is_debug = forms.ChoiceField(
        label='是否调试', required=False)
    badge = forms.CharField(label='徽章', required=False, max_length=50)
    order_number = forms.IntegerField(
        label='排序号', required=False, max_value=9999, min_value=0)
    status = forms.ChoiceField(label='显示模式', required=True)
    remark = forms.CharField(label='备注', required=False, max_length=200,
                             widget=forms.Textarea(attrs={'rows': 2, 'cols': 100}))

    def __init__(self, *args, **kwargs):
        super(AuthPermissionEditForm, self).__init__(*args, **kwargs)
        self.fields['is_important'].choices = ((0, '否'), (1, '是'))
        self.fields['is_open'].choices = ((0, '否'), (1, '是'))
        self.fields['is_enable'].choices = ((1, '是'), (0, '否'))
        self.fields['is_cache'].choices = ((0, '否'), (1, '是'))
        self.fields['is_cross'].choices = ((0, '否'), (1, '是'))
        self.fields['is_debug'].choices = ((0, '否'), (1, '是'))
        self.fields['status'].choices = ((1, '显示菜单'), (0, '隐示菜单'))
        self.fields['menu_target'].choices = (('inner', 'inner'), ('iframe', 'iframe'), ('iframe_scroll', 'iframe_scroll'),)

        self.parent_id_choice()

    def parent_id_choice(self):
        menu_id = self.context.get('pk', None)
        service = AuthPermissionModel()
        lst = service.get_list_system_tree()

        # 在修改的时候，可选择的上级菜单排除自己及自己的下级菜单。
        childs_menu = depth_find_childs(lst, join=lambda item, parent_item: item['parent_id']
                                        == parent_item['id'], parent_node=lambda item: item['id'] == menu_id)
        exclude_ids = [item['id'] for item in childs_menu]
        exclude_ids.append(menu_id)

        self.fields['parent_id'].choices = (
            (item['id'], self._rename_menu(item)) for item in lst if item['id'] not in exclude_ids)

    def _rename_menu(self, row):
        """重命名菜单名称"""

        depth = row['depth']
        menu_name = row['menu_name']
        if depth == 0:
            return menu_name
        return u'　　' * depth + '|-' + menu_name


class AuthPermissionCreateForm(AuthPermissionEditForm):

    def parent_id_choice(self):
        service = AuthPermissionModel()
        lst = service.get_list_system_tree()
        self.fields['parent_id'].choices = (
            (item['id'], self._rename_menu(item)) for item in lst)


class AuthPermissionEditFormAdmin(object):
    fieldsets = (
        ('基础信息', {'fields': ('parent_id', 'id', 'menu_name', 'menu_url', 'menu_url_alias', 'menu_url_debug', 'menu_target', 'fast_url', 'big_icon', 'small_icon', 'is_important',
                             'is_open', 'is_enable', 'is_cache', 'is_cross', 'is_debug', 'badge', 'order_number', 'status', 'remark', ), 'classes': ('col-sm-12', 'form-horizontal',)}),
        ('隐藏域', {'fields': ('_id', '_new_parent_id', ),
                 'classes': ('col-sm-12', 'hidefield',)}),
    )
    readonly_fields = ('id',)


class AuthPermissionCreateFormAdmin(object):
    fieldsets = (
        ('基础信息', {'fields': ('parent_id', 'menu_name', 'menu_url', 'menu_url_alias', 'menu_url_debug', 'menu_target', 'fast_url', 'big_icon', 'small_icon', 'is_important',
                             'is_open', 'is_enable', 'is_cache', 'is_cross', 'is_debug', 'badge', 'order_number', 'status', 'remark', ), 'classes': ('col-sm-12', 'form-horizontal',)}),
        ('隐藏域', {'fields': ('_id', 'id', '_new_parent_id', ),
                 'classes': ('col-sm-12', 'hidefield',)}),
    )
