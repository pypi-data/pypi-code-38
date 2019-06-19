import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-amplify", "0.35.0", __name__, "aws-amplify@0.35.0.jsii.tgz")
class CfnApp(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-amplify.CfnApp"):
    """A CloudFormation ``AWS::Amplify::App``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Amplify::App
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, repository: str, access_token: typing.Optional[str]=None, basic_auth_config: typing.Optional[typing.Union[typing.Optional["BasicAuthConfigProperty"], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, build_spec: typing.Optional[str]=None, custom_rules: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CustomRuleProperty"]]]]]=None, description: typing.Optional[str]=None, environment_variables: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "EnvironmentVariableProperty"]]]]]=None, iam_service_role: typing.Optional[str]=None, oauth_token: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::Amplify::App``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::Amplify::App.Name``.
            repository: ``AWS::Amplify::App.Repository``.
            accessToken: ``AWS::Amplify::App.AccessToken``.
            basicAuthConfig: ``AWS::Amplify::App.BasicAuthConfig``.
            buildSpec: ``AWS::Amplify::App.BuildSpec``.
            customRules: ``AWS::Amplify::App.CustomRules``.
            description: ``AWS::Amplify::App.Description``.
            environmentVariables: ``AWS::Amplify::App.EnvironmentVariables``.
            iamServiceRole: ``AWS::Amplify::App.IAMServiceRole``.
            oauthToken: ``AWS::Amplify::App.OauthToken``.
            tags: ``AWS::Amplify::App.Tags``.

        Stability:
            experimental
        """
        props: CfnAppProps = {"name": name, "repository": repository}

        if access_token is not None:
            props["accessToken"] = access_token

        if basic_auth_config is not None:
            props["basicAuthConfig"] = basic_auth_config

        if build_spec is not None:
            props["buildSpec"] = build_spec

        if custom_rules is not None:
            props["customRules"] = custom_rules

        if description is not None:
            props["description"] = description

        if environment_variables is not None:
            props["environmentVariables"] = environment_variables

        if iam_service_role is not None:
            props["iamServiceRole"] = iam_service_role

        if oauth_token is not None:
            props["oauthToken"] = oauth_token

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnApp, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrAppId")
    def attr_app_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            AppId
        """
        return jsii.get(self, "attrAppId")

    @property
    @jsii.member(jsii_name="attrAppName")
    def attr_app_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            AppName
        """
        return jsii.get(self, "attrAppName")

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
    @jsii.member(jsii_name="attrDefaultDomain")
    def attr_default_domain(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            DefaultDomain
        """
        return jsii.get(self, "attrDefaultDomain")

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
        """``AWS::Amplify::App.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::Amplify::App.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-name
        Stability:
            experimental
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="repository")
    def repository(self) -> str:
        """``AWS::Amplify::App.Repository``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-repository
        Stability:
            experimental
        """
        return jsii.get(self, "repository")

    @repository.setter
    def repository(self, value: str):
        return jsii.set(self, "repository", value)

    @property
    @jsii.member(jsii_name="accessToken")
    def access_token(self) -> typing.Optional[str]:
        """``AWS::Amplify::App.AccessToken``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-accesstoken
        Stability:
            experimental
        """
        return jsii.get(self, "accessToken")

    @access_token.setter
    def access_token(self, value: typing.Optional[str]):
        return jsii.set(self, "accessToken", value)

    @property
    @jsii.member(jsii_name="basicAuthConfig")
    def basic_auth_config(self) -> typing.Optional[typing.Union[typing.Optional["BasicAuthConfigProperty"], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::Amplify::App.BasicAuthConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-basicauthconfig
        Stability:
            experimental
        """
        return jsii.get(self, "basicAuthConfig")

    @basic_auth_config.setter
    def basic_auth_config(self, value: typing.Optional[typing.Union[typing.Optional["BasicAuthConfigProperty"], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "basicAuthConfig", value)

    @property
    @jsii.member(jsii_name="buildSpec")
    def build_spec(self) -> typing.Optional[str]:
        """``AWS::Amplify::App.BuildSpec``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-buildspec
        Stability:
            experimental
        """
        return jsii.get(self, "buildSpec")

    @build_spec.setter
    def build_spec(self, value: typing.Optional[str]):
        return jsii.set(self, "buildSpec", value)

    @property
    @jsii.member(jsii_name="customRules")
    def custom_rules(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CustomRuleProperty"]]]]]:
        """``AWS::Amplify::App.CustomRules``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-customrules
        Stability:
            experimental
        """
        return jsii.get(self, "customRules")

    @custom_rules.setter
    def custom_rules(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CustomRuleProperty"]]]]]):
        return jsii.set(self, "customRules", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::Amplify::App.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-description
        Stability:
            experimental
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="environmentVariables")
    def environment_variables(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "EnvironmentVariableProperty"]]]]]:
        """``AWS::Amplify::App.EnvironmentVariables``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-environmentvariables
        Stability:
            experimental
        """
        return jsii.get(self, "environmentVariables")

    @environment_variables.setter
    def environment_variables(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "EnvironmentVariableProperty"]]]]]):
        return jsii.set(self, "environmentVariables", value)

    @property
    @jsii.member(jsii_name="iamServiceRole")
    def iam_service_role(self) -> typing.Optional[str]:
        """``AWS::Amplify::App.IAMServiceRole``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-iamservicerole
        Stability:
            experimental
        """
        return jsii.get(self, "iamServiceRole")

    @iam_service_role.setter
    def iam_service_role(self, value: typing.Optional[str]):
        return jsii.set(self, "iamServiceRole", value)

    @property
    @jsii.member(jsii_name="oauthToken")
    def oauth_token(self) -> typing.Optional[str]:
        """``AWS::Amplify::App.OauthToken``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-oauthtoken
        Stability:
            experimental
        """
        return jsii.get(self, "oauthToken")

    @oauth_token.setter
    def oauth_token(self, value: typing.Optional[str]):
        return jsii.set(self, "oauthToken", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _BasicAuthConfigProperty(jsii.compat.TypedDict, total=False):
        enableBasicAuth: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnApp.BasicAuthConfigProperty.EnableBasicAuth``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-basicauthconfig.html#cfn-amplify-app-basicauthconfig-enablebasicauth
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-amplify.CfnApp.BasicAuthConfigProperty", jsii_struct_bases=[_BasicAuthConfigProperty])
    class BasicAuthConfigProperty(_BasicAuthConfigProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-basicauthconfig.html
        Stability:
            experimental
        """
        password: str
        """``CfnApp.BasicAuthConfigProperty.Password``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-basicauthconfig.html#cfn-amplify-app-basicauthconfig-password
        Stability:
            experimental
        """

        username: str
        """``CfnApp.BasicAuthConfigProperty.Username``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-basicauthconfig.html#cfn-amplify-app-basicauthconfig-username
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _CustomRuleProperty(jsii.compat.TypedDict, total=False):
        condition: str
        """``CfnApp.CustomRuleProperty.Condition``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-customrule.html#cfn-amplify-app-customrule-condition
        Stability:
            experimental
        """
        status: str
        """``CfnApp.CustomRuleProperty.Status``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-customrule.html#cfn-amplify-app-customrule-status
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-amplify.CfnApp.CustomRuleProperty", jsii_struct_bases=[_CustomRuleProperty])
    class CustomRuleProperty(_CustomRuleProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-customrule.html
        Stability:
            experimental
        """
        source: str
        """``CfnApp.CustomRuleProperty.Source``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-customrule.html#cfn-amplify-app-customrule-source
        Stability:
            experimental
        """

        target: str
        """``CfnApp.CustomRuleProperty.Target``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-customrule.html#cfn-amplify-app-customrule-target
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-amplify.CfnApp.EnvironmentVariableProperty", jsii_struct_bases=[])
    class EnvironmentVariableProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-environmentvariable.html
        Stability:
            experimental
        """
        name: str
        """``CfnApp.EnvironmentVariableProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-environmentvariable.html#cfn-amplify-app-environmentvariable-name
        Stability:
            experimental
        """

        value: str
        """``CfnApp.EnvironmentVariableProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-environmentvariable.html#cfn-amplify-app-environmentvariable-value
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-amplify.CfnApp.TokenProperty", jsii_struct_bases=[])
    class TokenProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-token.html
        Stability:
            experimental
        """
        key: str
        """``CfnApp.TokenProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-token.html#cfn-amplify-app-token-key
        Stability:
            experimental
        """

        value: str
        """``CfnApp.TokenProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-app-token.html#cfn-amplify-app-token-value
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnAppProps(jsii.compat.TypedDict, total=False):
    accessToken: str
    """``AWS::Amplify::App.AccessToken``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-accesstoken
    Stability:
        experimental
    """
    basicAuthConfig: typing.Union["CfnApp.BasicAuthConfigProperty", aws_cdk.cdk.IResolvable]
    """``AWS::Amplify::App.BasicAuthConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-basicauthconfig
    Stability:
        experimental
    """
    buildSpec: str
    """``AWS::Amplify::App.BuildSpec``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-buildspec
    Stability:
        experimental
    """
    customRules: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnApp.CustomRuleProperty"]]]
    """``AWS::Amplify::App.CustomRules``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-customrules
    Stability:
        experimental
    """
    description: str
    """``AWS::Amplify::App.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-description
    Stability:
        experimental
    """
    environmentVariables: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnApp.EnvironmentVariableProperty"]]]
    """``AWS::Amplify::App.EnvironmentVariables``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-environmentvariables
    Stability:
        experimental
    """
    iamServiceRole: str
    """``AWS::Amplify::App.IAMServiceRole``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-iamservicerole
    Stability:
        experimental
    """
    oauthToken: str
    """``AWS::Amplify::App.OauthToken``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-oauthtoken
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::Amplify::App.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-amplify.CfnAppProps", jsii_struct_bases=[_CfnAppProps])
class CfnAppProps(_CfnAppProps):
    """Properties for defining a ``AWS::Amplify::App``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html
    Stability:
        experimental
    """
    name: str
    """``AWS::Amplify::App.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-name
    Stability:
        experimental
    """

    repository: str
    """``AWS::Amplify::App.Repository``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-app.html#cfn-amplify-app-repository
    Stability:
        experimental
    """

class CfnBranch(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-amplify.CfnBranch"):
    """A CloudFormation ``AWS::Amplify::Branch``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Amplify::Branch
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, app_id: str, branch_name: str, basic_auth_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["BasicAuthConfigProperty"]]]=None, build_spec: typing.Optional[str]=None, description: typing.Optional[str]=None, environment_variables: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "EnvironmentVariableProperty"]]]]]=None, stage: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::Amplify::Branch``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            appId: ``AWS::Amplify::Branch.AppId``.
            branchName: ``AWS::Amplify::Branch.BranchName``.
            basicAuthConfig: ``AWS::Amplify::Branch.BasicAuthConfig``.
            buildSpec: ``AWS::Amplify::Branch.BuildSpec``.
            description: ``AWS::Amplify::Branch.Description``.
            environmentVariables: ``AWS::Amplify::Branch.EnvironmentVariables``.
            stage: ``AWS::Amplify::Branch.Stage``.
            tags: ``AWS::Amplify::Branch.Tags``.

        Stability:
            experimental
        """
        props: CfnBranchProps = {"appId": app_id, "branchName": branch_name}

        if basic_auth_config is not None:
            props["basicAuthConfig"] = basic_auth_config

        if build_spec is not None:
            props["buildSpec"] = build_spec

        if description is not None:
            props["description"] = description

        if environment_variables is not None:
            props["environmentVariables"] = environment_variables

        if stage is not None:
            props["stage"] = stage

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnBranch, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrBranchName")
    def attr_branch_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            BranchName
        """
        return jsii.get(self, "attrBranchName")

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
        """``AWS::Amplify::Branch.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="appId")
    def app_id(self) -> str:
        """``AWS::Amplify::Branch.AppId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-appid
        Stability:
            experimental
        """
        return jsii.get(self, "appId")

    @app_id.setter
    def app_id(self, value: str):
        return jsii.set(self, "appId", value)

    @property
    @jsii.member(jsii_name="branchName")
    def branch_name(self) -> str:
        """``AWS::Amplify::Branch.BranchName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-branchname
        Stability:
            experimental
        """
        return jsii.get(self, "branchName")

    @branch_name.setter
    def branch_name(self, value: str):
        return jsii.set(self, "branchName", value)

    @property
    @jsii.member(jsii_name="basicAuthConfig")
    def basic_auth_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["BasicAuthConfigProperty"]]]:
        """``AWS::Amplify::Branch.BasicAuthConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-basicauthconfig
        Stability:
            experimental
        """
        return jsii.get(self, "basicAuthConfig")

    @basic_auth_config.setter
    def basic_auth_config(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["BasicAuthConfigProperty"]]]):
        return jsii.set(self, "basicAuthConfig", value)

    @property
    @jsii.member(jsii_name="buildSpec")
    def build_spec(self) -> typing.Optional[str]:
        """``AWS::Amplify::Branch.BuildSpec``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-buildspec
        Stability:
            experimental
        """
        return jsii.get(self, "buildSpec")

    @build_spec.setter
    def build_spec(self, value: typing.Optional[str]):
        return jsii.set(self, "buildSpec", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::Amplify::Branch.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-description
        Stability:
            experimental
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="environmentVariables")
    def environment_variables(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "EnvironmentVariableProperty"]]]]]:
        """``AWS::Amplify::Branch.EnvironmentVariables``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-environmentvariables
        Stability:
            experimental
        """
        return jsii.get(self, "environmentVariables")

    @environment_variables.setter
    def environment_variables(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "EnvironmentVariableProperty"]]]]]):
        return jsii.set(self, "environmentVariables", value)

    @property
    @jsii.member(jsii_name="stage")
    def stage(self) -> typing.Optional[str]:
        """``AWS::Amplify::Branch.Stage``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-stage
        Stability:
            experimental
        """
        return jsii.get(self, "stage")

    @stage.setter
    def stage(self, value: typing.Optional[str]):
        return jsii.set(self, "stage", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _BasicAuthConfigProperty(jsii.compat.TypedDict, total=False):
        enableBasicAuth: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnBranch.BasicAuthConfigProperty.EnableBasicAuth``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-branch-basicauthconfig.html#cfn-amplify-branch-basicauthconfig-enablebasicauth
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-amplify.CfnBranch.BasicAuthConfigProperty", jsii_struct_bases=[_BasicAuthConfigProperty])
    class BasicAuthConfigProperty(_BasicAuthConfigProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-branch-basicauthconfig.html
        Stability:
            experimental
        """
        password: str
        """``CfnBranch.BasicAuthConfigProperty.Password``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-branch-basicauthconfig.html#cfn-amplify-branch-basicauthconfig-password
        Stability:
            experimental
        """

        username: str
        """``CfnBranch.BasicAuthConfigProperty.Username``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-branch-basicauthconfig.html#cfn-amplify-branch-basicauthconfig-username
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-amplify.CfnBranch.EnvironmentVariableProperty", jsii_struct_bases=[])
    class EnvironmentVariableProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-branch-environmentvariable.html
        Stability:
            experimental
        """
        name: str
        """``CfnBranch.EnvironmentVariableProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-branch-environmentvariable.html#cfn-amplify-branch-environmentvariable-name
        Stability:
            experimental
        """

        value: str
        """``CfnBranch.EnvironmentVariableProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-branch-environmentvariable.html#cfn-amplify-branch-environmentvariable-value
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnBranchProps(jsii.compat.TypedDict, total=False):
    basicAuthConfig: typing.Union[aws_cdk.cdk.IResolvable, "CfnBranch.BasicAuthConfigProperty"]
    """``AWS::Amplify::Branch.BasicAuthConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-basicauthconfig
    Stability:
        experimental
    """
    buildSpec: str
    """``AWS::Amplify::Branch.BuildSpec``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-buildspec
    Stability:
        experimental
    """
    description: str
    """``AWS::Amplify::Branch.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-description
    Stability:
        experimental
    """
    environmentVariables: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnBranch.EnvironmentVariableProperty"]]]
    """``AWS::Amplify::Branch.EnvironmentVariables``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-environmentvariables
    Stability:
        experimental
    """
    stage: str
    """``AWS::Amplify::Branch.Stage``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-stage
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::Amplify::Branch.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-amplify.CfnBranchProps", jsii_struct_bases=[_CfnBranchProps])
class CfnBranchProps(_CfnBranchProps):
    """Properties for defining a ``AWS::Amplify::Branch``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html
    Stability:
        experimental
    """
    appId: str
    """``AWS::Amplify::Branch.AppId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-appid
    Stability:
        experimental
    """

    branchName: str
    """``AWS::Amplify::Branch.BranchName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-branch.html#cfn-amplify-branch-branchname
    Stability:
        experimental
    """

