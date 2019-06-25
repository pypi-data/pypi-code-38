from django.utils.translation import ugettext as _
from rest_framework.generics import GenericAPIView
from drf_extra.mixins import *


class BaseAPIView(GenericAPIView):
    """
    Generic view with extended features for Rehive usage. All viewsets should
    extend this class.
    """

    # Store serializer classes used by the view based on the request method
    # This dict should take the request method type ("POST", ...) as key
    # and a serializer class a value.
    serializer_classes = {}

    def get_serializer_class(self):
        """
        `get_serializer_class` will first try to retrieve the serializer class
        from the `serializer_classes` dict based on the request method and if
        a serializer class is not set it will call the super.
        """
        try:
            return self.serializer_classes[self.request.method]
        except KeyError:
            return super().get_serializer_class()


class CreateAPIView(CreateModelMixin,
                    BaseAPIView):
    """
    Concrete view for creating a model instance.
    """

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ListAPIView(ListModelMixin,
                  BaseAPIView):
    """
    Concrete view for listing a queryset.
    """

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ListCreateAPIView(ListModelMixin,
                        CreateModelMixin,
                        BaseAPIView):
    """
    Concrete view for listing a queryset or creating a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class RetrieveUpdateAPIView(RetrieveModelMixin,
                            UpdateModelMixin,
                            BaseAPIView):
    """
    Concrete view for retrieving and updating a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class RetrieveDestroyAPIView(RetrieveModelMixin,
                             DestroyModelMixin,
                             BaseAPIView):
    """
    Concrete view for retrieving and deleting a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class RetrieveUpdateDestroyAPIView(RetrieveModelMixin,
                                   UpdateModelMixin,
                                   DestroyModelMixin,
                                   BaseAPIView):
    """
    Concrete view for retrieving, updating and deleting a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class RetrieveAPIView(RetrieveModelMixin,
                      BaseAPIView):
    """
    Concrete view for retrieving a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class DestroyAPIView(DestroyModelMixin,
                     BaseAPIView):
    """
    Concrete view for deleting a model instance.
    """

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
