import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-sagemaker", "0.36.0", __name__, "aws-sagemaker@0.36.0.jsii.tgz")
class CfnEndpoint(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sagemaker.CfnEndpoint"):
    """A CloudFormation ``AWS::SageMaker::Endpoint``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-endpoint.html
    Stability:
        stable
    cloudformationResource:
        AWS::SageMaker::Endpoint
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, endpoint_config_name: str, endpoint_name: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::SageMaker::Endpoint``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            endpoint_config_name: ``AWS::SageMaker::Endpoint.EndpointConfigName``.
            endpoint_name: ``AWS::SageMaker::Endpoint.EndpointName``.
            tags: ``AWS::SageMaker::Endpoint.Tags``.

        Stability:
            experimental
        """
        props: CfnEndpointProps = {"endpointConfigName": endpoint_config_name}

        if endpoint_name is not None:
            props["endpointName"] = endpoint_name

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnEndpoint, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="attrEndpointName")
    def attr_endpoint_name(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            EndpointName
        """
        return jsii.get(self, "attrEndpointName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::SageMaker::Endpoint.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-endpoint.html#cfn-sagemaker-endpoint-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="endpointConfigName")
    def endpoint_config_name(self) -> str:
        """``AWS::SageMaker::Endpoint.EndpointConfigName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-endpoint.html#cfn-sagemaker-endpoint-endpointconfigname
        Stability:
            stable
        """
        return jsii.get(self, "endpointConfigName")

    @endpoint_config_name.setter
    def endpoint_config_name(self, value: str):
        return jsii.set(self, "endpointConfigName", value)

    @property
    @jsii.member(jsii_name="endpointName")
    def endpoint_name(self) -> typing.Optional[str]:
        """``AWS::SageMaker::Endpoint.EndpointName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-endpoint.html#cfn-sagemaker-endpoint-endpointname
        Stability:
            stable
        """
        return jsii.get(self, "endpointName")

    @endpoint_name.setter
    def endpoint_name(self, value: typing.Optional[str]):
        return jsii.set(self, "endpointName", value)


class CfnEndpointConfig(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sagemaker.CfnEndpointConfig"):
    """A CloudFormation ``AWS::SageMaker::EndpointConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-endpointconfig.html
    Stability:
        stable
    cloudformationResource:
        AWS::SageMaker::EndpointConfig
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, production_variants: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union["ProductionVariantProperty", aws_cdk.core.IResolvable]]], endpoint_config_name: typing.Optional[str]=None, kms_key_id: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::SageMaker::EndpointConfig``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            production_variants: ``AWS::SageMaker::EndpointConfig.ProductionVariants``.
            endpoint_config_name: ``AWS::SageMaker::EndpointConfig.EndpointConfigName``.
            kms_key_id: ``AWS::SageMaker::EndpointConfig.KmsKeyId``.
            tags: ``AWS::SageMaker::EndpointConfig.Tags``.

        Stability:
            experimental
        """
        props: CfnEndpointConfigProps = {"productionVariants": production_variants}

        if endpoint_config_name is not None:
            props["endpointConfigName"] = endpoint_config_name

        if kms_key_id is not None:
            props["kmsKeyId"] = kms_key_id

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnEndpointConfig, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="attrEndpointConfigName")
    def attr_endpoint_config_name(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            EndpointConfigName
        """
        return jsii.get(self, "attrEndpointConfigName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::SageMaker::EndpointConfig.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-endpointconfig.html#cfn-sagemaker-endpointconfig-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="productionVariants")
    def production_variants(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union["ProductionVariantProperty", aws_cdk.core.IResolvable]]]:
        """``AWS::SageMaker::EndpointConfig.ProductionVariants``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-endpointconfig.html#cfn-sagemaker-endpointconfig-productionvariants
        Stability:
            stable
        """
        return jsii.get(self, "productionVariants")

    @production_variants.setter
    def production_variants(self, value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union["ProductionVariantProperty", aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "productionVariants", value)

    @property
    @jsii.member(jsii_name="endpointConfigName")
    def endpoint_config_name(self) -> typing.Optional[str]:
        """``AWS::SageMaker::EndpointConfig.EndpointConfigName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-endpointconfig.html#cfn-sagemaker-endpointconfig-endpointconfigname
        Stability:
            stable
        """
        return jsii.get(self, "endpointConfigName")

    @endpoint_config_name.setter
    def endpoint_config_name(self, value: typing.Optional[str]):
        return jsii.set(self, "endpointConfigName", value)

    @property
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> typing.Optional[str]:
        """``AWS::SageMaker::EndpointConfig.KmsKeyId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-endpointconfig.html#cfn-sagemaker-endpointconfig-kmskeyid
        Stability:
            stable
        """
        return jsii.get(self, "kmsKeyId")

    @kms_key_id.setter
    def kms_key_id(self, value: typing.Optional[str]):
        return jsii.set(self, "kmsKeyId", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ProductionVariantProperty(jsii.compat.TypedDict, total=False):
        acceleratorType: str
        """``CfnEndpointConfig.ProductionVariantProperty.AcceleratorType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sagemaker-endpointconfig-productionvariant.html#cfn-sagemaker-endpointconfig-productionvariant-acceleratortype
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-sagemaker.CfnEndpointConfig.ProductionVariantProperty", jsii_struct_bases=[_ProductionVariantProperty])
    class ProductionVariantProperty(_ProductionVariantProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sagemaker-endpointconfig-productionvariant.html
        Stability:
            stable
        """
        initialInstanceCount: jsii.Number
        """``CfnEndpointConfig.ProductionVariantProperty.InitialInstanceCount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sagemaker-endpointconfig-productionvariant.html#cfn-sagemaker-endpointconfig-productionvariant-initialinstancecount
        Stability:
            stable
        """

        initialVariantWeight: jsii.Number
        """``CfnEndpointConfig.ProductionVariantProperty.InitialVariantWeight``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sagemaker-endpointconfig-productionvariant.html#cfn-sagemaker-endpointconfig-productionvariant-initialvariantweight
        Stability:
            stable
        """

        instanceType: str
        """``CfnEndpointConfig.ProductionVariantProperty.InstanceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sagemaker-endpointconfig-productionvariant.html#cfn-sagemaker-endpointconfig-productionvariant-instancetype
        Stability:
            stable
        """

        modelName: str
        """``CfnEndpointConfig.ProductionVariantProperty.ModelName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sagemaker-endpointconfig-productionvariant.html#cfn-sagemaker-endpointconfig-productionvariant-modelname
        Stability:
            stable
        """

        variantName: str
        """``CfnEndpointConfig.ProductionVariantProperty.VariantName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sagemaker-endpointconfig-productionvariant.html#cfn-sagemaker-endpointconfig-productionvariant-variantname
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnEndpointConfigProps(jsii.compat.TypedDict, total=False):
    endpointConfigName: str
    """``AWS::SageMaker::EndpointConfig.EndpointConfigName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-endpointconfig.html#cfn-sagemaker-endpointconfig-endpointconfigname
    Stability:
        stable
    """
    kmsKeyId: str
    """``AWS::SageMaker::EndpointConfig.KmsKeyId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-endpointconfig.html#cfn-sagemaker-endpointconfig-kmskeyid
    Stability:
        stable
    """
    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::SageMaker::EndpointConfig.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-endpointconfig.html#cfn-sagemaker-endpointconfig-tags
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-sagemaker.CfnEndpointConfigProps", jsii_struct_bases=[_CfnEndpointConfigProps])
class CfnEndpointConfigProps(_CfnEndpointConfigProps):
    """Properties for defining a ``AWS::SageMaker::EndpointConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-endpointconfig.html
    Stability:
        stable
    """
    productionVariants: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union["CfnEndpointConfig.ProductionVariantProperty", aws_cdk.core.IResolvable]]]
    """``AWS::SageMaker::EndpointConfig.ProductionVariants``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-endpointconfig.html#cfn-sagemaker-endpointconfig-productionvariants
    Stability:
        stable
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnEndpointProps(jsii.compat.TypedDict, total=False):
    endpointName: str
    """``AWS::SageMaker::Endpoint.EndpointName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-endpoint.html#cfn-sagemaker-endpoint-endpointname
    Stability:
        stable
    """
    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::SageMaker::Endpoint.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-endpoint.html#cfn-sagemaker-endpoint-tags
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-sagemaker.CfnEndpointProps", jsii_struct_bases=[_CfnEndpointProps])
class CfnEndpointProps(_CfnEndpointProps):
    """Properties for defining a ``AWS::SageMaker::Endpoint``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-endpoint.html
    Stability:
        stable
    """
    endpointConfigName: str
    """``AWS::SageMaker::Endpoint.EndpointConfigName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-endpoint.html#cfn-sagemaker-endpoint-endpointconfigname
    Stability:
        stable
    """

class CfnModel(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sagemaker.CfnModel"):
    """A CloudFormation ``AWS::SageMaker::Model``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-model.html
    Stability:
        stable
    cloudformationResource:
        AWS::SageMaker::Model
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, execution_role_arn: str, containers: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ContainerDefinitionProperty"]]]]]=None, model_name: typing.Optional[str]=None, primary_container: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ContainerDefinitionProperty"]]]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None, vpc_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["VpcConfigProperty"]]]=None) -> None:
        """Create a new ``AWS::SageMaker::Model``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            execution_role_arn: ``AWS::SageMaker::Model.ExecutionRoleArn``.
            containers: ``AWS::SageMaker::Model.Containers``.
            model_name: ``AWS::SageMaker::Model.ModelName``.
            primary_container: ``AWS::SageMaker::Model.PrimaryContainer``.
            tags: ``AWS::SageMaker::Model.Tags``.
            vpc_config: ``AWS::SageMaker::Model.VpcConfig``.

        Stability:
            experimental
        """
        props: CfnModelProps = {"executionRoleArn": execution_role_arn}

        if containers is not None:
            props["containers"] = containers

        if model_name is not None:
            props["modelName"] = model_name

        if primary_container is not None:
            props["primaryContainer"] = primary_container

        if tags is not None:
            props["tags"] = tags

        if vpc_config is not None:
            props["vpcConfig"] = vpc_config

        jsii.create(CfnModel, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="attrModelName")
    def attr_model_name(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            ModelName
        """
        return jsii.get(self, "attrModelName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::SageMaker::Model.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-model.html#cfn-sagemaker-model-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="executionRoleArn")
    def execution_role_arn(self) -> str:
        """``AWS::SageMaker::Model.ExecutionRoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-model.html#cfn-sagemaker-model-executionrolearn
        Stability:
            stable
        """
        return jsii.get(self, "executionRoleArn")

    @execution_role_arn.setter
    def execution_role_arn(self, value: str):
        return jsii.set(self, "executionRoleArn", value)

    @property
    @jsii.member(jsii_name="containers")
    def containers(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ContainerDefinitionProperty"]]]]]:
        """``AWS::SageMaker::Model.Containers``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-model.html#cfn-sagemaker-model-containers
        Stability:
            stable
        """
        return jsii.get(self, "containers")

    @containers.setter
    def containers(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ContainerDefinitionProperty"]]]]]):
        return jsii.set(self, "containers", value)

    @property
    @jsii.member(jsii_name="modelName")
    def model_name(self) -> typing.Optional[str]:
        """``AWS::SageMaker::Model.ModelName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-model.html#cfn-sagemaker-model-modelname
        Stability:
            stable
        """
        return jsii.get(self, "modelName")

    @model_name.setter
    def model_name(self, value: typing.Optional[str]):
        return jsii.set(self, "modelName", value)

    @property
    @jsii.member(jsii_name="primaryContainer")
    def primary_container(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ContainerDefinitionProperty"]]]:
        """``AWS::SageMaker::Model.PrimaryContainer``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-model.html#cfn-sagemaker-model-primarycontainer
        Stability:
            stable
        """
        return jsii.get(self, "primaryContainer")

    @primary_container.setter
    def primary_container(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ContainerDefinitionProperty"]]]):
        return jsii.set(self, "primaryContainer", value)

    @property
    @jsii.member(jsii_name="vpcConfig")
    def vpc_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["VpcConfigProperty"]]]:
        """``AWS::SageMaker::Model.VpcConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-model.html#cfn-sagemaker-model-vpcconfig
        Stability:
            stable
        """
        return jsii.get(self, "vpcConfig")

    @vpc_config.setter
    def vpc_config(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["VpcConfigProperty"]]]):
        return jsii.set(self, "vpcConfig", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ContainerDefinitionProperty(jsii.compat.TypedDict, total=False):
        containerHostname: str
        """``CfnModel.ContainerDefinitionProperty.ContainerHostname``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sagemaker-model-containerdefinition.html#cfn-sagemaker-model-containerdefinition-containerhostname
        Stability:
            stable
        """
        environment: typing.Any
        """``CfnModel.ContainerDefinitionProperty.Environment``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sagemaker-model-containerdefinition.html#cfn-sagemaker-model-containerdefinition-environment
        Stability:
            stable
        """
        modelDataUrl: str
        """``CfnModel.ContainerDefinitionProperty.ModelDataUrl``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sagemaker-model-containerdefinition.html#cfn-sagemaker-model-containerdefinition-modeldataurl
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-sagemaker.CfnModel.ContainerDefinitionProperty", jsii_struct_bases=[_ContainerDefinitionProperty])
    class ContainerDefinitionProperty(_ContainerDefinitionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sagemaker-model-containerdefinition.html
        Stability:
            stable
        """
        image: str
        """``CfnModel.ContainerDefinitionProperty.Image``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sagemaker-model-containerdefinition.html#cfn-sagemaker-model-containerdefinition-image
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-sagemaker.CfnModel.VpcConfigProperty", jsii_struct_bases=[])
    class VpcConfigProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sagemaker-model-vpcconfig.html
        Stability:
            stable
        """
        securityGroupIds: typing.List[str]
        """``CfnModel.VpcConfigProperty.SecurityGroupIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sagemaker-model-vpcconfig.html#cfn-sagemaker-model-vpcconfig-securitygroupids
        Stability:
            stable
        """

        subnets: typing.List[str]
        """``CfnModel.VpcConfigProperty.Subnets``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sagemaker-model-vpcconfig.html#cfn-sagemaker-model-vpcconfig-subnets
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnModelProps(jsii.compat.TypedDict, total=False):
    containers: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnModel.ContainerDefinitionProperty"]]]
    """``AWS::SageMaker::Model.Containers``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-model.html#cfn-sagemaker-model-containers
    Stability:
        stable
    """
    modelName: str
    """``AWS::SageMaker::Model.ModelName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-model.html#cfn-sagemaker-model-modelname
    Stability:
        stable
    """
    primaryContainer: typing.Union[aws_cdk.core.IResolvable, "CfnModel.ContainerDefinitionProperty"]
    """``AWS::SageMaker::Model.PrimaryContainer``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-model.html#cfn-sagemaker-model-primarycontainer
    Stability:
        stable
    """
    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::SageMaker::Model.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-model.html#cfn-sagemaker-model-tags
    Stability:
        stable
    """
    vpcConfig: typing.Union[aws_cdk.core.IResolvable, "CfnModel.VpcConfigProperty"]
    """``AWS::SageMaker::Model.VpcConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-model.html#cfn-sagemaker-model-vpcconfig
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-sagemaker.CfnModelProps", jsii_struct_bases=[_CfnModelProps])
class CfnModelProps(_CfnModelProps):
    """Properties for defining a ``AWS::SageMaker::Model``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-model.html
    Stability:
        stable
    """
    executionRoleArn: str
    """``AWS::SageMaker::Model.ExecutionRoleArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-model.html#cfn-sagemaker-model-executionrolearn
    Stability:
        stable
    """

class CfnNotebookInstance(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sagemaker.CfnNotebookInstance"):
    """A CloudFormation ``AWS::SageMaker::NotebookInstance``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html
    Stability:
        stable
    cloudformationResource:
        AWS::SageMaker::NotebookInstance
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, instance_type: str, role_arn: str, accelerator_types: typing.Optional[typing.List[str]]=None, additional_code_repositories: typing.Optional[typing.List[str]]=None, default_code_repository: typing.Optional[str]=None, direct_internet_access: typing.Optional[str]=None, kms_key_id: typing.Optional[str]=None, lifecycle_config_name: typing.Optional[str]=None, notebook_instance_name: typing.Optional[str]=None, root_access: typing.Optional[str]=None, security_group_ids: typing.Optional[typing.List[str]]=None, subnet_id: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None, volume_size_in_gb: typing.Optional[jsii.Number]=None) -> None:
        """Create a new ``AWS::SageMaker::NotebookInstance``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            instance_type: ``AWS::SageMaker::NotebookInstance.InstanceType``.
            role_arn: ``AWS::SageMaker::NotebookInstance.RoleArn``.
            accelerator_types: ``AWS::SageMaker::NotebookInstance.AcceleratorTypes``.
            additional_code_repositories: ``AWS::SageMaker::NotebookInstance.AdditionalCodeRepositories``.
            default_code_repository: ``AWS::SageMaker::NotebookInstance.DefaultCodeRepository``.
            direct_internet_access: ``AWS::SageMaker::NotebookInstance.DirectInternetAccess``.
            kms_key_id: ``AWS::SageMaker::NotebookInstance.KmsKeyId``.
            lifecycle_config_name: ``AWS::SageMaker::NotebookInstance.LifecycleConfigName``.
            notebook_instance_name: ``AWS::SageMaker::NotebookInstance.NotebookInstanceName``.
            root_access: ``AWS::SageMaker::NotebookInstance.RootAccess``.
            security_group_ids: ``AWS::SageMaker::NotebookInstance.SecurityGroupIds``.
            subnet_id: ``AWS::SageMaker::NotebookInstance.SubnetId``.
            tags: ``AWS::SageMaker::NotebookInstance.Tags``.
            volume_size_in_gb: ``AWS::SageMaker::NotebookInstance.VolumeSizeInGB``.

        Stability:
            experimental
        """
        props: CfnNotebookInstanceProps = {"instanceType": instance_type, "roleArn": role_arn}

        if accelerator_types is not None:
            props["acceleratorTypes"] = accelerator_types

        if additional_code_repositories is not None:
            props["additionalCodeRepositories"] = additional_code_repositories

        if default_code_repository is not None:
            props["defaultCodeRepository"] = default_code_repository

        if direct_internet_access is not None:
            props["directInternetAccess"] = direct_internet_access

        if kms_key_id is not None:
            props["kmsKeyId"] = kms_key_id

        if lifecycle_config_name is not None:
            props["lifecycleConfigName"] = lifecycle_config_name

        if notebook_instance_name is not None:
            props["notebookInstanceName"] = notebook_instance_name

        if root_access is not None:
            props["rootAccess"] = root_access

        if security_group_ids is not None:
            props["securityGroupIds"] = security_group_ids

        if subnet_id is not None:
            props["subnetId"] = subnet_id

        if tags is not None:
            props["tags"] = tags

        if volume_size_in_gb is not None:
            props["volumeSizeInGb"] = volume_size_in_gb

        jsii.create(CfnNotebookInstance, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="attrNotebookInstanceName")
    def attr_notebook_instance_name(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            NotebookInstanceName
        """
        return jsii.get(self, "attrNotebookInstanceName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::SageMaker::NotebookInstance.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> str:
        """``AWS::SageMaker::NotebookInstance.InstanceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-instancetype
        Stability:
            stable
        """
        return jsii.get(self, "instanceType")

    @instance_type.setter
    def instance_type(self, value: str):
        return jsii.set(self, "instanceType", value)

    @property
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> str:
        """``AWS::SageMaker::NotebookInstance.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-rolearn
        Stability:
            stable
        """
        return jsii.get(self, "roleArn")

    @role_arn.setter
    def role_arn(self, value: str):
        return jsii.set(self, "roleArn", value)

    @property
    @jsii.member(jsii_name="acceleratorTypes")
    def accelerator_types(self) -> typing.Optional[typing.List[str]]:
        """``AWS::SageMaker::NotebookInstance.AcceleratorTypes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-acceleratortypes
        Stability:
            stable
        """
        return jsii.get(self, "acceleratorTypes")

    @accelerator_types.setter
    def accelerator_types(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "acceleratorTypes", value)

    @property
    @jsii.member(jsii_name="additionalCodeRepositories")
    def additional_code_repositories(self) -> typing.Optional[typing.List[str]]:
        """``AWS::SageMaker::NotebookInstance.AdditionalCodeRepositories``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-additionalcoderepositories
        Stability:
            stable
        """
        return jsii.get(self, "additionalCodeRepositories")

    @additional_code_repositories.setter
    def additional_code_repositories(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "additionalCodeRepositories", value)

    @property
    @jsii.member(jsii_name="defaultCodeRepository")
    def default_code_repository(self) -> typing.Optional[str]:
        """``AWS::SageMaker::NotebookInstance.DefaultCodeRepository``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-defaultcoderepository
        Stability:
            stable
        """
        return jsii.get(self, "defaultCodeRepository")

    @default_code_repository.setter
    def default_code_repository(self, value: typing.Optional[str]):
        return jsii.set(self, "defaultCodeRepository", value)

    @property
    @jsii.member(jsii_name="directInternetAccess")
    def direct_internet_access(self) -> typing.Optional[str]:
        """``AWS::SageMaker::NotebookInstance.DirectInternetAccess``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-directinternetaccess
        Stability:
            stable
        """
        return jsii.get(self, "directInternetAccess")

    @direct_internet_access.setter
    def direct_internet_access(self, value: typing.Optional[str]):
        return jsii.set(self, "directInternetAccess", value)

    @property
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> typing.Optional[str]:
        """``AWS::SageMaker::NotebookInstance.KmsKeyId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-kmskeyid
        Stability:
            stable
        """
        return jsii.get(self, "kmsKeyId")

    @kms_key_id.setter
    def kms_key_id(self, value: typing.Optional[str]):
        return jsii.set(self, "kmsKeyId", value)

    @property
    @jsii.member(jsii_name="lifecycleConfigName")
    def lifecycle_config_name(self) -> typing.Optional[str]:
        """``AWS::SageMaker::NotebookInstance.LifecycleConfigName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-lifecycleconfigname
        Stability:
            stable
        """
        return jsii.get(self, "lifecycleConfigName")

    @lifecycle_config_name.setter
    def lifecycle_config_name(self, value: typing.Optional[str]):
        return jsii.set(self, "lifecycleConfigName", value)

    @property
    @jsii.member(jsii_name="notebookInstanceName")
    def notebook_instance_name(self) -> typing.Optional[str]:
        """``AWS::SageMaker::NotebookInstance.NotebookInstanceName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-notebookinstancename
        Stability:
            stable
        """
        return jsii.get(self, "notebookInstanceName")

    @notebook_instance_name.setter
    def notebook_instance_name(self, value: typing.Optional[str]):
        return jsii.set(self, "notebookInstanceName", value)

    @property
    @jsii.member(jsii_name="rootAccess")
    def root_access(self) -> typing.Optional[str]:
        """``AWS::SageMaker::NotebookInstance.RootAccess``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-rootaccess
        Stability:
            stable
        """
        return jsii.get(self, "rootAccess")

    @root_access.setter
    def root_access(self, value: typing.Optional[str]):
        return jsii.set(self, "rootAccess", value)

    @property
    @jsii.member(jsii_name="securityGroupIds")
    def security_group_ids(self) -> typing.Optional[typing.List[str]]:
        """``AWS::SageMaker::NotebookInstance.SecurityGroupIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-securitygroupids
        Stability:
            stable
        """
        return jsii.get(self, "securityGroupIds")

    @security_group_ids.setter
    def security_group_ids(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "securityGroupIds", value)

    @property
    @jsii.member(jsii_name="subnetId")
    def subnet_id(self) -> typing.Optional[str]:
        """``AWS::SageMaker::NotebookInstance.SubnetId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-subnetid
        Stability:
            stable
        """
        return jsii.get(self, "subnetId")

    @subnet_id.setter
    def subnet_id(self, value: typing.Optional[str]):
        return jsii.set(self, "subnetId", value)

    @property
    @jsii.member(jsii_name="volumeSizeInGb")
    def volume_size_in_gb(self) -> typing.Optional[jsii.Number]:
        """``AWS::SageMaker::NotebookInstance.VolumeSizeInGB``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-volumesizeingb
        Stability:
            stable
        """
        return jsii.get(self, "volumeSizeInGb")

    @volume_size_in_gb.setter
    def volume_size_in_gb(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "volumeSizeInGb", value)


class CfnNotebookInstanceLifecycleConfig(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sagemaker.CfnNotebookInstanceLifecycleConfig"):
    """A CloudFormation ``AWS::SageMaker::NotebookInstanceLifecycleConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstancelifecycleconfig.html
    Stability:
        stable
    cloudformationResource:
        AWS::SageMaker::NotebookInstanceLifecycleConfig
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, notebook_instance_lifecycle_config_name: typing.Optional[str]=None, on_create: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "NotebookInstanceLifecycleHookProperty"]]]]]=None, on_start: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "NotebookInstanceLifecycleHookProperty"]]]]]=None) -> None:
        """Create a new ``AWS::SageMaker::NotebookInstanceLifecycleConfig``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            notebook_instance_lifecycle_config_name: ``AWS::SageMaker::NotebookInstanceLifecycleConfig.NotebookInstanceLifecycleConfigName``.
            on_create: ``AWS::SageMaker::NotebookInstanceLifecycleConfig.OnCreate``.
            on_start: ``AWS::SageMaker::NotebookInstanceLifecycleConfig.OnStart``.

        Stability:
            experimental
        """
        props: CfnNotebookInstanceLifecycleConfigProps = {}

        if notebook_instance_lifecycle_config_name is not None:
            props["notebookInstanceLifecycleConfigName"] = notebook_instance_lifecycle_config_name

        if on_create is not None:
            props["onCreate"] = on_create

        if on_start is not None:
            props["onStart"] = on_start

        jsii.create(CfnNotebookInstanceLifecycleConfig, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="attrNotebookInstanceLifecycleConfigName")
    def attr_notebook_instance_lifecycle_config_name(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            NotebookInstanceLifecycleConfigName
        """
        return jsii.get(self, "attrNotebookInstanceLifecycleConfigName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="notebookInstanceLifecycleConfigName")
    def notebook_instance_lifecycle_config_name(self) -> typing.Optional[str]:
        """``AWS::SageMaker::NotebookInstanceLifecycleConfig.NotebookInstanceLifecycleConfigName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstancelifecycleconfig.html#cfn-sagemaker-notebookinstancelifecycleconfig-notebookinstancelifecycleconfigname
        Stability:
            stable
        """
        return jsii.get(self, "notebookInstanceLifecycleConfigName")

    @notebook_instance_lifecycle_config_name.setter
    def notebook_instance_lifecycle_config_name(self, value: typing.Optional[str]):
        return jsii.set(self, "notebookInstanceLifecycleConfigName", value)

    @property
    @jsii.member(jsii_name="onCreate")
    def on_create(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "NotebookInstanceLifecycleHookProperty"]]]]]:
        """``AWS::SageMaker::NotebookInstanceLifecycleConfig.OnCreate``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstancelifecycleconfig.html#cfn-sagemaker-notebookinstancelifecycleconfig-oncreate
        Stability:
            stable
        """
        return jsii.get(self, "onCreate")

    @on_create.setter
    def on_create(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "NotebookInstanceLifecycleHookProperty"]]]]]):
        return jsii.set(self, "onCreate", value)

    @property
    @jsii.member(jsii_name="onStart")
    def on_start(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "NotebookInstanceLifecycleHookProperty"]]]]]:
        """``AWS::SageMaker::NotebookInstanceLifecycleConfig.OnStart``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstancelifecycleconfig.html#cfn-sagemaker-notebookinstancelifecycleconfig-onstart
        Stability:
            stable
        """
        return jsii.get(self, "onStart")

    @on_start.setter
    def on_start(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "NotebookInstanceLifecycleHookProperty"]]]]]):
        return jsii.set(self, "onStart", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-sagemaker.CfnNotebookInstanceLifecycleConfig.NotebookInstanceLifecycleHookProperty", jsii_struct_bases=[])
    class NotebookInstanceLifecycleHookProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sagemaker-notebookinstancelifecycleconfig-notebookinstancelifecyclehook.html
        Stability:
            stable
        """
        content: str
        """``CfnNotebookInstanceLifecycleConfig.NotebookInstanceLifecycleHookProperty.Content``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sagemaker-notebookinstancelifecycleconfig-notebookinstancelifecyclehook.html#cfn-sagemaker-notebookinstancelifecycleconfig-notebookinstancelifecyclehook-content
        Stability:
            stable
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-sagemaker.CfnNotebookInstanceLifecycleConfigProps", jsii_struct_bases=[])
class CfnNotebookInstanceLifecycleConfigProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::SageMaker::NotebookInstanceLifecycleConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstancelifecycleconfig.html
    Stability:
        stable
    """
    notebookInstanceLifecycleConfigName: str
    """``AWS::SageMaker::NotebookInstanceLifecycleConfig.NotebookInstanceLifecycleConfigName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstancelifecycleconfig.html#cfn-sagemaker-notebookinstancelifecycleconfig-notebookinstancelifecycleconfigname
    Stability:
        stable
    """

    onCreate: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnNotebookInstanceLifecycleConfig.NotebookInstanceLifecycleHookProperty"]]]
    """``AWS::SageMaker::NotebookInstanceLifecycleConfig.OnCreate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstancelifecycleconfig.html#cfn-sagemaker-notebookinstancelifecycleconfig-oncreate
    Stability:
        stable
    """

    onStart: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnNotebookInstanceLifecycleConfig.NotebookInstanceLifecycleHookProperty"]]]
    """``AWS::SageMaker::NotebookInstanceLifecycleConfig.OnStart``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstancelifecycleconfig.html#cfn-sagemaker-notebookinstancelifecycleconfig-onstart
    Stability:
        stable
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnNotebookInstanceProps(jsii.compat.TypedDict, total=False):
    acceleratorTypes: typing.List[str]
    """``AWS::SageMaker::NotebookInstance.AcceleratorTypes``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-acceleratortypes
    Stability:
        stable
    """
    additionalCodeRepositories: typing.List[str]
    """``AWS::SageMaker::NotebookInstance.AdditionalCodeRepositories``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-additionalcoderepositories
    Stability:
        stable
    """
    defaultCodeRepository: str
    """``AWS::SageMaker::NotebookInstance.DefaultCodeRepository``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-defaultcoderepository
    Stability:
        stable
    """
    directInternetAccess: str
    """``AWS::SageMaker::NotebookInstance.DirectInternetAccess``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-directinternetaccess
    Stability:
        stable
    """
    kmsKeyId: str
    """``AWS::SageMaker::NotebookInstance.KmsKeyId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-kmskeyid
    Stability:
        stable
    """
    lifecycleConfigName: str
    """``AWS::SageMaker::NotebookInstance.LifecycleConfigName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-lifecycleconfigname
    Stability:
        stable
    """
    notebookInstanceName: str
    """``AWS::SageMaker::NotebookInstance.NotebookInstanceName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-notebookinstancename
    Stability:
        stable
    """
    rootAccess: str
    """``AWS::SageMaker::NotebookInstance.RootAccess``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-rootaccess
    Stability:
        stable
    """
    securityGroupIds: typing.List[str]
    """``AWS::SageMaker::NotebookInstance.SecurityGroupIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-securitygroupids
    Stability:
        stable
    """
    subnetId: str
    """``AWS::SageMaker::NotebookInstance.SubnetId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-subnetid
    Stability:
        stable
    """
    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::SageMaker::NotebookInstance.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-tags
    Stability:
        stable
    """
    volumeSizeInGb: jsii.Number
    """``AWS::SageMaker::NotebookInstance.VolumeSizeInGB``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-volumesizeingb
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-sagemaker.CfnNotebookInstanceProps", jsii_struct_bases=[_CfnNotebookInstanceProps])
class CfnNotebookInstanceProps(_CfnNotebookInstanceProps):
    """Properties for defining a ``AWS::SageMaker::NotebookInstance``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html
    Stability:
        stable
    """
    instanceType: str
    """``AWS::SageMaker::NotebookInstance.InstanceType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-instancetype
    Stability:
        stable
    """

    roleArn: str
    """``AWS::SageMaker::NotebookInstance.RoleArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-rolearn
    Stability:
        stable
    """

__all__ = ["CfnEndpoint", "CfnEndpointConfig", "CfnEndpointConfigProps", "CfnEndpointProps", "CfnModel", "CfnModelProps", "CfnNotebookInstance", "CfnNotebookInstanceLifecycleConfig", "CfnNotebookInstanceLifecycleConfigProps", "CfnNotebookInstanceProps", "__jsii_assembly__"]

publication.publish()
