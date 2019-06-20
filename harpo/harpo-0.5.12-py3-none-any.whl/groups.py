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

from harpo.util import HarpoException
from harpo.util import list_uniq
from harpo.util import mkdir_p


class HarpoGroupExists(HarpoException):
    pass


class HarpoGroupDoesntExist(HarpoException):
    pass


class GroupManager(object):
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.access_dir = os.path.join(self.base_dir, 'access')
        self.groups_file = os.path.join(self.access_dir, 'groups')
        mkdir_p(self.access_dir)
        self.groups = {}
        self.load()

    def load(self):
        if os.path.exists(self.groups_file):
            with open(self.groups_file, 'r') as stream:
                try:
                    groups_data = json.loads(stream.read())
                    for group in groups_data.keys():
                        self.groups[group] = Group(group, groups_data[group])
                except (json.JSONDecodeError, OSError) as e:
                    raise HarpoException("Unable to parse groups file %s: %s", self.groups_file, e)
        else:
            logging.debug("No groups file found at %s. Creating an empty file.", self.groups_file)
            self.groups = {}
            self.save()

    def save(self):
        with open(self.groups_file, 'w') as stream:
            try:
                data = {}
                for group, group_obj in self.groups.items():
                    data[group] = group_obj.data
                data_encoded = json.dumps(data, sort_keys=True, indent=2)
                stream.write(data_encoded)
            except (json.JSONDecodeError, OSError) as e:
                raise HarpoException(e)

    def __getitem__(self, gid):
        try:
            return self.groups[gid]
        except KeyError:
            raise HarpoGroupDoesntExist("No such group: {}".format(gid))

    def __iter__(self):
        for group in self.groups.keys():
            yield group

    def create(self, gid):
        if gid in self.groups.keys():
            raise HarpoGroupExists("Group already exists: {}".format(gid))

        logging.info("Create group: %s", gid)
        self.groups[gid] = Group(gid=gid, data={"users": []})
        self.save()
        return self[gid]

    def remove(self, gid):
        if gid not in self.groups.keys():
            raise HarpoGroupDoesntExist("Group doesn't exist: {}".format(gid))

        logging.info("Remove group: %s", gid)
        self.groups.pop(gid)
        self.save()
        return True

    def exists(self, gid):
        try:
            self[gid]
            return True
        except (KeyError, HarpoGroupDoesntExist):
            return False


class Group(object):
    def __init__(self, gid, data):
        self.gid = gid
        self.data = data
        self.update_dict()

    def update_dict(self):
        self.data['users'] = list_uniq(self.data['users'])

    def add_user(self, user_name):
        self.data['users'].append(user_name)
        self.update_dict()

    def remove_user(self, user_name):
        self.data['users'].remove(user_name)
        self.update_dict()

    def has_user(self, user_name):
        return user_name in self.data['users']
