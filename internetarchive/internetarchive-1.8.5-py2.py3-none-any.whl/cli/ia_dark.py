# -*- coding: utf-8 -*-
#
# The internetarchive module is a Python/CLI interface to Archive.org.
#
# Copyright (C) 2012-2016 Internet Archive
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Dark an item.

usage:
    ia dark <identifier>... --comment=<comment>
    ia dark --help

options:
    -h, --help
    -c, --comment=<comment>   Curation comment.
"""
from __future__ import print_function, absolute_import
import os
import sys

import six
from docopt import docopt, printable_usage
from schema import Schema, Use, Or, And, SchemaError

from internetarchive.cli.argparser import get_args_dict


def main(argv, session):
    args = docopt(__doc__, argv=argv)

    # Validate args.
    s = Schema({
        str: Use(bool),
        '--comment': str,
        '<identifier>': list,
    })

    # Filenames should be unicode literals. Support PY2 and PY3.
    if six.PY2:
        args['<file>'] = [f.decode('utf-8') for f in args['<file>']]

    try:
        args = s.validate(args)
    except SchemaError as exc:
        sys.stderr.write('{0}\n{1}\n'.format(
            str(exc), printable_usage(__doc__)))
        sys.exit(1)

    errors = False
    if args['<identifier>'] == ['-']:
        args['<identifier>'] = sys.stdin
    for identifier in args['<identifier>']:
        item = session.get_item(identifier)
        if not item.exists:
            print('warning: item does not exist - {}'.format(item.identifier),
                  file=sys.stderr)
        r = item.dark(args['--comment'])
        if r is None:
            print('warning: no task submitted, item already dark - {}'.format(item.identifier),
                  file=sys.stderr)
        elif r.status_code != 200:
            print('error: task failed, item not dark - {}'.format(item.identifier),
                  file=sys.stderr)
            errors = True
        else:
            print('success: item darked - {}'.format(item.identifier))

    if errors:
        print('\n*** Not all items were darked! ***\n')
        sys.exit(1)
