# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import json
import warnings
import pulumi
import pulumi.runtime
from .. import utilities, tables

class LocalNetworkGateway(pulumi.CustomResource):
    address_spaces: pulumi.Output[list]
    """
    The list of string CIDRs representing the
    address spaces the gateway exposes.
    """
    bgp_settings: pulumi.Output[dict]
    """
    A `bgp_settings` block as defined below containing the
    Local Network Gateway's BGP speaker settings.
    """
    gateway_address: pulumi.Output[str]
    """
    The IP address of the gateway to which to
    connect.
    """
    location: pulumi.Output[str]
    """
    The location/region where the local network gateway is
    created. Changing this forces a new resource to be created.
    """
    name: pulumi.Output[str]
    """
    The name of the local network gateway. Changing this
    forces a new resource to be created.
    """
    resource_group_name: pulumi.Output[str]
    """
    The name of the resource group in which to
    create the local network gateway.
    """
    tags: pulumi.Output[dict]
    """
    A mapping of tags to assign to the resource.
    """
    def __init__(__self__, resource_name, opts=None, address_spaces=None, bgp_settings=None, gateway_address=None, location=None, name=None, resource_group_name=None, tags=None, __name__=None, __opts__=None):
        """
        Manages a local network gateway connection over which specific connections can be configured.
        
        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[list] address_spaces: The list of string CIDRs representing the
               address spaces the gateway exposes.
        :param pulumi.Input[dict] bgp_settings: A `bgp_settings` block as defined below containing the
               Local Network Gateway's BGP speaker settings.
        :param pulumi.Input[str] gateway_address: The IP address of the gateway to which to
               connect.
        :param pulumi.Input[str] location: The location/region where the local network gateway is
               created. Changing this forces a new resource to be created.
        :param pulumi.Input[str] name: The name of the local network gateway. Changing this
               forces a new resource to be created.
        :param pulumi.Input[str] resource_group_name: The name of the resource group in which to
               create the local network gateway.
        :param pulumi.Input[dict] tags: A mapping of tags to assign to the resource.
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

        if address_spaces is None:
            raise TypeError("Missing required property 'address_spaces'")
        __props__['address_spaces'] = address_spaces

        __props__['bgp_settings'] = bgp_settings

        if gateway_address is None:
            raise TypeError("Missing required property 'gateway_address'")
        __props__['gateway_address'] = gateway_address

        __props__['location'] = location

        __props__['name'] = name

        if resource_group_name is None:
            raise TypeError("Missing required property 'resource_group_name'")
        __props__['resource_group_name'] = resource_group_name

        __props__['tags'] = tags

        super(LocalNetworkGateway, __self__).__init__(
            'azure:network/localNetworkGateway:LocalNetworkGateway',
            resource_name,
            __props__,
            opts)


    def translate_output_property(self, prop):
        return tables._CAMEL_TO_SNAKE_CASE_TABLE.get(prop) or prop

    def translate_input_property(self, prop):
        return tables._SNAKE_TO_CAMEL_CASE_TABLE.get(prop) or prop

