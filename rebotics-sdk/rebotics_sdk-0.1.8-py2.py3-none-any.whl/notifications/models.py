import json
import logging

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.six import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class WebhookRouter(models.Model):
    user = models.ForeignKey(get_user_model(), related_name='webhooks', on_delete=models.CASCADE)
    url = models.URLField()
    auth_token = models.CharField(max_length=64, null=True)

    created = models.DateTimeField(_('Date Created'), auto_now_add=True, editable=False)
    modified = models.DateTimeField(_('Date Modified'), auto_now=True, editable=False)

    class Meta:
        verbose_name = _('Webhook router')
        verbose_name_plural = _('Webhook routers')

    def __str__(self):
        return '#{} {}-on-{}'.format(self.id, self.user, self.url)

    def emit_message(self, component, status, body):
        message = Message.objects.create(
            component=component,
            status=status,
            body=json.dumps(body),
            receiver=self,
            delivery_status=Message.DELIVERY_STATUS_PENDING
        )
        message.send()


@python_2_unicode_compatible
class Message(models.Model):
    DELIVERY_STATUS_PENDING = 'message_pending'
    DELIVERY_STATUS_DELIVERED = 'message_delivered'
    DELIVERY_STATUS_REJECTED = 'message_rejected'
    DELIVERY_STATUS_FAILED = 'message_failed'

    PROCESSING = 'processing'
    PLANOGRAM_IMPORT = 'planogram_import'
    INTERNAL = 'internal'

    receiver = models.ForeignKey(WebhookRouter, related_name='messages', on_delete=models.CASCADE)

    created = models.DateTimeField(_('Date Created'), auto_now_add=True, editable=False)
    modified = models.DateTimeField(_('Date Modified'), auto_now=True, editable=False)

    component = models.CharField(max_length=64, choices=[
        (PROCESSING, _("Processing action")),
        (PLANOGRAM_IMPORT, _("Planogram import")),
        (INTERNAL, _("Internal"))
    ])
    status = models.CharField(max_length=32)

    body = models.TextField()

    delivery_status = models.CharField(max_length=64, choices=[
        (DELIVERY_STATUS_PENDING, _("Pending")),
        (DELIVERY_STATUS_DELIVERED, _("Delivered")),
        (DELIVERY_STATUS_REJECTED, _("Rejected")),
        (DELIVERY_STATUS_FAILED, _("Failed")),
    ])

    exception_message = models.TextField()

    class Meta:
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')

    def __str__(self):
        return "Message on {} to {} with {}".format(
            self.component, self.receiver_id, self.delivery_status
        )

    def send(self):
        from .tasks import send_message
        send_message.delay(message_id=self.id)
