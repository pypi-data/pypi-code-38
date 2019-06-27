# -*- coding:utf-8 -*-
from django_szuprefix.api.mixins import UserApiMixin
from django_szuprefix_saas.saas.mixins import PartyMixin, PartySerializerMixin
from .apps import Config

__author__ = 'denishuang'
from . import models
from rest_framework import serializers, viewsets
from django_szuprefix.api.helper import register


class SigninSerializer(PartySerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Signin
        fields = ('address', 'longitude', 'latitude', 'url')


class SigninFullSerializer(serializers.HyperlinkedModelSerializer):
    class Meta(SigninSerializer.Meta):
        fields = SigninSerializer.Meta.fields + ('party',)


class SigninViewSet(PartyMixin, UserApiMixin, viewsets.ModelViewSet):
    queryset = models.Signin.objects.all()
    serializer_class = SigninSerializer



register(Config.label, 'signin', SigninViewSet)
