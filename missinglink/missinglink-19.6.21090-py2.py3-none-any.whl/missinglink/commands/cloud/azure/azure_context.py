import json
import random
import re
import string
import uuid

from azure.common.credentials import get_azure_cli_credentials
from azure.graphrbac import GraphRbacManagementClient
from azure.keyvault import KeyVaultClient
from azure.graphrbac.models import ServicePrincipalCreateParameters
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.authorization.models import RoleAssignmentCreateParameters
from azure.mgmt.containerregistry import ContainerRegistryManagementClient
from azure.mgmt.containerregistry.models import Registry, Sku
from azure.mgmt.msi import ManagedServiceIdentityClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import DeploymentProperties
from azure.mgmt.keyvault import KeyVaultManagementClient
from azure.common.client_factory import get_client_from_cli_profile
from azure.mgmt.storage import StorageManagementClient
from msrestazure.azure_active_directory import MSIAuthentication
import click
from missinglink.crypto import SshIdentity

from missinglink.commands.cloud.backend_context import BackendContext
from missinglink.commands.cloud.cloud_connector import CloudConnector
from missinglink.commands.utilities import pop_key_or_prompt_if, PathTools

APP_ID = '7eba301b-077d-4d8e-a1dd-a0b70113e6ca'


class AzureContext(BackendContext, CloudConnector):
    def __init__(self, ctx, kwargs):
        super(AzureContext, self).__init__(ctx, kwargs)
        self.location = ctx.obj.azure.location
        self.kwargs = kwargs

    def init_and_authorise_app(self, skip_acr=False):
        service_principal = self._create_service_principal()
        self._get_and_deploy_template()
        self._setup_default_storage()
        self._assign_role_key_vault_perms()
        self._register_compute_provider()
        self._create_key()
        self._authorize_app(service_principal)
        self._create_cloud_connector()
        self._init_prepare_connector_message(set_ssh=not self.auth_state['ssh_present'], set_ml=not self.auth_state['mali_config'])
        if not skip_acr:
            self._create_default_container_registry()

    def _create_service_principal(self):
        rbac_client = get_client_from_cli_profile(GraphRbacManagementClient)
        app_sp = list(rbac_client.service_principals.list(filter='appId eq \'%s\'' % APP_ID))
        if not app_sp:
            service_principal = rbac_client.service_principals.create(
                ServicePrincipalCreateParameters(app_id=APP_ID, account_enabled=True))
        else:
            service_principal = app_sp[0]
        self.tenant_id = rbac_client.config.tenant_id
        return service_principal

    def _authorize_app(self, service_principal):
        click.echo('(6/8) Authorizing MissingLink App to manage virtual machines')
        auth_client = get_client_from_cli_profile(AuthorizationManagementClient)
        scope = '/subscriptions/%s/resourceGroups/%s' % (auth_client.config.subscription_id, self.rg_name)
        role_defs = list(auth_client.role_definitions.list(
            scope,
            filter='roleName eq \'MissingLinkRM-%s\'' % self.org
        ))
        if not role_defs:
            role_id = uuid.uuid4()
        else:
            role_id = role_defs[0].name

        res = auth_client.role_definitions.create_or_update(
            scope,
            role_id,
            {
                "role_name": "MissingLinkRM-" + self.org,
                "description": "Manages instances for running jobs. See MissingLink.ai",
                "permissions": [
                    {
                        "actions": [
                            'Microsoft.Resources/deployments/*',
                            'Microsoft.Compute/virtualMachines/*',
                            'Microsoft.Network/publicIpAddresses/*',
                            'Microsoft.Network/networkInterfaces/*',
                            'Microsoft.Network/virtualNetworks/subnets/join/action',
                            'Microsoft.Compute/disks/*',
                            'Microsoft.Compute/images/*',
                            'Microsoft.ResourceHealth/availabilityStatuses/read',
                            'Microsoft.ManagedIdentity/userAssignedIdentities/assign/action',
                            'Microsoft.Storage/storageAccounts/listKeys/action',
                            'Microsoft.Storage/storageAccounts/read',
                        ],
                        "not_actions": [
                        ],
                    }
                ],

                "assignable_scopes": [
                    scope
                ]
            }
        )
        role_definition_id = res.id
        roles = list(auth_client.role_assignments.list_for_resource_group(self.rg_name, filter='principalId eq \'%s\'' % service_principal.object_id))
        self._create_role_if_missing(auth_client, role_definition_id, roles, service_principal.object_id, scope)
        click.echo('Done')

    def _create_role_if_missing(self, auth_client, role_id, roles, principal_id, scope):
        role = [r for r in roles if r.role_definition_id == role_id]
        if not role:
            auth_client.role_assignments.create(
                scope,
                uuid.uuid4(),
                RoleAssignmentCreateParameters(role_definition_id=role_id, principal_id=principal_id)
            )

    def _get_template(self):
        result = self._handle_api_call('get', '{}/azure/init_template'.format(self.org))
        return json.loads(result['template'])

    def _create_key(self):
        click.echo('(5/8) Creating a key in the Key Vault')
        credentials, subscription_id = get_azure_cli_credentials(resource='https://vault.azure.net')
        key_vault_client = KeyVaultClient(credentials)
        key_name = 'MissingLinkRM'
        results = list(key_vault_client.get_key_versions(self.key_vault, key_name))
        if not results:
            key_bundle = key_vault_client.create_key(self.key_vault, key_name, 'RSA', key_size=4096)
            self.key_id = key_bundle.key.kid
        else:
            self.key_id = results[0].kid
        click.echo('Done')

    def _get_existing_volumes(self):
        result = self._handle_api_call('get', 'orgs/{}/metadata?only=buckets'.format(self.org))
        buckets = result.get('data', [{'values': []}])[0]['values']
        storages = {self.storage_acc_name}
        for bucket in buckets:
            m = re.match(r'az://(.*)\..*', bucket)
            if m:
                storages.add(m.group(1))
        return storages

    def _assign_role_key_vault_perms(self):
        click.echo('(3/8) Giving permissions to access Key Vault to worker instances')
        msi_client = get_client_from_cli_profile(ManagedServiceIdentityClient)
        role_identity = msi_client.user_assigned_identities.get(self.rg_name, self.role_name)
        self.role_id = role_identity.id
        key_vault_client = get_client_from_cli_profile(KeyVaultManagementClient)
        policies = {'access_policies': [
            {
                'tenant_id': self.tenant_id,
                'object_id': role_identity.principal_id,
                'permissions': {'keys': ['Decrypt']}
            }
        ]}
        key_vault_client.vaults.update_access_policy(self.rg_name, self.vault_name, 'add', policies)

        used_storages = self._get_existing_volumes()

        storage_client = get_client_from_cli_profile(StorageManagementClient)
        all_storages = storage_client.storage_accounts.list()
        registered_storages = set()
        for storage_account in all_storages:
            if storage_account.name in used_storages:
                registered_storages.add(storage_account.id)
        for storage_id in registered_storages:
            self._grant_access_to_storage(role_identity, storage_id)

        click.echo('Done')

    def _grant_access_to_storage(self, role_identity, storage_id):
        auth_client = get_client_from_cli_profile(AuthorizationManagementClient)
        roles = list(auth_client.role_assignments.list_for_scope(storage_id,
                                                                 filter='principalId eq \'%s\'' % role_identity.principal_id))
        role_id = 'c12c1c16-33a1-487b-954d-41c89c60f349'  # https://docs.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#reader-and-data-access
        role_definition_id = '/subscriptions/%s/providers/Microsoft.Authorization/roleDefinitions/%s' % (auth_client.config.subscription_id, role_id)
        self._create_role_if_missing(auth_client, role_definition_id, roles, role_identity.principal_id, storage_id)

    def _create_default_container_registry(self):
        click.echo('(8/8) Creating default Container Registry')
        msi_client = get_client_from_cli_profile(ManagedServiceIdentityClient)
        role_identity = msi_client.user_assigned_identities.get(self.rg_name, self.role_name)
        auth_client = get_client_from_cli_profile(AuthorizationManagementClient)
        roles = auth_client.role_assignments.list(filter='principalId eq \'%s\'' % role_identity.principal_id)
        if any('providers/Microsoft.ContainerRegistry' in role.scope for role in roles):
            click.echo('Done')
            return
        acr_client = get_client_from_cli_profile(ContainerRegistryManagementClient)
        acr_name = 'ml' + self.normalize_org()
        acr = acr_client.registries.create(self.rg_name, acr_name, Registry(location=self.location, sku=Sku(name='Standard'))).result()

        self._grant_permissions_to_acr(acr, role_identity)
        click.echo('Done')

    def normalize_org(self):
        base_name = self.org.lower().replace('_', '-')
        if '-' in base_name:
            return base_name.replace('-', '')[:15] + ''.join(random.choice(string.ascii_lowercase) for _ in range(0, 4))
        return base_name[:19]

    def _get_existing_cloud_params(self):
        url = '{org}/azure/connector_info'.format(org=self.org)
        return self._handle_api_call('get', url)

    def _get_and_deploy_template(self):
        click.echo('(1/8) Applying template for Resource Group, Network and Key Vault. This may take a few minutes')
        template = self._get_template()
        rm_client = get_client_from_cli_profile(ResourceManagementClient)
        self.subscription_id = rm_client.config.subscription_id
        rbac_client = get_client_from_cli_profile(GraphRbacManagementClient)
        user = rbac_client.signed_in_user.get()

        old_params = self._get_existing_cloud_params()
        normalized_org = self.normalize_org()

        params = {
            'rgLocation': old_params.get('location', self.location),
            'org': self.org,
            'userObjectId': user.object_id,
            'rgName': old_params.get('resource_group', 'MissingLinkAI-' + self.org),
            'storageRgName': old_params.get('storage_resource_group', 'MissingLinkAI-' + self.org + '-storage'),
            'storageAccName': old_params.get('storage_acc_name', 'ml' + normalized_org),
            'imageStorageName': old_params.get('image_storage_name', 'mlimg' + normalized_org),
            'vaultName': old_params.get('vault_name', 'ML-' + self.org.lower().replace('_', '-')),
            'netName': old_params.get('net_name', 'MissingLinkAI-' + self.org),
            'subnets_default_name': old_params.get('subnet_name', 'default')
        }
        params = {k: {'value': v} for k, v in params.items()}
        poller = rm_client.deployments.create_or_update_at_subscription_scope(str(uuid.uuid4()), DeploymentProperties(template=template, mode='Incremental', parameters=params), location=self.location)
        poller.wait()
        result = poller.result()
        self.location = old_params.get('location', self.location)
        self.net_name = result.properties.outputs['netName']['value']
        self.rg_name = result.properties.outputs['groupName']['value']
        self.key_vault = result.properties.outputs['vaultPath']['value']
        self.vault_name = result.properties.outputs['vaultName']['value']
        self.subnet = result.properties.outputs['subnetName']['value']
        self.role_name = result.properties.outputs['roleName']['value']
        self.storage_rg_name = result.properties.outputs['storageRgName']['value']
        self.storage_acc_name = result.properties.outputs['storageAccName']['value']
        self.image_storage_name = result.properties.outputs['imageStorageName']['value']
        click.echo('Done')

    def _setup_default_storage(self):
        click.echo('(2/8) Setting up default container for artifacts')
        storage_client = get_client_from_cli_profile(StorageManagementClient)
        container_name = 'default'
        containers = storage_client.blob_containers.list(self.storage_rg_name, self.storage_acc_name)
        if not any(container.name == container_name for container in containers.value):
            storage_client.blob_containers.create(self.storage_rg_name, self.storage_acc_name, container_name)
        self.bucket_name = self.storage_acc_name + '.' + container_name

        containers = storage_client.blob_containers.list(self.rg_name, self.image_storage_name)
        if not any(container.name == container_name for container in containers.value):
            storage_client.blob_containers.create(self.rg_name, self.image_storage_name, container_name)

        click.echo('Done')

    def _register_compute_provider(self):
        click.echo('(4/8) Registering compute service in Azure subscription')
        rm_client = get_client_from_cli_profile(ResourceManagementClient)
        rm_client.providers.register('Microsoft.Compute')
        click.echo('Done')

    def _create_cloud_connector(self):
        queue = self.kwargs.pop('queue', None)
        click.echo('(7/8) Saving state to MissingLink servers')
        template = {
            'subscription_id': self.subscription_id,
            'tenant_id': self.tenant_id,
            'key_name': self.key_id,
            'location': self.location,
            'net_data': [{'name': self.net_name, 'region': self.location, 'subnet': self.subnet}],
            'resource_group': self.rg_name,
            'key_vault': self.key_vault,
            'role_name': self.role_name,
            'role_id': self.role_id,
            'az_storage': [{'bucket_name': self.bucket_name, 'group_name': self.storage_rg_name}],
            'image_storage': self.image_storage_name,
            'queue': queue
        }
        url = '{org}/azure/save_connector'.format(org=self.org)
        self.auth_state = self._handle_api_call('post', url, template)

    @classmethod
    def get_cloud_kms(cls, key_id, role_id):
        credentials = MSIAuthentication(
            msi_res_id=role_id,
            resource='https://vault.azure.net'
        )
        return cls.get_kms(key_id, credentials)

    @classmethod
    def get_cli_kms(cls, key_id):
        credentials, subscription_id = get_azure_cli_credentials(resource='https://vault.azure.net')
        return cls.get_kms(key_id, credentials)

    @classmethod
    def get_kms(cls, key_id, credentials):
        from missinglink.crypto import AzureEnvelope

        return AzureEnvelope(credentials, key_id)

    def _init_prepare_connector_message(self, set_ssh, set_ml):
        template, config_data = self.cloud_connector_defaults(self.ctx, cloud_type='azure', kwargs=dict(connector=self.subscription_id))
        kms = self.get_cli_kms(self.key_id)
        if set_ssh:
            ssh_key_path = pop_key_or_prompt_if(
                self.kwargs,
                'ssh_key_path',
                text='Enter the path to the SSH key. \n'
                     'This key would be used to encrypt sensitive data to pass it to the worker machine, \n'
                     'it would be put on the worker machine to decrypt sensitive data and \n'
                     'to use it as a SSH identity. It also would be added to authorized keys \n'
                     'so you will be able to access the worker machine via SSH. \n'
                     'SSH key path [--ssh-key-path]',
                default=PathTools.get_ssh_path()
            )
            ssh_key = SshIdentity(ssh_key_path)
            ssh_key_priv = ssh_key.export_private_key_bytes()
            ssh_key_pub = ssh_key.export_public_key_bytes().decode('utf-8')
            self._update_org_metadata_ssh_key(ssh_key_pub)
            ssh = self.encrypt(kms, ssh_key_priv)
            template['ssh'] = ssh
        if set_ml:
            mali = self.encrypt(kms, config_data)
            template['mali'] = mali

        template['cloud_data'] = {}
        url = '{org}/cloud_connector/{name}'.format(org=self.org, name=template['name'])
        self._handle_api_call('post', url, template)
        click.echo('Done')

    def authorise_acr(self, acr_names):
        connector_info = self._get_existing_cloud_params()
        if not connector_info:
            self.init_and_authorise_app(skip_acr=True)
            connector_info = self._get_existing_cloud_params()
            click.echo('(8/8) Authorising ACR(s)')

        msi_client = get_client_from_cli_profile(ManagedServiceIdentityClient)
        role_identity = msi_client.user_assigned_identities.get(connector_info['resource_group'], connector_info.get('role_name', 'MissingLinkRMWorker'))

        acr_client = get_client_from_cli_profile(ContainerRegistryManagementClient)
        registries = list(acr_client.registries.list())
        for acr_name in acr_names:
            self._try_authorise_acr(acr_name, registries, role_identity)

    def _try_authorise_acr(self, acr_name, registries, role_identity):
        for r in registries:
            if r.name == acr_name:
                self._grant_permissions_to_acr(r, role_identity)
                break
        else:
            click.echo('Can\'t find ACR %s' % acr_name)

    def _grant_permissions_to_acr(self, acr, role_identity):
        auth_client = get_client_from_cli_profile(AuthorizationManagementClient)
        roles = list(auth_client.role_assignments.list_for_scope(acr.id, filter='principalId eq \'%s\'' % role_identity.principal_id))
        role_id = '7f951dda-4ed3-4680-a7ca-43fe172d538d'  # https://docs.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#acrpull
        role_definition_id = '/subscriptions/%s/providers/Microsoft.Authorization/roleDefinitions/%s' % (auth_client.config.subscription_id, role_id)
        self._create_role_if_missing(auth_client, role_definition_id, roles, role_identity.principal_id, acr.id)
        click.echo('Now you can use ACR %s.azurecr.io to store and use your Docker images.' % acr.name)
