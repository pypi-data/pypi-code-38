# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module contains the CommaSeperatedValueFile plugin for fastr
"""

import csv
import os
import fastr
import urllib.parse
from fastr import exceptions, resources
from fastr.core.ioplugin import IOPlugin


class CommaSeperatedValueFile(IOPlugin):
    """
    The CommaSeperatedValueFile an expand-only type of IOPlugin. No URLs
    can actually be fetched, but it can expand a single URL into a larger
    amount of URLs.

    The ``csv://`` URL is a ``vfs://`` URL with a number of query variables
    available. The URL mount and path should point to a valid CSV file. The
    query variable then specify what column(s) of the file should be used.

    The following variable can be set in the query:

    ============= =============================================================================================
    variable      usage
    ============= =============================================================================================
    value         the column containing the value of interest, can be int for index or string for key
    id            the column containing the sample id (optional)
    header        indicates if the first row is considered the header, can be ``true`` or ``false`` (optional)
    delimiter     the delimiter used in the csv file (optional)
    quote         the quote character used in the csv file (optional)
    reformat      a reformatting string so that ``value = reformat.format(value)`` (used before relative_path)
    relative_path indicates the entries are relative paths (for files), can be ``true`` or ``false`` (optional)
    ============= =============================================================================================

    The header is by default ``false`` if the neither the ``value`` and ``id``
    are set as a string. If either of these are a string, the header is
    required to define the column names and it automatically is assumed ``true``

    The delimiter and quota characters of the file should be detected
    automatically using the :class:`Sniffer <csv.Sniffer>`, but can be forced
    by setting them in the URL.

    Example of valid ``csv`` URLs::

        # Use the first column in the file (no header row assumed)
        csv://mount/some/dir/file.csv?value=0

        # Use the images column in the file (first row is assumed header row)
        csv://mount/some/dir/file.csv?value=images

        # Use the segmentations column in the file (first row is assumed header row)
        # and use the id column as the sample id
        csv://mount/some/dir/file.csv?value=segmentations&id=id

        # Use the first column as the id and the second column as the value
        # and skip the first row (considered the header)
        csv://mount/some/dir/file.csv?value=1&id=0&header=true

        # Use the first column and force the delimiter to be a comma
        csv://mount/some/dir/file.csv?value=0&delimiter=,
    """
    scheme = 'csv'

    def __init__(self):
        super(CommaSeperatedValueFile, self).__init__()

    def expand_url(self, url):
        if fastr.data.url.get_url_scheme(url) != 'csv':
            raise exceptions.FastrValueError('URL not of csv type!')

        # Retrieve base path
        parsed = urllib.parse.urlparse(url)
        csvurl = urllib.parse.urlunparse(urllib.parse.ParseResult(scheme='vfs', netloc=parsed.netloc, path=parsed.path, params='', query='', fragment=''))
        baseurl = urllib.parse.urlunparse(urllib.parse.ParseResult(scheme='vfs', netloc=parsed.netloc, path=os.path.dirname(parsed.path), params='', query='', fragment=''))
        csvpath = resources.ioplugins.url_to_path(csvurl)
        query = urllib.parse.parse_qs(parsed.query)

        # Get dialect options
        dialect_override = {}
        if 'delimiter' in query:
            dialect_override['delimiter'] = query['delimiter'][0]
        if 'quote' in query:
            dialect_override['quotechar'] = query['quote'][0]

        # Check which column the values are in
        data_column = query['value'][0]
        try:
            data_column = int(data_column)
        except ValueError:
            pass

        # Check which column the ids are in
        id_column = query.get('id', [None])[0]
        try:
            id_column = int(id_column)
        except (ValueError, TypeError):
            pass

        # Get info about hear row
        header_row = {'0': False, '1': True, 'false': False, 'true': True, 'none': None}[query.get('header', ('none',))[0]]

        if header_row is None:
            header_row = isinstance(data_column, str) or isinstance(id_column, str)
        elif not header_row and (isinstance(data_column, str) or isinstance(id_column, str)):
            raise ValueError('Cannot use string keys if there is no header row')

        # Check if we expect relative paths
        relpath = {'0': False, '1': True, 'false': False, 'true': True, 'none': False}[query.get('relative_path', ('none',))[0]]
        if baseurl[-1] != '/':
            baseurl = baseurl + '/'

        reformat = query.get('reformat', (None,))[0]

        with open(csvpath, 'rb') as csvfile:
            dialect = csv.Sniffer().sniff(csvfile.read(4096))
            csvfile.seek(0)
            reader = csv.reader(csvfile, dialect, **dialect_override)

            values = []
            ids = []
            for row in reader:
                if header_row:
                    if isinstance(id_column, str):
                        id_column = row.index(id_column)
                    if isinstance(data_column, str):
                        data_column = row.index(data_column)

                    header_row = False
                    continue

                current_value = row[data_column]

                if reformat is not None:
                    current_value = reformat.format(current_value)

                if relpath:
                    current_value = baseurl + current_value

                values.append(current_value)

                ids.append(row[id_column] if id_column is not None else None)

        return tuple((i, value) for i, value in zip(ids, values))


