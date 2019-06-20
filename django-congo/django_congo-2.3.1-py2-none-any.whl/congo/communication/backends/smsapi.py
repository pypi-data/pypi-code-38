from congo.communication.backends.base import BaseSMSBackend
from congo.smsapi.client import SmsAPI
from congo.smsapi.responses import ApiError
from django.conf import settings

class SMSBackend(BaseSMSBackend):
    def send_messages(self, sms_messages):
        result = []

        self.api = SmsAPI(settings.CONGO_SMSAPI_USER, settings.CONGO_SMSAPI_PASSWORD)

        for message in sms_messages:
            try:
                self.api.service('sms').action('send')
                self.api.set_from(message.sender_name)
                self.api.set_to(message.recipient_mobile_phone)
                self.api.set_content(message.content)

                if settings.DEBUG:
                    self.print_message(message)

                result.append(self.api.execute())

            except ApiError:
                if not self.fail_silently:
                    raise

        return result
