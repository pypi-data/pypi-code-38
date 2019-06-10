# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Manages Azure Kubernetes Service compute targets in Azure Machine Learning service."""

import copy
import json
import requests
import traceback
from azureml._compute._constants import MLC_COMPUTE_RESOURCE_ID_FMT
from azureml._compute._constants import MLC_ENDPOINT_FMT
from azureml._compute._constants import MLC_WORKSPACE_API_VERSION
from azureml._compute._util import aks_payload_template
from azureml._compute._util import get_requests_session
from azureml.core.compute import ComputeTarget
from azureml.core.compute.compute import ComputeTargetProvisioningConfiguration
from azureml.core.compute.compute import ComputeTargetAttachConfiguration
from azureml.exceptions import ComputeTargetException
from azureml._restclient.clientbase import ClientBase


class AksCompute(ComputeTarget):
    """Manages Azure Kubernetes Service compute target objects."""

    _compute_type = 'AKS'

    def _initialize(self, workspace, obj_dict):
        """Class AksCompute constructor.

        :param workspace:
        :type workspace: azureml.core.workspace.Workspace
        :param obj_dict:
        :type obj_dict: dict
        :return:
        :rtype: None
        """
        name = obj_dict['name']
        compute_resource_id = MLC_COMPUTE_RESOURCE_ID_FMT.format(workspace.subscription_id,
                                                                 workspace.resource_group, workspace.name,
                                                                 name)
        mlc_endpoint = MLC_ENDPOINT_FMT.format(workspace.subscription_id, workspace.resource_group,
                                               workspace.name, name)
        location = obj_dict['location']
        compute_type = obj_dict['properties']['computeType']
        tags = obj_dict['tags']
        description = obj_dict['properties']['description']
        created_on = obj_dict['properties'].get('createdOn')
        modified_on = obj_dict['properties'].get('modifiedOn')
        cluster_resource_id = obj_dict['properties']['resourceId']
        cluster_location = obj_dict['properties']['computeLocation'] \
            if 'computeLocation' in obj_dict['properties'] else None
        provisioning_state = obj_dict['properties']['provisioningState']
        provisioning_errors = obj_dict['properties']['provisioningErrors']
        is_attached = obj_dict['properties']['isAttachedCompute']
        aks_properties = obj_dict['properties']['properties']
        agent_vm_size = aks_properties['agentVmSize'] if aks_properties else None
        agent_count = aks_properties['agentCount'] if aks_properties else None
        cluster_purpose = aks_properties['clusterPurpose'] if aks_properties else None
        cluster_fqdn = aks_properties['clusterFqdn'] if aks_properties else None
        system_services = aks_properties['systemServices'] if aks_properties else None
        if system_services:
            system_services = [SystemService.deserialize(service) for service in system_services]
        ssl_configuration = aks_properties['sslConfiguration'] \
            if aks_properties and 'sslConfiguration' in aks_properties else None
        if ssl_configuration:
            ssl_configuration = SslConfiguration.deserialize(ssl_configuration)
        super(AksCompute, self)._initialize(compute_resource_id, name, location, compute_type, tags, description,
                                            created_on, modified_on, provisioning_state, provisioning_errors,
                                            cluster_resource_id, cluster_location, workspace, mlc_endpoint, None,
                                            workspace._auth, is_attached)
        self.agent_vm_size = agent_vm_size
        self.agent_count = agent_count
        self.cluster_purpose = cluster_purpose
        self.cluster_fqdn = cluster_fqdn
        self.system_services = system_services
        self.ssl_configuration = ssl_configuration

    @staticmethod
    def _create(workspace, name, provisioning_configuration):
        """Create compute.

        :param workspace:
        :type workspace: azureml.core.workspace.Workspace
        :param name:
        :type name: str
        :param provisioning_configuration:
        :type provisioning_configuration: AksProvisioningConfiguration
        :return:
        :rtype: azureml.core.compute.aks.AksCompute
        """
        compute_create_payload = AksCompute._build_create_payload(provisioning_configuration,
                                                                  workspace.location, workspace.subscription_id)
        return ComputeTarget._create_compute_target(workspace, name, compute_create_payload, AksCompute)

    @staticmethod
    def attach(workspace, name, resource_id):
        """(Deprecated) Associate an already existing AKS compute resource with the provided workspace.

        :param workspace: The workspace object to associate the compute resource with
        :type workspace: azureml.core.workspace.Workspace
        :param name: The name to associate with the compute resource inside the provided workspace. Does not have to
            match with the already given name of the compute resource
        :type name: str
        :param resource_id: The Azure resource ID for the compute resource being attached
        :type resource_id: str
        :return: An AksCompute object representation of the compute object
        :rtype: azureml.core.compute.aks.AksCompute
        :raises: ComputeTargetException
        """
        raise ComputeTargetException('This method is DEPRECATED. Please use the following code to attach a AKS '
                                     'compute resource.\n'
                                     '# Attach AKS\n'
                                     'attach_config = AksCompute.attach_configuration(resource_group='
                                     '"name_of_resource_group",\n'
                                     '                                                cluster_name='
                                     '"name_of_aks_cluster")\n'
                                     'compute = ComputeTarget.attach(workspace, name, attach_config)')

    @staticmethod
    def _attach(workspace, name, config):
        """Associate an already existing AKS compute resource with the provided workspace.

        :param workspace: The workspace object to associate the compute resource with
        :type workspace: azureml.core.workspace.Workspace
        :param name: The name to associate with the compute resource inside the provided workspace. Does not have to
            match with the already given name of the compute resource
        :type name: str
        :param config: Attach configuration object
        :type config: AksAttachConfiguration
        :return: An AksCompute object representation of the compute object
        :rtype: azureml.core.compute.aks.AksCompute
        :raises: ComputeTargetException
        """
        resource_id = config.resource_id
        if not resource_id:
            resource_id = AksCompute._build_resource_id(workspace._subscription_id, config.resource_group,
                                                        config.cluster_name)
        attach_payload = AksCompute._build_attach_payload(config, resource_id)
        return ComputeTarget._attach(workspace, name, attach_payload, AksCompute)

    @staticmethod
    def _build_resource_id(subscription_id, resource_group, cluster_name):
        """Build the Azure resource ID for the compute resource.

        :param subscription_id: The Azure subscription ID
        :type subscription_id: str
        :param resource_group: Name of the resource group in which the AKS is located.
        :type resource_group: str
        :param cluster_name: The AKS cluster name
        :type cluster_name: str
        :return: The Azure resource ID for the compute resource
        :rtype: str
        """
        AKS_RESOURCE_ID_FMT = ('/subscriptions/{}/resourcegroups/{}/providers/Microsoft.ContainerService/'
                               'managedClusters/{}')
        return AKS_RESOURCE_ID_FMT.format(subscription_id, resource_group, cluster_name)

    @staticmethod
    def provisioning_configuration(agent_count=None, vm_size=None, ssl_cname=None, ssl_cert_pem_file=None,
                                   ssl_key_pem_file=None, location=None, vnet_resourcegroup_name=None,
                                   vnet_name=None, subnet_name=None, service_cidr=None,
                                   dns_service_ip=None, docker_bridge_cidr=None, cluster_purpose=None):
        """Create a configuration object for provisioning an AKS compute target.

        :param agent_count: Number of agents (VMs) to host containers. Defaults to 3
        :type agent_count: int
        :param vm_size: Size of agent VMs. A full list of options can be found here: https://aka.ms/azureml-aks-details
            Defaults to Standard_D3_v2
        :type vm_size: str
        :param ssl_cname: A CName to use if enabling SSL validation on the cluster. Must provide all three
            CName, cert file, and key file to enable SSL validation
        :type ssl_cname: str
        :param ssl_cert_pem_file: A file path to a file containing cert information for SSL validation. Must provide
            all three CName, cert file, and key file to enable SSL validation
        :type ssl_cert_pem_file: str
        :param ssl_key_pem_file: A file path to a file containing key information for SSL validation. Must provide
            all three CName, cert file, and key file to enable SSL validation
        :type ssl_key_pem_file: str
        :param location: Location to provision cluster in. If not specified, will default to workspace location.
            Available regions for this compute can be found here:
            https://azure.microsoft.com/en-us/global-infrastructure/services/?regions=all&products=kubernetes-service
        :type location: str
        :param vnet_resourcegroup_name: Name of the resource group where the virtual network is located
        :type vnet_resourcegroup_name: str
        :param vnet_name: Name of the virtual network
        :type vnet_name: str
        :param subnet_name: Name of the subnet inside the vnet
        :type subnet_name: str
        :param service_cidr: A CIDR notation IP range from which to assign service cluster IPs.
        :type service_cidr: str
        :param dns_service_ip: Containers DNS server IP address.
        :type dns_service_ip: str
        :param docker_bridge_cidr: A CIDR notation IP for Docker bridge.
        :type docker_bridge_cidr: str
        :param cluster_purpose: Targeted usage of the cluster. This is used to provision AzureML components to
            ensure the desired level of fault-tolerance and QoS. AksCompute.ClusterPurpose class is provided for
            convenience of specifying available values. More detailed information of these values and their use cases
            can be found here: https://aka.ms/azureml-create-attach-aks
        :type cluster_purpose: str
        :return: A configuration object to be used when creating a Compute object
        :rtype: AksProvisioningConfiguration
        :raises: ComputeTargetException
        """
        config = AksProvisioningConfiguration(agent_count, vm_size, ssl_cname, ssl_cert_pem_file, ssl_key_pem_file,
                                              location, vnet_resourcegroup_name, vnet_name, subnet_name, service_cidr,
                                              dns_service_ip, docker_bridge_cidr, cluster_purpose)
        return config

    @staticmethod
    def _build_create_payload(config, location, subscription_id):
        """Construct the payload needed to create an AKS cluster.

        :param config:
        :type config: AksProvisioningConfiguration
        :param location:
        :type location:
        :param subscription_id:
        :type subscription_id:
        :return:
        :rtype: dict
        """
        json_payload = copy.deepcopy(aks_payload_template)
        del(json_payload['properties']['resourceId'])
        json_payload['location'] = location
        if not config.agent_count and not config.vm_size and not config.ssl_cname and not config.vnet_name and \
                not config.vnet_resourcegroup_name and not config.subnet_name and not config.service_cidr and \
                not config.dns_service_ip and not config.docker_bridge_cidr and not config.leaf_domain_label and \
                not config.cluster_purpose:
            del(json_payload['properties']['properties'])
        else:
            if config.agent_count:
                json_payload['properties']['properties']['agentCount'] = config.agent_count
            else:
                del(json_payload['properties']['properties']['agentCount'])
            if config.vm_size:
                json_payload['properties']['properties']['agentVmSize'] = config.vm_size
            else:
                del(json_payload['properties']['properties']['agentVmSize'])
            if config.cluster_purpose:
                json_payload['properties']['properties']['clusterPurpose'] = config.cluster_purpose
            else:
                del(json_payload['properties']['properties']['clusterPurpose'])
            if config.ssl_cname:
                try:
                    with open(config.ssl_cert_pem_file, 'r') as cert_file:
                        cert_data = cert_file.read()
                    with open(config.ssl_key_pem_file, 'r') as key_file:
                        key_data = key_file.read()
                except (IOError, OSError) as exc:
                    raise ComputeTargetException("Error while reading ssl information:\n"
                                                 "{}".format(traceback.format_exc().splitlines()[-1]))
                json_payload['properties']['properties']['sslConfiguration']['status'] = 'Enabled'
                json_payload['properties']['properties']['sslConfiguration']['cname'] = config.ssl_cname
                json_payload['properties']['properties']['sslConfiguration']['cert'] = cert_data
                json_payload['properties']['properties']['sslConfiguration']['key'] = key_data
                del(json_payload['properties']['properties']['sslConfiguration']['leafDomainLabel'])
                del(json_payload['properties']['properties']['sslConfiguration']['overwriteExistingDomain'])
            elif config.leaf_domain_label:
                json_payload['properties']['properties']['sslConfiguration']['status'] = 'Auto'
                json_payload['properties']['properties']['sslConfiguration']['leafDomainLabel'] = \
                    config.leaf_domain_label
                json_payload['properties']['properties']['sslConfiguration']['overwriteExistingDomain'] = \
                    config.overwrite_existing_domain
                del(json_payload['properties']['properties']['sslConfiguration']['cname'])
                del(json_payload['properties']['properties']['sslConfiguration']['cert'])
                del(json_payload['properties']['properties']['sslConfiguration']['key'])
            else:
                del(json_payload['properties']['properties']['sslConfiguration'])
            if config.vnet_name:
                json_payload['properties']['properties']['aksNetworkingConfiguration']['subnetId'] = \
                    "/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.Network/virtualNetworks" \
                    "/{2}/subnets/{3}".format(subscription_id, config.vnet_resourcegroup_name,
                                              config.vnet_name, config.subnet_name)
                json_payload['properties']['properties']['aksNetworkingConfiguration']['serviceCidr'] = \
                    config.service_cidr
                json_payload['properties']['properties']['aksNetworkingConfiguration']['dnsServiceIP'] = \
                    config.dns_service_ip
                json_payload['properties']['properties']['aksNetworkingConfiguration']['dockerBridgeCidr'] = \
                    config.docker_bridge_cidr
            else:
                del(json_payload['properties']['properties']['aksNetworkingConfiguration'])
        if config.location:
            json_payload['properties']['computeLocation'] = config.location
        else:
            del(json_payload['properties']['computeLocation'])
        return json_payload

    @staticmethod
    def attach_configuration(resource_group=None, cluster_name=None, resource_id=None, cluster_purpose=None):
        """Create a configuration object for attaching a AKS compute target.

        :param resource_group: Name of the resource group in which the AKS is located.
        :type resource_group: str
        :param cluster_name: The AKS cluster name
        :type cluster_name: str
        :param resource_id: The Azure resource ID for the compute resource being attached
        :type resource_id: str
        :param cluster_purpose: Targeted usage of the cluster. This is used to provision AzureML components to
            ensure the desired level of fault-tolerance and QoS. AksCompute.ClusterPurpose class is provided for
            convenience of specifying available values. More detailed information of these values and their use cases
            can be found here: https://aka.ms/azureml-create-attach-aks
        :type cluster_purpose: str
        :return: A configuration object to be used when attaching a Compute object
        :rtype: AksAttachConfiguration
        """
        config = AksAttachConfiguration(resource_group, cluster_name, resource_id, cluster_purpose)
        return config

    @staticmethod
    def _build_attach_payload(config, resource_id):
        """Build attach payload.

        :param config: Attach configuration object
        :type config: AksAttachConfiguration
        :param resource_id:
        :type resource_id: str
        :return:
        :rtype: dict
        """
        json_payload = copy.deepcopy(aks_payload_template)
        json_payload['properties']['resourceId'] = resource_id
        del(json_payload['properties']['computeLocation'])
        del(json_payload['properties']['properties']['agentCount'])
        del(json_payload['properties']['properties']['agentVmSize'])
        if config.cluster_purpose:
            json_payload['properties']['properties']['clusterPurpose'] = config.cluster_purpose
        else:
            del(json_payload['properties']['properties']['clusterPurpose'])
        del(json_payload['properties']['properties']['aksNetworkingConfiguration'])
        if config.ssl_cname:
            try:
                with open(config.ssl_cert_pem_file, 'r') as cert_file:
                    cert_data = cert_file.read()
                with open(config.ssl_key_pem_file, 'r') as key_file:
                    key_data = key_file.read()
            except (IOError, OSError) as exc:
                raise ComputeTargetException("Error while reading ssl information:\n"
                                             "{}".format(traceback.format_exc().splitlines()[-1]))
            json_payload['properties']['properties']['sslConfiguration']['status'] = 'Enabled'
            json_payload['properties']['properties']['sslConfiguration']['cname'] = config.ssl_cname
            json_payload['properties']['properties']['sslConfiguration']['cert'] = cert_data
            json_payload['properties']['properties']['sslConfiguration']['key'] = key_data
            del(json_payload['properties']['properties']['sslConfiguration']['leafDomainLabel'])
            del(json_payload['properties']['properties']['sslConfiguration']['overwriteExistingDomain'])
        elif config.leaf_domain_label:
            json_payload['properties']['properties']['sslConfiguration']['status'] = 'Auto'
            json_payload['properties']['properties']['sslConfiguration']['leafDomainLabel'] = \
                config.leaf_domain_label
            json_payload['properties']['properties']['sslConfiguration']['overwriteExistingDomain'] = \
                config.overwrite_existing_domain
            del(json_payload['properties']['properties']['sslConfiguration']['cname'])
            del(json_payload['properties']['properties']['sslConfiguration']['cert'])
            del(json_payload['properties']['properties']['sslConfiguration']['key'])
        else:
            del(json_payload['properties']['properties']['sslConfiguration'])

        if not json_payload['properties']['properties']:
            del(json_payload['properties']['properties'])

        return json_payload

    def refresh_state(self):
        """Perform an in-place update of the properties of the object.

        Based on the current state of the corresponding cloud object.
        Primarily useful for manual polling of compute state.
        """
        cluster = AksCompute(self.workspace, self.name)
        self.modified_on = cluster.modified_on
        self.provisioning_state = cluster.provisioning_state
        self.provisioning_errors = cluster.provisioning_errors
        self.cluster_resource_id = cluster.cluster_resource_id
        self.cluster_location = cluster.cluster_location
        self.agent_vm_size = cluster.agent_vm_size
        self.agent_count = cluster.agent_count
        self.cluster_purpose = cluster.cluster_purpose
        self.cluster_fqdn = cluster.cluster_fqdn
        self.system_services = cluster.system_services
        self.ssl_configuration = cluster.ssl_configuration

    def delete(self):
        """Remove the AksCompute object from its associated workspace.

        If this object was created through Azure ML, the corresponding cloud based objects will also be deleted.
        If this object was created externally and only attached to the workspace, it will raise exception and nothing
        will be changed.

        :raises: ComputeTargetException
        """
        self._delete_or_detach('delete')

    def detach(self):
        """Detach the AksCompute object from its associated workspace.

        No underlying cloud object will be deleted, the association will just be removed.

        :raises: ComputeTargetException
        """
        self._delete_or_detach('detach')

    def get_credentials(self):
        """Retrieve the credentials for the AKS target.

        :return: Credentials for the AKS target
        :rtype: dict
        :raises: ComputeTargetException
        """
        endpoint = self._mlc_endpoint + '/listKeys'
        headers = self._auth.get_authentication_header()
        params = {'api-version': MLC_WORKSPACE_API_VERSION}
        resp = ClientBase._execute_func(get_requests_session().post, endpoint, params=params, headers=headers)

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            raise ComputeTargetException('Received bad response from Resource Provider:\n'
                                         'Response Code: {}\n'
                                         'Headers: {}\n'
                                         'Content: {}'.format(resp.status_code, resp.headers, resp.content))
        content = resp.content
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        creds_content = json.loads(content)
        return creds_content

    def serialize(self):
        """Convert this AksCompute object into a json serialized dictionary.

        :return: The json representation of this AksCompute object
        :rtype: dict
        """
        system_services = [system_service.serialize() for system_service in self.system_services] \
            if self.system_services else None

        ssl_configuration = self.ssl_configuration.serialize() if self.ssl_configuration else None

        aks_properties = {'agentVmSize': self.agent_vm_size, 'agentCount': self.agent_count,
                          'clusterPurpose': self.cluster_purpose, 'clusterFqdn': self.cluster_fqdn,
                          'systemServices': system_services, 'sslConfiguration': ssl_configuration}

        cluster_properties = {'computeType': self.type, 'computeLocation': self.cluster_location,
                              'description': self.description, 'resourceId': self.cluster_resource_id,
                              'provisioningState': self.provisioning_state,
                              'provisioningErrors': self.provisioning_errors, 'properties': aks_properties}

        return {'id': self.id, 'name': self.name, 'tags': self.tags, 'location': self.location,
                'properties': cluster_properties}

    @staticmethod
    def deserialize(workspace, object_dict):
        """Convert a json object into a AksCompute object.

        Will fail if the provided workspace is not the workspace the Compute is associated with.

        :param workspace: The workspace object the AksCompute object is associated with
        :type workspace: azureml.core.workspace.Workspace
        :param object_dict: A json object to convert to a AksCompute object
        :type object_dict: dict
        :return: The AksCompute representation of the provided json object
        :rtype: azureml.core.compute.aks.AksCompute
        :raises: ComputeTargetException
        """
        AksCompute._validate_get_payload(object_dict)
        target = AksCompute(None, None)
        target._initialize(workspace, object_dict)
        return target

    @staticmethod
    def _validate_get_payload(payload):
        """Validate get payload.

        :param payload:
        :type payload: dict
        :return:
        :rtype: None
        """
        if 'properties' not in payload or 'computeType' not in payload['properties']:
            raise ComputeTargetException('Invalid cluster payload:\n'
                                         '{}'.format(payload))
        if payload['properties']['computeType'] != AksCompute._compute_type:
            raise ComputeTargetException('Invalid cluster payload, not "{}":\n'
                                         '{}'.format(AksCompute._compute_type, payload))
        for arm_key in ['location', 'id', 'tags']:
            if arm_key not in payload:
                raise ComputeTargetException('Invalid cluster payload, missing ["{}"]:\n'
                                             '{}'.format(arm_key, payload))
        for key in ['properties', 'provisioningErrors', 'description', 'provisioningState', 'resourceId']:
            if key not in payload['properties']:
                raise ComputeTargetException('Invalid cluster payload, missing ["properties"]["{}"]:\n'
                                             '{}'.format(key, payload))
        aks_properties = payload['properties']['properties']
        if aks_properties:
            for aks_key in ['agentVmSize', 'agentCount', 'clusterPurpose', 'clusterFqdn', 'systemServices']:
                if aks_key not in aks_properties:
                    raise ComputeTargetException('Invalid cluster payload, missing '
                                                 '["properties"]["properties"]["{}"]:\n'
                                                 '{}'.format(aks_key, payload))

    class ClusterPurpose(object):
        """Constants for targeted purpose of AKS cluster.

        This constant is used when provisioning AzureML components to ensure
        the desired level of fault-tolerance and QoS.

        'FAST_PROD' will provision AzureML components to handle higher levels of traffic
        with production quality fault-tolerance. This will default the AKS cluster to have 3 nodes.
        'DEV_TEST' will provisions AzureML components at minimal level for testing.
        This will default the AKS cluster to have 1 node.

        More detailed information of the use cases can be found here: https://aka.ms/azureml-create-attach-aks
        """

        FAST_PROD = "FastProd"
        DEV_TEST = "DevTest"


