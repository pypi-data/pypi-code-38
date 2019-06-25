# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
import json
import logging
import copy

from .exceptions import ConfigUploadFailed
from .entitybase import EntityBase
from . import utils


logger = logging.getLogger(__name__)


class System(EntityBase):
    """
    This class represents a system.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def delete(self):
        """Deletes this system from the sesam-node.
        """
        url = self._connection.get_system_url(self.id)
        response = self._connection.do_delete_request(url)
        utils.validate_response_is_ok(response, allowable_response_status_codes=[200])
        self.update_raw_jsondata(response.text)

    def modify(self, system_config, force=False):
        """Modifies the system with the specified configuration."""
        request_params = {"force": "true" if force else "false"}

        system_config = copy.deepcopy(system_config)
        system_config["_id"] = self.id
        response = self._connection.do_put_request(self._connection.get_system_config_url(self.id), json=system_config,
                                                   params=request_params)
        utils.validate_response_is_ok(response, allowable_response_status_codes=[200, 400])

        if response.status_code == 400:
            raise ConfigUploadFailed(response=response)

        self.update_raw_jsondata(response.text)

    @property
    def runtime(self):
        return copy.deepcopy(self._raw_jsondata["runtime"])

    def get_source_prototypes(self, timeout=None):
        kwargs = {}
        if timeout is not None:
            kwargs["timeout"] = timeout
        url = self._connection.get_system_source_prototypes_url(self.id)
        response = self._connection.do_get_request(url, **kwargs)
        utils.validate_response_is_ok(response, allowable_response_status_codes=[200])
        return response.json()

    def get_sink_prototypes(self, timeout=None):
        kwargs = {}
        if timeout is not None:
            kwargs["timeout"] = timeout
        url = self._connection.get_system_sink_prototypes_url(self.id)
        response = self._connection.do_get_request(url, **kwargs)
        utils.validate_response_is_ok(response, allowable_response_status_codes=[200])
        return response.json()

    def get_secrets(self, include_internal_secrets=False):
        """This returns a list with the names of the secrets."""
        request_params = {}
        if include_internal_secrets:
            request_params["include-internal-secrets"] = "true"

        response = self._connection.do_get_request(self._connection.get_secrets_url(system_id=self.id),
                                                   params=request_params)
        utils.validate_response_is_ok(response, allowable_response_status_codes=[200])
        secrets_info = utils.parse_json_response(response)
        return secrets_info

    def get_secrets_values(self):
        """This returns a dict with secretname=>secretvalue mappings. This is only available for nodes that
        are running in ci-test mode. In addition, the user has to have the "SystemAdmin" role."""
        request_params = {}
        response = self._connection.do_get_request(self._connection.get_secrets_values_url(system_id=self.id),
                                                   params=request_params)
        utils.validate_response_is_ok(response, allowable_response_status_codes=[200])
        secrets_info = utils.parse_json_response(response)
        return secrets_info

    def put_secrets(self, secrets_content, dont_encrypt=False):
        encrypt = dont_encrypt and "false" or "true"
        response = self._connection.do_put_request(self._connection.get_secrets_url(system_id=self.id),
                                                   json=secrets_content, params=dict(encrypt=encrypt))
        utils.validate_response_is_ok(response, allowable_response_status_codes=[200])

        secrets_info = utils.parse_json_response(response)
        return secrets_info

    def post_secrets(self, secrets_content, dont_encrypt=False):
        encrypt = dont_encrypt and "false" or "true"
        response = self._connection.do_post_request(self._connection.get_secrets_url(system_id=self.id),
                                                    json=secrets_content, params=dict(encrypt=encrypt))
        utils.validate_response_is_ok(response, allowable_response_status_codes=[200])

        secrets_info = utils.parse_json_response(response)
        return secrets_info

    def delete_secret(self, key):
        response = self._connection.do_delete_request(self._connection.get_secret_url(key, system_id=self.id))
        utils.validate_response_is_ok(response, allowable_response_status_codes=[200])
        secrets_info = utils.parse_json_response(response)
        return secrets_info

    def get_status(self):
        """This returns a dict with the system's status information."""
        request_params = {}
        response = self._connection.do_get_request(self._connection.get_system_status_url(self.id),
                                                   params=request_params)
        utils.validate_response_is_ok(response, allowable_response_status_codes=[200])
        status_info = utils.parse_json_response(response)
        return status_info

    @property
    def is_valid_config(self):
        return self._raw_jsondata["runtime"]["is-valid-config"]

    @property
    def config_errors(self):
        return self._raw_jsondata["runtime"]["config-errors"]
