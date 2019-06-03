# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import json
import warnings
import pulumi
import pulumi.runtime
from .. import utilities, tables

class LinkedServicePostgresql(pulumi.CustomResource):
    additional_properties: pulumi.Output[dict]
    """
    A map of additional properties to associate with the Data Factory Linked Service PostgreSQL.
    """
    annotations: pulumi.Output[list]
    """
    List of tags that can be used for describing the Data Factory Linked Service PostgreSQL.
    """
    connection_string: pulumi.Output[str]
    """
    The connection string in which to authenticate with PostgreSQL.
    """
    data_factory_name: pulumi.Output[str]
    """
    The Data Factory name in which to associate the Linked Service with. Changing this forces a new resource.
    """
    description: pulumi.Output[str]
    """
    The description for the Data Factory Linked Service PostgreSQL.
    """
    integration_runtime_name: pulumi.Output[str]
    """
    The integration runtime reference to associate with the Data Factory Linked Service PostgreSQL.
    """
    name: pulumi.Output[str]
    """
    Specifies the name of the Data Factory Linked Service PostgreSQL. Changing this forces a new resource to be created. Must be globally unique. See the [Microsoft documentation](https://docs.microsoft.com/en-us/azure/data-factory/naming-rules) for all restrictions.
    """
    parameters: pulumi.Output[dict]
    """
    A map of parameters to associate with the Data Factory Linked Service PostgreSQL.
    """
    resource_group_name: pulumi.Output[str]
    """
    The name of the resource group in which to create the Data Factory Linked Service PostgreSQL. Changing this forces a new resource
    """
    def __init__(__self__, resource_name, opts=None, additional_properties=None, annotations=None, connection_string=None, data_factory_name=None, description=None, integration_runtime_name=None, name=None, parameters=None, resource_group_name=None, __name__=None, __opts__=None):
        """
        Manage a Linked Service (connection) between PostgreSQL and Azure Data Factory.
        
        > **Note:** All arguments including the connection_string will be stored in the raw state as plain-text. [Read more about sensitive data in state](https://www.terraform.io/docs/state/sensitive-data.html).
        
        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[dict] additional_properties: A map of additional properties to associate with the Data Factory Linked Service PostgreSQL.
        :param pulumi.Input[list] annotations: List of tags that can be used for describing the Data Factory Linked Service PostgreSQL.
        :param pulumi.Input[str] connection_string: The connection string in which to authenticate with PostgreSQL.
        :param pulumi.Input[str] data_factory_name: The Data Factory name in which to associate the Linked Service with. Changing this forces a new resource.
        :param pulumi.Input[str] description: The description for the Data Factory Linked Service PostgreSQL.
        :param pulumi.Input[str] integration_runtime_name: The integration runtime reference to associate with the Data Factory Linked Service PostgreSQL.
        :param pulumi.Input[str] name: Specifies the name of the Data Factory Linked Service PostgreSQL. Changing this forces a new resource to be created. Must be globally unique. See the [Microsoft documentation](https://docs.microsoft.com/en-us/azure/data-factory/naming-rules) for all restrictions.
        :param pulumi.Input[dict] parameters: A map of parameters to associate with the Data Factory Linked Service PostgreSQL.
        :param pulumi.Input[str] resource_group_name: The name of the resource group in which to create the Data Factory Linked Service PostgreSQL. Changing this forces a new resource
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

        __props__['additional_properties'] = additional_properties

        __props__['annotations'] = annotations

        if connection_string is None:
            raise TypeError("Missing required property 'connection_string'")
        __props__['connection_string'] = connection_string

        if data_factory_name is None:
            raise TypeError("Missing required property 'data_factory_name'")
        __props__['data_factory_name'] = data_factory_name

        __props__['description'] = description

        __props__['integration_runtime_name'] = integration_runtime_name

        __props__['name'] = name

        __props__['parameters'] = parameters

        if resource_group_name is None:
            raise TypeError("Missing required property 'resource_group_name'")
        __props__['resource_group_name'] = resource_group_name

        super(LinkedServicePostgresql, __self__).__init__(
            'azure:datafactory/linkedServicePostgresql:LinkedServicePostgresql',
            resource_name,
            __props__,
            opts)


    def translate_output_property(self, prop):
        return tables._CAMEL_TO_SNAKE_CASE_TABLE.get(prop) or prop

    def translate_input_property(self, prop):
        return tables._SNAKE_TO_CAMEL_CASE_TABLE.get(prop) or prop

