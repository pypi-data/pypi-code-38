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

from distutils.spawn import find_executable
import gnupg

from harpo.domains import *
from harpo.groups import *
from harpo.users import *


class Harpo(object):
    """harpo main class"""

    def __init__(self, base_path, gpg_home_sys):
        """
        :param base_path: path to the harpo home
        :param gpg_home_sys: path to user's GPG dir to import keys from
        """
        self.path = base_path
        self.access_dir = os.path.join(self.path, 'access')
        self.domains_dir = os.path.join(self.path, 'domains')

        # Select gpg executable, prefer gpg2
        gpgbinary = find_executable('gpg2') or find_executable('gpg')
        if gpgbinary is None:
            raise HarpoException("GPG binary not found.")

        self.gpg_home = os.path.join(self.path, 'keychain')
        self.gpg = gnupg.GPG(gnupghome=self.gpg_home)
        self.gpg_home_sys = gpg_home_sys
        self.gpg_sys = gnupg.GPG(gnupghome=self.gpg_home_sys, use_agent=True, gpgbinary=gpgbinary)

        self.domains = DomainManager(self.path)
        self.users = UserManager(self.path, self.gpg, self.gpg_sys)
        self.groups = GroupManager(self.path)

        self.must_be_reencrypted = False

    def is_initialized(self):
        """
        Check if harpo is initialized
        :return: bool
        """
        return (os.path.exists(self.path) and
                os.path.exists(self.access_dir) and
                os.path.exists(self.domains_dir))

    def initialize(self):
        """
        Create harpo directory structure, system groups and domains
        :return: True on success, False on failure
        """
        if self.is_initialized():
            logging.warning("Already initialized at %s", self.path)
            return False

        logging.info("Initializing at %s", self.path)

        # make dirs
        dirs = [
            self.access_dir,
            self.domains_dir
        ]
        for directory in dirs:
            mkdir_p(directory)

        # bootstrap system domains and groups
        self.add_domain('all')
        self.add_group('all')
        self.add_group('adm')
        all_group = self.groups['all']
        self.domains['all'].allow_group(all_group)

        logging.info("OK")
        return True

    # Domains -------------------------------------------------------
    def add_domain(self, domain_name):
        """
        Create new domain with a given name
        :param domain_name: name of a domain to create
        :return: domain object
        """
        domain = self.domains.create(domain_name)
        return domain

    def remove_domain(self, domain_name):
        """
        Remove existing domain by name
        :param domain_name: name of a domain to remove
        :return: domain object
        """
        domain = self.domains.remove(domain_name)
        return domain

    def list_domains(self):
        """
        List existing domains' names.
        :return: list of domain names
        """
        return [d.name for d in self.domains]

    def show_domain(self, domain):
        """
        Show detailed information about domain.
        :param domain: domain object
        :return: dictionary with information
        """
        if not self.domains[domain].exists:
            raise HarpoException("Domain doesn't exist: {}".format(domain))
        return {
            "access": {
                "users": self.domains[domain].recipients['users'],
                "groups": self.domains[domain].recipients['groups'],
            }
        }

    # Users ---------------------------------------------------------
    def add_user(self, user_name, key_material=None):
        """
        Create new user
        :param user_name: name of a user
        :raises HarpoUserExists: when user already exists
        :return: user object
        """
        user = self.users.create(user_name, key_material)
        self.add_user_to_group(user_name, 'all')
        self.must_be_reencrypted = True
        return user

    def remove_user(self, user_name):
        """
        Remove existing user
        :param user_name: name of a user
        :raises HarpoUserDoesNotExist: when user doesn't exist
        :return:
        """
        user = self.users.remove(user_name)
        self.must_be_reencrypted = True
        return user

    def list_users(self):
        """
        List of user uids
        :return: list of strings, containing uids of existing users
        """
        return [d.uid for d in self.users]

    def show_user(self, user_name):
        """
        Show detailed information about user
        :param user_name: name of a user
        :raises HarpoUserDoesNotExist: when user doesn't exist
        :return: dict with user information
        """
        user = self.users[user_name]
        if user.exists:
            return {
                "key": user.key,
                "access": {
                    "groups": [g for g in self.groups if self.groups[g].has_user(user.uid)]
                }
            }
        else:
            raise HarpoUserDoesntExist(user_name)

    # Groups --------------------------------------------------------
    def add_group(self, group_name):
        """
        Create new group
        :param group_name: name of a group to create
        :raises HarpoGroupExists: when group already exists
        :return: group object
        """
        group = self.groups.create(group_name)
        return group

    def remove_group(self, group_name):
        """
        Remove existing group
        :param group_name: name of a group to remove
        :raises HarpoGroupDoesNotExist: when group doesn't exist
        :return: group object
        """
        group = self.groups.remove(group_name)
        self.must_be_reencrypted = True
        return group

    def list_groups(self):
        """
        List groups names
        :return: list of strings with groups names
        """
        return [group for group in self.groups]

    def add_user_to_group(self, user_name, group_name):
        """
        Add existing user to existing group
        :param user_name: name of a user
        :param group_name: name of a group
        :raises HarpoGroupDoesNotExist: when target group does not exist
        :raises HarpoUserDoesNotExist: when user doesn't exist
        :return: group object on success, None otherwise
        """
        user = self.users[user_name]
        if user.exists:
            group = self.groups[group_name]
            logging.info("Add user '%s' to group '%s'", user.uid, group_name)
            group.add_user(user.uid)
            self.groups.save()
            self.must_be_reencrypted = True
            return group
        else:
            raise HarpoUserDoesntExist("User doesn't exist: {}".format(user_name))

    def remove_user_from_group(self, user_name, group_name):
        """
        Remove existing user from existing group
        :param user_name: name of a user
        :param group_name: name of a group
        :raises HarpoGroupDoesNotExist: when target group does not exist
        :return: group object on success, None otherwise
        """
        user = self.users[user_name]
        if user.exists:
            group = self.groups[group_name]
            logging.info("Remove user '%s' from group '%s'", user.uid, group_name)
            group.remove_user(user.uid)
            self.groups.save()
            self.must_be_reencrypted = True
            return group

    def show_group(self, group_name):
        """
        Show detailed information about a group
        :param group_name: name of a group
        :return: dict with info
        """
        return self.groups[group_name].data

    # Crypto --------------------------------------------------------
    def get_key_by_uids(self, term):
        """
        Find gpg key by term.
        :param term: search term; a string
        :return: list of keys
        """
        return self.gpg.list_keys(keys=term)

    def encrypt(self, domain, key, value):
        """
        Encrypt given string with a key of each user in a given domain + with admins' keys
        :param domain: domain name
        :param key: secret name
        :param value: secret value
        :raises HarpoException: on error
        :return: path to encrypted secret on success
        """
        recipients = []
        recipients_users = self.domains[domain].recipients['users']
        recipients += recipients_users
        recipients_groups = self.domains[domain].recipients['groups']
        for group in recipients_groups:
            recipients += self.groups[group].data['users']

        recipients = list_uniq(recipients)
        recipients_fps = [self.users[u].fingerprint for u in recipients]
        logging.debug("Encrypt %s/%s. Recipients: %s", domain, key, recipients_fps)

        if len(recipients) == 0:
            raise HarpoException("No valid recipients (users) found for domain '{}'".format(domain))

        encrypted_ascii_data = self.gpg.encrypt(value, recipients, always_trust=True)
        if encrypted_ascii_data.ok:
            logging.debug("Successfully encrypted %s. Writing...", key)
        else:
            raise HarpoException("Error encrypting {}/{}".format(domain, key))

        secret_file_path = self.domains[domain].store_encrypted_data(key, encrypted_ascii_data)
        logging.debug("Done.")
        return secret_file_path

    def decrypt(self, domain, key):
        """
        Decrypt specified secret in a given domain
        :param domain: domain name
        :param key: secret name
        :raises HarpoException: on error
        :return: decrypted secret
        """
        logging.debug("Decrypt %s/%s", domain, key)
        encrypted_ascii_data = self.domains[domain].read_encrypted_data(key)
        result = self.gpg_sys.decrypt(encrypted_ascii_data)
        if result.ok:
            return str(result)
        else:
            raise HarpoException("Decryption failed for {}/{}:\n{}".format(domain, key, result.stderr))

    def reencrypt(self, domain):
        """
        Reencrypt all secrets in a given domain
        :param domain: domain name
        :raises HarpoException: on error
        :return: None
        """
        for key in self.domains[domain].secrets:
            logging.debug("Reencrypt %s/%s", domain, key)
            value = self.decrypt(domain, key)
            self.encrypt(domain, key, value)

    def reencrypt_all(self):
        """
        Reencrypt all secrets in harpo
        :raises HarpoException: on error
        :return: None
        """
        logging.info("Reencrypting everything!")
        for domain in self.list_domains():
            try:
                self.reencrypt(domain)
            except HarpoException as e:
                logging.warning("%s, skipping...", e)

    def remove_secret(self, domain, key):
        """
        Remove specified secret in a given domain
        :param domain: domain name
        :param key: secret name
        :raises HarpoException: on error
        :return: removed secret path
        """
        return self.domains[domain].remove_encrypted_data(key)
