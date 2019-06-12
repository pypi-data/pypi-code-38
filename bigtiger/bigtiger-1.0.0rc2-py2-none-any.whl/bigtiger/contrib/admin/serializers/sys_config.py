# -*- coding: utf-8 -*-

"""
系统配置
Created on 2017-07-19
@author: linkeddt.com
"""

from rest_framework import serializers


class SysConfigSerializer(serializers.Serializer):
    config_key = serializers.CharField(
        label=u'键', max_length=20, required=True)
    config_value = serializers.CharField(label=u'值', required=True)
    config_name = serializers.CharField(
        label=u'说明', max_length=200, required=True)
