import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_iam
import aws_cdk.aws_lambda
import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-cognito", "0.35.0", __name__, "aws-cognito@0.35.0.jsii.tgz")
@jsii.enum(jsii_type="@aws-cdk/aws-cognito.AuthFlow")
class AuthFlow(enum.Enum):
    """Types of authentication flow.

    Stability:
        experimental
    """
    AdminNoSrp = "AdminNoSrp"
    """Enable flow for server-side or admin authentication (no client app).

    Stability:
        experimental
    """
    CustomFlowOnly = "CustomFlowOnly"
    """Enable custom authentication flow.

    Stability:
        experimental
    """
    UserPassword = "UserPassword"
    """Enable auth using username & password.

    Stability:
        experimental
    """

class CfnIdentityPool(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-cognito.CfnIdentityPool"):
    """A CloudFormation ``AWS::Cognito::IdentityPool``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-identitypool.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Cognito::IdentityPool
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, allow_unauthenticated_identities: typing.Union[bool, aws_cdk.cdk.IResolvable], cognito_events: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, cognito_identity_providers: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CognitoIdentityProviderProperty"]]]]]=None, cognito_streams: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["CognitoStreamsProperty"]]]=None, developer_provider_name: typing.Optional[str]=None, identity_pool_name: typing.Optional[str]=None, open_id_connect_provider_arns: typing.Optional[typing.List[str]]=None, push_sync: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["PushSyncProperty"]]]=None, saml_provider_arns: typing.Optional[typing.List[str]]=None, supported_login_providers: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.IResolvable]]]=None) -> None:
        """Create a new ``AWS::Cognito::IdentityPool``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            allowUnauthenticatedIdentities: ``AWS::Cognito::IdentityPool.AllowUnauthenticatedIdentities``.
            cognitoEvents: ``AWS::Cognito::IdentityPool.CognitoEvents``.
            cognitoIdentityProviders: ``AWS::Cognito::IdentityPool.CognitoIdentityProviders``.
            cognitoStreams: ``AWS::Cognito::IdentityPool.CognitoStreams``.
            developerProviderName: ``AWS::Cognito::IdentityPool.DeveloperProviderName``.
            identityPoolName: ``AWS::Cognito::IdentityPool.IdentityPoolName``.
            openIdConnectProviderArns: ``AWS::Cognito::IdentityPool.OpenIdConnectProviderARNs``.
            pushSync: ``AWS::Cognito::IdentityPool.PushSync``.
            samlProviderArns: ``AWS::Cognito::IdentityPool.SamlProviderARNs``.
            supportedLoginProviders: ``AWS::Cognito::IdentityPool.SupportedLoginProviders``.

        Stability:
            experimental
        """
        props: CfnIdentityPoolProps = {"allowUnauthenticatedIdentities": allow_unauthenticated_identities}

        if cognito_events is not None:
            props["cognitoEvents"] = cognito_events

        if cognito_identity_providers is not None:
            props["cognitoIdentityProviders"] = cognito_identity_providers

        if cognito_streams is not None:
            props["cognitoStreams"] = cognito_streams

        if developer_provider_name is not None:
            props["developerProviderName"] = developer_provider_name

        if identity_pool_name is not None:
            props["identityPoolName"] = identity_pool_name

        if open_id_connect_provider_arns is not None:
            props["openIdConnectProviderArns"] = open_id_connect_provider_arns

        if push_sync is not None:
            props["pushSync"] = push_sync

        if saml_provider_arns is not None:
            props["samlProviderArns"] = saml_provider_arns

        if supported_login_providers is not None:
            props["supportedLoginProviders"] = supported_login_providers

        jsii.create(CfnIdentityPool, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Name
        """
        return jsii.get(self, "attrName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="allowUnauthenticatedIdentities")
    def allow_unauthenticated_identities(self) -> typing.Union[bool, aws_cdk.cdk.IResolvable]:
        """``AWS::Cognito::IdentityPool.AllowUnauthenticatedIdentities``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-identitypool.html#cfn-cognito-identitypool-allowunauthenticatedidentities
        Stability:
            experimental
        """
        return jsii.get(self, "allowUnauthenticatedIdentities")

    @allow_unauthenticated_identities.setter
    def allow_unauthenticated_identities(self, value: typing.Union[bool, aws_cdk.cdk.IResolvable]):
        return jsii.set(self, "allowUnauthenticatedIdentities", value)

    @property
    @jsii.member(jsii_name="cognitoEvents")
    def cognito_events(self) -> typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::Cognito::IdentityPool.CognitoEvents``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-identitypool.html#cfn-cognito-identitypool-cognitoevents
        Stability:
            experimental
        """
        return jsii.get(self, "cognitoEvents")

    @cognito_events.setter
    def cognito_events(self, value: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "cognitoEvents", value)

    @property
    @jsii.member(jsii_name="cognitoIdentityProviders")
    def cognito_identity_providers(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CognitoIdentityProviderProperty"]]]]]:
        """``AWS::Cognito::IdentityPool.CognitoIdentityProviders``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-identitypool.html#cfn-cognito-identitypool-cognitoidentityproviders
        Stability:
            experimental
        """
        return jsii.get(self, "cognitoIdentityProviders")

    @cognito_identity_providers.setter
    def cognito_identity_providers(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CognitoIdentityProviderProperty"]]]]]):
        return jsii.set(self, "cognitoIdentityProviders", value)

    @property
    @jsii.member(jsii_name="cognitoStreams")
    def cognito_streams(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["CognitoStreamsProperty"]]]:
        """``AWS::Cognito::IdentityPool.CognitoStreams``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-identitypool.html#cfn-cognito-identitypool-cognitostreams
        Stability:
            experimental
        """
        return jsii.get(self, "cognitoStreams")

    @cognito_streams.setter
    def cognito_streams(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["CognitoStreamsProperty"]]]):
        return jsii.set(self, "cognitoStreams", value)

    @property
    @jsii.member(jsii_name="developerProviderName")
    def developer_provider_name(self) -> typing.Optional[str]:
        """``AWS::Cognito::IdentityPool.DeveloperProviderName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-identitypool.html#cfn-cognito-identitypool-developerprovidername
        Stability:
            experimental
        """
        return jsii.get(self, "developerProviderName")

    @developer_provider_name.setter
    def developer_provider_name(self, value: typing.Optional[str]):
        return jsii.set(self, "developerProviderName", value)

    @property
    @jsii.member(jsii_name="identityPoolName")
    def identity_pool_name(self) -> typing.Optional[str]:
        """``AWS::Cognito::IdentityPool.IdentityPoolName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-identitypool.html#cfn-cognito-identitypool-identitypoolname
        Stability:
            experimental
        """
        return jsii.get(self, "identityPoolName")

    @identity_pool_name.setter
    def identity_pool_name(self, value: typing.Optional[str]):
        return jsii.set(self, "identityPoolName", value)

    @property
    @jsii.member(jsii_name="openIdConnectProviderArns")
    def open_id_connect_provider_arns(self) -> typing.Optional[typing.List[str]]:
        """``AWS::Cognito::IdentityPool.OpenIdConnectProviderARNs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-identitypool.html#cfn-cognito-identitypool-openidconnectproviderarns
        Stability:
            experimental
        """
        return jsii.get(self, "openIdConnectProviderArns")

    @open_id_connect_provider_arns.setter
    def open_id_connect_provider_arns(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "openIdConnectProviderArns", value)

    @property
    @jsii.member(jsii_name="pushSync")
    def push_sync(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["PushSyncProperty"]]]:
        """``AWS::Cognito::IdentityPool.PushSync``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-identitypool.html#cfn-cognito-identitypool-pushsync
        Stability:
            experimental
        """
        return jsii.get(self, "pushSync")

    @push_sync.setter
    def push_sync(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["PushSyncProperty"]]]):
        return jsii.set(self, "pushSync", value)

    @property
    @jsii.member(jsii_name="samlProviderArns")
    def saml_provider_arns(self) -> typing.Optional[typing.List[str]]:
        """``AWS::Cognito::IdentityPool.SamlProviderARNs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-identitypool.html#cfn-cognito-identitypool-samlproviderarns
        Stability:
            experimental
        """
        return jsii.get(self, "samlProviderArns")

    @saml_provider_arns.setter
    def saml_provider_arns(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "samlProviderArns", value)

    @property
    @jsii.member(jsii_name="supportedLoginProviders")
    def supported_login_providers(self) -> typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::Cognito::IdentityPool.SupportedLoginProviders``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-identitypool.html#cfn-cognito-identitypool-supportedloginproviders
        Stability:
            experimental
        """
        return jsii.get(self, "supportedLoginProviders")

    @supported_login_providers.setter
    def supported_login_providers(self, value: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "supportedLoginProviders", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-cognito.CfnIdentityPool.CognitoIdentityProviderProperty", jsii_struct_bases=[])
    class CognitoIdentityProviderProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-identitypool-cognitoidentityprovider.html
        Stability:
            experimental
        """
        clientId: str
        """``CfnIdentityPool.CognitoIdentityProviderProperty.ClientId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-identitypool-cognitoidentityprovider.html#cfn-cognito-identitypool-cognitoidentityprovider-clientid
        Stability:
            experimental
        """

        providerName: str
        """``CfnIdentityPool.CognitoIdentityProviderProperty.ProviderName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-identitypool-cognitoidentityprovider.html#cfn-cognito-identitypool-cognitoidentityprovider-providername
        Stability:
            experimental
        """

        serverSideTokenCheck: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnIdentityPool.CognitoIdentityProviderProperty.ServerSideTokenCheck``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-identitypool-cognitoidentityprovider.html#cfn-cognito-identitypool-cognitoidentityprovider-serversidetokencheck
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-cognito.CfnIdentityPool.CognitoStreamsProperty", jsii_struct_bases=[])
    class CognitoStreamsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-identitypool-cognitostreams.html
        Stability:
            experimental
        """
        roleArn: str
        """``CfnIdentityPool.CognitoStreamsProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-identitypool-cognitostreams.html#cfn-cognito-identitypool-cognitostreams-rolearn
        Stability:
            experimental
        """

        streamingStatus: str
        """``CfnIdentityPool.CognitoStreamsProperty.StreamingStatus``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-identitypool-cognitostreams.html#cfn-cognito-identitypool-cognitostreams-streamingstatus
        Stability:
            experimental
        """

        streamName: str
        """``CfnIdentityPool.CognitoStreamsProperty.StreamName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-identitypool-cognitostreams.html#cfn-cognito-identitypool-cognitostreams-streamname
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-cognito.CfnIdentityPool.PushSyncProperty", jsii_struct_bases=[])
    class PushSyncProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-identitypool-pushsync.html
        Stability:
            experimental
        """
        applicationArns: typing.List[str]
        """``CfnIdentityPool.PushSyncProperty.ApplicationArns``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-identitypool-pushsync.html#cfn-cognito-identitypool-pushsync-applicationarns
        Stability:
            experimental
        """

        roleArn: str
        """``CfnIdentityPool.PushSyncProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-identitypool-pushsync.html#cfn-cognito-identitypool-pushsync-rolearn
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnIdentityPoolProps(jsii.compat.TypedDict, total=False):
    cognitoEvents: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.IResolvable]
    """``AWS::Cognito::IdentityPool.CognitoEvents``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-identitypool.html#cfn-cognito-identitypool-cognitoevents
    Stability:
        experimental
    """
    cognitoIdentityProviders: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnIdentityPool.CognitoIdentityProviderProperty"]]]
    """``AWS::Cognito::IdentityPool.CognitoIdentityProviders``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-identitypool.html#cfn-cognito-identitypool-cognitoidentityproviders
    Stability:
        experimental
    """
    cognitoStreams: typing.Union[aws_cdk.cdk.IResolvable, "CfnIdentityPool.CognitoStreamsProperty"]
    """``AWS::Cognito::IdentityPool.CognitoStreams``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-identitypool.html#cfn-cognito-identitypool-cognitostreams
    Stability:
        experimental
    """
    developerProviderName: str
    """``AWS::Cognito::IdentityPool.DeveloperProviderName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-identitypool.html#cfn-cognito-identitypool-developerprovidername
    Stability:
        experimental
    """
    identityPoolName: str
    """``AWS::Cognito::IdentityPool.IdentityPoolName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-identitypool.html#cfn-cognito-identitypool-identitypoolname
    Stability:
        experimental
    """
    openIdConnectProviderArns: typing.List[str]
    """``AWS::Cognito::IdentityPool.OpenIdConnectProviderARNs``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-identitypool.html#cfn-cognito-identitypool-openidconnectproviderarns
    Stability:
        experimental
    """
    pushSync: typing.Union[aws_cdk.cdk.IResolvable, "CfnIdentityPool.PushSyncProperty"]
    """``AWS::Cognito::IdentityPool.PushSync``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-identitypool.html#cfn-cognito-identitypool-pushsync
    Stability:
        experimental
    """
    samlProviderArns: typing.List[str]
    """``AWS::Cognito::IdentityPool.SamlProviderARNs``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-identitypool.html#cfn-cognito-identitypool-samlproviderarns
    Stability:
        experimental
    """
    supportedLoginProviders: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.IResolvable]
    """``AWS::Cognito::IdentityPool.SupportedLoginProviders``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-identitypool.html#cfn-cognito-identitypool-supportedloginproviders
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-cognito.CfnIdentityPoolProps", jsii_struct_bases=[_CfnIdentityPoolProps])
class CfnIdentityPoolProps(_CfnIdentityPoolProps):
    """Properties for defining a ``AWS::Cognito::IdentityPool``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-identitypool.html
    Stability:
        experimental
    """
    allowUnauthenticatedIdentities: typing.Union[bool, aws_cdk.cdk.IResolvable]
    """``AWS::Cognito::IdentityPool.AllowUnauthenticatedIdentities``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-identitypool.html#cfn-cognito-identitypool-allowunauthenticatedidentities
    Stability:
        experimental
    """

class CfnIdentityPoolRoleAttachment(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-cognito.CfnIdentityPoolRoleAttachment"):
    """A CloudFormation ``AWS::Cognito::IdentityPoolRoleAttachment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-identitypoolroleattachment.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Cognito::IdentityPoolRoleAttachment
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, identity_pool_id: str, role_mappings: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.Mapping[str,typing.Union[aws_cdk.cdk.IResolvable, "RoleMappingProperty"]]]]]=None, roles: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.IResolvable]]]=None) -> None:
        """Create a new ``AWS::Cognito::IdentityPoolRoleAttachment``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            identityPoolId: ``AWS::Cognito::IdentityPoolRoleAttachment.IdentityPoolId``.
            roleMappings: ``AWS::Cognito::IdentityPoolRoleAttachment.RoleMappings``.
            roles: ``AWS::Cognito::IdentityPoolRoleAttachment.Roles``.

        Stability:
            experimental
        """
        props: CfnIdentityPoolRoleAttachmentProps = {"identityPoolId": identity_pool_id}

        if role_mappings is not None:
            props["roleMappings"] = role_mappings

        if roles is not None:
            props["roles"] = roles

        jsii.create(CfnIdentityPoolRoleAttachment, self, [scope, id, props])

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
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="identityPoolId")
    def identity_pool_id(self) -> str:
        """``AWS::Cognito::IdentityPoolRoleAttachment.IdentityPoolId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-identitypoolroleattachment.html#cfn-cognito-identitypoolroleattachment-identitypoolid
        Stability:
            experimental
        """
        return jsii.get(self, "identityPoolId")

    @identity_pool_id.setter
    def identity_pool_id(self, value: str):
        return jsii.set(self, "identityPoolId", value)

    @property
    @jsii.member(jsii_name="roleMappings")
    def role_mappings(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.Mapping[str,typing.Union[aws_cdk.cdk.IResolvable, "RoleMappingProperty"]]]]]:
        """``AWS::Cognito::IdentityPoolRoleAttachment.RoleMappings``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-identitypoolroleattachment.html#cfn-cognito-identitypoolroleattachment-rolemappings
        Stability:
            experimental
        """
        return jsii.get(self, "roleMappings")

    @role_mappings.setter
    def role_mappings(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.Mapping[str,typing.Union[aws_cdk.cdk.IResolvable, "RoleMappingProperty"]]]]]):
        return jsii.set(self, "roleMappings", value)

    @property
    @jsii.member(jsii_name="roles")
    def roles(self) -> typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::Cognito::IdentityPoolRoleAttachment.Roles``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-identitypoolroleattachment.html#cfn-cognito-identitypoolroleattachment-roles
        Stability:
            experimental
        """
        return jsii.get(self, "roles")

    @roles.setter
    def roles(self, value: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "roles", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-cognito.CfnIdentityPoolRoleAttachment.MappingRuleProperty", jsii_struct_bases=[])
    class MappingRuleProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-identitypoolroleattachment-mappingrule.html
        Stability:
            experimental
        """
        claim: str
        """``CfnIdentityPoolRoleAttachment.MappingRuleProperty.Claim``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-identitypoolroleattachment-mappingrule.html#cfn-cognito-identitypoolroleattachment-mappingrule-claim
        Stability:
            experimental
        """

        matchType: str
        """``CfnIdentityPoolRoleAttachment.MappingRuleProperty.MatchType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-identitypoolroleattachment-mappingrule.html#cfn-cognito-identitypoolroleattachment-mappingrule-matchtype
        Stability:
            experimental
        """

        roleArn: str
        """``CfnIdentityPoolRoleAttachment.MappingRuleProperty.RoleARN``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-identitypoolroleattachment-mappingrule.html#cfn-cognito-identitypoolroleattachment-mappingrule-rolearn
        Stability:
            experimental
        """

        value: str
        """``CfnIdentityPoolRoleAttachment.MappingRuleProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-identitypoolroleattachment-mappingrule.html#cfn-cognito-identitypoolroleattachment-mappingrule-value
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _RoleMappingProperty(jsii.compat.TypedDict, total=False):
        ambiguousRoleResolution: str
        """``CfnIdentityPoolRoleAttachment.RoleMappingProperty.AmbiguousRoleResolution``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-identitypoolroleattachment-rolemapping.html#cfn-cognito-identitypoolroleattachment-rolemapping-ambiguousroleresolution
        Stability:
            experimental
        """
        rulesConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnIdentityPoolRoleAttachment.RulesConfigurationTypeProperty"]
        """``CfnIdentityPoolRoleAttachment.RoleMappingProperty.RulesConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-identitypoolroleattachment-rolemapping.html#cfn-cognito-identitypoolroleattachment-rolemapping-rulesconfiguration
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-cognito.CfnIdentityPoolRoleAttachment.RoleMappingProperty", jsii_struct_bases=[_RoleMappingProperty])
    class RoleMappingProperty(_RoleMappingProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-identitypoolroleattachment-rolemapping.html
        Stability:
            experimental
        """
        type: str
        """``CfnIdentityPoolRoleAttachment.RoleMappingProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-identitypoolroleattachment-rolemapping.html#cfn-cognito-identitypoolroleattachment-rolemapping-type
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-cognito.CfnIdentityPoolRoleAttachment.RulesConfigurationTypeProperty", jsii_struct_bases=[])
    class RulesConfigurationTypeProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-identitypoolroleattachment-rulesconfigurationtype.html
        Stability:
            experimental
        """
        rules: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnIdentityPoolRoleAttachment.MappingRuleProperty"]]]
        """``CfnIdentityPoolRoleAttachment.RulesConfigurationTypeProperty.Rules``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-identitypoolroleattachment-rulesconfigurationtype.html#cfn-cognito-identitypoolroleattachment-rulesconfigurationtype-rules
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnIdentityPoolRoleAttachmentProps(jsii.compat.TypedDict, total=False):
    roleMappings: typing.Union[aws_cdk.cdk.IResolvable, typing.Mapping[str,typing.Union[aws_cdk.cdk.IResolvable, "CfnIdentityPoolRoleAttachment.RoleMappingProperty"]]]
    """``AWS::Cognito::IdentityPoolRoleAttachment.RoleMappings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-identitypoolroleattachment.html#cfn-cognito-identitypoolroleattachment-rolemappings
    Stability:
        experimental
    """
    roles: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.IResolvable]
    """``AWS::Cognito::IdentityPoolRoleAttachment.Roles``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-identitypoolroleattachment.html#cfn-cognito-identitypoolroleattachment-roles
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-cognito.CfnIdentityPoolRoleAttachmentProps", jsii_struct_bases=[_CfnIdentityPoolRoleAttachmentProps])
class CfnIdentityPoolRoleAttachmentProps(_CfnIdentityPoolRoleAttachmentProps):
    """Properties for defining a ``AWS::Cognito::IdentityPoolRoleAttachment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-identitypoolroleattachment.html
    Stability:
        experimental
    """
    identityPoolId: str
    """``AWS::Cognito::IdentityPoolRoleAttachment.IdentityPoolId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-identitypoolroleattachment.html#cfn-cognito-identitypoolroleattachment-identitypoolid
    Stability:
        experimental
    """

class CfnUserPool(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-cognito.CfnUserPool"):
    """A CloudFormation ``AWS::Cognito::UserPool``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Cognito::UserPool
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, admin_create_user_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["AdminCreateUserConfigProperty"]]]=None, alias_attributes: typing.Optional[typing.List[str]]=None, auto_verified_attributes: typing.Optional[typing.List[str]]=None, device_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["DeviceConfigurationProperty"]]]=None, email_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["EmailConfigurationProperty"]]]=None, email_verification_message: typing.Optional[str]=None, email_verification_subject: typing.Optional[str]=None, lambda_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["LambdaConfigProperty"]]]=None, mfa_configuration: typing.Optional[str]=None, policies: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["PoliciesProperty"]]]=None, schema: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "SchemaAttributeProperty"]]]]]=None, sms_authentication_message: typing.Optional[str]=None, sms_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["SmsConfigurationProperty"]]]=None, sms_verification_message: typing.Optional[str]=None, username_attributes: typing.Optional[typing.List[str]]=None, user_pool_name: typing.Optional[str]=None, user_pool_tags: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.IResolvable]]]=None) -> None:
        """Create a new ``AWS::Cognito::UserPool``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            adminCreateUserConfig: ``AWS::Cognito::UserPool.AdminCreateUserConfig``.
            aliasAttributes: ``AWS::Cognito::UserPool.AliasAttributes``.
            autoVerifiedAttributes: ``AWS::Cognito::UserPool.AutoVerifiedAttributes``.
            deviceConfiguration: ``AWS::Cognito::UserPool.DeviceConfiguration``.
            emailConfiguration: ``AWS::Cognito::UserPool.EmailConfiguration``.
            emailVerificationMessage: ``AWS::Cognito::UserPool.EmailVerificationMessage``.
            emailVerificationSubject: ``AWS::Cognito::UserPool.EmailVerificationSubject``.
            lambdaConfig: ``AWS::Cognito::UserPool.LambdaConfig``.
            mfaConfiguration: ``AWS::Cognito::UserPool.MfaConfiguration``.
            policies: ``AWS::Cognito::UserPool.Policies``.
            schema: ``AWS::Cognito::UserPool.Schema``.
            smsAuthenticationMessage: ``AWS::Cognito::UserPool.SmsAuthenticationMessage``.
            smsConfiguration: ``AWS::Cognito::UserPool.SmsConfiguration``.
            smsVerificationMessage: ``AWS::Cognito::UserPool.SmsVerificationMessage``.
            usernameAttributes: ``AWS::Cognito::UserPool.UsernameAttributes``.
            userPoolName: ``AWS::Cognito::UserPool.UserPoolName``.
            userPoolTags: ``AWS::Cognito::UserPool.UserPoolTags``.

        Stability:
            experimental
        """
        props: CfnUserPoolProps = {}

        if admin_create_user_config is not None:
            props["adminCreateUserConfig"] = admin_create_user_config

        if alias_attributes is not None:
            props["aliasAttributes"] = alias_attributes

        if auto_verified_attributes is not None:
            props["autoVerifiedAttributes"] = auto_verified_attributes

        if device_configuration is not None:
            props["deviceConfiguration"] = device_configuration

        if email_configuration is not None:
            props["emailConfiguration"] = email_configuration

        if email_verification_message is not None:
            props["emailVerificationMessage"] = email_verification_message

        if email_verification_subject is not None:
            props["emailVerificationSubject"] = email_verification_subject

        if lambda_config is not None:
            props["lambdaConfig"] = lambda_config

        if mfa_configuration is not None:
            props["mfaConfiguration"] = mfa_configuration

        if policies is not None:
            props["policies"] = policies

        if schema is not None:
            props["schema"] = schema

        if sms_authentication_message is not None:
            props["smsAuthenticationMessage"] = sms_authentication_message

        if sms_configuration is not None:
            props["smsConfiguration"] = sms_configuration

        if sms_verification_message is not None:
            props["smsVerificationMessage"] = sms_verification_message

        if username_attributes is not None:
            props["usernameAttributes"] = username_attributes

        if user_pool_name is not None:
            props["userPoolName"] = user_pool_name

        if user_pool_tags is not None:
            props["userPoolTags"] = user_pool_tags

        jsii.create(CfnUserPool, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "attrArn")

    @property
    @jsii.member(jsii_name="attrProviderName")
    def attr_provider_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ProviderName
        """
        return jsii.get(self, "attrProviderName")

    @property
    @jsii.member(jsii_name="attrProviderUrl")
    def attr_provider_url(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ProviderURL
        """
        return jsii.get(self, "attrProviderUrl")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="adminCreateUserConfig")
    def admin_create_user_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["AdminCreateUserConfigProperty"]]]:
        """``AWS::Cognito::UserPool.AdminCreateUserConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html#cfn-cognito-userpool-admincreateuserconfig
        Stability:
            experimental
        """
        return jsii.get(self, "adminCreateUserConfig")

    @admin_create_user_config.setter
    def admin_create_user_config(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["AdminCreateUserConfigProperty"]]]):
        return jsii.set(self, "adminCreateUserConfig", value)

    @property
    @jsii.member(jsii_name="aliasAttributes")
    def alias_attributes(self) -> typing.Optional[typing.List[str]]:
        """``AWS::Cognito::UserPool.AliasAttributes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html#cfn-cognito-userpool-aliasattributes
        Stability:
            experimental
        """
        return jsii.get(self, "aliasAttributes")

    @alias_attributes.setter
    def alias_attributes(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "aliasAttributes", value)

    @property
    @jsii.member(jsii_name="autoVerifiedAttributes")
    def auto_verified_attributes(self) -> typing.Optional[typing.List[str]]:
        """``AWS::Cognito::UserPool.AutoVerifiedAttributes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html#cfn-cognito-userpool-autoverifiedattributes
        Stability:
            experimental
        """
        return jsii.get(self, "autoVerifiedAttributes")

    @auto_verified_attributes.setter
    def auto_verified_attributes(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "autoVerifiedAttributes", value)

    @property
    @jsii.member(jsii_name="deviceConfiguration")
    def device_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["DeviceConfigurationProperty"]]]:
        """``AWS::Cognito::UserPool.DeviceConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html#cfn-cognito-userpool-deviceconfiguration
        Stability:
            experimental
        """
        return jsii.get(self, "deviceConfiguration")

    @device_configuration.setter
    def device_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["DeviceConfigurationProperty"]]]):
        return jsii.set(self, "deviceConfiguration", value)

    @property
    @jsii.member(jsii_name="emailConfiguration")
    def email_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["EmailConfigurationProperty"]]]:
        """``AWS::Cognito::UserPool.EmailConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html#cfn-cognito-userpool-emailconfiguration
        Stability:
            experimental
        """
        return jsii.get(self, "emailConfiguration")

    @email_configuration.setter
    def email_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["EmailConfigurationProperty"]]]):
        return jsii.set(self, "emailConfiguration", value)

    @property
    @jsii.member(jsii_name="emailVerificationMessage")
    def email_verification_message(self) -> typing.Optional[str]:
        """``AWS::Cognito::UserPool.EmailVerificationMessage``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html#cfn-cognito-userpool-emailverificationmessage
        Stability:
            experimental
        """
        return jsii.get(self, "emailVerificationMessage")

    @email_verification_message.setter
    def email_verification_message(self, value: typing.Optional[str]):
        return jsii.set(self, "emailVerificationMessage", value)

    @property
    @jsii.member(jsii_name="emailVerificationSubject")
    def email_verification_subject(self) -> typing.Optional[str]:
        """``AWS::Cognito::UserPool.EmailVerificationSubject``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html#cfn-cognito-userpool-emailverificationsubject
        Stability:
            experimental
        """
        return jsii.get(self, "emailVerificationSubject")

    @email_verification_subject.setter
    def email_verification_subject(self, value: typing.Optional[str]):
        return jsii.set(self, "emailVerificationSubject", value)

    @property
    @jsii.member(jsii_name="lambdaConfig")
    def lambda_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["LambdaConfigProperty"]]]:
        """``AWS::Cognito::UserPool.LambdaConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html#cfn-cognito-userpool-lambdaconfig
        Stability:
            experimental
        """
        return jsii.get(self, "lambdaConfig")

    @lambda_config.setter
    def lambda_config(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["LambdaConfigProperty"]]]):
        return jsii.set(self, "lambdaConfig", value)

    @property
    @jsii.member(jsii_name="mfaConfiguration")
    def mfa_configuration(self) -> typing.Optional[str]:
        """``AWS::Cognito::UserPool.MfaConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html#cfn-cognito-userpool-mfaconfiguration
        Stability:
            experimental
        """
        return jsii.get(self, "mfaConfiguration")

    @mfa_configuration.setter
    def mfa_configuration(self, value: typing.Optional[str]):
        return jsii.set(self, "mfaConfiguration", value)

    @property
    @jsii.member(jsii_name="policies")
    def policies(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["PoliciesProperty"]]]:
        """``AWS::Cognito::UserPool.Policies``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html#cfn-cognito-userpool-policies
        Stability:
            experimental
        """
        return jsii.get(self, "policies")

    @policies.setter
    def policies(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["PoliciesProperty"]]]):
        return jsii.set(self, "policies", value)

    @property
    @jsii.member(jsii_name="schema")
    def schema(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "SchemaAttributeProperty"]]]]]:
        """``AWS::Cognito::UserPool.Schema``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html#cfn-cognito-userpool-schema
        Stability:
            experimental
        """
        return jsii.get(self, "schema")

    @schema.setter
    def schema(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "SchemaAttributeProperty"]]]]]):
        return jsii.set(self, "schema", value)

    @property
    @jsii.member(jsii_name="smsAuthenticationMessage")
    def sms_authentication_message(self) -> typing.Optional[str]:
        """``AWS::Cognito::UserPool.SmsAuthenticationMessage``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html#cfn-cognito-userpool-smsauthenticationmessage
        Stability:
            experimental
        """
        return jsii.get(self, "smsAuthenticationMessage")

    @sms_authentication_message.setter
    def sms_authentication_message(self, value: typing.Optional[str]):
        return jsii.set(self, "smsAuthenticationMessage", value)

    @property
    @jsii.member(jsii_name="smsConfiguration")
    def sms_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["SmsConfigurationProperty"]]]:
        """``AWS::Cognito::UserPool.SmsConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html#cfn-cognito-userpool-smsconfiguration
        Stability:
            experimental
        """
        return jsii.get(self, "smsConfiguration")

    @sms_configuration.setter
    def sms_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["SmsConfigurationProperty"]]]):
        return jsii.set(self, "smsConfiguration", value)

    @property
    @jsii.member(jsii_name="smsVerificationMessage")
    def sms_verification_message(self) -> typing.Optional[str]:
        """``AWS::Cognito::UserPool.SmsVerificationMessage``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html#cfn-cognito-userpool-smsverificationmessage
        Stability:
            experimental
        """
        return jsii.get(self, "smsVerificationMessage")

    @sms_verification_message.setter
    def sms_verification_message(self, value: typing.Optional[str]):
        return jsii.set(self, "smsVerificationMessage", value)

    @property
    @jsii.member(jsii_name="usernameAttributes")
    def username_attributes(self) -> typing.Optional[typing.List[str]]:
        """``AWS::Cognito::UserPool.UsernameAttributes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html#cfn-cognito-userpool-usernameattributes
        Stability:
            experimental
        """
        return jsii.get(self, "usernameAttributes")

    @username_attributes.setter
    def username_attributes(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "usernameAttributes", value)

    @property
    @jsii.member(jsii_name="userPoolName")
    def user_pool_name(self) -> typing.Optional[str]:
        """``AWS::Cognito::UserPool.UserPoolName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html#cfn-cognito-userpool-userpoolname
        Stability:
            experimental
        """
        return jsii.get(self, "userPoolName")

    @user_pool_name.setter
    def user_pool_name(self, value: typing.Optional[str]):
        return jsii.set(self, "userPoolName", value)

    @property
    @jsii.member(jsii_name="userPoolTags")
    def user_pool_tags(self) -> typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::Cognito::UserPool.UserPoolTags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html#cfn-cognito-userpool-userpooltags
        Stability:
            experimental
        """
        return jsii.get(self, "userPoolTags")

    @user_pool_tags.setter
    def user_pool_tags(self, value: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "userPoolTags", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-cognito.CfnUserPool.AdminCreateUserConfigProperty", jsii_struct_bases=[])
    class AdminCreateUserConfigProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-admincreateuserconfig.html
        Stability:
            experimental
        """
        allowAdminCreateUserOnly: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnUserPool.AdminCreateUserConfigProperty.AllowAdminCreateUserOnly``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-admincreateuserconfig.html#cfn-cognito-userpool-admincreateuserconfig-allowadmincreateuseronly
        Stability:
            experimental
        """

        inviteMessageTemplate: typing.Union[aws_cdk.cdk.IResolvable, "CfnUserPool.InviteMessageTemplateProperty"]
        """``CfnUserPool.AdminCreateUserConfigProperty.InviteMessageTemplate``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-admincreateuserconfig.html#cfn-cognito-userpool-admincreateuserconfig-invitemessagetemplate
        Stability:
            experimental
        """

        unusedAccountValidityDays: jsii.Number
        """``CfnUserPool.AdminCreateUserConfigProperty.UnusedAccountValidityDays``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-admincreateuserconfig.html#cfn-cognito-userpool-admincreateuserconfig-unusedaccountvaliditydays
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-cognito.CfnUserPool.DeviceConfigurationProperty", jsii_struct_bases=[])
    class DeviceConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-deviceconfiguration.html
        Stability:
            experimental
        """
        challengeRequiredOnNewDevice: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnUserPool.DeviceConfigurationProperty.ChallengeRequiredOnNewDevice``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-deviceconfiguration.html#cfn-cognito-userpool-deviceconfiguration-challengerequiredonnewdevice
        Stability:
            experimental
        """

        deviceOnlyRememberedOnUserPrompt: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnUserPool.DeviceConfigurationProperty.DeviceOnlyRememberedOnUserPrompt``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-deviceconfiguration.html#cfn-cognito-userpool-deviceconfiguration-deviceonlyrememberedonuserprompt
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-cognito.CfnUserPool.EmailConfigurationProperty", jsii_struct_bases=[])
    class EmailConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-emailconfiguration.html
        Stability:
            experimental
        """
        emailSendingAccount: str
        """``CfnUserPool.EmailConfigurationProperty.EmailSendingAccount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-emailconfiguration.html#cfn-cognito-userpool-emailconfiguration-emailsendingaccount
        Stability:
            experimental
        """

        replyToEmailAddress: str
        """``CfnUserPool.EmailConfigurationProperty.ReplyToEmailAddress``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-emailconfiguration.html#cfn-cognito-userpool-emailconfiguration-replytoemailaddress
        Stability:
            experimental
        """

        sourceArn: str
        """``CfnUserPool.EmailConfigurationProperty.SourceArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-emailconfiguration.html#cfn-cognito-userpool-emailconfiguration-sourcearn
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-cognito.CfnUserPool.InviteMessageTemplateProperty", jsii_struct_bases=[])
    class InviteMessageTemplateProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-invitemessagetemplate.html
        Stability:
            experimental
        """
        emailMessage: str
        """``CfnUserPool.InviteMessageTemplateProperty.EmailMessage``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-invitemessagetemplate.html#cfn-cognito-userpool-invitemessagetemplate-emailmessage
        Stability:
            experimental
        """

        emailSubject: str
        """``CfnUserPool.InviteMessageTemplateProperty.EmailSubject``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-invitemessagetemplate.html#cfn-cognito-userpool-invitemessagetemplate-emailsubject
        Stability:
            experimental
        """

        smsMessage: str
        """``CfnUserPool.InviteMessageTemplateProperty.SMSMessage``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-invitemessagetemplate.html#cfn-cognito-userpool-invitemessagetemplate-smsmessage
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-cognito.CfnUserPool.LambdaConfigProperty", jsii_struct_bases=[])
    class LambdaConfigProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-lambdaconfig.html
        Stability:
            experimental
        """
        createAuthChallenge: str
        """``CfnUserPool.LambdaConfigProperty.CreateAuthChallenge``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-lambdaconfig.html#cfn-cognito-userpool-lambdaconfig-createauthchallenge
        Stability:
            experimental
        """

        customMessage: str
        """``CfnUserPool.LambdaConfigProperty.CustomMessage``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-lambdaconfig.html#cfn-cognito-userpool-lambdaconfig-custommessage
        Stability:
            experimental
        """

        defineAuthChallenge: str
        """``CfnUserPool.LambdaConfigProperty.DefineAuthChallenge``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-lambdaconfig.html#cfn-cognito-userpool-lambdaconfig-defineauthchallenge
        Stability:
            experimental
        """

        postAuthentication: str
        """``CfnUserPool.LambdaConfigProperty.PostAuthentication``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-lambdaconfig.html#cfn-cognito-userpool-lambdaconfig-postauthentication
        Stability:
            experimental
        """

        postConfirmation: str
        """``CfnUserPool.LambdaConfigProperty.PostConfirmation``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-lambdaconfig.html#cfn-cognito-userpool-lambdaconfig-postconfirmation
        Stability:
            experimental
        """

        preAuthentication: str
        """``CfnUserPool.LambdaConfigProperty.PreAuthentication``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-lambdaconfig.html#cfn-cognito-userpool-lambdaconfig-preauthentication
        Stability:
            experimental
        """

        preSignUp: str
        """``CfnUserPool.LambdaConfigProperty.PreSignUp``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-lambdaconfig.html#cfn-cognito-userpool-lambdaconfig-presignup
        Stability:
            experimental
        """

        verifyAuthChallengeResponse: str
        """``CfnUserPool.LambdaConfigProperty.VerifyAuthChallengeResponse``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-lambdaconfig.html#cfn-cognito-userpool-lambdaconfig-verifyauthchallengeresponse
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-cognito.CfnUserPool.NumberAttributeConstraintsProperty", jsii_struct_bases=[])
    class NumberAttributeConstraintsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-numberattributeconstraints.html
        Stability:
            experimental
        """
        maxValue: str
        """``CfnUserPool.NumberAttributeConstraintsProperty.MaxValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-numberattributeconstraints.html#cfn-cognito-userpool-numberattributeconstraints-maxvalue
        Stability:
            experimental
        """

        minValue: str
        """``CfnUserPool.NumberAttributeConstraintsProperty.MinValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-numberattributeconstraints.html#cfn-cognito-userpool-numberattributeconstraints-minvalue
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-cognito.CfnUserPool.PasswordPolicyProperty", jsii_struct_bases=[])
    class PasswordPolicyProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-passwordpolicy.html
        Stability:
            experimental
        """
        minimumLength: jsii.Number
        """``CfnUserPool.PasswordPolicyProperty.MinimumLength``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-passwordpolicy.html#cfn-cognito-userpool-passwordpolicy-minimumlength
        Stability:
            experimental
        """

        requireLowercase: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnUserPool.PasswordPolicyProperty.RequireLowercase``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-passwordpolicy.html#cfn-cognito-userpool-passwordpolicy-requirelowercase
        Stability:
            experimental
        """

        requireNumbers: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnUserPool.PasswordPolicyProperty.RequireNumbers``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-passwordpolicy.html#cfn-cognito-userpool-passwordpolicy-requirenumbers
        Stability:
            experimental
        """

        requireSymbols: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnUserPool.PasswordPolicyProperty.RequireSymbols``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-passwordpolicy.html#cfn-cognito-userpool-passwordpolicy-requiresymbols
        Stability:
            experimental
        """

        requireUppercase: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnUserPool.PasswordPolicyProperty.RequireUppercase``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-passwordpolicy.html#cfn-cognito-userpool-passwordpolicy-requireuppercase
        Stability:
            experimental
        """

        temporaryPasswordValidityDays: jsii.Number
        """``CfnUserPool.PasswordPolicyProperty.TemporaryPasswordValidityDays``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-passwordpolicy.html#cfn-cognito-userpool-passwordpolicy-temporarypasswordvaliditydays
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-cognito.CfnUserPool.PoliciesProperty", jsii_struct_bases=[])
    class PoliciesProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-policies.html
        Stability:
            experimental
        """
        passwordPolicy: typing.Union[aws_cdk.cdk.IResolvable, "CfnUserPool.PasswordPolicyProperty"]
        """``CfnUserPool.PoliciesProperty.PasswordPolicy``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-policies.html#cfn-cognito-userpool-policies-passwordpolicy
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-cognito.CfnUserPool.SchemaAttributeProperty", jsii_struct_bases=[])
    class SchemaAttributeProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-schemaattribute.html
        Stability:
            experimental
        """
        attributeDataType: str
        """``CfnUserPool.SchemaAttributeProperty.AttributeDataType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-schemaattribute.html#cfn-cognito-userpool-schemaattribute-attributedatatype
        Stability:
            experimental
        """

        developerOnlyAttribute: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnUserPool.SchemaAttributeProperty.DeveloperOnlyAttribute``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-schemaattribute.html#cfn-cognito-userpool-schemaattribute-developeronlyattribute
        Stability:
            experimental
        """

        mutable: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnUserPool.SchemaAttributeProperty.Mutable``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-schemaattribute.html#cfn-cognito-userpool-schemaattribute-mutable
        Stability:
            experimental
        """

        name: str
        """``CfnUserPool.SchemaAttributeProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-schemaattribute.html#cfn-cognito-userpool-schemaattribute-name
        Stability:
            experimental
        """

        numberAttributeConstraints: typing.Union[aws_cdk.cdk.IResolvable, "CfnUserPool.NumberAttributeConstraintsProperty"]
        """``CfnUserPool.SchemaAttributeProperty.NumberAttributeConstraints``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-schemaattribute.html#cfn-cognito-userpool-schemaattribute-numberattributeconstraints
        Stability:
            experimental
        """

        required: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnUserPool.SchemaAttributeProperty.Required``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-schemaattribute.html#cfn-cognito-userpool-schemaattribute-required
        Stability:
            experimental
        """

        stringAttributeConstraints: typing.Union[aws_cdk.cdk.IResolvable, "CfnUserPool.StringAttributeConstraintsProperty"]
        """``CfnUserPool.SchemaAttributeProperty.StringAttributeConstraints``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-schemaattribute.html#cfn-cognito-userpool-schemaattribute-stringattributeconstraints
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-cognito.CfnUserPool.SmsConfigurationProperty", jsii_struct_bases=[])
    class SmsConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-smsconfiguration.html
        Stability:
            experimental
        """
        externalId: str
        """``CfnUserPool.SmsConfigurationProperty.ExternalId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-smsconfiguration.html#cfn-cognito-userpool-smsconfiguration-externalid
        Stability:
            experimental
        """

        snsCallerArn: str
        """``CfnUserPool.SmsConfigurationProperty.SnsCallerArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-smsconfiguration.html#cfn-cognito-userpool-smsconfiguration-snscallerarn
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-cognito.CfnUserPool.StringAttributeConstraintsProperty", jsii_struct_bases=[])
    class StringAttributeConstraintsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-stringattributeconstraints.html
        Stability:
            experimental
        """
        maxLength: str
        """``CfnUserPool.StringAttributeConstraintsProperty.MaxLength``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-stringattributeconstraints.html#cfn-cognito-userpool-stringattributeconstraints-maxlength
        Stability:
            experimental
        """

        minLength: str
        """``CfnUserPool.StringAttributeConstraintsProperty.MinLength``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpool-stringattributeconstraints.html#cfn-cognito-userpool-stringattributeconstraints-minlength
        Stability:
            experimental
        """


class CfnUserPoolClient(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-cognito.CfnUserPoolClient"):
    """A CloudFormation ``AWS::Cognito::UserPoolClient``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolclient.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Cognito::UserPoolClient
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, user_pool_id: str, client_name: typing.Optional[str]=None, explicit_auth_flows: typing.Optional[typing.List[str]]=None, generate_secret: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, read_attributes: typing.Optional[typing.List[str]]=None, refresh_token_validity: typing.Optional[jsii.Number]=None, write_attributes: typing.Optional[typing.List[str]]=None) -> None:
        """Create a new ``AWS::Cognito::UserPoolClient``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            userPoolId: ``AWS::Cognito::UserPoolClient.UserPoolId``.
            clientName: ``AWS::Cognito::UserPoolClient.ClientName``.
            explicitAuthFlows: ``AWS::Cognito::UserPoolClient.ExplicitAuthFlows``.
            generateSecret: ``AWS::Cognito::UserPoolClient.GenerateSecret``.
            readAttributes: ``AWS::Cognito::UserPoolClient.ReadAttributes``.
            refreshTokenValidity: ``AWS::Cognito::UserPoolClient.RefreshTokenValidity``.
            writeAttributes: ``AWS::Cognito::UserPoolClient.WriteAttributes``.

        Stability:
            experimental
        """
        props: CfnUserPoolClientProps = {"userPoolId": user_pool_id}

        if client_name is not None:
            props["clientName"] = client_name

        if explicit_auth_flows is not None:
            props["explicitAuthFlows"] = explicit_auth_flows

        if generate_secret is not None:
            props["generateSecret"] = generate_secret

        if read_attributes is not None:
            props["readAttributes"] = read_attributes

        if refresh_token_validity is not None:
            props["refreshTokenValidity"] = refresh_token_validity

        if write_attributes is not None:
            props["writeAttributes"] = write_attributes

        jsii.create(CfnUserPoolClient, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrClientSecret")
    def attr_client_secret(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ClientSecret
        """
        return jsii.get(self, "attrClientSecret")

    @property
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Name
        """
        return jsii.get(self, "attrName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="userPoolId")
    def user_pool_id(self) -> str:
        """``AWS::Cognito::UserPoolClient.UserPoolId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolclient.html#cfn-cognito-userpoolclient-userpoolid
        Stability:
            experimental
        """
        return jsii.get(self, "userPoolId")

    @user_pool_id.setter
    def user_pool_id(self, value: str):
        return jsii.set(self, "userPoolId", value)

    @property
    @jsii.member(jsii_name="clientName")
    def client_name(self) -> typing.Optional[str]:
        """``AWS::Cognito::UserPoolClient.ClientName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolclient.html#cfn-cognito-userpoolclient-clientname
        Stability:
            experimental
        """
        return jsii.get(self, "clientName")

    @client_name.setter
    def client_name(self, value: typing.Optional[str]):
        return jsii.set(self, "clientName", value)

    @property
    @jsii.member(jsii_name="explicitAuthFlows")
    def explicit_auth_flows(self) -> typing.Optional[typing.List[str]]:
        """``AWS::Cognito::UserPoolClient.ExplicitAuthFlows``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolclient.html#cfn-cognito-userpoolclient-explicitauthflows
        Stability:
            experimental
        """
        return jsii.get(self, "explicitAuthFlows")

    @explicit_auth_flows.setter
    def explicit_auth_flows(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "explicitAuthFlows", value)

    @property
    @jsii.member(jsii_name="generateSecret")
    def generate_secret(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::Cognito::UserPoolClient.GenerateSecret``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolclient.html#cfn-cognito-userpoolclient-generatesecret
        Stability:
            experimental
        """
        return jsii.get(self, "generateSecret")

    @generate_secret.setter
    def generate_secret(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "generateSecret", value)

    @property
    @jsii.member(jsii_name="readAttributes")
    def read_attributes(self) -> typing.Optional[typing.List[str]]:
        """``AWS::Cognito::UserPoolClient.ReadAttributes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolclient.html#cfn-cognito-userpoolclient-readattributes
        Stability:
            experimental
        """
        return jsii.get(self, "readAttributes")

    @read_attributes.setter
    def read_attributes(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "readAttributes", value)

    @property
    @jsii.member(jsii_name="refreshTokenValidity")
    def refresh_token_validity(self) -> typing.Optional[jsii.Number]:
        """``AWS::Cognito::UserPoolClient.RefreshTokenValidity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolclient.html#cfn-cognito-userpoolclient-refreshtokenvalidity
        Stability:
            experimental
        """
        return jsii.get(self, "refreshTokenValidity")

    @refresh_token_validity.setter
    def refresh_token_validity(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "refreshTokenValidity", value)

    @property
    @jsii.member(jsii_name="writeAttributes")
    def write_attributes(self) -> typing.Optional[typing.List[str]]:
        """``AWS::Cognito::UserPoolClient.WriteAttributes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolclient.html#cfn-cognito-userpoolclient-writeattributes
        Stability:
            experimental
        """
        return jsii.get(self, "writeAttributes")

    @write_attributes.setter
    def write_attributes(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "writeAttributes", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnUserPoolClientProps(jsii.compat.TypedDict, total=False):
    clientName: str
    """``AWS::Cognito::UserPoolClient.ClientName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolclient.html#cfn-cognito-userpoolclient-clientname
    Stability:
        experimental
    """
    explicitAuthFlows: typing.List[str]
    """``AWS::Cognito::UserPoolClient.ExplicitAuthFlows``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolclient.html#cfn-cognito-userpoolclient-explicitauthflows
    Stability:
        experimental
    """
    generateSecret: typing.Union[bool, aws_cdk.cdk.IResolvable]
    """``AWS::Cognito::UserPoolClient.GenerateSecret``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolclient.html#cfn-cognito-userpoolclient-generatesecret
    Stability:
        experimental
    """
    readAttributes: typing.List[str]
    """``AWS::Cognito::UserPoolClient.ReadAttributes``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolclient.html#cfn-cognito-userpoolclient-readattributes
    Stability:
        experimental
    """
    refreshTokenValidity: jsii.Number
    """``AWS::Cognito::UserPoolClient.RefreshTokenValidity``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolclient.html#cfn-cognito-userpoolclient-refreshtokenvalidity
    Stability:
        experimental
    """
    writeAttributes: typing.List[str]
    """``AWS::Cognito::UserPoolClient.WriteAttributes``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolclient.html#cfn-cognito-userpoolclient-writeattributes
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-cognito.CfnUserPoolClientProps", jsii_struct_bases=[_CfnUserPoolClientProps])
class CfnUserPoolClientProps(_CfnUserPoolClientProps):
    """Properties for defining a ``AWS::Cognito::UserPoolClient``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolclient.html
    Stability:
        experimental
    """
    userPoolId: str
    """``AWS::Cognito::UserPoolClient.UserPoolId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolclient.html#cfn-cognito-userpoolclient-userpoolid
    Stability:
        experimental
    """

class CfnUserPoolGroup(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-cognito.CfnUserPoolGroup"):
    """A CloudFormation ``AWS::Cognito::UserPoolGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolgroup.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Cognito::UserPoolGroup
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, user_pool_id: str, description: typing.Optional[str]=None, group_name: typing.Optional[str]=None, precedence: typing.Optional[jsii.Number]=None, role_arn: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Cognito::UserPoolGroup``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            userPoolId: ``AWS::Cognito::UserPoolGroup.UserPoolId``.
            description: ``AWS::Cognito::UserPoolGroup.Description``.
            groupName: ``AWS::Cognito::UserPoolGroup.GroupName``.
            precedence: ``AWS::Cognito::UserPoolGroup.Precedence``.
            roleArn: ``AWS::Cognito::UserPoolGroup.RoleArn``.

        Stability:
            experimental
        """
        props: CfnUserPoolGroupProps = {"userPoolId": user_pool_id}

        if description is not None:
            props["description"] = description

        if group_name is not None:
            props["groupName"] = group_name

        if precedence is not None:
            props["precedence"] = precedence

        if role_arn is not None:
            props["roleArn"] = role_arn

        jsii.create(CfnUserPoolGroup, self, [scope, id, props])

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
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="userPoolId")
    def user_pool_id(self) -> str:
        """``AWS::Cognito::UserPoolGroup.UserPoolId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolgroup.html#cfn-cognito-userpoolgroup-userpoolid
        Stability:
            experimental
        """
        return jsii.get(self, "userPoolId")

    @user_pool_id.setter
    def user_pool_id(self, value: str):
        return jsii.set(self, "userPoolId", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::Cognito::UserPoolGroup.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolgroup.html#cfn-cognito-userpoolgroup-description
        Stability:
            experimental
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="groupName")
    def group_name(self) -> typing.Optional[str]:
        """``AWS::Cognito::UserPoolGroup.GroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolgroup.html#cfn-cognito-userpoolgroup-groupname
        Stability:
            experimental
        """
        return jsii.get(self, "groupName")

    @group_name.setter
    def group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "groupName", value)

    @property
    @jsii.member(jsii_name="precedence")
    def precedence(self) -> typing.Optional[jsii.Number]:
        """``AWS::Cognito::UserPoolGroup.Precedence``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolgroup.html#cfn-cognito-userpoolgroup-precedence
        Stability:
            experimental
        """
        return jsii.get(self, "precedence")

    @precedence.setter
    def precedence(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "precedence", value)

    @property
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> typing.Optional[str]:
        """``AWS::Cognito::UserPoolGroup.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolgroup.html#cfn-cognito-userpoolgroup-rolearn
        Stability:
            experimental
        """
        return jsii.get(self, "roleArn")

    @role_arn.setter
    def role_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "roleArn", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnUserPoolGroupProps(jsii.compat.TypedDict, total=False):
    description: str
    """``AWS::Cognito::UserPoolGroup.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolgroup.html#cfn-cognito-userpoolgroup-description
    Stability:
        experimental
    """
    groupName: str
    """``AWS::Cognito::UserPoolGroup.GroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolgroup.html#cfn-cognito-userpoolgroup-groupname
    Stability:
        experimental
    """
    precedence: jsii.Number
    """``AWS::Cognito::UserPoolGroup.Precedence``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolgroup.html#cfn-cognito-userpoolgroup-precedence
    Stability:
        experimental
    """
    roleArn: str
    """``AWS::Cognito::UserPoolGroup.RoleArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolgroup.html#cfn-cognito-userpoolgroup-rolearn
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-cognito.CfnUserPoolGroupProps", jsii_struct_bases=[_CfnUserPoolGroupProps])
class CfnUserPoolGroupProps(_CfnUserPoolGroupProps):
    """Properties for defining a ``AWS::Cognito::UserPoolGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolgroup.html
    Stability:
        experimental
    """
    userPoolId: str
    """``AWS::Cognito::UserPoolGroup.UserPoolId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolgroup.html#cfn-cognito-userpoolgroup-userpoolid
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-cognito.CfnUserPoolProps", jsii_struct_bases=[])
class CfnUserPoolProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::Cognito::UserPool``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html
    Stability:
        experimental
    """
    adminCreateUserConfig: typing.Union[aws_cdk.cdk.IResolvable, "CfnUserPool.AdminCreateUserConfigProperty"]
    """``AWS::Cognito::UserPool.AdminCreateUserConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html#cfn-cognito-userpool-admincreateuserconfig
    Stability:
        experimental
    """

    aliasAttributes: typing.List[str]
    """``AWS::Cognito::UserPool.AliasAttributes``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html#cfn-cognito-userpool-aliasattributes
    Stability:
        experimental
    """

    autoVerifiedAttributes: typing.List[str]
    """``AWS::Cognito::UserPool.AutoVerifiedAttributes``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html#cfn-cognito-userpool-autoverifiedattributes
    Stability:
        experimental
    """

    deviceConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnUserPool.DeviceConfigurationProperty"]
    """``AWS::Cognito::UserPool.DeviceConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html#cfn-cognito-userpool-deviceconfiguration
    Stability:
        experimental
    """

    emailConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnUserPool.EmailConfigurationProperty"]
    """``AWS::Cognito::UserPool.EmailConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html#cfn-cognito-userpool-emailconfiguration
    Stability:
        experimental
    """

    emailVerificationMessage: str
    """``AWS::Cognito::UserPool.EmailVerificationMessage``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html#cfn-cognito-userpool-emailverificationmessage
    Stability:
        experimental
    """

    emailVerificationSubject: str
    """``AWS::Cognito::UserPool.EmailVerificationSubject``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html#cfn-cognito-userpool-emailverificationsubject
    Stability:
        experimental
    """

    lambdaConfig: typing.Union[aws_cdk.cdk.IResolvable, "CfnUserPool.LambdaConfigProperty"]
    """``AWS::Cognito::UserPool.LambdaConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html#cfn-cognito-userpool-lambdaconfig
    Stability:
        experimental
    """

    mfaConfiguration: str
    """``AWS::Cognito::UserPool.MfaConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html#cfn-cognito-userpool-mfaconfiguration
    Stability:
        experimental
    """

    policies: typing.Union[aws_cdk.cdk.IResolvable, "CfnUserPool.PoliciesProperty"]
    """``AWS::Cognito::UserPool.Policies``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html#cfn-cognito-userpool-policies
    Stability:
        experimental
    """

    schema: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnUserPool.SchemaAttributeProperty"]]]
    """``AWS::Cognito::UserPool.Schema``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html#cfn-cognito-userpool-schema
    Stability:
        experimental
    """

    smsAuthenticationMessage: str
    """``AWS::Cognito::UserPool.SmsAuthenticationMessage``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html#cfn-cognito-userpool-smsauthenticationmessage
    Stability:
        experimental
    """

    smsConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnUserPool.SmsConfigurationProperty"]
    """``AWS::Cognito::UserPool.SmsConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html#cfn-cognito-userpool-smsconfiguration
    Stability:
        experimental
    """

    smsVerificationMessage: str
    """``AWS::Cognito::UserPool.SmsVerificationMessage``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html#cfn-cognito-userpool-smsverificationmessage
    Stability:
        experimental
    """

    usernameAttributes: typing.List[str]
    """``AWS::Cognito::UserPool.UsernameAttributes``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html#cfn-cognito-userpool-usernameattributes
    Stability:
        experimental
    """

    userPoolName: str
    """``AWS::Cognito::UserPool.UserPoolName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html#cfn-cognito-userpool-userpoolname
    Stability:
        experimental
    """

    userPoolTags: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.IResolvable]
    """``AWS::Cognito::UserPool.UserPoolTags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html#cfn-cognito-userpool-userpooltags
    Stability:
        experimental
    """

class CfnUserPoolUser(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-cognito.CfnUserPoolUser"):
    """A CloudFormation ``AWS::Cognito::UserPoolUser``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpooluser.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Cognito::UserPoolUser
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, user_pool_id: str, desired_delivery_mediums: typing.Optional[typing.List[str]]=None, force_alias_creation: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, message_action: typing.Optional[str]=None, user_attributes: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "AttributeTypeProperty"]]]]]=None, username: typing.Optional[str]=None, validation_data: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "AttributeTypeProperty"]]]]]=None) -> None:
        """Create a new ``AWS::Cognito::UserPoolUser``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            userPoolId: ``AWS::Cognito::UserPoolUser.UserPoolId``.
            desiredDeliveryMediums: ``AWS::Cognito::UserPoolUser.DesiredDeliveryMediums``.
            forceAliasCreation: ``AWS::Cognito::UserPoolUser.ForceAliasCreation``.
            messageAction: ``AWS::Cognito::UserPoolUser.MessageAction``.
            userAttributes: ``AWS::Cognito::UserPoolUser.UserAttributes``.
            username: ``AWS::Cognito::UserPoolUser.Username``.
            validationData: ``AWS::Cognito::UserPoolUser.ValidationData``.

        Stability:
            experimental
        """
        props: CfnUserPoolUserProps = {"userPoolId": user_pool_id}

        if desired_delivery_mediums is not None:
            props["desiredDeliveryMediums"] = desired_delivery_mediums

        if force_alias_creation is not None:
            props["forceAliasCreation"] = force_alias_creation

        if message_action is not None:
            props["messageAction"] = message_action

        if user_attributes is not None:
            props["userAttributes"] = user_attributes

        if username is not None:
            props["username"] = username

        if validation_data is not None:
            props["validationData"] = validation_data

        jsii.create(CfnUserPoolUser, self, [scope, id, props])

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
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="userPoolId")
    def user_pool_id(self) -> str:
        """``AWS::Cognito::UserPoolUser.UserPoolId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpooluser.html#cfn-cognito-userpooluser-userpoolid
        Stability:
            experimental
        """
        return jsii.get(self, "userPoolId")

    @user_pool_id.setter
    def user_pool_id(self, value: str):
        return jsii.set(self, "userPoolId", value)

    @property
    @jsii.member(jsii_name="desiredDeliveryMediums")
    def desired_delivery_mediums(self) -> typing.Optional[typing.List[str]]:
        """``AWS::Cognito::UserPoolUser.DesiredDeliveryMediums``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpooluser.html#cfn-cognito-userpooluser-desireddeliverymediums
        Stability:
            experimental
        """
        return jsii.get(self, "desiredDeliveryMediums")

    @desired_delivery_mediums.setter
    def desired_delivery_mediums(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "desiredDeliveryMediums", value)

    @property
    @jsii.member(jsii_name="forceAliasCreation")
    def force_alias_creation(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::Cognito::UserPoolUser.ForceAliasCreation``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpooluser.html#cfn-cognito-userpooluser-forcealiascreation
        Stability:
            experimental
        """
        return jsii.get(self, "forceAliasCreation")

    @force_alias_creation.setter
    def force_alias_creation(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "forceAliasCreation", value)

    @property
    @jsii.member(jsii_name="messageAction")
    def message_action(self) -> typing.Optional[str]:
        """``AWS::Cognito::UserPoolUser.MessageAction``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpooluser.html#cfn-cognito-userpooluser-messageaction
        Stability:
            experimental
        """
        return jsii.get(self, "messageAction")

    @message_action.setter
    def message_action(self, value: typing.Optional[str]):
        return jsii.set(self, "messageAction", value)

    @property
    @jsii.member(jsii_name="userAttributes")
    def user_attributes(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "AttributeTypeProperty"]]]]]:
        """``AWS::Cognito::UserPoolUser.UserAttributes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpooluser.html#cfn-cognito-userpooluser-userattributes
        Stability:
            experimental
        """
        return jsii.get(self, "userAttributes")

    @user_attributes.setter
    def user_attributes(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "AttributeTypeProperty"]]]]]):
        return jsii.set(self, "userAttributes", value)

    @property
    @jsii.member(jsii_name="username")
    def username(self) -> typing.Optional[str]:
        """``AWS::Cognito::UserPoolUser.Username``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpooluser.html#cfn-cognito-userpooluser-username
        Stability:
            experimental
        """
        return jsii.get(self, "username")

    @username.setter
    def username(self, value: typing.Optional[str]):
        return jsii.set(self, "username", value)

    @property
    @jsii.member(jsii_name="validationData")
    def validation_data(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "AttributeTypeProperty"]]]]]:
        """``AWS::Cognito::UserPoolUser.ValidationData``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpooluser.html#cfn-cognito-userpooluser-validationdata
        Stability:
            experimental
        """
        return jsii.get(self, "validationData")

    @validation_data.setter
    def validation_data(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "AttributeTypeProperty"]]]]]):
        return jsii.set(self, "validationData", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-cognito.CfnUserPoolUser.AttributeTypeProperty", jsii_struct_bases=[])
    class AttributeTypeProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpooluser-attributetype.html
        Stability:
            experimental
        """
        name: str
        """``CfnUserPoolUser.AttributeTypeProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpooluser-attributetype.html#cfn-cognito-userpooluser-attributetype-name
        Stability:
            experimental
        """

        value: str
        """``CfnUserPoolUser.AttributeTypeProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-userpooluser-attributetype.html#cfn-cognito-userpooluser-attributetype-value
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnUserPoolUserProps(jsii.compat.TypedDict, total=False):
    desiredDeliveryMediums: typing.List[str]
    """``AWS::Cognito::UserPoolUser.DesiredDeliveryMediums``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpooluser.html#cfn-cognito-userpooluser-desireddeliverymediums
    Stability:
        experimental
    """
    forceAliasCreation: typing.Union[bool, aws_cdk.cdk.IResolvable]
    """``AWS::Cognito::UserPoolUser.ForceAliasCreation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpooluser.html#cfn-cognito-userpooluser-forcealiascreation
    Stability:
        experimental
    """
    messageAction: str
    """``AWS::Cognito::UserPoolUser.MessageAction``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpooluser.html#cfn-cognito-userpooluser-messageaction
    Stability:
        experimental
    """
    userAttributes: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnUserPoolUser.AttributeTypeProperty"]]]
    """``AWS::Cognito::UserPoolUser.UserAttributes``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpooluser.html#cfn-cognito-userpooluser-userattributes
    Stability:
        experimental
    """
    username: str
    """``AWS::Cognito::UserPoolUser.Username``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpooluser.html#cfn-cognito-userpooluser-username
    Stability:
        experimental
    """
    validationData: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnUserPoolUser.AttributeTypeProperty"]]]
    """``AWS::Cognito::UserPoolUser.ValidationData``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpooluser.html#cfn-cognito-userpooluser-validationdata
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-cognito.CfnUserPoolUserProps", jsii_struct_bases=[_CfnUserPoolUserProps])
class CfnUserPoolUserProps(_CfnUserPoolUserProps):
    """Properties for defining a ``AWS::Cognito::UserPoolUser``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpooluser.html
    Stability:
        experimental
    """
    userPoolId: str
    """``AWS::Cognito::UserPoolUser.UserPoolId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpooluser.html#cfn-cognito-userpooluser-userpoolid
    Stability:
        experimental
    """

class CfnUserPoolUserToGroupAttachment(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-cognito.CfnUserPoolUserToGroupAttachment"):
    """A CloudFormation ``AWS::Cognito::UserPoolUserToGroupAttachment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolusertogroupattachment.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Cognito::UserPoolUserToGroupAttachment
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, group_name: str, username: str, user_pool_id: str) -> None:
        """Create a new ``AWS::Cognito::UserPoolUserToGroupAttachment``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            groupName: ``AWS::Cognito::UserPoolUserToGroupAttachment.GroupName``.
            username: ``AWS::Cognito::UserPoolUserToGroupAttachment.Username``.
            userPoolId: ``AWS::Cognito::UserPoolUserToGroupAttachment.UserPoolId``.

        Stability:
            experimental
        """
        props: CfnUserPoolUserToGroupAttachmentProps = {"groupName": group_name, "username": username, "userPoolId": user_pool_id}

        jsii.create(CfnUserPoolUserToGroupAttachment, self, [scope, id, props])

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
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="groupName")
    def group_name(self) -> str:
        """``AWS::Cognito::UserPoolUserToGroupAttachment.GroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolusertogroupattachment.html#cfn-cognito-userpoolusertogroupattachment-groupname
        Stability:
            experimental
        """
        return jsii.get(self, "groupName")

    @group_name.setter
    def group_name(self, value: str):
        return jsii.set(self, "groupName", value)

    @property
    @jsii.member(jsii_name="username")
    def username(self) -> str:
        """``AWS::Cognito::UserPoolUserToGroupAttachment.Username``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolusertogroupattachment.html#cfn-cognito-userpoolusertogroupattachment-username
        Stability:
            experimental
        """
        return jsii.get(self, "username")

    @username.setter
    def username(self, value: str):
        return jsii.set(self, "username", value)

    @property
    @jsii.member(jsii_name="userPoolId")
    def user_pool_id(self) -> str:
        """``AWS::Cognito::UserPoolUserToGroupAttachment.UserPoolId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolusertogroupattachment.html#cfn-cognito-userpoolusertogroupattachment-userpoolid
        Stability:
            experimental
        """
        return jsii.get(self, "userPoolId")

    @user_pool_id.setter
    def user_pool_id(self, value: str):
        return jsii.set(self, "userPoolId", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-cognito.CfnUserPoolUserToGroupAttachmentProps", jsii_struct_bases=[])
class CfnUserPoolUserToGroupAttachmentProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::Cognito::UserPoolUserToGroupAttachment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolusertogroupattachment.html
    Stability:
        experimental
    """
    groupName: str
    """``AWS::Cognito::UserPoolUserToGroupAttachment.GroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolusertogroupattachment.html#cfn-cognito-userpoolusertogroupattachment-groupname
    Stability:
        experimental
    """

    username: str
    """``AWS::Cognito::UserPoolUserToGroupAttachment.Username``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolusertogroupattachment.html#cfn-cognito-userpoolusertogroupattachment-username
    Stability:
        experimental
    """

    userPoolId: str
    """``AWS::Cognito::UserPoolUserToGroupAttachment.UserPoolId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolusertogroupattachment.html#cfn-cognito-userpoolusertogroupattachment-userpoolid
    Stability:
        experimental
    """

@jsii.interface(jsii_type="@aws-cdk/aws-cognito.IUserPool")
class IUserPool(aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IUserPoolProxy

    @property
    @jsii.member(jsii_name="userPoolArn")
    def user_pool_arn(self) -> str:
        """The ARN of this user pool resource.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="userPoolId")
    def user_pool_id(self) -> str:
        """The physical ID of this user pool resource.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="userPoolProviderName")
    def user_pool_provider_name(self) -> str:
        """The provider name of this user pool resource.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="userPoolProviderUrl")
    def user_pool_provider_url(self) -> str:
        """The provider URL of this user pool resource.

        Stability:
            experimental
        attribute:
            true
        """
        ...


class _IUserPoolProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-cognito.IUserPool"
    @property
    @jsii.member(jsii_name="userPoolArn")
    def user_pool_arn(self) -> str:
        """The ARN of this user pool resource.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "userPoolArn")

    @property
    @jsii.member(jsii_name="userPoolId")
    def user_pool_id(self) -> str:
        """The physical ID of this user pool resource.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "userPoolId")

    @property
    @jsii.member(jsii_name="userPoolProviderName")
    def user_pool_provider_name(self) -> str:
        """The provider name of this user pool resource.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "userPoolProviderName")

    @property
    @jsii.member(jsii_name="userPoolProviderUrl")
    def user_pool_provider_url(self) -> str:
        """The provider URL of this user pool resource.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "userPoolProviderUrl")


@jsii.enum(jsii_type="@aws-cdk/aws-cognito.SignInType")
class SignInType(enum.Enum):
    """Methods of user sign-in.

    Stability:
        experimental
    """
    Username = "Username"
    """End-user will sign in with a username, with optional aliases.

    Stability:
        experimental
    """
    Email = "Email"
    """End-user will sign in using an email address.

    Stability:
        experimental
    """
    Phone = "Phone"
    """End-user will sign in using a phone number.

    Stability:
        experimental
    """
    EmailOrPhone = "EmailOrPhone"
    """End-user will sign in using either an email address or phone number.

    Stability:
        experimental
    """

@jsii.implements(IUserPool)
class UserPool(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-cognito.UserPool"):
    """Define a Cognito User Pool.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, auto_verified_attributes: typing.Optional[typing.List["UserPoolAttribute"]]=None, lambda_triggers: typing.Optional["UserPoolTriggers"]=None, pool_name: typing.Optional[str]=None, sign_in_type: typing.Optional["SignInType"]=None, username_alias_attributes: typing.Optional[typing.List["UserPoolAttribute"]]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            autoVerifiedAttributes: Attributes which Cognito will automatically send a verification message to. Must be either EMAIL, PHONE, or both. Default: - No auto verification.
            lambdaTriggers: Lambda functions to use for supported Cognito triggers. Default: - No Lambda triggers.
            poolName: Name of the user pool. Default: - Unique ID.
            signInType: Method used for user registration & sign in. Allows either username with aliases OR sign in with email, phone, or both. Default: SignInType.Username
            usernameAliasAttributes: Attributes to allow as username alias. Only valid if signInType is USERNAME. Default: - No alias.

        Stability:
            experimental
        """
        props: UserPoolProps = {}

        if auto_verified_attributes is not None:
            props["autoVerifiedAttributes"] = auto_verified_attributes

        if lambda_triggers is not None:
            props["lambdaTriggers"] = lambda_triggers

        if pool_name is not None:
            props["poolName"] = pool_name

        if sign_in_type is not None:
            props["signInType"] = sign_in_type

        if username_alias_attributes is not None:
            props["usernameAliasAttributes"] = username_alias_attributes

        jsii.create(UserPool, self, [scope, id, props])

    @jsii.member(jsii_name="fromUserPoolAttributes")
    @classmethod
    def from_user_pool_attributes(cls, scope: aws_cdk.cdk.Construct, id: str, *, user_pool_arn: str, user_pool_id: str, user_pool_provider_name: str, user_pool_provider_url: str) -> "IUserPool":
        """Import an existing user pool resource.

        Arguments:
            scope: Parent construct.
            id: Construct ID.
            attrs: Imported user pool properties.
            userPoolArn: The ARN of the imported user pool.
            userPoolId: The ID of an existing user pool.
            userPoolProviderName: The provider name of the imported user pool.
            userPoolProviderUrl: The URL of the imported user pool.

        Stability:
            experimental
        """
        attrs: UserPoolAttributes = {"userPoolArn": user_pool_arn, "userPoolId": user_pool_id, "userPoolProviderName": user_pool_provider_name, "userPoolProviderUrl": user_pool_provider_url}

        return jsii.sinvoke(cls, "fromUserPoolAttributes", [scope, id, attrs])

    @jsii.member(jsii_name="addCreateAuthChallengeTrigger")
    def add_create_auth_challenge_trigger(self, fn: aws_cdk.aws_lambda.IFunction) -> None:
        """Attach 'Create Auth Challenge' trigger Grants access from cognito-idp.amazonaws.com to the lambda.

        Arguments:
            fn: the lambda function to attach.

        See:
            https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-create-auth-challenge.html
        Stability:
            experimental
        """
        return jsii.invoke(self, "addCreateAuthChallengeTrigger", [fn])

    @jsii.member(jsii_name="addCustomMessageTrigger")
    def add_custom_message_trigger(self, fn: aws_cdk.aws_lambda.IFunction) -> None:
        """Attach 'Custom Message' trigger Grants access from cognito-idp.amazonaws.com to the lambda.

        Arguments:
            fn: the lambda function to attach.

        See:
            https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-custom-message.html
        Stability:
            experimental
        """
        return jsii.invoke(self, "addCustomMessageTrigger", [fn])

    @jsii.member(jsii_name="addDefineAuthChallengeTrigger")
    def add_define_auth_challenge_trigger(self, fn: aws_cdk.aws_lambda.IFunction) -> None:
        """Attach 'Define Auth Challenge' trigger Grants access from cognito-idp.amazonaws.com to the lambda.

        Arguments:
            fn: the lambda function to attach.

        See:
            https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-define-auth-challenge.html
        Stability:
            experimental
        """
        return jsii.invoke(self, "addDefineAuthChallengeTrigger", [fn])

    @jsii.member(jsii_name="addPostAuthenticationTrigger")
    def add_post_authentication_trigger(self, fn: aws_cdk.aws_lambda.IFunction) -> None:
        """Attach 'Post Authentication' trigger Grants access from cognito-idp.amazonaws.com to the lambda.

        Arguments:
            fn: the lambda function to attach.

        See:
            https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-post-authentication.html
        Stability:
            experimental
        """
        return jsii.invoke(self, "addPostAuthenticationTrigger", [fn])

    @jsii.member(jsii_name="addPostConfirmationTrigger")
    def add_post_confirmation_trigger(self, fn: aws_cdk.aws_lambda.IFunction) -> None:
        """Attach 'Post Confirmation' trigger Grants access from cognito-idp.amazonaws.com to the lambda.

        Arguments:
            fn: the lambda function to attach.

        See:
            https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-post-confirmation.html
        Stability:
            experimental
        """
        return jsii.invoke(self, "addPostConfirmationTrigger", [fn])

    @jsii.member(jsii_name="addPreAuthenticationTrigger")
    def add_pre_authentication_trigger(self, fn: aws_cdk.aws_lambda.IFunction) -> None:
        """Attach 'Pre Authentication' trigger Grants access from cognito-idp.amazonaws.com to the lambda.

        Arguments:
            fn: the lambda function to attach.

        See:
            https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-pre-authentication.html
        Stability:
            experimental
        """
        return jsii.invoke(self, "addPreAuthenticationTrigger", [fn])

    @jsii.member(jsii_name="addPreSignUpTrigger")
    def add_pre_sign_up_trigger(self, fn: aws_cdk.aws_lambda.IFunction) -> None:
        """Attach 'Pre Sign Up' trigger Grants access from cognito-idp.amazonaws.com to the lambda.

        Arguments:
            fn: the lambda function to attach.

        See:
            https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-pre-sign-up.html
        Stability:
            experimental
        """
        return jsii.invoke(self, "addPreSignUpTrigger", [fn])

    @jsii.member(jsii_name="addVerifyAuthChallengeResponseTrigger")
    def add_verify_auth_challenge_response_trigger(self, fn: aws_cdk.aws_lambda.IFunction) -> None:
        """Attach 'Verify Auth Challenge Response' trigger Grants access from cognito-idp.amazonaws.com to the lambda.

        Arguments:
            fn: the lambda function to attach.

        See:
            https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-verify-auth-challenge-response.html
        Stability:
            experimental
        """
        return jsii.invoke(self, "addVerifyAuthChallengeResponseTrigger", [fn])

    @property
    @jsii.member(jsii_name="userPoolArn")
    def user_pool_arn(self) -> str:
        """The ARN of the user pool.

        Stability:
            experimental
        """
        return jsii.get(self, "userPoolArn")

    @property
    @jsii.member(jsii_name="userPoolId")
    def user_pool_id(self) -> str:
        """The physical ID of this user pool resource.

        Stability:
            experimental
        """
        return jsii.get(self, "userPoolId")

    @property
    @jsii.member(jsii_name="userPoolProviderName")
    def user_pool_provider_name(self) -> str:
        """User pool provider name.

        Stability:
            experimental
        """
        return jsii.get(self, "userPoolProviderName")

    @property
    @jsii.member(jsii_name="userPoolProviderUrl")
    def user_pool_provider_url(self) -> str:
        """User pool provider URL.

        Stability:
            experimental
        """
        return jsii.get(self, "userPoolProviderUrl")


@jsii.enum(jsii_type="@aws-cdk/aws-cognito.UserPoolAttribute")
class UserPoolAttribute(enum.Enum):
    """Standard attributes Specified following the OpenID Connect spec.

    See:
        https://openid.net/specs/openid-connect-core-1_0.html#StandardClaims
    Stability:
        experimental
    """
    Address = "Address"
    """End-User's preferred postal address.

    Stability:
        experimental
    """
    Birthdate = "Birthdate"
    """End-User's birthday, represented as an ISO 8601:2004 [ISO8601‑2004] YYYY-MM-DD format. The year MAY be 0000, indicating that it is omitted. To represent only the year, YYYY format is allowed.

    Stability:
        experimental
    """
    Email = "Email"
    """End-User's preferred e-mail address. Its value MUST conform to the RFC 5322 [RFC5322] addr-spec syntax.

    Stability:
        experimental
    """
    FamilyName = "FamilyName"
    """Surname(s) or last name(s) of the End-User. Note that in some cultures, people can have multiple family names or no family name; all can be present, with the names being separated by space characters.

    Stability:
        experimental
    """
    Gender = "Gender"
    """End-User's gender.

    Stability:
        experimental
    """
    GivenName = "GivenName"
    """Given name(s) or first name(s) of the End-User. Note that in some cultures, people can have multiple given names; all can be present, with the names being separated by space characters.

    Stability:
        experimental
    """
    Locale = "Locale"
    """End-User's locale, represented as a BCP47 [RFC5646] language tag. This is typically an ISO 639-1 Alpha-2 [ISO639‑1] language code in lowercase and an ISO 3166-1 Alpha-2 [ISO3166‑1] country code in uppercase, separated by a dash. For example, en-US or fr-CA.

    Stability:
        experimental
    """
    MiddleName = "MiddleName"
    """Middle name(s) of the End-User. Note that in some cultures, people can have multiple middle names; all can be present, with the names being separated by space characters. Also note that in some cultures, middle names are not used.

    Stability:
        experimental
    """
    Name = "Name"
    """End-User's full name in displayable form including all name parts, possibly including titles and suffixes, ordered according to the End-User's locale and preferences.

    Stability:
        experimental
    """
    Nickname = "Nickname"
    """Casual name of the End-User that may or may not be the same as the given_name. For instance, a nickname value of Mike might be returned alongside a given_name value of Michael.

    Stability:
        experimental
    """
    PhoneNumber = "PhoneNumber"
    """End-User's preferred telephone number. E.164 [E.164] is RECOMMENDED as the format of this Claim, for example, +1 (425) 555-1212 or +56 (2) 687 2400. If the phone number contains an extension, it is RECOMMENDED that the extension be represented using the RFC 3966 [RFC3966] extension syntax, for example, +1 (604) 555-1234;ext=5678.

    Stability:
        experimental
    """
    Picture = "Picture"
    """URL of the End-User's profile picture. This URL MUST refer to an image file (for example, a PNG, JPEG, or GIF image file), rather than to a Web page containing an image. Note that this URL SHOULD specifically reference a profile photo of the End-User suitable for displaying when describing the End-User, rather than an arbitrary photo taken by the End-User.

    Stability:
        experimental
    """
    PreferredUsername = "PreferredUsername"
    """Shorthand name by which the End-User wishes to be referred to.

    Stability:
        experimental
    """
    Profile = "Profile"
    """URL of the End-User's profile page.

    The contents of this Web page SHOULD be about the End-User.

    Stability:
        experimental
    """
    Timezone = "Timezone"
    """The End-User's time zone.

    Stability:
        experimental
    """
    UpdatedAt = "UpdatedAt"
    """Time the End-User's information was last updated. Its value is a JSON number representing the number of seconds from 1970-01-01T0:0:0Z as measured in UTC until the date/time.

    Stability:
        experimental
    """
    Website = "Website"
    """URL of the End-User's Web page or blog. This Web page SHOULD contain information published by the End-User or an organization that the End-User is affiliated with.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-cognito.UserPoolAttributes", jsii_struct_bases=[])
