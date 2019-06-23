# coding=utf-8

"""Actual implementation of SSO"""


import base64
import hashlib
import hmac
import typing
from urllib.parse import parse_qs, urlencode

import logging
from django.conf import settings
from django.utils.crypto import constant_time_compare
from django.utils.encoding import force_bytes

SSOResponse = typing.NamedTuple(
    "SSOResponse",
    (
        ("nonce", bytes),
        ("redirect", str)
    )
)


SignedPayload = typing.NamedTuple(
    "SignedPayload",
    (
        ("sso", bytes),
        ("sig", bytes)
    )
)


class BaseSSOGenerator(object):

    """Base class for SSO generator."""

    def __init__(self, sso_key: typing.Union[str, bytes]):
        self.sso_key = force_bytes(sso_key)

    def _get_payload_singature(self, payload: typing.Union[str, bytes]) -> bytes:
        """Returns HMAC signature for ``payload``."""
        digest = hmac.new(self.sso_key, force_bytes(payload), digestmod=hashlib.sha256).hexdigest()
        return force_bytes(digest)

    def prepare_signed_payload(
            self,
            params: typing.Union[dict, typing.Sequence[typing.Tuple[str, str]]]
    ) -> SignedPayload:
        """Prepare payload and signature."""
        encoded_params = base64.b64encode(force_bytes(urlencode(params)))
        response_sig = self._get_payload_singature(encoded_params)
        return (
            ('sso', encoded_params),
            ('sig', response_sig),
        )

    def _verify_payload(
            self,
            payload: typing.Union[str, bytes],
            signature: typing.Union[str, bytes]
    ) -> bool:
        """Verifies that signature is correct for payload."""
        this_signature = self._get_payload_singature(payload)
        result = constant_time_compare(
            this_signature,
            force_bytes(signature)
        )
        return result

    @classmethod
    def create_url(cls, base_url, signed_payload) -> str:
        """Get full url with query string."""
        query_string = urlencode(signed_payload)
        return '%s?%s' % (base_url, query_string)


class SSOProducerUtils(BaseSSOGenerator):
    """Utils for SSO producer."""

    def __init__(
            self,
            sso_key: typing.Union[str, bytes],
            consumer_url: str,
            user: settings.AUTH_USER_MODEL,
            sso: typing.Union[str, bytes],
            sig: typing.Union[str, bytes]
    ):
        """
        Init function, gets unpacked parameters from SSO endpoint,
        as well as logged in user.
        """
        super().__init__(sso_key)
        self.consumer_url = consumer_url
        assert isinstance(self.consumer_url, str)
        self.user = user
        self.sso = force_bytes(sso)
        self.sig = force_bytes(sig)

    def validate(self):
        """Validate this sso instance, this should perform sanity checks."""

        payload = base64.b64decode(self.sso)
        if b'nonce' not in payload:
            raise ValueError(self.sso, payload)

    @property
    def request_payload(self) -> str:
        """Returns decoded request payload."""
        payload = base64.b64decode(self.sso)
        return payload

    def verify_signature(self) -> bool:
        """Verifies the signature."""
        return self._verify_payload(self.sso, self.sig)

    def get_nonce(self) -> bytes:
        """Returns nonce from request payload."""
        parsed_payload = parse_qs(self.request_payload)
        return parsed_payload[b'nonce'][0]

    def get_response_params(self) -> typing.Sequence[typing.Tuple[str, str]]:
        """
        Returns SSO response parameters.

        Tuple of tuples is returned instead of a dict to have
        deterministic ordering of parameters, as order of parameters
        changes signature, and makes testing harder.
        """
        return (
            ('nonce', self.get_nonce()),
            ('email', self.user.email),
            ('username', self.user.username),
            ('external_id', self.user.id),
        )

    def get_signed_payload(self) -> dict:
        """Returns signed GET parameters for redirect."""
        return self.prepare_signed_payload(self.get_response_params())

    def get_sso_redirect(self, signed_payload) -> str:
        """Get full sso redirect."""
        return self.create_url(self.consumer_url, signed_payload)


class SSOProviderService(object):
    """
    SSO provider service.
    """

    def __init__(self, sso_key):
        """
        :param sso_key: SSO shared secret key.
        """
        self.sso_key = sso_key

    def get_signed_url(
            self,
            user: settings.AUTH_USER_MODEL,
            sso: str,
            signature: str,
            redirect_to: str
    ) -> typing.Optional[str]:
        """
        Performs SSO, returning redirect url.

        :param user: User that will be logged in using SSO.
        :param sso: SSO string received from consumer
        :param signature: Signature for sso string
        :param redirect_to: Endpoint user will be redirected to
        :param consumer_type: type of SSO consumer, can be used to
                              customize SSO a bit.
        """

        gen = SSOProducerUtils(
            sso_key=self.sso_key,
            consumer_url=redirect_to,
            user=user,
            sso=sso,
            sig=signature
        )
        try:
            gen.validate()
        except ValueError:
            logging.exception("Invalid sso")
            return None
        if not gen.verify_signature():
            return None
        payload = gen.get_signed_payload()
        return gen.get_sso_redirect(payload)


class SSOClientUtils(BaseSSOGenerator):
    """
    Utils for clients to the SSO mechanism.
    """

    def __init__(
            self,
            sso_key: typing.Union[str, bytes],
            base_sso_url: str
    ):
        """
        Init function. Set sso key and sso url
        """
        super().__init__(sso_key)
        self.base_sso_url = base_sso_url

    def generate_sso_url(self, nonce: str, require_activation=False) -> str:
        """
        Generates url to sso with given nonce
        :param nonce: nonce to be used in the sso url
        :param require_activation: Set to false if email is not validated
        :return: Full url to sso provider with all required query parameters
        """
        payload = [
            ('nonce', nonce),
        ]
        if require_activation:
            payload.append(('require_activation', "true"))
        signed_payload = self.prepare_signed_payload(payload)
        return self.create_url(self.base_sso_url, signed_payload)

    def validate_sso_against_sid(self, sso: str, sig: str) -> bool:
        """

        :param sso: payload to be verified
        :param sig: signed payload
        :return: Return true if sso matches sig
        """
        return self._verify_payload(sso, sig)

    @classmethod
    def decode_client_data(cls, base64_payload: str) -> dict:
        """
        Decode payload to dict of param and values
        :param base64_payload: Payload encoded in base 64
        :return: Dict of parameters and values. Values are in array.
        """
        parsed_payload = parse_qs(base64.b64decode(base64_payload))
        return parsed_payload

    @classmethod
    def get_param(cls, sso_decoded_payload: dict, param_name: str) -> str:
        """
        Extract parameter from payload dict
        :param sso_decoded_payload: dict
        :param param_name: Name of the param
        :return: Value of the param or empty string
        """
        if param_name in sso_decoded_payload.keys():
            values = sso_decoded_payload[param_name]
            if values:
                return values[0].decode('ascii')
        return ''
