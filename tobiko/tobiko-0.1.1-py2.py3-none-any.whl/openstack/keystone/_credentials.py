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

import collections

from oslo_log import log

import tobiko


LOG = log.getLogger(__name__)


def default_keystone_credentials():
    return tobiko.setup_fixture(DefaultKeystoneCredentialsFixture).credentials


class KeystoneCredentials(collections.namedtuple(
        'KeystoneCredentials', ['api_version',
                                'auth_url',
                                'username',
                                'password',
                                'project_name',
                                'domain_name',
                                'user_domain_name',
                                'project_domain_name',
                                'project_domain_id',
                                'trust_id'])):

    def to_dict(self):
        return collections.OrderedDict(
            (k, v)
            for k, v in self._asdict().items()
            if v is not None)

    def __repr__(self):
        params = self.to_dict()
        if 'password' in params:
            params['password'] = '***'
        return 'keystone_credentials({!s})'.format(
            ", ".join("{!s}={!r}".format(k, v)
                      for k, v in params.items()))

    required_params = ('auth_url', 'username', 'password', 'project_name')

    def validate(self, required_params=None):
        required_params = required_params or self.required_params
        missing_params = [p
                          for p in required_params
                          if not getattr(self, p)]
        if missing_params:
            reason = "undefined parameters: {!s}".format(
                ', '.join(missing_params))
            raise InvalidKeystoneCredentials(credentials=self, reason=reason)


def keystone_credentials(api_version=None,
                         auth_url=None,
                         username=None,
                         password=None,
                         project_name=None,
                         domain_name=None,
                         user_domain_name=None,
                         project_domain_name=None,
                         project_domain_id=None,
                         trust_id=None,
                         cls=KeystoneCredentials):
    return cls(api_version=api_version,
               auth_url=auth_url,
               username=username,
               password=password,
               project_name=project_name,
               domain_name=domain_name,
               user_domain_name=user_domain_name,
               project_domain_name=project_domain_name,
               project_domain_id=project_domain_id,
               trust_id=trust_id)


class InvalidKeystoneCredentials(tobiko.TobikoException):
    message = "invalid Keystone credentials; {reason!s}; {credentials!r}"


class EnvironKeystoneCredentialsFixture(tobiko.SharedFixture):

    credentials = None

    def setup_fixture(self):
        from tobiko import config
        auth_url = config.get_env('OS_AUTH_URL')
        if not auth_url:
            LOG.debug("OS_AUTH_URL environment variable not defined")
            return

        api_version = (
            config.get_int_env('OS_IDENTITY_API_VERSION') or
            api_version_from_url(auth_url))
        username = (
            config.get_env('OS_USERNAME') or
            config.get_env('OS_USER_ID'))
        password = config.get_env('OS_PASSWORD')
        project_name = (
            config.get_env('OS_PROJECT_NAME') or
            config.get_env('OS_TENANT_NAME') or
            config.get_env('OS_PROJECT_ID') or
            config.get_env('OS_TENANT_ID'))
        if api_version == 2:
            credentials = keystone_credentials(
                api_version=api_version,
                auth_url=auth_url,
                username=username,
                password=password,
                project_name=project_name)
        else:
            domain_name = (
                config.get_env('OS_DOMAIN_NAME') or
                config.get_env('OS_DOMAIN_ID'))
            user_domain_name = (
                config.get_env('OS_USER_DOMAIN_NAME') or
                config.get_env('OS_USER_DOMAIN_ID'))
            project_domain_name = (
                config.get_env('OS_PROJECT_DOMAIN_NAME'))
            project_domain_id = (
                config.get_env('OS_PROJECT_DOMAIN_ID'))
            trust_id = config.get_env('OS_TRUST_ID')
            credentials = keystone_credentials(
                api_version=api_version,
                auth_url=auth_url,
                username=username,
                password=password,
                project_name=project_name,
                domain_name=domain_name,
                user_domain_name=user_domain_name,
                project_domain_name=project_domain_name,
                project_domain_id=project_domain_id,
                trust_id=trust_id)
        try:
            credentials.validate()
        except InvalidKeystoneCredentials as ex:
            LOG.info("No such valid credentials from environment: %r", ex)
        else:
            self.credentials = credentials


class ConfigKeystoneCredentialsFixture(tobiko.SharedFixture):

    credentials = None

    def setup_fixture(self):
        from tobiko import config
        conf = config.CONF.tobiko.keystone
        auth_url = conf.auth_url
        if not auth_url:
            LOG.debug("auth_url option not defined in 'keystone' section of "
                      "tobiko.conf")
            return

        api_version = (conf.api_version or
                       api_version_from_url(auth_url))
        if api_version == 2:
            credentials = keystone_credentials(
                api_version=api_version,
                auth_url=auth_url,
                username=conf.username,
                password=conf.password,
                project_name=conf.project_name)
        else:
            credentials = keystone_credentials(
                api_version=api_version,
                auth_url=auth_url,
                username=conf.username,
                password=conf.password,
                project_name=conf.project_name,
                domain_name=conf.domain_name,
                user_domain_name=conf.user_domain_name,
                project_domain_name=conf.project_domain_name,
                project_domain_id=conf.project_domain_id,
                trust_id=conf.trust_id)
        try:
            credentials.validate()
        except InvalidKeystoneCredentials as ex:
            LOG.info("No such valid credentials from tobiko.conf: %r", ex)
        else:
            self.credentials = credentials


DEFAULT_KEYSTONE_CREDENTIALS_FIXTURES = [
    EnvironKeystoneCredentialsFixture,
    ConfigKeystoneCredentialsFixture]


class DefaultKeystoneCredentialsFixture(tobiko.SharedFixture):

    fixtures = DEFAULT_KEYSTONE_CREDENTIALS_FIXTURES
    credentials = None

    def setup_fixture(self):
        for fixture in self.fixtures:
            try:
                credentials = tobiko.setup_fixture(fixture).credentials
            except Exception:
                LOG.exception("Error setting up fixture %r", fixture)
            else:
                if credentials:
                    LOG.info("Got default credentials from %r: %r",
                             fixture, credentials)
                    self.credentials = credentials
                    return credentials
        raise RuntimeError('Unable to found any valid credentials')


def api_version_from_url(auth_url):
    if auth_url.endswith('/v2.0'):
        LOG.info('Got Keystone API version 2 from auth_url: %r', auth_url)
        return 2
    elif auth_url.endswith('/v3'):
        LOG.info('Got Keystone API version 3 from auth_url: %r', auth_url)
        return 3
    else:
        LOG.warning('Unable to get Keystone API version from auth_url:  %r',
                    auth_url)
        return None
