# Copyright 2018 Catalyst IT Ltd.
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

from rt_client.v2.client import LimitedRecordManager


class CustomFieldManager(LimitedRecordManager):
    record_type = "customfield"

    def __init__(self, client):
        self.client = client
        self.customfield_cache = {}

    def get_id(self, customfield_name):
        """
        Translate a CustomField name into its associated id

        Args:
            customfield_name (str): The name of the CustomField.

        Returns:
            String CustomField id
        """
        if self.customfield_cache.get(customfield_name, None):
            return self.customfield_cache[customfield_name]
        else:
            search = self.search(
                [{"field": "Name", "value": customfield_name}], page=1, per_page=1
            )
            if search["count"] != 0:
                result = search["items"][0]["id"]
                self.customfield_cache[customfield_name] = result
                return result
            else:
                return None
