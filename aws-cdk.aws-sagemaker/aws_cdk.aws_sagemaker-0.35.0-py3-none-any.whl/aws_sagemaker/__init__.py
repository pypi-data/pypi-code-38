import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-sagemaker", "0.35.0", __name__, "aws-sagemaker@0.35.0.jsii.tgz")
class CfnEndpoint(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sagemaker.CfnEndpoint"):
    """A CloudFormation ``AWS::SageMaker::Endpoint``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-endpoint.html
    Stability:
        experimental
    cloudformationResource:
        AWS::SageMaker::Endpoint
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, endpoint_config_name: str, endpoint_name: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::SageMaker::Endpoint``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            endpointConfigName: ``AWS::SageMaker::Endpoint.EndpointConfigName``.
            endpointName: ``AWS::SageMaker::Endpoint.EndpointName``.
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
            experimental
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="cfnResourceTypeName")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            experimental
        """
        return jsii.sget(cls, "cfnResourceTypeName")

    @property
    @jsii.member(jsii_name="attrEndpointName")
    def attr_endpoint_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            EndpointName
        """
        return jsii.get(self, "attrEndpointName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.cdk.TagManager:
        """``AWS::SageMaker::Endpoint.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-endpoint.html#cfn-sagemaker-endpoint-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="endpointConfigName")
    def endpoint_config_name(self) -> str:
        """``AWS::SageMaker::Endpoint.EndpointConfigName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-endpoint.html#cfn-sagemaker-endpoint-endpointconfigname
        Stability:
            experimental
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
            experimental
        """
        return jsii.get(self, "endpointName")

    @endpoint_name.setter
    def endpoint_name(self, value: typing.Optional[str]):
        return jsii.set(self, "endpointName", value)


class CfnEndpointConfig(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sagemaker.CfnEndpointConfig"):
    """A CloudFormation ``AWS::SageMaker::EndpointConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-endpointconfig.html
    Stability:
        experimental
    cloudformationResource:
        AWS::SageMaker::EndpointConfig
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, production_variants: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union["ProductionVariantProperty", aws_cdk.cdk.IResolvable]]], endpoint_config_name: typing.Optional[str]=None, kms_key_id: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::SageMaker::EndpointConfig``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            productionVariants: ``AWS::SageMaker::EndpointConfig.ProductionVariants``.
            endpointConfigName: ``AWS::SageMaker::EndpointConfig.EndpointConfigName``.
            kmsKeyId: ``AWS::SageMaker::EndpointConfig.KmsKeyId``.
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
            experimental
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="cfnResourceTypeName")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            experimental
        """
        return jsii.sget(cls, "cfnResourceTypeName")

    @property
    @jsii.member(jsii_name="attrEndpointConfigName")
    def attr_endpoint_config_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            EndpointConfigName
        """
        return jsii.get(self, "attrEndpointConfigName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.cdk.TagManager:
        """``AWS::SageMaker::EndpointConfig.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-endpointconfig.html#cfn-sagemaker-endpointconfig-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="productionVariants")
    def production_variants(self) -> typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union["ProductionVariantProperty", aws_cdk.cdk.IResolvable]]]:
        """``AWS::SageMaker::EndpointConfig.ProductionVariants``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-endpointconfig.html#cfn-sagemaker-endpointconfig-productionvariants
        Stability:
            experimental
        """
        return jsii.get(self, "productionVariants")

    @production_variants.setter
    def production_variants(self, value: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union["ProductionVariantProperty", aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "productionVariants", value)

    @property
    @jsii.member(jsii_name="endpointConfigName")
    def endpoint_config_name(self) -> typing.Optional[str]:
        """``AWS::SageMaker::EndpointConfig.EndpointConfigName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-endpointconfig.html#cfn-sagemaker-endpointconfig-endpointconfigname
        Stability:
            experimental
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
            experimental
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
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-sagemaker.CfnEndpointConfig.ProductionVariantProperty", jsii_struct_bases=[_ProductionVariantProperty])
    class ProductionVariantProperty(_ProductionVariantProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sagemaker-endpointconfig-productionvariant.html
        Stability:
            experimental
        """
        initialInstanceCount: jsii.Number
        """``CfnEndpointConfig.ProductionVariantProperty.InitialInstanceCount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sagemaker-endpointconfig-productionvariant.html#cfn-sagemaker-endpointconfig-productionvariant-initialinstancecount
        Stability:
            experimental
        """

        initialVariantWeight: jsii.Number
        """``CfnEndpointConfig.ProductionVariantProperty.InitialVariantWeight``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sagemaker-endpointconfig-productionvariant.html#cfn-sagemaker-endpointconfig-productionvariant-initialvariantweight
        Stability:
            experimental
        """

        instanceType: str
        """``CfnEndpointConfig.ProductionVariantProperty.InstanceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sagemaker-endpointconfig-productionvariant.html#cfn-sagemaker-endpointconfig-productionvariant-instancetype
        Stability:
            experimental
        """

        modelName: str
        """``CfnEndpointConfig.ProductionVariantProperty.ModelName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sagemaker-endpointconfig-productionvariant.html#cfn-sagemaker-endpointconfig-productionvariant-modelname
        Stability:
            experimental
        """

        variantName: str
        """``CfnEndpointConfig.ProductionVariantProperty.VariantName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sagemaker-endpointconfig-productionvariant.html#cfn-sagemaker-endpointconfig-productionvariant-variantname
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnEndpointConfigProps(jsii.compat.TypedDict, total=False):
    endpointConfigName: str
    """``AWS::SageMaker::EndpointConfig.EndpointConfigName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-endpointconfig.html#cfn-sagemaker-endpointconfig-endpointconfigname
    Stability:
        experimental
    """
    kmsKeyId: str
    """``AWS::SageMaker::EndpointConfig.KmsKeyId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-endpointconfig.html#cfn-sagemaker-endpointconfig-kmskeyid
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::SageMaker::EndpointConfig.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-endpointconfig.html#cfn-sagemaker-endpointconfig-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-sagemaker.CfnEndpointConfigProps", jsii_struct_bases=[_CfnEndpointConfigProps])
class CfnEndpointConfigProps(_CfnEndpointConfigProps):
    """Properties for defining a ``AWS::SageMaker::EndpointConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-endpointconfig.html
    Stability:
        experimental
    """
    productionVariants: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union["CfnEndpointConfig.ProductionVariantProperty", aws_cdk.cdk.IResolvable]]]
    """``AWS::SageMaker::EndpointConfig.ProductionVariants``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-endpointconfig.html#cfn-sagemaker-endpointconfig-productionvariants
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnEndpointProps(jsii.compat.TypedDict, total=False):
    endpointName: str
    """``AWS::SageMaker::Endpoint.EndpointName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-endpoint.html#cfn-sagemaker-endpoint-endpointname
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::SageMaker::Endpoint.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-endpoint.html#cfn-sagemaker-endpoint-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-sagemaker.CfnEndpointProps", jsii_struct_bases=[_CfnEndpointProps])
class CfnEndpointProps(_CfnEndpointProps):
    """Properties for defining a ``AWS::SageMaker::Endpoint``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-endpoint.html
    Stability:
        experimental
    """
    endpointConfigName: str
    """``AWS::SageMaker::Endpoint.EndpointConfigName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-endpoint.html#cfn-sagemaker-endpoint-endpointconfigname
    Stability:
        experimental
    """

