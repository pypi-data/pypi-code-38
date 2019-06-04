import json
from abc import ABCMeta
from enum import Enum

from typing import List, Dict

from sidecar.messaging_service import MessagingConnectionProperties


class InputParameter:
    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.name == other.name and \
                   self.value == other.value
        return False

    def __repr__(self):
        return "name={} value={} ".format(self.name, self.value)


class ISidecarService(metaclass=ABCMeta):
    def __init__(self,
                 name: str,
                 type: str,
                 dependencies: List[str] = None,
                 inputs: List[InputParameter] = None):
        self.inputs = inputs
        self.dependencies = dependencies
        self.type = type
        self.name = name


class Script:
    def __init__(self, headers: Dict, path: str, name: str):
        self.headers = headers
        self.path = path
        self.name = name

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.headers == other.headers and \
                   self.path == other.path and \
                   self.name == other.name
        return False

    def __repr__(self):
        return "headers={} " \
               "path={} " \
               "name={} ".format(json.dumps(self.headers),
                                 self.path,
                                 self.name)


class TerraformServiceModule:
    def __init__(self,
                 source: str,
                 version: str):
        self.source = source
        self.version = version

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.source == other.source and \
                   self.version == other.version
        return False

    def __repr__(self):
        return "source={} " \
               "version={} ".format(self.source,
                                    self.version)


class SidecarTerraformService(ISidecarService):
    def __init__(self, name: str,
                 type: str,
                 terraform_module: TerraformServiceModule,
                 terraform_version: str,
                 tfvars_file: Script,
                 dependencies: List[str] = None,
                 inputs: List[InputParameter] = None,
                 ):
        super().__init__(name, type, dependencies, inputs)
        self.tfvars_file = tfvars_file
        self.terraform_version = terraform_version
        self.terraform_module = terraform_module

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.name == other.name and \
                   self.type == other.type and \
                   self.tfvars_file == other.tfvars_file and \
                   self.terraform_version == other.terraform_version and \
                   self.terraform_module == other.terraform_module and \
                   self.dependencies == other.dependencies and \
                   self.inputs == other.inputs
        return False

    def __repr__(self):
        return "name={} " \
               "type={} " \
               "tfvars_file={} " \
               "terraform_version={} " \
               "terraform_module={} " \
               "dependencies={} " \
               "inputs={} ".format(self.name,
                                   self.type,
                                   self.tfvars_file,
                                   self.terraform_version,
                                   self.terraform_module,
                                   self.dependencies,
                                   self.inputs)


class SidecarApplication:
    def __init__(self, name: str,
                 instances_count: int,
                 dependencies: List[str],
                 env: Dict[str, str],
                 healthcheck_timeout: int,
                 healthcheck_script: str,
                 default_health_check_ports_to_test: List[int],
                 has_public_access: bool):
        self.has_public_access = has_public_access
        self.name = name
        self.default_health_check_ports_to_test = default_health_check_ports_to_test
        self.healthcheck_timeout = healthcheck_timeout
        self.healthcheck_script = healthcheck_script
        self.env = env
        self.dependencies = dependencies
        self.instances_count = instances_count

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.name == other.name and \
                   self.instances_count == other.instances_count and \
                   self.dependencies == other.dependencies and \
                   self.env == other.env and \
                   self.healthcheck_timeout == other.healthcheck_timeout and \
                   self.default_health_check_ports_to_test == other.default_health_check_ports_to_test and \
                   self.healthcheck_script == other.healthcheck_script and \
                   self.has_public_access == other.has_public_access
        return False

    def __repr__(self):
        return "name={} " \
               "instances_count={} " \
               "dependencies={} " \
               "env={} " \
               "healthcheck_timeout={} " \
               "healthcheck_script={} " \
               "default_health_check_ports_to_test={} " \
               "has_public_access={} ".format(self.name,
                                              self.instances_count,
                                              self.dependencies,
                                              self.env,
                                              self.healthcheck_timeout,
                                              self.healthcheck_script,
                                              self.default_health_check_ports_to_test,
                                              self.has_public_access)


class EnvironmentType(Enum):
    Sandbox = "sandbox"
    ProductionBlue = "production-blue"
    ProductionGreen = "production-green"

    def __eq__(self, other):
        return self.value == other

    def __ne__(self, other):
        return self.value != other


class ISidecarConfiguration(metaclass=ABCMeta):
    def __init__(self,
                 environment: str,
                 provider: str,
                 sandbox_id: str,
                 production_id: str,
                 space_id: str,
                 cloud_external_key: str,
                 apps: List[SidecarApplication],
                 services: List[ISidecarService],
                 messaging: MessagingConnectionProperties,
                 env_type: str):
        self.messaging = messaging
        self.apps = apps
        self.services = services
        self.space_id = space_id
        self.sandbox_id = sandbox_id
        self.production_id = production_id
        self.provider = provider
        self.environment = environment
        self.cloud_external_key = cloud_external_key
        self.env_type = EnvironmentType(env_type)


