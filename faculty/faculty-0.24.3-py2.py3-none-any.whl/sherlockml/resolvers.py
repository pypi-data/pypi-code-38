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


import sherlockml


def resolve_project(project):
    try:
        project_id = uuid.UUID(project)
    except ValueError:
        account_client = sherlockml.client('account')
        project_client = sherlockml.client('project')
        user_id = account_client.authenticated_user_id()
        project_id = project_client.get_by_owner_and_name(user_id, project).id
    return project_id
