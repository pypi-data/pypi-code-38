import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-pinpoint", "0.36.0", __name__, "aws-pinpoint@0.36.0.jsii.tgz")
class CfnADMChannel(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpoint.CfnADMChannel"):
    """A CloudFormation ``AWS::Pinpoint::ADMChannel``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-admchannel.html
    Stability:
        stable
    cloudformationResource:
        AWS::Pinpoint::ADMChannel
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application_id: str, client_id: str, client_secret: str, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None) -> None:
        """Create a new ``AWS::Pinpoint::ADMChannel``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            application_id: ``AWS::Pinpoint::ADMChannel.ApplicationId``.
            client_id: ``AWS::Pinpoint::ADMChannel.ClientId``.
            client_secret: ``AWS::Pinpoint::ADMChannel.ClientSecret``.
            enabled: ``AWS::Pinpoint::ADMChannel.Enabled``.

        Stability:
            experimental
        """
        props: CfnADMChannelProps = {"applicationId": application_id, "clientId": client_id, "clientSecret": client_secret}

        if enabled is not None:
            props["enabled"] = enabled

        jsii.create(CfnADMChannel, self, [scope, id, props])

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
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> str:
        """``AWS::Pinpoint::ADMChannel.ApplicationId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-admchannel.html#cfn-pinpoint-admchannel-applicationid
        Stability:
            stable
        """
        return jsii.get(self, "applicationId")

    @application_id.setter
    def application_id(self, value: str):
        return jsii.set(self, "applicationId", value)

    @property
    @jsii.member(jsii_name="clientId")
    def client_id(self) -> str:
        """``AWS::Pinpoint::ADMChannel.ClientId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-admchannel.html#cfn-pinpoint-admchannel-clientid
        Stability:
            stable
        """
        return jsii.get(self, "clientId")

    @client_id.setter
    def client_id(self, value: str):
        return jsii.set(self, "clientId", value)

    @property
    @jsii.member(jsii_name="clientSecret")
    def client_secret(self) -> str:
        """``AWS::Pinpoint::ADMChannel.ClientSecret``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-admchannel.html#cfn-pinpoint-admchannel-clientsecret
        Stability:
            stable
        """
        return jsii.get(self, "clientSecret")

    @client_secret.setter
    def client_secret(self, value: str):
        return jsii.set(self, "clientSecret", value)

    @property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::ADMChannel.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-admchannel.html#cfn-pinpoint-admchannel-enabled
        Stability:
            stable
        """
        return jsii.get(self, "enabled")

    @enabled.setter
    def enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "enabled", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnADMChannelProps(jsii.compat.TypedDict, total=False):
    enabled: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::Pinpoint::ADMChannel.Enabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-admchannel.html#cfn-pinpoint-admchannel-enabled
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnADMChannelProps", jsii_struct_bases=[_CfnADMChannelProps])
class CfnADMChannelProps(_CfnADMChannelProps):
    """Properties for defining a ``AWS::Pinpoint::ADMChannel``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-admchannel.html
    Stability:
        stable
    """
    applicationId: str
    """``AWS::Pinpoint::ADMChannel.ApplicationId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-admchannel.html#cfn-pinpoint-admchannel-applicationid
    Stability:
        stable
    """

    clientId: str
    """``AWS::Pinpoint::ADMChannel.ClientId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-admchannel.html#cfn-pinpoint-admchannel-clientid
    Stability:
        stable
    """

    clientSecret: str
    """``AWS::Pinpoint::ADMChannel.ClientSecret``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-admchannel.html#cfn-pinpoint-admchannel-clientsecret
    Stability:
        stable
    """

class CfnAPNSChannel(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpoint.CfnAPNSChannel"):
    """A CloudFormation ``AWS::Pinpoint::APNSChannel``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html
    Stability:
        stable
    cloudformationResource:
        AWS::Pinpoint::APNSChannel
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application_id: str, bundle_id: typing.Optional[str]=None, certificate: typing.Optional[str]=None, default_authentication_method: typing.Optional[str]=None, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, private_key: typing.Optional[str]=None, team_id: typing.Optional[str]=None, token_key: typing.Optional[str]=None, token_key_id: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Pinpoint::APNSChannel``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            application_id: ``AWS::Pinpoint::APNSChannel.ApplicationId``.
            bundle_id: ``AWS::Pinpoint::APNSChannel.BundleId``.
            certificate: ``AWS::Pinpoint::APNSChannel.Certificate``.
            default_authentication_method: ``AWS::Pinpoint::APNSChannel.DefaultAuthenticationMethod``.
            enabled: ``AWS::Pinpoint::APNSChannel.Enabled``.
            private_key: ``AWS::Pinpoint::APNSChannel.PrivateKey``.
            team_id: ``AWS::Pinpoint::APNSChannel.TeamId``.
            token_key: ``AWS::Pinpoint::APNSChannel.TokenKey``.
            token_key_id: ``AWS::Pinpoint::APNSChannel.TokenKeyId``.

        Stability:
            experimental
        """
        props: CfnAPNSChannelProps = {"applicationId": application_id}

        if bundle_id is not None:
            props["bundleId"] = bundle_id

        if certificate is not None:
            props["certificate"] = certificate

        if default_authentication_method is not None:
            props["defaultAuthenticationMethod"] = default_authentication_method

        if enabled is not None:
            props["enabled"] = enabled

        if private_key is not None:
            props["privateKey"] = private_key

        if team_id is not None:
            props["teamId"] = team_id

        if token_key is not None:
            props["tokenKey"] = token_key

        if token_key_id is not None:
            props["tokenKeyId"] = token_key_id

        jsii.create(CfnAPNSChannel, self, [scope, id, props])

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
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> str:
        """``AWS::Pinpoint::APNSChannel.ApplicationId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html#cfn-pinpoint-apnschannel-applicationid
        Stability:
            stable
        """
        return jsii.get(self, "applicationId")

    @application_id.setter
    def application_id(self, value: str):
        return jsii.set(self, "applicationId", value)

    @property
    @jsii.member(jsii_name="bundleId")
    def bundle_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSChannel.BundleId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html#cfn-pinpoint-apnschannel-bundleid
        Stability:
            stable
        """
        return jsii.get(self, "bundleId")

    @bundle_id.setter
    def bundle_id(self, value: typing.Optional[str]):
        return jsii.set(self, "bundleId", value)

    @property
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSChannel.Certificate``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html#cfn-pinpoint-apnschannel-certificate
        Stability:
            stable
        """
        return jsii.get(self, "certificate")

    @certificate.setter
    def certificate(self, value: typing.Optional[str]):
        return jsii.set(self, "certificate", value)

    @property
    @jsii.member(jsii_name="defaultAuthenticationMethod")
    def default_authentication_method(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSChannel.DefaultAuthenticationMethod``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html#cfn-pinpoint-apnschannel-defaultauthenticationmethod
        Stability:
            stable
        """
        return jsii.get(self, "defaultAuthenticationMethod")

    @default_authentication_method.setter
    def default_authentication_method(self, value: typing.Optional[str]):
        return jsii.set(self, "defaultAuthenticationMethod", value)

    @property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::APNSChannel.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html#cfn-pinpoint-apnschannel-enabled
        Stability:
            stable
        """
        return jsii.get(self, "enabled")

    @enabled.setter
    def enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "enabled", value)

    @property
    @jsii.member(jsii_name="privateKey")
    def private_key(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSChannel.PrivateKey``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html#cfn-pinpoint-apnschannel-privatekey
        Stability:
            stable
        """
        return jsii.get(self, "privateKey")

    @private_key.setter
    def private_key(self, value: typing.Optional[str]):
        return jsii.set(self, "privateKey", value)

    @property
    @jsii.member(jsii_name="teamId")
    def team_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSChannel.TeamId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html#cfn-pinpoint-apnschannel-teamid
        Stability:
            stable
        """
        return jsii.get(self, "teamId")

    @team_id.setter
    def team_id(self, value: typing.Optional[str]):
        return jsii.set(self, "teamId", value)

    @property
    @jsii.member(jsii_name="tokenKey")
    def token_key(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSChannel.TokenKey``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html#cfn-pinpoint-apnschannel-tokenkey
        Stability:
            stable
        """
        return jsii.get(self, "tokenKey")

    @token_key.setter
    def token_key(self, value: typing.Optional[str]):
        return jsii.set(self, "tokenKey", value)

    @property
    @jsii.member(jsii_name="tokenKeyId")
    def token_key_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSChannel.TokenKeyId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html#cfn-pinpoint-apnschannel-tokenkeyid
        Stability:
            stable
        """
        return jsii.get(self, "tokenKeyId")

    @token_key_id.setter
    def token_key_id(self, value: typing.Optional[str]):
        return jsii.set(self, "tokenKeyId", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnAPNSChannelProps(jsii.compat.TypedDict, total=False):
    bundleId: str
    """``AWS::Pinpoint::APNSChannel.BundleId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html#cfn-pinpoint-apnschannel-bundleid
    Stability:
        stable
    """
    certificate: str
    """``AWS::Pinpoint::APNSChannel.Certificate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html#cfn-pinpoint-apnschannel-certificate
    Stability:
        stable
    """
    defaultAuthenticationMethod: str
    """``AWS::Pinpoint::APNSChannel.DefaultAuthenticationMethod``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html#cfn-pinpoint-apnschannel-defaultauthenticationmethod
    Stability:
        stable
    """
    enabled: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::Pinpoint::APNSChannel.Enabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html#cfn-pinpoint-apnschannel-enabled
    Stability:
        stable
    """
    privateKey: str
    """``AWS::Pinpoint::APNSChannel.PrivateKey``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html#cfn-pinpoint-apnschannel-privatekey
    Stability:
        stable
    """
    teamId: str
    """``AWS::Pinpoint::APNSChannel.TeamId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html#cfn-pinpoint-apnschannel-teamid
    Stability:
        stable
    """
    tokenKey: str
    """``AWS::Pinpoint::APNSChannel.TokenKey``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html#cfn-pinpoint-apnschannel-tokenkey
    Stability:
        stable
    """
    tokenKeyId: str
    """``AWS::Pinpoint::APNSChannel.TokenKeyId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html#cfn-pinpoint-apnschannel-tokenkeyid
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnAPNSChannelProps", jsii_struct_bases=[_CfnAPNSChannelProps])
class CfnAPNSChannelProps(_CfnAPNSChannelProps):
    """Properties for defining a ``AWS::Pinpoint::APNSChannel``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html
    Stability:
        stable
    """
    applicationId: str
    """``AWS::Pinpoint::APNSChannel.ApplicationId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html#cfn-pinpoint-apnschannel-applicationid
    Stability:
        stable
    """

class CfnAPNSSandboxChannel(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpoint.CfnAPNSSandboxChannel"):
    """A CloudFormation ``AWS::Pinpoint::APNSSandboxChannel``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html
    Stability:
        stable
    cloudformationResource:
        AWS::Pinpoint::APNSSandboxChannel
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application_id: str, bundle_id: typing.Optional[str]=None, certificate: typing.Optional[str]=None, default_authentication_method: typing.Optional[str]=None, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, private_key: typing.Optional[str]=None, team_id: typing.Optional[str]=None, token_key: typing.Optional[str]=None, token_key_id: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Pinpoint::APNSSandboxChannel``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            application_id: ``AWS::Pinpoint::APNSSandboxChannel.ApplicationId``.
            bundle_id: ``AWS::Pinpoint::APNSSandboxChannel.BundleId``.
            certificate: ``AWS::Pinpoint::APNSSandboxChannel.Certificate``.
            default_authentication_method: ``AWS::Pinpoint::APNSSandboxChannel.DefaultAuthenticationMethod``.
            enabled: ``AWS::Pinpoint::APNSSandboxChannel.Enabled``.
            private_key: ``AWS::Pinpoint::APNSSandboxChannel.PrivateKey``.
            team_id: ``AWS::Pinpoint::APNSSandboxChannel.TeamId``.
            token_key: ``AWS::Pinpoint::APNSSandboxChannel.TokenKey``.
            token_key_id: ``AWS::Pinpoint::APNSSandboxChannel.TokenKeyId``.

        Stability:
            experimental
        """
        props: CfnAPNSSandboxChannelProps = {"applicationId": application_id}

        if bundle_id is not None:
            props["bundleId"] = bundle_id

        if certificate is not None:
            props["certificate"] = certificate

        if default_authentication_method is not None:
            props["defaultAuthenticationMethod"] = default_authentication_method

        if enabled is not None:
            props["enabled"] = enabled

        if private_key is not None:
            props["privateKey"] = private_key

        if team_id is not None:
            props["teamId"] = team_id

        if token_key is not None:
            props["tokenKey"] = token_key

        if token_key_id is not None:
            props["tokenKeyId"] = token_key_id

        jsii.create(CfnAPNSSandboxChannel, self, [scope, id, props])

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
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> str:
        """``AWS::Pinpoint::APNSSandboxChannel.ApplicationId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html#cfn-pinpoint-apnssandboxchannel-applicationid
        Stability:
            stable
        """
        return jsii.get(self, "applicationId")

    @application_id.setter
    def application_id(self, value: str):
        return jsii.set(self, "applicationId", value)

    @property
    @jsii.member(jsii_name="bundleId")
    def bundle_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSSandboxChannel.BundleId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html#cfn-pinpoint-apnssandboxchannel-bundleid
        Stability:
            stable
        """
        return jsii.get(self, "bundleId")

    @bundle_id.setter
    def bundle_id(self, value: typing.Optional[str]):
        return jsii.set(self, "bundleId", value)

    @property
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSSandboxChannel.Certificate``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html#cfn-pinpoint-apnssandboxchannel-certificate
        Stability:
            stable
        """
        return jsii.get(self, "certificate")

    @certificate.setter
    def certificate(self, value: typing.Optional[str]):
        return jsii.set(self, "certificate", value)

    @property
    @jsii.member(jsii_name="defaultAuthenticationMethod")
    def default_authentication_method(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSSandboxChannel.DefaultAuthenticationMethod``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html#cfn-pinpoint-apnssandboxchannel-defaultauthenticationmethod
        Stability:
            stable
        """
        return jsii.get(self, "defaultAuthenticationMethod")

    @default_authentication_method.setter
    def default_authentication_method(self, value: typing.Optional[str]):
        return jsii.set(self, "defaultAuthenticationMethod", value)

    @property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::APNSSandboxChannel.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html#cfn-pinpoint-apnssandboxchannel-enabled
        Stability:
            stable
        """
        return jsii.get(self, "enabled")

    @enabled.setter
    def enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "enabled", value)

    @property
    @jsii.member(jsii_name="privateKey")
    def private_key(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSSandboxChannel.PrivateKey``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html#cfn-pinpoint-apnssandboxchannel-privatekey
        Stability:
            stable
        """
        return jsii.get(self, "privateKey")

    @private_key.setter
    def private_key(self, value: typing.Optional[str]):
        return jsii.set(self, "privateKey", value)

    @property
    @jsii.member(jsii_name="teamId")
    def team_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSSandboxChannel.TeamId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html#cfn-pinpoint-apnssandboxchannel-teamid
        Stability:
            stable
        """
        return jsii.get(self, "teamId")

    @team_id.setter
    def team_id(self, value: typing.Optional[str]):
        return jsii.set(self, "teamId", value)

    @property
    @jsii.member(jsii_name="tokenKey")
    def token_key(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSSandboxChannel.TokenKey``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html#cfn-pinpoint-apnssandboxchannel-tokenkey
        Stability:
            stable
        """
        return jsii.get(self, "tokenKey")

    @token_key.setter
    def token_key(self, value: typing.Optional[str]):
        return jsii.set(self, "tokenKey", value)

    @property
    @jsii.member(jsii_name="tokenKeyId")
    def token_key_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSSandboxChannel.TokenKeyId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html#cfn-pinpoint-apnssandboxchannel-tokenkeyid
        Stability:
            stable
        """
        return jsii.get(self, "tokenKeyId")

    @token_key_id.setter
    def token_key_id(self, value: typing.Optional[str]):
        return jsii.set(self, "tokenKeyId", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnAPNSSandboxChannelProps(jsii.compat.TypedDict, total=False):
    bundleId: str
    """``AWS::Pinpoint::APNSSandboxChannel.BundleId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html#cfn-pinpoint-apnssandboxchannel-bundleid
    Stability:
        stable
    """
    certificate: str
    """``AWS::Pinpoint::APNSSandboxChannel.Certificate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html#cfn-pinpoint-apnssandboxchannel-certificate
    Stability:
        stable
    """
    defaultAuthenticationMethod: str
    """``AWS::Pinpoint::APNSSandboxChannel.DefaultAuthenticationMethod``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html#cfn-pinpoint-apnssandboxchannel-defaultauthenticationmethod
    Stability:
        stable
    """
    enabled: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::Pinpoint::APNSSandboxChannel.Enabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html#cfn-pinpoint-apnssandboxchannel-enabled
    Stability:
        stable
    """
    privateKey: str
    """``AWS::Pinpoint::APNSSandboxChannel.PrivateKey``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html#cfn-pinpoint-apnssandboxchannel-privatekey
    Stability:
        stable
    """
    teamId: str
    """``AWS::Pinpoint::APNSSandboxChannel.TeamId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html#cfn-pinpoint-apnssandboxchannel-teamid
    Stability:
        stable
    """
    tokenKey: str
    """``AWS::Pinpoint::APNSSandboxChannel.TokenKey``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html#cfn-pinpoint-apnssandboxchannel-tokenkey
    Stability:
        stable
    """
    tokenKeyId: str
    """``AWS::Pinpoint::APNSSandboxChannel.TokenKeyId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html#cfn-pinpoint-apnssandboxchannel-tokenkeyid
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnAPNSSandboxChannelProps", jsii_struct_bases=[_CfnAPNSSandboxChannelProps])
class CfnAPNSSandboxChannelProps(_CfnAPNSSandboxChannelProps):
    """Properties for defining a ``AWS::Pinpoint::APNSSandboxChannel``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html
    Stability:
        stable
    """
    applicationId: str
    """``AWS::Pinpoint::APNSSandboxChannel.ApplicationId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html#cfn-pinpoint-apnssandboxchannel-applicationid
    Stability:
        stable
    """

class CfnAPNSVoipChannel(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpoint.CfnAPNSVoipChannel"):
    """A CloudFormation ``AWS::Pinpoint::APNSVoipChannel``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html
    Stability:
        stable
    cloudformationResource:
        AWS::Pinpoint::APNSVoipChannel
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application_id: str, bundle_id: typing.Optional[str]=None, certificate: typing.Optional[str]=None, default_authentication_method: typing.Optional[str]=None, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, private_key: typing.Optional[str]=None, team_id: typing.Optional[str]=None, token_key: typing.Optional[str]=None, token_key_id: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Pinpoint::APNSVoipChannel``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            application_id: ``AWS::Pinpoint::APNSVoipChannel.ApplicationId``.
            bundle_id: ``AWS::Pinpoint::APNSVoipChannel.BundleId``.
            certificate: ``AWS::Pinpoint::APNSVoipChannel.Certificate``.
            default_authentication_method: ``AWS::Pinpoint::APNSVoipChannel.DefaultAuthenticationMethod``.
            enabled: ``AWS::Pinpoint::APNSVoipChannel.Enabled``.
            private_key: ``AWS::Pinpoint::APNSVoipChannel.PrivateKey``.
            team_id: ``AWS::Pinpoint::APNSVoipChannel.TeamId``.
            token_key: ``AWS::Pinpoint::APNSVoipChannel.TokenKey``.
            token_key_id: ``AWS::Pinpoint::APNSVoipChannel.TokenKeyId``.

        Stability:
            experimental
        """
        props: CfnAPNSVoipChannelProps = {"applicationId": application_id}

        if bundle_id is not None:
            props["bundleId"] = bundle_id

        if certificate is not None:
            props["certificate"] = certificate

        if default_authentication_method is not None:
            props["defaultAuthenticationMethod"] = default_authentication_method

        if enabled is not None:
            props["enabled"] = enabled

        if private_key is not None:
            props["privateKey"] = private_key

        if team_id is not None:
            props["teamId"] = team_id

        if token_key is not None:
            props["tokenKey"] = token_key

        if token_key_id is not None:
            props["tokenKeyId"] = token_key_id

        jsii.create(CfnAPNSVoipChannel, self, [scope, id, props])

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
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> str:
        """``AWS::Pinpoint::APNSVoipChannel.ApplicationId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html#cfn-pinpoint-apnsvoipchannel-applicationid
        Stability:
            stable
        """
        return jsii.get(self, "applicationId")

    @application_id.setter
    def application_id(self, value: str):
        return jsii.set(self, "applicationId", value)

    @property
    @jsii.member(jsii_name="bundleId")
    def bundle_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipChannel.BundleId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html#cfn-pinpoint-apnsvoipchannel-bundleid
        Stability:
            stable
        """
        return jsii.get(self, "bundleId")

    @bundle_id.setter
    def bundle_id(self, value: typing.Optional[str]):
        return jsii.set(self, "bundleId", value)

    @property
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipChannel.Certificate``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html#cfn-pinpoint-apnsvoipchannel-certificate
        Stability:
            stable
        """
        return jsii.get(self, "certificate")

    @certificate.setter
    def certificate(self, value: typing.Optional[str]):
        return jsii.set(self, "certificate", value)

    @property
    @jsii.member(jsii_name="defaultAuthenticationMethod")
    def default_authentication_method(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipChannel.DefaultAuthenticationMethod``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html#cfn-pinpoint-apnsvoipchannel-defaultauthenticationmethod
        Stability:
            stable
        """
        return jsii.get(self, "defaultAuthenticationMethod")

    @default_authentication_method.setter
    def default_authentication_method(self, value: typing.Optional[str]):
        return jsii.set(self, "defaultAuthenticationMethod", value)

    @property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::APNSVoipChannel.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html#cfn-pinpoint-apnsvoipchannel-enabled
        Stability:
            stable
        """
        return jsii.get(self, "enabled")

    @enabled.setter
    def enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "enabled", value)

    @property
    @jsii.member(jsii_name="privateKey")
    def private_key(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipChannel.PrivateKey``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html#cfn-pinpoint-apnsvoipchannel-privatekey
        Stability:
            stable
        """
        return jsii.get(self, "privateKey")

    @private_key.setter
    def private_key(self, value: typing.Optional[str]):
        return jsii.set(self, "privateKey", value)

    @property
    @jsii.member(jsii_name="teamId")
    def team_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipChannel.TeamId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html#cfn-pinpoint-apnsvoipchannel-teamid
        Stability:
            stable
        """
        return jsii.get(self, "teamId")

    @team_id.setter
    def team_id(self, value: typing.Optional[str]):
        return jsii.set(self, "teamId", value)

    @property
    @jsii.member(jsii_name="tokenKey")
    def token_key(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipChannel.TokenKey``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html#cfn-pinpoint-apnsvoipchannel-tokenkey
        Stability:
            stable
        """
        return jsii.get(self, "tokenKey")

    @token_key.setter
    def token_key(self, value: typing.Optional[str]):
        return jsii.set(self, "tokenKey", value)

    @property
    @jsii.member(jsii_name="tokenKeyId")
    def token_key_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipChannel.TokenKeyId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html#cfn-pinpoint-apnsvoipchannel-tokenkeyid
        Stability:
            stable
        """
        return jsii.get(self, "tokenKeyId")

    @token_key_id.setter
    def token_key_id(self, value: typing.Optional[str]):
        return jsii.set(self, "tokenKeyId", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnAPNSVoipChannelProps(jsii.compat.TypedDict, total=False):
    bundleId: str
    """``AWS::Pinpoint::APNSVoipChannel.BundleId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html#cfn-pinpoint-apnsvoipchannel-bundleid
    Stability:
        stable
    """
    certificate: str
    """``AWS::Pinpoint::APNSVoipChannel.Certificate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html#cfn-pinpoint-apnsvoipchannel-certificate
    Stability:
        stable
    """
    defaultAuthenticationMethod: str
    """``AWS::Pinpoint::APNSVoipChannel.DefaultAuthenticationMethod``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html#cfn-pinpoint-apnsvoipchannel-defaultauthenticationmethod
    Stability:
        stable
    """
    enabled: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::Pinpoint::APNSVoipChannel.Enabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html#cfn-pinpoint-apnsvoipchannel-enabled
    Stability:
        stable
    """
    privateKey: str
    """``AWS::Pinpoint::APNSVoipChannel.PrivateKey``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html#cfn-pinpoint-apnsvoipchannel-privatekey
    Stability:
        stable
    """
    teamId: str
    """``AWS::Pinpoint::APNSVoipChannel.TeamId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html#cfn-pinpoint-apnsvoipchannel-teamid
    Stability:
        stable
    """
    tokenKey: str
    """``AWS::Pinpoint::APNSVoipChannel.TokenKey``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html#cfn-pinpoint-apnsvoipchannel-tokenkey
    Stability:
        stable
    """
    tokenKeyId: str
    """``AWS::Pinpoint::APNSVoipChannel.TokenKeyId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html#cfn-pinpoint-apnsvoipchannel-tokenkeyid
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnAPNSVoipChannelProps", jsii_struct_bases=[_CfnAPNSVoipChannelProps])
class CfnAPNSVoipChannelProps(_CfnAPNSVoipChannelProps):
    """Properties for defining a ``AWS::Pinpoint::APNSVoipChannel``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html
    Stability:
        stable
    """
    applicationId: str
    """``AWS::Pinpoint::APNSVoipChannel.ApplicationId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html#cfn-pinpoint-apnsvoipchannel-applicationid
    Stability:
        stable
    """

class CfnAPNSVoipSandboxChannel(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpoint.CfnAPNSVoipSandboxChannel"):
    """A CloudFormation ``AWS::Pinpoint::APNSVoipSandboxChannel``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html
    Stability:
        stable
    cloudformationResource:
        AWS::Pinpoint::APNSVoipSandboxChannel
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application_id: str, bundle_id: typing.Optional[str]=None, certificate: typing.Optional[str]=None, default_authentication_method: typing.Optional[str]=None, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, private_key: typing.Optional[str]=None, team_id: typing.Optional[str]=None, token_key: typing.Optional[str]=None, token_key_id: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Pinpoint::APNSVoipSandboxChannel``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            application_id: ``AWS::Pinpoint::APNSVoipSandboxChannel.ApplicationId``.
            bundle_id: ``AWS::Pinpoint::APNSVoipSandboxChannel.BundleId``.
            certificate: ``AWS::Pinpoint::APNSVoipSandboxChannel.Certificate``.
            default_authentication_method: ``AWS::Pinpoint::APNSVoipSandboxChannel.DefaultAuthenticationMethod``.
            enabled: ``AWS::Pinpoint::APNSVoipSandboxChannel.Enabled``.
            private_key: ``AWS::Pinpoint::APNSVoipSandboxChannel.PrivateKey``.
            team_id: ``AWS::Pinpoint::APNSVoipSandboxChannel.TeamId``.
            token_key: ``AWS::Pinpoint::APNSVoipSandboxChannel.TokenKey``.
            token_key_id: ``AWS::Pinpoint::APNSVoipSandboxChannel.TokenKeyId``.

        Stability:
            experimental
        """
        props: CfnAPNSVoipSandboxChannelProps = {"applicationId": application_id}

        if bundle_id is not None:
            props["bundleId"] = bundle_id

        if certificate is not None:
            props["certificate"] = certificate

        if default_authentication_method is not None:
            props["defaultAuthenticationMethod"] = default_authentication_method

        if enabled is not None:
            props["enabled"] = enabled

        if private_key is not None:
            props["privateKey"] = private_key

        if team_id is not None:
            props["teamId"] = team_id

        if token_key is not None:
            props["tokenKey"] = token_key

        if token_key_id is not None:
            props["tokenKeyId"] = token_key_id

        jsii.create(CfnAPNSVoipSandboxChannel, self, [scope, id, props])

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
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> str:
        """``AWS::Pinpoint::APNSVoipSandboxChannel.ApplicationId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html#cfn-pinpoint-apnsvoipsandboxchannel-applicationid
        Stability:
            stable
        """
        return jsii.get(self, "applicationId")

    @application_id.setter
    def application_id(self, value: str):
        return jsii.set(self, "applicationId", value)

    @property
    @jsii.member(jsii_name="bundleId")
    def bundle_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipSandboxChannel.BundleId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html#cfn-pinpoint-apnsvoipsandboxchannel-bundleid
        Stability:
            stable
        """
        return jsii.get(self, "bundleId")

    @bundle_id.setter
    def bundle_id(self, value: typing.Optional[str]):
        return jsii.set(self, "bundleId", value)

    @property
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipSandboxChannel.Certificate``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html#cfn-pinpoint-apnsvoipsandboxchannel-certificate
        Stability:
            stable
        """
        return jsii.get(self, "certificate")

    @certificate.setter
    def certificate(self, value: typing.Optional[str]):
        return jsii.set(self, "certificate", value)

    @property
    @jsii.member(jsii_name="defaultAuthenticationMethod")
    def default_authentication_method(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipSandboxChannel.DefaultAuthenticationMethod``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html#cfn-pinpoint-apnsvoipsandboxchannel-defaultauthenticationmethod
        Stability:
            stable
        """
        return jsii.get(self, "defaultAuthenticationMethod")

    @default_authentication_method.setter
    def default_authentication_method(self, value: typing.Optional[str]):
        return jsii.set(self, "defaultAuthenticationMethod", value)

    @property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::APNSVoipSandboxChannel.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html#cfn-pinpoint-apnsvoipsandboxchannel-enabled
        Stability:
            stable
        """
        return jsii.get(self, "enabled")

    @enabled.setter
    def enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "enabled", value)

    @property
    @jsii.member(jsii_name="privateKey")
    def private_key(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipSandboxChannel.PrivateKey``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html#cfn-pinpoint-apnsvoipsandboxchannel-privatekey
        Stability:
            stable
        """
        return jsii.get(self, "privateKey")

    @private_key.setter
    def private_key(self, value: typing.Optional[str]):
        return jsii.set(self, "privateKey", value)

    @property
    @jsii.member(jsii_name="teamId")
    def team_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipSandboxChannel.TeamId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html#cfn-pinpoint-apnsvoipsandboxchannel-teamid
        Stability:
            stable
        """
        return jsii.get(self, "teamId")

    @team_id.setter
    def team_id(self, value: typing.Optional[str]):
        return jsii.set(self, "teamId", value)

    @property
    @jsii.member(jsii_name="tokenKey")
    def token_key(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipSandboxChannel.TokenKey``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html#cfn-pinpoint-apnsvoipsandboxchannel-tokenkey
        Stability:
            stable
        """
        return jsii.get(self, "tokenKey")

    @token_key.setter
    def token_key(self, value: typing.Optional[str]):
        return jsii.set(self, "tokenKey", value)

    @property
    @jsii.member(jsii_name="tokenKeyId")
    def token_key_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipSandboxChannel.TokenKeyId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html#cfn-pinpoint-apnsvoipsandboxchannel-tokenkeyid
        Stability:
            stable
        """
        return jsii.get(self, "tokenKeyId")

    @token_key_id.setter
    def token_key_id(self, value: typing.Optional[str]):
        return jsii.set(self, "tokenKeyId", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnAPNSVoipSandboxChannelProps(jsii.compat.TypedDict, total=False):
    bundleId: str
    """``AWS::Pinpoint::APNSVoipSandboxChannel.BundleId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html#cfn-pinpoint-apnsvoipsandboxchannel-bundleid
    Stability:
        stable
    """
    certificate: str
    """``AWS::Pinpoint::APNSVoipSandboxChannel.Certificate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html#cfn-pinpoint-apnsvoipsandboxchannel-certificate
    Stability:
        stable
    """
    defaultAuthenticationMethod: str
    """``AWS::Pinpoint::APNSVoipSandboxChannel.DefaultAuthenticationMethod``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html#cfn-pinpoint-apnsvoipsandboxchannel-defaultauthenticationmethod
    Stability:
        stable
    """
    enabled: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::Pinpoint::APNSVoipSandboxChannel.Enabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html#cfn-pinpoint-apnsvoipsandboxchannel-enabled
    Stability:
        stable
    """
    privateKey: str
    """``AWS::Pinpoint::APNSVoipSandboxChannel.PrivateKey``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html#cfn-pinpoint-apnsvoipsandboxchannel-privatekey
    Stability:
        stable
    """
    teamId: str
    """``AWS::Pinpoint::APNSVoipSandboxChannel.TeamId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html#cfn-pinpoint-apnsvoipsandboxchannel-teamid
    Stability:
        stable
    """
    tokenKey: str
    """``AWS::Pinpoint::APNSVoipSandboxChannel.TokenKey``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html#cfn-pinpoint-apnsvoipsandboxchannel-tokenkey
    Stability:
        stable
    """
    tokenKeyId: str
    """``AWS::Pinpoint::APNSVoipSandboxChannel.TokenKeyId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html#cfn-pinpoint-apnsvoipsandboxchannel-tokenkeyid
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnAPNSVoipSandboxChannelProps", jsii_struct_bases=[_CfnAPNSVoipSandboxChannelProps])
class CfnAPNSVoipSandboxChannelProps(_CfnAPNSVoipSandboxChannelProps):
    """Properties for defining a ``AWS::Pinpoint::APNSVoipSandboxChannel``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html
    Stability:
        stable
    """
    applicationId: str
    """``AWS::Pinpoint::APNSVoipSandboxChannel.ApplicationId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html#cfn-pinpoint-apnsvoipsandboxchannel-applicationid
    Stability:
        stable
    """

class CfnApp(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpoint.CfnApp"):
    """A CloudFormation ``AWS::Pinpoint::App``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-app.html
    Stability:
        stable
    cloudformationResource:
        AWS::Pinpoint::App
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str) -> None:
        """Create a new ``AWS::Pinpoint::App``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::Pinpoint::App.Name``.

        Stability:
            experimental
        """
        props: CfnAppProps = {"name": name}

        jsii.create(CfnApp, self, [scope, id, props])

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
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::Pinpoint::App.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-app.html#cfn-pinpoint-app-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnAppProps", jsii_struct_bases=[])
class CfnAppProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::Pinpoint::App``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-app.html
    Stability:
        stable
    """
    name: str
    """``AWS::Pinpoint::App.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-app.html#cfn-pinpoint-app-name
    Stability:
        stable
    """

class CfnApplicationSettings(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpoint.CfnApplicationSettings"):
    """A CloudFormation ``AWS::Pinpoint::ApplicationSettings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-applicationsettings.html
    Stability:
        stable
    cloudformationResource:
        AWS::Pinpoint::ApplicationSettings
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application_id: str, campaign_hook: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CampaignHookProperty"]]]=None, cloud_watch_metrics_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, limits: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LimitsProperty"]]]=None, quiet_time: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["QuietTimeProperty"]]]=None) -> None:
        """Create a new ``AWS::Pinpoint::ApplicationSettings``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            application_id: ``AWS::Pinpoint::ApplicationSettings.ApplicationId``.
            campaign_hook: ``AWS::Pinpoint::ApplicationSettings.CampaignHook``.
            cloud_watch_metrics_enabled: ``AWS::Pinpoint::ApplicationSettings.CloudWatchMetricsEnabled``.
            limits: ``AWS::Pinpoint::ApplicationSettings.Limits``.
            quiet_time: ``AWS::Pinpoint::ApplicationSettings.QuietTime``.

        Stability:
            experimental
        """
        props: CfnApplicationSettingsProps = {"applicationId": application_id}

        if campaign_hook is not None:
            props["campaignHook"] = campaign_hook

        if cloud_watch_metrics_enabled is not None:
            props["cloudWatchMetricsEnabled"] = cloud_watch_metrics_enabled

        if limits is not None:
            props["limits"] = limits

        if quiet_time is not None:
            props["quietTime"] = quiet_time

        jsii.create(CfnApplicationSettings, self, [scope, id, props])

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
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> str:
        """``AWS::Pinpoint::ApplicationSettings.ApplicationId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-applicationsettings.html#cfn-pinpoint-applicationsettings-applicationid
        Stability:
            stable
        """
        return jsii.get(self, "applicationId")

    @application_id.setter
    def application_id(self, value: str):
        return jsii.set(self, "applicationId", value)

    @property
    @jsii.member(jsii_name="campaignHook")
    def campaign_hook(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CampaignHookProperty"]]]:
        """``AWS::Pinpoint::ApplicationSettings.CampaignHook``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-applicationsettings.html#cfn-pinpoint-applicationsettings-campaignhook
        Stability:
            stable
        """
        return jsii.get(self, "campaignHook")

    @campaign_hook.setter
    def campaign_hook(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CampaignHookProperty"]]]):
        return jsii.set(self, "campaignHook", value)

    @property
    @jsii.member(jsii_name="cloudWatchMetricsEnabled")
    def cloud_watch_metrics_enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::ApplicationSettings.CloudWatchMetricsEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-applicationsettings.html#cfn-pinpoint-applicationsettings-cloudwatchmetricsenabled
        Stability:
            stable
        """
        return jsii.get(self, "cloudWatchMetricsEnabled")

    @cloud_watch_metrics_enabled.setter
    def cloud_watch_metrics_enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "cloudWatchMetricsEnabled", value)

    @property
    @jsii.member(jsii_name="limits")
    def limits(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LimitsProperty"]]]:
        """``AWS::Pinpoint::ApplicationSettings.Limits``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-applicationsettings.html#cfn-pinpoint-applicationsettings-limits
        Stability:
            stable
        """
        return jsii.get(self, "limits")

    @limits.setter
    def limits(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LimitsProperty"]]]):
        return jsii.set(self, "limits", value)

    @property
    @jsii.member(jsii_name="quietTime")
    def quiet_time(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["QuietTimeProperty"]]]:
        """``AWS::Pinpoint::ApplicationSettings.QuietTime``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-applicationsettings.html#cfn-pinpoint-applicationsettings-quiettime
        Stability:
            stable
        """
        return jsii.get(self, "quietTime")

    @quiet_time.setter
    def quiet_time(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["QuietTimeProperty"]]]):
        return jsii.set(self, "quietTime", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnApplicationSettings.CampaignHookProperty", jsii_struct_bases=[])
    class CampaignHookProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-applicationsettings-campaignhook.html
        Stability:
            stable
        """
        lambdaFunctionName: str
        """``CfnApplicationSettings.CampaignHookProperty.LambdaFunctionName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-applicationsettings-campaignhook.html#cfn-pinpoint-applicationsettings-campaignhook-lambdafunctionname
        Stability:
            stable
        """

        mode: str
        """``CfnApplicationSettings.CampaignHookProperty.Mode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-applicationsettings-campaignhook.html#cfn-pinpoint-applicationsettings-campaignhook-mode
        Stability:
            stable
        """

        webUrl: str
        """``CfnApplicationSettings.CampaignHookProperty.WebUrl``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-applicationsettings-campaignhook.html#cfn-pinpoint-applicationsettings-campaignhook-weburl
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnApplicationSettings.LimitsProperty", jsii_struct_bases=[])
    class LimitsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-applicationsettings-limits.html
        Stability:
            stable
        """
        daily: jsii.Number
        """``CfnApplicationSettings.LimitsProperty.Daily``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-applicationsettings-limits.html#cfn-pinpoint-applicationsettings-limits-daily
        Stability:
            stable
        """

        maximumDuration: jsii.Number
        """``CfnApplicationSettings.LimitsProperty.MaximumDuration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-applicationsettings-limits.html#cfn-pinpoint-applicationsettings-limits-maximumduration
        Stability:
            stable
        """

        messagesPerSecond: jsii.Number
        """``CfnApplicationSettings.LimitsProperty.MessagesPerSecond``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-applicationsettings-limits.html#cfn-pinpoint-applicationsettings-limits-messagespersecond
        Stability:
            stable
        """

        total: jsii.Number
        """``CfnApplicationSettings.LimitsProperty.Total``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-applicationsettings-limits.html#cfn-pinpoint-applicationsettings-limits-total
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnApplicationSettings.QuietTimeProperty", jsii_struct_bases=[])
    class QuietTimeProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-applicationsettings-quiettime.html
        Stability:
            stable
        """
        end: str
        """``CfnApplicationSettings.QuietTimeProperty.End``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-applicationsettings-quiettime.html#cfn-pinpoint-applicationsettings-quiettime-end
        Stability:
            stable
        """

        start: str
        """``CfnApplicationSettings.QuietTimeProperty.Start``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-applicationsettings-quiettime.html#cfn-pinpoint-applicationsettings-quiettime-start
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnApplicationSettingsProps(jsii.compat.TypedDict, total=False):
    campaignHook: typing.Union[aws_cdk.core.IResolvable, "CfnApplicationSettings.CampaignHookProperty"]
    """``AWS::Pinpoint::ApplicationSettings.CampaignHook``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-applicationsettings.html#cfn-pinpoint-applicationsettings-campaignhook
    Stability:
        stable
    """
    cloudWatchMetricsEnabled: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::Pinpoint::ApplicationSettings.CloudWatchMetricsEnabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-applicationsettings.html#cfn-pinpoint-applicationsettings-cloudwatchmetricsenabled
    Stability:
        stable
    """
    limits: typing.Union[aws_cdk.core.IResolvable, "CfnApplicationSettings.LimitsProperty"]
    """``AWS::Pinpoint::ApplicationSettings.Limits``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-applicationsettings.html#cfn-pinpoint-applicationsettings-limits
    Stability:
        stable
    """
    quietTime: typing.Union[aws_cdk.core.IResolvable, "CfnApplicationSettings.QuietTimeProperty"]
    """``AWS::Pinpoint::ApplicationSettings.QuietTime``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-applicationsettings.html#cfn-pinpoint-applicationsettings-quiettime
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnApplicationSettingsProps", jsii_struct_bases=[_CfnApplicationSettingsProps])
class CfnApplicationSettingsProps(_CfnApplicationSettingsProps):
    """Properties for defining a ``AWS::Pinpoint::ApplicationSettings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-applicationsettings.html
    Stability:
        stable
    """
    applicationId: str
    """``AWS::Pinpoint::ApplicationSettings.ApplicationId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-applicationsettings.html#cfn-pinpoint-applicationsettings-applicationid
    Stability:
        stable
    """

class CfnBaiduChannel(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpoint.CfnBaiduChannel"):
    """A CloudFormation ``AWS::Pinpoint::BaiduChannel``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-baiduchannel.html
    Stability:
        stable
    cloudformationResource:
        AWS::Pinpoint::BaiduChannel
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, api_key: str, application_id: str, secret_key: str, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None) -> None:
        """Create a new ``AWS::Pinpoint::BaiduChannel``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            api_key: ``AWS::Pinpoint::BaiduChannel.ApiKey``.
            application_id: ``AWS::Pinpoint::BaiduChannel.ApplicationId``.
            secret_key: ``AWS::Pinpoint::BaiduChannel.SecretKey``.
            enabled: ``AWS::Pinpoint::BaiduChannel.Enabled``.

        Stability:
            experimental
        """
        props: CfnBaiduChannelProps = {"apiKey": api_key, "applicationId": application_id, "secretKey": secret_key}

        if enabled is not None:
            props["enabled"] = enabled

        jsii.create(CfnBaiduChannel, self, [scope, id, props])

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
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="apiKey")
    def api_key(self) -> str:
        """``AWS::Pinpoint::BaiduChannel.ApiKey``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-baiduchannel.html#cfn-pinpoint-baiduchannel-apikey
        Stability:
            stable
        """
        return jsii.get(self, "apiKey")

    @api_key.setter
    def api_key(self, value: str):
        return jsii.set(self, "apiKey", value)

    @property
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> str:
        """``AWS::Pinpoint::BaiduChannel.ApplicationId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-baiduchannel.html#cfn-pinpoint-baiduchannel-applicationid
        Stability:
            stable
        """
        return jsii.get(self, "applicationId")

    @application_id.setter
    def application_id(self, value: str):
        return jsii.set(self, "applicationId", value)

    @property
    @jsii.member(jsii_name="secretKey")
    def secret_key(self) -> str:
        """``AWS::Pinpoint::BaiduChannel.SecretKey``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-baiduchannel.html#cfn-pinpoint-baiduchannel-secretkey
        Stability:
            stable
        """
        return jsii.get(self, "secretKey")

    @secret_key.setter
    def secret_key(self, value: str):
        return jsii.set(self, "secretKey", value)

    @property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::BaiduChannel.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-baiduchannel.html#cfn-pinpoint-baiduchannel-enabled
        Stability:
            stable
        """
        return jsii.get(self, "enabled")

    @enabled.setter
    def enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "enabled", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnBaiduChannelProps(jsii.compat.TypedDict, total=False):
    enabled: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::Pinpoint::BaiduChannel.Enabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-baiduchannel.html#cfn-pinpoint-baiduchannel-enabled
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnBaiduChannelProps", jsii_struct_bases=[_CfnBaiduChannelProps])
class CfnBaiduChannelProps(_CfnBaiduChannelProps):
    """Properties for defining a ``AWS::Pinpoint::BaiduChannel``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-baiduchannel.html
    Stability:
        stable
    """
    apiKey: str
    """``AWS::Pinpoint::BaiduChannel.ApiKey``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-baiduchannel.html#cfn-pinpoint-baiduchannel-apikey
    Stability:
        stable
    """

    applicationId: str
    """``AWS::Pinpoint::BaiduChannel.ApplicationId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-baiduchannel.html#cfn-pinpoint-baiduchannel-applicationid
    Stability:
        stable
    """

    secretKey: str
    """``AWS::Pinpoint::BaiduChannel.SecretKey``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-baiduchannel.html#cfn-pinpoint-baiduchannel-secretkey
    Stability:
        stable
    """

class CfnCampaign(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpoint.CfnCampaign"):
    """A CloudFormation ``AWS::Pinpoint::Campaign``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html
    Stability:
        stable
    cloudformationResource:
        AWS::Pinpoint::Campaign
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application_id: str, message_configuration: typing.Union[aws_cdk.core.IResolvable, "MessageConfigurationProperty"], name: str, schedule: typing.Union[aws_cdk.core.IResolvable, "ScheduleProperty"], segment_id: str, additional_treatments: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "WriteTreatmentResourceProperty"]]]]]=None, campaign_hook: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CampaignHookProperty"]]]=None, description: typing.Optional[str]=None, holdout_percent: typing.Optional[jsii.Number]=None, is_paused: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, limits: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LimitsProperty"]]]=None, segment_version: typing.Optional[jsii.Number]=None, treatment_description: typing.Optional[str]=None, treatment_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Pinpoint::Campaign``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            application_id: ``AWS::Pinpoint::Campaign.ApplicationId``.
            message_configuration: ``AWS::Pinpoint::Campaign.MessageConfiguration``.
            name: ``AWS::Pinpoint::Campaign.Name``.
            schedule: ``AWS::Pinpoint::Campaign.Schedule``.
            segment_id: ``AWS::Pinpoint::Campaign.SegmentId``.
            additional_treatments: ``AWS::Pinpoint::Campaign.AdditionalTreatments``.
            campaign_hook: ``AWS::Pinpoint::Campaign.CampaignHook``.
            description: ``AWS::Pinpoint::Campaign.Description``.
            holdout_percent: ``AWS::Pinpoint::Campaign.HoldoutPercent``.
            is_paused: ``AWS::Pinpoint::Campaign.IsPaused``.
            limits: ``AWS::Pinpoint::Campaign.Limits``.
            segment_version: ``AWS::Pinpoint::Campaign.SegmentVersion``.
            treatment_description: ``AWS::Pinpoint::Campaign.TreatmentDescription``.
            treatment_name: ``AWS::Pinpoint::Campaign.TreatmentName``.

        Stability:
            experimental
        """
        props: CfnCampaignProps = {"applicationId": application_id, "messageConfiguration": message_configuration, "name": name, "schedule": schedule, "segmentId": segment_id}

        if additional_treatments is not None:
            props["additionalTreatments"] = additional_treatments

        if campaign_hook is not None:
            props["campaignHook"] = campaign_hook

        if description is not None:
            props["description"] = description

        if holdout_percent is not None:
            props["holdoutPercent"] = holdout_percent

        if is_paused is not None:
            props["isPaused"] = is_paused

        if limits is not None:
            props["limits"] = limits

        if segment_version is not None:
            props["segmentVersion"] = segment_version

        if treatment_description is not None:
            props["treatmentDescription"] = treatment_description

        if treatment_name is not None:
            props["treatmentName"] = treatment_name

        jsii.create(CfnCampaign, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrCampaignId")
    def attr_campaign_id(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            CampaignId
        """
        return jsii.get(self, "attrCampaignId")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> str:
        """``AWS::Pinpoint::Campaign.ApplicationId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-applicationid
        Stability:
            stable
        """
        return jsii.get(self, "applicationId")

    @application_id.setter
    def application_id(self, value: str):
        return jsii.set(self, "applicationId", value)

    @property
    @jsii.member(jsii_name="messageConfiguration")
    def message_configuration(self) -> typing.Union[aws_cdk.core.IResolvable, "MessageConfigurationProperty"]:
        """``AWS::Pinpoint::Campaign.MessageConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-messageconfiguration
        Stability:
            stable
        """
        return jsii.get(self, "messageConfiguration")

    @message_configuration.setter
    def message_configuration(self, value: typing.Union[aws_cdk.core.IResolvable, "MessageConfigurationProperty"]):
        return jsii.set(self, "messageConfiguration", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::Pinpoint::Campaign.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="schedule")
    def schedule(self) -> typing.Union[aws_cdk.core.IResolvable, "ScheduleProperty"]:
        """``AWS::Pinpoint::Campaign.Schedule``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-schedule
        Stability:
            stable
        """
        return jsii.get(self, "schedule")

    @schedule.setter
    def schedule(self, value: typing.Union[aws_cdk.core.IResolvable, "ScheduleProperty"]):
        return jsii.set(self, "schedule", value)

    @property
    @jsii.member(jsii_name="segmentId")
    def segment_id(self) -> str:
        """``AWS::Pinpoint::Campaign.SegmentId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-segmentid
        Stability:
            stable
        """
        return jsii.get(self, "segmentId")

    @segment_id.setter
    def segment_id(self, value: str):
        return jsii.set(self, "segmentId", value)

    @property
    @jsii.member(jsii_name="additionalTreatments")
    def additional_treatments(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "WriteTreatmentResourceProperty"]]]]]:
        """``AWS::Pinpoint::Campaign.AdditionalTreatments``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-additionaltreatments
        Stability:
            stable
        """
        return jsii.get(self, "additionalTreatments")

    @additional_treatments.setter
    def additional_treatments(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "WriteTreatmentResourceProperty"]]]]]):
        return jsii.set(self, "additionalTreatments", value)

    @property
    @jsii.member(jsii_name="campaignHook")
    def campaign_hook(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CampaignHookProperty"]]]:
        """``AWS::Pinpoint::Campaign.CampaignHook``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-campaignhook
        Stability:
            stable
        """
        return jsii.get(self, "campaignHook")

    @campaign_hook.setter
    def campaign_hook(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CampaignHookProperty"]]]):
        return jsii.set(self, "campaignHook", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::Campaign.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-description
        Stability:
            stable
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="holdoutPercent")
    def holdout_percent(self) -> typing.Optional[jsii.Number]:
        """``AWS::Pinpoint::Campaign.HoldoutPercent``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-holdoutpercent
        Stability:
            stable
        """
        return jsii.get(self, "holdoutPercent")

    @holdout_percent.setter
    def holdout_percent(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "holdoutPercent", value)

    @property
    @jsii.member(jsii_name="isPaused")
    def is_paused(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::Campaign.IsPaused``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-ispaused
        Stability:
            stable
        """
        return jsii.get(self, "isPaused")

    @is_paused.setter
    def is_paused(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "isPaused", value)

    @property
    @jsii.member(jsii_name="limits")
    def limits(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LimitsProperty"]]]:
        """``AWS::Pinpoint::Campaign.Limits``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-limits
        Stability:
            stable
        """
        return jsii.get(self, "limits")

    @limits.setter
    def limits(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LimitsProperty"]]]):
        return jsii.set(self, "limits", value)

    @property
    @jsii.member(jsii_name="segmentVersion")
    def segment_version(self) -> typing.Optional[jsii.Number]:
        """``AWS::Pinpoint::Campaign.SegmentVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-segmentversion
        Stability:
            stable
        """
        return jsii.get(self, "segmentVersion")

    @segment_version.setter
    def segment_version(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "segmentVersion", value)

    @property
    @jsii.member(jsii_name="treatmentDescription")
    def treatment_description(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::Campaign.TreatmentDescription``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-treatmentdescription
        Stability:
            stable
        """
        return jsii.get(self, "treatmentDescription")

    @treatment_description.setter
    def treatment_description(self, value: typing.Optional[str]):
        return jsii.set(self, "treatmentDescription", value)

    @property
    @jsii.member(jsii_name="treatmentName")
    def treatment_name(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::Campaign.TreatmentName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-treatmentname
        Stability:
            stable
        """
        return jsii.get(self, "treatmentName")

    @treatment_name.setter
    def treatment_name(self, value: typing.Optional[str]):
        return jsii.set(self, "treatmentName", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnCampaign.AttributeDimensionProperty", jsii_struct_bases=[])
    class AttributeDimensionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-attributedimension.html
        Stability:
            stable
        """
        attributeType: str
        """``CfnCampaign.AttributeDimensionProperty.AttributeType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-attributedimension.html#cfn-pinpoint-campaign-attributedimension-attributetype
        Stability:
            stable
        """

        values: typing.List[str]
        """``CfnCampaign.AttributeDimensionProperty.Values``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-attributedimension.html#cfn-pinpoint-campaign-attributedimension-values
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnCampaign.CampaignEmailMessageProperty", jsii_struct_bases=[])
    class CampaignEmailMessageProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-campaignemailmessage.html
        Stability:
            stable
        """
        body: str
        """``CfnCampaign.CampaignEmailMessageProperty.Body``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-campaignemailmessage.html#cfn-pinpoint-campaign-campaignemailmessage-body
        Stability:
            stable
        """

        fromAddress: str
        """``CfnCampaign.CampaignEmailMessageProperty.FromAddress``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-campaignemailmessage.html#cfn-pinpoint-campaign-campaignemailmessage-fromaddress
        Stability:
            stable
        """

        htmlBody: str
        """``CfnCampaign.CampaignEmailMessageProperty.HtmlBody``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-campaignemailmessage.html#cfn-pinpoint-campaign-campaignemailmessage-htmlbody
        Stability:
            stable
        """

        title: str
        """``CfnCampaign.CampaignEmailMessageProperty.Title``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-campaignemailmessage.html#cfn-pinpoint-campaign-campaignemailmessage-title
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnCampaign.CampaignEventFilterProperty", jsii_struct_bases=[])
    class CampaignEventFilterProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-campaigneventfilter.html
        Stability:
            stable
        """
        dimensions: typing.Union[aws_cdk.core.IResolvable, "CfnCampaign.EventDimensionsProperty"]
        """``CfnCampaign.CampaignEventFilterProperty.Dimensions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-campaigneventfilter.html#cfn-pinpoint-campaign-campaigneventfilter-dimensions
        Stability:
            stable
        """

        filterType: str
        """``CfnCampaign.CampaignEventFilterProperty.FilterType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-campaigneventfilter.html#cfn-pinpoint-campaign-campaigneventfilter-filtertype
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnCampaign.CampaignHookProperty", jsii_struct_bases=[])
    class CampaignHookProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-campaignhook.html
        Stability:
            stable
        """
        lambdaFunctionName: str
        """``CfnCampaign.CampaignHookProperty.LambdaFunctionName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-campaignhook.html#cfn-pinpoint-campaign-campaignhook-lambdafunctionname
        Stability:
            stable
        """

        mode: str
        """``CfnCampaign.CampaignHookProperty.Mode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-campaignhook.html#cfn-pinpoint-campaign-campaignhook-mode
        Stability:
            stable
        """

        webUrl: str
        """``CfnCampaign.CampaignHookProperty.WebUrl``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-campaignhook.html#cfn-pinpoint-campaign-campaignhook-weburl
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnCampaign.CampaignSmsMessageProperty", jsii_struct_bases=[])
    class CampaignSmsMessageProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-campaignsmsmessage.html
        Stability:
            stable
        """
        body: str
        """``CfnCampaign.CampaignSmsMessageProperty.Body``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-campaignsmsmessage.html#cfn-pinpoint-campaign-campaignsmsmessage-body
        Stability:
            stable
        """

        messageType: str
        """``CfnCampaign.CampaignSmsMessageProperty.MessageType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-campaignsmsmessage.html#cfn-pinpoint-campaign-campaignsmsmessage-messagetype
        Stability:
            stable
        """

        senderId: str
        """``CfnCampaign.CampaignSmsMessageProperty.SenderId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-campaignsmsmessage.html#cfn-pinpoint-campaign-campaignsmsmessage-senderid
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnCampaign.EventDimensionsProperty", jsii_struct_bases=[])
    class EventDimensionsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-eventdimensions.html
        Stability:
            stable
        """
        attributes: typing.Any
        """``CfnCampaign.EventDimensionsProperty.Attributes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-eventdimensions.html#cfn-pinpoint-campaign-eventdimensions-attributes
        Stability:
            stable
        """

        eventType: typing.Union[aws_cdk.core.IResolvable, "CfnCampaign.SetDimensionProperty"]
        """``CfnCampaign.EventDimensionsProperty.EventType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-eventdimensions.html#cfn-pinpoint-campaign-eventdimensions-eventtype
        Stability:
            stable
        """

        metrics: typing.Any
        """``CfnCampaign.EventDimensionsProperty.Metrics``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-eventdimensions.html#cfn-pinpoint-campaign-eventdimensions-metrics
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnCampaign.LimitsProperty", jsii_struct_bases=[])
    class LimitsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-limits.html
        Stability:
            stable
        """
        daily: jsii.Number
        """``CfnCampaign.LimitsProperty.Daily``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-limits.html#cfn-pinpoint-campaign-limits-daily
        Stability:
            stable
        """

        maximumDuration: jsii.Number
        """``CfnCampaign.LimitsProperty.MaximumDuration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-limits.html#cfn-pinpoint-campaign-limits-maximumduration
        Stability:
            stable
        """

        messagesPerSecond: jsii.Number
        """``CfnCampaign.LimitsProperty.MessagesPerSecond``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-limits.html#cfn-pinpoint-campaign-limits-messagespersecond
        Stability:
            stable
        """

        total: jsii.Number
        """``CfnCampaign.LimitsProperty.Total``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-limits.html#cfn-pinpoint-campaign-limits-total
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnCampaign.MessageConfigurationProperty", jsii_struct_bases=[])
    class MessageConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-messageconfiguration.html
        Stability:
            stable
        """
        admMessage: typing.Union[aws_cdk.core.IResolvable, "CfnCampaign.MessageProperty"]
        """``CfnCampaign.MessageConfigurationProperty.ADMMessage``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-messageconfiguration.html#cfn-pinpoint-campaign-messageconfiguration-admmessage
        Stability:
            stable
        """

        apnsMessage: typing.Union[aws_cdk.core.IResolvable, "CfnCampaign.MessageProperty"]
        """``CfnCampaign.MessageConfigurationProperty.APNSMessage``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-messageconfiguration.html#cfn-pinpoint-campaign-messageconfiguration-apnsmessage
        Stability:
            stable
        """

        baiduMessage: typing.Union[aws_cdk.core.IResolvable, "CfnCampaign.MessageProperty"]
        """``CfnCampaign.MessageConfigurationProperty.BaiduMessage``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-messageconfiguration.html#cfn-pinpoint-campaign-messageconfiguration-baidumessage
        Stability:
            stable
        """

        defaultMessage: typing.Union[aws_cdk.core.IResolvable, "CfnCampaign.MessageProperty"]
        """``CfnCampaign.MessageConfigurationProperty.DefaultMessage``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-messageconfiguration.html#cfn-pinpoint-campaign-messageconfiguration-defaultmessage
        Stability:
            stable
        """

        emailMessage: typing.Union[aws_cdk.core.IResolvable, "CfnCampaign.CampaignEmailMessageProperty"]
        """``CfnCampaign.MessageConfigurationProperty.EmailMessage``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-messageconfiguration.html#cfn-pinpoint-campaign-messageconfiguration-emailmessage
        Stability:
            stable
        """

        gcmMessage: typing.Union[aws_cdk.core.IResolvable, "CfnCampaign.MessageProperty"]
        """``CfnCampaign.MessageConfigurationProperty.GCMMessage``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-messageconfiguration.html#cfn-pinpoint-campaign-messageconfiguration-gcmmessage
        Stability:
            stable
        """

        smsMessage: typing.Union[aws_cdk.core.IResolvable, "CfnCampaign.CampaignSmsMessageProperty"]
        """``CfnCampaign.MessageConfigurationProperty.SMSMessage``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-messageconfiguration.html#cfn-pinpoint-campaign-messageconfiguration-smsmessage
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnCampaign.MessageProperty", jsii_struct_bases=[])
    class MessageProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-message.html
        Stability:
            stable
        """
        action: str
        """``CfnCampaign.MessageProperty.Action``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-message.html#cfn-pinpoint-campaign-message-action
        Stability:
            stable
        """

        body: str
        """``CfnCampaign.MessageProperty.Body``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-message.html#cfn-pinpoint-campaign-message-body
        Stability:
            stable
        """

        imageIconUrl: str
        """``CfnCampaign.MessageProperty.ImageIconUrl``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-message.html#cfn-pinpoint-campaign-message-imageiconurl
        Stability:
            stable
        """

        imageSmallIconUrl: str
        """``CfnCampaign.MessageProperty.ImageSmallIconUrl``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-message.html#cfn-pinpoint-campaign-message-imagesmalliconurl
        Stability:
            stable
        """

        imageUrl: str
        """``CfnCampaign.MessageProperty.ImageUrl``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-message.html#cfn-pinpoint-campaign-message-imageurl
        Stability:
            stable
        """

        jsonBody: str
        """``CfnCampaign.MessageProperty.JsonBody``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-message.html#cfn-pinpoint-campaign-message-jsonbody
        Stability:
            stable
        """

        mediaUrl: str
        """``CfnCampaign.MessageProperty.MediaUrl``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-message.html#cfn-pinpoint-campaign-message-mediaurl
        Stability:
            stable
        """

        rawContent: str
        """``CfnCampaign.MessageProperty.RawContent``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-message.html#cfn-pinpoint-campaign-message-rawcontent
        Stability:
            stable
        """

        silentPush: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnCampaign.MessageProperty.SilentPush``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-message.html#cfn-pinpoint-campaign-message-silentpush
        Stability:
            stable
        """

        timeToLive: jsii.Number
        """``CfnCampaign.MessageProperty.TimeToLive``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-message.html#cfn-pinpoint-campaign-message-timetolive
        Stability:
            stable
        """

        title: str
        """``CfnCampaign.MessageProperty.Title``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-message.html#cfn-pinpoint-campaign-message-title
        Stability:
            stable
        """

        url: str
        """``CfnCampaign.MessageProperty.Url``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-message.html#cfn-pinpoint-campaign-message-url
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnCampaign.MetricDimensionProperty", jsii_struct_bases=[])
    class MetricDimensionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-metricdimension.html
        Stability:
            stable
        """
        comparisonOperator: str
        """``CfnCampaign.MetricDimensionProperty.ComparisonOperator``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-metricdimension.html#cfn-pinpoint-campaign-metricdimension-comparisonoperator
        Stability:
            stable
        """

        value: jsii.Number
        """``CfnCampaign.MetricDimensionProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-metricdimension.html#cfn-pinpoint-campaign-metricdimension-value
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnCampaign.QuietTimeProperty", jsii_struct_bases=[])
    class QuietTimeProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-schedule-quiettime.html
        Stability:
            stable
        """
        end: str
        """``CfnCampaign.QuietTimeProperty.End``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-schedule-quiettime.html#cfn-pinpoint-campaign-schedule-quiettime-end
        Stability:
            stable
        """

        start: str
        """``CfnCampaign.QuietTimeProperty.Start``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-schedule-quiettime.html#cfn-pinpoint-campaign-schedule-quiettime-start
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnCampaign.ScheduleProperty", jsii_struct_bases=[])
    class ScheduleProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-schedule.html
        Stability:
            stable
        """
        endTime: str
        """``CfnCampaign.ScheduleProperty.EndTime``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-schedule.html#cfn-pinpoint-campaign-schedule-endtime
        Stability:
            stable
        """

        eventFilter: typing.Union[aws_cdk.core.IResolvable, "CfnCampaign.CampaignEventFilterProperty"]
        """``CfnCampaign.ScheduleProperty.EventFilter``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-schedule.html#cfn-pinpoint-campaign-schedule-eventfilter
        Stability:
            stable
        """

        frequency: str
        """``CfnCampaign.ScheduleProperty.Frequency``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-schedule.html#cfn-pinpoint-campaign-schedule-frequency
        Stability:
            stable
        """

        isLocalTime: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnCampaign.ScheduleProperty.IsLocalTime``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-schedule.html#cfn-pinpoint-campaign-schedule-islocaltime
        Stability:
            stable
        """

        quietTime: typing.Union[aws_cdk.core.IResolvable, "CfnCampaign.QuietTimeProperty"]
        """``CfnCampaign.ScheduleProperty.QuietTime``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-schedule.html#cfn-pinpoint-campaign-schedule-quiettime
        Stability:
            stable
        """

        startTime: str
        """``CfnCampaign.ScheduleProperty.StartTime``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-schedule.html#cfn-pinpoint-campaign-schedule-starttime
        Stability:
            stable
        """

        timeZone: str
        """``CfnCampaign.ScheduleProperty.TimeZone``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-schedule.html#cfn-pinpoint-campaign-schedule-timezone
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnCampaign.SetDimensionProperty", jsii_struct_bases=[])
    class SetDimensionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-setdimension.html
        Stability:
            stable
        """
        dimensionType: str
        """``CfnCampaign.SetDimensionProperty.DimensionType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-setdimension.html#cfn-pinpoint-campaign-setdimension-dimensiontype
        Stability:
            stable
        """

        values: typing.List[str]
        """``CfnCampaign.SetDimensionProperty.Values``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-setdimension.html#cfn-pinpoint-campaign-setdimension-values
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnCampaign.WriteTreatmentResourceProperty", jsii_struct_bases=[])
    class WriteTreatmentResourceProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-writetreatmentresource.html
        Stability:
            stable
        """
        messageConfiguration: typing.Union[aws_cdk.core.IResolvable, "CfnCampaign.MessageConfigurationProperty"]
        """``CfnCampaign.WriteTreatmentResourceProperty.MessageConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-writetreatmentresource.html#cfn-pinpoint-campaign-writetreatmentresource-messageconfiguration
        Stability:
            stable
        """

        schedule: typing.Union[aws_cdk.core.IResolvable, "CfnCampaign.ScheduleProperty"]
        """``CfnCampaign.WriteTreatmentResourceProperty.Schedule``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-writetreatmentresource.html#cfn-pinpoint-campaign-writetreatmentresource-schedule
        Stability:
            stable
        """

        sizePercent: jsii.Number
        """``CfnCampaign.WriteTreatmentResourceProperty.SizePercent``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-writetreatmentresource.html#cfn-pinpoint-campaign-writetreatmentresource-sizepercent
        Stability:
            stable
        """

        treatmentDescription: str
        """``CfnCampaign.WriteTreatmentResourceProperty.TreatmentDescription``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-writetreatmentresource.html#cfn-pinpoint-campaign-writetreatmentresource-treatmentdescription
        Stability:
            stable
        """

        treatmentName: str
        """``CfnCampaign.WriteTreatmentResourceProperty.TreatmentName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-writetreatmentresource.html#cfn-pinpoint-campaign-writetreatmentresource-treatmentname
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnCampaignProps(jsii.compat.TypedDict, total=False):
    additionalTreatments: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCampaign.WriteTreatmentResourceProperty"]]]
    """``AWS::Pinpoint::Campaign.AdditionalTreatments``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-additionaltreatments
    Stability:
        stable
    """
    campaignHook: typing.Union[aws_cdk.core.IResolvable, "CfnCampaign.CampaignHookProperty"]
    """``AWS::Pinpoint::Campaign.CampaignHook``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-campaignhook
    Stability:
        stable
    """
    description: str
    """``AWS::Pinpoint::Campaign.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-description
    Stability:
        stable
    """
    holdoutPercent: jsii.Number
    """``AWS::Pinpoint::Campaign.HoldoutPercent``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-holdoutpercent
    Stability:
        stable
    """
    isPaused: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::Pinpoint::Campaign.IsPaused``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-ispaused
    Stability:
        stable
    """
    limits: typing.Union[aws_cdk.core.IResolvable, "CfnCampaign.LimitsProperty"]
    """``AWS::Pinpoint::Campaign.Limits``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-limits
    Stability:
        stable
    """
    segmentVersion: jsii.Number
    """``AWS::Pinpoint::Campaign.SegmentVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-segmentversion
    Stability:
        stable
    """
    treatmentDescription: str
    """``AWS::Pinpoint::Campaign.TreatmentDescription``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-treatmentdescription
    Stability:
        stable
    """
    treatmentName: str
    """``AWS::Pinpoint::Campaign.TreatmentName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-treatmentname
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnCampaignProps", jsii_struct_bases=[_CfnCampaignProps])
class CfnCampaignProps(_CfnCampaignProps):
    """Properties for defining a ``AWS::Pinpoint::Campaign``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html
    Stability:
        stable
    """
    applicationId: str
    """``AWS::Pinpoint::Campaign.ApplicationId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-applicationid
    Stability:
        stable
    """

    messageConfiguration: typing.Union[aws_cdk.core.IResolvable, "CfnCampaign.MessageConfigurationProperty"]
    """``AWS::Pinpoint::Campaign.MessageConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-messageconfiguration
    Stability:
        stable
    """

    name: str
    """``AWS::Pinpoint::Campaign.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-name
    Stability:
        stable
    """

    schedule: typing.Union[aws_cdk.core.IResolvable, "CfnCampaign.ScheduleProperty"]
    """``AWS::Pinpoint::Campaign.Schedule``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-schedule
    Stability:
        stable
    """

    segmentId: str
    """``AWS::Pinpoint::Campaign.SegmentId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-segmentid
    Stability:
        stable
    """

class CfnEmailChannel(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpoint.CfnEmailChannel"):
    """A CloudFormation ``AWS::Pinpoint::EmailChannel``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-emailchannel.html
    Stability:
        stable
    cloudformationResource:
        AWS::Pinpoint::EmailChannel
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application_id: str, from_address: str, identity: str, configuration_set: typing.Optional[str]=None, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, role_arn: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Pinpoint::EmailChannel``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            application_id: ``AWS::Pinpoint::EmailChannel.ApplicationId``.
            from_address: ``AWS::Pinpoint::EmailChannel.FromAddress``.
            identity: ``AWS::Pinpoint::EmailChannel.Identity``.
            configuration_set: ``AWS::Pinpoint::EmailChannel.ConfigurationSet``.
            enabled: ``AWS::Pinpoint::EmailChannel.Enabled``.
            role_arn: ``AWS::Pinpoint::EmailChannel.RoleArn``.

        Stability:
            experimental
        """
        props: CfnEmailChannelProps = {"applicationId": application_id, "fromAddress": from_address, "identity": identity}

        if configuration_set is not None:
            props["configurationSet"] = configuration_set

        if enabled is not None:
            props["enabled"] = enabled

        if role_arn is not None:
            props["roleArn"] = role_arn

        jsii.create(CfnEmailChannel, self, [scope, id, props])

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
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> str:
        """``AWS::Pinpoint::EmailChannel.ApplicationId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-emailchannel.html#cfn-pinpoint-emailchannel-applicationid
        Stability:
            stable
        """
        return jsii.get(self, "applicationId")

    @application_id.setter
    def application_id(self, value: str):
        return jsii.set(self, "applicationId", value)

    @property
    @jsii.member(jsii_name="fromAddress")
    def from_address(self) -> str:
        """``AWS::Pinpoint::EmailChannel.FromAddress``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-emailchannel.html#cfn-pinpoint-emailchannel-fromaddress
        Stability:
            stable
        """
        return jsii.get(self, "fromAddress")

    @from_address.setter
    def from_address(self, value: str):
        return jsii.set(self, "fromAddress", value)

    @property
    @jsii.member(jsii_name="identity")
    def identity(self) -> str:
        """``AWS::Pinpoint::EmailChannel.Identity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-emailchannel.html#cfn-pinpoint-emailchannel-identity
        Stability:
            stable
        """
        return jsii.get(self, "identity")

    @identity.setter
    def identity(self, value: str):
        return jsii.set(self, "identity", value)

    @property
    @jsii.member(jsii_name="configurationSet")
    def configuration_set(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::EmailChannel.ConfigurationSet``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-emailchannel.html#cfn-pinpoint-emailchannel-configurationset
        Stability:
            stable
        """
        return jsii.get(self, "configurationSet")

    @configuration_set.setter
    def configuration_set(self, value: typing.Optional[str]):
        return jsii.set(self, "configurationSet", value)

    @property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::EmailChannel.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-emailchannel.html#cfn-pinpoint-emailchannel-enabled
        Stability:
            stable
        """
        return jsii.get(self, "enabled")

    @enabled.setter
    def enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "enabled", value)

    @property
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::EmailChannel.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-emailchannel.html#cfn-pinpoint-emailchannel-rolearn
        Stability:
            stable
        """
        return jsii.get(self, "roleArn")

    @role_arn.setter
    def role_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "roleArn", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnEmailChannelProps(jsii.compat.TypedDict, total=False):
    configurationSet: str
    """``AWS::Pinpoint::EmailChannel.ConfigurationSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-emailchannel.html#cfn-pinpoint-emailchannel-configurationset
    Stability:
        stable
    """
    enabled: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::Pinpoint::EmailChannel.Enabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-emailchannel.html#cfn-pinpoint-emailchannel-enabled
    Stability:
        stable
    """
    roleArn: str
    """``AWS::Pinpoint::EmailChannel.RoleArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-emailchannel.html#cfn-pinpoint-emailchannel-rolearn
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnEmailChannelProps", jsii_struct_bases=[_CfnEmailChannelProps])
class CfnEmailChannelProps(_CfnEmailChannelProps):
    """Properties for defining a ``AWS::Pinpoint::EmailChannel``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-emailchannel.html
    Stability:
        stable
    """
    applicationId: str
    """``AWS::Pinpoint::EmailChannel.ApplicationId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-emailchannel.html#cfn-pinpoint-emailchannel-applicationid
    Stability:
        stable
    """

    fromAddress: str
    """``AWS::Pinpoint::EmailChannel.FromAddress``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-emailchannel.html#cfn-pinpoint-emailchannel-fromaddress
    Stability:
        stable
    """

    identity: str
    """``AWS::Pinpoint::EmailChannel.Identity``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-emailchannel.html#cfn-pinpoint-emailchannel-identity
    Stability:
        stable
    """

class CfnEventStream(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpoint.CfnEventStream"):
    """A CloudFormation ``AWS::Pinpoint::EventStream``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-eventstream.html
    Stability:
        stable
    cloudformationResource:
        AWS::Pinpoint::EventStream
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application_id: str, destination_stream_arn: str, role_arn: str) -> None:
        """Create a new ``AWS::Pinpoint::EventStream``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            application_id: ``AWS::Pinpoint::EventStream.ApplicationId``.
            destination_stream_arn: ``AWS::Pinpoint::EventStream.DestinationStreamArn``.
            role_arn: ``AWS::Pinpoint::EventStream.RoleArn``.

        Stability:
            experimental
        """
        props: CfnEventStreamProps = {"applicationId": application_id, "destinationStreamArn": destination_stream_arn, "roleArn": role_arn}

        jsii.create(CfnEventStream, self, [scope, id, props])

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
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> str:
        """``AWS::Pinpoint::EventStream.ApplicationId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-eventstream.html#cfn-pinpoint-eventstream-applicationid
        Stability:
            stable
        """
        return jsii.get(self, "applicationId")

    @application_id.setter
    def application_id(self, value: str):
        return jsii.set(self, "applicationId", value)

    @property
    @jsii.member(jsii_name="destinationStreamArn")
    def destination_stream_arn(self) -> str:
        """``AWS::Pinpoint::EventStream.DestinationStreamArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-eventstream.html#cfn-pinpoint-eventstream-destinationstreamarn
        Stability:
            stable
        """
        return jsii.get(self, "destinationStreamArn")

    @destination_stream_arn.setter
    def destination_stream_arn(self, value: str):
        return jsii.set(self, "destinationStreamArn", value)

    @property
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> str:
        """``AWS::Pinpoint::EventStream.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-eventstream.html#cfn-pinpoint-eventstream-rolearn
        Stability:
            stable
        """
        return jsii.get(self, "roleArn")

    @role_arn.setter
    def role_arn(self, value: str):
        return jsii.set(self, "roleArn", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnEventStreamProps", jsii_struct_bases=[])
class CfnEventStreamProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::Pinpoint::EventStream``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-eventstream.html
    Stability:
        stable
    """
    applicationId: str
    """``AWS::Pinpoint::EventStream.ApplicationId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-eventstream.html#cfn-pinpoint-eventstream-applicationid
    Stability:
        stable
    """

    destinationStreamArn: str
    """``AWS::Pinpoint::EventStream.DestinationStreamArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-eventstream.html#cfn-pinpoint-eventstream-destinationstreamarn
    Stability:
        stable
    """

    roleArn: str
    """``AWS::Pinpoint::EventStream.RoleArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-eventstream.html#cfn-pinpoint-eventstream-rolearn
    Stability:
        stable
    """

class CfnGCMChannel(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpoint.CfnGCMChannel"):
    """A CloudFormation ``AWS::Pinpoint::GCMChannel``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-gcmchannel.html
    Stability:
        stable
    cloudformationResource:
        AWS::Pinpoint::GCMChannel
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, api_key: str, application_id: str, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None) -> None:
        """Create a new ``AWS::Pinpoint::GCMChannel``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            api_key: ``AWS::Pinpoint::GCMChannel.ApiKey``.
            application_id: ``AWS::Pinpoint::GCMChannel.ApplicationId``.
            enabled: ``AWS::Pinpoint::GCMChannel.Enabled``.

        Stability:
            experimental
        """
        props: CfnGCMChannelProps = {"apiKey": api_key, "applicationId": application_id}

        if enabled is not None:
            props["enabled"] = enabled

        jsii.create(CfnGCMChannel, self, [scope, id, props])

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
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="apiKey")
    def api_key(self) -> str:
        """``AWS::Pinpoint::GCMChannel.ApiKey``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-gcmchannel.html#cfn-pinpoint-gcmchannel-apikey
        Stability:
            stable
        """
        return jsii.get(self, "apiKey")

    @api_key.setter
    def api_key(self, value: str):
        return jsii.set(self, "apiKey", value)

    @property
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> str:
        """``AWS::Pinpoint::GCMChannel.ApplicationId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-gcmchannel.html#cfn-pinpoint-gcmchannel-applicationid
        Stability:
            stable
        """
        return jsii.get(self, "applicationId")

    @application_id.setter
    def application_id(self, value: str):
        return jsii.set(self, "applicationId", value)

    @property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::GCMChannel.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-gcmchannel.html#cfn-pinpoint-gcmchannel-enabled
        Stability:
            stable
        """
        return jsii.get(self, "enabled")

    @enabled.setter
    def enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "enabled", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnGCMChannelProps(jsii.compat.TypedDict, total=False):
    enabled: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::Pinpoint::GCMChannel.Enabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-gcmchannel.html#cfn-pinpoint-gcmchannel-enabled
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnGCMChannelProps", jsii_struct_bases=[_CfnGCMChannelProps])
class CfnGCMChannelProps(_CfnGCMChannelProps):
    """Properties for defining a ``AWS::Pinpoint::GCMChannel``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-gcmchannel.html
    Stability:
        stable
    """
    apiKey: str
    """``AWS::Pinpoint::GCMChannel.ApiKey``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-gcmchannel.html#cfn-pinpoint-gcmchannel-apikey
    Stability:
        stable
    """

    applicationId: str
    """``AWS::Pinpoint::GCMChannel.ApplicationId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-gcmchannel.html#cfn-pinpoint-gcmchannel-applicationid
    Stability:
        stable
    """

class CfnSMSChannel(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpoint.CfnSMSChannel"):
    """A CloudFormation ``AWS::Pinpoint::SMSChannel``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-smschannel.html
    Stability:
        stable
    cloudformationResource:
        AWS::Pinpoint::SMSChannel
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application_id: str, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, sender_id: typing.Optional[str]=None, short_code: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Pinpoint::SMSChannel``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            application_id: ``AWS::Pinpoint::SMSChannel.ApplicationId``.
            enabled: ``AWS::Pinpoint::SMSChannel.Enabled``.
            sender_id: ``AWS::Pinpoint::SMSChannel.SenderId``.
            short_code: ``AWS::Pinpoint::SMSChannel.ShortCode``.

        Stability:
            experimental
        """
        props: CfnSMSChannelProps = {"applicationId": application_id}

        if enabled is not None:
            props["enabled"] = enabled

        if sender_id is not None:
            props["senderId"] = sender_id

        if short_code is not None:
            props["shortCode"] = short_code

        jsii.create(CfnSMSChannel, self, [scope, id, props])

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
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> str:
        """``AWS::Pinpoint::SMSChannel.ApplicationId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-smschannel.html#cfn-pinpoint-smschannel-applicationid
        Stability:
            stable
        """
        return jsii.get(self, "applicationId")

    @application_id.setter
    def application_id(self, value: str):
        return jsii.set(self, "applicationId", value)

    @property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::SMSChannel.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-smschannel.html#cfn-pinpoint-smschannel-enabled
        Stability:
            stable
        """
        return jsii.get(self, "enabled")

    @enabled.setter
    def enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "enabled", value)

    @property
    @jsii.member(jsii_name="senderId")
    def sender_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::SMSChannel.SenderId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-smschannel.html#cfn-pinpoint-smschannel-senderid
        Stability:
            stable
        """
        return jsii.get(self, "senderId")

    @sender_id.setter
    def sender_id(self, value: typing.Optional[str]):
        return jsii.set(self, "senderId", value)

    @property
    @jsii.member(jsii_name="shortCode")
    def short_code(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::SMSChannel.ShortCode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-smschannel.html#cfn-pinpoint-smschannel-shortcode
        Stability:
            stable
        """
        return jsii.get(self, "shortCode")

    @short_code.setter
    def short_code(self, value: typing.Optional[str]):
        return jsii.set(self, "shortCode", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnSMSChannelProps(jsii.compat.TypedDict, total=False):
    enabled: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::Pinpoint::SMSChannel.Enabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-smschannel.html#cfn-pinpoint-smschannel-enabled
    Stability:
        stable
    """
    senderId: str
    """``AWS::Pinpoint::SMSChannel.SenderId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-smschannel.html#cfn-pinpoint-smschannel-senderid
    Stability:
        stable
    """
    shortCode: str
    """``AWS::Pinpoint::SMSChannel.ShortCode``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-smschannel.html#cfn-pinpoint-smschannel-shortcode
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnSMSChannelProps", jsii_struct_bases=[_CfnSMSChannelProps])
class CfnSMSChannelProps(_CfnSMSChannelProps):
    """Properties for defining a ``AWS::Pinpoint::SMSChannel``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-smschannel.html
    Stability:
        stable
    """
    applicationId: str
    """``AWS::Pinpoint::SMSChannel.ApplicationId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-smschannel.html#cfn-pinpoint-smschannel-applicationid
    Stability:
        stable
    """

class CfnSegment(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpoint.CfnSegment"):
    """A CloudFormation ``AWS::Pinpoint::Segment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-segment.html
    Stability:
        stable
    cloudformationResource:
        AWS::Pinpoint::Segment
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application_id: str, name: str, dimensions: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SegmentDimensionsProperty"]]]=None, segment_groups: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SegmentGroupsProperty"]]]=None) -> None:
        """Create a new ``AWS::Pinpoint::Segment``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            application_id: ``AWS::Pinpoint::Segment.ApplicationId``.
            name: ``AWS::Pinpoint::Segment.Name``.
            dimensions: ``AWS::Pinpoint::Segment.Dimensions``.
            segment_groups: ``AWS::Pinpoint::Segment.SegmentGroups``.

        Stability:
            experimental
        """
        props: CfnSegmentProps = {"applicationId": application_id, "name": name}

        if dimensions is not None:
            props["dimensions"] = dimensions

        if segment_groups is not None:
            props["segmentGroups"] = segment_groups

        jsii.create(CfnSegment, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrSegmentId")
    def attr_segment_id(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            SegmentId
        """
        return jsii.get(self, "attrSegmentId")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> str:
        """``AWS::Pinpoint::Segment.ApplicationId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-segment.html#cfn-pinpoint-segment-applicationid
        Stability:
            stable
        """
        return jsii.get(self, "applicationId")

    @application_id.setter
    def application_id(self, value: str):
        return jsii.set(self, "applicationId", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::Pinpoint::Segment.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-segment.html#cfn-pinpoint-segment-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="dimensions")
    def dimensions(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SegmentDimensionsProperty"]]]:
        """``AWS::Pinpoint::Segment.Dimensions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-segment.html#cfn-pinpoint-segment-dimensions
        Stability:
            stable
        """
        return jsii.get(self, "dimensions")

    @dimensions.setter
    def dimensions(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SegmentDimensionsProperty"]]]):
        return jsii.set(self, "dimensions", value)

    @property
    @jsii.member(jsii_name="segmentGroups")
    def segment_groups(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SegmentGroupsProperty"]]]:
        """``AWS::Pinpoint::Segment.SegmentGroups``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-segment.html#cfn-pinpoint-segment-segmentgroups
        Stability:
            stable
        """
        return jsii.get(self, "segmentGroups")

    @segment_groups.setter
    def segment_groups(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SegmentGroupsProperty"]]]):
        return jsii.set(self, "segmentGroups", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnSegment.AttributeDimensionProperty", jsii_struct_bases=[])
    class AttributeDimensionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-attributedimension.html
        Stability:
            stable
        """
        attributeType: str
        """``CfnSegment.AttributeDimensionProperty.AttributeType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-attributedimension.html#cfn-pinpoint-segment-attributedimension-attributetype
        Stability:
            stable
        """

        values: typing.List[str]
        """``CfnSegment.AttributeDimensionProperty.Values``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-attributedimension.html#cfn-pinpoint-segment-attributedimension-values
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnSegment.BehaviorProperty", jsii_struct_bases=[])
    class BehaviorProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-behavior.html
        Stability:
            stable
        """
        recency: typing.Union[aws_cdk.core.IResolvable, "CfnSegment.RecencyProperty"]
        """``CfnSegment.BehaviorProperty.Recency``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-behavior.html#cfn-pinpoint-segment-segmentdimensions-behavior-recency
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnSegment.CoordinatesProperty", jsii_struct_bases=[])
    class CoordinatesProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-location-gpspoint-coordinates.html
        Stability:
            stable
        """
        latitude: jsii.Number
        """``CfnSegment.CoordinatesProperty.Latitude``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-location-gpspoint-coordinates.html#cfn-pinpoint-segment-segmentdimensions-location-gpspoint-coordinates-latitude
        Stability:
            stable
        """

        longitude: jsii.Number
        """``CfnSegment.CoordinatesProperty.Longitude``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-location-gpspoint-coordinates.html#cfn-pinpoint-segment-segmentdimensions-location-gpspoint-coordinates-longitude
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnSegment.DemographicProperty", jsii_struct_bases=[])
    class DemographicProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-demographic.html
        Stability:
            stable
        """
        appVersion: typing.Union[aws_cdk.core.IResolvable, "CfnSegment.SetDimensionProperty"]
        """``CfnSegment.DemographicProperty.AppVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-demographic.html#cfn-pinpoint-segment-segmentdimensions-demographic-appversion
        Stability:
            stable
        """

        channel: typing.Union[aws_cdk.core.IResolvable, "CfnSegment.SetDimensionProperty"]
        """``CfnSegment.DemographicProperty.Channel``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-demographic.html#cfn-pinpoint-segment-segmentdimensions-demographic-channel
        Stability:
            stable
        """

        deviceType: typing.Union[aws_cdk.core.IResolvable, "CfnSegment.SetDimensionProperty"]
        """``CfnSegment.DemographicProperty.DeviceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-demographic.html#cfn-pinpoint-segment-segmentdimensions-demographic-devicetype
        Stability:
            stable
        """

        make: typing.Union[aws_cdk.core.IResolvable, "CfnSegment.SetDimensionProperty"]
        """``CfnSegment.DemographicProperty.Make``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-demographic.html#cfn-pinpoint-segment-segmentdimensions-demographic-make
        Stability:
            stable
        """

        model: typing.Union[aws_cdk.core.IResolvable, "CfnSegment.SetDimensionProperty"]
        """``CfnSegment.DemographicProperty.Model``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-demographic.html#cfn-pinpoint-segment-segmentdimensions-demographic-model
        Stability:
            stable
        """

        platform: typing.Union[aws_cdk.core.IResolvable, "CfnSegment.SetDimensionProperty"]
        """``CfnSegment.DemographicProperty.Platform``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-demographic.html#cfn-pinpoint-segment-segmentdimensions-demographic-platform
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnSegment.GPSPointProperty", jsii_struct_bases=[])
    class GPSPointProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-location-gpspoint.html
        Stability:
            stable
        """
        coordinates: typing.Union[aws_cdk.core.IResolvable, "CfnSegment.CoordinatesProperty"]
        """``CfnSegment.GPSPointProperty.Coordinates``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-location-gpspoint.html#cfn-pinpoint-segment-segmentdimensions-location-gpspoint-coordinates
        Stability:
            stable
        """

        rangeInKilometers: jsii.Number
        """``CfnSegment.GPSPointProperty.RangeInKilometers``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-location-gpspoint.html#cfn-pinpoint-segment-segmentdimensions-location-gpspoint-rangeinkilometers
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnSegment.GroupsProperty", jsii_struct_bases=[])
    class GroupsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentgroups-groups.html
        Stability:
            stable
        """
        dimensions: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSegment.SegmentDimensionsProperty"]]]
        """``CfnSegment.GroupsProperty.Dimensions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentgroups-groups.html#cfn-pinpoint-segment-segmentgroups-groups-dimensions
        Stability:
            stable
        """

        sourceSegments: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSegment.SourceSegmentsProperty"]]]
        """``CfnSegment.GroupsProperty.SourceSegments``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentgroups-groups.html#cfn-pinpoint-segment-segmentgroups-groups-sourcesegments
        Stability:
            stable
        """

        sourceType: str
        """``CfnSegment.GroupsProperty.SourceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentgroups-groups.html#cfn-pinpoint-segment-segmentgroups-groups-sourcetype
        Stability:
            stable
        """

        type: str
        """``CfnSegment.GroupsProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentgroups-groups.html#cfn-pinpoint-segment-segmentgroups-groups-type
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnSegment.LocationProperty", jsii_struct_bases=[])
    class LocationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-location.html
        Stability:
            stable
        """
        country: typing.Union[aws_cdk.core.IResolvable, "CfnSegment.SetDimensionProperty"]
        """``CfnSegment.LocationProperty.Country``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-location.html#cfn-pinpoint-segment-segmentdimensions-location-country
        Stability:
            stable
        """

        gpsPoint: typing.Union[aws_cdk.core.IResolvable, "CfnSegment.GPSPointProperty"]
        """``CfnSegment.LocationProperty.GPSPoint``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-location.html#cfn-pinpoint-segment-segmentdimensions-location-gpspoint
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnSegment.RecencyProperty", jsii_struct_bases=[])
    class RecencyProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-behavior-recency.html
        Stability:
            stable
        """
        duration: str
        """``CfnSegment.RecencyProperty.Duration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-behavior-recency.html#cfn-pinpoint-segment-segmentdimensions-behavior-recency-duration
        Stability:
            stable
        """

        recencyType: str
        """``CfnSegment.RecencyProperty.RecencyType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-behavior-recency.html#cfn-pinpoint-segment-segmentdimensions-behavior-recency-recencytype
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnSegment.SegmentDimensionsProperty", jsii_struct_bases=[])
    class SegmentDimensionsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions.html
        Stability:
            stable
        """
        attributes: typing.Any
        """``CfnSegment.SegmentDimensionsProperty.Attributes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions.html#cfn-pinpoint-segment-segmentdimensions-attributes
        Stability:
            stable
        """

        behavior: typing.Union[aws_cdk.core.IResolvable, "CfnSegment.BehaviorProperty"]
        """``CfnSegment.SegmentDimensionsProperty.Behavior``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions.html#cfn-pinpoint-segment-segmentdimensions-behavior
        Stability:
            stable
        """

        demographic: typing.Union[aws_cdk.core.IResolvable, "CfnSegment.DemographicProperty"]
        """``CfnSegment.SegmentDimensionsProperty.Demographic``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions.html#cfn-pinpoint-segment-segmentdimensions-demographic
        Stability:
            stable
        """

        location: typing.Union[aws_cdk.core.IResolvable, "CfnSegment.LocationProperty"]
        """``CfnSegment.SegmentDimensionsProperty.Location``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions.html#cfn-pinpoint-segment-segmentdimensions-location
        Stability:
            stable
        """

        metrics: typing.Any
        """``CfnSegment.SegmentDimensionsProperty.Metrics``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions.html#cfn-pinpoint-segment-segmentdimensions-metrics
        Stability:
            stable
        """

        userAttributes: typing.Any
        """``CfnSegment.SegmentDimensionsProperty.UserAttributes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions.html#cfn-pinpoint-segment-segmentdimensions-userattributes
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnSegment.SegmentGroupsProperty", jsii_struct_bases=[])
    class SegmentGroupsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentgroups.html
        Stability:
            stable
        """
        groups: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSegment.GroupsProperty"]]]
        """``CfnSegment.SegmentGroupsProperty.Groups``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentgroups.html#cfn-pinpoint-segment-segmentgroups-groups
        Stability:
            stable
        """

        include: str
        """``CfnSegment.SegmentGroupsProperty.Include``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentgroups.html#cfn-pinpoint-segment-segmentgroups-include
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnSegment.SetDimensionProperty", jsii_struct_bases=[])
    class SetDimensionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-setdimension.html
        Stability:
            stable
        """
        dimensionType: str
        """``CfnSegment.SetDimensionProperty.DimensionType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-setdimension.html#cfn-pinpoint-segment-setdimension-dimensiontype
        Stability:
            stable
        """

        values: typing.List[str]
        """``CfnSegment.SetDimensionProperty.Values``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-setdimension.html#cfn-pinpoint-segment-setdimension-values
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _SourceSegmentsProperty(jsii.compat.TypedDict, total=False):
        version: jsii.Number
        """``CfnSegment.SourceSegmentsProperty.Version``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentgroups-groups-sourcesegments.html#cfn-pinpoint-segment-segmentgroups-groups-sourcesegments-version
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnSegment.SourceSegmentsProperty", jsii_struct_bases=[_SourceSegmentsProperty])
    class SourceSegmentsProperty(_SourceSegmentsProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentgroups-groups-sourcesegments.html
        Stability:
            stable
        """
        id: str
        """``CfnSegment.SourceSegmentsProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentgroups-groups-sourcesegments.html#cfn-pinpoint-segment-segmentgroups-groups-sourcesegments-id
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnSegmentProps(jsii.compat.TypedDict, total=False):
    dimensions: typing.Union[aws_cdk.core.IResolvable, "CfnSegment.SegmentDimensionsProperty"]
    """``AWS::Pinpoint::Segment.Dimensions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-segment.html#cfn-pinpoint-segment-dimensions
    Stability:
        stable
    """
    segmentGroups: typing.Union[aws_cdk.core.IResolvable, "CfnSegment.SegmentGroupsProperty"]
    """``AWS::Pinpoint::Segment.SegmentGroups``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-segment.html#cfn-pinpoint-segment-segmentgroups
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnSegmentProps", jsii_struct_bases=[_CfnSegmentProps])
class CfnSegmentProps(_CfnSegmentProps):
    """Properties for defining a ``AWS::Pinpoint::Segment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-segment.html
    Stability:
        stable
    """
    applicationId: str
    """``AWS::Pinpoint::Segment.ApplicationId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-segment.html#cfn-pinpoint-segment-applicationid
    Stability:
        stable
    """

    name: str
    """``AWS::Pinpoint::Segment.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-segment.html#cfn-pinpoint-segment-name
    Stability:
        stable
    """

class CfnVoiceChannel(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpoint.CfnVoiceChannel"):
    """A CloudFormation ``AWS::Pinpoint::VoiceChannel``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-voicechannel.html
    Stability:
        stable
    cloudformationResource:
        AWS::Pinpoint::VoiceChannel
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application_id: str, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None) -> None:
        """Create a new ``AWS::Pinpoint::VoiceChannel``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            application_id: ``AWS::Pinpoint::VoiceChannel.ApplicationId``.
            enabled: ``AWS::Pinpoint::VoiceChannel.Enabled``.

        Stability:
            experimental
        """
        props: CfnVoiceChannelProps = {"applicationId": application_id}

        if enabled is not None:
            props["enabled"] = enabled

        jsii.create(CfnVoiceChannel, self, [scope, id, props])

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
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> str:
        """``AWS::Pinpoint::VoiceChannel.ApplicationId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-voicechannel.html#cfn-pinpoint-voicechannel-applicationid
        Stability:
            stable
        """
        return jsii.get(self, "applicationId")

    @application_id.setter
    def application_id(self, value: str):
        return jsii.set(self, "applicationId", value)

    @property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::VoiceChannel.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-voicechannel.html#cfn-pinpoint-voicechannel-enabled
        Stability:
            stable
        """
        return jsii.get(self, "enabled")

    @enabled.setter
    def enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "enabled", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnVoiceChannelProps(jsii.compat.TypedDict, total=False):
    enabled: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::Pinpoint::VoiceChannel.Enabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-voicechannel.html#cfn-pinpoint-voicechannel-enabled
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnVoiceChannelProps", jsii_struct_bases=[_CfnVoiceChannelProps])
class CfnVoiceChannelProps(_CfnVoiceChannelProps):
    """Properties for defining a ``AWS::Pinpoint::VoiceChannel``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-voicechannel.html
    Stability:
        stable
    """
    applicationId: str
    """``AWS::Pinpoint::VoiceChannel.ApplicationId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-voicechannel.html#cfn-pinpoint-voicechannel-applicationid
    Stability:
        stable
    """

__all__ = ["CfnADMChannel", "CfnADMChannelProps", "CfnAPNSChannel", "CfnAPNSChannelProps", "CfnAPNSSandboxChannel", "CfnAPNSSandboxChannelProps", "CfnAPNSVoipChannel", "CfnAPNSVoipChannelProps", "CfnAPNSVoipSandboxChannel", "CfnAPNSVoipSandboxChannelProps", "CfnApp", "CfnAppProps", "CfnApplicationSettings", "CfnApplicationSettingsProps", "CfnBaiduChannel", "CfnBaiduChannelProps", "CfnCampaign", "CfnCampaignProps", "CfnEmailChannel", "CfnEmailChannelProps", "CfnEventStream", "CfnEventStreamProps", "CfnGCMChannel", "CfnGCMChannelProps", "CfnSMSChannel", "CfnSMSChannelProps", "CfnSegment", "CfnSegmentProps", "CfnVoiceChannel", "CfnVoiceChannelProps", "__jsii_assembly__"]

publication.publish()
