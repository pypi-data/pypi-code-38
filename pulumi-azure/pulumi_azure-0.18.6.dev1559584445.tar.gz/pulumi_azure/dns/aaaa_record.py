# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import json
import warnings
import pulumi
import pulumi.runtime
from .. import utilities, tables

class AaaaRecord(pulumi.CustomResource):
    name: pulumi.Output[str]
    """
    The name of the DNS AAAA Record.
    """
    records: pulumi.Output[list]
    """
    List of IPv6 Addresses.
    """
    resource_group_name: pulumi.Output[str]
    """
    Specifies the resource group where the resource exists. Changing this forces a new resource to be created.
    """
    tags: pulumi.Output[dict]
    """
    A mapping of tags to assign to the resource.
    """
    ttl: pulumi.Output[float]
    zone_name: pulumi.Output[str]
    """
    Specifies the DNS Zone where the resource exists. Changing this forces a new resource to be created.
    """
    def __init__(__self__, resource_name, opts=None, name=None, records=None, resource_group_name=None, tags=None, ttl=None, zone_name=None, __name__=None, __opts__=None):
        """
        Enables you to manage DNS AAAA Records within Azure DNS.
        
        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] name: The name of the DNS AAAA Record.
        :param pulumi.Input[list] records: List of IPv6 Addresses.
        :param pulumi.Input[str] resource_group_name: Specifies the resource group where the resource exists. Changing this forces a new resource to be created.
        :param pulumi.Input[dict] tags: A mapping of tags to assign to the resource.
        :param pulumi.Input[str] zone_name: Specifies the DNS Zone where the resource exists. Changing this forces a new resource to be created.
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

        __props__['name'] = name

        if records is None:
            raise TypeError("Missing required property 'records'")
        __props__['records'] = records

        if resource_group_name is None:
            raise TypeError("Missing required property 'resource_group_name'")
        __props__['resource_group_name'] = resource_group_name

        __props__['tags'] = tags

        if ttl is None:
            raise TypeError("Missing required property 'ttl'")
        __props__['ttl'] = ttl

        if zone_name is None:
            raise TypeError("Missing required property 'zone_name'")
        __props__['zone_name'] = zone_name

        super(AaaaRecord, __self__).__init__(
            'azure:dns/aaaaRecord:AaaaRecord',
            resource_name,
            __props__,
            opts)


    def translate_output_property(self, prop):
        return tables._CAMEL_TO_SNAKE_CASE_TABLE.get(prop) or prop

    def translate_input_property(self, prop):
        return tables._SNAKE_TO_CAMEL_CASE_TABLE.get(prop) or prop

