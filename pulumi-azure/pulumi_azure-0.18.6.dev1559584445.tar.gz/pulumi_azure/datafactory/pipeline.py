# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import json
import warnings
import pulumi
import pulumi.runtime
from .. import utilities, tables

class Pipeline(pulumi.CustomResource):
    annotations: pulumi.Output[list]
    """
    List of tags that can be used for describing the Data Factory Pipeline.
    """
    data_factory_name: pulumi.Output[str]
    """
    The Data Factory name in which to associate the Pipeline with. Changing this forces a new resource.
    """
    description: pulumi.Output[str]
    """
    The description for the Data Factory Pipeline.
    """
    name: pulumi.Output[str]
    """
    Specifies the name of the Data Factory Pipeline. Changing this forces a new resource to be created. Must be globally unique. See the [Microsoft documentation](https://docs.microsoft.com/en-us/azure/data-factory/naming-rules) for all restrictions.
    """
    parameters: pulumi.Output[dict]
    """
    A map of parameters to associate with the Data Factory Pipeline.
    """
    resource_group_name: pulumi.Output[str]
    """
    The name of the resource group in which to create the Data Factory Pipeline. Changing this forces a new resource
    """
    variables: pulumi.Output[dict]
    """
    A map of variables to associate with the Data Factory Pipeline.
    """
    def __init__(__self__, resource_name, opts=None, annotations=None, data_factory_name=None, description=None, name=None, parameters=None, resource_group_name=None, variables=None, __name__=None, __opts__=None):
        """
        Manage a Pipeline inside a Azure Data Factory.
        
        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[list] annotations: List of tags that can be used for describing the Data Factory Pipeline.
        :param pulumi.Input[str] data_factory_name: The Data Factory name in which to associate the Pipeline with. Changing this forces a new resource.
        :param pulumi.Input[str] description: The description for the Data Factory Pipeline.
        :param pulumi.Input[str] name: Specifies the name of the Data Factory Pipeline. Changing this forces a new resource to be created. Must be globally unique. See the [Microsoft documentation](https://docs.microsoft.com/en-us/azure/data-factory/naming-rules) for all restrictions.
        :param pulumi.Input[dict] parameters: A map of parameters to associate with the Data Factory Pipeline.
        :param pulumi.Input[str] resource_group_name: The name of the resource group in which to create the Data Factory Pipeline. Changing this forces a new resource
        :param pulumi.Input[dict] variables: A map of variables to associate with the Data Factory Pipeline.
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

        __props__['annotations'] = annotations

        if data_factory_name is None:
            raise TypeError("Missing required property 'data_factory_name'")
        __props__['data_factory_name'] = data_factory_name

        __props__['description'] = description

        __props__['name'] = name

        __props__['parameters'] = parameters

        if resource_group_name is None:
            raise TypeError("Missing required property 'resource_group_name'")
        __props__['resource_group_name'] = resource_group_name

        __props__['variables'] = variables

        super(Pipeline, __self__).__init__(
            'azure:datafactory/pipeline:Pipeline',
            resource_name,
            __props__,
            opts)


    def translate_output_property(self, prop):
        return tables._CAMEL_TO_SNAKE_CASE_TABLE.get(prop) or prop

    def translate_input_property(self, prop):
        return tables._SNAKE_TO_CAMEL_CASE_TABLE.get(prop) or prop

