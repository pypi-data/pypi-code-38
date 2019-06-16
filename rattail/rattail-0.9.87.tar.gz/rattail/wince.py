# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2019 Lance Edgar
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
Windows CE App Interface
"""

from __future__ import unicode_literals, absolute_import

import os
import os.path

from rattail import files
from rattail.csvutil import DictWriter
from rattail.core import Object
from rattail.util import progress_loop


def collect_batch(path, queue, device='Default'):
    """
    This function is meant to be invoked by the file monitor.  Its purpose is
    to gather handheld scan batch files from arbitrary device-specific folders,
    and move them to yet another ("upstream") folder so that they may be part
    of a single processing queue.  Rather than moving the file as-is, the
    following processing is done on the file:

    Since the Rattail CE app saves the batch contents using a somewhat "binary"
    format, the raw file is parsed (with :func:`parse_batch_file()`) and a
    proper CSV file is written with the "translated" contents.  This file is
    then copied to the collection folder.

    The filename used for the final destination path is also manipulated.
    Instead of using the original filename, one is generated which contains the
    original filename, plus the "device name" and the timestamp of the original
    file.  The ``device`` parameter is used to determine the device name.
    """

    ctime = files.creation_time(path)
    final_path = os.path.join(queue, '%s,%s,%s.csv' % (
            device,
            ctime.strftime('%Y-%m-%d %H-%M-%S'),
            os.path.basename(path)))

    csv_path = files.temp_path(suffix='.csv')
    csv_file = open(csv_path, 'wb')
    writer = DictWriter(csv_file, ['upc', 'cases', 'units'])
    writer.writeheader()
    for upc, cases, units in parse_batch_file(path):
        writer.writerow({
                'upc': upc,
                'cases': cases,
                'units': units,
                })
    csv_file.close()

    # TODO: Ugh, this locking copy situation is getting out of hand..FIXME.
    files.locking_copy_old(csv_path, final_path)


def parse_batch_file(path, progress=None):
    """
    Generator which parses a scan batch file originating from the Rattail CE
    application.

    When a valid record is encountered, it is returned as a tuple of the form
    ``(scancode, cases, units)``.
    """
    current = Object(scancode=None,
                     cases=None,
                     units=None)
    results = []

    def parse(line, i):
        line = line.decode('ascii')
        line = line.replace('\x00', '')
        line = line.rstrip('\n')
        
        if current.scancode is None:
            current.scancode = line

        elif current.cases is None:
            line = line.strip()
            if line and line.isdigit():
                current.cases = int(line)
            else:
                current.cases = 0

        elif current.units is None:
            line = line.strip()
            if line and line.isdigit():
                current.units = int(line)
            else:
                current.units = 0

            results.append((current.scancode, current.cases, current.units))
            current.scancode = None
            current.cases = None
            current.units = None

    with open(path, 'rb') as f:
        lines = list(f)

    progress_loop(parse, lines, progress,
                  message="Parsing scan batch file")
    return results
