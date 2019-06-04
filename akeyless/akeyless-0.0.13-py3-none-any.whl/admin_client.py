import base64

import ecdsa
from hashlib import sha256

from akeyless_auth_api import SetUAMPolicyCredsParams
from akeyless_uam_api import GetAccountDetailsReplyObj, PolicyRules, GetRoleReplyObj, GetUserReplyObj, \
    GetAccountUsersReplyObj, GetAccountRolesReplyObj, GetUserItemsReplyObj
from akeyless_uam_api.rest import ApiException

from akeyless.admin_client_base import AkeylessAdminUserI
from akeyless.config import AkeylessClientConfig
from akeyless.crypto import CryptoAlgorithm
from akeyless.client import AkeylessClient
from akeyless.utils import UserAccessApi
from akeyless.utils.structures import ApiKey


class AkeylessAdminClient(AkeylessAdminUserI, AkeylessClient):

    def __init__(self, config):
        # type: (AkeylessClientConfig) -> None
        super(AkeylessAdminClient, self).__init__(config)

    def get_account_details(self):
        # type: () -> GetAccountDetailsReplyObj
        return self.api.get_account_details(self.cr.get_uam_creds())

    def create_aes_key(self, key_name, alg, metadata, split_level):
        # type: (str, CryptoAlgorithm, str, int) -> None
        return self.api.create_aes_key_item(self.cr.get_uam_creds(), key_name, alg, metadata, split_level)

    def update_key(self, key_name, new_key_name, metadata):
        # type: (str, str, str) -> None
        return self.api.update_item(self.cr.get_uam_creds(), new_key_name, key_name, user_metadata=metadata)

    def create_secret(self, secret_name, secret_val, user_metadata, protected_key=""):
        # type: (str, str, str, str) -> None
        return self.api.create_secret(self.cr.get_uam_creds(), self.cr.get_kfm_creds(), secret_name, secret_val,
                                      user_metadata, protected_key)

    def update_secret(self, secret_name, new_secret_name, metadata):
        # type: (str, str, str) -> None
        return self.api.update_item(self.cr.get_uam_creds(), new_secret_name, secret_name, user_metadata=metadata)

    def update_secret_value(self, secret_name, new_secret_val, protected_key=""):
        # type: (str, str, str) -> None
        return self.api.update_secret_value(self.cr.get_uam_creds(), self.cr.get_kfm_creds(),
                                            secret_name, new_secret_val, protected_key)

    def delete_item(self, item_name):
        # type: (str) -> None
        return self.api.delete_item(self.cr.get_uam_creds(), item_name)

    def describe_account_items(self, item_types=None):
        # type: (list) -> GetUserItemsReplyObj
        return self.describe_user_items(item_types)

    def create_user(self, user_name, expires=0, cidr_whitelist=None):
        # type: (str, int, list) -> UserAccessApi
        api_key = ecdsa.SigningKey.generate(curve=ecdsa.NIST256p, hashfunc=sha256)
        pub_key_der = api_key.get_verifying_key().to_der()
        pub_key_encoded = base64.b64encode(pub_key_der).decode()
        cidr_str = ""
        if cidr_whitelist is not None:
            cidr_str = ','.join(cidr_whitelist)

        rules = PolicyRules(alg="ECDSA_P256_SHA256", cidr_whitelist=cidr_str, key=pub_key_encoded)
        policy_params = SetUAMPolicyCredsParams(expires, "api_key", rules, None)

        set_policy_creds = self.api.set_uam_policy_creds(self.cr.get_auth_creds(), policy_params)
        res = self.api.create_user(self.cr.get_uam_creds(), set_policy_creds.credential, user_name)

        return UserAccessApi(user_name, res.user_policy_id, api_key)

    def get_user(self, user_name):
        # type: (str) -> GetUserReplyObj
        return self.api.get_user(self.cr.get_uam_creds(), user_name)

    def get_account_users(self):
        # type: () -> GetAccountUsersReplyObj
        try:
            return self.api.get_account_users(self.cr.get_uam_creds())
        except ApiException as e:
            if "NotFound" not in e.body:
                raise e
            return GetAccountUsersReplyObj([])

    def update_user_name(self, user_name, new_user_name):
        # type: (str, str) -> None
        policy_params = SetUAMPolicyCredsParams(None, None, None, None)
        set_policy_creds = self.api.set_uam_policy_creds(self.cr.get_auth_creds(), policy_params)
        return self.api.update_user(self.cr.get_uam_creds(), set_policy_creds.credential, new_user_name, user_name)

    def update_user_access_expires(self, user_name, expires):
        # type: (str, int) -> None

        update_modes = ["update_exp"]
        policy_params = SetUAMPolicyCredsParams(expires, None, None, update_modes)
        set_policy_creds = self.api.set_uam_policy_creds(self.cr.get_auth_creds(), policy_params)
        return self.api.update_user(self.cr.get_uam_creds(), set_policy_creds.credential, user_name, user_name)

    def update_user_cidr_whitelist(self, user_name, cidr_whitelist=None):
        # type: (str, list) -> None

        cidr_str = ""
        if cidr_whitelist is not None:
            cidr_str = ','.join(cidr_whitelist)

        update_modes = ["update_cidr"]
        rules = PolicyRules(cidr_whitelist=cidr_str)
        policy_params = SetUAMPolicyCredsParams(None, None, rules, update_modes)
        set_policy_creds = self.api.set_uam_policy_creds(self.cr.get_auth_creds(), policy_params)
        return self.api.update_user(self.cr.get_uam_creds(), set_policy_creds.credential, user_name, user_name)

    def update_user(self, user_name, new_user_name, expires=None, cidr_whitelist=None):
        # type: (str, str, int, list) -> None

        cidr_str = ""
        if cidr_whitelist is not None:
            cidr_str = ','.join(cidr_whitelist)

        update_modes = ["update_exp", "update_cidr"]
        rules =  PolicyRules(cidr_whitelist=cidr_str)
        policy_params = SetUAMPolicyCredsParams(expires, None, rules, update_modes)
        set_policy_creds = self.api.set_uam_policy_creds(self.cr.get_auth_creds(), policy_params)
        return self.api.update_user(self.cr.get_uam_creds(), set_policy_creds.credential, new_user_name, user_name)

    def reset_user_access_key(self, user_name):
        # type: (str) -> ApiKey
        api_key = ecdsa.SigningKey.generate(curve=ecdsa.NIST256p, hashfunc=sha256)
        pub_key_der = api_key.get_verifying_key().to_der()
        pub_key_encoded = base64.b64encode(pub_key_der).decode()

        rules = PolicyRules(alg="ECDSA_P256_SHA256", key=pub_key_encoded)
        policy_params = SetUAMPolicyCredsParams(None, "api_key", rules, ["update_key"])

        set_policy_creds = self.api.set_uam_policy_creds(self.cr.get_auth_creds(), policy_params)
        self.api.update_user(self.cr.get_uam_creds(), set_policy_creds.credential, user_name, user_name)

        return ApiKey(api_key)

    def delete_user(self, user_name):
        # type: (str) -> None
        return self.api.delete_user(self.cr.get_uam_creds(), user_name)

    def create_role(self, role_name, role_action="", comment=""):
        # type: (str, str, str) -> None
        return self.api.create_role(self.cr.get_uam_creds(), role_name, role_action=role_action, comment=comment)

    def get_role(self, role_name):
        # type: (str) -> GetRoleReplyObj
        return self.api.get_role(self.cr.get_uam_creds(), role_name)

    def get_account_roles(self):
        # type: () -> GetAccountRolesReplyObj
        try:
            return self.api.get_account_roles(self.cr.get_uam_creds())
        except ApiException as e:
            if "NotFound" not in e.body:
                raise e
            return GetAccountRolesReplyObj([])

    def update_role(self, role_name, new_role_name, role_action="", comment=""):
        # type: (str, str, str, str) -> None
        return self.api.update_role(self.cr.get_uam_creds(), new_role_name, role_name,
                                    role_action=role_action, comment=comment)

    def delete_role(self, role_name):
        # type: (str) -> None
        return self.api.delete_role(self.cr.get_uam_creds(), role_name)

    def create_role_item_assoc(self, role_name, associated_name):
        # type: (str, str) -> None
        return self.api.create_role_item_assoc(self.cr.get_uam_creds(), role_name, associated_name)

    def create_role_user_assoc(self, role_name, associated_name):
        # type: (str, str) -> None
        return self.api.create_role_user_assoc(self.cr.get_uam_creds(), role_name, associated_name)

    def delete_role_item_assoc(self, role_name, associated_name):
        # type: (str, str) -> None
        return self.api.delete_role_item_assoc(self.cr.get_uam_creds(), role_name, associated_name)

    def delete_role_user_assoc(self, role_name, associated_name):
        # type: (str, str) -> None
        return self.api.delete_role_user_assoc(self.cr.get_uam_creds(), role_name, associated_name)