class AksProvisioningConfiguration(ComputeTargetProvisioningConfiguration):
    """Provisioning configuration object for AKS compute targets.

    This object is used to define the configuration parameters for provisioning AksCompute objects.

    :param agent_count: Number of agents (VMs) to host containers. Defaults to 3
    :type agent_count: int
    :param vm_size: Size of agent VMs. A full list of options can be found here: https://aka.ms/azureml-aks-details
        Defaults to Standard_D3_v2
    :type vm_size: str
    :param ssl_cname: A CName to use if enabling SSL validation on the cluster. Must provide all three
        CName, cert file, and key file to enable SSL validation
    :type ssl_cname: str
    :param ssl_cert_pem_file: A file path to a file containing cert information for SSL validation. Must provide
        all three CName, cert file, and key file to enable SSL validation
    :type ssl_cert_pem_file: str
    :param ssl_key_pem_file: A file path to a file containing key information for SSL validation. Must provide
        all three CName, cert file, and key file to enable SSL validation
    :type ssl_key_pem_file: str
    :param location: Location to provision cluster in. If not specified, will default to workspace location.
        Available regions for this compute can be found here:
        https://azure.microsoft.com/en-us/global-infrastructure/services/?regions=all&products=kubernetes-service
    :type location: str
    :param vnet_resourcegroup_name: Name of the resource group where the virtual network is located
    :type vnet_resourcegroup_name: str
    :param vnet_name: Name of the virtual network
    :type vnet_name: str
    :param subnet_name: Name of the subnet inside the vnet
    :type subnet_name: str
    :param service_cidr: A CIDR notation IP range from which to assign service cluster IPs.
    :type service_cidr: str
    :param dns_service_ip: Containers DNS server IP address.
    :type dns_service_ip: str
    :param docker_bridge_cidr: A CIDR notation IP for Docker bridge.
    :type docker_bridge_cidr: str
    :param cluster_purpose: Targeted usage of the cluster. This is used to provision AzureML components to
        ensure the desired level of fault-tolerance and QoS. AksCompute.ClusterPurpose class is provided for
        convenience of specifying available values. More detailed information of these values and their use cases
        can be found here: https://aka.ms/azureml-create-attach-aks
    :type cluster_purpose: str
    """

    def __init__(self, agent_count, vm_size, ssl_cname, ssl_cert_pem_file, ssl_key_pem_file, location,
                 vnet_resourcegroup_name, vnet_name, subnet_name, service_cidr, dns_service_ip,
                 docker_bridge_cidr, cluster_purpose):
        """Initialize a configuration object for provisioning an AKS compute target.

        Must provide all three CName, cert file, and key file to enable SSL validation.

        :param agent_count: Number of agents (VMs) to host containers. Defaults to 3
        :type agent_count: int
        :param vm_size: Size of agent VMs. A full list of options can be found here: https://aka.ms/azureml-aks-details
            Defaults to Standard_D3_v2
        :type vm_size: str
        :param ssl_cname: A CName to use if enabling SSL validation on the cluster.
        :type ssl_cname: str
        :param ssl_cert_pem_file: A file path to a file containing cert information for SSL validation.
        :type ssl_cert_pem_file: str
        :param ssl_key_pem_file: A file path to a file containing key information for SSL validation.
        :type ssl_key_pem_file: str
        :param location: Location to provision cluster in. If not specified, will default to workspace location.
            Available regions for this compute can be found here:
            https://azure.microsoft.com/en-us/global-infrastructure/services/?regions=all&products=kubernetes-service
        :type location: str
        :param vnet_resourcegroup_name: Name of the resource group where the virtual network is located
        :type vnet_resourcegroup_name: str
        :param vnet_name: Name of the virtual network
        :type vnet_name: str
        :param subnet_name: Name of the subnet inside the vnet
        :type subnet_name: str
        :param service_cidr: A CIDR notation IP range from which to assign service cluster IPs.
        :type service_cidr: str
        :param dns_service_ip: Containers DNS server IP address.
        :type dns_service_ip: str
        :param docker_bridge_cidr: A CIDR notation IP for Docker bridge.
        :type docker_bridge_cidr: str
        :param cluster_purpose: Targeted usage of the cluster. This is used to provision AzureML components to
            ensure the desired level of fault-tolerance and QoS. AksCompute.ClusterPurpose class is provided for
            convenience of specifying available values. More detailed information of these values and their use cases
            can be found here: https://aka.ms/azureml-create-attach-aks
        :type cluster_purpose: str
        :return: A configuration object to be used when creating a Compute object
        :rtype: AksProvisioningConfiguration
        :raises: ComputeTargetException
        """
        super(AksProvisioningConfiguration, self).__init__(AksCompute, location)
        self.agent_count = agent_count
        self.vm_size = vm_size
        self.ssl_cname = ssl_cname
        self.ssl_cert_pem_file = ssl_cert_pem_file
        self.ssl_key_pem_file = ssl_key_pem_file
        self.vnet_resourcegroup_name = vnet_resourcegroup_name
        self.vnet_name = vnet_name
        self.subnet_name = subnet_name
        self.leaf_domain_label = None
        self.overwrite_existing_domain = False
        self.service_cidr = service_cidr
        self.dns_service_ip = dns_service_ip
        self.docker_bridge_cidr = docker_bridge_cidr
        self.cluster_purpose = cluster_purpose
        self.validate_configuration()

    def validate_configuration(self):
        """Check that the specified configuration values are valid.

        Will raise a ComputeTargetException if validation fails.

        :raises: ComputeTargetException
        """
        if self.agent_count and self.agent_count <= 0:
            raise ComputeTargetException('Invalid configuration, agent count must be a positive integer.')
        if self.ssl_cname or self.ssl_cert_pem_file or self.ssl_key_pem_file:
            if not self.ssl_cname or not self.ssl_cert_pem_file or not self.ssl_key_pem_file:
                raise ComputeTargetException('Invalid configuration, not all ssl information provided. To enable SSL '
                                             'validation please provide the cname, cert pem file, and key pem file.')
            if self.leaf_domain_label:
                raise ComputeTargetException('Invalid configuration. When cname, cert pem file, and key pem file is '
                                             'provided, leaf domain label should not be provided.')
            if self.overwrite_existing_domain:
                raise ComputeTargetException('Invalid configuration. Overwrite existing domain only applies to leaf '
                                             'domain label. When cname, cert pem file, and key pem file is provided, '
                                             'Overwrite existing domain should not be provided.')
        elif self.leaf_domain_label:
            if self.ssl_cname or self.ssl_cert_pem_file or self.ssl_key_pem_file:
                raise ComputeTargetException('Invalid configuration. When leaf domain label is provided, cname, cert '
                                             'pem file, or key pem file should not be provided.')
        if self.vnet_name or self.vnet_resourcegroup_name or self.subnet_name or self.service_cidr or \
                self.dns_service_ip or self.docker_bridge_cidr:
            if not self.vnet_name or not self.vnet_resourcegroup_name or not self.subnet_name or \
                    not self.service_cidr or not self.dns_service_ip or not self.docker_bridge_cidr:
                raise ComputeTargetException('Invalid configuration, not all virtual net information provided. To use '
                                             'a custom virtual net with aks, please provide vnet name, vnet resource '
                                             'group, subnet name, service cidr, dns service ip and docker bridge cidr')

    def enable_ssl(self, ssl_cname=None, ssl_cert_pem_file=None, ssl_key_pem_file=None, leaf_domain_label=None,
                   overwrite_existing_domain=False):
        """Enable SSL validation on the cluster.

        :param ssl_cname: A CName to use if enabling SSL validation on the cluster. Must provide all three
            CName, cert file, and key file to enable SSL validation
        :type ssl_cname: str
        :param ssl_cert_pem_file: A file path to a file containing cert information for SSL validation. Must provide
            all three CName, cert file, and key file to enable SSL validation
        :type ssl_cert_pem_file: str
        :param ssl_key_pem_file: A file path to a file containing key information for SSL validation. Must provide
            all three CName, cert file, and key file to enable SSL validation
        :type ssl_key_pem_file: str
        :param leaf_domain_label: leaf domain label to use if enabling SSL validation on the cluster. When leaf domain
            label is provided, cname, cert pem file, or key pem file should not be provided
        :type leaf_domain_label: str
        :param overwrite_existing_domain: Whether or not to overwrite the existing leaf domain label. Overwrite
            existing domain only applies to leaf domain label. When it is provided, cname, cert pem file, or key pem
            file should not be provided. Defaults to False
        :type overwrite_existing_domain: bool
        """
        if ssl_cname:
            self.ssl_cname = ssl_cname
        if ssl_cert_pem_file:
            self.ssl_cert_pem_file = ssl_cert_pem_file
        if ssl_key_pem_file:
            self.ssl_key_pem_file = ssl_key_pem_file
        if leaf_domain_label:
            self.leaf_domain_label = leaf_domain_label
        if overwrite_existing_domain:
            self.overwrite_existing_domain = overwrite_existing_domain
        self.validate_configuration()


