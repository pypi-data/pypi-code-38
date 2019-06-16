# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
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
Email Bouncer Configuration
"""

from __future__ import unicode_literals

from rattail.config import parse_list
from rattail.util import load_object
from rattail.exceptions import ConfigurationError


class Profile(object):
    """
    Simple class to hold configuration for an email bouncer "profile".  Each
    profile determines how to connect to an IMAP folder, which handler to
    invoke when new messages appear, etc.  Each instance of this class has the
    following attributes:

    .. attribute:: config

       Reference to the underlying configuration object from which the profile
       derives its other attributes.

    .. attribute:: key

       String which differentiates this profile from any others which may exist
       within the configuration.

    .. attribute:: imap_server

       Hostname or IP address of the IMAP server to which to connect.

    .. attribute:: imap_username

       Username to use when logging into the IMAP server.

    .. attribute:: imap_password

       Password to use when logging into the IMAP server.

    .. attribute:: imap_folder

       Folder to select when checking the IMAP server for new messages.

    .. attribute:: handler_spec

       Spec string for the handler.  This must be a subclass of
       :class:`rattail.bouncer:BounceHandler`.

    .. attribute:: handler

       Reference to the handler instance.  This will be a subclass of
       :class:`rattail.bouncer:BounceHandler`.
    """

    def __init__(self, config, key):
        self.config = config
        self.key = key

        self.imap_server = self._config_string('imap.server')
        self.imap_username = self._config_string('imap.username')
        self.imap_password = self._config_string('imap.password')
        self.imap_folder_inbox = self._config_string('imap.inbox')
        self.imap_folder_backup = self._config_string('imap.backup')
        self.imap_delay = self._config_int('imap.delay', default=120)
        self.imap_recycle = self._config_int('imap.recycle', default=1200)

        self.workdir = self._config_string('workdir')

        self.handler_spec = self._config_string('handler') or 'rattail.bouncer:BounceHandler'
        self.handler = load_object(self.handler_spec)(config, key)

    def _config_string(self, option):
        return self.config.get('rattail.bouncer', '{0}.{1}'.format(self.key, option))

    def _config_int(self, option, minimum=1, default=None):
        option = '{0}.{1}'.format(self.key, option)
        if self.config.has_option('rattail.bouncer', option):
            value = self.config.getint('rattail.bouncer', option)
            if value < minimum:
                log.warning("config value {0} is too small; falling back to minimum "
                            "of {1} for option: {2}".format(value, minimum, option))
                value = minimum
        elif default is not None and default >= minimum:
            value = default
        else:
            value = minimum
        return value


def get_profile_keys(config):
    """
    Returns a list of keys used in the bouncer configuration.
    """
    keys = config.get('rattail.bouncer', 'watch')
    if keys:
        return parse_list(keys)


def load_profiles(config):
    """
    Load all active email bouncer profiles defined within configuration.
    """
    # Make sure we have a top-level directive.
    keys = get_profile_keys(config)
    if not keys:
        raise ConfigurationError(
            "The bouncer configuration does not specify any IMAP profiles to "
            "be watched.  Please defined the 'watch' option within the "
            "[rattail.bouncer] section of your config file.")

    watched = {}
    for key in keys:
        profile = Profile(config, key)
        watched[key] = profile
    return watched
