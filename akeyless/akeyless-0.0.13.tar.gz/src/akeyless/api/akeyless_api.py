import base64

from akeyless_auth_api.api_client import ApiClient as AuthApiClient
from akeyless_auth_api.configuration import Configuration as AuthApiConfiguration
from akeyless_auth_api import DefaultApi as AuthApi, SystemUserCredentialsReplyObj, SetUAMPolicyCredsParams, \
    CredentialsReplyObj, AuthStatusReplyObj

from akeyless_uam_api.api_client import ApiClient as UamApiClient
from akeyless_uam_api.configuration import Configuration as UamApiConfiguration
from akeyless_uam_api import DefaultApi as UamApi, DerivationCredsReplyObj, RSADecryptCredsReplyObj, \
    GetAccountDetailsReplyObj, GetItemReplyObj, GetUserItemsReplyObj, CreateUserReplyObj, GetUserReplyObj, \
    GetRoleReplyObj, SecretAccessCredsReplyObj, GetAccountRolesReplyObj, GetAccountUsersReplyObj, UAMStatusReplyObj

from akeyless_kfm_api.api_client import ApiClient as KfmApiClient
from akeyless_kfm_api.configuration import Configuration as KfmApiConfiguration
from akeyless_kfm_api import DefaultApi as KfmApi

from akeyless.api.base import AkeylessApiI
from akeyless.api.item_types import ItemType
from akeyless.config import AkeylessClientConfig
from akeyless.crypto import CryptoAlgorithm, encrypt, decrypt
from akeyless.crypto.utils import xor_fragments, AkeylessCiphertext