class UserPoolAttributes(jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    userPoolArn: str
    """The ARN of the imported user pool.

    Stability:
        experimental
    """

    userPoolId: str
    """The ID of an existing user pool.

    Stability:
        experimental
    """

    userPoolProviderName: str
    """The provider name of the imported user pool.

    Stability:
        experimental
    """

    userPoolProviderUrl: str
    """The URL of the imported user pool.

    Stability:
        experimental
    """

class UserPoolClient(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-cognito.UserPoolClient"):
    """Define a UserPool App Client.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, user_pool: "IUserPool", client_name: typing.Optional[str]=None, enabled_auth_flows: typing.Optional[typing.List["AuthFlow"]]=None, generate_secret: typing.Optional[bool]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            userPool: The UserPool resource this client will have access to.
            clientName: Name of the application client. Default: cloudformation generated name
            enabledAuthFlows: List of enabled authentication flows. Default: no enabled flows
            generateSecret: Whether to generate a client secret. Default: false

        Stability:
            experimental
        """
        props: UserPoolClientProps = {"userPool": user_pool}

        if client_name is not None:
            props["clientName"] = client_name

        if enabled_auth_flows is not None:
            props["enabledAuthFlows"] = enabled_auth_flows

        if generate_secret is not None:
            props["generateSecret"] = generate_secret

        jsii.create(UserPoolClient, self, [scope, id, props])

    @property
    @jsii.member(jsii_name="userPoolClientClientSecret")
    def user_pool_client_client_secret(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "userPoolClientClientSecret")

    @property
    @jsii.member(jsii_name="userPoolClientId")
    def user_pool_client_id(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "userPoolClientId")

    @property
    @jsii.member(jsii_name="userPoolClientName")
    def user_pool_client_name(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "userPoolClientName")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _UserPoolClientProps(jsii.compat.TypedDict, total=False):
    clientName: str
    """Name of the application client.

    Default:
        cloudformation generated name

    Stability:
        experimental
    """
    enabledAuthFlows: typing.List["AuthFlow"]
    """List of enabled authentication flows.

    Default:
        no enabled flows

    Stability:
        experimental
    """
    generateSecret: bool
    """Whether to generate a client secret.

    Default:
        false

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-cognito.UserPoolClientProps", jsii_struct_bases=[_UserPoolClientProps])
class UserPoolClientProps(_UserPoolClientProps):
    """
    Stability:
        experimental
    """
    userPool: "IUserPool"
    """The UserPool resource this client will have access to.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-cognito.UserPoolProps", jsii_struct_bases=[])
class UserPoolProps(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    autoVerifiedAttributes: typing.List["UserPoolAttribute"]
    """Attributes which Cognito will automatically send a verification message to. Must be either EMAIL, PHONE, or both.

    Default:
        - No auto verification.

    Stability:
        experimental
    """

    lambdaTriggers: "UserPoolTriggers"
    """Lambda functions to use for supported Cognito triggers.

    Default:
        - No Lambda triggers.

    Stability:
        experimental
    """

    poolName: str
    """Name of the user pool.

    Default:
        - Unique ID.

    Stability:
        experimental
    """

    signInType: "SignInType"
    """Method used for user registration & sign in. Allows either username with aliases OR sign in with email, phone, or both.

    Default:
        SignInType.Username

    Stability:
        experimental
    """

    usernameAliasAttributes: typing.List["UserPoolAttribute"]
    """Attributes to allow as username alias. Only valid if signInType is USERNAME.

    Default:
        - No alias.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-cognito.UserPoolTriggers", jsii_struct_bases=[])
class UserPoolTriggers(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    createAuthChallenge: aws_cdk.aws_lambda.IFunction
    """Creates an authentication challenge.

    See:
        https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-create-auth-challenge.html
    Stability:
        experimental
    """

    customMessage: aws_cdk.aws_lambda.IFunction
    """A custom Message AWS Lambda trigger.

    See:
        https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-custom-message.html
    Stability:
        experimental
    """

    defineAuthChallenge: aws_cdk.aws_lambda.IFunction
    """Defines the authentication challenge.

    See:
        https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-define-auth-challenge.html
    Stability:
        experimental
    """

    postAuthentication: aws_cdk.aws_lambda.IFunction
    """A post-authentication AWS Lambda trigger.

    See:
        https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-post-authentication.html
    Stability:
        experimental
    """

    postConfirmation: aws_cdk.aws_lambda.IFunction
    """A post-confirmation AWS Lambda trigger.

    See:
        https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-post-confirmation.html
    Stability:
        experimental
    """

    preAuthentication: aws_cdk.aws_lambda.IFunction
    """A pre-authentication AWS Lambda trigger.

    See:
        https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-pre-authentication.html
    Stability:
        experimental
    """

    preSignUp: aws_cdk.aws_lambda.IFunction
    """A pre-registration AWS Lambda trigger.

    See:
        https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-pre-sign-up.html
    Stability:
        experimental
    """

    verifyAuthChallengeResponse: aws_cdk.aws_lambda.IFunction
    """Verifies the authentication challenge response.

    See:
        https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-verify-auth-challenge-response.html
    Stability:
        experimental
    """

__all__ = ["AuthFlow", "CfnIdentityPool", "CfnIdentityPoolProps", "CfnIdentityPoolRoleAttachment", "CfnIdentityPoolRoleAttachmentProps", "CfnUserPool", "CfnUserPoolClient", "CfnUserPoolClientProps", "CfnUserPoolGroup", "CfnUserPoolGroupProps", "CfnUserPoolProps", "CfnUserPoolUser", "CfnUserPoolUserProps", "CfnUserPoolUserToGroupAttachment", "CfnUserPoolUserToGroupAttachmentProps", "IUserPool", "SignInType", "UserPool", "UserPoolAttribute", "UserPoolAttributes", "UserPoolClient", "UserPoolClientProps", "UserPoolProps", "UserPoolTriggers", "__jsii_assembly__"]

publication.publish()
