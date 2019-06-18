# Copyright 2016 Commerce Technologies, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
import pexpect
import subprocess

from requests_kerberos import HTTPKerberosAuth, OPTIONAL
from requests_ntlm import HttpNtlmAuth
from pexpect import popen_spawn


class Authenticator(object):
    """
    The Authenticator class is an abstract class for shared functionality
    between the possible authentication types.
    """

    def get_auth_handler(self, session):
        raise NotImplementedError("override this method")

    @staticmethod
    def get_auth_type():
        raise NotImplementedError("override this method")


class KerberosAuthenticator(Authenticator):
    """
    The KerberosAuthenticator uses the local Kerberos install to
    authenticate a user who's machine is logged into to the Domain.
    """
    AUTH_TYPE = 'kerberos'

    def __init__(self, kerb_hostname=None, username=None, password=None, domain=None):
        self.kerb_hostname = kerb_hostname if kerb_hostname else None

        if username:
            KerberosAuthenticator.__generate_kerberos_ticket(username, password, domain)
        else:
            KerberosAuthenticator.__generate_kerberos_ticket_using_credentials_cache()

    @staticmethod
    def __generate_kerberos_ticket(username, password, domain):
        # Assume Windows users have a valid Kerberos ticket.
        if os.name != 'nt':
            try:
                principal = '{}@{}'.format(username, domain)
                kinit = pexpect.spawn('kinit {}'.format(principal))
                kinit.sendline(password)
                kinit.expect(pexpect.EOF)
                kinit.close()
                if kinit.exitstatus is not 0:
                    raise Exception('kinit failed for principal {}'.format(principal))
            except Exception as ex:
                raise ex

    @staticmethod
    def __generate_kerberos_ticket_using_credentials_cache():
        # Windows does not have support for `klist`. Assume
        # Windows users have a valid Kerberos ticket.
        if os.name != 'nt':
            try:
                subprocess.check_output(['klist', '-s'])
            except subprocess.CalledProcessError:
                logging.info('no kerberos ticket found. running kinit')
                try:
                    subprocess.check_output(['kinit'])
                except subprocess.CalledProcessError as err:
                    logging.error('failed to generate a kerberos ticket')
                    raise err

    def get_auth_handler(self, session):
        return HTTPKerberosAuth(mutual_authentication=OPTIONAL, hostname_override=self.kerb_hostname)

    @staticmethod
    def get_auth_type():
        return KerberosAuthenticator.AUTH_TYPE


class NtlmAuthenticator(Authenticator):
    """
    The NtlmAuthenticator authenticates users with basic credentials
    and a domain.
    """
    AUTH_TYPE = 'ntlm'

    def __init__(self, username, password, domain):
        self.username = username
        self.password = password
        self.domain = domain

    def get_auth_handler(self, session):
        return HttpNtlmAuth(
            "{}\\{}".format(self.domain, self.username),
            self.password,
            session
        )

    @staticmethod
    def get_auth_type():
        return NtlmAuthenticator.AUTH_TYPE


class KeytabAuthenticator(Authenticator):
    """
    The KeytabAuthenticator allows users to sign keytabs with
    their password and then request valid Kerberos tickets
    with those keytabs without requiring password input.
    """

    def __init__(self, kerb_hostname, username, keytab, domain):
        self.kerb_hostname = kerb_hostname
        self.username = username
        self.keytab = keytab
        self.domain = domain

        if os.name == 'nt':
            raise Exception("keytab is not supported on Windows!")

        # Setup a temporary credentials cache
        credentials_cache = os.path.join(os.getcwd(), 'credentials_cache')
        os.environ['KRB5CCNAME'] = credentials_cache

        # Call kinit to generate a Kerberos ticket for the given username and keytab
        try:
            subprocess.check_output(['kinit', '-c', credentials_cache, '-kt', self.keytab,
                                     "{}@{}".format(self.username, self.domain)])
        except subprocess.CalledProcessError:
            raise Exception("could not generate a valid ticket for the given keytab")

    def get_auth_handler(self, session):
        return HTTPKerberosAuth(mutual_authentication=OPTIONAL, hostname_override=self.kerb_hostname)

    @staticmethod
    def get_auth_type():
        return 'keytab'

