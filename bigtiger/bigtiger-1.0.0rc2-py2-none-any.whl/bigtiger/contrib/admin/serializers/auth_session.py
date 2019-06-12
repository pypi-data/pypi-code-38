# -*- coding: utf-8 -*-

from rest_framework import serializers


class AuthSessionSerializer(serializers.Serializer):

    session_key = serializers.CharField(required=True)
    session_data = serializers.CharField(required=True)
    expire_date = serializers.DateTimeField(required=True)


class AuthSessionPagerSerializer(serializers.Serializer):
    count = serializers.IntegerField(required=True)
    data = AuthSessionSerializer(many=True)
