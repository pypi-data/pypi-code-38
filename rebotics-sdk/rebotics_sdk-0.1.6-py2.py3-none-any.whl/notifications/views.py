import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rebotics_sdk.notifications.models import WebhookRouter
from rebotics_sdk.notifications.serializers import SetWebhookSerializer
from rebotics_sdk.notifications.utils import log_action

logger = logging.getLogger(__name__)


class SetWebhookView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, *args, **kwargs):
        serializer = SetWebhookSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        url = serializer.validated_data['url']
        user = request.user
        router, created = WebhookRouter.objects.get_or_create(user=user, url=url)
        if created:
            log_action(user, router, "Created from API")

        auth_token = serializer.validated_data.get('auth_token')
        if auth_token is not None and auth_token != router.auth_token:
            logger.debug('Overriding auth token')
            router.auth_token = auth_token
            router.save()

        logger.info('Router created for user %s with id %s', user, router)
        logger.debug("Sending pong message to new webhook...")
        router.emit_message('internal', 'succeed', {
            'message': "Pong!",
        })
        return Response({
            'id': router.id,
        }, status=status.HTTP_200_OK)