class AzureSidecarConfiguration(ISidecarConfiguration):
    def __init__(self,
                 management_resource_group: str,
                 subscription_id: str,
                 application_id: str,
                 application_secret: str,
                 tenant_id: str,
                 environment: str,
                 sandbox_id: str,
                 production_id: str,
                 space_id: str,
                 cloud_external_key: str,
                 apps: List[SidecarApplication],
                 services: List[ISidecarService],
                 messaging: MessagingConnectionProperties,
                 env_type: str):
        super().__init__(environment, "azure", sandbox_id, production_id, space_id, cloud_external_key, apps, services,
                         messaging,
                         env_type)
        self.tenant_id = tenant_id
        self.application_secret = application_secret
        self.application_id = application_id
        self.subscription_id = subscription_id
        self.management_resource_group = management_resource_group

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.management_resource_group == other.management_resource_group and \
                   self.subscription_id == other.subscription_id and \
                   self.application_id == other.application_id and \
                   self.tenant_id == other.tenant_id and \
                   self.environment == other.environment and \
                   self.provider == other.provider and \
                   self.sandbox_id == other.sandbox_id and \
                   self.space_id == other.space_id and \
                   self.cloud_external_key == other.cloud_external_key and \
                   self.apps == other.apps and \
                   self.messaging == other.messaging
        return False

    def __repr__(self):
        return "management_resource_group={} " \
               "subscription_id={} " \
               "application_id={} " \
               "tenant_id={} " \
               "environment={} " \
               "provider={} " \
               "sandbox_id={} " \
               "production_id={} " \
               "space_id={} " \
               "cloud_external_key={} " \
               "apps={} " \
               "services={} " \
               "messaging={}".format(self.management_resource_group,
                                     self.subscription_id,
                                     self.application_id,
                                     self.tenant_id,
                                     self.environment,
                                     self.provider,
                                     self.sandbox_id,
                                     self.production_id,
                                     self.space_id,
                                     self.cloud_external_key,
                                     self.apps,
                                     self.services,
                                     self.messaging)


class AwsSidecarConfiguration(ISidecarConfiguration):
    def __init__(self,
                 region_name: str,
                 environment: str,
                 sandbox_id: str,
                 production_id: str,
                 space_id: str,
                 cloud_external_key: str,
                 apps: List[SidecarApplication],
                 services: List[ISidecarService],
                 messaging: MessagingConnectionProperties,
                 env_type: str,
                 data_table_name: str,
                 onboarding_region: str = None):
        super().__init__(environment, "aws", sandbox_id, production_id, space_id, cloud_external_key, apps, services, messaging,
                         env_type)
        self.onboarding_region = onboarding_region
        self.region_name = region_name
        self.data_table_name = data_table_name

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.region_name == other.region_name and \
                   self.environment == other.environment and \
                   self.provider == other.provider and \
                   self.sandbox_id == other.sandbox_id and \
                   self.space_id == other.space_id and \
                   self.cloud_external_key == other.cloud_external_key and \
                   self.apps == other.apps and \
                   self.messaging == other.messaging and \
                   self.data_table_name == other.data_table_name
        return False

    def __repr__(self):
        return "region_name={} " \
               "environment={} " \
               "provider={} " \
               "sandbox_id={} " \
               "production_id={} " \
               "space_id={} " \
               "cloud_external_key={} " \
               "apps={} " \
               "services={} " \
               "messaging={} " \
               "onboarding_region={} " \
               "data_table_name={}".format(self.region_name,
                                           self.environment,
                                           self.provider,
                                           self.sandbox_id,
                                           self.production_id,
                                           self.space_id,
                                           self.cloud_external_key,
                                           self.apps,
                                           self.services,
                                           self.messaging,
                                           self.onboarding_region,
                                           self.data_table_name)


class KubernetesSidecarConfiguration(ISidecarConfiguration):
    def __init__(self, kub_api_address: str,
                 environment: str,
                 sandbox_id: str,
                 production_id: str,
                 space_id: str,
                 cloud_external_key: str,
                 apps: List[SidecarApplication],
                 services: List[ISidecarService],
                 messaging: MessagingConnectionProperties,
                 env_type: str):
        super().__init__(environment, "kubernetes", sandbox_id, production_id, space_id, cloud_external_key, apps, services,
                         messaging,
                         env_type)
        self.kub_api_address = kub_api_address

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.kub_api_address == other.kub_api_address and \
                   self.environment == other.environment and \
                   self.provider == other.provider and \
                   self.sandbox_id == other.sandbox_id and \
                   self.space_id == other.space_id and \
                   self.cloud_external_key == other.cloud_external_key and \
                   self.apps == other.apps and \
                   self.messaging == other.messaging
        return False

    def __repr__(self):
        return "kub_api_address={} " \
               "environment={} " \
               "provider={} " \
               "sandbox_id={} " \
               "production_id={} " \
               "space_id={} " \
               "cloud_external_key={} " \
               "apps={} " \
               "services={} " \
               "messaging={}".format(self.kub_api_address,
                                     self.environment,
                                     self.provider,
                                     self.sandbox_id,
                                     self.production_id,
                                     self.space_id,
                                     self.cloud_external_key,
                                     self.apps,
                                     self.services,
                                     self.messaging)
