# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import json
import warnings
import pulumi
import pulumi.runtime
from .. import utilities, tables

class ApiOperation(pulumi.CustomResource):
    api_management_name: pulumi.Output[str]
    """
    The Name of the API Management Service where the API exists. Changing this forces a new resource to be created.
    """
    api_name: pulumi.Output[str]
    """
    The name of the API within the API Management Service where this API Operation should be created. Changing this forces a new resource to be created.
    """
    description: pulumi.Output[str]
    """
    A description for this API Operation, which may include HTML formatting tags.
    """
    display_name: pulumi.Output[str]
    """
    The Display Name for this API Management Operation.
    """
    method: pulumi.Output[str]
    """
    The HTTP Method used for this API Management Operation, like `GET`, `DELETE`, `PUT` or `POST` - but not limited to these values.
    """
    operation_id: pulumi.Output[str]
    """
    A unique identifier for this API Operation. Changing this forces a new resource to be created.
    """
    request: pulumi.Output[dict]
    """
    A `request` block as defined below.
    """
    resource_group_name: pulumi.Output[str]
    """
    The Name of the Resource Group in which the API Management Service exists. Changing this forces a new resource to be created.
    """
    responses: pulumi.Output[list]
    """
    One or more `response` blocks as defined below.
    """
    template_parameters: pulumi.Output[list]
    """
    One or more `template_parameter` blocks as defined below.
    """
    url_template: pulumi.Output[str]
    """
    The relative URL Template identifying the target resource for this operation, which may include parameters.
    """
    def __init__(__self__, resource_name, opts=None, api_management_name=None, api_name=None, description=None, display_name=None, method=None, operation_id=None, request=None, resource_group_name=None, responses=None, template_parameters=None, url_template=None, __name__=None, __opts__=None):
        """
        Manages an API Operation within an API Management Service.
        
        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] api_management_name: The Name of the API Management Service where the API exists. Changing this forces a new resource to be created.
        :param pulumi.Input[str] api_name: The name of the API within the API Management Service where this API Operation should be created. Changing this forces a new resource to be created.
        :param pulumi.Input[str] description: A description for this API Operation, which may include HTML formatting tags.
        :param pulumi.Input[str] display_name: The Display Name for this API Management Operation.
        :param pulumi.Input[str] method: The HTTP Method used for this API Management Operation, like `GET`, `DELETE`, `PUT` or `POST` - but not limited to these values.
        :param pulumi.Input[str] operation_id: A unique identifier for this API Operation. Changing this forces a new resource to be created.
        :param pulumi.Input[dict] request: A `request` block as defined below.
        :param pulumi.Input[str] resource_group_name: The Name of the Resource Group in which the API Management Service exists. Changing this forces a new resource to be created.
        :param pulumi.Input[list] responses: One or more `response` blocks as defined below.
        :param pulumi.Input[list] template_parameters: One or more `template_parameter` blocks as defined below.
        :param pulumi.Input[str] url_template: The relative URL Template identifying the target resource for this operation, which may include parameters.
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

        if api_management_name is None:
            raise TypeError("Missing required property 'api_management_name'")
        __props__['api_management_name'] = api_management_name

        if api_name is None:
            raise TypeError("Missing required property 'api_name'")
        __props__['api_name'] = api_name

        __props__['description'] = description

        if display_name is None:
            raise TypeError("Missing required property 'display_name'")
        __props__['display_name'] = display_name

        if method is None:
            raise TypeError("Missing required property 'method'")
        __props__['method'] = method

        if operation_id is None:
            raise TypeError("Missing required property 'operation_id'")
        __props__['operation_id'] = operation_id

        __props__['request'] = request

        if resource_group_name is None:
            raise TypeError("Missing required property 'resource_group_name'")
        __props__['resource_group_name'] = resource_group_name

        __props__['responses'] = responses

        __props__['template_parameters'] = template_parameters

        if url_template is None:
            raise TypeError("Missing required property 'url_template'")
        __props__['url_template'] = url_template

        super(ApiOperation, __self__).__init__(
            'azure:apimanagement/apiOperation:ApiOperation',
            resource_name,
            __props__,
            opts)


    def translate_output_property(self, prop):
        return tables._CAMEL_TO_SNAKE_CASE_TABLE.get(prop) or prop

    def translate_input_property(self, prop):
        return tables._SNAKE_TO_CAMEL_CASE_TABLE.get(prop) or prop

