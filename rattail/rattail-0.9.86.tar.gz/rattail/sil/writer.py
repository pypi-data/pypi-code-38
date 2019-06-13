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
SIL Writer
"""

from __future__ import unicode_literals, absolute_import

import datetime
from decimal import Decimal

import six

from rattail import __version__
from rattail.core import Object
from rattail.gpc import GPC
from rattail.files import temp_path
from rattail.sil import batches
from rattail.util import progress_loop


class Writer(Object):

    def __init__(self, path=None, **kwargs):
        Object.__init__(self, **kwargs)
        if path is None:
            path = self.temp_path(suffix='.sil')
        self.sil_path = path
        self.fileobj = self.get_fileobj()

    def get_fileobj(self):
        return open(self.sil_path, 'wb')

    def close(self):
        self.fileobj.close()

    @classmethod
    def temp_path(cls, **kwargs):
        """
        Generate a temporary file path, using
        :func:`rattail.files.temp_path()`.
        """
        kwargs.setdefault('prefix', 'rattail.')
        kwargs.setdefault('suffix', '.sil')
        return temp_path(**kwargs)

    def consume_batch_id(self, source='RATAIL'):
        """
        Consume and return a SIL-compatible batch ID.
        """
        return batches.consume_batch_id(source)

    def val(self, value):
        """
        Returns a string version of ``value``, suitable for inclusion within a
        data row of a SIL batch.  The conversion is done as follows:

        If ``value`` is ``None``, an empty string is returned.

        If it is an ``int`` or ``decimal.Decimal`` instance, it is converted
        directly to a string (i.e. not quoted).

        If it is a ``datetime.date`` instance, it will be formatted as
        ``'%Y%j'``.

        If it is a ``datetime.time`` instance, it will be formatted as
        ``'%H%M'``.

        Otherwise, it is converted to a string if necessary, and quoted with
        apostrophes escaped.
        """
        if value is None:
            return ''
        if isinstance(value, GPC):
            return six.text_type(value)
        if isinstance(value, int):
            return six.text_type(value)
        if isinstance(value, float):
            return six.text_type(value)
        if isinstance(value, Decimal):
            return six.text_type(value)
        if isinstance(value, datetime.date):
            return value.strftime('%Y%j')
        if isinstance(value, datetime.time):
            return value.strftime('%H%M')
        if not isinstance(value, six.string_types):
            value = six.text_type(value)
        return "'{}'".format(value.replace("'", "''"))

    def write(self, string):
        self.fileobj.write(string)

    def write_batch_header_raw(self, **kwargs):
        """
        Writes a SIL batch header string.  All keyword arguments correspond to
        the SIL specification for the Batch Header Dictionary.

        **Batch Header Dictionary:**

        ====  ====    ====  ===========
        Name  Type    Size  Description
        ====  ====    ====  ===========
        H01   CHAR       2  Batch Type
        H02   CHAR       8  Batch Identifier
        H03   CHAR       6  Source Identifier
        H04   CHAR       6  Destination Identifier
        H05   CHAR      12  Audit File Name
        H06   CHAR      12  Response File Name
        H07   DATE       7  Origin Date
        H08   TIME       4  Origin Time
        H09   DATE       7  Execution (Apply) Date
        H10   DATE       4  Execution (Apply) Time
        H11   DATE       7  Purge Date
        H12   CHAR       6  Action Type
        H13   CHAR      50  Batch Description
        H14   CHAR      30  User Defined
        H15   CHAR      30  User Defined
        H16   CHAR      30  User Defined
        H17   NUMBER     1  Warning Level
        H18   NUMBER     5  Maximum Error Count
        H19   CHAR       7  SIL Level/Revision
        H20   CHAR       4  Software Revision
        H21   CHAR      50  Primary Key
        H22   CHAR     512  System Specific Command
        H23   CHAR       8  Dictionary Revision

        Consult the SIL Specification for more information.
        """

        kw = kwargs

        # Don't quote H09 if special "immediate" value.
        H09 = kw.get('H09')
        if H09 != '0000000':
            H09 = self.val(H09)

        # Don't quote H10 if special "immediate" value.
        H10 = kw.get('H10')
        if H10 != '0000':
            H10 = self.val(H10)

        row = [
            self.val(kw.get('H01')),
            self.val(kw.get('H02')),
            self.val(kw.get('H03')),
            self.val(kw.get('H04')),
            self.val(kw.get('H05')),
            self.val(kw.get('H06')),
            self.val(kw.get('H07')),
            self.val(kw.get('H08')),
            H09,
            H10,
            self.val(kw.get('H11')),
            self.val(kw.get('H12')),
            self.val(kw.get('H13')),
            self.val(kw.get('H14')),
            self.val(kw.get('H15')),
            self.val(kw.get('H16')),
            self.val(kw.get('H17')),
            self.val(kw.get('H18')),
            self.val(kw.get('H19')),
            self.val(kw.get('H20')),
            self.val(kw.get('H21')),
            self.val(kw.get('H22')),
            self.val(kw.get('H23')),
            ]

        self.write('INSERT INTO HEADER_DCT VALUES\n')
        self.write_row(row, quote=False, last=True)
        self.write('\n')

    def write_batch_header(self, **kwargs):
        """
        Convenience method to take some of the gruntwork out of writing batch
        headers.

        If you do not override ``H03`` (Source Identifier), then Rattail will
        provide a default value for it, as well as ``H20`` (Software Revision)
        - that is, unless you've supplied it yourself.

        If you do not provide values for ``H07`` or ``H08``, the current date
        and time will be assumed.

        If you do not provide values for ``H09`` or ``H10``, it is assumed that
        you wish the batch to be immediately executable.  Default values will
        be provided accordingly.

        If you do not provide a value for ``H11`` (Purge Date), a default of 90
        days from the current date will be assumed.
        """

        kw = kwargs

        # Provide default for H03 (Source Identifier) if none specified.
        if 'H03' not in kw:
            kw['H03'] = 'RATAIL'

            # Provide default for H20 (Software Revision) if none specified.
            if 'H20' not in kw:
                kw['H20'] = __version__[:4]

        # Provide default (current local time) values H07 and H08 (Origin Date /
        # Time) if none was specified.
        now = datetime.datetime.now()
        if 'H07' not in kw:
            kw['H07'] = now.date()
        if 'H08' not in kw:
            kw['H08'] = now.time()

        # Use special "immediate" values for H09 and H10 (Execution (Apply) Date /
        # Time) if none was specified.
        if 'H09' not in kw:
            kw['H09'] = '0000000'
        if 'H10' not in kw:
            kw['H10'] = '0000'

        # Provide default value for H11 (Purge Date) if none was specified.
        if 'H11' not in kw:
            kw['H11'] = (now + datetime.timedelta(days=90)).date()

        self.write_batch_header_raw(**kw)

    def write_create_header(self, **kwargs):
        """
        Convenience method to take some of the gruntwork out of writing batch
        headers.

        The following default values are provided by this method:

        * ``H01`` = ``'HC'``
        * ``H12`` = ``'LOAD'``

        This method also calls :meth:`write_batch_header()`; see its
        documentation for the other default values provided.
        """

        kw = kwargs
        kw.setdefault('H01', 'HC')
        kw.setdefault('H12', 'LOAD')
        self.write_batch_header(**kw)

    def write_maintenance_header(self, **kwargs):
        """
        Convenience method to take some of the gruntwork out of writing batch
        headers.

        The following default values are provided by this method:

        * ``H01`` = ``'HM'``

        This method also calls :meth:`write_batch_header()`; see its
        documentation for the other default values provided.
        """

        kw = kwargs
        kw.setdefault('H01', 'HM')
        self.write_batch_header(**kw)

    def write_row(self, row, quote=True, last=False):
        """
        Writes a SIL row string.

        ``row`` should be a sequence of values.

        If ``quote`` is ``True``, each value in ``row`` will be ran through the
        :func:`val()` function before being written.  If it is ``False``, the
        values are written as-is.

        If ``last`` is ``True``, then ``';'`` will be used as the statement
        terminator; otherwise ``','`` is used.
        """

        terminator = ';' if last else ','
        if quote:
            row = [self.val(x) for x in row]
        self.write('(' + ','.join(row) + ')' + terminator + '\n')

    def write_rows(self, rows, count=None, progress=None,
                   progress_text="Writing data to SIL file"):
        """
        Write some SIL data row strings to the file object.

        This is a wrapper around :meth:`write_row()` which adds some
        convenience, and hopefully improves efficiency.  It should make calling
        code a little prettier if nothing else.

        :param rows: Provider of data rows, each of which should be a sequence
          of data suitable for use with :meth:`write_row()`.  ``rows`` itself
          may be a sequence or a generator, or a callable which returns either
          of these.

        :param count: Optional count of ``rows``, in case ``len(rows)`` doesn't
          give the right answer or is expensive to calculate.

        :param progress: Optional progress indicator factory.

        :returns: ``True``, unless the operation is canceled by the user.
        """
        if callable(rows):
            rows = rows()
        if count is None:
            count = len(rows)

        def write(row, i):
            self.write_row(row, last=i == count)

        return progress_loop(write, rows, progress,
                             message=progress_text,
                             count=count, allow_cancel=True)
