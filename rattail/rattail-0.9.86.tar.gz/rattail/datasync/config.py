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
DataSync Configuration
"""

from __future__ import unicode_literals, absolute_import

from rattail.config import ConfigProfile, parse_list
from rattail.util import load_object
from rattail.exceptions import ConfigurationError

from rattail.datasync.watchers import NullWatcher


class DataSyncProfile(ConfigProfile):
    """
    Simple class to hold configuration for a DataSync "profile".  Each profile
    determines which database(s) will be watched for new changes, and which
    consumer(s) will then be instructed to process the changes.

    .. todo::
       This clearly needs more documentation.
    """
    section = 'rattail.datasync'

    def __init__(self, config, key):
        self.config = config
        self.key = key

        self.watcher_spec = self._config_string('watcher')
        if self.watcher_spec == 'null':
            self.watcher = NullWatcher(config, key)
        else:
            dbkey = self._config_string('watcher.db', default='default')
            self.watcher = load_object(self.watcher_spec)(config, key, dbkey=dbkey)
        self.watcher.delay = self._config_int('watcher.delay', default=self.watcher.delay)
        self.watcher.retry_attempts = self._config_int('watcher.retry_attempts', default=self.watcher.retry_attempts)
        self.watcher.retry_delay = self._config_int('watcher.retry_delay', default=self.watcher.retry_delay)

        consumers = self._config_list('consumers')
        if consumers == ['self']:
            self.watcher.consumes_self = True
        else:
            self.watcher.consumes_self = False
            self.consumer_delay = self._config_int('consumer_delay', default=1)
            self.consumers = self.normalize_consumers(consumers)
            self.watcher.consumer_stub_keys = [c.key for c in self.consumers]

    def normalize_consumers(self, raw_consumers):
        # TODO: This will do for now, but isn't as awesome as it probably could be.
        default_runas = self._config_string('consumers.runas')
        consumers = []
        for key in raw_consumers:
            consumer_spec = self._config_string('consumer.{}'.format(key))
            if consumer_spec == 'null':
                consumer_spec = 'rattail.datasync.consumers:NullTestConsumer'
            dbkey = self._config_string('consumer.{}.db'.format(key), default=key)
            runas = self._config_string('consumer.{}.runas'.format(key))
            consumer = load_object(consumer_spec)(self.config, key, dbkey=dbkey,
                                                  runas=runas or default_runas,
                                                  watcher=self.watcher)
            consumer.spec = consumer_spec
            consumer.delay = self._config_int(
                'consumer.{}.delay'.format(key),
                default=self.consumer_delay)
            consumer.retry_attempts = self._config_int(
                'consumer.{}.retry_attempts'.format(key),
                default=consumer.retry_attempts)
            consumer.retry_delay = self._config_int(
                'consumer.{}.retry_delay'.format(key),
                default=consumer.retry_delay)
            consumers.append(consumer)
        return consumers


def get_profile_keys(config):
    """
    Returns a list of profile keys used in the DataSync configuration.
    """
    keys = config.get('rattail.datasync', 'watch')
    if keys:
        return parse_list(keys)


def load_profiles(config):
    """
    Load all active DataSync profiles defined within configuration.
    """
    # Make sure we have a top-level directive.
    keys = get_profile_keys(config)
    if not keys:
        raise ConfigurationError(
            "The DataSync configuration does not specify any profiles "
            "to be watched.  Please defined the 'watch' option within "
            "the [rattail.datasync] section of your config file.")

    watched = {}
    for key in keys:
        profile = DataSyncProfile(config, key)
        watched[key] = profile
    return watched
