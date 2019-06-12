# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms

from bigtiger.forms.forms import BaseForm, OrderForm
from bigtiger.utils.choice import choice_wrap
from django_sae.models.user import UserModel
from bigtree_api.models.auth_group import AuthGroupModel
from bigtiger.contrib.admin.models.auth_user import AuthUserModel


def get_roles():
    """ 用户角色
    """
    m = AuthGroupModel()
    lst = m.get_all()
    return lst


def role_manager():
    """ 角色管理，通过角色id获取角色名
    """
    lst = get_roles()

    def _role(roles_str):
        roles = roles_str.split(',')
        lst1 = [item['name'] for item in lst if item['id'] in roles]
        return ','.join(lst1)
    return _role


@choice_wrap()
def get_roles_choice(*args, **kwargs):
    """ 用户角色
    """
    lst = get_roles()
    return [(item['id'], item['name']) for item in lst]


class AuthUserSearchForm(OrderForm):
    user_name = forms.CharField(label='人员姓名：', required=False, max_length=10)
    roles = forms.ChoiceField(label='所属角色：')

    def __init__(self, *args, **kwargs):
        super(AuthUserSearchForm, self).__init__(*args, **kwargs)
        self.fields['roles'].choices = get_roles_choice(is_all=True)


class AuthUserBaseForm(BaseForm):
    _id = forms.CharField(required=False, widget=forms.HiddenInput)

    id = forms.CharField(label='Id', required=True, max_length=36)
    login_name = forms.RegexField(label='登陆用户名', max_length=30,
                                  regex=r'^[\w.@+-]+$',
                                  help_text='只能用字母、数字和字符 @/./+/-/_ 。',
                                  error_messages={'invalid': '该值只能包含字母、数字和字符@/./+/-/_ 。'})
    first_name = forms.CharField(label='姓氏', required=True, max_length=10)
    last_name = forms.CharField(label='名字', required=True, max_length=20)
    sex = forms.ChoiceField(label='性别', required=False)
    phone_number = forms.CharField(label='手机号码', required=True, max_length=11)
    email = forms.CharField(label='邮箱', required=False, max_length=50)
    is_active = forms.ChoiceField(label='是否激活', required=True)
    is_dba = forms.ChoiceField(label='数据管理员', required=True)
    is_read = forms.ChoiceField(
        label='只读用户', required=True, help_text='对数据只有查看的权限。')
    is_leader = forms.ChoiceField(
        label='是否为领导', required=True, help_text='领导用户有特殊的用于演示的功能。')
    roles = forms.MultipleChoiceField(
        label='所属角色', required=True, help_text='所属角色支持多选，权限并集处理。')
    wechat_json = forms.CharField(label='微信信息', required=False)
    extend_json = forms.CharField(label='扩展信息', required=False)
    remark = forms.CharField(label='备注', required=False, max_length=200,
                             widget=forms.Textarea(attrs={'rows': 2, 'cols': 100}))

    def __init__(self, *args, **kwargs):
        super(AuthUserBaseForm, self).__init__(*args, **kwargs)
        self.fields['sex'].choices = ((1, '男'), (0, '女'),)
        self.fields['is_active'].choices = ((1, '是'), (0, '否'),)
        self.fields['is_dba'].choices = ((0, '否'), (1, '是'),)
        self.fields['is_read'].choices = ((0, '否'), (1, '是'),)
        self.fields['is_leader'].choices = ((0, '否'), (1, '是'),)
        self.fields['roles'].choices = get_roles_choice()


class AuthUserCreateForm(AuthUserBaseForm):
    login_password = forms.CharField(
        label='登陆密码', required=True, max_length=20)

    def clean_login_name(self):
        login_name = self.cleaned_data['login_name']
        m = AuthUserModel()
        result = m.get_one_login_name(login_name)
        if result is None:
            return login_name
        raise forms.ValidationError('已存在一位使用该登录名的用户。')


class AuthUserEditForm(AuthUserBaseForm):
    pass


class AuthUserModifyPwdForm(BaseForm):
    user_id = forms.CharField(widget=forms.HiddenInput)
    old_pwd = forms.CharField(
        label='旧的密码', max_length=30, widget=forms.PasswordInput)
    new_pwd = forms.CharField(
        label='新的密码', max_length=30, widget=forms.PasswordInput)
    confirm_pwd = forms.CharField(
        label='确认密码', max_length=30, widget=forms.PasswordInput)

    def clean_confirm_pwd(self):
        new_pwd = self.cleaned_data['new_pwd']
        confirm_pwd = self.cleaned_data['confirm_pwd']
        if new_pwd == confirm_pwd:
            return confirm_pwd
        raise forms.ValidationError('确认密码与新密码不一致。')


class AuthUserCreateFormAdmin(object):
    fieldsets = (
        ('基础信息', {'fields': ('login_name', 'login_password', 'first_name', 'last_name', 'sex',
                             'phone_number', 'email', 'is_active',), 'classes': ('col-sm-12', 'form-horizontal',)}),

        ('权限信息', {'fields': ('is_read', 'is_leader', 'roles',
                             'remark', ), 'classes': ('col-sm-12', 'form-horizontal',)}),
        ('隐藏域', {'fields': ('_id', 'id', 'is_dba', 'extend_json', 'wechat_json',),
                 'classes': ('col-sm-12', 'hidefield',)}),
    )
    readonly_fields = ()


class AuthUserEditFormAdmin(object):
    fieldsets = (
        ('基础信息', {'fields': ('login_name', 'first_name', 'last_name', 'sex',
                             'phone_number', 'email', 'is_active',), 'classes': ('col-sm-12', 'form-horizontal',)}),
        ('权限信息', {'fields': ('is_read', 'is_leader', 'roles',
                             'remark', ), 'classes': ('col-sm-12', 'form-horizontal',)}),
        ('隐藏域', {'fields': ('_id', 'id', 'is_dba', 'extend_json', 'wechat_json',),
                 'classes': ('col-sm-12', 'hidefield',)}),
    )
    readonly_fields = ()


class AuthUserModifyPwdFormAdmin(object):
    fieldsets = (
        ('修改密码', {'fields': ('old_pwd', 'new_pwd', 'confirm_pwd',),
                  'classes':  ('col-sm-12', 'form-horizontal',)}),
        ('隐藏域', {'fields': ('user_id',),
                 'classes': ('col-sm-12', 'hidefield',)}),
    )
    readonly_fields = ()
