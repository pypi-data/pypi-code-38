import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-mediastore", "0.34.0", __name__, "aws-mediastore@0.34.0.jsii.tgz")
class CfnContainer(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-mediastore.CfnContainer"):
    """A CloudFormation ``AWS::MediaStore::Container``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediastore-container.html
    Stability:
        experimental
    cloudformationResource:
        AWS::MediaStore::Container
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, container_name: str, access_logging_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, cors_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "CorsRuleProperty"]]]]]=None, lifecycle_policy: typing.Optional[str]=None, policy: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::MediaStore::Container``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            containerName: ``AWS::MediaStore::Container.ContainerName``.
            accessLoggingEnabled: ``AWS::MediaStore::Container.AccessLoggingEnabled``.
            corsPolicy: ``AWS::MediaStore::Container.CorsPolicy``.
            lifecyclePolicy: ``AWS::MediaStore::Container.LifecyclePolicy``.
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
    def _render_properties(self, properties: typing.Any) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            properties: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "renderProperties", [properties])

    @classproperty
    @jsii.member(jsii_name="resourceTypeName")
    def RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            experimental
        """
        return jsii.sget(cls, "resourceTypeName")

    @property
    @jsii.member(jsii_name="containerEndpoint")
    def container_endpoint(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Endpoint
        """
        return jsii.get(self, "containerEndpoint")

    @property
    @jsii.member(jsii_name="containerName")
    def container_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "containerName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnContainerProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-mediastore.CfnContainer.CorsRuleProperty", jsii_struct_bases=[])
    class CorsRuleProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-mediastore-container-corsrule.html
        Stability:
            experimental
        """
        allowedHeaders: typing.List[str]
        """``CfnContainer.CorsRuleProperty.AllowedHeaders``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-mediastore-container-corsrule.html#cfn-mediastore-container-corsrule-allowedheaders
        Stability:
            experimental
        """

        allowedMethods: typing.List[str]
        """``CfnContainer.CorsRuleProperty.AllowedMethods``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-mediastore-container-corsrule.html#cfn-mediastore-container-corsrule-allowedmethods
        Stability:
            experimental
        """

        allowedOrigins: typing.List[str]
        """``CfnContainer.CorsRuleProperty.AllowedOrigins``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-mediastore-container-corsrule.html#cfn-mediastore-container-corsrule-allowedorigins
        Stability:
            experimental
        """

        exposeHeaders: typing.List[str]
        """``CfnContainer.CorsRuleProperty.ExposeHeaders``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-mediastore-container-corsrule.html#cfn-mediastore-container-corsrule-exposeheaders
        Stability:
            experimental
        """

        maxAgeSeconds: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnContainer.CorsRuleProperty.MaxAgeSeconds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-mediastore-container-corsrule.html#cfn-mediastore-container-corsrule-maxageseconds
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnContainerProps(jsii.compat.TypedDict, total=False):
    accessLoggingEnabled: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::MediaStore::Container.AccessLoggingEnabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediastore-container.html#cfn-mediastore-container-accessloggingenabled
    Stability:
        experimental
    """
    corsPolicy: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnContainer.CorsRuleProperty"]]]
    """``AWS::MediaStore::Container.CorsPolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediastore-container.html#cfn-mediastore-container-corspolicy
    Stability:
        experimental
    """
    lifecyclePolicy: str
    """``AWS::MediaStore::Container.LifecyclePolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediastore-container.html#cfn-mediastore-container-lifecyclepolicy
    Stability:
        experimental
    """
    policy: str
    """``AWS::MediaStore::Container.Policy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediastore-container.html#cfn-mediastore-container-policy
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-mediastore.CfnContainerProps", jsii_struct_bases=[_CfnContainerProps])
class CfnContainerProps(_CfnContainerProps):
    """Properties for defining a ``AWS::MediaStore::Container``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediastore-container.html
    Stability:
        experimental
    """
    containerName: str
    """``AWS::MediaStore::Container.ContainerName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediastore-container.html#cfn-mediastore-container-containername
    Stability:
        experimental
    """

__all__ = ["CfnContainer", "CfnContainerProps", "__jsii_assembly__"]

publication.publish()
