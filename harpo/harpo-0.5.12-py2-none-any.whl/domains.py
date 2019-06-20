# Copyright 2018 Behavox Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging
import os
import shutil

from harpo.util import HarpoException
from harpo.util import list_uniq
from harpo.util import mkdir_p


class HarpoDomainExists(HarpoException):
    pass


class HarpoDomainDoesntExist(HarpoException):
    pass


class DomainManager(object):
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.domains_dir = os.path.join(self.base_dir, 'domains')
        self.domains = {}
        self._load_domains()

    def _load_domains(self):
        try:
            self.domains = {f: Domain(self.domains_dir, f) for f in os.listdir(self.domains_dir)
                            if os.path.isdir(os.path.join(self.domains_dir, f))}
        except OSError:
            self.domains = {}
        return self.domains

    def __getitem__(self, domain_name):
        try:
            return self.domains[domain_name]
        except KeyError:
            return Domain(self.domains_dir, domain_name)

    def __iter__(self):
        for domain in self.domains.items():
            yield domain[1]

    def create(self, domain_name):
        """
        Create new domain directory with a given name
        :param domain_name: domain name
        :return: path
        :raises: HarpoDomainExists when already exists
        """
        if self.exists(domain_name):
            raise HarpoDomainExists("Domain already exists: {}".format(domain_name))

        logging.info("Add domain: {}".format(domain_name))
        directory = os.path.join(self.domains_dir, domain_name)
        logging.debug('Create: %s', directory)
        secrets_directory = os.path.join(directory, 'secrets')
        mkdir_p(secrets_directory)
        self._load_domains()
        return self[domain_name]

    def remove(self, domain_name):
        """
        Remove existing domain by name
        :param domain_name: domain name
        :return: path
        :raises: HarpoException when doesn't exist
        """
        if not self.exists(domain_name):
            raise HarpoDomainDoesntExist("Domain doesn't exist: {}".format(domain_name))

        logging.info("Remove domain: %s", domain_name)
        directory = os.path.join(self.domains_dir, domain_name)
        logging.debug('Remove: %s', directory)
        shutil.rmtree(directory)
        return self[domain_name]

    def exists(self, domain_name):
        return self[domain_name].exists


class Domain(object):
    def __init__(self, base_domains_path, name):
        self.name = name
        self.path = os.path.join(base_domains_path, name)
        self.secrets_dir = os.path.join(self.path, 'secrets')
        self.recipients = {'groups': ['adm'], 'users': []}
        self.recipients_file = os.path.join(self.path, 'recipients')
        if self.exists:
            self.load_recipients()

    @property
    def exists(self):
        return os.path.exists(self.path) and os.path.exists(self.secrets_dir)

    def load_recipients(self):
        try:
            if not os.path.exists(self.recipients_file):
                self.save_recipients()
            with open(self.recipients_file, 'r') as stream:
                recipients_content = stream.read()
                self.recipients = json.loads(recipients_content)
        except (json.JSONDecodeError, OSError) as e:
            raise HarpoException(e)
        return self.recipients

    def save_recipients(self):
        try:
            with open(self.recipients_file, 'w+') as stream:
                stream.write(json.dumps(self.recipients, sort_keys=True, indent=2))
        except OSError as e:
            raise HarpoException(e)

    def allow_user(self, recipient):
        self.recipients['users'].append(recipient.uid)
        self.recipients['users'] = list_uniq(self.recipients['users'])
        self.save_recipients()
        return self.recipients

    def allow_group(self, recipient):
        self.recipients['groups'].append(recipient.gid)
        self.recipients['groups'] = list_uniq(self.recipients['groups'])
        self.save_recipients()
        return self.recipients

    def deny_user(self, recipient):
        try:
            self.recipients['users'].remove(recipient)
        except ValueError:
            raise HarpoException("No user {} in domain {}".format(recipient, self.name))
        self.recipients['users'] = list_uniq(self.recipients['users'])
        self.save_recipients()
        return self.recipients

    def deny_group(self, recipient):
        try:
            self.recipients['groups'].remove(recipient)
        except ValueError:
            raise HarpoException("No group {} in domain {}".format(recipient, self.name))
        self.recipients['groups'] = list_uniq(self.recipients['groups'])
        self.save_recipients()
        return self.recipients

    @property
    def secrets(self):
        try:
            keys = [f for f in os.listdir(self.secrets_dir) if os.path.isfile(os.path.join(self.secrets_dir, f))]
        except OSError:
            keys = []
        return keys

    def read_encrypted_data(self, key):
        secret_file_path = os.path.join(self.secrets_dir, key)
        try:
            with open(secret_file_path, "r") as secret_file:
                encrypted_ascii_data = secret_file.read()
        except OSError as e:
            raise HarpoException("Unable to read {}/{}: {}".format(self.name, key, e))
        return encrypted_ascii_data

    def remove_encrypted_data(self, key):
        secret_file_path = os.path.join(self.secrets_dir, key)
        logging.debug("Remove %s/%s at %s", self.name, key, secret_file_path)
        try:
            os.remove(secret_file_path)
        except OSError as e:
            raise HarpoException("Unable to remove {}/{}: {}".format(self.name, key, e))
        return secret_file_path

    def store_encrypted_data(self, key, encrypted_ascii_data):
        secret_file_path = os.path.join(self.secrets_dir, key)
        try:
            with open(secret_file_path, "w") as secret_file:
                secret_file.write(str(encrypted_ascii_data))
        except OSError as e:
            raise HarpoException("Unable to write {}/{}: {}".format(self.name, key, e))
        return secret_file_path
