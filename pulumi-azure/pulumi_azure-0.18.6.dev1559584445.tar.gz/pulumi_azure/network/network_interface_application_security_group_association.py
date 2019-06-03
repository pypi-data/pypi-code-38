# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import json
import warnings
import pulumi
import pulumi.runtime
from .. import utilities, tables

class NetworkInterfaceApplicationSecurityGroupAssociation(pulumi.CustomResource):
    application_security_group_id: pulumi.Output[str]
    """
    The ID of the Application Security Group which this Network Interface which should be connected to. Changing this forces a new resource to be created.
    """
    ip_configuration_name: pulumi.Output[str]
    """
    The Name of the IP Configuration within the Network Interface which should be connected to the Application Security Group. Changing this forces a new resource to be created.
    """
    network_interface_id: pulumi.Output[str]
    """
    The ID of the Network Interface. Changing this forces a new resource to be created.
    """
    def __init__(__self__, resource_name, opts=None, application_security_group_id=None, ip_configuration_name=None, network_interface_id=None, __name__=None, __opts__=None):
        """
        Manages the association between a Network Interface and a Application Security Group.
        
        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] application_security_group_id: The ID of the Application Security Group which this Network Interface which should be connected to. Changing this forces a new resource to be created.
        :param pulumi.Input[str] ip_configuration_name: The Name of the IP Configuration within the Network Interface which should be connected to the Application Security Group. Changing this forces a new resource to be created.
        :param pulumi.Input[str] network_interface_id: The ID of the Network Interface. Changing this forces a new resource to be created.
        """
        if __name__ is not None:
            warnings.warn("explicit use of __name__ is deprecated", DeprecationWarning)
            resource_name = __name__
        if __opts__ is not None:
            warnings.warn("explicit use of __opts__ is deprecated, use 'opts' instead", DeprecationWarning)
            opts = __opts__
        if not resource_name:
            raise TypeError('Missing resource name argument (for URN creation)')
        if not isinstance(resource_name, str):
            raise TypeError('Expected resource name to be a string')
        if opts and not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')

        __props__ = dict()

        if application_security_group_id is None:
            raise TypeError("Missing required property 'application_security_group_id'")
        __props__['application_security_group_id'] = application_security_group_id

        if ip_configuration_name is None:
            raise TypeError("Missing required property 'ip_configuration_name'")
        __props__['ip_configuration_name'] = ip_configuration_name

        if network_interface_id is None:
            raise TypeError("Missing required property 'network_interface_id'")
        __props__['network_interface_id'] = network_interface_id

        super(NetworkInterfaceApplicationSecurityGroupAssociation, __self__).__init__(
            'azure:network/networkInterfaceApplicationSecurityGroupAssociation:NetworkInterfaceApplicationSecurityGroupAssociation',
            resource_name,
            __props__,
            opts)


    def translate_output_property(self, prop):
        return tables._CAMEL_TO_SNAKE_CASE_TABLE.get(prop) or prop

    def translate_input_property(self, prop):
        return tables._SNAKE_TO_CAMEL_CASE_TABLE.get(prop) or prop

