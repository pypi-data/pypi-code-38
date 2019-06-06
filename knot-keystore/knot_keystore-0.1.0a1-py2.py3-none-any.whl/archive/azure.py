# Copyright (c) 2019 Workonline Communications (Pty) Ltd. All rights reserved.
#
# The contents of this file are licensed under the MIT License
# (the "License"); you may not use this file except in compliance with the
# License.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
"""knot_keystore.archive.azure module."""

import logging
import tempfile

import adal

from azure.keyvault import KeyVaultClient, KeyVaultAuthentication, KeyId
from azure.storage.blob import BlockBlobService
from azure.storage.common import TokenCredential

from knot_keystore.archive.base import ArchiveBase

log = logging.getLogger(__name__)

AAD_ENDPOINT = "https://login.microsoftonline.com"
STORAGE_RESOURCE_ID = "https://storage.azure.com"


class ArchiveAzure(ArchiveBase):
    """Archive knot kasp-db to Azure blob storage."""

    def __init__(self, *args, **kwargs):
        """Initialise a new instance."""
        super().__init__(*args, **kwargs)
        log.debug("Trying to aquire an azure blob service client")
        try:
            self.blob_service = self.get_blob_service()
        except Exception as e:
            log.error(f"Failed to aquire blob service client: {e}")
            raise e

    @property
    def auth_endpoint(self):
        """Get the authentication endpoint URL for the AAD tenant."""
        return f"{AAD_ENDPOINT}/{self.tenant_id}"

    def get_blob_service(self):
        """Authenticate to the azure blob service."""
        log.debug("Trying to authenticate to azure AD")
        try:
            ctx = adal.AuthenticationContext(self.auth_endpoint)
            token = ctx.acquire_token_with_client_credentials(STORAGE_RESOURCE_ID,  # noqa: E501
                                                              self.client_id,
                                                              self.client_secret)  # noqa: E
        except Exception as e:
            log.error(f"Failed to authenticate to azure AD: {e}")
            raise e
        token_credential = TokenCredential(token["accessToken"])
        blob_service = BlockBlobService(account_name=self.storage_account_name,
                                        token_credential=token_credential)
        resolver = KeyResolver(context=self)
        blob_service.key_encryption_key = resolver.resolve()
        blob_service.key_resolver_function = resolver.resolve
        blob_service.require_encryption = True
        return blob_service

    def get_blob_hash(self):
        """Check that container and blob exist and get the sha256 hash."""
        log.debug(f"Checking that container '{self.container_name}' exists")
        if not self.blob_service.exists(self.container_name):
            e = RuntimeError(f"Container {self.container_name} does not exist")
            log.error(e)
            raise e
        hash = None
        log.debug(f"Checking whether blob {self.blob_name} exists")
        if self.blob_service.exists(self.container_name, self.blob_name):
            log.debug("Trying to get blob metadata")
            try:
                metadata = self.blob_service.get_blob_metadata(self.container_name,  # noqa: E501
                                                               self.blob_name)
            except Exception as e:
                log.error(f"Failed to get blob metadata: {e}")
            log.debug("Getting content-sha265-hash property")
            try:
                hash = metadata["content_sha256_hash"]
            except KeyError:
                log.warning(f"Blob {self.blob_name} has no "
                            "'content-sha256-hash' metadata property")
                hash = ""
        return hash

    def exec(self):
        """Execute archival proceedure."""
        log.debug(f"Tying to backup kasp-db to azure")
        log.debug("Creating temp directory")
        with tempfile.TemporaryDirectory() as tmp_path:
            log.debug(f"Working in {tmp_path}")
            path, archive_sha256_hash = self.get_cleartext_archive(tmp_path)
            blob_sha256_hash = self.get_blob_hash()
            if blob_sha256_hash is not None:
                log.debug(f"Comparing local ('{archive_sha256_hash}') "
                          f"and remote ('{blob_sha256_hash}') sha256 hashes")
                if archive_sha256_hash == blob_sha256_hash:
                    log.info("Content hashes match: exiting")
                    return False
                log.debug("Trying to take blob snapshot")
                try:
                    self.blob_service.snapshot_blob(self.container_name,
                                                    self.blob_name)
                except Exception as e:
                    log.error(f"Failed to take blob snapshot: {e}")
                    raise e
            log.debug(f"Trying to store archive to azure")
            metadata = {"content_sha256_hash": archive_sha256_hash}
            try:
                self.blob_service.create_blob_from_path(self.container_name,
                                                        self.blob_name,
                                                        path,
                                                        metadata=metadata)
            except Exception as e:
                log.error(f"Failed to create azure blob: {e}")
                raise e
        log.info("Encrypted archive written to "
                 f"{self.container_name}/{self.blob_name}")


class KeyResolver(object):
    """Implementation of the KEK interface."""

    alg = "RSA-OAEP-256"

    def __init__(self, context):
        """Initialise an instance of KeyWrapper."""
        self.context = context
        auth_callback = self.get_auth_callback()
        auth = KeyVaultAuthentication(auth_callback)
        self.client = KeyVaultClient(auth)

    def resolve(self, kid=None):
        """Resolve a key id."""
        if kid is None:
            self.kid = KeyId(vault=self.context.vault_url,
                             name=self.context.kek_key_name)
        else:
            self.kid = KeyId(uri=kid)
        return self

    def get_auth_callback(self):
        """Get a callback to authenticate with ADAL for key vault access."""
        def auth_callback(server, resource, scope):
            ctx = adal.AuthenticationContext(self.context.auth_endpoint)
            token = ctx.acquire_token_with_client_credentials(resource,
                                                              self.context.client_id,  # noqa: E501
                                                              self.context.client_secret)  # noqa: E501
            return token["tokenType"], token["accessToken"]
        return auth_callback

    def get_kid(self):
        """Get the key ID of the KEK."""
        return self.kid.id

    def get_key_wrap_algorithm(self):
        """Get the algorithm used to wrap CEKs."""
        return self.alg

    def wrap_key(self, cek):
        """Wrap the specified CEK."""
        resp = self.client.wrap_key(self.kid.vault, self.kid.name,
                                    self.kid.version, self.alg, cek)
        return resp.result

    def unwrap_key(self, wraped_cek, algorithm):
        """Unwrap the wraped CEK."""
        resp = self.client.unwrap_key(self.kid.vault, self.kid.name,
                                      self.kid.version, algorithm, wraped_cek)
        return resp.result