class AksAttachConfiguration(ComputeTargetAttachConfiguration):
    """Attach configuration object for AKS compute targets.

    This objects is used to define the configuration parameters for attaching AksCompute objects.
    """

    def __init__(self, resource_group=None, cluster_name=None, resource_id=None, cluster_purpose=None):
        """Initialize the configuration object.

        :param resource_group: Name of the resource group in which the AKS is located.
        :type resource_group: str
        :param cluster_name: The AKS cluster name
        :type cluster_name: str
        :param resource_id: The Azure resource ID for the compute resource being attached
        :type resource_id: str
        :param cluster_purpose: Targeted usage of the cluster. This is used to provision AzureML components to
            ensure the desired level of fault-tolerance and QoS. AksCompute.ClusterPurpose class is provided for
            convenience of specifying available values. More detailed information of these values and their use cases
            can be found here: https://aka.ms/azureml-create-attach-aks
        :type cluster_purpose: str
        :return: The configuration object
        :rtype: AksAttachConfiguration
        """
        super(AksAttachConfiguration, self).__init__(AksCompute)
        self.resource_group = resource_group
        self.cluster_name = cluster_name
        self.resource_id = resource_id
        self.cluster_purpose = cluster_purpose
        self.ssl_cname = None
        self.ssl_cert_pem_file = None
        self.ssl_key_pem_file = None
        self.leaf_domain_label = None
        self.overwrite_existing_domain = False
        self.validate_configuration()

    def validate_configuration(self):
        """Check that the specified configuration values are valid.

        Will raise a ComputeTargetException if validation fails.

        :raises: ComputeTargetException
        """
        if self.resource_id:
            # resource_id is provided, validate resource_id
            resource_parts = self.resource_id.split('/')
            if len(resource_parts) != 9:
                raise ComputeTargetException('Invalid resource_id provided: {}'.format(self.resource_id))
            resource_type = resource_parts[6]
            if resource_type != 'Microsoft.ContainerService':
                raise ComputeTargetException('Invalid resource_id provided, resource type {} does not match for '
                                             'AKS'.format(resource_type))
            # make sure do not use other info
            if self.resource_group:
                raise ComputeTargetException('Since resource_id is provided, please do not provide resource_group.')
            if self.cluster_name:
                raise ComputeTargetException('Since resource_id is provided, please do not provide cluster_name.')
        elif self.resource_group or self.cluster_name:
            # resource_id is not provided, validate other info
            if not self.resource_group:
                raise ComputeTargetException('resource_group is not provided.')
            if not self.cluster_name:
                raise ComputeTargetException('cluster_name is not provided.')
        else:
            # neither resource_id nor other info is provided
            raise ComputeTargetException('Please provide resource_group and cluster_name for the AKS compute '
                                         'resource being attached. Or please provide resource_id for the resource '
                                         'being attached.')

        if self.ssl_cname or self.ssl_cert_pem_file or self.ssl_key_pem_file:
            if not self.ssl_cname or not self.ssl_cert_pem_file or not self.ssl_key_pem_file:
                raise ComputeTargetException('Invalid configuration, not all ssl information provided. To enable SSL '
                                             'validation please provide the cname, cert pem file, and key pem file.')
            if self.leaf_domain_label:
                raise ComputeTargetException('Invalid configuration. When cname, cert pem file, and key pem file is '
                                             'provided, leaf domain label should not be provided.')
            if self.overwrite_existing_domain:
                raise ComputeTargetException('Invalid configuration. Overwrite existing domain only applies to leaf '
                                             'domain label. When cname, cert pem file, and key pem file is provided, '
                                             'Overwrite existing domain should not be provided.')
        elif self.leaf_domain_label:
            if self.ssl_cname or self.ssl_cert_pem_file or self.ssl_key_pem_file:
                raise ComputeTargetException('Invalid configuration. When leaf domain label is provided, cname, cert '
                                             'pem file, or key pem file should not be provided.')

    def enable_ssl(self, ssl_cname=None, ssl_cert_pem_file=None, ssl_key_pem_file=None, leaf_domain_label=None,
                   overwrite_existing_domain=False):
        """Enable SSL validation on the cluster.

        :param ssl_cname: A CName to use if enabling SSL validation on the cluster. Must provide all three
            CName, cert file, and key file to enable SSL validation
        :type ssl_cname: str
        :param ssl_cert_pem_file: A file path to a file containing cert information for SSL validation. Must provide
            all three CName, cert file, and key file to enable SSL validation
        :type ssl_cert_pem_file: str
        :param ssl_key_pem_file: A file path to a file containing key information for SSL validation. Must provide
            all three CName, cert file, and key file to enable SSL validation
        :type ssl_key_pem_file: str
        :param leaf_domain_label: leaf domain label to use if enabling SSL validation on the cluster. When leaf domain
            label is provided, cname, cert pem file, or key pem file should not be provided
        :type leaf_domain_label: str
        :param overwrite_existing_domain: Whether or not to overwrite the existing leaf domain label. Overwrite
            existing domain only applies to leaf domain label. When it is provided, cname, cert pem file, or key pem
            file should not be provided. Defaults to False
        :type overwrite_existing_domain: bool
        """
        if ssl_cname:
            self.ssl_cname = ssl_cname
        if ssl_cert_pem_file:
            self.ssl_cert_pem_file = ssl_cert_pem_file
        if ssl_key_pem_file:
            self.ssl_key_pem_file = ssl_key_pem_file
        if leaf_domain_label:
            self.leaf_domain_label = leaf_domain_label
        if overwrite_existing_domain:
            self.overwrite_existing_domain = overwrite_existing_domain
        self.validate_configuration()


