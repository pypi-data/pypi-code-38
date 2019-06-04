import abc
import six
from akeyless_auth_api import SystemUserCredentialsReplyObj, SetUAMPolicyCredsParams, CredentialsReplyObj
from akeyless_uam_api import DerivationCredsReplyObj, RSADecryptCredsReplyObj, GetAccountDetailsReplyObj, \
    GetItemReplyObj, GetUserItemsReplyObj, CreateUserReplyObj, GetUserReplyObj, GetRoleReplyObj, \
    SecretAccessCredsReplyObj

from akeyless.config import AkeylessClientConfig
from akeyless.crypto import CryptoAlgorithm


@six.add_metaclass(abc.ABCMeta)
class AkeylessApiI(object):
    """Parent interface for Akeyless API."""

    def __init__(self, config):
        # type: (AkeylessClientConfig) -> None
        self.config = config

    @abc.abstractmethod
    def get_account_details(self, akeyless_uam_user_creds, **kwargs):
        # type: (str, dict) -> GetAccountDetailsReplyObj
        """Get account details.

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.get_account_details(akeyless_uam_user_creds, async=True)
        >>> result = thread.get()

        :param async bool
        :param str akeyless_uam_user_creds: Temporary credentials for accessing the endpoint (required)
        :return: GetAccountDetailsReplyObj
                 If the method is called asynchronously,
                 returns the request thread.
        """

    @abc.abstractmethod
    def authenticate_uam_api_key_policy(self, policy_id, timestamp, nonce, signature, **kwargs):
        # type: (str, int, str, str, dict) -> SystemUserCredentialsReplyObj
        """Return a combination of three temporary credentials for accessing Auth, UAM and KFMs instances.

        System's user that meet an API key access policy will be able to get a combination of three
        temporary credentials signed by Auth for accessing Auth, UAM and KFMs instances. The client
        must provide a signature that proves his compliance with the policy.
        In this case the IP address used for authentication will be taken from the http request.
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.authenticate_uam_api_key_policy(policy_id, timestamp, nonce, signature, async=True)
        >>> result = thread.get()

        :param async bool
        :param str policy_id: Policy id. (required)
        :param int timestamp: A Unix timestamp which was used for the signature. (required)
        :param str nonce: Random string which was used for the signature. (required)
        :param str signature: A digital signature generated with the private key that complies with the access policy. (required)
        :param str client_ip: The Client's IP for authentication. Relevant only to the services that mediate between Auth and their clients in obtaining temporary access credentials.
        :param int creds_expiry: The requested expiration time of the temporary credentials in minutes.
        :return: SystemUserCredentialsReplyObj
                 If the method is called asynchronously,
                 returns the request thread.
        """

    @abc.abstractmethod
    def get_item_derivation_creds(self, akeyless_uam_user_creds, item_name, **kwargs):
        # type: (str, str, dict) -> DerivationCredsReplyObj
        """Get temporary access credentials to KFM instances for item&#39;s fragments derivation.

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.get_item_derivation_creds(akeyless_uam_user_creds, item_name, async=True)
        >>> result = thread.get()

        :param async bool
        :param str akeyless_uam_user_creds: Temporary credentials for accessing the endpoint (required)
        :param str item_name: The item name for derivation (required)
        :param int item_version: The item version. If it is empty, the derivation credentials will be returned for the latest item version
        :param str restricted_derivation_data: In case not empty, the derivation credentials will be restricted only to this derivation data
        :param int creds_expiry: The requested expiration time of the temporary credentials in minutes.
        :return: DerivationCredsReplyObj
                 If the method is called asynchronously,
                 returns the request thread.
        """

    @abc.abstractmethod
    def get_rsa_key_decrypt_creds(self, akeyless_uam_user_creds, item_name, **kwargs):
        # type: (str, str, dict) -> RSADecryptCredsReplyObj
        """Get temporary access credentials to KFM instances for RSA key fragments decryption.

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.get_rsa_key_decrypt_creds(akeyless_uam_user_creds, item_name, async=True)
        >>> result = thread.get()

        :param async bool
        :param str akeyless_uam_user_creds: Temporary credentials for accessing the endpoint (required)
        :param str item_name: The item name for decrypt operation (required)
        :param int item_version: The item version. If it is empty, the RSA decrypt credentials will be
                                 returned for the latest item version.
        :param str restricted_cipher: In case not empty, the RSA decrypt credentials will be restricted
                                      only to this cipher.
        :param int creds_expiry: The requested expiration time of the temporary credentials in minutes.
        :return: RSADecryptCredsReplyObj
                 If the method is called asynchronously,
                 returns the request thread.
        """

    @abc.abstractmethod
    def get_upload_secret_creds(self, akeyless_uam_user_creds, secret_name, **kwargs):
        # type: (str, str, dict) -> DerivationCredsReplyObj
        """Get temporary access credentials to KFM instances to produce the derived protected key of the secret.

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.get_upload_secret_creds(akeyless_uam_user_creds, secret_name, async=True)
        >>> result = thread.get()

        :param async bool
        :param str akeyless_uam_user_creds: Temporary credentials for accessing the endpoint (required)
        :param str secret_name: The secret name. (required)
        :param str protected_key_name: The name of the key that will be used to encrypt the secret. If not provided, the account default secret key will be used.
        :param int creds_expiry: The requested expiration time of the temporary credentials in minutes.
        :return: DerivationCredsReplyObj
                 If the method is called asynchronously,
                 returns the request thread.
        """

    @abc.abstractmethod
    def get_secret_access_creds(self, akeyless_uam_user_creds, item_name, **kwargs):
        # type: (str, str, dict) -> SecretAccessCredsReplyObj
        """get_secret_access_creds

        Get temporary access credentials to KFM instances for secret protected key derivation and the encrypted secret value.
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.get_secret_access_creds(akeyless_uam_user_creds, item_name, async=True)
        >>> result = thread.get()

        :param async bool
        :param str akeyless_uam_user_creds: Temporary credentials for accessing the endpoint (required)
        :param str item_name: The secret item name (required)
        :param int item_version: The secret item version. If it is empty, the credentials will be returned for the latest secret item version
        :param int creds_expiry: The requested expiration time of the temporary credentials in minutes.
        :return: SecretAccessCredsReplyObj
                 If the method is called asynchronously,
                 returns the request thread.
        """

    @abc.abstractmethod
    def set_uam_policy_creds(self, akeyless_auth_creds, body, **kwargs):
        # type: (str, SetUAMPolicyCredsParams, dict) -> CredentialsReplyObj
        """Getting temporary access credentials to add a new access policy or to update an existing access policy in
        an UAM account. The UAM service will use this credentials to create/update an access policy to be used for
        accessing key fragments.

        This endpoint is accessible only by services that have a permission to access Auth for managing their
        policies for their clients.

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.set_uam_policy_creds(akeyless_auth_creds, body, async=True)
        >>> result = thread.get()

        :param async bool
        :param str akeyless_auth_creds: Temporary credentials for accessing the endpoint (required)
        :param SetUAMPolicyCredsParams body: Policy params. (required)
        :return: CredentialsReplyObj
                 If the method is called asynchronously,
                 returns the request thread.
        """

    @abc.abstractmethod
    def derive_key(self, derivation_creds, kfm_user_creds, derivations_data, double_derivation=False):
        # type: (DerivationCredsReplyObj, str, list, bool) -> (bytes, list)
        """Returns a derived fragment from the origin fragment via the supplied derivation data.

        :param DerivationCredsReplyObj Temporary credentials for the fragment derivation operation. (required)
        :param str kfm_user_creds: Temporary credentials for accessing the KFM endpoints. (required)
        :param list derivations_data: The derivation data to be used for the fragment derivation operation. (required)
        :param str double_derivation: Indicate if perform a double derivation.
        :return: The derived key and a list of the final derivations data (in case of double derivation the final
                 derivations data list will be different from the origin derivations data list).
        :rtype: bytes, list
        """

    @abc.abstractmethod
    def create_aes_key_item(self, akeyless_uam_user_creds, item_name, alg, user_metadata, split_level, **kwargs):
        # type: (str, str, CryptoAlgorithm, str, int, dict) -> None
        """Creates a new AES key.

        This endpoint is accessible only by the account admin user
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.create_aes_key_item(akeyless_uam_user_creds, item_name, alg, user_metadata, split_level, async=True)
        >>> result = thread.get()

        :param async bool
        :param str akeyless_uam_user_creds: Temporary credentials for accessing the endpoint (required)
        :param str item_name: The item name to be created (required)
        :param CryptoAlgorithm alg: The type of the item to be created Types available are: [AES128GCM, AES256GCM, AES128SIV, AES256SIV] (required)
        :param str user_metadata: User metadata about the item. (required)
        :param int split_level: The splitting level represent the number of fragments that the item will be split into. (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

    @abc.abstractmethod
    def create_secret(self, akeyless_uam_user_creds, kfm_user_creds, secret_name, secret_val, user_metadata, protected_key=None):
        # type: (str, str, str, str, str, str) -> None
        """Creates a new secret.

        This endpoint is accessible only by the account admin user

        :param str akeyless_uam_user_creds: Temporary credentials for accessing the endpoint (required)
        :param str kfm_user_creds: Temporary credentials for accessing the KFM endpoints. (required)
        :param str secret_name: The secret name to be created (required)
        :param str secret_val: The value of the secret to be created (required)
        :param str user_metadata: User metadata about the secret. (required)
        :param str protected_key: The name of a key that used to encrypt the secret value (if empty, the account default
                                  protected key will be used)
        """

    @abc.abstractmethod
    def get_secret_value(self, akeyless_uam_user_creds, kfm_user_creds, secret_name):
        # type: (str, str, str) -> str
        """return secret value.

        This endpoint is accessible only by the account admin user

        :param str akeyless_uam_user_creds: Temporary credentials for accessing the endpoint (required)
        :param str kfm_user_creds: Temporary credentials for accessing the KFM endpoints. (required)
        :param str secret_name: The secret name (required)
        :return: The secret value in plaintext
        :rtype: srt
        """

    @abc.abstractmethod
    def update_secret_value(self, akeyless_uam_user_creds, kfm_user_creds, secret_name,
                            new_secret_val, protected_key=""):
        # type: (str, str, str, str, str) -> None
        """Update secret value.

        This endpoint is accessible only by the account admin user

        :param str akeyless_uam_user_creds: Temporary credentials for accessing the endpoint (required)
        :param str kfm_user_creds: Temporary credentials for accessing the KFM endpoints. (required)
        :param str secret_name: The secret name to be created (required)
        :param str new_secret_val: The new value of the secret to be updated (required)
        :param str protected_key: The name of a key that used to encrypt the secret value (if empty, the account default
                                  protected key will be used)
        """

    @abc.abstractmethod
    def get_item(self, akeyless_uam_user_creds, item_name, **kwargs):
        # type: (str, str, dict) -> GetItemReplyObj
        """Get item details.

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.get_item(akeyless_uam_user_creds, item_name, async=True)
        >>> result = thread.get()

        :param async bool
        :param str akeyless_uam_user_creds: Temporary credentials for accessing the endpoint (required)
        :param str item_name: Item name. (required)
        :param int item_version: The item version (for item attributes that are unique to each version). If it is
                                 empty, the item attributes of the latest version will be returned.
        :return: GetItemReplyObj
                 If the method is called asynchronously,
                 returns the request thread.
        """

    @abc.abstractmethod
    def get_user_items(self, akeyless_uam_user_creds, **kwargs):
        # type: (str, dict) -> GetUserItemsReplyObj
        """Get All the items associated with the user.

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.get_user_items(akeyless_uam_user_creds, async=True)
        >>> result = thread.get()

        :param async bool
        :param str akeyless_uam_user_creds: Temporary credentials for accessing the endpoint (required)
        :param str item_types: The item types list of the requested items . In case it is empty, all types of items
                               will be returned. The format of the item types list is a comma-separated list of a
                               valid item types. Valid opinions are -
                               \"AES128GCM,AES256GCM,AES128SIV,AES256SIV,RSA1024,RSA2048,USER_SECRET\"
        :return: GetUserItemsReplyObj
                 If the method is called asynchronously,
                 returns the request thread.
        """

    @abc.abstractmethod
    def update_item(self, akeyless_uam_user_creds, new_item_name, item_name, **kwargs):
        # type: (str, str, str, dict) -> None
        """Updating an existing item in the account

        This endpoint is accessible only by the account admin user
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.update_item(akeyless_uam_user_creds, new_item_name, item_name, async=True)
        >>> result = thread.get()

        :param async bool
        :param str akeyless_uam_user_creds: Temporary credentials for accessing the endpoint (required)
        :param str new_item_name: The new item name that will replace the existing one (required)
        :param str item_name: Item name. (required)
        :param str user_metadata: User metadata about the item.
        :param int item_version: The item version to be updated.
                                 This parameter relevant only when updating a version-dependent attribute of the item
                                 (for example a secret encrypted value in case of secret item).  If it is empty, the
                                 item attributes of the latest version will be updated.
        :param str upload_secret_creds: The credentials to upload a secret.
                                        This parameter relevant only when updating a secret. this parameter will be
                                        used to extract the protected key and the derivation data that used to encrypt
                                        the secret.
        :param str secret_enc_val: The encrypted secret value.
                                   This parameter relevant only when updating a secret. This parameter should contain
                                   the encrypted secret that is encrypted using the protected key.
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

    @abc.abstractmethod
    def delete_item(self, akeyless_uam_user_creds, item_name, **kwargs):
        # type: (str, str, dict) -> None
        """Deleting an existing item from the account

        This endpoint is accessible only by the account admin user
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.delete_item(akeyless_uam_user_creds, item_name, async=True)
        >>> result = thread.get()

        :param async bool
        :param str akeyless_uam_user_creds: Temporary credentials for accessing the endpoint (required)
        :param str item_name: Item name. (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

    @abc.abstractmethod
    def create_user(self, akeyless_uam_user_creds, akeyless_set_user_access_policy_creds, user_name, **kwargs):
        # type: (str, str, str, dict) -> CreateUserReplyObj
        """Add a new user to the account.

        This endpoint is accessible only by the account admin user
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.create_user(akeyless_uam_user_creds, akeyless_set_user_access_policy_creds, user_name, async=True)
        >>> result = thread.get()

        :param async bool
        :param str akeyless_uam_user_creds: Temporary credentials for accessing the endpoint (required)
        :param str akeyless_set_user_access_policy_creds: Temporary credentials for accessing the endpoint (required)
        :param str user_name: The user name to be created (required)
        :return: CreateUserReplyObj
                 If the method is called asynchronously,
                 returns the request thread.
        """

    @abc.abstractmethod
    def get_user(self, akeyless_uam_user_creds, user_name, **kwargs):
        # type: (str, str, dict) -> GetUserReplyObj
        """Get user details.

        This endpoint is accessible only by the account admin user
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.get_user(akeyless_uam_user_creds, user_name, async=True)
        >>> result = thread.get()

        :param async bool
        :param str akeyless_uam_user_creds: Temporary credentials for accessing the endpoint (required)
        :param str user_name: User name. (required)
        :return: GetUserReplyObj
                 If the method is called asynchronously,
                 returns the request thread.
        """

    @abc.abstractmethod
    def get_account_users(self, akeyless_uam_user_creds, **kwargs):
        """Get All the existing users in the account.

        This endpoint is accessible only by the account admin user
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.get_account_users(akeyless_uam_user_creds, async=True)
        >>> result = thread.get()

        :param async bool
        :param str akeyless_uam_user_creds: Temporary credentials for accessing the endpoint (required)
        :return: GetAccountUsersReplyObj
                 If the method is called asynchronously,
                 returns the request thread.
        """

    @abc.abstractmethod
    def update_user(self, akeyless_uam_user_creds, akeyless_set_user_access_policy_creds, new_user_name, user_name, **kwargs):
        # type: (str, str, str, str, dict) -> None
        """Updating an existing user in the account

        This endpoint is accessible only by the account admin user
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.update_user(akeyless_uam_user_creds, akeyless_set_user_access_policy_creds, new_user_name, user_name, async=True)
        >>> result = thread.get()

        :param async bool
        :param str akeyless_uam_user_creds: Temporary credentials for accessing the endpoint (required)
        :param str akeyless_set_user_access_policy_creds: Temporary credentials for accessing the endpoint (required)
        :param str new_user_name: The new username that will replace the existing one (required)
        :param str user_name: User name. (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

    @abc.abstractmethod
    def delete_user(self, akeyless_uam_user_creds, user_name, **kwargs):
        # type: (str, str, dict) -> None
        """Deleting an existing user from the account.

        This endpoint is accessible only by the account admin user
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.delete_user(akeyless_uam_user_creds, user_name, async=True)
        >>> result = thread.get()

        :param async bool
        :param str akeyless_uam_user_creds: Temporary credentials for accessing the endpoint (required)
        :param str user_name: User name. (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

    @abc.abstractmethod
    def create_role(self, akeyless_uam_user_creds, role_name, **kwargs):
        # type: (str, str, dict) -> None
        """Add a new role to the account.

        This endpoint is accessible only by the account admin user
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.create_role(akeyless_uam_user_creds, role_name, async=True)
        >>> result = thread.get()

        :param async bool
        :param str akeyless_uam_user_creds: Temporary credentials for accessing the endpoint (required)
        :param str role_name: The role name to be created (required)
        :param str role_action: The role action.
        :param str comment: Comments
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

    @abc.abstractmethod
    def get_role(self, akeyless_uam_user_creds, role_name, **kwargs):
        # type: (str, str, dict) -> GetRoleReplyObj
        """Get role details.

        This endpoint is accessible only by the account admin user
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.get_role(akeyless_uam_user_creds, role_name, async=True)
        >>> result = thread.get()

        :param async bool
        :param str akeyless_uam_user_creds: Temporary credentials for accessing the endpoint (required)
        :param str role_name: Role name. (required)
        :return: GetRoleReplyObj
                 If the method is called asynchronously,
                 returns the request thread.
        """

    @abc.abstractmethod
    def get_account_roles(self, akeyless_uam_user_creds, **kwargs):
        """Get All the existing roles in the account.

        This endpoint is accessible only by the account admin user
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.get_account_roles(akeyless_uam_user_creds, async=True)
        >>> result = thread.get()

        :param async bool
        :param str akeyless_uam_user_creds: Temporary credentials for accessing the endpoint (required)
        :return: GetAccountRolesReplyObj
                 If the method is called asynchronously,
                 returns the request thread.
        """

    @abc.abstractmethod
    def update_role(self, akeyless_uam_user_creds, new_role_name, role_name, **kwargs):
        # type: (str, str, str, dict) -> None
        """Updating an existing role in the account

        This endpoint is accessible only by the account admin user
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.update_role(akeyless_uam_user_creds, new_role_name, role_name, async=True)
        >>> result = thread.get()

        :param async bool
        :param str akeyless_uam_user_creds: Temporary credentials for accessing the endpoint (required)
        :param str new_role_name: The new role name that will replace the existing one (required)
        :param str role_name: Role name. (required)
        :param str role_action: The role action.
        :param str comment: Comments
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

    @abc.abstractmethod
    def delete_role(self, akeyless_uam_user_creds, role_name, **kwargs):
        # type: (str, str, dict) -> None
        """Deleting an existing role from the account.

        This endpoint is accessible only by the account admin role
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.delete_role(akeyless_uam_user_creds, role_name, async=True)
        >>> result = thread.get()

        :param async bool
        :param str akeyless_uam_user_creds: Temporary credentials for accessing the endpoint (required)
        :param str role_name: Role name. (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

    @abc.abstractmethod
    def create_role_item_assoc(self, akeyless_uam_user_creds, role_name, associated_name, **kwargs):
        # type: (str, str, str, dict) -> None
        """Add an association between a role and an item.

        This endpoint is accessible only by the account admin user
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.create_role_item_assoc(akeyless_uam_user_creds, role_name, associated_name, async=True)
        >>> result = thread.get()

        :param async bool
        :param str akeyless_uam_user_creds: Temporary credentials for accessing the endpoint (required)
        :param str role_name: The role name to be associated (required)
        :param str associated_name: The item or user name to be associated. (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

    @abc.abstractmethod
    def create_role_user_assoc(self, akeyless_uam_user_creds, role_name, associated_name, **kwargs):
        # type: (str, str, str, dict) -> None
        """Add an association between a role and a user.

        This endpoint is accessible only by the account admin user
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.create_role_user_assoc(akeyless_uam_user_creds, role_name, associated_name, async=True)
        >>> result = thread.get()

        :param async bool
        :param str akeyless_uam_user_creds: Temporary credentials for accessing the endpoint (required)
        :param str role_name: The role name to be associated (required)
        :param str associated_name: The item or user name to be associated. (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

    @abc.abstractmethod
    def delete_role_item_assoc(self, akeyless_uam_user_creds, role_name, associated_name, **kwargs):
        # type: (str, str, str, dict) -> None
        """Deleting an association between a role and an item.

        This endpoint is accessible only by the account admin role
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.delete_role_item_assoc(akeyless_uam_user_creds, role_name, associated_name, async=True)
        >>> result = thread.get()

        :param async bool
        :param str akeyless_uam_user_creds: Temporary credentials for accessing the endpoint (required)
        :param str role_name: The role name to be associated (required)
        :param str associated_name: The item or user name to be associated. (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

    @abc.abstractmethod
    def delete_role_user_assoc(self, akeyless_uam_user_creds, role_name, associated_name, **kwargs):
        # type: (str, str, str, dict) -> None
        """Deleting an association between a role and an user.

        This endpoint is accessible only by the account admin role
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.delete_role_user_assoc(akeyless_uam_user_creds, role_name, associated_name, async=True)
        >>> result = thread.get()

        :param async bool
        :param str akeyless_uam_user_creds: Temporary credentials for accessing the endpoint (required)
        :param str role_name: The role name to be associated (required)
        :param str associated_name: The item or user name to be associated. (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
