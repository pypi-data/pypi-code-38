"""
This module hold all the classes for the different text notification services
(except twilio which is implemented in original django-herald)
"""
import json

from django.conf import settings

from herald.base import NotificationBase
from herald.clients.msg91 import Client

class Msg91TextNotification(NotificationBase):
    """
    Base class for msg91 text notifications.
    """

    render_types = ['text']
    from_number = None
    to_number = None
    override_sender_id = None

    def get_recipients(self):
        return [self.to_number]

    def get_sent_from(self):
        if self.override_sender_id:
            if len(self.override_sender_id) != 6 or not self.override_sender_id.isalpha():
                raise Exception(
                    'override_sender_id must be a 6 alphabets string'
                )

            return self.override_sender_id
        try:
            sender_id = settings.MSG91_TRANSACTIONAL_SENDER_ID
        except AttributeError:
            raise Exception(
                'MSG91_TRANSACTIONAL_SENDER_ID setting is required for sending transactional msg'
            )

        return sender_id

    @staticmethod
    # pylint: disable-msg=R0913
    def _send(recipients, text_content=None, html_content=None, sent_from=None, subject=None,
              extra_data=None, attachments=None):
        try:
            authkey = settings.MSG91_AUTHKEY
        except AttributeError:
            raise Exception(
                'MSG91_AUTHKEY setting is required for sending a Msg91TextNotification'
            )

        client = Client(authkey)

        to_number = recipients[0]
        if not to_number:
            raise Exception(
                'to_number must be defined in the notification class'
            )

        api_result = client.send_transactional(
            sender_id=sent_from,
            to_number=to_number,
            message=text_content
        )

        result = json.loads(api_result.content.decode("utf-8"))

        if result['type'] == 'error':
            raise Exception(result['message'])
