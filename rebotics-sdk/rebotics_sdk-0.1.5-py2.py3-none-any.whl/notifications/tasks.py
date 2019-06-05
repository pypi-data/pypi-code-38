import logging

import requests
from celery import shared_task
from rest_framework import status

from .models import Message

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 180


@shared_task(bind=True)
def send_message(self, message_id):
    message = Message.objects.get(id=message_id)
    try:
        if message.receiver.auth_token:
            headers = {
                'Authorization': 'Token %s' % message.receiver.auth_token
            }
        else:
            headers = {}
        response = requests.post(message.receiver.url, data={
            'component': message.component,
            'status': message.status,
            'body': message.body,  # requires JSON string
        }, timeout=DEFAULT_TIMEOUT, headers=headers)

        if response.status_code == status.HTTP_202_ACCEPTED:
            logger.info('Component %s is posted to %s', message.component, message.receiver.url)
            message.delivery_status = Message.DELIVERY_STATUS_DELIVERED
        else:
            logger.error('Webhook failed with status %s and message %s', response.status_code, response.content)
            message.delivery_status = Message.DELIVERY_STATUS_REJECTED
            message.exception_message = response.content

    except Exception as exc:
        logger.exception(exc)
        message.delivery_status = Message.DELIVERY_STATUS_FAILED
        message.exception_message = str(exc)
    finally:
        message.save()
