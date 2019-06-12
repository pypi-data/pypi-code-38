# -*- coding: utf-8 -*-

from rest_framework import serializers


class AuthUserLogSerializer(serializers.Serializer):
    id = serializers.CharField(label=u'Id', max_length=36, required=True)
    user_id = serializers.CharField(
        label=u'操作用户', max_length=36, required=True)
    action_flag = serializers.IntegerField(
        label=u'动作标志', max_value=99, min_value=0, required=True)
    action_time = serializers.CharField(label=u'操作时间', required=True)
    ip = serializers.CharField(label=u'IP', max_length=32, required=True)
    action_class = serializers.CharField(label=u'操作类名', required=True)
    action_object = serializers.CharField(label=u'操作对象', required=True)
    action_handler = serializers.CharField(
        label=u'执行处理器', max_length=200, required=True)
    status = serializers.IntegerField(
        label=u'执行状态', max_value=99, min_value=0, required=True)
    status_note = serializers.CharField(
        label=u'状态说明', required=False, allow_blank=True)
