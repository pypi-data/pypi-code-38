# Copyright 2019 Red Hat
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from __future__ import absolute_import

from keystoneauth1 import loading
from keystoneauth1 import session as _session
from oslo_log import log

import tobiko
from tobiko.openstack.keystone import _credentials


LOG = log.getLogger(__name__)


class KeystoneSessionFixture(tobiko.SharedFixture):

    session = None
    credentials = None
    credentials_fixture = None

    def __init__(self, credentials=None):
        super(KeystoneSessionFixture, self).__init__()
        if credentials:
            if tobiko.is_fixture(credentials):
                self.credentials_fixture = credentials
            else:
                self.credentials = credentials

    def setup_fixture(self):
        self.setup_credentials()
        self.setup_session(credentials=self.credentials)

    def setup_credentials(self):
        credentials_fixture = self.credentials_fixture
        if credentials_fixture:
            self.credentials = tobiko.setup_fixture(
                credentials_fixture).credentials
        elif not self.credentials:
            self.credentials = _credentials.default_keystone_credentials()

    def setup_session(self, credentials):
        LOG.debug("Create session for credentials %r", credentials)
        loader = loading.get_plugin_loader('password')
        params = credentials.to_dict()
        del params['api_version']  # parameter not required
        auth = loader.load_from_options(**params)
        self.session = _session.Session(auth=auth, verify=False)


class KeystoneSessionManager(object):

    def __init__(self):
        self._sessions = {}

    def get_session(self, credentials=None, shared=True, init_session=None):
        if shared:
            key = credentials
            if credentials:
                if tobiko.is_fixture(credentials):
                    key = tobiko.get_fixture_name(credentials)

            session = self._sessions.get(key)
            if session:
                return session

        init_session = init_session or KeystoneSessionFixture
        assert callable(init_session)
        LOG.debug('Initialize Keystone session: %r(credentials=%r)',
                  init_session, credentials)
        session = init_session(credentials=credentials)

        if shared:
            self._sessions[key] = session
        return session


SESSIONS = KeystoneSessionManager()


def get_keystone_session(credentials=None, shared=True, init_session=None,
                         manager=None):
    manager = manager or SESSIONS
    session = manager.get_session(credentials=credentials, shared=shared,
                                  init_session=init_session)
    session.setUp()
    return session.session
