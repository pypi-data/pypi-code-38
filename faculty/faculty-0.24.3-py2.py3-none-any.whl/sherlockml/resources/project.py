# Copyright 2018 ASI Data Science
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import uuid

from attr import attrs, attrib

import sherlockml
from sherlockml.resources.user import User


@attrs
class Project(object):

    id = attrib(converter=uuid.UUID)
    name = attrib(converter=str)
    owner = attrib()

    @classmethod
    def get(cls, name):
        # TODO: Support getting projects by both owner and name
        owner = User.me()
        project_client = sherlockml.client("project")
        project = project_client.get_by_owner_and_name(owner.id, name)
        return cls(
            id=project.id, name=project.name, owner=User(project.owner_id)
        )