class CfnModel(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sagemaker.CfnModel"):
    """A CloudFormation ``AWS::SageMaker::Model``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-model.html
    Stability:
        experimental
    cloudformationResource:
        AWS::SageMaker::Model
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, execution_role_arn: str, containers: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "ContainerDefinitionProperty"]]]]]=None, model_name: typing.Optional[str]=None, primary_container: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["ContainerDefinitionProperty"]]]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, vpc_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["VpcConfigProperty"]]]=None) -> None:
        """Create a new ``AWS::SageMaker::Model``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            executionRoleArn: ``AWS::SageMaker::Model.ExecutionRoleArn``.
            containers: ``AWS::SageMaker::Model.Containers``.
            modelName: ``AWS::SageMaker::Model.ModelName``.
            primaryContainer: ``AWS::SageMaker::Model.PrimaryContainer``.
            tags: ``AWS::SageMaker::Model.Tags``.
            vpcConfig: ``AWS::SageMaker::Model.VpcConfig``.

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
            experimental
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="cfnResourceTypeName")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            experimental
        """
        return jsii.sget(cls, "cfnResourceTypeName")

    @property
    @jsii.member(jsii_name="attrModelName")
    def attr_model_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ModelName
        """
        return jsii.get(self, "attrModelName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.cdk.TagManager:
        """``AWS::SageMaker::Model.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-model.html#cfn-sagemaker-model-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="executionRoleArn")
    def execution_role_arn(self) -> str:
        """``AWS::SageMaker::Model.ExecutionRoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-model.html#cfn-sagemaker-model-executionrolearn
        Stability:
            experimental
        """
        return jsii.get(self, "executionRoleArn")

    @execution_role_arn.setter
    def execution_role_arn(self, value: str):
        return jsii.set(self, "executionRoleArn", value)

    @property
    @jsii.member(jsii_name="containers")
    def containers(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "ContainerDefinitionProperty"]]]]]:
        """``AWS::SageMaker::Model.Containers``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-model.html#cfn-sagemaker-model-containers
        Stability:
            experimental
        """
        return jsii.get(self, "containers")

    @containers.setter
    def containers(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "ContainerDefinitionProperty"]]]]]):
        return jsii.set(self, "containers", value)

    @property
    @jsii.member(jsii_name="modelName")
    def model_name(self) -> typing.Optional[str]:
        """``AWS::SageMaker::Model.ModelName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-model.html#cfn-sagemaker-model-modelname
        Stability:
            experimental
        """
        return jsii.get(self, "modelName")

    @model_name.setter
    def model_name(self, value: typing.Optional[str]):
        return jsii.set(self, "modelName", value)

    @property
    @jsii.member(jsii_name="primaryContainer")
    def primary_container(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["ContainerDefinitionProperty"]]]:
        """``AWS::SageMaker::Model.PrimaryContainer``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-model.html#cfn-sagemaker-model-primarycontainer
        Stability:
            experimental
        """
        return jsii.get(self, "primaryContainer")

    @primary_container.setter
    def primary_container(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["ContainerDefinitionProperty"]]]):
        return jsii.set(self, "primaryContainer", value)

    @property
    @jsii.member(jsii_name="vpcConfig")
    def vpc_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["VpcConfigProperty"]]]:
        """``AWS::SageMaker::Model.VpcConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-model.html#cfn-sagemaker-model-vpcconfig
        Stability:
            experimental
        """
        return jsii.get(self, "vpcConfig")

    @vpc_config.setter
    def vpc_config(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["VpcConfigProperty"]]]):
        return jsii.set(self, "vpcConfig", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ContainerDefinitionProperty(jsii.compat.TypedDict, total=False):
        containerHostname: str
        """``CfnModel.ContainerDefinitionProperty.ContainerHostname``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sagemaker-model-containerdefinition.html#cfn-sagemaker-model-containerdefinition-containerhostname
        Stability:
            experimental
        """
        environment: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.IResolvable]
        """``CfnModel.ContainerDefinitionProperty.Environment``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sagemaker-model-containerdefinition.html#cfn-sagemaker-model-containerdefinition-environment
        Stability:
            experimental
        """
        modelDataUrl: str
        """``CfnModel.ContainerDefinitionProperty.ModelDataUrl``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sagemaker-model-containerdefinition.html#cfn-sagemaker-model-containerdefinition-modeldataurl
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-sagemaker.CfnModel.ContainerDefinitionProperty", jsii_struct_bases=[_ContainerDefinitionProperty])
    class ContainerDefinitionProperty(_ContainerDefinitionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sagemaker-model-containerdefinition.html
        Stability:
            experimental
        """
        image: str
        """``CfnModel.ContainerDefinitionProperty.Image``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sagemaker-model-containerdefinition.html#cfn-sagemaker-model-containerdefinition-image
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-sagemaker.CfnModel.VpcConfigProperty", jsii_struct_bases=[])
    class VpcConfigProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sagemaker-model-vpcconfig.html
        Stability:
            experimental
        """
        securityGroupIds: typing.List[str]
        """``CfnModel.VpcConfigProperty.SecurityGroupIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sagemaker-model-vpcconfig.html#cfn-sagemaker-model-vpcconfig-securitygroupids
        Stability:
            experimental
        """

        subnets: typing.List[str]
        """``CfnModel.VpcConfigProperty.Subnets``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sagemaker-model-vpcconfig.html#cfn-sagemaker-model-vpcconfig-subnets
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnModelProps(jsii.compat.TypedDict, total=False):
    containers: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnModel.ContainerDefinitionProperty"]]]
    """``AWS::SageMaker::Model.Containers``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-model.html#cfn-sagemaker-model-containers
    Stability:
        experimental
    """
    modelName: str
    """``AWS::SageMaker::Model.ModelName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-model.html#cfn-sagemaker-model-modelname
    Stability:
        experimental
    """
    primaryContainer: typing.Union[aws_cdk.cdk.IResolvable, "CfnModel.ContainerDefinitionProperty"]
    """``AWS::SageMaker::Model.PrimaryContainer``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-model.html#cfn-sagemaker-model-primarycontainer
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::SageMaker::Model.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-model.html#cfn-sagemaker-model-tags
    Stability:
        experimental
    """
    vpcConfig: typing.Union[aws_cdk.cdk.IResolvable, "CfnModel.VpcConfigProperty"]
    """``AWS::SageMaker::Model.VpcConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-model.html#cfn-sagemaker-model-vpcconfig
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-sagemaker.CfnModelProps", jsii_struct_bases=[_CfnModelProps])
class CfnModelProps(_CfnModelProps):
    """Properties for defining a ``AWS::SageMaker::Model``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-model.html
    Stability:
        experimental
    """
    executionRoleArn: str
    """``AWS::SageMaker::Model.ExecutionRoleArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-model.html#cfn-sagemaker-model-executionrolearn
    Stability:
        experimental
    """

class CfnNotebookInstance(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sagemaker.CfnNotebookInstance"):
    """A CloudFormation ``AWS::SageMaker::NotebookInstance``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html
    Stability:
        experimental
    cloudformationResource:
        AWS::SageMaker::NotebookInstance
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, instance_type: str, role_arn: str, accelerator_types: typing.Optional[typing.List[str]]=None, additional_code_repositories: typing.Optional[typing.List[str]]=None, default_code_repository: typing.Optional[str]=None, direct_internet_access: typing.Optional[str]=None, kms_key_id: typing.Optional[str]=None, lifecycle_config_name: typing.Optional[str]=None, notebook_instance_name: typing.Optional[str]=None, root_access: typing.Optional[str]=None, security_group_ids: typing.Optional[typing.List[str]]=None, subnet_id: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, volume_size_in_gb: typing.Optional[jsii.Number]=None) -> None:
        """Create a new ``AWS::SageMaker::NotebookInstance``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            instanceType: ``AWS::SageMaker::NotebookInstance.InstanceType``.
            roleArn: ``AWS::SageMaker::NotebookInstance.RoleArn``.
            acceleratorTypes: ``AWS::SageMaker::NotebookInstance.AcceleratorTypes``.
            additionalCodeRepositories: ``AWS::SageMaker::NotebookInstance.AdditionalCodeRepositories``.
            defaultCodeRepository: ``AWS::SageMaker::NotebookInstance.DefaultCodeRepository``.
            directInternetAccess: ``AWS::SageMaker::NotebookInstance.DirectInternetAccess``.
            kmsKeyId: ``AWS::SageMaker::NotebookInstance.KmsKeyId``.
            lifecycleConfigName: ``AWS::SageMaker::NotebookInstance.LifecycleConfigName``.
            notebookInstanceName: ``AWS::SageMaker::NotebookInstance.NotebookInstanceName``.
            rootAccess: ``AWS::SageMaker::NotebookInstance.RootAccess``.
            securityGroupIds: ``AWS::SageMaker::NotebookInstance.SecurityGroupIds``.
            subnetId: ``AWS::SageMaker::NotebookInstance.SubnetId``.
            tags: ``AWS::SageMaker::NotebookInstance.Tags``.
            volumeSizeInGb: ``AWS::SageMaker::NotebookInstance.VolumeSizeInGB``.

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
            experimental
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="cfnResourceTypeName")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            experimental
        """
        return jsii.sget(cls, "cfnResourceTypeName")

    @property
    @jsii.member(jsii_name="attrNotebookInstanceName")
    def attr_notebook_instance_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            NotebookInstanceName
        """
        return jsii.get(self, "attrNotebookInstanceName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.cdk.TagManager:
        """``AWS::SageMaker::NotebookInstance.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> str:
        """``AWS::SageMaker::NotebookInstance.InstanceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-instancetype
        Stability:
            experimental
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
            experimental
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
            experimental
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
            experimental
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
            experimental
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
            experimental
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
            experimental
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
            experimental
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
            experimental
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
            experimental
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
            experimental
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
            experimental
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
            experimental
        """
        return jsii.get(self, "volumeSizeInGb")

    @volume_size_in_gb.setter
    def volume_size_in_gb(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "volumeSizeInGb", value)


class CfnNotebookInstanceLifecycleConfig(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sagemaker.CfnNotebookInstanceLifecycleConfig"):
    """A CloudFormation ``AWS::SageMaker::NotebookInstanceLifecycleConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstancelifecycleconfig.html
    Stability:
        experimental
    cloudformationResource:
        AWS::SageMaker::NotebookInstanceLifecycleConfig
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, notebook_instance_lifecycle_config_name: typing.Optional[str]=None, on_create: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "NotebookInstanceLifecycleHookProperty"]]]]]=None, on_start: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "NotebookInstanceLifecycleHookProperty"]]]]]=None) -> None:
        """Create a new ``AWS::SageMaker::NotebookInstanceLifecycleConfig``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            notebookInstanceLifecycleConfigName: ``AWS::SageMaker::NotebookInstanceLifecycleConfig.NotebookInstanceLifecycleConfigName``.
            onCreate: ``AWS::SageMaker::NotebookInstanceLifecycleConfig.OnCreate``.
            onStart: ``AWS::SageMaker::NotebookInstanceLifecycleConfig.OnStart``.

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
            experimental
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="cfnResourceTypeName")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            experimental
        """
        return jsii.sget(cls, "cfnResourceTypeName")

    @property
    @jsii.member(jsii_name="attrNotebookInstanceLifecycleConfigName")
    def attr_notebook_instance_lifecycle_config_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            NotebookInstanceLifecycleConfigName
        """
        return jsii.get(self, "attrNotebookInstanceLifecycleConfigName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="notebookInstanceLifecycleConfigName")
    def notebook_instance_lifecycle_config_name(self) -> typing.Optional[str]:
        """``AWS::SageMaker::NotebookInstanceLifecycleConfig.NotebookInstanceLifecycleConfigName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstancelifecycleconfig.html#cfn-sagemaker-notebookinstancelifecycleconfig-notebookinstancelifecycleconfigname
        Stability:
            experimental
        """
        return jsii.get(self, "notebookInstanceLifecycleConfigName")

    @notebook_instance_lifecycle_config_name.setter
    def notebook_instance_lifecycle_config_name(self, value: typing.Optional[str]):
        return jsii.set(self, "notebookInstanceLifecycleConfigName", value)

    @property
    @jsii.member(jsii_name="onCreate")
    def on_create(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "NotebookInstanceLifecycleHookProperty"]]]]]:
        """``AWS::SageMaker::NotebookInstanceLifecycleConfig.OnCreate``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstancelifecycleconfig.html#cfn-sagemaker-notebookinstancelifecycleconfig-oncreate
        Stability:
            experimental
        """
        return jsii.get(self, "onCreate")

    @on_create.setter
    def on_create(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "NotebookInstanceLifecycleHookProperty"]]]]]):
        return jsii.set(self, "onCreate", value)

    @property
    @jsii.member(jsii_name="onStart")
    def on_start(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "NotebookInstanceLifecycleHookProperty"]]]]]:
        """``AWS::SageMaker::NotebookInstanceLifecycleConfig.OnStart``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstancelifecycleconfig.html#cfn-sagemaker-notebookinstancelifecycleconfig-onstart
        Stability:
            experimental
        """
        return jsii.get(self, "onStart")

    @on_start.setter
    def on_start(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "NotebookInstanceLifecycleHookProperty"]]]]]):
        return jsii.set(self, "onStart", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-sagemaker.CfnNotebookInstanceLifecycleConfig.NotebookInstanceLifecycleHookProperty", jsii_struct_bases=[])
    class NotebookInstanceLifecycleHookProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sagemaker-notebookinstancelifecycleconfig-notebookinstancelifecyclehook.html
        Stability:
            experimental
        """
        content: str
        """``CfnNotebookInstanceLifecycleConfig.NotebookInstanceLifecycleHookProperty.Content``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sagemaker-notebookinstancelifecycleconfig-notebookinstancelifecyclehook.html#cfn-sagemaker-notebookinstancelifecycleconfig-notebookinstancelifecyclehook-content
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-sagemaker.CfnNotebookInstanceLifecycleConfigProps", jsii_struct_bases=[])
class CfnNotebookInstanceLifecycleConfigProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::SageMaker::NotebookInstanceLifecycleConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstancelifecycleconfig.html
    Stability:
        experimental
    """
    notebookInstanceLifecycleConfigName: str
    """``AWS::SageMaker::NotebookInstanceLifecycleConfig.NotebookInstanceLifecycleConfigName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstancelifecycleconfig.html#cfn-sagemaker-notebookinstancelifecycleconfig-notebookinstancelifecycleconfigname
    Stability:
        experimental
    """

    onCreate: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnNotebookInstanceLifecycleConfig.NotebookInstanceLifecycleHookProperty"]]]
    """``AWS::SageMaker::NotebookInstanceLifecycleConfig.OnCreate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstancelifecycleconfig.html#cfn-sagemaker-notebookinstancelifecycleconfig-oncreate
    Stability:
        experimental
    """

    onStart: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnNotebookInstanceLifecycleConfig.NotebookInstanceLifecycleHookProperty"]]]
    """``AWS::SageMaker::NotebookInstanceLifecycleConfig.OnStart``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstancelifecycleconfig.html#cfn-sagemaker-notebookinstancelifecycleconfig-onstart
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnNotebookInstanceProps(jsii.compat.TypedDict, total=False):
    acceleratorTypes: typing.List[str]
    """``AWS::SageMaker::NotebookInstance.AcceleratorTypes``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-acceleratortypes
    Stability:
        experimental
    """
    additionalCodeRepositories: typing.List[str]
    """``AWS::SageMaker::NotebookInstance.AdditionalCodeRepositories``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-additionalcoderepositories
    Stability:
        experimental
    """
    defaultCodeRepository: str
    """``AWS::SageMaker::NotebookInstance.DefaultCodeRepository``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-defaultcoderepository
    Stability:
        experimental
    """
    directInternetAccess: str
    """``AWS::SageMaker::NotebookInstance.DirectInternetAccess``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-directinternetaccess
    Stability:
        experimental
    """
    kmsKeyId: str
    """``AWS::SageMaker::NotebookInstance.KmsKeyId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-kmskeyid
    Stability:
        experimental
    """
    lifecycleConfigName: str
    """``AWS::SageMaker::NotebookInstance.LifecycleConfigName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-lifecycleconfigname
    Stability:
        experimental
    """
    notebookInstanceName: str
    """``AWS::SageMaker::NotebookInstance.NotebookInstanceName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-notebookinstancename
    Stability:
        experimental
    """
    rootAccess: str
    """``AWS::SageMaker::NotebookInstance.RootAccess``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-rootaccess
    Stability:
        experimental
    """
    securityGroupIds: typing.List[str]
    """``AWS::SageMaker::NotebookInstance.SecurityGroupIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-securitygroupids
    Stability:
        experimental
    """
    subnetId: str
    """``AWS::SageMaker::NotebookInstance.SubnetId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-subnetid
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::SageMaker::NotebookInstance.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-tags
    Stability:
        experimental
    """
    volumeSizeInGb: jsii.Number
    """``AWS::SageMaker::NotebookInstance.VolumeSizeInGB``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-volumesizeingb
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-sagemaker.CfnNotebookInstanceProps", jsii_struct_bases=[_CfnNotebookInstanceProps])
class CfnNotebookInstanceProps(_CfnNotebookInstanceProps):
    """Properties for defining a ``AWS::SageMaker::NotebookInstance``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html
    Stability:
        experimental
    """
    instanceType: str
    """``AWS::SageMaker::NotebookInstance.InstanceType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-instancetype
    Stability:
        experimental
    """

    roleArn: str
    """``AWS::SageMaker::NotebookInstance.RoleArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-notebookinstance.html#cfn-sagemaker-notebookinstance-rolearn
    Stability:
        experimental
    """

__all__ = ["CfnEndpoint", "CfnEndpointConfig", "CfnEndpointConfigProps", "CfnEndpointProps", "CfnModel", "CfnModelProps", "CfnNotebookInstance", "CfnNotebookInstanceLifecycleConfig", "CfnNotebookInstanceLifecycleConfigProps", "CfnNotebookInstanceProps", "__jsii_assembly__"]

publication.publish()
