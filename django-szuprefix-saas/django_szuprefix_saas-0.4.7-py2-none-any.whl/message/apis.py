# -*- coding:utf-8 -*-
from rest_framework.decorators import list_route

from .apps import Config

__author__ = 'denishuang'
from . import models
from rest_framework import serializers, viewsets
from django_szuprefix.api.helper import register


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Task
        fields = ('title', 'content', 'is_active', 'receiver_content_type', 'receiver_ids')


class TaskViewSet(viewsets.ModelViewSet):
    queryset = models.Task.objects.all()
    serializer_class = TaskSerializer

    @list_route(methods=['post'])
    def to(self, request):
        ids = request.data['ids']




register(Config.label, 'task', TaskViewSet)
