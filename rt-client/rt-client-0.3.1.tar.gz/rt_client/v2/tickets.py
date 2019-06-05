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

import os
import json

from urllib.parse import quote_plus, urlencode

import magic

from rt_client import exceptions
from rt_client.common import utils
from rt_client.v2.client import RecordManager


# Ticket Statuses
STATUS_TYPES = ("new", "open", "stalled", "resolved", "rejected", "deleted")
CLOSED_STATUS = ("resolved", "rejected", "deleted")


class TicketManager(RecordManager):
    record_type = "ticket"

    def __init__(self, client):
        self.client = client

    def get_all(self, *args, **kwargs):
        raise exceptions.UnsupportedError(self._not_supported_msg("get all"))

    def _prep_attachments(self, attachments):
        files = []
        for attachment in attachments:
            files.append(
                (
                    "Attachment",
                    (
                        os.path.basename(attachment),
                        open(attachment, "rb"),
                        magic.from_file(attachment, mime=True),
                    ),
                )
            )
        return files

    def create(self, attrs, attachments=None):
        """
        ticket creation.

        Args:
            attrs (dict): A dictionary of attributes for the record.
            attachments (array, optional): Files to attach, as full path filenames.
                Defaults to None.

        Returns:
            json dict of attributes.

        Raises:
            See Python Requests docs at
                http://docs.python-requests.org/en/master/_modules/requests/exceptions/
        """
        if attachments:
            files = [("Json", (None, json.dumps(attrs), "application/json"))]
            files += self._prep_attachments(attachments)
            return self.client.post_files(self.record_type, files)
        else:
            return self.client.post(self.record_type, attrs)

    def update(self, record_id, attrs, attachments=None):
        """"
        ticket update.

        Args:
            record_id (str): The id code of the specific record to update.
            attrs (dict): A dictionary of attributes with updated values.
            attachments (array, optional): Files to attach. Defaults to None.

        Returns:
            Array containing a string with confirmation of update.

        Raises:
            See Python Requests docs at
                http://docs.python-requests.org/en/master/_modules/requests/exceptions/
        """
        if attachments:
            files = [("Json", (None, json.dumps(attrs), "application/json"))]
            files += self._prep_attachments(attachments)
            return self.client.post_files(f"{self.record_type}/{record_id}", files)
        else:
            return self.client.put(f"{self.record_type}/{record_id}", attrs)

    def bulk_create(self, data):
        """ For the creation of multiple tickets in a single request """
        # TODO Testing
        return self.client.post("/tickets/bulk", data)

    def bulk_update(self, data):
        """ For making changes to multiple tickets in a single request """
        # TODO Testing
        return self.client.put("/tickets/bulk", data)

    def reply(self, ticket_id, attrs, attachments=None):
        """
        Reply to a ticket, include email update to correspondents.

        Args:
            ticket_id (str): The id code of the specific ticket to reply.
            attrs (dict): A dictionary containing keys "Subject", "Content",
                and optionally "Cc" and "Bcc" fields.
            attachments (array, optional): Files to attach. Defaults to None.

        Returns:
            Array containing a string with confirmation of update.

        Raises:
            See Python Requests docs at
                http://docs.python-requests.org/en/master/_modules/requests/exceptions/
        """
        if attachments:
            attrs.update({"ContentType": "application/json"})
            files = [("Json", (None, json.dumps(attrs), "application/json"))]
            files += self._prep_attachments(attachments)
            return self.client.post_files(f"ticket/{ticket_id}/correspond", files)
        else:
            attrs.update({"ContentType": "text/plain"})
            return self.client.post(f"ticket/{ticket_id}/correspond", attrs)

    def comment(self, ticket_id, comment, attachments=None):
        """
        Add a comment to an existing ticket. Comments are for internal
        use and not visible to clients.

        Args:
            ticket_id (str): The id code of the specific ticket to reply.
            comment (str): The string content of the comment to be added.
            attachments (array, optional): Files to attach. Defaults to None.

        Returns:
            Array containing a string with confirmation of update.

        Raises:
            See Python Requests docs at
                http://docs.python-requests.org/en/master/_modules/requests/exceptions/

        """
        if attachments:
            content = {"id": ticket_id, "Action": "comment", "Text": comment}
            files = [("Json", (None, json.dumps(content), "application/json"))]
            files += self._prep_attachments(attachments)
            return self.client.post_files(f"ticket/{ticket_id}/comment", files)
        else:
            # Because this endpoint needs a text/plain content type,
            # it calls client.sess.post directly, rather than going through
            # client.post like most other methods.
            response = self.client.sess.post(
                self.client.host + f"ticket/{ticket_id}/comment",
                data=comment,
                headers={"Content-Type": "text/plain"},
            )
            response.raise_for_status()
            return response.json()

    def close(self, ticket_id, reject=False):
        """
        'Close' a ticket. The default status used for closing is "Resolved"
        though "Rejected" can be selected instead via an optional parameter.

        Args:
            ticket_id (str): The id code of the specific ticket to close.
            reject (bool, optional): Optionally close as "Rejected" rather
                than "Resolved."

        Returns:
            Array containing a string with confirmation of status update.

        Raises:
            See Python Requests docs at
                http://docs.python-requests.org/en/master/_modules/requests/exceptions/
        """
        closed = "rejected" if reject else "resolved"
        return self.update(ticket_id, {"Status": closed})

    def reopen(self, ticket_id):
        """
        Change a ticket's status to open.

        Args:
            ticket_id (str): The id code of the specific ticket to reopen.

        Returns:
            Array containing a string with confirmation of status update.

        Raises:
            See Python Requests docs at
                http://docs.python-requests.org/en/master/_modules/requests/exceptions/
        """
        return self.update(ticket_id, {"Status": "open"})

    def change_status(self, ticket_id, new_status):
        """
        Change a given ticket's status to specified value.

        Args:
            ticket_id (str): The id code of the specific ticket to reopen.
            new_status (str): A valid ticket state as a string. Valid states
                include: "new", "open", "blocked", "stalled", "resolved", and
                "rejected".

        Returns:
            Array containing a string with confirmation of status update.

        Raises:
            ValueError: If the status does not match a valid existing status.
            See Python Requests docs at
                http://docs.python-requests.org/en/master/_modules/requests/exceptions/
        """
        if new_status in STATUS_TYPES:
            return self.update(ticket_id, {"Status": new_status})
        else:
            raise ValueError(f"Invalid ticket status type {new_status}.")

    def history(
        self, ticket_id, fields="Data,Type,Creator,Created", page=1, per_page=20
    ):
        """
        retrieve transactions related to a specific ticket.

        Args:
            ticket_id (str): The id code of the ticket.
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

        endpoint = f"{self.record_type}/{ticket_id}/history?"
        endpoint += urlencode(payload, quote_via=quote_plus)
        return self.client.get(endpoint)

    def search(
        self, search_query, fields=None, simple_search=False, page=1, per_page=20
    ):
        """
        Search for tickets using TicketSQL.

        Args:
            search_query (str): The query string in TicketSQL.
                Example: '(Status = "new" OR Status = "open") AND Queue = "General"'
                See https://rt-wiki.bestpractical.com/wiki/TicketSQL for more
                detailed information.
            fields (dict/list/string, optional): A value representing the fields or
                subfields wanted from the record. Expected format is the form of:
                    - "FieldA"
                    - ["FieldA", "FieldB", "FieldC"]
                    - {"FieldA": "SubfieldA"}
                    - {"FieldA": {"SubfieldA": "Sub-subfieldA"}}
                    - {"FieldA": {"SubfieldA": "Sub-subfieldA"},
                       {"FieldC": {"SubfieldC": "Sub-subfieldC"}}
                    - ["FieldA", {"FieldA": "SubfieldA"}]
            simple_search (bool, optional): When True use simple search syntax,
                when False use TicketSQL.
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
        payload = {
            "query": search_query,
            "simple": 1 if simple_search else 0,
            "page": page,
            "per_page": per_page,
        }

        if fields:
            payload.update(utils.build_fields_query(fields))

        search_endpoint = "tickets?" + urlencode(payload, quote_via=quote_plus)
        return self.client.get(search_endpoint)
