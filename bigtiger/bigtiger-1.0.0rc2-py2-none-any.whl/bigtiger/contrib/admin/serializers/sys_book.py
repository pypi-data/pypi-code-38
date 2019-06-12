# -*- coding: utf-8 -*-

"""
系统数据字典
Created on 2017-07-19
@author: linkeddt.com
"""

from rest_framework import serializers


class SysBookSerializer(serializers.Serializer):
    id = serializers.CharField(label=u'Id', max_length=36, required=True)
    class_code = serializers.CharField(
        label=u'分类编码', max_length=20, required=True)
    code = serializers.CharField(label=u'字典编码', max_length=50, required=True)
    text = serializers.CharField(label=u'字典名称', max_length=50, required=True)
    order_number = serializers.IntegerField(
        label=u'排序号', max_value=99, min_value=0, required=True)
    is_enable = serializers.IntegerField(
        label=u'启用状态', max_value=99, min_value=0, required=True)
    remark = serializers.CharField(
        label=u'备注', max_length=200, required=False, allow_blank=True)
