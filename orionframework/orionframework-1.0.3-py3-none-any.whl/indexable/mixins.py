from rest_framework.decorators import action
from rest_framework.response import Response

from orionframework.serializers import ListIDSerializer


class IndexedModelMixin(object):

    def get_serializer_class(self):
        if self.action == 'reorder':
            return ListIDSerializer

        return super(IndexedModelMixin, self).get_serializer_class()

    @action(detail=False, methods=["POST"])
    def reorder(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.get_queryset().model.objects.reorder(serializer.data.get("ids"))

        return Response("OK")
