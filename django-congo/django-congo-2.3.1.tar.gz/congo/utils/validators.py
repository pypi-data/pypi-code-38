# -*- coding: utf-8 -*-
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _
import re

# @og Deprecated
POLISH_PHONE_REGEX = RegexValidator(regex = r'^(\+48|0048)?\d{9}$', message = _(u"Obowiązujący format numeru telefonu to \"999999999\". Dozwolone jest 9 cyfr"))
PHONE_REGEX = RegexValidator(regex = r'^\+?1?\d{9,15}$', message = _(u"Obowiązujący format numeru telefonu to \"+99999999999. Dozwolone od 9 do 15 cyfr."))

class PolishPhoneValidator(RegexValidator):
    regex = r'^(\+|00)48( )?\d{9}$'
    message = _(u"Poprawny format to \"+48 999999999\" (9 cyfr).")

class PhoneValidator(RegexValidator):
    regex = r'^(\+|00)(9[976]\d|8[987530]\d|6[987]\d|5[90]\d|42\d|3[875]\d|2[98654321]\d|9[8543210]|8[6421]|6[6543210]|5[87654321]|4[987654310]|3[9643210]|2[70]|7|1)( )?\d{1,14}$'
    message = _(u"Poprawny format to \"+99 999999999 (od 9 do 15 cyfr).")

# @bz uzyc https://docs.djangoproject.com/en/1.11/ref/validators/#regexvalidator
def matches_regex(str, regex):
    return re.match(regex, str)
