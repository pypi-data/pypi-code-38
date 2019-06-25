from rest_framework import status
from rest_framework.response import Response
from rest_framework.settings import api_settings
from django_filters.rest_framework import DjangoFilterBackend
from drf_extra.pagination import PageNumberPagination, CursorPagination


class CreateModelMixin(object):
    """
    Create a model instance.
    """

    def create(self, request, *args, **kwargs):
        """
        Generates a Response object with create status and response data.
        Accepts optional `return_serializer` and return_status_code` kwargs that
        will be used if set to override the serializer used in the response
        data and response status code.
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        _return_serializer = kwargs.get('return_serializer')
        data = _return_serializer(
            serializer.instance, context={'request': request}
        ).data if _return_serializer else serializer.data

        return Response(
            {'status': 'success', 'data': data},
            status=kwargs.get('return_status_code', status.HTTP_201_CREATED),
            headers=headers
        )

    def perform_create(self, serializer):
        serializer.save()

    def get_success_headers(self, data):
        try:
            return {'Location': data[api_settings.URL_FIELD_NAME]}
        except (TypeError, KeyError):
            return {}


class ListModelMixin(object):
    """
    List a queryset.
    """

    filter_backends = (DjangoFilterBackend,)
    pagination_class = PageNumberPagination

    def paginate_queryset(self, queryset):
        """
        Allow pagination to be overided via query params. Defaults to page
        number pagination.
        """

        paginator_name = self.request.GET.get('pagination')

        try:
            self.pagination_class = {
                "page": PageNumberPagination,
                "cursor": CursorPagination
            }[paginator_name]
        except KeyError:
            pass

        return super().paginate_queryset(queryset)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'status': 'success', 'data': serializer.data})


class RetrieveModelMixin(object):
    """
    Retrieve a model instance.
    """

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({'status': 'success', 'data': serializer.data})


class UpdateModelMixin(object):
    """
    Update a model instance.
    """

    def update(self, request, *args, **kwargs):
        """
        Generates a Response object with response data.
        Accepts optional `return_serializer` kwarg that will be used if set, to
        override the serializer used in the response data.
        """

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        _return_serializer = kwargs.get('return_serializer')
        data = _return_serializer(
            serializer.instance, context={'request': request}
        ).data if _return_serializer else serializer.data

        return Response({'status': 'success', 'data': data})

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class DestroyModelMixin(object):
    """
    Destroy a model instance.
    """

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        self.perform_destroy(serializer)
        return Response(
            data={'status': 'success'},
            status=status.HTTP_200_OK)

    def perform_destroy(self, serializer):
        serializer.destroy()
