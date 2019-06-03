# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import json
import warnings
import pulumi
import pulumi.runtime
from .. import utilities, tables

class SharedAccessPolicy(pulumi.CustomResource):
    device_connect: pulumi.Output[bool]
    """
    Adds `DeviceConnect` permission to this Shared Access Account. It allows sending and receiving on the device-side endpoints.
    """
    iothub_name: pulumi.Output[str]
    """
    The name of the IoTHub to which this Shared Access Policy belongs. Changing this forces a new resource to be created.
    """
    name: pulumi.Output[str]
    """
    Specifies the name of the IotHub Shared Access Policy resource. Changing this forces a new resource to be created.
    """
    primary_connection_string: pulumi.Output[str]
    """
    The primary connection string of the Shared Access Policy.
    """
    primary_key: pulumi.Output[str]
    """
    The primary key used to create the authentication token.
    """
    registry_read: pulumi.Output[bool]
    """
    Adds `RegistryRead` permission to this Shared Access Account. It allows read access to the identity registry.
    """
    registry_write: pulumi.Output[bool]
    """
    Adds `RegistryWrite` permission to this Shared Access Account. It allows write access to the identity registry.
    """
    resource_group_name: pulumi.Output[str]
    """
    The name of the resource group under which the IotHub Shared Access Policy resource has to be created. Changing this forces a new resource to be created.
    """
    secondary_connection_string: pulumi.Output[str]
    """
    The secondary connection string of the Shared Access Policy.
    """
    secondary_key: pulumi.Output[str]
    """
    The secondary key used to create the authentication token.
    """
    service_connect: pulumi.Output[bool]
    """
    Adds `ServiceConnect` permission to this Shared Access Account. It allows sending and receiving on the cloud-side endpoints.
    """
    def __init__(__self__, resource_name, opts=None, device_connect=None, iothub_name=None, name=None, registry_read=None, registry_write=None, resource_group_name=None, service_connect=None, __name__=None, __opts__=None):
        """
        Manages an IotHub Shared Access Policy
        
        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[bool] device_connect: Adds `DeviceConnect` permission to this Shared Access Account. It allows sending and receiving on the device-side endpoints.
        :param pulumi.Input[str] iothub_name: The name of the IoTHub to which this Shared Access Policy belongs. Changing this forces a new resource to be created.
        :param pulumi.Input[str] name: Specifies the name of the IotHub Shared Access Policy resource. Changing this forces a new resource to be created.
        :param pulumi.Input[bool] registry_read: Adds `RegistryRead` permission to this Shared Access Account. It allows read access to the identity registry.
        :param pulumi.Input[bool] registry_write: Adds `RegistryWrite` permission to this Shared Access Account. It allows write access to the identity registry.
        :param pulumi.Input[str] resource_group_name: The name of the resource group under which the IotHub Shared Access Policy resource has to be created. Changing this forces a new resource to be created.
        :param pulumi.Input[bool] service_connect: Adds `ServiceConnect` permission to this Shared Access Account. It allows sending and receiving on the cloud-side endpoints.
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

        __props__['device_connect'] = device_connect

        if iothub_name is None:
            raise TypeError("Missing required property 'iothub_name'")
        __props__['iothub_name'] = iothub_name

        __props__['name'] = name

        __props__['registry_read'] = registry_read

        __props__['registry_write'] = registry_write

        if resource_group_name is None:
            raise TypeError("Missing required property 'resource_group_name'")
        __props__['resource_group_name'] = resource_group_name

        __props__['service_connect'] = service_connect

        __props__['primary_connection_string'] = None
        __props__['primary_key'] = None
        __props__['secondary_connection_string'] = None
        __props__['secondary_key'] = None

        super(SharedAccessPolicy, __self__).__init__(
            'azure:iot/sharedAccessPolicy:SharedAccessPolicy',
            resource_name,
            __props__,
            opts)


    def translate_output_property(self, prop):
        return tables._CAMEL_TO_SNAKE_CASE_TABLE.get(prop) or prop

    def translate_input_property(self, prop):
        return tables._SNAKE_TO_CAMEL_CASE_TABLE.get(prop) or prop

