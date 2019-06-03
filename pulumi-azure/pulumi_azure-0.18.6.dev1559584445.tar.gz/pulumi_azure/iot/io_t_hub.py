# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import json
import warnings
import pulumi
import pulumi.runtime
from .. import utilities, tables

class IoTHub(pulumi.CustomResource):
    endpoints: pulumi.Output[list]
    """
    An `endpoint` block as defined below.
    """
    event_hub_events_endpoint: pulumi.Output[str]
    """
    The EventHub compatible endpoint for events data
    """
    event_hub_events_path: pulumi.Output[str]
    """
    The EventHub compatible path for events data
    """
    event_hub_operations_endpoint: pulumi.Output[str]
    """
    The EventHub compatible endpoint for operational data
    """
    event_hub_operations_path: pulumi.Output[str]
    """
    The EventHub compatible path for operational data
    """
    fallback_route: pulumi.Output[dict]
    """
    A `fallback_route` block as defined below. If the fallback route is enabled, messages that don't match any of the supplied routes are automatically sent to this route. Defaults to messages/events.
    """
    hostname: pulumi.Output[str]
    """
    The hostname of the IotHub Resource.
    """
    ip_filter_rules: pulumi.Output[list]
    """
    One or more `ip_filter_rule` blocks as defined below.
    """
    location: pulumi.Output[str]
    """
    Specifies the supported Azure location where the resource has to be createc. Changing this forces a new resource to be created.
    """
    name: pulumi.Output[str]
    """
    Specifies the name of the IotHub resource. Changing this forces a new resource to be created.
    """
    resource_group_name: pulumi.Output[str]
    """
    The name of the resource group under which the IotHub resource has to be created. Changing this forces a new resource to be created.
    """
    routes: pulumi.Output[list]
    """
    A `route` block as defined below.
    """
    shared_access_policies: pulumi.Output[list]
    """
    One or more `shared_access_policy` blocks as defined below.
    """
    sku: pulumi.Output[dict]
    """
    A `sku` block as defined below.
    """
    tags: pulumi.Output[dict]
    """
    A mapping of tags to assign to the resource.
    """
    type: pulumi.Output[str]
    def __init__(__self__, resource_name, opts=None, endpoints=None, fallback_route=None, ip_filter_rules=None, location=None, name=None, resource_group_name=None, routes=None, sku=None, tags=None, __name__=None, __opts__=None):
        """
        Manages an IotHub
        
        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[list] endpoints: An `endpoint` block as defined below.
        :param pulumi.Input[dict] fallback_route: A `fallback_route` block as defined below. If the fallback route is enabled, messages that don't match any of the supplied routes are automatically sent to this route. Defaults to messages/events.
        :param pulumi.Input[list] ip_filter_rules: One or more `ip_filter_rule` blocks as defined below.
        :param pulumi.Input[str] location: Specifies the supported Azure location where the resource has to be createc. Changing this forces a new resource to be created.
        :param pulumi.Input[str] name: Specifies the name of the IotHub resource. Changing this forces a new resource to be created.
        :param pulumi.Input[str] resource_group_name: The name of the resource group under which the IotHub resource has to be created. Changing this forces a new resource to be created.
        :param pulumi.Input[list] routes: A `route` block as defined below.
        :param pulumi.Input[dict] sku: A `sku` block as defined below.
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

        __props__['endpoints'] = endpoints

        __props__['fallback_route'] = fallback_route

        __props__['ip_filter_rules'] = ip_filter_rules

        __props__['location'] = location

        __props__['name'] = name

        if resource_group_name is None:
            raise TypeError("Missing required property 'resource_group_name'")
        __props__['resource_group_name'] = resource_group_name

        __props__['routes'] = routes

        if sku is None:
            raise TypeError("Missing required property 'sku'")
        __props__['sku'] = sku

        __props__['tags'] = tags

        __props__['event_hub_events_endpoint'] = None
        __props__['event_hub_events_path'] = None
        __props__['event_hub_operations_endpoint'] = None
        __props__['event_hub_operations_path'] = None
        __props__['hostname'] = None
        __props__['shared_access_policies'] = None
        __props__['type'] = None

        super(IoTHub, __self__).__init__(
            'azure:iot/ioTHub:IoTHub',
            resource_name,
            __props__,
            opts)


    def translate_output_property(self, prop):
        return tables._CAMEL_TO_SNAKE_CASE_TABLE.get(prop) or prop

    def translate_input_property(self, prop):
        return tables._SNAKE_TO_CAMEL_CASE_TABLE.get(prop) or prop

