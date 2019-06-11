# Copyright (c) 2012 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

from contextlib import contextmanager

import os.path
import re

def get_bytes(byte_string):
    symbol = { 'KB': 10**3, 'KiB': 2**10,
               'MB': 10**6, 'MiB': 2**20,
               'GB': 10**9, 'GiB': 2**30,
               'TB': 10**12, 'TiB': 2**40,
               'PB': 10**16, 'PiB': 2**50,
               'EB': 10**18, 'EiB': 2**60,}
    if byte_string.isdigit():
        return int(byte_string)
    elif byte_string[-2:] in symbol:
        return int(float(byte_string[0:-2]) * symbol[byte_string[-2:]])
    elif byte_string[-3:] in symbol:
        return int(float(byte_string[0:-3]) * symbol[byte_string[-3:]])
    else:
        raise ValueError("Limit format is not acceptable!")

def pretty_bytes(num_bytes):
    '''
    Return a string represenation of @p num_bytes, up to 1 decimal place. Units
    are in base 10 (i.e., no kibibytes, etc.).

    pretty_bytes(0) --> "0.0 B"
    pretty_bytes(999) --> "1.0 KB"
    pretty_bytes(1000) --> "1.0 KB"
    pretty_bytes(1100) --> "1.1 KB"
    pretty_bytes(8 * 10**16) --> "8.0 PB"
    pretty_bytes(1.1 * 10**18) --> "1.1 EB"
    '''
    symbol = { 10**3: 'KB',
               10**6: 'MB',
               10**9: 'GB',
               10**12: 'TB',
               10**16: 'PB',
               10**18: 'EB' }
    # Cast to a float first, for division below and for consistency in output.
    smallest = num_bytes = float(num_bytes)
    size_str = str(smallest) + " B"
    for k, v in symbol.items():
        size = round(num_bytes / k, 1)
        if size >= 1 and size < smallest:
            smallest = size
            size_str = "{} {}".format(str(size), v)
    return size_str

# Wrapper needed mocking.
# (patching __builtin__.open directly causes issues when running tests)
@contextmanager
def open_file(*args, **kwargs):
    f = open(*args, **kwargs)
    yield f
    f.close()

def bool_from_string(value):
    value = value.lower()
    if value in ['t', 'true', '1', 'yes', 'on', 'enabled']:
        return True
    if value in ['f', 'false', '0', 'no', 'off', 'disabled']:
        return False
    raise ValueError('Unable to convert "%s" to boolean' % value)

figlet_yes_or_no = '''\
__   _______ ____      _   _  ___ ___
\\ \\ / / ____/ ___|    | \\ | |/ _ \\__ \\
 \\ V /|  _| \\___ \\    |  \\| | | | |/ /
  | | | |___ ___) |   | |\\  | |_| |_|
  |_| |_____|____/ or |_| \\_|\\___/(_) '''

def ask(prompt):
    return raw_input('{} '.format(prompt)).strip().lower()

def are_you_sure():
    prompts = ['yes or no?', 'Yes or No?', 'YES or NO?', figlet_yes_or_no]
    times = 0
    answer = ask(prompts[times])
    while answer != 'yes' and answer != 'no':
        times += 1
        answer = ask(prompts[min(times, len(prompts) - 1)])
    return answer == 'yes'

# Join two paths, force basename to be relative
def path_join(dirname, basename):
    if basename.startswith('/'):
        basename = basename[1:]
    return '{}/{}'.format(dirname, basename)

# Emulate UNIX basename behavior: basename('/foo/bar/') => 'bar'
def unix_path_split(path):
    dirname, basename = os.path.split(path)
    if not basename:
        dirname, basename = os.path.split(dirname)
    return (dirname, basename)

def to_unicode(val, decoder='utf-8'):
    '''
    Coerce a value to unicode, if possible, attempting the given decoder if
    @p val isn't already unicode and str(val) returns non-ascii characters.

    Note that there really isn't a standard one-stop call that does this:
    - unicode(val) uses the default decoder, which is usually ascii.
    - unicode(val, decoder) only works on strings; it won't attempt str(val),
      and won't pass through unicode values that are already unicode.
    - unicode(str(val), decoder) would coerce a unicode to string using the
      default encoder, which is usually ascii.
    '''
    try:
        return unicode(val)
    except UnicodeDecodeError:
        return unicode(str(val), decoder)

def check_unicode(val, friendly_name):
    '''
    Produce a relatively useful error message if @p cannot be coerced to
    unicode.  This is similar to the logic the json module would use when
    encoding @p val, but json produces a cryptic utf8 codec error on failure.
    '''
    try:
        # Don't convert None to u'None'
        return to_unicode(val) if val is not None else None
    except UnicodeDecodeError:
        # This will throw the desired error message:
        return check_ascii(val, friendly_name)

