
"""
Copyright 2018 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from cortex_client.utils import base64decode_jsonstring
from .client import _Client
from .utils import get_logger
import traceback
log = get_logger(__name__)

class SecretsClient(_Client):
    """A client for the Cortex Jobs REST API."""

    URIs = {
        'secrets': 'tenants/secrets',
        'secret': 'tenants/secrets/{}'
    }

    def get_secret(self, secret_key):
        """Returns the secret stored within the tenancy with a certain name.
        :return: JSONType
        """
        secret_with_original_file_path_as_key = None
        try:
            secret_with_original_file_path_as_key = self._get_json(self.URIs['secret'].format(secret_key))
        except Exception as e:
            log.error("Failed to get secret.")
            log.error(traceback.format_exc(e))
            return None
        secret_value = (
            None if not secret_with_original_file_path_as_key or len(secret_with_original_file_path_as_key) < 1 else
            list(secret_with_original_file_path_as_key.values())[0]
        )
        return base64decode_jsonstring(secret_value)

    def post_secret(self, secret_key, secret):
        """Publish a new secret with a certain key.
        :return: JSONType
        """
        return self._post_json(
            self.URIs['secret'].format(secret_key),
            secret
        )
