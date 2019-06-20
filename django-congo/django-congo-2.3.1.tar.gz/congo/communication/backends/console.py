# -*- coding: utf-8 -*-
from congo.communication.backends.base import BaseSMSBackend

class SMSBackend(BaseSMSBackend):
    def send_messages(self, sms_messages):
        for sms_message in sms_messages:
            self.print_message(sms_message)
        return []
