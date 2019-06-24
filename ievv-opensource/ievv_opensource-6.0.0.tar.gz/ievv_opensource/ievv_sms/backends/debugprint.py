from __future__ import print_function

from ievv_opensource.ievv_sms import sms_registry


class Backend(sms_registry.AbstractSmsBackend):
    """
    Backend that just prints the phone number and
    message. Does not send an SMS.

    Useful for development.

    The backend_id for this backend is ``debugprint``.
    """
    @classmethod
    def get_backend_id(cls):
        return 'debugprint'

    def send(self):
        print('**************')
        print('opensource: ', self.send_as)
        print('**************')
        print(
            '{border}\n'
            'DEBUG PRINT SMS:\n'
            'Send as: {send_as}\n'
            'Phone number: {phone_number}\n'
            'Message: {message}\n'
            'Message length: {message_length}\n'
            '{border}\n'.format(
                send_as=self.send_as,
                phone_number=self.cleaned_phone_number,
                message=self.cleaned_message,
                message_length=len(self.cleaned_message),
                border='-' * 70
            )
        )


class Latin1Backend(Backend):
    """
    Just like :class:`.Backend`, but this backend crashes
    if you try to send any characters outside the latin1
    charset.

    The backend_id for this backend is ``debugprint_latin1``.

    Very useful when the targeted production backend
    only supports latin1.
    """
    @classmethod
    def get_backend_id(cls):
        return 'debugprint_latin1'

    def clean_message(self, message):
        return message.encode('latin1').decode('latin1')