def check_ascii(val, friendly_name):
    '''
    Produce a relatively useful error message if str(val) contains non-ascii
    characters.
    '''
    if val is None:
        # Don't convert None to "None"
        return None
    try:
        return str(val).encode('ascii')
    except (UnicodeDecodeError, UnicodeEncodeError):
        # Produce an error message with all non-ascii characters replaced with
        # '?'.  Note that str.encode would attempt to decode to unicode using
        # the default encoder, which may fail if the string is non-ascii, so the
        # input is first decoded to unicode with all non-ascii characters
        # replaced, which produces non-ascii replacement characters, which are
        # then replaced when encoding to ascii :/
        raise ValueError(
            'The string "{}" for {} contains invalid characters'.format(
                str(val).decode('ascii', 'replace').encode('ascii', 'replace'),
                friendly_name))


def get_certificate_from_pem_format_string(content):
    CERT_RE = (
    r'-----BEGIN CERTIFICATE-----\s+' +
    r'([\S\s]*)\s+' +
    r'-----END CERTIFICATE-----')

    match = re.search(CERT_RE, content)
    return match.group(1) if match else None

def get_rsa_private_key_from_pem_format_string(content):
    RSA_PRIV_KEY_RE = (
    r'-----BEGIN RSA PRIVATE KEY-----\s+' +
    r'([\S\s]*)\s+' +
    r'-----END RSA PRIVATE KEY-----')

    match = re.search(RSA_PRIV_KEY_RE, content)
    return match.group(1) if match else None

def tabulate(table, headers=None):
    '''
    Print a pretty table with fixed-width columns.
    @p table A list of rows, which are also lists.  All rows must have the same
         length.
    @p headers A list of column header strings, or "firstrow" to use the first
         row as column headers, or None to not print column headers.
    This implements a subset of the functionality of the tabulate module that's
    in the toolchain.  It is re-implemented to avoid taking that dependency for
    our public CLI package.
    '''

    # Pull the header row out of the table, if it is integrated:
    if headers == 'firstrow':
        headers = table[0]
        table = table[1:]

    # Find the width of each columnn
    if headers:
        col_widths = [max(len(to_unicode(h)), 1) for h in headers]
    else:
        col_count = len(table[0]) if table else 0
        col_widths = [1] * col_count
    for row in table:
        assert len(row) == len(col_widths)
        col_widths = [max(m, len(to_unicode(v)))
            for m, v in zip(col_widths, row)]

    sep = u'  '
    lines = []
    if headers:
        lines.append(sep.join(u'{:<{}}'.format(to_unicode(h), w)
            for h, w in zip(headers, col_widths)))
        lines.append(sep.join(u'=' * w for w in col_widths))
    for row in table:
        lines.append(sep.join(u'{:<{}}'.format(to_unicode(v), w)
            for v, w in zip(row, col_widths)))

    return u'\n'.join(lines)

def edit_distance(str1, str2):
    '''
    Compute the Levenshtein distance between @p str1 and @p str2.

    This is evolved from the Wagner-Fischer Dynamic Programming solution that
    has been posted in multiple places all over Google.
    '''
    if len(str1) < len(str2):
        str1, str2 = str2, str1

    if len(str2) == 0:
        return len(str1)

    # DP Algo: You build an NxM matrix where
    #   N := len(str1)+1
    #   M := len(str2)+1.
    # Note that N and M are 1 larger than the string lengths because we need a
    # row and column in the matrix to represent the empty string on either
    # side of the computation. Each cell will represent the minimum edit
    # distance to get to a substring of str1 and str2 of lengths i and j
    # where 0 <= i <= len(str1) and 0 <= j <= len(str2).

    #   ex: str1 = foo, str2 = boo
    #          b   o   o
    #    +---------------+
    #    | 0 | 1 | 2 | 3 |
    #  f | 1 | 1 | 2 | 3 |
    #  o | 2 | 2 | 1 | 2 |
    #  o | 3 | 3 | 2 | 1 | <--- min distance is 1
    #    +---------------+

    # first, we start by populating the first  row that represents if str1 was
    # empty string. Hence, each cell is just the number of inserts to get to
    # str2. +1 required since range is a half-open interval.
    prev_row = list(range(len(str2) + 1))
    for i, char1 in enumerate(str1):
        # This is the first column which represents if str2 was empty but str1
        # wasn't.
        cur_row = [i+1]
        for j, char2 in enumerate(str2):
            insertions = prev_row[j+1] + 1
            deletions = cur_row[j] + 1
            substitutions = prev_row[j]
            if char1 != char2:
                substitutions += 1
            cur_row.append(min(insertions, deletions, substitutions))
        prev_row = cur_row
    return prev_row[-1]

#  _____         _      _    _ _
# |_   _|____  _| |_   / \  | (_) __ _ _ __   ___ _ __
#   | |/ _ \ \/ / __| / _ \ | | |/ _` | '_ \ / _ \ '__|
#   | |  __/>  <| |_ / ___ \| | | (_| | | | |  __/ |
#   |_|\___/_/\_\\__/_/   \_\_|_|\__, |_| |_|\___|_|
#                                |___/
#  FIGLET: TextAligner
#

