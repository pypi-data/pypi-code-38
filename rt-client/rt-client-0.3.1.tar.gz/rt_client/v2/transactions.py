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
from rt_client.v2.client import LimitedRecordManager


class TransactionManager(LimitedRecordManager):
    record_type = "transaction"

    def __init__(self, client):
        self.client = client

    def get_attachments(
        self,
        transaction_id,
        fields="Subject,Content,ContentType,Created,Creator",
        page=1,
        per_page=20,
    ):
        """
        Get attachments for transaction.

        Args:
            transaction_id (str): The id code of the specific transaction
                to retrieve.
            page (int, optional): The page number, for paginated results.
                Defaults to the first (1) page.
            per_page (int, optional): Number of results per page. Defaults
                to 20 records per page, maximum value of 100.

        Returns:
            Dictionary with keys 'per_page', 'page', 'total', 'count', and
                'items' which is itself a dict with 'id', '_url', and 'type'.

        Raises:
            See Python Requests docs at
                http://docs.python-requests.org/en/master/_modules/requests/exceptions/
        """
        payload = {"page": page, "per_page": per_page}
        if fields:
            payload.update(utils.build_fields_query(fields))
        endpoint = f"transaction/{transaction_id}/attachments?"
        endpoint += urlencode(payload, quote_via=quote_plus)
        return self.client.get(endpoint)