class AkeylessApi(AkeylessApiI):

    def __init__(self, config):
        # type: (AkeylessClientConfig) -> None
        super(AkeylessApi, self).__init__(config)

        self.config = config
        self._init_api_clients()

    def get_account_details(self, akeyless_uam_user_creds, **kwargs):
        # type: (str, dict) -> GetAccountDetailsReplyObj
        return self.uam_api.get_account_details(akeyless_uam_user_creds, **kwargs)

    def authenticate_uam_api_key_policy(self, policy_id, timestamp, nonce, signature, **kwargs):
        # type: (str, int, str, str, dict) -> SystemUserCredentialsReplyObj
        return self.auth_api.authenticate_uam(policy_id, timestamp=timestamp, nonce=nonce, signature=signature, **kwargs)

    def set_uam_policy_creds(self, akeyless_auth_creds, body, **kwargs):
        # type: (str, SetUAMPolicyCredsParams, dict) -> CredentialsReplyObj
        return self.auth_api.set_uam_policy_creds(akeyless_auth_creds, body, **kwargs)

    def get_item_derivation_creds(self, akeyless_uam_user_creds, item_name, **kwargs):
        # type: (str, str, dict) -> DerivationCredsReplyObj
        return self.uam_api.get_item_derivation_creds(akeyless_uam_user_creds, item_name, **kwargs)

    def get_rsa_key_decrypt_creds(self, akeyless_uam_user_creds, item_name, **kwargs):
        # type: (str, str, dict) -> RSADecryptCredsReplyObj
        return self.uam_api.get_rsa_key_decrypt_creds(akeyless_uam_user_creds, item_name, **kwargs)

    def get_upload_secret_creds(self, akeyless_uam_user_creds, secret_name, **kwargs):
        # type: (str, str, dict) -> DerivationCredsReplyObj
        return self.uam_api.get_upload_secret_creds(akeyless_uam_user_creds, secret_name, **kwargs)

    def get_secret_access_creds(self, akeyless_uam_user_creds, item_name, **kwargs):
        # type: (str, str, dict) -> SecretAccessCredsReplyObj
        return self.uam_api.get_secret_access_creds(akeyless_uam_user_creds, item_name, **kwargs)

    def derive_key(self, derivation_creds, kfm_user_creds, derivations_data, double_derivation=False):
        # type: (DerivationCredsReplyObj, str, list, bool) -> (bytes, list)
        return self._derive_key(derivation_creds, kfm_user_creds, derivations_data, double_derivation)

    def create_aes_key_item(self, akeyless_uam_user_creds, item_name, alg, user_metadata, split_level, **kwargs):
        # type: (str, str, CryptoAlgorithm, str, int, dict) -> None
        if not alg.is_aes():
            raise ValueError("Invalid algorithm")
        return self.uam_api.create_item(akeyless_uam_user_creds, item_name, alg.alg_name,
                                        user_metadata, split_level, **kwargs)

    def create_secret(self, akeyless_uam_user_creds, kfm_user_creds,
                      secret_name, secret_val, user_metadata, protected_key=""):
        # type: (str, str, str, str, str, str) -> None
        return self._create_secret(akeyless_uam_user_creds, kfm_user_creds, secret_name, secret_val,
                                   user_metadata, protected_key)

    def get_secret_value(self, akeyless_uam_user_creds, kfm_user_creds, secret_name):
        # type: (str, str, str) -> str
        return self._get_secret_value(akeyless_uam_user_creds, kfm_user_creds, secret_name)

    def update_secret_value(self, akeyless_uam_user_creds, kfm_user_creds, secret_name,
                            new_secret_val, protected_key=""):
        # type: (str, str, str, str, str) -> None
        return self._update_secret_value(akeyless_uam_user_creds, kfm_user_creds, secret_name,
                                         new_secret_val, protected_key)

    def get_item(self, akeyless_uam_user_creds, item_name, **kwargs):
        # type: (str, str, dict) -> GetItemReplyObj
        return self.uam_api.get_item(akeyless_uam_user_creds, item_name, **kwargs)

    def get_user_items(self, akeyless_uam_user_creds, **kwargs):
        # type: (str, dict) -> GetUserItemsReplyObj
        return self.uam_api.get_user_items(akeyless_uam_user_creds, **kwargs)

    def update_item(self, akeyless_uam_user_creds, new_item_name, item_name, **kwargs):
        # type: (str, str, str, dict) -> None
        return self.uam_api.update_item(akeyless_uam_user_creds, new_item_name, item_name, **kwargs)

    def delete_item(self, akeyless_uam_user_creds, item_name, **kwargs):
        # type: (str, str, dict) -> None
        return self.uam_api.delete_item(akeyless_uam_user_creds, item_name, **kwargs)

    def create_user(self, akeyless_uam_user_creds, akeyless_set_user_access_policy_creds, user_name, **kwargs):
        # type: (str, str, str, dict) -> CreateUserReplyObj
        return self.uam_api.create_user(akeyless_uam_user_creds, akeyless_set_user_access_policy_creds,
                                        user_name, **kwargs)

    def get_user(self, akeyless_uam_user_creds, user_name, **kwargs):
        # type: (str, str, dict) -> GetUserReplyObj
        return self.uam_api.get_user(akeyless_uam_user_creds, user_name, **kwargs)

    def get_account_users(self, akeyless_uam_user_creds, **kwargs):
        # type: (str, dict) -> GetAccountUsersReplyObj
        return self.uam_api.get_account_users(akeyless_uam_user_creds, **kwargs)

    def update_user(self, akeyless_uam_user_creds, akeyless_set_user_access_policy_creds,
                    new_user_name, user_name, **kwargs):
        # type: (str, str, str, str, dict) -> None
        return self.uam_api.update_user(akeyless_uam_user_creds, akeyless_set_user_access_policy_creds,
                                        new_user_name, user_name, **kwargs)

    def delete_user(self, akeyless_uam_user_creds, user_name, **kwargs):
        # type: (str, str, dict) -> None
        return self.uam_api.delete_user(akeyless_uam_user_creds, user_name, **kwargs)

    def create_role(self, akeyless_uam_user_creds, role_name, **kwargs):
        # type: (str, str, dict) -> None
        return self.uam_api.create_role(akeyless_uam_user_creds, role_name, **kwargs)

    def get_role(self, akeyless_uam_user_creds, role_name, **kwargs):
        # type: (str, str, dict) -> GetRoleReplyObj
        return self.uam_api.get_role(akeyless_uam_user_creds, role_name, **kwargs)

    def get_account_roles(self, akeyless_uam_user_creds, **kwargs):
        # type: (str, dict) -> GetAccountRolesReplyObj
        return self.uam_api.get_account_roles(akeyless_uam_user_creds, **kwargs)

    def update_role(self, akeyless_uam_user_creds, new_role_name, role_name, **kwargs):
        # type: (str, str, str, dict) -> None
        return self.uam_api.update_role(akeyless_uam_user_creds, new_role_name, role_name, **kwargs)

    def delete_role(self, akeyless_uam_user_creds, role_name, **kwargs):
        # type: (str, str, dict) -> None
        return self.uam_api.delete_role(akeyless_uam_user_creds, role_name, **kwargs)

    def create_role_item_assoc(self, akeyless_uam_user_creds, role_name, associated_name, **kwargs):
        # type: (str, str, str, dict) -> None
        return self.uam_api.create_role_item_assoc(akeyless_uam_user_creds, role_name, associated_name, **kwargs)

    def create_role_user_assoc(self, akeyless_uam_user_creds, role_name, associated_name, **kwargs):
        # type: (str, str, str, dict) -> None
        return self.uam_api.create_role_user_assoc(akeyless_uam_user_creds, role_name, associated_name, **kwargs)

    def delete_role_item_assoc(self, akeyless_uam_user_creds, role_name, associated_name, **kwargs):
        # type: (str, str, str, dict) -> None
        return self.uam_api.delete_role_item_assoc(akeyless_uam_user_creds, role_name, associated_name, **kwargs)

    def delete_role_user_assoc(self, akeyless_uam_user_creds, role_name, associated_name, **kwargs):
        # type: (str, str, str, dict) -> None
        return self.uam_api.delete_role_user_assoc(akeyless_uam_user_creds, role_name, associated_name, **kwargs)

    def close(self):
        # type: () -> None
        self.uam_api.api_client.rest_client.pool_manager.clear()
        self.uam_api.api_client.pool.close()
        self.uam_api.api_client.pool.join()

        self.auth_api.api_client.rest_client.pool_manager.clear()
        self.auth_api.api_client.pool.close()
        self.auth_api.api_client.pool.join()

        for kfm_api in self.kfm_api_map:
            self.kfm_api_map[kfm_api].api_client.rest_client.pool_manager.clear()
            self.kfm_api_map[kfm_api].api_client.pool.close()
            self.kfm_api_map[kfm_api].api_client.pool.join()

    def _init_api_clients(self):
        # type: () -> None
        api_conf = UamApiConfiguration()
        api_conf.host = self._get_uam_host
        api_client = UamApiClient(api_conf)
        api_client.set_default_header("Cache-Control", "no-cache, no-store, must-revalidate")
        api_client.set_default_header("Pragma", "no-cache")
        api_client.set_default_header("Expires", "0")
        api_client.set_default_header("AkeylessClientId", self._get_client_id)
        self.uam_api = UamApi(api_client)

        api_conf = AuthApiConfiguration()
        api_conf.host = self._get_auth_host
        api_client = AuthApiClient(api_conf)
        api_client.set_default_header("Cache-Control", "no-cache, no-store, must-revalidate")
        api_client.set_default_header("Pragma", "no-cache")
        api_client.set_default_header("Expires", "0")
        api_client.set_default_header("AkeylessClientId", self._get_client_id)
        self.auth_api = AuthApi(api_client)

        self.kfm_api_map = {}

    @property
    def _get_uam_host(self):
        # type: () -> str
        return self.config.protocol + "://" + self.config.uam_server_dns

    @property
    def _get_auth_host(self):
        # type: () -> str
        return self.config.protocol + "://" + \
               self.uam_api.get_status().auth_dns

    @property
    def _get_client_id(self):
        # type: () -> str
        return self.config.policy_id

    def _derive_key(self, derivation_creds, kfm_user_creds, derivations_data, double_derivation):
        # type: (DerivationCredsReplyObj, str, list, bool) -> (bytes, list)
        threads = []
        for i, val in derivation_creds.kf_ms_hosts_dns_map.items():
            kfm_api = self._get_kfm_api(val)
            dd = base64.b64encode(derivations_data[int(i)])
            threads.append(kfm_api.derive_fragment(kfm_user_creds, derivation_creds.credential, dd,
                                                   double_derivation=double_derivation, async=True))

        fragments = []
        derivations_data = []
        for t in threads:
            res = t.get()
            fragments.append(base64.b64decode(res.derived_fragment))
            derivations_data.append(base64.b64decode(res.derivation_data))

        return xor_fragments(fragments), derivations_data

    def _get_kfm_api(self, host):
        # type: (str) -> KfmApi

        if host in self.kfm_api_map:
            return self.kfm_api_map[host]

        api_conf = KfmApiConfiguration()
        api_conf.host = host
        api_client = KfmApiClient(api_conf)
        api_client.set_default_header("Cache-Control", "no-cache, no-store, must-revalidate")
        api_client.set_default_header("Pragma", "no-cache")
        api_client.set_default_header("Expires", "0")
        api_client.set_default_header("AkeylessClientId", self._get_client_id)
        self.kfm_api_map[host] = KfmApi(api_client)
        return self.kfm_api_map[host]

    def _create_secret(self, akeyless_uam_user_creds, kfm_user_creds, secret_name,
                       secret_val, user_metadata, protected_key=""):
        # type: (str, str, str, str, str, str) -> None
        enc_val_base64, upload_creds = self._encrypt_secret_value(akeyless_uam_user_creds, kfm_user_creds,
                                                                  secret_name, secret_val, protected_key)
        return self.uam_api.create_item(akeyless_uam_user_creds, secret_name,
                                        ItemType.USER_SECRET.name,
                                        user_metadata, 0,
                                        upload_secret_creds=upload_creds.credential,
                                        secret_enc_val=enc_val_base64)

    def _get_secret_value(self, akeyless_uam_user_creds, kfm_user_creds, secret_name):
        # type: (str, str, str) -> str
        access_creds = self.uam_api.get_secret_access_creds(akeyless_uam_user_creds,
                                                            secret_name)
        protected_key_derive_cres = DerivationCredsReplyObj(
            credential=access_creds.credential,
            expiry=access_creds.expiry,
            kf_ms_hosts_dns_map=access_creds.kf_ms_hosts_dns_map,
            restricted_dd=access_creds.restricted_dd,
            item_type=access_creds.protected_key_type,
            item_size=CryptoAlgorithm.get_alg_by_name(access_creds.protected_key_type).key_len,

        )

        num_of_fragments = len(access_creds.kf_ms_hosts_dns_map)
        dd_list = []
        dd = base64.b64decode(access_creds.restricted_dd)
        for i in range(0, num_of_fragments):
            dd_list.append(dd)

        derived_protected_key, _ = self.derive_key(protected_key_derive_cres, kfm_user_creds, dd_list)
        alg = CryptoAlgorithm.get_alg_by_name(access_creds.protected_key_type)
        cipher = AkeylessCiphertext.deserialize(alg, base64.b64decode(access_creds.secret_enc_val))
        return decrypt(alg, derived_protected_key, cipher).decode("utf-8")

    def _update_secret_value(self, akeyless_uam_user_creds, kfm_user_creds, secret_name,
                             new_secret_val, protected_key=""):
        # type: (str, str, str, str, str) -> None
        enc_val_base64, upload_creds = self._encrypt_secret_value(akeyless_uam_user_creds, kfm_user_creds, secret_name,
                                                                  new_secret_val, protected_key)
        return self.uam_api.update_item(akeyless_uam_user_creds,
                                        secret_name, secret_name,
                                        upload_secret_creds=upload_creds.credential,
                                        secret_enc_val=enc_val_base64)

    def _encrypt_secret_value(self, akeyless_uam_user_creds, kfm_user_creds, secret_name,
                              secret_val, protected_key=""):
        # type: (str, str, str, str, str) -> (str, DerivationCredsReplyObj)
        upload_creds = self.uam_api.get_upload_secret_creds(akeyless_uam_user_creds,
                                                            secret_name,
                                                            protected_key_name=protected_key)

        num_of_fragments = len(upload_creds.kf_ms_hosts_dns_map)
        dd_list = []
        dd = base64.b64decode(upload_creds.restricted_dd)
        for i in range(0, num_of_fragments):
            dd_list.append(dd)

        derived_protected_key, final_dd = self.derive_key(upload_creds, kfm_user_creds, dd_list)
        alg = CryptoAlgorithm.get_alg_by_name(upload_creds.item_type)
        key_version = upload_creds.item_version
        encrypt_secret = encrypt(alg, derived_protected_key, key_version, final_dd, str.encode(secret_val))
        return base64.b64encode(encrypt_secret.to_bytes()), upload_creds
