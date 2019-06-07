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

import abc

from oslo_log import log

import tobiko
from tobiko.openstack import keystone


LOG = log.getLogger(__name__)


class OpenstackClientFixture(tobiko.SharedFixture):

    client = None
    session = None
    session_fixture = None

    def __init__(self, session=None):
        super(OpenstackClientFixture, self).__init__()
        if session:
            if tobiko.is_fixture(session):
                self.session_fixture = session
            else:
                self.session = session

    def setup_fixture(self):
        self.setup_session()
        self.setup_client()

    def setup_session(self):
        session_fixture = self.session_fixture
        if session_fixture:
            self.session = tobiko.setup_fixture(session_fixture).session
        elif not self.session:
            self.session = keystone.get_keystone_session()

    def setup_client(self):
        self.client = self.init_client(session=self.session)

    @abc.abstractmethod
    def init_client(self, session):
        raise NotImplementedError


class OpenstackClientManager(object):

    def __init__(self, init_client=None):
        self._clients = {}
        self.init_client = init_client

    def get_client(self, session=None, shared=True, init_client=None):
        if shared:
            if session and tobiko.is_fixture(session):
                key = tobiko.get_fixture_name(session)
            else:
                key = session

            client = self._clients.get(key)
            if client:
                return client

        session = session or keystone.get_keystone_session()
        init_client = init_client or self.init_client
        assert callable(init_client)
        LOG.debug('Initialize OpenStack client: %r(session=%r)',
                  init_client, session)
        client = init_client(session=session)

        if shared:
            self._clients[key] = client
        return client
