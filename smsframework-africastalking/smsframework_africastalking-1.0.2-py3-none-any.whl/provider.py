import logging
import json

import africastalking
import phonenumbers
from smsframework import IProvider

from .error import AfricasTalkingProviderError, InvalidNumberError


class AfricasTalkingProvider(IProvider):
    """Africa's Talking Provider"""

    def __init__(self, gateway, name, username, api_key):
        """
        Configure AfricasTalking Provider

        :param gateway: (smsframework.Gateway) Passed automatically by gateway
         on add_provider call
        :param name: (str) Uniquely identify the instance of
         AfricasTalkingProvider registered to the gateway
        :param username: (str) Username for your AfricasTalking account
        :param api_key: (str) API key for your AfricasTalking account
        """
        super().__init__(gateway, name)

        africastalking.initialize(username, api_key)
        self.sms_client = africastalking.SMS

    def send(self, message):
        """
        Send a single text message.
        TODO: Add a batch send feature.

        :param message: (smsframework.OutgoingMessage) The message to send.
        :return: (smsframework.OutgoingMessage) The sent message, updated with
         msgid.
        """

        num_ending = message.dst[-3:]

        logging.info(
            'AFRICAS_TALKING SENDING SMS TO NUM ENDING ...%s' % (num_ending)
        )

        target_country = message.provider_params['target_country']

        try:
            phone_number = phonenumbers.parse(message.dst, target_country)
        except:
            raise InvalidNumberError(message.dst, 'Unable to Parse Number')

        number_is_valid = phonenumbers.is_valid_number_for_region(
            phone_number, target_country
        )
        if number_is_valid is False:
            raise InvalidNumberError(
                message.dst,
                'Invalid Phone Number for Target Country',
                target_country=target_country
            )

        try:
            formatted_number = phonenumbers.format_number(
                phone_number,
                phonenumbers.PhoneNumberFormat.E164
            )
        except:
            InvalidNumberError(
                message.dst,
                'Unable to Parse Phone Number'
            )

        try:
            api_response = self.sms_client.send(
                message.body,
                [formatted_number],
                message.provider_options.senderId
            )
        except Exception as e:
            error = json.loads(e.args[0])
            error_status = error['SMSMessageData']['Recipients'][0]['status']

            logging.error(
                'AFRICAS_TALKING SMS TO NUM ENDING ...%s FAILED' % (num_ending)
            )

            if error_status == 'InvalidPhoneNumber':
                raise InvalidNumberError(formatted_number)
            else:
                raise AfricasTalkingProviderError(error_status)

        sent_message = api_response['SMSMessageData']['Recipients'][0]
        message.msgid = sent_message['messageId']

        logging.info(
            'AFRICAS_TALKING SMS TO NUM ENDING ...%s SENT' % (num_ending)
        )

        return message
