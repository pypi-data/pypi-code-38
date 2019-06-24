import re

from django.conf import settings
from django.utils.module_loading import import_string


class BasePhoneNumberHandler:
    STRIP_WHITESPACE_PATTERN = re.compile(r'\s+')

    def __init__(self, phone_number, country_calling_code=None):
        self.raw_phone_number = phone_number or ''
        self._country_calling_code = country_calling_code

    def get_country_calling_code(self):
        """
        Get the country code as an integer.
        """
        return self._country_calling_code

    def get_phone_number_without_country_code(self):
        """
        Get the phone number without the country code.
        """
        return self.raw_phone_number

    def can_receive_sms(self):
        return False

    def get_cleaned_phone_number(self):
        """
        Get the cleaned phone number.

        This returns `None` if we do not have (or can detect) a country calling code,
        or if the phone number is blank.

        If you just want to normalize the phone number, use :meth:`.get_normalized_phone_number`.
        """
        country_code = self.get_country_calling_code()
        phone_number = self.get_phone_number_without_country_code()
        if not country_code or not phone_number:
            return None
        return f'+{country_code}{phone_number}'

    def _strip_whitespace(self, string):
        return self.STRIP_WHITESPACE_PATTERN.sub('', string)

    def get_normalized_phone_number(self):
        """
        Get the normalized full phone number with country code (if there a country code can be detected).
        """
        cleaned_phone_number = self.get_cleaned_phone_number()
        if cleaned_phone_number:
            return cleaned_phone_number
        return self._strip_whitespace(self.raw_phone_number)


class NorwegianPhoneNumberHandler(BasePhoneNumberHandler):
    """
    Simple handler that works if you only have norwegian users.
    """
    STRIP_WHITESPACE_PATTERN = re.compile(r'\s+')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._clean_raw_phone_number = self._strip_whitespace(self.raw_phone_number)

    def get_country_calling_code(self):
        if self._country_calling_code:
            return self._country_calling_code
        if self._clean_raw_phone_number.startswith('00') and len(self._clean_raw_phone_number) == 12:
            if self._clean_raw_phone_number[2:4] == '47':
                return 47
        elif self._clean_raw_phone_number.startswith('+') and len(self._clean_raw_phone_number) == 11:
            if self._clean_raw_phone_number[1:3] == '47':
                return 47
        elif len(self._clean_raw_phone_number) == 8:
            return 47
        return None

    def get_phone_number_without_country_code(self):
        """
        Get the phone number without the country code.
        """
        if self.get_country_calling_code() != 47:
            return None
        if self._clean_raw_phone_number.startswith('00'):
            return self._clean_raw_phone_number[4:]
        elif self._clean_raw_phone_number.startswith('+'):
            return self._clean_raw_phone_number[3:]
        return self._clean_raw_phone_number

    def can_receive_sms(self):
        if self.get_country_calling_code() != 47:
            return False
        phone_number = self.get_phone_number_without_country_code()
        return phone_number.startswith('9') or phone_number.startswith('4')


def _get_handler_class():
    adapter_class_path = getattr(settings, 'IEVV_PHONE_NUMBER_HANDLER', None) \
                         or 'ievv_opensource.ievv_sms.phone_number_handler.BasePhoneNumberHandler'
    return import_string(adapter_class_path)


def get(phone_number):
    """
    Get the configured phone number handler.

    Returns:
        ievv_opensource.ievv_sms.phone_number_handler.BasePhoneNumberHandler: The currently configured
            phone number handler.
    """
    handler_class = _get_handler_class()
    return handler_class(phone_number)
