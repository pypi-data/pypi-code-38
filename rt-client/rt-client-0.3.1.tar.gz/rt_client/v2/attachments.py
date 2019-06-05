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

from urllib.parse import urljoin

from rt_client.v2.client import LimitedRecordManager


class AttachmentManager(LimitedRecordManager):
    record_type = "attachment"

    def __init__(self, client):
        self.client = client

    def file_url(self, attachment_id, ticket_id=None):
        """
        Retrieve direct link to attachment file.

        Args:
            attatchment_id (str): The id code of the specific attachment
                to retrieve.
            ticket_id (str, optional): The id code of the ticket the attatchment
                is connected to.

        Returns:
            String URL for the file location.
        """
        if not ticket_id:
            attach_data = self.attachment_data(attachment_id)
            transaction_id = attach_data["TransactionId"]["id"]
            ticket_id = self.transaction_get(transaction_id)["Object"]["id"]
        url = urljoin(self.base_host, f"Ticket/Attachment/{ticket_id}/{attachment_id}")
        return url
