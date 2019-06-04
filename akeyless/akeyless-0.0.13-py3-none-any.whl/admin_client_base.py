import abc

import six
from akeyless_uam_api import GetAccountDetailsReplyObj, GetUserReplyObj, GetRoleReplyObj, \
    GetAccountRolesReplyObj, GetAccountUsersReplyObj, GetUserItemsReplyObj

from akeyless.config import AkeylessClientConfig
from akeyless.crypto import CryptoAlgorithm
from akeyless.client_base import AkeylessClientI
from akeyless.utils import UserAccessApi
from akeyless.utils.structures import ApiKey


@six.add_metaclass(abc.ABCMeta)
class AkeylessAdminUserI(AkeylessClientI):

    def __init__(self, config):
        # type: (AkeylessClientConfig) -> None
        super(AkeylessAdminUserI, self).__init__(config)

    @abc.abstractmethod
    def get_account_details(self):
        # type: () -> GetAccountDetailsReplyObj
        """Get account details.

        This endpoint is accessible only by the account admin user

        :return: The account details
        :rtype: GetAccountDetailsReplyObj
        """

    @abc.abstractmethod
    def create_aes_key(self, key_name, alg, metadata, split_level):
        # type: (str, CryptoAlgorithm, str, int) -> None
        """Creates a new AES key.

        This endpoint is accessible only by the account admin user

        :param str key_name: The key name to be created (required)
        :param CryptoAlgorithm alg: The algorithm for the key to be created. Types available are: [AES128GCM,
                                    AES256GCM, AES128SIV, AES256SIV] (required)
        :param str metadata: Metadata about the key. (required)
        :param int split_level: The splitting level represent the number of fragments that the key will be
                                split into. (required)
        """

    @abc.abstractmethod
    def update_key(self, key_name, new_key_name, metadata):
        # type: (str, str, str) -> None
        """Updating name and metadata of an existing key in the account

        This endpoint is accessible only by the account admin user

        :param str key_name: Key name. (required)
        :param str new_key_name: The new key name that will replace the existing one (required)
        :param str metadata: Metadata about the key.
        """
    @abc.abstractmethod
    def create_secret(self, secret_name, secret_val, metadata, protected_key=None):
        # type: (str, str, str, str) -> None
        """Creates a new secret.

        This endpoint is accessible only by the account admin user

        :param str secret_name: The secret name to be created (required)
        :param str secret_val: The value of the secret to be created (required)
        :param str metadata: Metadata about the secret. (required)
        :param str protected_key: The name of a key that used to encrypt the secret value (if empty, the account default
                                  protected key will be used)
        """

    @abc.abstractmethod
    def update_secret(self, secret_name, new_secret_name, metadata):
        # type: (str, str, str) -> None
        """Updating name and metadata of an existing secret in the account

        This endpoint is accessible only by the account admin user

        :param str secret_name: Secret name. (required)
        :param str new_secret_name: The new secret name that will replace the existing one (required)
        :param str metadata: Metadata about the secret.
        """

    @abc.abstractmethod
    def update_secret_value(self, secret_name, new_secret_val, protected_key=""):
        # type: (str, str, str) -> None
        """Update secret value.

        This endpoint is accessible only by the account admin user

        :param str secret_name: The secret name to be created (required)
        :param str new_secret_val: The new value of the secret to be updated (required)
        :param str protected_key: The name of a key that used to encrypt the secret value (if empty, the account default
                                  protected key will be used)
        """

    @abc.abstractmethod
    def delete_item(self, item_name):
        # type: (str) -> None
        """Deleting an existing item (key or secret) from the account

        This endpoint is accessible only by the account admin user

        :param str item_name: The name of the item (key or secret) to be deleted. (required)
        """

    @abc.abstractmethod
    def describe_account_items(self, item_types):
        # type: (list) -> GetUserItemsReplyObj
        """Return a list of all the keys and secrets in the account.

        :param list item_types: A list with the type names of the items requested. In case it is None or empty, all
                                the items will be returned.
        :return: A list of all the keys and secrets in the account.
        :rtype: GetUserItemsReplyObj
        """

    @abc.abstractmethod
    def create_user(self, user_name, expires=0, cidr_whitelist=None):
        # type: (str, int, list) -> UserAccessApi
        """Add a new user to the account.

        This endpoint is accessible only by the account admin user

        :param str user_name: The user name to be created (required)
        :param int expires: User access expiration date in Unix timestamp. In case of 0 or null the user
                            access will not be limited in time.
        :param list cidr_whitelist: An CIDR Whitelisting. Only requests from the ip addresses that match the CIDR
                                    list will be able to obtain temporary access credentials. The list length is
                                    limited to 10 CIDRs. In the case of None or an empty string there will be no
                                    restriction of IP addresses.
        :return: An object that contains the user name, policy id and access key
        :rtype: UserAccessApi
        """

    @abc.abstractmethod
    def get_user(self, user_name):
        # type: (str) -> GetUserReplyObj
        """Get user details.

        This endpoint is accessible only by the account admin user

        :param str user_name: User name. (required)
        :return: The user details
        :rtype: GetUserReplyObj
        """

    @abc.abstractmethod
    def get_account_users(self):
        # type: () -> GetAccountUsersReplyObj
        """Get All the existing users in the account.

        This endpoint is accessible only by the account admin user

        :return: A list of all the existing users in the account.
        :rtype: GetAccountUsersReplyObj
        """

    @abc.abstractmethod
    def update_user_name(self, user_name, new_user_name):
        # type: (str, str) -> None
        """Updating username

        This endpoint is accessible only by the account admin user

        :param str user_name: User name. (required)
        :param str new_user_name: The new username that will replace the existing one (required)
        """

    @abc.abstractmethod
    def update_user_access_expires(self, user_name, expires):
        # type: (str, int) -> None
        """Updating user access expiration date

        This endpoint is accessible only by the account admin user

        :param str user_name: User name. (required)
        :param int expires: User access expiration date in Unix timestamp. In case of 0 or null the user access will
                            not be limited in time.
        """

    @abc.abstractmethod
    def update_user_cidr_whitelist(self, user_name, cidr_whitelist=None):
        # type: (str , list) -> None
        """Updating user CIDR whitelist

        This endpoint is accessible only by the account admin user

        :param str user_name: User name. (required)
        :param list cidr_whitelist: An CIDR Whitelisting. Only requests from the ip addresses that match the CIDR
                                    list will be able to obtain temporary access credentials. The list length is
                                    limited to 10 CIDRs. In the case of None or an empty string there will be no
                                    restriction of IP addresses
        """

    @abc.abstractmethod
    def update_user(self, user_name, new_user_name, expires=0, cidr_whitelist=None):
        # type: (str, str, int , list) -> None
        """Updating user parameters

        This endpoint is accessible only by the account admin user

        :param str user_name: User name. (required)
        :param str new_user_name: The new username that will replace the existing one (required)
        :param int expires: User access expiration date in Unix timestamp. In case of 0 or null the user access will
                            not be limited in time.
        :param list cidr_whitelist: An CIDR Whitelisting. Only requests from the ip addresses that match the CIDR
                                    list will be able to obtain temporary access credentials. The list length is
                                    limited to 10 CIDRs. In the case of None or an empty string there will be no
                                    restriction of IP addresses
        """

    @abc.abstractmethod
    def reset_user_access_key(self, user_name):
        # type: (str) -> ApiKey
        """Replacing the user's access API key

        This endpoint is accessible only by the account admin user

        :param str user_name: User name. (required)
        :return: The new user access key
        :rtype: ApiKey
        """

    @abc.abstractmethod
    def delete_user(self, user_name):
        # type: (str) -> None
        """Deleting an existing user from the account.

        This endpoint is accessible only by the account admin user

        :param str user_name: User name. (required)
        """

    @abc.abstractmethod
    def create_role(self, role_name, role_action="", comment=""):
        # type: (str, str, str) -> None
        """Add a new role to the account.

        This endpoint is accessible only by the account admin user

        :param str role_name: The role name to be created (required)
        :param str role_action: The role action.
        :param str comment: Comments
        """

    @abc.abstractmethod
    def get_role(self, role_name):
        # type: (str) -> GetRoleReplyObj
        """Get role details.

        This endpoint is accessible only by the account admin user

        :param str role_name: Role name. (required)
        :return: The role details
        :rtype: GetRoleReplyObj
        """

    @abc.abstractmethod
    def get_account_roles(self):
        # type: () -> GetAccountRolesReplyObj
        """Get All the existing roles in the account.

        This endpoint is accessible only by the account admin user

        :return: A list of all the existing roles in the account.
        :rtype: GetAccountRolesReplyObj
        """

    @abc.abstractmethod
    def update_role(self, role_name, new_role_name, role_action="", comment=""):
        # type: (str, str, str, str) -> None
        """Updating an existing role in the account

        This endpoint is accessible only by the account admin user

        :param str role_name: Role name. (required)
        :param str new_role_name: The new role name that will replace the existing one (required)
        :param str role_action: The role action.
        :param str comment: Comments
        """

    @abc.abstractmethod
    def delete_role(self, role_name):
        # type: (str) -> None
        """Deleting an existing role from the account.

        This endpoint is accessible only by the account admin role

        :param str role_name: Role name. (required)
        """

    @abc.abstractmethod
    def create_role_item_assoc(self, role_name, associated_name):
        # type: (str, str) -> None
        """Add an association between a role and an item.

        This endpoint is accessible only by the account admin user

        :param str role_name: The role name to be associated (required)
        :param str associated_name: The item or user name to be associated. (required)
        """

    @abc.abstractmethod
    def create_role_user_assoc(self, role_name, associated_name):
        # type: (str, str) -> None
        """Add an association between a role and a user.

        This endpoint is accessible only by the account admin user

        :param str role_name: The role name to be associated (required)
        :param str associated_name: The item or user name to be associated. (required)
        """

    @abc.abstractmethod
    def delete_role_item_assoc(self, role_name, associated_name):
        # type: (str, str) -> None
        """Deleting an association between a role and an item.

        This endpoint is accessible only by the account admin role

        :param str role_name: The role name to be associated (required)
        :param str associated_name: The item or user name to be associated. (required)
        """

    @abc.abstractmethod
    def delete_role_user_assoc(self, role_name, associated_name):
        # type: (str, str) -> None
        """Deleting an association between a role and an user.

        This endpoint is accessible only by the account admin role

        :param str role_name: The role name to be associated (required)
        :param str associated_name: The item or user name to be associated. (required)
        """