class CfnDomain(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-amplify.CfnDomain"):
    """A CloudFormation ``AWS::Amplify::Domain``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-domain.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Amplify::Domain
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, app_id: str, domain_name: str, sub_domain_settings: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "SubDomainSettingProperty"]]]) -> None:
        """Create a new ``AWS::Amplify::Domain``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            appId: ``AWS::Amplify::Domain.AppId``.
            domainName: ``AWS::Amplify::Domain.DomainName``.
            subDomainSettings: ``AWS::Amplify::Domain.SubDomainSettings``.

        Stability:
            experimental
        """
        props: CfnDomainProps = {"appId": app_id, "domainName": domain_name, "subDomainSettings": sub_domain_settings}

        jsii.create(CfnDomain, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrCertificateRecord")
    def attr_certificate_record(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            CertificateRecord
        """
        return jsii.get(self, "attrCertificateRecord")

    @property
    @jsii.member(jsii_name="attrDomainName")
    def attr_domain_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            DomainName
        """
        return jsii.get(self, "attrDomainName")

    @property
    @jsii.member(jsii_name="attrDomainStatus")
    def attr_domain_status(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            DomainStatus
        """
        return jsii.get(self, "attrDomainStatus")

    @property
    @jsii.member(jsii_name="attrStatusReason")
    def attr_status_reason(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            StatusReason
        """
        return jsii.get(self, "attrStatusReason")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="appId")
    def app_id(self) -> str:
        """``AWS::Amplify::Domain.AppId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-domain.html#cfn-amplify-domain-appid
        Stability:
            experimental
        """
        return jsii.get(self, "appId")

    @app_id.setter
    def app_id(self, value: str):
        return jsii.set(self, "appId", value)

    @property
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> str:
        """``AWS::Amplify::Domain.DomainName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-domain.html#cfn-amplify-domain-domainname
        Stability:
            experimental
        """
        return jsii.get(self, "domainName")

    @domain_name.setter
    def domain_name(self, value: str):
        return jsii.set(self, "domainName", value)

    @property
    @jsii.member(jsii_name="subDomainSettings")
    def sub_domain_settings(self) -> typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "SubDomainSettingProperty"]]]:
        """``AWS::Amplify::Domain.SubDomainSettings``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-domain.html#cfn-amplify-domain-subdomainsettings
        Stability:
            experimental
        """
        return jsii.get(self, "subDomainSettings")

    @sub_domain_settings.setter
    def sub_domain_settings(self, value: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "SubDomainSettingProperty"]]]):
        return jsii.set(self, "subDomainSettings", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-amplify.CfnDomain.SubDomainSettingProperty", jsii_struct_bases=[])
    class SubDomainSettingProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-domain-subdomainsetting.html
        Stability:
            experimental
        """
        branchName: str
        """``CfnDomain.SubDomainSettingProperty.BranchName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-domain-subdomainsetting.html#cfn-amplify-domain-subdomainsetting-branchname
        Stability:
            experimental
        """

        prefix: str
        """``CfnDomain.SubDomainSettingProperty.Prefix``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amplify-domain-subdomainsetting.html#cfn-amplify-domain-subdomainsetting-prefix
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-amplify.CfnDomainProps", jsii_struct_bases=[])
class CfnDomainProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::Amplify::Domain``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-domain.html
    Stability:
        experimental
    """
    appId: str
    """``AWS::Amplify::Domain.AppId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-domain.html#cfn-amplify-domain-appid
    Stability:
        experimental
    """

    domainName: str
    """``AWS::Amplify::Domain.DomainName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-domain.html#cfn-amplify-domain-domainname
    Stability:
        experimental
    """

    subDomainSettings: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnDomain.SubDomainSettingProperty"]]]
    """``AWS::Amplify::Domain.SubDomainSettings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amplify-domain.html#cfn-amplify-domain-subdomainsettings
    Stability:
        experimental
    """

__all__ = ["CfnApp", "CfnAppProps", "CfnBranch", "CfnBranchProps", "CfnDomain", "CfnDomainProps", "__jsii_assembly__"]

publication.publish()
