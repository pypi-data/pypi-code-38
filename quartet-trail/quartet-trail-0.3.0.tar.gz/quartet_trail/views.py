from os import path
from django.apps import apps
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from . import serializers


class QuartetTrailViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)
    @property
    def model(self):
        current_path = self.request.path.split('/')
        if current_path[1] == 'quartet-trail' and current_path[2] != 'AuthenticationInfo':
            tracked_model = current_path[2]
            historical_model = 'Historical' + tracked_model
            return apps.get_model('quartet_trail', model_name=historical_model)
        else:
            # Django Rest Framework requires a default when it loads.                           
            return apps.get_model('quartet_trail', model_name="HistoricalEndpoint")

    def get_queryset(self):
        model = self.model
        return model.objects.all()

    def get_serializer_class(self):
        serializers.QuartetTrailSerializer.Meta.model = self.model
        return serializers.QuartetTrailSerializer

