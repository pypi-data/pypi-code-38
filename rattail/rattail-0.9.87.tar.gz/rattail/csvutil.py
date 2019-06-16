# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2018 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
CSV File Utilities

Contains various utilities relating to CSV file processing.

.. note::
   This module is named ``csvutil`` instead of ``csv`` primarily as a
   workaround to the problem of ``PythonService.exe`` insisting on doing
   relative imports.
"""

from __future__ import unicode_literals, absolute_import

import csv
import codecs
from six import StringIO

import six


class DictWriter(csv.DictWriter):
    """
    Convenience implementation of ``csv.DictWriter``.

    This exists only to provide the :meth:`writeheader()` method on Python 2.6.
    """

    def writeheader(self):
        if hasattr(csv.DictWriter, 'writeheader'):
            return csv.DictWriter.writeheader(self)
        self.writer.writerow(self.fieldnames)


class UTF8Recoder(object):
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8.

    .. note::
       This class was stolen from the Python 2.7 documentation.
    """

    def __init__(self, fileobj, encoding, errors='strict'):
        self.errors = errors
        self.reader = codecs.getreader(encoding)(fileobj, errors=self.errors)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode('utf_8')


if six.PY3:

    # TODO: probably should deprecate / remove this for py3?
    UnicodeReader = csv.reader

else: # PY2

    class UnicodeReader(object):
        """
        A CSV reader which will iterate over lines in a CSV file, which is encoded
        in the given encoding.

        .. note::
           This class was stolen from the Python 2.7 documentation.
        """

        def __init__(self, fileobj, dialect=csv.excel, encoding='utf_8', errors='strict', **kwargs):
            fileobj = UTF8Recoder(fileobj, encoding, errors=errors)
            self.reader = csv.reader(fileobj, dialect=dialect, **kwargs)

        def __iter__(self):
            return self

        def next(self):
            row = self.reader.next()
            return [six.text_type(x, 'utf_8') for x in row]


if six.PY3:
    UnicodeDictReader = csv.DictReader

else: # PY2

    class UnicodeDictReader(object):
        """
        A CSV Dict reader which will iterate over lines in a CSV file, which is
        encoded in the given encoding.
        """

        def __init__(self, fileobj, dialect=csv.excel, encoding='utf_8', errors='strict', **kwargs):
            recoder = UTF8Recoder(fileobj, encoding, errors=errors)
            fieldnames = kwargs.pop('fieldnames', None)
            self.reader = csv.reader(recoder, dialect=dialect, **kwargs)
            if fieldnames:
                self.header = fieldnames
            else:
                self.header = self.reader.next()

        def next(self):
            row = self.reader.next()
            vals = [six.text_type(s, 'utf_8') for s in row]
            return dict((self.header[i], vals[i]) for i in range(len(self.header)))

        def __iter__(self):
            return self


if six.PY3:
    UnicodeWriter = csv.writer

else: # PY2

    class UnicodeWriter(object):
        """
        A CSV writer which will write rows to CSV file "f", which is encoded in the
        given encoding.

        .. note::
           This class was stolen from the Python 2.7 documentation.
        """

        def __init__(self, f, dialect='excel', encoding='utf_8', encoding_errors='strict', **kwargs):
            # Redirect output to a queue
            self.queue = StringIO()
            self.writer = csv.writer(self.queue, dialect=dialect, **kwargs)
            self.stream = f
            self.encoder = codecs.getincrementalencoder(encoding)(encoding_errors)

        def writerow(self, row):
            self.writer.writerow([s.encode('utf_8') for s in row])
            # Fetch UTF-8 output from the queue ...
            data = self.queue.getvalue()
            data = data.decode('utf_8')
            # ... and reencode it into the target encoding
            data = self.encoder.encode(data)
            # write to the target stream
            self.stream.write(data)
            # empty queue
            self.queue.truncate(0)

        def writerows(self, rows):
            for row in rows:
                self.writerow(row)


if six.PY3:
    UnicodeDictWriter = csv.DictWriter

else: # PY2

    class UnicodeDictWriter(UnicodeWriter):
        """
        A ``DictWriter``-ish class which accepts row data as Unicode and can write
        to the file with any encoding.

        .. note::
           This logic was stolen from a `Django snippet`_.  The original docstring
           from this snippet follows ("sic" applies here; our logic uses 'utf_8'
           encoding and regular 'excel' dialect by default):

        A CSV writer that produces Excel-compatibly CSV files from unicode data.
        Uses UTF-16 and tabs as delimeters - it turns out this is the only way to
        get unicode data in to Excel using CSV.

        Usage example::

           fp = open('my-file.csv', 'wb')
           writer = UnicodeDictWriter(fp, ['name', 'age', 'shoesize'])
           writer.writerows([
               {'name': u'Bob', 'age': 22, 'shoesize': 7},
               {'name': u'Sue', 'age': 28, 'shoesize': 6},
               {'name': u'Ben', 'age': 31, 'shoesize': 8},
               # \xc3\x80 is LATIN CAPITAL LETTER A WITH MACRON
               {'name': '\xc4\x80dam'.decode('utf8'), 'age': 11, 'shoesize': 4},
           ])
           fp.close()

        Initially derived from http://docs.python.org/lib/csv-examples.html

        .. _`Django snippet`: https://djangosnippets.org/snippets/993/
        """

        def __init__(self, f, fields, dialect='excel', encoding='utf_8', **kwds):
            super(UnicodeDictWriter, self).__init__(f, dialect, encoding, **kwds)
            self.fields = fields

        def writerow(self, rowdict):
            # import ipdb; ipdb.set_trace()
            row = [rowdict.get(field, '') for field in self.fields]
            super(UnicodeDictWriter, self).writerow(row)

        def writeheader(self):
            super(UnicodeDictWriter, self).writerow(self.fields)
