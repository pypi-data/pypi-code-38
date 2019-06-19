import base64

from akeyless_uam_api import GetItemReplyObj, GetUserItemsReplyObj
from akeyless_uam_api.rest import ApiException

from akeyless.client_base import AkeylessClientI
from akeyless.config import AkeylessClientConfig
from akeyless.crypto import gen_derivation_data, CryptoAlgorithm, encrypt, decrypt
from akeyless.crypto.utils import AkeylessCiphertext
from akeyless.exceptions import AkeylessSDKClientError


class AkeylessClient(AkeylessClientI):

    def __init__(self, config):
        # type: (AkeylessClientConfig) -> None
        super(AkeylessClient, self).__init__(config)

    def describe_item(self, item_name):
        # type: (str) -> GetItemReplyObj
        return self.api.get_item(self.cr.get_uam_creds(), item_name)

    def encrypt_string(self, key_name, plaintext):
        # type: (str, str) -> str
        return self._encrypt(key_name, str.encode(plaintext)).to_base64()

    def decrypt_string(self, key_name, ciphertext):
        # type: (str, str) -> str
        return self._decrypt(key_name, base64.b64decode(ciphertext)).decode("utf-8")

    def encrypt_data(self, key_name, plaintext, associated_data=b""):
        # type: (str, bytes, bytes) -> bytes
        return self._encrypt(key_name, plaintext, associated_data).to_bytes()

    def decrypt_data(self, key_name, ciphertext, associated_data=b""):
        # type: (str, bytes, bytes) -> bytes
        return self._decrypt(key_name, ciphertext, associated_data)

    def get_secret_value(self, secret_name):
        # type: (str) -> str
        return self.api.get_secret_value(self.cr.get_uam_creds(), self.cr.get_kfm_creds(), secret_name)

    def describe_user_items(self, item_types=None):
        # type: (list) -> GetUserItemsReplyObj
        req_types = ""
        if item_types is not None:
            req_types = ','.join(item_types)
        try:
            return self.api.get_user_items(self.cr.get_uam_creds(), item_types=req_types)
        except ApiException as e:
            if "NotFound" not in e.body:
                raise e
            return GetUserItemsReplyObj([])

    def _encrypt(self, key_name, plaintext, associated_data=b""):
        # type: (str, bytes, bytes) -> AkeylessCiphertext

        derivation_creds = self.key_ops_cache.get_key_derivation_creds(key_name)
        alg = CryptoAlgorithm.get_alg_by_name(derivation_creds.item_type)
        key_version = derivation_creds.item_version
        cf_id = derivation_creds.customer_fragment_id
        if cf_id:
            raise AkeylessSDKClientError(
                "keys with an associated customer fragment are not supported by the Akeyless Python SDK")

        num_of_fragments = len(derivation_creds.kf_ms_hosts_dns_map)
        dd_list = []
        dd = gen_derivation_data()
        for i in range(0, num_of_fragments):
            dd_list.append(dd)

        derived_key, final_dd = self.api.derive_key(derivation_creds,
                                                    self.cr.get_kfm_creds(),
                                                    dd_list,
                                                    alg.is_deterministic())
        return encrypt(alg, derived_key, key_version, final_dd, plaintext, associated_data)

    def _decrypt(self, key_name, ciphertext, associated_data=b""):
        # type: (str, bytes, bytes) -> bytes
        key_version = AkeylessCiphertext.extract_key_version_from_cipher(ciphertext)
        derivation_creds = self.key_ops_cache.get_key_derivation_creds(key_name, key_version)
        alg = CryptoAlgorithm.get_alg_by_name(derivation_creds.item_type)
        cf_id = derivation_creds.customer_fragment_id
        if cf_id:
            raise AkeylessSDKClientError(
                "keys with an associated customer fragment are not supported by the Akeyless Python SDK")

        akeyless_cipher = AkeylessCiphertext.deserialize(alg, ciphertext)

        derivation_creds = self.key_ops_cache.get_key_derivation_creds(key_name)
        num_of_fragments = len(derivation_creds.kf_ms_hosts_dns_map)

        derived_key, final_dd = self.api.derive_key(derivation_creds,
                                                    self.cr.get_kfm_creds(),
                                                    akeyless_cipher.get_derivations_data(num_of_fragments),
                                                    alg.is_deterministic())
        return decrypt(alg, derived_key, akeyless_cipher, associated_data)
