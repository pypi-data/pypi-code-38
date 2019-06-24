# -*- coding:utf-8 -*- 
from __future__ import unicode_literals
from rest_framework import serializers, viewsets, mixins, decorators
from django.contrib.auth import models

from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import authenticate

from ..api.mixins import IDAndStrFieldSerializerMixin


class GroupSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Group
        fields = ('name',)


class UserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="get_full_name")
    permissions = serializers.ListField(source="get_all_permissions")

    class Meta:
        model = models.User
        fields = ('id', 'username', 'name', 'email', 'groups', 'permissions')

    def to_representation(self, instance):
        rep = super(UserSerializer, self).to_representation(instance)
        from .helper import gen_permissions_map
        rep['permissions_map'] = gen_permissions_map(rep['permissions'])
        return rep


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, allow_blank=False, max_length=100)
    password = serializers.CharField(required=True, allow_blank=False, max_length=100)

    def validate(self, attrs):
        user = authenticate(**attrs)
        if not user:
            raise serializers.ValidationError("帐号或者密码不正确")
        self.user = user
        return attrs

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128)
    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)

    set_password_form_class = SetPasswordForm

    def __init__(self, *args, **kwargs):
        super(PasswordChangeSerializer, self).__init__(*args, **kwargs)

        self.request = self.context.get('request')
        self.user = getattr(self.request, 'user', None)

    def validate_old_password(self, value):
        invalid_password_conditions = (
            self.user,
            not self.user.check_password(value)
        )

        if all(invalid_password_conditions):
            raise serializers.ValidationError('密码不正确')
        return value

    def validate(self, attrs):
        self.set_password_form = self.set_password_form_class(
            user=self.user, data=attrs
        )

        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)
        return attrs

    def save(self):
        self.set_password_form.save()
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(self.request, self.user)