class SystemService(object):
    """AKS System Service object.

    .. remarks::

        Initialize the System Service object

    :param service_type: The underlying type associated with this service
    :type service_type: str
    :param version: Service version
    :type version: str
    :param public_ip_address: Accessible IP address for this service
    :type public_ip_address: str
    """

    def __init__(self, service_type, version, public_ip_address):
        """Initialize the System Service object.

        :param service_type: The underlying type associated with this service
        :type service_type: str
        :param version: Service version
        :type version: str
        :param public_ip_address: Accessible IP address for this service
        :type public_ip_address: str
        """
        self.service_type = service_type
        self.version = version
        self.public_ip_address = public_ip_address

    def serialize(self):
        """Convert this SystemService object into a json serialized dictionary.

        :return: The json representation of this SystemService object
        :rtype: dict
        """
        return {'serviceType': self.service_type, 'version': self.version, 'publicIpAddress': self.public_ip_address}

    @staticmethod
    def deserialize(object_dict):
        """Convert a json object into a SystemService object.

        :param object_dict: A json object to convert to a SystemService object
        :type object_dict: dict
        :return: The SystemService representation of the provided json object
        :rtype: SystemService
        :raises: ComputeTargetException
        """
        for service_key in ['systemServiceType', 'version', 'publicIpAddress']:
            if service_key not in object_dict:
                raise ComputeTargetException('Invalid system service payload, missing "{}":\n'
                                             '{}'.format(service_key, object_dict))
        return SystemService(object_dict['systemServiceType'], object_dict['version'], object_dict['publicIpAddress'])


