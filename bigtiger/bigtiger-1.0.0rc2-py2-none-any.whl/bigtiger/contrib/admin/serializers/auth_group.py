# -*- coding: utf-8 -*-

from rest_framework import serializers


class AuthGroupSerializer(serializers.Serializer):

    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(label=u'组名称', max_length=50, required=True)
    type = serializers.CharField(label=u'组分类', max_length=2, required=True)
    remark = serializers.CharField(
        label=u'备注', max_length=200, required=False, allow_blank=True)
