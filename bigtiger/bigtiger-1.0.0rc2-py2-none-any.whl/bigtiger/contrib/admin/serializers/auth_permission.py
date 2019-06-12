# -*- coding: utf-8 -*-

from rest_framework import serializers


class AuthPermissionSerializer(serializers.Serializer):

    id = serializers.UUIDField(read_only=True)
    parent_id = serializers.UUIDField(required=False, allow_null=True)
    depth = serializers.IntegerField(
        label=u'深度', max_value=9999, min_value=0, required=False, allow_null=True)

    menu_name = serializers.CharField(
        label=u'菜单名称', max_length=100, required=True)
    menu_url = serializers.CharField(
        label=u'菜单URL', max_length=200, required=False, allow_blank=True)
    menu_url_alias = serializers.CharField(
        label=u'菜单URL别名', max_length=200, required=False, allow_blank=True)
    menu_url_debug = serializers.CharField(
        label=u'菜单URL调试', max_length=200, required=False, allow_blank=True)
    menu_target = serializers.CharField(
        label=u'菜单目标', max_length=20, required=False, allow_blank=True)
    fast_url = serializers.CharField(
        label=u'快捷URL', max_length=200, required=False, allow_blank=True)
    big_icon = serializers.CharField(
        label=u'大图标', max_length=200, required=False, allow_blank=True)
    small_icon = serializers.CharField(
        label=u'小图标', max_length=200, required=False, allow_blank=True)
    is_important = serializers.IntegerField(
        label=u'是否重要', max_value=99, min_value=0, required=True)
    is_open = serializers.IntegerField(
        label=u'是否展开', max_value=99, min_value=0, required=True)
    is_enable = serializers.IntegerField(
        label=u'是否启用', max_value=99, min_value=0, required=True)
    is_cache = serializers.IntegerField(
        label=u'是否缓存', max_value=99, min_value=0, required=False, allow_null=True)
    is_cross = serializers.IntegerField(
        label=u'是否跨域', max_value=99, min_value=0, required=False, allow_null=True)
    is_debug = serializers.IntegerField(
        label=u'是否调试', max_value=99, min_value=0, required=False, allow_null=True)
    badge = serializers.CharField(
        label=u'徽章', max_length=50, required=False, allow_blank=True)
    order_number = serializers.IntegerField(
        label=u'排序号', max_value=9999, min_value=0, required=False, allow_null=True)
    status = serializers.IntegerField(
        label=u'显示模式', max_value=9999, min_value=0, required=True)
    remark = serializers.CharField(
        label=u'备注', max_length=200, required=False, allow_blank=True)
