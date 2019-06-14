import logging

from rest_framework import viewsets
from rest_framework.permissions import BasePermission
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from acmin.models import Permission, PermissionItem
from acmin.serializer import get_serializer
from acmin.utils import import_class, attr, param

logger = logging.getLogger(__name__)


class BaseViewSet(viewsets.ModelViewSet):
    class Meta:
        model = None

    def get_serializer_class(self):
        result = get_serializer(self.Meta.model)
        return result

    def get_serializer_context(self):
        context = super().get_serializer_context()
        return context

    def get_serializer(self, *args, **kwargs):
        serializer = super().get_serializer(*args, **kwargs)
        return serializer

    def get_queryset(self):
        queryset = attr(self, "Meta.model").objects.all()
        sorter = param(self.request, "sorter")
        if sorter:
            queryset = queryset.order_by(sorter)
        return queryset

    def get_paginated_response(self, data):
        paginator = self.paginator.page.paginator
        count = paginator.count
        return Response(dict(
            data=dict(
                list=data,
                total=count,
                pageSize=paginator.per_page,
                pages=paginator.num_pages,
                current=int(self.request.GET.get("page", 1))
            ),
            status=200,
            message="success"
        ))


class ViewPermission(BasePermission):
    def has_permission(self, request, view):
        return Permission.has_permission(request.user, view.Meta.model, PermissionItem.listable)


class AuthenticatedBaseViewSet(BaseViewSet):
    permission_classes = (IsAuthenticated, ViewPermission,)


def get_viewset(model_class, login_required=True):
    app_name = model_class.__module__.split(".")[0]
    name = f"{model_class.__name__}ViewSet"
    module = f'{app_name}.views'
    try:
        return import_class(f'{module}.{name}')
    except(ImportError, AttributeError, Exception):
        super_class = AuthenticatedBaseViewSet if login_required else BaseViewSet
        return type(f"Dynamic{name}", (super_class,), dict(
            Meta=type("Meta", (), dict(
                model=model_class
            )),
            __module__=module,
        ))
