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
Luigi utilities
"""

from __future__ import unicode_literals, absolute_import

import os
import datetime
import subprocess
import sys

import luigi


class OvernightTask(luigi.Task):
    """
    Base class for overnight automation tasks.
    """
    date = luigi.DateParameter()

    # TODO: subclass must define this
    filename = None

    # how long should we wait after task completes, for datasync to catch up?
    datasync_wait_minutes = None

    def output(self):
        return luigi.LocalTarget('{}/{}'.format(self.date.strftime('%Y/%m/%d'), self.filename))

    def run_command(self):
        raise NotImplementedError

    def touch_output(self):
        with self.output().open('w') as f:
            pass

    def datasync_wait(self, minutes=None):
        if minutes is None:
            minutes = self.datasync_wait_minutes or 10
        subprocess.check_call([
            'bin/rattail',
            '--config=app/cron.conf',
            'datasync',
            '--timeout={}'.format(minutes),
            'wait',
        ])

    def run(self):
        workdir = os.getcwd()
        os.chdir(sys.prefix)
        self.date_plus = self.date + datetime.timedelta(days=1)
        self.run_command()
        if self.datasync_wait_minutes:
            self.datasync_wait()
        os.chdir(workdir)
        self.touch_output()
