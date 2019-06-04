# -*- coding:utf-8 -*-

from .apps import Config

from . import models, mixins, serializers, permissions

from rest_framework import viewsets, decorators, response
from rest_framework.permissions import IsAdminUser
from django_szuprefix.api.helper import register
from django_szuprefix.api.permissions import DjangoModelPermissionsWithView

__author__ = 'denishuang'


class PartyViewSet(viewsets.ModelViewSet):
    queryset = models.Party.objects.all()
    serializer_class = serializers.PartySerializer
    permission_classes = [IsAdminUser]


register(Config.label, 'party', PartyViewSet)


class WorkerViewSet(mixins.PartyMixin, viewsets.ModelViewSet):
    queryset = models.Worker.objects.all()
    serializer_class = serializers.WorkerSerializer
    permission_classes = [DjangoModelPermissionsWithView]
    filter_fields = {
        'number': ['exact', 'in']
    }

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.WorkerListSerializer
        return super(WorkerViewSet, self).get_serializer_class()

    @decorators.list_route(['get'], permission_classes=[permissions.IsSaasWorker])
    def current(self, request):
        serializer = serializers.CurrentWorkerSerializer(self.worker, context={'request': request})
        return response.Response(serializer.data)


    @decorators.list_route(['POST'])
    def batch_active(self, request):
        a = request.data.get('active', 'true')
        is_active = not (a is False or a == 'false')
        ids = request.data.get('ids', [])
        rows = self.get_queryset().filter(id__in=ids).update(is_active=is_active)
        return response.Response({'rows': rows})


register(Config.label, 'worker', WorkerViewSet)
