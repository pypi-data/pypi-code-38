# -*- coding: utf-8 -*-

from rest_framework import serializers


class AuthUserSerializer(serializers.Serializer):

    id = serializers.UUIDField(read_only=True)
    login_name = serializers.CharField(required=True)
    login_password = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    user_name = serializers.CharField(required=True)
    sex = serializers.IntegerField(required=False)
    phone_number = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    is_active = serializers.IntegerField(required=True)
    is_superuser = serializers.IntegerField(required=True)
    is_dba = serializers.IntegerField(required=True)
    is_read = serializers.IntegerField(required=True)
    is_leader = serializers.IntegerField(required=True)
    roles = serializers.CharField(required=True)
    domain = serializers.CharField(required=False)
    create_date = serializers.DateTimeField(required=True)
    last_login_date = serializers.CharField(required=False)
    last_login_ip = serializers.CharField(required=False)
    extend_json = serializers.CharField(required=False)
    remark = serializers.CharField(required=False)
