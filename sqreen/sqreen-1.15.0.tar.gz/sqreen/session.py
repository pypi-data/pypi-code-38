# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" High-level interaction with sqreen API
"""
import logging
from sys import exc_info

from ._vendors.urllib3.exceptions import HTTPError, MaxRetryError
from .exceptions import SqreenException
from .http_client import InvalidStatusCodeResponse, StatusFailedResponse
from .remote_exception import RemoteException

LOGGER = logging.getLogger(__name__)


class InvalidToken(Exception):
    """ Exception raise when a login fails because of the token value
    """

    pass


class Session(object):
    """ Class responsible for collection date and interacting with the sqreen API
    """

    def __init__(self, connection, api_key, app_name=None):
        self.connection = connection
        self.api_key = api_key
        self.app_name = app_name
        self.session_token = None

    def login(self, runtime_infos, retries=None):
        """ Login to the backend
        """

        if not retries:
            retries = self.connection.RETRY

        # We want repeat this logic for as long as necessary, but want to avoid a recursive call
        try:
            result = self.connection.post(
                "v1/app-login", runtime_infos, headers=self._api_headers(),
                retries=retries
            )
        except InvalidStatusCodeResponse as exc:
            LOGGER.error(
                "Cannot login. Token may be invalid: %s", self.api_key
            )
            LOGGER.error("Invalid response: %s", exc.response_data)
            if exc.status in (401, 403):
                raise InvalidToken()
            raise
        except StatusFailedResponse as exc:
            LOGGER.error(
                "Cannot login. Token may be invalid: %s", self.api_key
            )
            LOGGER.error("Invalid response: %s", exc.response)
            raise InvalidToken()
        except (SqreenException, HTTPError) as exc:
            LOGGER.error(
                "Cannot login. back.sqreen.io appears to be unavailable (%s).", type(exc).__name__
            )
            raise HTTPError()

        LOGGER.debug("Received session_id %s", result["session_id"])
        self.session_token = result["session_id"]

        return result

    def is_connected(self):
        """ Return a boolean indicating if a successfull login was made
        """
        return self.session_token is not None

    def _headers(self):
        """Return session headers used for authentication."""
        return {"x-session-key": self.session_token}

    def _api_headers(self):
        """Return API headers."""
        if self.app_name:
            return {
                "x-api-key": self.api_key,
                "x-app-name": self.app_name
            }
        else:
            return {
                "x-api-key": self.api_key
            }

    def perform_network(self, net_operation, url, retries, payload=None, headers=None, last_resort=False):
        """ Perform a network operation safely
        """
        try:
            if headers is None:
                headers = self._headers()

            if payload is None:
                return net_operation(url, headers=headers, retries=retries)
            else:
                return net_operation(url, payload, headers=headers, retries=retries)

        except MaxRetryError:
            LOGGER.info(
                "Request to %s expired after %d retries, moving on", url, retries.total
            )
            return None

        except (SqreenException, HTTPError) as exc:
            LOGGER.info(
                "Couldn't connect to %s due to exception %s", url, type(exc).__name__
            )
            # Prevent recursive exception
            if not last_resort:
                self.post_sqreen_exception(RemoteException(exc_info()).to_dict(), last_resort=True)
            return None

    def _get(self, url, retries=None):
        """ Call connection.get with right headers
        """
        return self.perform_network(self.connection.get, url=url, retries=retries)

    def _post(self, url, data, retries=None, last_resort=False):
        """Call connection.post with session headers."""
        return self.perform_network(self.connection.post, payload=data, url=url, retries=retries, last_resort=last_resort)

    def _post_api(self, url, data, retries=None):
        """Call connection.post with API headers."""
        return self.perform_network(self.connection.post, payload=data, url=url, headers=self._api_headers(), retries=retries)

    def logout(self):
        """ Logout current instance in the backend
        """
        return self._get("v0/app-logout", retries=self.connection.RETRY_ONCE)

    def heartbeat(self, payload):
        """ Tell the backend that the instance is still up, send latests command
        result, latest metrics and retrieve latest commands
        """
        return self._post(
            "v1/app-beat", payload, retries=self.connection.RETRY_LONG
        )

    def post_attack(self, attack):
        """ Report an attack on the backend
        """
        LOGGER.debug("Post attack %s", attack)
        return self._post(
            "v0/attack", attack, retries=self.connection.RETRY_LONG
        )

    def post_sqreen_exception(self, exception, last_resort=False):
        """Report a Sqreen exception happening at agent level."""
        return self._post(
            "v0/sqreen_exception", exception, retries=self.connection.RETRY_LONG,
            last_resort=last_resort
        )

    def post_app_sqreen_exception(self, exception):
        """Post a sqreen exception happening at application level."""
        return self._post_api(
            "v0/app_sqreen_exception", exception, retries=self.connection.RETRY_ONCE
        )

    def post_metrics(self, metrics):
        """ Post metrics aggregates to the backend
        """
        # Don't send empty metrics payload
        if len(metrics) < 1:
            return

        data = {"metrics": metrics}

        return self._post(
            "v0/metrics", data, retries=self.connection.RETRY_ONCE
        )

    def post_request_record(self, request_record):
        LOGGER.debug("Post request record %r", request_record)
        return self._post(
            "v0/request_record",
            request_record,
            retries=self.connection.RETRY_LONG
        )

    def get_rulespack(self):
        """ Retrieve rulespack from backend
        """
        return self._get("v0/rulespack", retries=self.connection.RETRY_LONG)

    def post_batch(self, batch, send_resiliently=True):
        """ Post a batch to the backend
        """
        LOGGER.debug("Post batch of size %d", len(batch))

        if send_resiliently:
            retry_policy = self.connection.RETRY_LONG
        else:
            retry_policy = self.connection.RETRY_ONCE

        return self._post(
            "v0/batch", {"batch": batch}, retries=retry_policy
        )

    def post_bundle(self, runtime_infos):
        data = {
            "bundle_signature": runtime_infos["bundle_signature"],
            "dependencies": runtime_infos["various_infos"]["dependencies"],
        }
        return self._post(
            "v0/bundle", data, retries=self.connection.RETRY_LONG
        )

    def get_actionspack(self):
        """Retrieve actions from backend."""
        return self._get("v0/actionspack", retries=self.connection.RETRY_LONG)
