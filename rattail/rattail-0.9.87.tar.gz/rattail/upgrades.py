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
Upgrade handlers
"""

from __future__ import unicode_literals, absolute_import

import os
import shutil
import subprocess

from rattail.time import make_utc
from rattail.util import load_object
from rattail.mail import send_email


class UpgradeHandler(object):
    """
    Base class and default implementation for upgrade handlers.
    """

    def __init__(self, config):
        self.config = config
        self.enum = config.get_enum()

    def executable(self, upgrade):
        """
        This method should return a boolean indicating whether or not execution
        should be allowed for the upgrade, given its current condition.  The
        default simply returns ``True`` unless the upgrade has already been
        executed.
        """
        if upgrade is None:
            return True
        return not bool(upgrade.executed)

    def mark_executing(self, upgrade):
        upgrade.executing = True
        upgrade.status_code = self.enum.UPGRADE_STATUS_EXECUTING

    def do_execute(self, upgrade, user, **kwargs):
        success = self.execute(upgrade, user, **kwargs)
        upgrade.executing = False
        if success:
            upgrade.status_code = self.enum.UPGRADE_STATUS_SUCCEEDED
            email_key = 'upgrade_success'
        else:
            upgrade.status_code = self.enum.UPGRADE_STATUS_FAILED
            email_key = 'upgrade_failure'
        upgrade.executed = make_utc()
        upgrade.executed_by = user
        url = self.config.get('tailbone', 'url.upgrade', default='#')
        send_email(self.config, email_key, {
            'upgrade': upgrade,
            'upgrade_url': url.format(uuid=upgrade.uuid),
        })

    def execute(self, upgrade, user, progress=None, **kwargs):
        """
        Execute the given upgrade, as the given user.
        """
        before_path = self.config.upgrade_filepath(upgrade.uuid, filename='requirements.before.txt', makedirs=True)
        self.record_requirements_snapshot(before_path)

        stdout_path = self.config.upgrade_filepath(upgrade.uuid, filename='stdout.log')
        stderr_path = self.config.upgrade_filepath(upgrade.uuid, filename='stderr.log')
        cmd = self.config.upgrade_command()
        with open(stdout_path, 'wb') as stdout:
            with open(stderr_path, 'wb') as stderr:
                upgrade.exit_code = subprocess.call(cmd, stdout=stdout, stderr=stderr)

        after_path = self.config.upgrade_filepath(upgrade.uuid, filename='requirements.after.txt')
        self.record_requirements_snapshot(after_path)
        return upgrade.exit_code == 0

    def record_requirements_snapshot(self, path):
        pip = self.get_pip_path()
        logpath = os.path.join(self.config.workdir(), 'pip.log')

        kwargs = {}
        suppress_stderr = self.config.getbool('rattail.upgrades', 'suppress_pip_freeze_stderr',
                                              default=False, usedb=False)
        if suppress_stderr:
            stderr = open('/dev/null', 'w')
            kwargs['stderr'] = stderr

        with open(path, 'wb') as stdout:
            subprocess.call([pip, '--log', logpath, 'freeze'], stdout=stdout, **kwargs)

        if suppress_stderr:
            stderr.close()

    def get_pip_path(self):
        path = os.path.join(self.config.appdir(), os.pardir, 'bin', 'pip')
        return os.path.abspath(path)

    def delete_files(self, upgrade):
        """
        Delete all data files for the given upgrade.
        """
        path = self.config.upgrade_filepath(upgrade.uuid)
        if os.path.exists(path):
            shutil.rmtree(path)


def get_upgrade_handler(config, default=None):
    """
    Returns an upgrade handler object.
    """
    spec = config.get('rattail.upgrades', 'handler', default=default)
    if spec:
        handler = load_object(spec)(config)
    else:
        handler = UpgradeHandler(config)
    return handler