SINGLE_LEVEL_INDENT = ' ' * 4

class TextAligner(object):
    '''
    Builds up a set of lines of text, with padding for named fields to have the
    same width in all lines where that field occurs.
    This makes it easy to build up complex text where there is interleaving of
    lines with different alignment structure.
    '''
    def __init__(self, indent=None, max_width=None):
        self.indent_lvl = 0
        # Tracks the maximum length for each field.
        self.max_lengths = {}
        # Lines to format.  tuple(indent, fmt, positional_args, aligned_kwargs)
        self.lines = []
        # Custom format specs for aligned fields.
        self.formats = {}
        # Maximum column width. Changes based on indent level.
        # XXX jkong: make max_width more general
        # Used in some methods to concatenate shorter lines together, but does
        # not generally wrap longer lines added to the class.
        self.max_width = max_width or 80
        # The string used to indent lines
        self.indent_val = indent or ' ' * 4

    @contextmanager
    def indented(self):
        '''
        Increase the indent level by one for all lines added within this
        context. This may be nested for multiple indentation levels.
        '''
        self.indent_lvl += 1
        self.max_width -= len(self.indent_val)
        yield
        self.indent_lvl -= 1
        self.max_width += len(self.indent_val)

    def set_padding(self, **kwargs):
        '''
        Override the default format specification that controls how named fields
        are padded.  Each keyword argument names a field, and the value provides
        the "[[fill]align][sign][#][0]" subsection of the python format string
        specification mini-language.  By default, fields are right-padded with
        spaces.
        e.g. self.set_padding(foo="0>") will result in the foo field being
        left-padded with zeroes.
        '''
        self.formats.update(kwargs)

    def add_line(self, fmt, *args, **kwargs):
        '''
        Add a line to the text.
        @p fmt A format string for the line.
        @p extra_indent if given, added to the current indent level
        @p args positional arguments to the format string, which will not be
            padded.  These must be fixed width in order to be interleaved with
            named fields without breaking alignment.
        @p kwargs keyword arguments to the format string, which will be padded
            for alignment.  If the same format prefix always precedes a given
            field, that field will always start at the same column.
        '''
        self.lines.append((
            self.indent_lvl + kwargs.pop('extra_indent', 0), fmt, args, kwargs))
        for name, value in kwargs.items():
            self.max_lengths[name] = max(
                len(str(value)), self.max_lengths.get(name, 0))

    def add_lines(self, lines, *args, **kwargs):
        '''
        Simple helper function to ergonomically add multiple lines at once.
        @p lines An iterable containing lines to add
        '''
        for line in lines:
            # NB: This will result in the same set of *args being passed in for
            # each line.
            self.add_line(line, *args, **kwargs)

    def format_list(self, items, sep=None, max_len=None):
        '''
        Concatenates fragments made from @p items to build lines of at most @p
        max_len characters. Each individual item must be shorter than max_len.
        '''
        sep = sep or ', '
        max_len = max_len or self.max_width

        # Account for adding separator at the end of the line
        max_len -= len(sep)

        line = ""
        for i, item in enumerate(items):
            if i == 0:
                line = str(item)
            elif len(line + sep + item) <= max_len:
                line += "{sep}{item}".format(sep=sep, item=item)
            else:
                yield "{line}{sep}".format(line=line, sep=sep)
                line = str(item)
        yield line

    def add_concatenated_lines(self, items):
        '''
        Simple wrapper function that takes in a list and adds width-formatted
        lines.
        '''
        self.add_lines(self.format_list(items))

    def add_wrapped_table(self, table):
        '''
        Takes a list of pairs (tuples) and adds lines for a two-column table
        with wrapped rows.
        @p table The list of (k, v) pairs to be turned into a table.
        '''
        # Find the maximum left column length in characters
        max_col = max([len(a[0]) for a in table]) + len(self.indent_val)

        for k, v in table:
            # Format the right column
            max_len = self.max_width - max_col
            if type(v) is str:
                line_gen = self.format_list(
                    v.split(' '), sep=' ', max_len=max_len)
            else:
                line_gen = self.format_list(v, max_len=max_len)
            lines = list(line_gen)

            # Prepend the first line of values with the key, and then any
            # following lines with the appropriate number of spaces
            pad = ' ' * (max_col - len(k))
            self.add_line(k + pad + lines[0])
            for line in lines[1:]:
                self.add_line((' ' * max_col) + line)

    def write(self, outfile):
        for indent, fmt, positional, aligned in self.lines:
            # Pad all the aligned fields to the observed max width:
            padded = {
                t: '{:{f}{w}}'.format(
                    # NB: str(v) to avoid format trying to get clever based on
                    # type, e.g. formatting True as "1"
                    str(v), w=self.max_lengths[t], f=self.formats.get(t, '<'))
                for t, v in aligned.items()}

            outfile.write(self.indent_val*indent)
            outfile.write(fmt.format(*positional, **padded))
            outfile.write('\n')
