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

import logging
from urllib.parse import urljoin

import requests

from rt_client.v2.record_manager import LimitedRecordManager, RecordManager
from rt_client.v2.attachments import AttachmentManager
from rt_client.v2.customfields import CustomFieldManager
from rt_client.v2.tickets import TicketManager
from rt_client.v2.transactions import TransactionManager


logger = logging.getLogger(__name__)


class Client(object):
    def __init__(
        self,
        username,
        password,
        endpoint,
        auth_endpoint="NoAuth/Login.html",
        api_endpoint="REST/2.0/",
        auth_token=None,
        verify=True,
    ):
        """
        Args:
            username (str): The user's login username.
            password (str): The user's login password.
            endpoint (str): The base URL of the host RT system. e.g 'rt.host.com/'
            auth_endpoint (str): The endpoint to POST Authorization. e.g 'login/'
            api_endpoint (str, optional): The endpoint for the REST API.
                Defaults to 'REST/2.0/'
            auth_token (str, optional): Authentication token from
                the RT::Authen::Token extension. Defaults to None.
            verify (boolean, optional): whether to verify certs or not
        """
        # Authentication
        self.verify = verify
        self.sess = requests.Session()
        self._authenicate(
            urljoin(endpoint, auth_endpoint), username, password, auth_token
        )
        # Set important endpoints
        self.base_host = endpoint
        self.host = urljoin(endpoint, api_endpoint)
        # Create record manager links
        self._create_record_managers()

    def _authenicate(self, auth_url, username, password, auth_token=None):
        """ Session authentication function """
        try:
            # Use token authentication, if able
            if auth_token:
                token = f"token {auth_token}"
                self.sess.post(
                    auth_url, data={"Authentication": token}, verify=self.verify
                )
            # Otherwise, revert to username/password authentication
            else:
                self.sess.post(
                    auth_url,
                    data={"user": username, "pass": password},
                    verify=self.verify,
                )
            return self.sess
        except Exception:
            logger.debug("RT Client Authentication Failure")
            raise

    def _create_record_managers(self):
        """ Creates managers for each required record type """
        try:
            # Special Records
            self.ticket = TicketManager(self)
            self.transaction = TransactionManager(self)
            self.attachment = AttachmentManager(self)
            self.customfield = CustomFieldManager(self)

            # Fully supported records
            for full_record in ["queue", "catalog", "asset", "user"]:
                setattr(self, full_record, RecordManager(self, full_record))

            # Partially supported records
            for limited_record in ["group", "customrole"]:
                setattr(
                    self, limited_record, LimitedRecordManager(self, limited_record)
                )
        except Exception:
            logger.debug("Failed to create RT Client Record Managers")
            raise

    # REST V2

    def get(self, url, *args, **kwargs):
        """ Generic GET request to specified URL """
        url = urljoin(self.host, url)
        response = self.sess.get(url, verify=self.verify, *args, **kwargs)
        response.raise_for_status()
        result = response.json()
        return result

    def post(self, url, content, *args, **kwargs):
        """ Generic POST request to specified URL """
        url = urljoin(self.host, url)
        response = self.sess.post(
            url,
            verify=self.verify,
            json=content,
            headers={"Content-Type": "application/json"},
            *args,
            **kwargs,
        )
        response.raise_for_status()
        return response.json()

    def post_files(self, url, files, *args, **kwargs):
        """ Generic POST request with files to specified URL """
        url = urljoin(self.host, url)
        response = self.sess.post(url, verify=self.verify, files=files, *args, **kwargs)
        response.raise_for_status()
        return response.json()

    def put(self, url, content, *args, **kwargs):
        """ Generic PUT request to specified URL """
        url = urljoin(self.host, url)
        response = self.sess.put(
            url,
            verify=self.verify,
            json=content,
            headers={"Content-Type": "application/json"},
            *args,
            **kwargs,
        )
        response.raise_for_status()
        return response.json()

    def delete(self, url, *args, **kwargs):
        """ Generic DELETE request to specified URL """
        url = urljoin(self.host, url)
        response = self.sess.delete(url, verify=self.verify, *args, **kwargs)
        response.raise_for_status()
        return response.json()

    # System Information functionality

    def rt_info(self):
        """
        General Information about the RT system, including RT version and
        plugins
        """
        response = self.sess.get("rt", verify=self.verify)
        response.raise_for_status()
        return response.json()

    def rt_version(self):
        """
        Get RT version.
        """
        response_data = self.rt_info()
        return response_data["Version"]

    def rt_plugins(self):
        """
        Retrieve array of RT plugins.
        """
        response_data = self.rt_info()
        return response_data["Plugins"]
