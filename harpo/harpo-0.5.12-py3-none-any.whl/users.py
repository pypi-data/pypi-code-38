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

import logging
import os

from harpo.util import HarpoException


class HarpoUserExists(HarpoException):
    pass


class HarpoUserDoesntExist(HarpoException):
    pass


class UserManager(object):
    def __init__(self, base_dir, gpg, gpg_sys):
        self.base_dir = base_dir
        self.gpg = gpg
        self.gpg_sys = gpg_sys
        self.users_file = os.path.join(self.base_dir, 'access/users')

    def __getitem__(self, uid):
        return User(uid, self.gpg, self.gpg_sys)

    def __iter__(self):
        for key in self.gpg.list_keys():
            yield User(key['fingerprint'], self.gpg, self.gpg_sys)

    def create(self, uid, key_material=None):
        if key_material is not None:
            self.gpg.import_keys(key_material)

        user = self[uid]
        if user.exists:
            raise HarpoUserExists("User already exists: {}".format(user.uid))

        logging.info("Importing key %s - %s", user.fingerprint, user.uid)
        if key_material is None:
            key_data = self.gpg_sys.export_keys(user.fingerprint)
        else:
            key_data = key_material
        self.gpg.import_keys(key_data)
        return user

    def remove(self, uid):
        user = self[uid]
        if not user.exists:
            raise HarpoUserDoesntExist("User doesn't exist: {}".format(user.uid))

        logging.info("Removing key %s - %s", user.fingerprint, user.uid)
        self.gpg.delete_keys(user.fingerprint)
        return user

    def exists(self, uid):
        return self[uid].exists


class User(object):
    def __init__(self, uid, gpg, gpg_sys):
        self.uid = uid
        self.gpg = gpg
        self.gpg_sys = gpg_sys

        # Firstly check 'system' gpg keyring
        self.key = self.gpg_sys.list_keys(keys=uid)
        # Failing that, try searching in harpo keyring
        if len(self.key) < 1:
            self.key = self.gpg.list_keys(keys=uid)

        if len(self.key) < 1:
            raise HarpoException("No keys found for '{}'.".format(uid))
        elif len(self.key) > 1:
            raise HarpoException("More than one key was found for '{}'.".format(uid))
        else:
            self.key = self.key[0]
            # Correct uid to the full one
            self.uid = self.key['uids'][0]

    @property
    def exists(self):
        keys = self.gpg.list_keys(keys=self.uid)
        return len(keys) > 0

    @property
    def fingerprint(self):
        return self.key['fingerprint']
