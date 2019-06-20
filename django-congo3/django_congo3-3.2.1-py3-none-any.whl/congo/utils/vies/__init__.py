# -*- coding: utf-8 -*-
import re

from django.core.exceptions import ValidationError

from django.utils.functional import cached_property
from django.utils.translation import gettext
from suds import WebFault
from suds.client import Client
from operator import mul
from django.utils.itercompat import is_iterable

VIES_WSDL_URL = str('http://ec.europa.eu/taxation_customs/vies/checkVatService.wsdl')# NoQA
VATIN_MAX_LENGTH = 14

def dk_format(v):
    return '%s %s %s %s' % (v[:4], v[4:6], v[6:8], v[8:10])

def gb_format(v):
    if len(v) == 11:
        return '%s %s %s' % (v[:5], v[5:9], v[9:11])
    if len(v) == 14:
        return '%s %s' % (gb_format(v[:11]), v[11:14])
    return v

def fr_format(v):
    return '%s %s' % (v[:4], v[4:])

def pl_checksum(v):
    v = v.replace('-', '').replace(' ', '')
    digits = list(map(int, v))
    weights = (6, 5, 7, 2, 3, 4, 5, 6, 7)
    check_sum = sum(map(mul, digits[0:9], weights)) % 11
    return check_sum == digits[9]

def vat_no_is_valid(vat_no, country, accept_ue_only = True):
    if not (vat_no and country):
        return False

    vat_no = vat_no.replace('-', '').replace(' ', '')
    test = VATIN(country, vat_no)

    try:
        test.verify_country_code()
        try:
            test.verify_regex()
        except ValidationError:
            return False
    except ValidationError:
        if accept_ue_only:
            return False
        else:
            return bool(len(vat_no))
    return True

def check_company_in_vies(vat_no, country):
    country = country.upper()
    if country == "PL":
        vat_no = vat_no.replace('-', '').replace(' ', '')
        test = VATIN(country, vat_no)
        try:
            test.validate()
            return True
        except WebFault:
            return None
        except ValidationError:
            return False
    return None

VIES_OPTIONS = {
    'AT': ('Austria', re.compile(r'^ATU\d{8}$')),
    'BE': ('Belgium', re.compile(r'^BE0?\d{9}$')),
    'BG': ('Bulgaria', re.compile(r'^BG\d{9,10}$')),
    'HR': ('Croatia', re.compile(r'^HR\d{11}$')),
    'CY': ('Cyprus', re.compile(r'^CY\d{8}[A-Z]$')),
    'CZ': ('Czech Republic', re.compile(r'^CZ\d{8,10}$')),
    'DE': ('Germany', re.compile(r'^DE\d{9}$')),
    'DK': ('Denmark', re.compile(r'^DK\d{8}$'), dk_format),
    'EE': ('Estonia', re.compile(r'^EE\d{9}$')),
    'EL': ('Greece', re.compile(r'^EL\d{9}$')),
    'ES': ('Spain', re.compile(r'^ES[A-Z0-9]\d{7}[A-Z0-9]$')),
    'FI': ('Finland', re.compile(r'^FI\d{8}$')),
    'FR': ('France', re.compile(r'^FR[A-HJ-NP-Z0-9][A-HJ-NP-Z0-9]\d{9}$'), fr_format),
    'GB': ('United Kingdom', re.compile(r'^(GB(GD|HA)\d{3}|GB\d{9}|GB\d{12})$'), gb_format),
    'HU': ('Hungary', re.compile(r'^HU\d{8}$')),
    'IE': ('Ireland', re.compile(r'^IE\d[A-Z0-9\+\*]\d{5}[A-Z]{1,2}$')),
    'IT': ('Italy', re.compile(r'^IT\d{11}$')),
    'LT': ('Lithuania', re.compile(r'^LT(\d{9}|\d{12})$')),
    'LU': ('Luxembourg', re.compile(r'^LU\d{8}$')),
    'LV': ('Latvia', re.compile(r'^LV\d{11}$')),
    'MT': ('Malta', re.compile(r'^MT\d{8}$')),
    'NL': ('The Netherlands', re.compile(r'^NL\d{9}B\d{2}$')),
    'PL': ('Poland', re.compile(r'^PL\d{10}$'), None, pl_checksum),
    'PT': ('Portugal', re.compile(r'^PT\d{9}$')),
    'RO': ('Romania', re.compile(r'^RO\d{2,10}$')),
    'SE': ('Sweden', re.compile(r'^SE\d{10}01$')),
    'SI': ('Slovenia', re.compile(r'^SI\d{8}$')),
    'SK': ('Slovakia', re.compile(r'^SK\d{10}$')),
}

VIES_COUNTRY_CHOICES = sorted(
    (('', '--'),) +
    tuple(
        (key, key)
        for key, value in list(VIES_OPTIONS.items()))
)

MEMBER_COUNTRY_CODES = list(VIES_OPTIONS.keys())


class VATIN(object):
    """Object wrapper for the european VAT Identification Number."""

    def __init__(self, country_code, number, clean_chars = '-'):
        self.country_code = country_code
        self.number = number

        if is_iterable(clean_chars):
            for char in clean_chars:
                self.number = self.number.replace(char, '')

    def __str__(self):
        unformated_number = "{country_code}{number}".format(
            country_code = self.country_code,
            number = self.number,
        )

        country = VIES_OPTIONS.get(self.country_code, {})
        if len(country) == 3:
            return country[2](unformated_number)
        return unformated_number

    def __repr__(self):
        return "<VATIN {}>".format(self.__str__())

    def get_country_code(self):
        return self._country_code

    def set_country_code(self, value):
        self._country_code = value.upper()

    country_code = property(get_country_code, set_country_code)

    def get_number(self):
        return self._number

    def set_number(self, value):
        self._number = value.upper().replace(' ', '')

    number = property(get_number, set_number)

    @cached_property
    def data(self):
        """VIES API response data."""
        client = Client(VIES_WSDL_URL)
        try:
            return client.service.checkVat(
                self.country_code,
                self.number
            )
        except WebFault as e:
            raise

    def is_valid(self):
        try:
            self.verify()
            self.validate()
        except ValidationError:
            return False
        else:
            return True

    def verify_country_code(self):
        if not re.match(r'^[a-zA-Z]', self.country_code):
            msg = gettext('%s is not a valid ISO_3166-1 country code.')
            raise ValidationError(msg % self.country_code)

        elif self.country_code not in MEMBER_COUNTRY_CODES:
            msg = gettext('%s is not a european member state.')
            raise ValidationError(msg % self.country_code)

    def verify_regex(self):
        country = dict(list(map(
            lambda x, y: (x, y), ('country', 'regex_validator', 'formatter', 'checksum_validator'),
            VIES_OPTIONS[self.country_code]
        )))

        regex_validator = country['regex_validator']
        if regex_validator and not regex_validator.match("%s%s" % (self.country_code, self.number)):
            msg = gettext("%s does not match the countries VAT ID specifications.")
            raise ValidationError(msg % self)

        checksum_validator = country['checksum_validator']
        if checksum_validator and not checksum_validator(self.number):
            msg = gettext("%s does not match the countries VAT ID specifications.")
            raise ValidationError(msg % self)

    def verify(self):
        self.verify_country_code()
        self.verify_regex()

    def validate(self):
        if not self.data.valid:
            msg = gettext("%s is not a valid VATIN.")
            raise ValidationError(msg % self)

    @classmethod
    def from_str(cls, value):
        """Return a VATIN object by given string."""
        return cls(value[:2].strip(), value[2:].strip())
