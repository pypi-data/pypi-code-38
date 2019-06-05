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

from urllib.parse import quote_plus, urlencode

from rt_client.common import utils
from rt_client import exceptions

# Valid record types
RECORD_TYPES = (
    "ticket",
    "queue",
    "asset",
    "user",
    "group",
    "catalog",
    "attachment",
    "customfield",
    "customrole",
)


class RecordManager(object):
    def __init__(self, client, record_type):
        """
        Generic Record Manager.

        Args:
            client (RTClient): A valid RTClient instance.
            record_type (str): String value present in RECORD_TYPES.

        InvalidRecordException: If the record_type is not in RECORD_TYPES.
        """
        if record_type not in RECORD_TYPES:
            raise ValueError(f"Invalid record type: {record_type}")
        self.record_type = record_type
        self.client = client

    def create(self, attrs):
        """
        Generic record creation.

        Args:
            attrs (dict): A dictionary of attributes for the record.

        Returns:
            json dict of attributes.

        Raises:
            See Python Requests docs at
                http://docs.python-requests.org/en/master/_modules/requests/exceptions/
        """
        return self.client.post(self.record_type, attrs)

    def get(self, record_id):
        """
        Generic record retrieval.

        Args:
            record_id (str): The id code of the specific record to retrieve.

        Returns:
            json dict of attributes.

        Raises:
            See Python Requests docs at
                http://docs.python-requests.org/en/master/_modules/requests/exceptions/
        """
        return self.client.get(f"{self.record_type}/{record_id}")

    def get_all(self, fields=None, page=1, per_page=20):
        """
        Generic record archive retrieval.

        Args:
            self.record_type (str): Record type from RECORD_TYPES,
                e.g. 'ticket', 'queue', 'asset', 'user', 'group', 'attachment'
            fields (dict/list/string, optional): A value representing the fields or
                subfields wanted from the record. Expected format is the form of:
                    - "FieldA"
                    - ["FieldA", "FieldB", "FieldC"]
                    - {"FieldA": "SubfieldA"}
                    - {"FieldA": {"SubfieldA": "Sub-subfieldA"}}
                    - {"FieldA": {"SubfieldA": "Sub-subfieldA"},
                       {"FieldC": {"SubfieldC": "Sub-subfieldC"}}
                    - ["FieldA", {"FieldA": "SubfieldA"}]
            page (int, optional): The page number, for paginated results.
                Defaults to the first (1) page.
            per_page (int, optional): Number of results per page. Defaults
                to 20 records per page, maximum value of 100.

        Returns:
            JSON dict in the form of the example below:

            {
                "count": 20,
                "page": 1,
                "per_page": 20,
                "total": 3810,
                "items": [
                    {…},
                    {…},
                    …
                ]
            }

        Raises:
            See Python Requests docs at
                http://docs.python-requests.org/en/master/_modules/requests/exceptions/
        """
        payload = {"page": page, "per_page": per_page}

        if fields:
            payload.update(utils.build_fields_query(fields))

        query_string = urlencode(payload, quote_via=quote_plus)

        return self.client.get(f"{self.record_type}s/all?{query_string}")

    def update(self, record_id, attrs):
        """"
        Generic record update.

        Args:
            record_id (str): The id code of the specific record to update.
            attrs (dict): A dictionary of attributes with updated values.

        Returns:
            Array containing a string with confirmation of update.

        Raises:
            See Python Requests docs at
                http://docs.python-requests.org/en/master/_modules/requests/exceptions/
        """
        return self.client.put(f"{self.record_type}/{record_id}", attrs)

    def delete(self, record_id):
        """
        Generic record deletion.

        Args:
            record_id (str): The id code of the specific record to delete.

        Returns:
            Array containing a string with confirmation of deletion.

        Raises:
            See Python Requests docs at
                http://docs.python-requests.org/en/master/_modules/requests/exceptions/
        """
        return self.client.delete(f"{self.record_type}/{record_id}")

    def search(self, search_terms, fields=None, page=1, per_page=20):
        """
        Generic record search.

        Args:
            search_terms (array of dict): An array of dicts containing
                the keys "field", "operator" (optional), and "value."
                Example:
                [
                    { "field":    "Name",
                      "operator": "LIKE",
                      "value":    "Engineering" },

                    { "field":    "Lifecycle",
                      "value":    "helpdesk" }
                ]
            fields (dict/list/string, optional): A value representing the fields or
                subfields wanted from the record. Expected format is the form of:
                    - "FieldA"
                    - ["FieldA", "FieldB", "FieldC"]
                    - {"FieldA": "SubfieldA"}
                    - {"FieldA": {"SubfieldA": "Sub-subfieldA"}}
                    - {"FieldA": {"SubfieldA": "Sub-subfieldA"},
                       {"FieldC": {"SubfieldC": "Sub-subfieldC"}}
                    - ["FieldA", {"FieldA": "SubfieldA"}]
            page (int, optional): The page number, for paginated results.
                Defaults to the first (1) page.
            per_page (int, optional): Number of results per page. Defaults
                to 20 records per page, maximum value of 100.

        Returns:
            JSON dict in the form of the example below:

            {
                "count": 20,
                "page": 1,
                "per_page": 20,
                "total": 3810,
                "items": [
                    {…},
                    {…},
                    …
                ]
            }

        Raises:
            See Python Requests docs at
                http://docs.python-requests.org/en/master/_modules/requests/exceptions/
        """
        search_terms.extend(
            [{"field": "page", "value": page}, {"field": "per_page", "value": per_page}]
        )

        payload = {}
        if fields:
            payload.update(utils.build_fields_query(fields))

        query_string = urlencode(payload, quote_via=quote_plus)
        return self.client.post(
            f"{self.record_type}s?{query_string}", content=search_terms
        )

    def history(self, record_id, fields=None, page=1, per_page=20):
        """
        Generic history retrieval.

        Args:
            record_id (str): The id code of the specific record.
            fields (dict/list/string, optional): A value representing the fields or
                subfields wanted from the record. Expected format is the form of:
                    - "FieldA"
                    - ["FieldA", "FieldB", "FieldC"]
                    - {"FieldA": "SubfieldA"}
                    - {"FieldA": {"SubfieldA": "Sub-subfieldA"}}
                    - {"FieldA": {"SubfieldA": "Sub-subfieldA"},
                       {"FieldC": {"SubfieldC": "Sub-subfieldC"}}
                    - ["FieldA", {"FieldA": "SubfieldA"}]
            page (int, optional): The page number, for paginated results.
                Defaults to the first (1) page.
            per_page (int, optional): Number of results per page. Defaults
                to 20 records per page, maximum value of 100.

        Returns:
            JSON dict in the form of the example below:

            {
               "count" : 20,
               "page" : 1,
               "per_page" : 20,
               "total" : 3810,
               "items" : [
                  { … },
                  { … },
                    …
               ]
            }

        Raises:
            See Python Requests docs at
                http://docs.python-requests.org/en/master/_modules/requests/exceptions/
        """
        payload = {"page": page, "per_page": per_page}
        if fields:
            payload.update(utils.build_fields_query(fields))

        endpoint = f"{self.record_type}/{record_id}/history?"
        endpoint += urlencode(payload, quote_via=quote_plus)
        return self.client.get(endpoint)

    def _not_supported_msg(self, operation):
        err_message = f"{operation.title()} is not supported "
        err_message += f"for record type {self.record_type} due to RT API limitations."
        return err_message


class LimitedRecordManager(RecordManager):
    def get_all(self, *args, **kwargs):
        raise exceptions.UnsupportedOperation(self._not_supported_msg("get all"))

    def create(self, *args, **kwargs):
        raise exceptions.UnsupportedOperation(self._not_supported_msg("create"))

    def update(self, *args, **kwargs):
        raise exceptions.UnsupportedOperation(self._not_supported_msg("update"))

    def delete(self, *args, **kwargs):
        raise exceptions.UnsupportedOperation(self._not_supported_msg("delete"))

    def history(self, *args, **kwargs):
        raise exceptions.UnsupportedOperation(self._not_supported_msg("history"))
