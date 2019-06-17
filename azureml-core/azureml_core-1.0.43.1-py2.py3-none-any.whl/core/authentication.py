# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Module for managing the different types of Authentication from Azure Machine Learning.

Types of authentication:
Interactive Login - The default mode when using Azure ML SDK, uses an interactive dialog
Azure Cli - For use with the azure-cli package
Service Principal - For use in a machine learning workflow automated process
Msi - For use with Msi-enabled assets
Azure ML Token - Used for acquiring Azure ML tokens, for submitted runs only
Arm Token - Used for authenticating using ARM token

Please refer to aka.ms/aml-notebook-auth to learn more about these authentication mechanisms.
"""
import datetime
import logging
import os
import pytz
import time
import threading
import jwt
import dateutil.parser

from abc import ABCMeta, abstractmethod

import collections
from requests import Session
from azureml.core.util import NewLoggingLevel
from azureml.exceptions import AuthenticationException, UserErrorException
from azureml._async.daemon import Daemon
from azureml._base_sdk_common.common import fetch_tenantid_from_aad_token, perform_interactive_login
from azureml._logging.logged_lock import ACQUIRE_DURATION_THRESHOLD, LoggedLock

_SubscriptionInfo = collections.namedtuple("SubscriptionInfo", "subscription_name subscription_id")

module_logger = logging.getLogger(__name__)


class AbstractAuthentication(object):
    """An abstract class for all authentication classes.

    All derived classes provide different means to authenticate the user and acquire a valid access token.
    """

    __metaclass__ = ABCMeta

    def get_authentication_header(self):
        """Return the HTTP authorization header.

        The authorization header contains the user access token for access authorization against the service.

        :return: Returns the HTTP authorization header.

        :rtype: dict
        """
        # We return a new dictionary each time, as some functions modify the headers returned
        # by this function.
        auth_header = {"Authorization": "Bearer " + self._get_arm_token()}
        return auth_header

    @abstractmethod
    def _get_arm_token(self):
        """Abstract method that auth classes should implement to return an arm token.

        :return: Return a user's arm token.
        :rtype: str
        """
        pass

    @abstractmethod
    def _get_graph_token(self):
        """Abstract method that auth classes should implement to return an Graph token.

        :return: Return a user's Graph token.
        :rtype: str
        """
        pass

    @abstractmethod
    def _get_all_subscription_ids(self):
        """Return a list of subscriptions that are accessible through this authentication.

        :return: Returns a list of SubscriptionInfo named tuples, and the current tenant id.
        :rtype: list, str
        """
        pass

    def _get_service_client(self, client_class, subscription_id, subscription_bound=True, base_url=None):
        """Create and return a service client object for client_class using subscription_id and auth token.

        :param client_class:
        :type client_class: object
        :param subscription_id:
        :type subscription_id: str
        :param subscription_bound: True if a subscription id is required to construct the client. Only False for
        1 RP clients.
        :type subscription_bound: bool
        :param base_url: The specified base URL client should use, usually differs by region
        :type base_url: str
        :return:
        :rtype: client_class
        """
        # Checks if auth has access to the provided subscription.
        # In Azureml Token based auth, we don't do subscription check, as this requires querying ARM.
        # We don't use az CLI methods to get a service client because in multi-tenant case, based on a subscription
        # az CLI code changes the arm token while getting a service client, which means that
        # the arm token that this auth object has differs from the arm token in the service client
        # in the multi-tenant case, which causes confusion.
        if subscription_id:
            all_subscription_list, tenant_id = self._get_all_subscription_ids()
            self._check_if_subscription_exists(subscription_id, all_subscription_list, tenant_id)

        return _get_service_client_using_arm_token(self, client_class, subscription_id,
                                                   subscription_bound=subscription_bound,
                                                   base_url=base_url)

    def signed_session(self, session=None):
        """Add the authorization header as a persisted header on an HTTP session.

        Any new requests sent by the session will contain the authorization header.

        :param session: HTTP session that will have the authorization header as a default persisted header.
            When None a new session will be created.
        :type session: requests.session:
        :return: Returns the HTTP session after the update.
        :rtype: requests.session
        """
        session = session or Session()
        session.headers.update(self.get_authentication_header())
        return session

    def _get_arm_end_point(self):
        """Return the arm end point.

        :return: Returns the arm end point. For the azure public cloud this is always 'https://management.azure.com/'
        :rtype: str
        """
        from azureml._vendor.azure_cli_core.cloud import AZURE_PUBLIC_CLOUD
        return AZURE_PUBLIC_CLOUD.endpoints.resource_manager

    def _get_cloud_type(self):
        """Return the cloud type. Currently SDK only supports AZURE_PUBLIC_CLOUD.

        :return:
        :rtype: azureml._vendor.azure_cli_core.cloud.Cloud
        """
        from azureml._vendor.azure_cli_core.cloud import AZURE_PUBLIC_CLOUD
        return AZURE_PUBLIC_CLOUD

    def _get_adal_auth_object(self, is_graph_auth=False):
        """Return an adal auth object.

        :return: Returns adal auth object needed for azure sdk clients.
        :rtype: azureml._vendor.azure_cli_core.adal_authentication.AdalAuthentication
        """
        from azureml._vendor.azure_cli_core.adal_authentication import AdalAuthentication
        if is_graph_auth:
            token = self._get_graph_token()
        else:
            token = self.get_authentication_header()["Authorization"].split(" ")[1]
        adal_auth_object = AdalAuthentication(lambda: ("Bearer", token, None))
        return adal_auth_object

    def _check_if_subscription_exists(self, subscription_id, subscription_id_list, tenant_id):
        """Check if subscription_id exists in subscription_id_list.

        :param subscription_id: Subscription id to check.
        :type subscription_id: str
        :param subscription_id_list: Subscription id list.
        :type subscription_id_list: list[azureml.core.authentication.SubscriptionInfo]
        :param tenant_id: Currently logged-in tenant id
        :type tenant_id: str
        :return: True if subscription exists.
        :rtype: bool
        """
        name_matched = False
        for subscription_info in subscription_id_list:
            if subscription_info.subscription_id.lower().strip() == subscription_id.lower().strip():
                return True
            if subscription_info.subscription_name.lower().strip() == subscription_id.lower().strip():
                name_matched = True

        if name_matched:
            raise UserErrorException("It looks like you have specified subscription name, {}, instead of "
                                     "subscription id. Subscription names may not be unique, please specify "
                                     "subscription id from this list \n {}".format(subscription_id,
                                                                                   subscription_id_list))
        else:
            raise UserErrorException("You are currently logged-in to {} tenant. You don't have access "
                                     "to {} subscription, please check if it is in this tenant. "
                                     "All the subscriptions that you have access to in this tenant are = \n "
                                     "{}. \n Please refer to aka.ms/aml-notebook-auth for different "
                                     "authentication mechanisms in azureml-sdk.".format(tenant_id,
                                                                                        subscription_id,
                                                                                        subscription_id_list))


def _login_on_failure_decorator(lock_to_use):
    """Login on failure decorator.

    This decorator performs az login on failure of the actual function and retries the actual function one more
    time.

    Notebooks are long running processes, like people open them and then never close them.
    So, on InteractiveLoginAuthentication object, auth._get_arm_token etc functions can throw
    error if the arm token and refresh token both have expired, and this will prompt a
    user to run "az login" outside the notebook. So, we use this decorator on every function
    of InteractiveLoginAuthentication to catch the first failure, perform "az login" and retry the
    function.

    We also use Profile(async_persist=False), so that tokens are persisted and re-used on-disk.
    async_persist=True (default), az CLI only persists tokens on the process exit, which just never
    happens in a notebook case, in turn requiring users to perform "az login" outside notebooks.

    :return:
    :rtype: object
    """
    def actual_decorator(test_function):
        """Actual decorator.

        :param test_function:
        :type test_function: object
        :return: Returns the wrapper.
        :rtype: object
        """
        def wrapper(self, *args, **kwargs):
            """Wrapper.

            :param args:
            :type args: list
            :param kwargs:
            :type kwargs: dict
            :return: Returns the test function.
            :rtype: object
            """
            try:
                start_time = time.time()
                lock_to_use.acquire()
                duration = time.time() - start_time
                if duration > ACQUIRE_DURATION_THRESHOLD:
                    module_logger.debug("{} acquired lock in {} s.".format(type(self).__name__, duration))
                return test_function(self, *args, **kwargs)
            except Exception as e:
                if type(self) == InteractiveLoginAuthentication:
                    # Perform InteractiveLoginAuthentication and try one more time.
                    InteractiveLoginAuthentication(force=True, tenant_id=self._tenant_id)
                    # Try one more time
                    return test_function(self, *args, **kwargs)
                else:
                    raise e
            finally:
                lock_to_use.release()
        return wrapper

    return actual_decorator


class InteractiveLoginAuthentication(AbstractAuthentication):
    """This class authenticates the user to acquire the user's access token.

    The access token is used for authorization.

    .. remarks::

        The constructor of the class will prompt the user to login. The constructor then will save the credentials for any subsequent attempts.
        If the user is already logged in to azure CLI or have logged-in before, the constructor will load the existing credentials without prompt.

        When this python process is running in Azure Notebook service, the constructor will attempt to use the "connect to azure" feature in Azure Notebooks.

        Please refer to aka.ms/aml-notebook-auth to learn about authentication mechanisms in AzureML SDK.
    """

    # We are using locks because in some cases like hyperdrive this
    # function gets called in parallel, which initiates multiple
    # "az login" at once.
    # TODO: This needs to be made non-static.
    # Currently we are not sure if it is a parallelism issue or multiple auth objects.
    # So, going with static global lock.
    _interactive_auth_lock = threading.Lock()

    # TODO: This authentication mechanism should use the azureml application ID while
    # authenticating with ARM, rather than the az CLI application ID.

    # TODO: This should also persist state separately from .azure directory, so we need to
    # implement the state saving mechanism in a thread-safe manner using locking.

    def __init__(self, force=False, tenant_id=None):
        """Interactive Login Authentication constructor.

        This constructor will prompt the user to login, then it will save the credentials for any subsequent
        attempts. If the user is already logged in to azure CLI  or have logged in before, the constructor will load
        the existing credentials without prompt. When this python process is running in Azure Notebook service, the
        constructor will attempt to use the "connect to azure" feature in Azure Notebooks.

        :param force: If force=True, then "az login" will be run even if the old "az login" is still valid.
        :type force: bool
        :param tenant_id: Tenant id to login into, if a user has access to multiple tenants then the user can
        specify a tenant to login into. If unspecified, default tenant will be used.
        :type tenant_id: str
        """
        # TODO: This is just based on az login for now.
        # This all will need to change and made az CLI independent.

        self._tenant_id = tenant_id
        self._ambient_auth = self._get_ambient()

        if self._ambient_auth is None:
            if force:
                print("Performing interactive authentication. Please follow the instructions "
                      "on the terminal.")
                perform_interactive_login(tenant=tenant_id)
                print("Interactive authentication successfully completed.")
            else:
                need_to_login = False
                try:
                    self._get_arm_token_using_interactive_auth()
                except Exception:
                    try:
                        self._fallback_to_azure_cli_credential()
                    except Exception:
                        need_to_login = True

                if need_to_login:
                    print("Performing interactive authentication. Please follow the instructions "
                          "on the terminal.")
                    perform_interactive_login(tenant=tenant_id)
                    print("Interactive authentication successfully completed.")

    @_login_on_failure_decorator(_interactive_auth_lock)
    def _get_arm_token(self):
        """Return the arm access token.

        :return: Returns the arm access token.
        :rtype: str
        """
        if isinstance(self._ambient_auth, AbstractAuthentication):
            return self._ambient_auth._get_arm_token()
        else:
            return self._get_arm_token_using_interactive_auth()

    @_login_on_failure_decorator(_interactive_auth_lock)
    def _get_graph_token(self):
        """Return the Graph access token.

        :return: Returns the Graph access token.
        :rtype: str
        """
        if isinstance(self._ambient_auth, AbstractAuthentication):
            if hasattr(self._ambient_auth, '_get_graph_token'):
                return self._ambient_auth._get_graph_token()
            raise NotImplementedError(
                "No graph token for ambient authentication type {}".format(type(self._ambient_auth).__name__))
        else:
            return self._get_arm_token_using_interactive_auth(
                resource=self._get_cloud_type().endpoints.active_directory_graph_resource_id)

    def _get_all_subscription_ids(self):
        """Return a list of subscriptions that are accessible through this authentication.

        :return: Returns a list of SubscriptionInfo named tuples.
        :rtype: list, str
        """
        arm_token = self._get_arm_token()
        return self._get_all_subscription_ids_internal(arm_token)

    @_login_on_failure_decorator(_interactive_auth_lock)
    def _get_all_subscription_ids_internal(self, arm_token):
        if isinstance(self._ambient_auth, AbstractAuthentication):
            return self._ambient_auth._get_all_subscription_ids()
        else:
            from azureml._vendor.azure_cli_core._profile import Profile
            from azureml._base_sdk_common.common import fetch_tenantid_from_aad_token
            token_tenant_id = fetch_tenantid_from_aad_token(arm_token)
            profile_object = Profile(async_persist=False)
            # List of subscriptions might be cached on disk, so we are just trying to get it from disk.
            all_subscriptions = profile_object.load_cached_subscriptions()
            result = []

            for subscription_info in all_subscriptions:
                # Az CLI returns subscriptions for all tenants, but we want subscriptions
                # that a user has access to using the current arm token for the tenant. So we
                # filter based on tenant id.
                # There are some subscriptions from windows azure time that don't have
                # tenant id for them, so we ignore tenantId check for them.
                if "tenantId" not in subscription_info or \
                        subscription_info["tenantId"].lower() == token_tenant_id.lower():
                    subscription_tuple = _SubscriptionInfo(subscription_info['name'],
                                                           subscription_info['id'])
                    result.append(subscription_tuple)
            return result, token_tenant_id

    @_login_on_failure_decorator(_interactive_auth_lock)
    def _check_if_subscription_exists(self, subscription_id, subscription_id_list, tenant_id):
        super(InteractiveLoginAuthentication, self)._check_if_subscription_exists(subscription_id,
                                                                                  subscription_id_list, tenant_id)

    def _get_ambient(self):
        ambient_auth = None

        if "MSI_ENDPOINT" in os.environ:
            # MSI_ENDPOINT is always set by Azure Notebooks, so if the MSI_ENDPOINT env var
            # is set, we will try to create an MsiAuthentication object.
            ambient_auth = self._get_in_msi_scope()

        if not ambient_auth:
            # Check if we're in a high-concurrency ADB cluster
            ambient_auth = self._get_in_databricks_cluster()

        return ambient_auth

    def _get_in_msi_scope(self):
        """Get the msi authentication otherwise None.

        :return: MsiAuthentication or None.
        :rtype: azureml.core.authentication.MsiAuthentication
        """
        try:
            msi_auth = MsiAuthentication()
            # make sure we can get an arm token through msi to validate the auth object.
            arm_token = msi_auth._get_arm_token()
            # If a user has specified a tenant id then we need to check if this token is for that tenant.
            if self._tenant_id and fetch_tenantid_from_aad_token(arm_token) != self._tenant_id:
                raise UserErrorException("The tenant in the MSI authentication is different "
                                         "than the user specified tenant.")
            else:
                return msi_auth
        except Exception as e:
            # let it fail silently and move on to AzureCliAuthentication as users on
            # Azure Notebooks may want to use the credentials from 'az login'.
            module_logger.debug(e)

    def _get_in_databricks_cluster(self):
        """Get the msi authentication otherwise None.

        :return: MsiAuthentication or None.
        :rtype: azureml.core.authentication.MsiAuthentication
        """
        try:
            db_auth = _DatabricksClusterAuthentication(None)
            # make sure we can get an arm token through msi to validate the auth object.
            arm_token = db_auth._get_arm_token()
            # If a user has specified a tenant id then we need to check if this token is for that tenant.
            auth_tenant = fetch_tenantid_from_aad_token(arm_token)
            if self._tenant_id and auth_tenant != self._tenant_id:
                raise UserErrorException("The tenant in the Databricks cluster authentication {} is different "
                                         "than the user specified tenant {}.".format(auth_tenant, self._tenant_id))
            else:
                return db_auth
        except Exception as e:
            # let it fail silently and move on
            module_logger.debug(e)

    def _get_arm_token_using_interactive_auth(self, force_reload=False, resource=None):
        """Get the arm token cached on disk in interactive auth.

        :param force_reload: Force reloads credential information from disk.
        :type force_reload: bool
        :return: arm token or exception.
        :rtype: str
        """
        from azureml._vendor.azure_cli_core._profile import Profile
        from azureml._vendor.azure_cli_core.cloud import AZURE_PUBLIC_CLOUD
        from azureml._vendor.azure_cli_core._session import ACCOUNT, CONFIG, SESSION
        from azureml._vendor.azure_cli_core._environment import get_config_dir

        # If we can get a valid ARM token, then we don't need to login.
        profile_object = Profile(async_persist=False)
        cloud_type = AZURE_PUBLIC_CLOUD
        arm_token = _get_arm_token_with_refresh(profile_object, cloud_type, ACCOUNT, CONFIG, SESSION,
                                                get_config_dir(), force_reload=force_reload, resource=resource)
        # If a user has specified a tenant id then we need to check if this token is for that tenant.
        if self._tenant_id and fetch_tenantid_from_aad_token(arm_token) != self._tenant_id:
            raise UserErrorException("The tenant in the authentication is different "
                                     "than the user specified tenant.")
        else:
            return arm_token

    def _fallback_to_azure_cli_credential(self):
        from azureml._vendor.azure_cli_core._environment import _AZUREML_AUTH_CONFIG_DIR_ENV_NAME
        from azureml._vendor.azure_cli_core._profile import Profile
        try:
            # Setting the environment variable for ~/.azure directory.
            os.environ[_AZUREML_AUTH_CONFIG_DIR_ENV_NAME] \
                = os.getenv('AZURE_CONFIG_DIR', None) or os.path.expanduser(os.path.join('~', '.azure'))
            # Resetting global credential cache.
            Profile._global_creds_cache = None
            # Reloading the state from disk with new directory.
            self._get_arm_token_using_interactive_auth(force_reload=True)
            # If this succeeds then we keep using the directory, and even child process will inherit this
            # env variable.
            import logging
            logging.getLogger().warning("Warning: Falling back to use azure cli login credentials.\n"
                                        "If you run your code in unattended mode, i.e., where you can't give a user input, "
                                        "then we recommend to use ServicePrincipalAuthentication or MsiAuthentication.\n"
                                        "Please refer to aka.ms/aml-notebook-auth for different authentication mechanisms "
                                        "in azureml-sdk.")
        except Exception as ex:
            Profile._global_creds_cache = None
            # If this fails then we remove this env variable to use ~/.azureml/auth directory.
            del os.environ[_AZUREML_AUTH_CONFIG_DIR_ENV_NAME]
            raise ex


class AzureCliAuthentication(AbstractAuthentication):
    """The class used internally to prompt the user for login.

    .. remarks::
        Please refer to aka.ms/aml-notebook-auth to learn about authentication mechanisms in AzureML SDK.

    It's preferable to use :class:`azureml.core.authentication.InteractiveLoginAuthentication` for better Azure Notebooks experience.
    """

    _azcli_auth_lock = threading.Lock()

    _TOKEN_TIMEOUT_SECs = 3600

    @_login_on_failure_decorator(_azcli_auth_lock)
    def _get_default_subscription_id(self):
        """Return default subscription id.

        This method has lock, as it access az CLI internal methods.

        :return: Returns the default subscription id.
        :rtype: str
        """
        self._azure_cli_core_check()

        # Hack to make this work outside the Azure CLI.
        from azure.cli.core._session import ACCOUNT, CONFIG, SESSION
        from azure.cli.core._environment import get_config_dir
        from azure.cli.core.commands.client_factory import get_subscription_id
        from azure.cli.core import get_default_cli

        if not ACCOUNT.data:
            config_dir = get_config_dir()
            ACCOUNT.load(os.path.join(config_dir, 'azureProfile.json'))
            CONFIG.load(os.path.join(config_dir, 'az.json'))
            SESSION.load(os.path.join(config_dir, 'az.sess'), max_age=AzureCliAuthentication._TOKEN_TIMEOUT_SECs)

        return get_subscription_id(get_default_cli())

    @_login_on_failure_decorator(_azcli_auth_lock)
    def _get_arm_token(self):
        """Fetch a valid ARM token using azure API calls.

        This method has lock, as it access az CLI internal methods.

        :return: Arm access token.
        :rtype: str
        """
        self._azure_cli_core_check()

        from azure.cli.core._profile import Profile
        from azure.cli.core.cloud import get_active_cloud

        # Hack to make this work outside the Azure CLI.
        from azure.cli.core._session import ACCOUNT, CONFIG, SESSION
        from azure.cli.core._environment import get_config_dir

        # From notebook, we want to persist tokens synchronously to the on-disk file,
        # so that users don't have to run az login multiple times.
        # By default, a tokens are persisted on-disk on exit on a process, which
        # doesn't happen in notebook or happens in a way where token persistence logic
        # is not called.
        profile_object = Profile(async_persist=False)
        cloud_type = get_active_cloud()
        return _get_arm_token_with_refresh(profile_object, cloud_type, ACCOUNT, CONFIG, SESSION, get_config_dir())

    @_login_on_failure_decorator(_azcli_auth_lock)
    def _get_graph_token(self):
        """Fetch a valid Graph token using azure API calls.

        This method has lock, as it access az CLI internal methods.

        :return: Graph access token.
        :rtype: str
        """
        self._azure_cli_core_check()
        print('az cli auth')

        from azure.cli.core._profile import Profile
        from azure.cli.core.cloud import get_active_cloud

        # Hack to make this work outside the Azure CLI.
        from azure.cli.core._session import ACCOUNT, CONFIG, SESSION
        from azure.cli.core._environment import get_config_dir

        # From notebook, we want to persist tokens synchronously to the on-disk file,
        # so that users don't have to run az login multiple times.
        # By default, a tokens are persisted on-disk on exit on a process, which
        # doesn't happen in notebook or happens in a way where token persistence logic
        # is not called.
        profile_object = Profile(async_persist=False)
        cloud_type = get_active_cloud()
        print('az cli auth1')
        print(self._get_cloud_type().endpoints.active_directory_graph_resource_id)
        return _get_arm_token_with_refresh(
            profile_object,
            cloud_type,
            ACCOUNT,
            CONFIG,
            SESSION,
            get_config_dir(),
            resource=self._get_cloud_type().endpoints.active_directory_graph_resource_id)

    def _get_all_subscription_ids(self):
        """Return a list of subscriptions that are accessible through this authentication.

        This method has lock, as it access az CLI internal methods.

        :return: Returns a list of SubscriptionInfo named tuples.
        :rtype: list, str
        """
        arm_token = self._get_arm_token()
        return self._get_all_subscription_ids_internal(arm_token)

    @_login_on_failure_decorator(_azcli_auth_lock)
    def _get_all_subscription_ids_internal(self, arm_token):
        self._azure_cli_core_check()

        from azureml._base_sdk_common.common import fetch_tenantid_from_aad_token
        from azure.cli.core._profile import Profile
        profile = Profile(async_persist=False)
        # This is a CLI authentication, so we are just calling simple CLI methods
        # for getting subscriptions.
        all_subscriptions = profile.load_cached_subscriptions()
        result = []

        token_tenant_id = fetch_tenantid_from_aad_token(arm_token)

        for subscription_info in all_subscriptions:

            # Az CLI returns subscriptions for all tenants, but we want subscriptions
            # that a user has access to using the current arm token for the tenant. So we
            # filter based on tenant id.
            # There are some subscriptions from windows azure time that don't have
            # tenant id for them, so we ignore tenantId check for them.
            if "tenantId" not in subscription_info or \
                    subscription_info["tenantId"].lower() == token_tenant_id.lower():
                subscription_tuple = _SubscriptionInfo(subscription_info['name'],
                                                       subscription_info['id'])
                result.append(subscription_tuple)
        return result, token_tenant_id

    def _azure_cli_core_check(self):
        try:
            from azure.cli.core._profile import Profile  # noqa
            from azure.cli.core.cloud import get_active_cloud  # noqa

            # Hack to make this work outside the Azure CLI.
            from azure.cli.core._session import ACCOUNT, CONFIG, SESSION  # noqa
            from azure.cli.core._environment import get_config_dir  # noqa
        except Exception:
            raise AuthenticationException("azure.cli.core package is not installed. "
                                          "AzureCliAuthentication requires azure.cli.core to be installed in the "
                                          "same python environment where azureml-sdk is installed.")


class ArmTokenAuthentication(AbstractAuthentication):
    """The class is used internally to acquire ARM access tokens using service principle or managed service identity.

    It's preferable to use :class:`azureml.core.authentication.ServicePrincipalAuthentication` instead.
    """

    def __init__(self, arm_access_token):
        """Class ArmTokenAuthentification constructor.

        :param arm_access_token: ARM access token
        :type arm_access_token: str
        """
        self._arm_access_token = arm_access_token

    def update_arm_access_token(self, new_arm_access_token):
        """Update arm access token.

        :param new_arm_access_token: ARM access token
        :type new_arm_access_token: str
        """
        self._arm_access_token = new_arm_access_token

    def _get_arm_token(self):
        """Return arm access token.

        :return: Returns arm access token
        :rtype: str
        """
        return self._arm_access_token

    def _get_all_subscription_ids(self):
        """Return a list of subscriptions that are accessible through this authentication.

        :return: Returns a list of SubscriptionInfo named tuples.
        :rtype: list, str
        """
        arm_token = self._get_arm_token()
        from azureml._vendor.azure_cli_core.adal_authentication import AdalAuthentication
        auth_object = AdalAuthentication(lambda: ("Bearer", arm_token, None))
        from azureml._base_sdk_common.common import fetch_tenantid_from_aad_token
        token_tenant_id = fetch_tenantid_from_aad_token(arm_token)

        return _get_subscription_ids_via_client(auth_object), token_tenant_id


class _DatabricksClusterAuthentication(ArmTokenAuthentication):

    def _get_arm_token(self):
        """Return arm token.

        :return: Returns the arm token.
        :rtype: str
        """
        # retrieves the AAD token through DB cluster exposed token
        return dbutils.notebook.entry_point.getDbutils().notebook().getContext().adlsAadToken().get() # noqa


def _sp_auth_caching_decorator(token_type):

    def actual_decorator(actual_function):
        """Actual decorator.

        :param actual_function: Actual function to which this decorator was applied to.
        :type actual_function: object
        :return: Returns the wrapper.
        :rtype: object
        """
        def wrapper(self, *args, **kwargs):
            """Wrapper.

            :param args:
            :type args: list
            :param kwargs:
            :type kwargs: dict
            :return: Returns the test function.
            :rtype: object
            """
            field_name = ServicePrincipalAuthentication._token_type_to_field_dict[token_type]
            if self._enable_caching:
                cached_token = getattr(self, field_name)
                if not cached_token or self._is_token_expired(cached_token):
                    with self._auth_lock:
                        # Getting it again after acquiring the lock in case some other thread might have updated it.
                        cached_token = getattr(self, field_name)
                        if not cached_token or self._is_token_expired(cached_token):
                            new_token = actual_function(self, *args, **kwargs)
                            setattr(self, field_name, new_token)
                            return new_token
                        else:
                            return cached_token
                else:
                    return cached_token
            else:
                return actual_function(self, *args, **kwargs)

        return wrapper

    return actual_decorator


class ServicePrincipalAuthentication(AbstractAuthentication):
    """The class allows for authentication using a service principle instead of users own identity.

    The class is ideal for automation and CI/CD scenarios.

    .. remarks::
        Please refer to aka.ms/aml-notebook-auth to learn about authentication mechanisms in AzureML SDK.

    :param tenant_id: The active directory tenant that the service identity belongs to.
    :type tenant_id: str
    :param service_principal_id: The service principal id.
    :type service_principal_id: str
    :param service_principal_password: The service principal password/key.
    :type service_principal_password: str
    """

    _token_type_to_field_dict = {"ARM_TOKEN": "_cached_arm_token", "GRAPH_TOKEN": "_cached_graph_token"}

    def __init__(self, tenant_id, service_principal_id, service_principal_password, _enable_caching=False):
        """Class ServicePrincipalAuthentication constructor."""
        self._tenant_id = tenant_id
        self._service_principal_id = service_principal_id
        self._service_principal_password = service_principal_password
        self._enable_caching = _enable_caching
        self._cached_arm_token = None
        self._cached_graph_token = None
        self._auth_lock = threading.Lock()

    @_sp_auth_caching_decorator("ARM_TOKEN")
    def _get_arm_token(self):
        """Return arm access token.

        :return: Returns arm token from sp credential object
        :rtype: str
        """
        header = self._get_sp_credential_object().signed_session().headers['Authorization']
        return header.split(" ")[1]

    @_sp_auth_caching_decorator("GRAPH_TOKEN")
    def _get_graph_token(self):
        """Return Graph access token.

        :return: Returns Graph token from sp credential object
        :rtype: str
        """
        resource = self._get_cloud_type().endpoints.active_directory_graph_resource_id
        header = self._get_sp_credential_object(resource).signed_session().headers['Authorization']
        return header.split(" ")[1]

    def _get_sp_credential_object(self, resource=None):
        """Return service principal credentials.

        :return: Returns sp credentials
        :rtype: AdalAuthentication
        """
        import adal
        from msrestazure.azure_active_directory import AdalAuthentication
        from msrestazure.azure_cloud import AZURE_PUBLIC_CLOUD

        # TODO: We have some sad deepcopy in our code, and keeping
        # sp_credentials object as a class field prevents the deepcopy
        # off  auth object in workspace, project classes.
        # Because sp_credentials somehow contains RLock object that cannot be deepcopied.
        login_endpoint = AZURE_PUBLIC_CLOUD.endpoints.active_directory
        if not resource:
            resource = AZURE_PUBLIC_CLOUD.endpoints.active_directory_resource_id

        context = adal.AuthenticationContext('{0}/{1}'.format(login_endpoint, self._tenant_id),
                                             api_version=None)
        sp_credentials = AdalAuthentication(
            context.acquire_token_with_client_credentials,
            resource, self._service_principal_id, self._service_principal_password)
        return sp_credentials

    def _get_all_subscription_ids(self):
        """Return a list of subscriptions that are accessible through this authentication.

        :return: Returns a list of SubscriptionInfo named tuples.
        :rtype: list, str
        """
        arm_token = self._get_arm_token()
        arm_auth = ArmTokenAuthentication(arm_token)
        return arm_auth._get_all_subscription_ids()

    def _is_token_expired(self, token_to_check):
        if not token_to_check:
            return True

        decoded_json = jwt.decode(token_to_check, verify=False)
        return (decoded_json["exp"] - time.time()) < (5 * 60)


class AzureMLTokenAuthentication(AbstractAuthentication):
    """Authorizes users by their Azure ML token.

    The Azure ML token is generated when a run is submitted and is only available to the code submitted. The class can
    only be used in the context of submitted run. The token cannot be used against any ARM operations like provisioning
    compute. The Azure ML token is useful when executing a program remotely where it might be unsafe to use the user's
    private credentials.
    """

    _registered_auth = dict()
    _host_clientbase = dict()
    _register_auth_lock = threading.Lock()
    _daemon = None

    # To refresh the token as late as (3 network retries (30s call timeout) + 5s buffer) seconds before it expires
    EXPIRATION_THRESHOLD_IN_SECONDS = 95
    REFRESH_INTERVAL_IN_SECONDS = 30

    def __init__(self, azureml_access_token, expiry_time=None, host=None, subscription_id=None,
                 resource_group_name=None, workspace_name=None, experiment_name=None, run_id=None, user_email=None):
        """Authorize users by their Azure ML token.

        The Azure ML token is generated when a run is submitted and is only available to the code submitted.
        The class can only be used in the context of submitted run. The token cannot be used against any ARM operations like provisioning compute.
        The Azure ML token is useful when executing a program remotely where it might be unsafe to use the user's private credentials.
        The consumer of this class should call the class method create which creates a new object or returns a registered instance
        with the same run_scope (subscription_id, resource_group_name, workspace_name, experiment_name, run_id) provided.

        :param azureml_access_token: The Azure ML token is generated when a run is submitted and is only available to the code submitted.
        :type azureml_access_token: str
        :param user_email:
        :type user_email: str
        :param expiry_time:
        :type expiry_time: datetime.Datetime
        """
        self._aml_access_token = azureml_access_token
        self._user_email = user_email
        self._aml_token_lock = LoggedLock(_ident="AMLTokenLock", _parent_logger=module_logger)
        self._expiry_time = AzureMLTokenAuthentication._parse_expiry_time_from_token(
            self._aml_access_token) if expiry_time is None else expiry_time
        self._host = host
        self._subscription_id = subscription_id
        self._resource_group_name = resource_group_name
        self._workspace_name = workspace_name
        self._experiment_name = experiment_name
        self._run_id = run_id
        self._run_scope_info = (self._subscription_id,
                                self._resource_group_name,
                                self._workspace_name,
                                self._experiment_name,
                                self._run_id)

        if AzureMLTokenAuthentication._daemon is None:
            AzureMLTokenAuthentication._daemon = Daemon(work_func=AzureMLTokenAuthentication._update_registered_auth,
                                                        interval_sec=AzureMLTokenAuthentication.REFRESH_INTERVAL_IN_SECONDS,
                                                        _ident="TokenRefresherDaemon",
                                                        _parent_logger=module_logger)
            AzureMLTokenAuthentication._daemon.start()

        if any((param is None for param in self._run_scope_info)):
            module_logger.warning("The AzureMLTokenAuthentication created will not be updated due to missing params. "
                                  "The token expires on {}.\n".format(self._expiry_time))
        else:
            self._register_auth()

    @classmethod
    def create(cls, azureml_access_token, expiry_time, host, subscription_id,
               resource_group_name, workspace_name, experiment_name, run_id, user_email=None):
        """Create an AzureMLTokenAuthentication object or return a registered instance with the same run_scope."""
        auth_key = cls._construct_key(subscription_id,
                                      resource_group_name,
                                      workspace_name,
                                      experiment_name,
                                      run_id)
        if auth_key in cls._registered_auth:
            return cls._registered_auth[auth_key]

        return cls(azureml_access_token, expiry_time, host, subscription_id,
                   resource_group_name, workspace_name, experiment_name, run_id, user_email)

    @staticmethod
    def _parse_expiry_time_from_token(token):
        # We set verify=False, as we don't have keys to verify signature, and we also don't need to
        # verify signature, we just need the expiry time.
        decode_json = jwt.decode(token, verify=False)
        return AzureMLTokenAuthentication._convert_to_datetime(decode_json['exp'])

    @staticmethod
    def _convert_to_datetime(expiry_time):
        if isinstance(expiry_time, datetime.datetime):
            return expiry_time
        try:
            date = dateutil.parser.parse(expiry_time)
        except (ValueError, TypeError):
            date = datetime.datetime.fromtimestamp(int(expiry_time))
        return date

    @property
    def token(self):
        """Azure ML token.

        :return: the _aml_access_token
        :rtype: str
        """
        with self._aml_token_lock:
            return self._aml_access_token

    @property
    def expiry_time(self):
        """Azure ML token's expiry time.

        :return: the expiry_time
        :rtype: datetime.Datetime
        """
        with self._aml_token_lock:
            return self._expiry_time

    def get_authentication_header(self):
        """Return the HTTP authorization header.

        The authorization header contains the user access token for access authorization against the service.

        :return: Returns the HTTP authorization header.
        :rtype: dict
        """
        return {"Authorization": "Bearer " + self._aml_access_token}

    def set_token(self, token, expiry_time):
        """Update azureml access token.

        :param token:
        :type token: str
        :param expiry_time:
        :type expiry_time:
        """
        self._aml_access_token = token
        self._expiry_time = expiry_time

    def _get_arm_token(self):
        raise AuthenticationException("AzureMLTokenAuthentication._get_arm_token "
                                      "not yet supported.")

    def _get_graph_token(self):
        raise AuthenticationException("AzureMLTokenAuthentication._get_graph_token "
                                      "not yet supported.")

    @staticmethod
    def _construct_key(*args):
        return "//".join(args)

    @staticmethod
    def _should_refresh_token(current_expiry_time):
        if current_expiry_time is None:
            return True
        # Refresh when remaining duration < EXPIRATION_THRESHOLD_IN_SECONDS
        expiry_time_utc = current_expiry_time.replace(tzinfo=pytz.utc)
        current_time = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        time_difference = expiry_time_utc - current_time
        time_to_expire = time_difference / datetime.timedelta(seconds=1)
        module_logger.debug("Time to expire {} seconds".format(time_to_expire))
        return time_to_expire < AzureMLTokenAuthentication.EXPIRATION_THRESHOLD_IN_SECONDS

    def _update_auth(self):
        if AzureMLTokenAuthentication._should_refresh_token(self.expiry_time):
            module_logger.debug("Expiration time for run scope: {} = {}, refreshing token\n".format(
                self._run_scope_info, self.expiry_time))
            with AzureMLTokenAuthentication._register_auth_lock:
                host_key = AzureMLTokenAuthentication._construct_key(self._host,
                                                                     self._subscription_id,
                                                                     self._resource_group_name,
                                                                     self._workspace_name)
                if host_key in AzureMLTokenAuthentication._host_clientbase:
                    token_result = AzureMLTokenAuthentication._host_clientbase[host_key]._client.run.get_token(
                        *self._run_scope_info,
                        is_async=False
                    )
                    self.set_token(token_result.token, token_result.expiry_time_utc)

    def _register_auth(self):
        auth_key = AzureMLTokenAuthentication._construct_key(self._subscription_id,
                                                             self._resource_group_name,
                                                             self._workspace_name,
                                                             self._experiment_name,
                                                             self._run_id)
        if auth_key in AzureMLTokenAuthentication._registered_auth:
            module_logger.warning("Already registered authentication for run id: {}".format(self._run_id))
        else:
            from azureml._restclient.token_client import TokenClient
            host_key = AzureMLTokenAuthentication._construct_key(self._host,
                                                                 self._subscription_id,
                                                                 self._resource_group_name,
                                                                 self._workspace_name)
            if host_key not in AzureMLTokenAuthentication._host_clientbase:
                AzureMLTokenAuthentication._host_clientbase[host_key] = TokenClient(self, self._host)

            self._update_auth()
            with AzureMLTokenAuthentication._register_auth_lock:
                AzureMLTokenAuthentication._registered_auth[auth_key] = self

    @classmethod
    def _update_registered_auth(cls):
        with cls._register_auth_lock:
            auths = list(cls._registered_auth.values())
        for auth in auths:
            auth._update_auth()


class MsiAuthentication(AbstractAuthentication):
    """Authorizes users using MSIAuthentication in msrestazure.azure_active_directory."""

    def _get_arm_token(self):
        """Return arm token.

        :return: Returns the arm token.
        :rtype: str
        """
        # retrieves the AAD token through MSI
        from msrestazure.azure_active_directory import MSIAuthentication
        msi_auth = MSIAuthentication()
        msi_auth.set_token()
        return msi_auth.token['access_token']

    def _get_graph_token(self):
        """Return graph token.

        :return: Returns the graph token.
        :rtype: str
        """
        # retrieves the AAD token through MSI
        from msrestazure.azure_active_directory import MSIAuthentication
        resource = self._get_cloud_type().endpoints.active_directory_graph_resource_id
        msi_auth = MSIAuthentication(resource)
        msi_auth.set_token()
        return msi_auth.token['access_token']

    def _get_all_subscription_ids(self):
        """Return a list of subscriptions that are accessible through this authentication.

        :return: Returns a list of SubscriptionInfo named tuples.
        :rtype: list
        """
        from msrestazure.azure_active_directory import MSIAuthentication
        msi_auth = MSIAuthentication()
        arm_token = self._get_arm_token()
        from azureml._base_sdk_common.common import fetch_tenantid_from_aad_token
        token_tenant_id = fetch_tenantid_from_aad_token(arm_token)
        return _get_subscription_ids_via_client(msi_auth), token_tenant_id


def _get_subscription_ids_via_client(auth_obj):
    """Return a list of subscriptions that are accessible through this authentication.

    Helper function to retrieve subscriptionIDs and names using the SubscriptionClient.

    :param auth_obj: The msrest auth object. This is not azureml.core.authentication object.
    :type auth_obj: azureml._vendor.azure_cli_core.adal_authentication.AdalAuthentication
    :return: Returns a list of SubscriptionInfo named tuples.
    :rtype: list
    """
    from azure.mgmt.resource import SubscriptionClient
    result = []
    subscription_client = SubscriptionClient(auth_obj)
    for subscription in subscription_client.subscriptions.list():
        subscription_info = _SubscriptionInfo(subscription.display_name,
                                              subscription.subscription_id)
        result.append(subscription_info)
    return result


def _get_service_client_using_arm_token(auth, client_class, subscription_id,
                                        subscription_bound=True, base_url=None):
    """Return service client.

    :param auth:
    :type auth: AbstractAuthentication
    :param client_class: The service client class
    :type client_class: object
    :param subscription_id:
    :type subscription_id: str
    :param subscription_bound: True if a subscription id is required to construct the client. Only False for
        1 RP clients.
    :type subscription_bound: bool
    :param base_url:
    :type base_url: str
    :return:
    :rtype: object
    """
    adal_auth_object = auth._get_adal_auth_object()

    # 1 RP clients are not subscription bound.
    if not subscription_bound:
        client = client_class(adal_auth_object, base_url=base_url)
    else:
        # converting subscription_id, which is string, to string because of weird python 2.7 errors.
        client = client_class(adal_auth_object, str(subscription_id))
    return client


def _get_arm_token_with_refresh(profile_object, cloud_type, account_object, config_object, session_object,
                                config_directory, force_reload=False, resource=None):
    """Get an arm token while refreshing it if needed. This is a common function across InteractiveLoginAuthentication and AzureCliAuthentication.

    :return:
    :rtype: str
    """
    # Update token if it expires in < TOKEN_REFRESH_THRESHOLD_SEC
    TOKEN_REFRESH_THRESHOLD_SEC = 5 * 60

    AZ_CLI_AAP_ID = '04b07795-8ddb-461a-bbee-02f9e1bf7b46'

    if force_reload or not account_object.data:
        account_object.load(os.path.join(config_directory, 'azureProfile.json'))
        config_object.load(os.path.join(config_directory, 'az.json'))
        session_object.load(os.path.join(config_directory, 'az.sess'),
                            max_age=AzureCliAuthentication._TOKEN_TIMEOUT_SECs)

    # From notebook, we want to persist tokens synchronously to the on-disk file,
    # so that users don't have to run az login multiple times.
    # By default, a tokens are persisted on-disk on exit on a process, which
    # doesn't happen in notebook or happens in a way where token persistence logic
    # is not called.
    # profile = Profile(async_persist=False)
    token_about_to_expire = False
    try:
        auth, _, _ = profile_object.get_login_credentials(resource)
        access_token = auth._token_retriever()[1]
        if (_get_exp_time(access_token) - time.time()) < TOKEN_REFRESH_THRESHOLD_SEC:
            # Token is about to expire, do not return, request a new one
            token_about_to_expire = True
        else:
            return access_token
    except Exception as e:
        if not token_about_to_expire:
            raise AuthenticationException("Could not retrieve user token. Please run 'az login'",
                                          inner_exception=e)

    try:
        # This call fails when AZ cli is run in parallel
        user_type = profile_object.get_subscription()['user']['type']
        if user_type == "user":
            _, refresh_token, access_token, tenant = profile_object.get_refresh_token(resource)
            if (_get_exp_time(access_token) - time.time()) < TOKEN_REFRESH_THRESHOLD_SEC:
                authority = cloud_type.endpoints.active_directory
                if authority[-1] == '/':
                    authority = authority[:-1]

                # Note: Moved adal import from the beginning of the file to here.
                # This import takes 0.25 s, so we move it close the the place where
                # it is used, rather than slowing down other functions that don't use this.
                import adal
                context = adal.AuthenticationContext('{0}/{1}'.format(authority, tenant), api_version=None)
                from adal import ADAL_LOGGER_NAME
                if not resource:
                    resource = cloud_type.endpoints.management
                with NewLoggingLevel(ADAL_LOGGER_NAME, level=logging.WARNING):
                    adal_token = context.acquire_token_with_refresh_token(
                        refresh_token, AZ_CLI_AAP_ID, resource)
                    token = adal_token['accessToken']
            else:
                token = access_token
            return token
        else:
            if not resource:
                resource = cloud_type.endpoints.management
            creds, subscription, tenant = profile_object.get_raw_token(resource, None)
            token_dict = {
                'tokenType': creds[0],
                'accessToken': creds[1],
                'expiresOn': creds[2]['expiresOn'],
                'subscription': subscription,
                'tenant': tenant
            }
            if (token_dict["expiresOn"] - time.time()) < TOKEN_REFRESH_THRESHOLD_SEC:
                auth, _, _ = profile_object.get_login_credentials(resource)
                access_token = auth._token_retriever()[1]
                return access_token
            return token_dict["accessToken"]

    except Exception as e:
        raise AuthenticationException("Could not retrieve user token. Please run 'az login'",
                                      inner_exception=e)


def _get_exp_time(access_token):
    """Return the expiry time of the supplied arm access token.

    :param access_token:
    :type access_token: str
    :return:
    :rtype: time
    """
    # We set verify=False, as we don't have keys to verify signature, and we also don't need to
    # verify signature, we just need the expiry time.
    decode_json = jwt.decode(access_token, verify=False)
    return decode_json['exp']

