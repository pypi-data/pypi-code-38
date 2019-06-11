# -*- coding: utf-8 -*-

from future.utils import python_2_unicode_compatible
from tableutil import Table, KEY_VALUE_HEADINGS, KEY, VALUE

__all__ = ['APIUnresponsive',
           'APIMissing',
           'APIError']


class APIUnresponsive(Exception):
    pass


class APIMissing(Exception):
    pass


@python_2_unicode_compatible
class APIError(Exception):

    def __init__(self,
                 message=None,
                 response=None):
        """

        :param message: Text
        :param response: A requests Response instance
        """
        # Call the base class constructor with the parameters it needs
        super(APIError, self).__init__(message)

        self.response = response

        if self.response is not None:
            self.table = Table(title=u'{method}:{uri}'.format(method=self.response.request.method,
                                                              uri=self.response.url),
                               show_column_headings=False,
                               row_numbers=False,
                               headings=KEY_VALUE_HEADINGS,
                               table_format=Table.TEXT_TABLE_FORMAT,
                               show_separators=True)

            if hasattr(self, 'message'):
                self.table.add_row({KEY: u'Info',
                                    VALUE: self.message})

            self.table.add_row({KEY: u'Status',
                                VALUE: self.response.status_code})
            self.table.add_row({KEY: u'Content',
                                VALUE: self.response.content})

        elif hasattr(self, 'message'):
            self.table = self.message

        else:
            self.table = u'No additional information'

    def __str__(self):
        try:
            return self.table.text()

        except Exception:
            return super(APIError, self).__str__()
