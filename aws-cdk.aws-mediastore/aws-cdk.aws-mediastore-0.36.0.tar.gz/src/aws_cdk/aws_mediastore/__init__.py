import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-mediastore", "0.36.0", __name__, "aws-mediastore@0.36.0.jsii.tgz")
class CfnContainer(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-mediastore.CfnContainer"):
    """A CloudFormation ``AWS::MediaStore::Container``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediastore-container.html
    Stability:
        stable
    cloudformationResource:
        AWS::MediaStore::Container
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, container_name: str, access_logging_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, cors_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CorsRuleProperty"]]]]]=None, lifecycle_policy: typing.Optional[str]=None, policy: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::MediaStore::Container``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            container_name: ``AWS::MediaStore::Container.ContainerName``.
            access_logging_enabled: ``AWS::MediaStore::Container.AccessLoggingEnabled``.
            cors_policy: ``AWS::MediaStore::Container.CorsPolicy``.
            lifecycle_policy: ``AWS::MediaStore::Container.LifecyclePolicy``.
            policy: ``AWS::MediaStore::Container.Policy``.

        Stability:
            experimental
        """
        props: CfnContainerProps = {"containerName": container_name}

        if access_logging_enabled is not None:
            props["accessLoggingEnabled"] = access_logging_enabled

        if cors_policy is not None:
            props["corsPolicy"] = cors_policy

        if lifecycle_policy is not None:
            props["lifecyclePolicy"] = lifecycle_policy

        if policy is not None:
            props["policy"] = policy

        jsii.create(CfnContainer, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrEndpoint")
    def attr_endpoint(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Endpoint
        """
        return jsii.get(self, "attrEndpoint")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="containerName")
    def container_name(self) -> str:
        """``AWS::MediaStore::Container.ContainerName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediastore-container.html#cfn-mediastore-container-containername
        Stability:
            stable
        """
        return jsii.get(self, "containerName")

    @container_name.setter
    def container_name(self, value: str):
        return jsii.set(self, "containerName", value)

    @property
    @jsii.member(jsii_name="accessLoggingEnabled")
    def access_logging_enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::MediaStore::Container.AccessLoggingEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediastore-container.html#cfn-mediastore-container-accessloggingenabled
        Stability:
            stable
        """
        return jsii.get(self, "accessLoggingEnabled")

    @access_logging_enabled.setter
    def access_logging_enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "accessLoggingEnabled", value)

    @property
    @jsii.member(jsii_name="corsPolicy")
    def cors_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CorsRuleProperty"]]]]]:
        """``AWS::MediaStore::Container.CorsPolicy``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediastore-container.html#cfn-mediastore-container-corspolicy
        Stability:
            stable
        """
        return jsii.get(self, "corsPolicy")

    @cors_policy.setter
    def cors_policy(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CorsRuleProperty"]]]]]):
        return jsii.set(self, "corsPolicy", value)

    @property
    @jsii.member(jsii_name="lifecyclePolicy")
    def lifecycle_policy(self) -> typing.Optional[str]:
        """``AWS::MediaStore::Container.LifecyclePolicy``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediastore-container.html#cfn-mediastore-container-lifecyclepolicy
        Stability:
            stable
        """
        return jsii.get(self, "lifecyclePolicy")

    @lifecycle_policy.setter
    def lifecycle_policy(self, value: typing.Optional[str]):
        return jsii.set(self, "lifecyclePolicy", value)

    @property
    @jsii.member(jsii_name="policy")
    def policy(self) -> typing.Optional[str]:
        """``AWS::MediaStore::Container.Policy``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediastore-container.html#cfn-mediastore-container-policy
        Stability:
            stable
        """
        return jsii.get(self, "policy")

    @policy.setter
    def policy(self, value: typing.Optional[str]):
        return jsii.set(self, "policy", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-mediastore.CfnContainer.CorsRuleProperty", jsii_struct_bases=[])
    class CorsRuleProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-mediastore-container-corsrule.html
        Stability:
            stable
        """
        allowedHeaders: typing.List[str]
        """``CfnContainer.CorsRuleProperty.AllowedHeaders``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-mediastore-container-corsrule.html#cfn-mediastore-container-corsrule-allowedheaders
        Stability:
            stable
        """

        allowedMethods: typing.List[str]
        """``CfnContainer.CorsRuleProperty.AllowedMethods``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-mediastore-container-corsrule.html#cfn-mediastore-container-corsrule-allowedmethods
        Stability:
            stable
        """

        allowedOrigins: typing.List[str]
        """``CfnContainer.CorsRuleProperty.AllowedOrigins``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-mediastore-container-corsrule.html#cfn-mediastore-container-corsrule-allowedorigins
        Stability:
            stable
        """

        exposeHeaders: typing.List[str]
        """``CfnContainer.CorsRuleProperty.ExposeHeaders``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-mediastore-container-corsrule.html#cfn-mediastore-container-corsrule-exposeheaders
        Stability:
            stable
        """

        maxAgeSeconds: jsii.Number
        """``CfnContainer.CorsRuleProperty.MaxAgeSeconds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-mediastore-container-corsrule.html#cfn-mediastore-container-corsrule-maxageseconds
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnContainerProps(jsii.compat.TypedDict, total=False):
    accessLoggingEnabled: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::MediaStore::Container.AccessLoggingEnabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediastore-container.html#cfn-mediastore-container-accessloggingenabled
    Stability:
        stable
    """
    corsPolicy: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnContainer.CorsRuleProperty"]]]
    """``AWS::MediaStore::Container.CorsPolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediastore-container.html#cfn-mediastore-container-corspolicy
    Stability:
        stable
    """
    lifecyclePolicy: str
    """``AWS::MediaStore::Container.LifecyclePolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediastore-container.html#cfn-mediastore-container-lifecyclepolicy
    Stability:
        stable
    """
    policy: str
    """``AWS::MediaStore::Container.Policy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediastore-container.html#cfn-mediastore-container-policy
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-mediastore.CfnContainerProps", jsii_struct_bases=[_CfnContainerProps])
class CfnContainerProps(_CfnContainerProps):
    """Properties for defining a ``AWS::MediaStore::Container``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediastore-container.html
    Stability:
        stable
    """
    containerName: str
    """``AWS::MediaStore::Container.ContainerName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediastore-container.html#cfn-mediastore-container-containername
    Stability:
        stable
    """

__all__ = ["CfnContainer", "CfnContainerProps", "__jsii_assembly__"]

publication.publish()
