# encoding: utf-8

from uiutil.widget.entry import TextEntry
from ..validation import valid_ipv4, valid_ipv4_network


class IPv4Entry(TextEntry):
    DEFAULT_VALUE = u'0.0.0.0'
    VALID_CHARACTERS = u'0123456789.'

    def __init__(self,
                 *args,
                 **kwargs):
        super(IPv4Entry, self).__init__(*args,
                                        **kwargs)

    @staticmethod
    def valid(value):
        return valid_ipv4(value)

    def permit_invalid_value(self,
                             value):
        return not [c for c in value if c not in IPv4Entry.VALID_CHARACTERS]


class IPv4NetworkEntry(TextEntry):
    DEFAULT_VALUE = u'0.0.0.0'
    VALID_CHARACTERS = u'0123456789./'

    def __init__(self,
                 strict=True,
                 *args,
                 **kwargs):

        self.strict = strict

        super(IPv4NetworkEntry, self).__init__(*args,
                                               **kwargs)

    def valid(self,
              value):
        return valid_ipv4_network(value,
                                  strict=self.strict)

    def permit_invalid_value(self,
                             value):
        return not [c for c in value if c not in IPv4NetworkEntry.VALID_CHARACTERS]