class SslConfiguration(object):
    """AKS SSL Configuration object.

    .. remarks::

        Initialize the SslConfiguration object

    :param status: Whether SSL validation is enabled or disabled
    :type status: str
    :param cert: Cert string used for SSL validation
    :type cert: str
    :param key: Key string used for SSL validation
    :type key: str
    :param cname: CName used for SSL validation
    :type cname: str
    :param leaf_domain_label: leaf domain label
    :type leaf_domain_label: str
    :param overwrite_existing_domain: whether or not to overwrite the existing leaf domain label
    :type overwrite_existing_domain: bool
    """

    def __init__(self, status, cert, key, cname, leaf_domain_label, overwrite_existing_domain):
        """Initialize the SslConfiguration object.

        :param status: Whether SSL validation is enabled or disabled
        :type status: str
        :param cert: Cert string used for SSL validation
        :type cert: str
        :param key: Key string used for SSL validation
        :type key: str
        :param cname: CName used for SSL validation
        :type cname: str
        """
        self.status = status
        self.cert = cert
        self.key = key
        self.cname = cname
        self.leaf_domain_label = leaf_domain_label
        self.overwrite_existing_domain = overwrite_existing_domain

    def serialize(self):
        """Convert this SslConfiguration object into a json serialized dictionary.

        :return: The json representation of this SslConfiguration object
        :rtype: dict
        """
        return {
            'status': self.status, 'cert': self.cert, 'key': self.key, 'cname': self.cname,
            'leafDomainLabel': self.leaf_domain_label, 'overwriteExistingDomain': self.overwrite_existing_domain}

    @staticmethod
    def deserialize(object_dict):
        """Convert a json object into a SslConfiguration object.

        :param object_dict: A json object to convert to a SslConfiguration object
        :type object_dict: dict
        :return: The SslConfiguration representation of the provided json object
        :rtype: SslConfiguration
        :raises: ComputeTargetException
        """
        status = object_dict.get('status', None)
        cert = object_dict.get('cert', None)
        key = object_dict.get('key', None)
        cname = object_dict.get('cname', None)
        leaf_domain_label = object_dict.get('leafDomainLabel', None)
        overwrite_existing_domain = object_dict.get('overwriteExistingDomain', False)
        return SslConfiguration(status, cert, key, cname, leaf_domain_label, overwrite_existing_domain)
