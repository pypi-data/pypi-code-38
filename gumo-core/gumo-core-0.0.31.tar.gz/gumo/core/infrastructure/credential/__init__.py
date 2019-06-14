import os
import json

from typing import Optional
from typing import Union
from typing import Tuple

import google.auth.transport.requests
from google.oauth2 import service_account
from google.auth import compute_engine
from google.cloud import storage
from injector import inject

from gumo.core.exceptions import ServiceAccountConfigurationError
from gumo.core.injector import injector
from gumo.core.domain.configuration import GumoConfiguration

DEFAULT_TOKEN_URI = 'https://www.googleapis.com/oauth2/v4/token'

Credentials = Union[service_account.Credentials, compute_engine.Credentials]
IDTokenCredentials = Union[service_account.IDTokenCredentials, compute_engine.IDTokenCredentials]
Request = google.auth.transport.Request


class GoogleOAuthCredentialManager:
    @inject
    def __init__(
            self,
            gumo_configuration: GumoConfiguration,
    ):
        self._gumo_configuration = gumo_configuration
        self._credential_config = self._gumo_configuration.service_account_credential_config

    def build_credential(self) -> Credentials:
        _credentials = None

        try:
            if self._gumo_configuration.is_google_app_engine:
                _credentials = compute_engine.Credentials()
            elif 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
                _credentials = service_account.Credentials.from_service_account_info(
                    info=self._get_content_from_local()
                )
            elif self._credential_config.enabled:
                # will be deprecated.
                _credentials = service_account.Credentials.from_service_account_info(
                    info=self._get_content_from_storage()
                )
        except ServiceAccountConfigurationError:
            raise
        except RuntimeError as e:
            raise ServiceAccountConfigurationError(e)

        if _credentials is None:
            raise ServiceAccountConfigurationError(f'ServiceAccount Credential Config disabled.')

        return _credentials

    def build_request(self) -> Request:
        return google.auth.transport.requests.Request()

    def build_id_token_credential(
            self,
            target_audience: str,
            with_refresh: bool = True,
            token_uri: Optional[str] = None,
    ) -> Tuple[IDTokenCredentials, Request]:
        request = self.build_request()
        _id_token_credential = None

        try:
            if self._gumo_configuration.is_google_app_engine:
                _id_token_credential = compute_engine.IDTokenCredentials(
                    request=request,
                    target_audience=target_audience,
                )
                if with_refresh:
                    _id_token_credential.refresh(request=request)
            elif 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
                _credential = self.build_credential()
                _id_token_credential = service_account.IDTokenCredentials(
                    signer=_credential.signer,
                    service_account_email=_credential.service_account_email,
                    token_uri=token_uri if token_uri else DEFAULT_TOKEN_URI,
                    target_audience=target_audience,
                )
                if with_refresh:
                    _id_token_credential.refresh(request=request)
        except ServiceAccountConfigurationError:
            raise
        except RuntimeError as e:
            raise ServiceAccountConfigurationError(e)

        if _id_token_credential is None:
            raise ServiceAccountConfigurationError(f'ServiceAccount Credential Config disabled.')

        return (_id_token_credential, request)

    def _get_content_from_storage(self):
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name=self._credential_config.bucket_name)
        blob = bucket.blob(blob_name=self._credential_config.blob_path)
        content = blob.download_as_string(client=storage_client)

        return json.loads(content)

    def _get_content_from_local(self):
        credential_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')

        if not os.path.exists(credential_path):
            raise ServiceAccountConfigurationError(f'GOOGLE_APPLICATION_CREDENTIALS={credential_path} is not found.')

        with open(credential_path, 'r') as f:
            content = f.read()

        return json.loads(content)


def get_google_oauth_credential() -> Credentials:
    return injector.get(GoogleOAuthCredentialManager).build_credential()


def get_google_id_token_credential(
        target_audience: str,
        with_refresh: bool = True,
        token_uri: Optional[str] = None,
) -> Tuple[IDTokenCredentials, Request]:
    return injector.get(GoogleOAuthCredentialManager).build_id_token_credential(
        target_audience=target_audience,
        with_refresh=with_refresh,
        token_uri=token_uri,
    )
