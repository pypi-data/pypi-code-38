from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from rebotics_sdk.hook import signals
from rebotics_sdk.hook.serializers import WebhookDataSerializer


class WebhookHandlerViewSet(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = WebhookDataSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        emitter = signals.emitter_factory(
            serializer.validated_data['component'],
            serializer.validated_data['status'],
            serializer.validated_data['body'],
            request)
        emitter.emit()

        return Response(status=status.HTTP_202_ACCEPTED)
