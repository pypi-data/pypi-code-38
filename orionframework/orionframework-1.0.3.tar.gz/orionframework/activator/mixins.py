import datetime

from django_extensions.db.models import ActivatorModel
from rest_framework.decorators import action
from rest_framework.response import Response

from orionframework.serializers import ListIDSerializer


class ActivateModelMixin(object):

    def get_serializer_class(self):
        if self.action == 'activate':
            return ListIDSerializer

        return super(ActivateModelMixin, self).get_serializer_class()

    @action(detail=False, methods=["POST"])
    def activate(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.get_queryset().filter(id__in=serializer.data.get("ids")).update(status=ActivatorModel.ACTIVE_STATUS,
                                                                             activate_date=datetime.datetime.now())

        return Response("OK")


class DeactivateModelMixin(object):

    def get_serializer_class(self):
        if self.action == 'deactivate':
            return ListIDSerializer

        return super(DeactivateModelMixin, self).get_serializer_class()

    @action(detail=False, methods=["POST"])
    def deactivate(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.get_queryset().filter(id__in=serializer.data.get("ids")).update(status=ActivatorModel.INACTIVE_STATUS,
                                                                             deactivate_date=datetime.datetime.now())

        return Response("OK")


class ActiveModelMixin(object):

    @action(detail=False)
    def active(self, request, *args, **kwargs):
        """
        List active queryset.
        """
        queryset = self.filter_queryset(self.get_queryset().filter(status=ActivatorModel.ACTIVE_STATUS))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class InactiveModelMixin(object):

    @action(detail=False)
    def inactive(self, request, *args, **kwargs):
        """
        List inactive queryset.
        """
        queryset = self.filter_queryset(self.get_queryset().filter(status=ActivatorModel.INACTIVE_STATUS))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ActivatorModelMixin(ActivateModelMixin,
                          DeactivateModelMixin,
                          ActiveModelMixin,
                          InactiveModelMixin):
    pass
