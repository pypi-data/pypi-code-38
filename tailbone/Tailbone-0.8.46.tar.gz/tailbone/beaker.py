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
Custom sessions, based on Beaker

Note that most of the code for this module was copied from the beaker and
pyramid_beaker projects.
"""

from __future__ import unicode_literals, absolute_import

import time

from beaker.session import Session
from beaker.util import coerce_session_params
from pyramid.settings import asbool
from pyramid_beaker import BeakerSessionFactoryConfig, set_cache_regions_from_settings


class TailboneSession(Session):
    """
    Custom session class for Beaker, which overrides load() to add per-request
    session timeout support.
    """

    def load(self):
        "Loads the data from this session from persistent storage"
        self.namespace = self.namespace_class(self.id,
            data_dir=self.data_dir,
            digest_filenames=False,
            **self.namespace_args)
        now = time.time()
        if self.use_cookies:
            self.request['set_cookie'] = True

        self.namespace.acquire_read_lock()
        timed_out = False
        try:
            self.clear()
            try:
                session_data = self.namespace['session']

                if (session_data is not None and self.encrypt_key):
                    session_data = self._decrypt_data(session_data)

                # Memcached always returns a key, its None when its not
                # present
                if session_data is None:
                    session_data = {
                        '_creation_time': now,
                        '_accessed_time': now
                    }
                    self.is_new = True
            except (KeyError, TypeError):
                session_data = {
                    '_creation_time': now,
                    '_accessed_time': now
                }
                self.is_new = True

            if session_data is None or len(session_data) == 0:
                session_data = {
                    '_creation_time': now,
                    '_accessed_time': now
                }
                self.is_new = True

            # TODO: sure would be nice if we could get this little bit of logic
            # into the upstream Beaker package, as that would avoid the need
            # for this module entirely...
            timeout = session_data.get('_timeout', self.timeout)
            if timeout is not None and \
               now - session_data['_accessed_time'] > timeout:
                timed_out = True
            else:
                # Properly set the last_accessed time, which is different
                # than the *currently* _accessed_time
                if self.is_new or '_accessed_time' not in session_data:
                    self.last_accessed = None
                else:
                    self.last_accessed = session_data['_accessed_time']

                # Update the current _accessed_time
                session_data['_accessed_time'] = now

                # Set the path if applicable
                if '_path' in session_data:
                    self._path = session_data['_path']
                self.update(session_data)
                self.accessed_dict = session_data.copy()
        finally:
            self.namespace.release_read_lock()
        if timed_out:
            self.invalidate()


def session_factory_from_settings(settings):
    """ Return a Pyramid session factory using Beaker session settings
    supplied from a Paste configuration file"""
    prefixes = ('session.', 'beaker.session.')
    options = {}

    # Pull out any config args meant for beaker session. if there are any
    for k, v in settings.items():
        for prefix in prefixes:
            if k.startswith(prefix):
                option_name = k[len(prefix):]
                if option_name == 'cookie_on_exception':
                    v = asbool(v)
                options[option_name] = v

    options = coerce_session_params(options)
    options['session_class'] = TailboneSession
    return BeakerSessionFactoryConfig(**options)


def includeme(config):
    session_factory = session_factory_from_settings(config.registry.settings)
    config.set_session_factory(session_factory)
    set_cache_regions_from_settings(config.registry.settings)
