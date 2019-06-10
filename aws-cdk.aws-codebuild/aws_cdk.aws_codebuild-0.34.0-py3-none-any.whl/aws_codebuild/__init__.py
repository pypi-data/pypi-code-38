import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.assets
import aws_cdk.assets_docker
import aws_cdk.aws_cloudwatch
import aws_cdk.aws_codecommit
import aws_cdk.aws_ec2
import aws_cdk.aws_ecr
import aws_cdk.aws_events
import aws_cdk.aws_iam
import aws_cdk.aws_kms
import aws_cdk.aws_s3
import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-codebuild", "0.34.0", __name__, "aws-codebuild@0.34.0.jsii.tgz")
@jsii.data_type(jsii_type="@aws-cdk/aws-codebuild.BucketCacheOptions", jsii_struct_bases=[])
class BucketCacheOptions(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    prefix: str
    """The prefix to use to store the cache in the bucket.

    Stability:
        experimental
    """

class BuildArtifacts(metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/aws-codebuild.BuildArtifacts"):
    """Artifacts definition for a CodeBuild Project.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _BuildArtifactsProxy

    def __init__(self, *, identifier: typing.Optional[str]=None) -> None:
        """
        Arguments:
            props: -
            identifier: The artifact identifier. This property is required on secondary artifacts.

        Stability:
            experimental
        """
        props: BuildArtifactsProps = {}

        if identifier is not None:
            props["identifier"] = identifier

        jsii.create(BuildArtifacts, self, [props])

    @jsii.member(jsii_name="toArtifactsJSON")
    def to_artifacts_json(self) -> "CfnProject.ArtifactsProperty":
        """
        Stability:
            experimental
        """
        return jsii.invoke(self, "toArtifactsJSON", [])

    @jsii.member(jsii_name="toArtifactsProperty")
    def _to_artifacts_property(self) -> typing.Any:
        """
        Stability:
            experimental
        """
        return jsii.invoke(self, "toArtifactsProperty", [])

    @property
    @jsii.member(jsii_name="type")
    @abc.abstractmethod
    def _type(self) -> str:
        """
        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="identifier")
    def identifier(self) -> typing.Optional[str]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "identifier")


class _BuildArtifactsProxy(BuildArtifacts):
    @property
    @jsii.member(jsii_name="type")
    def _type(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "type")


@jsii.data_type(jsii_type="@aws-cdk/aws-codebuild.BuildArtifactsProps", jsii_struct_bases=[])
class BuildArtifactsProps(jsii.compat.TypedDict, total=False):
    """Properties common to all Artifacts classes.

    Stability:
        experimental
    """
    identifier: str
    """The artifact identifier. This property is required on secondary artifacts.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-codebuild.BuildEnvironment", jsii_struct_bases=[])
class BuildEnvironment(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    buildImage: "IBuildImage"
    """The image used for the builds.

    Default:
        LinuxBuildImage.STANDARD_1_0

    Stability:
        experimental
    """

    computeType: "ComputeType"
    """The type of compute to use for this build. See the {@link ComputeType} enum for the possible values.

    Default:
        taken from {@link #buildImage#defaultComputeType}

    Stability:
        experimental
    """

    environmentVariables: typing.Mapping[str,"BuildEnvironmentVariable"]
    """The environment variables that your builds can use.

    Stability:
        experimental
    """

    privileged: bool
    """Indicates how the project builds Docker images.

    Specify true to enable
    running the Docker daemon inside a Docker container. This value must be
    set to true only if this build project will be used to build Docker
    images, and the specified build environment image is not one provided by
    AWS CodeBuild with Docker support. Otherwise, all associated builds that
    attempt to interact with the Docker daemon will fail.

    Default:
        false

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _BuildEnvironmentVariable(jsii.compat.TypedDict, total=False):
    type: "BuildEnvironmentVariableType"
    """The type of environment variable.

    Default:
        PlainText

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-codebuild.BuildEnvironmentVariable", jsii_struct_bases=[_BuildEnvironmentVariable])
class BuildEnvironmentVariable(_BuildEnvironmentVariable):
    """
    Stability:
        experimental
    """
    value: typing.Any
    """The value of the environment variable (or the name of the parameter in the SSM parameter store.).

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-codebuild.BuildEnvironmentVariableType")
class BuildEnvironmentVariableType(enum.Enum):
    """
    Stability:
        experimental
    """
    PlainText = "PlainText"
    """An environment variable in plaintext format.

    Stability:
        experimental
    """
    ParameterStore = "ParameterStore"
    """An environment variable stored in Systems Manager Parameter Store.

    Stability:
        experimental
    """

class BuildSource(metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/aws-codebuild.BuildSource"):
    """Source provider definition for a CodeBuild Project.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _BuildSourceProxy

    def __init__(self, *, identifier: typing.Optional[str]=None) -> None:
        """
        Arguments:
            props: -
            identifier: The source identifier. This property is required on secondary sources.

        Stability:
            experimental
        """
        props: BuildSourceProps = {}

        if identifier is not None:
            props["identifier"] = identifier

        jsii.create(BuildSource, self, [props])

    @jsii.member(jsii_name="toSourceProperty")
    def _to_source_property(self) -> typing.Any:
        """
        Stability:
            experimental
        """
        return jsii.invoke(self, "toSourceProperty", [])

    @property
    @jsii.member(jsii_name="badgeSupported")
    def badge_supported(self) -> bool:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "badgeSupported")

    @property
    @jsii.member(jsii_name="type")
    @abc.abstractmethod
    def type(self) -> "SourceType":
        """
        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="identifier")
    def identifier(self) -> typing.Optional[str]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "identifier")


class _BuildSourceProxy(BuildSource):
    @property
    @jsii.member(jsii_name="type")
    def type(self) -> "SourceType":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "type")


@jsii.data_type(jsii_type="@aws-cdk/aws-codebuild.BuildSourceProps", jsii_struct_bases=[])
class BuildSourceProps(jsii.compat.TypedDict, total=False):
    """Properties common to all Source classes.

    Stability:
        experimental
    """
    identifier: str
    """The source identifier. This property is required on secondary sources.

    Stability:
        experimental
    """

class Cache(metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/aws-codebuild.Cache"):
    """Cache options for CodeBuild Project. A cache can store reusable pieces of your build environment and use them across multiple builds.

    See:
        https://docs.aws.amazon.com/codebuild/latest/userguide/build-caching.html
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _CacheProxy

    def __init__(self) -> None:
        jsii.create(Cache, self, [])

    @jsii.member(jsii_name="bucket")
    @classmethod
    def bucket(cls, bucket: aws_cdk.aws_s3.IBucket, *, prefix: typing.Optional[str]=None) -> "Cache":
        """Create an S3 caching strategy.

        Arguments:
            bucket: the S3 bucket to use for caching.
            options: additional options to pass to the S3 caching.
            prefix: The prefix to use to store the cache in the bucket.

        Stability:
            experimental
        """
        options: BucketCacheOptions = {}

        if prefix is not None:
            options["prefix"] = prefix

        return jsii.sinvoke(cls, "bucket", [bucket, options])

    @jsii.member(jsii_name="local")
    @classmethod
    def local(cls, *modes: "LocalCacheMode") -> "Cache":
        """Create a local caching strategy.

        Arguments:
            modes: the mode(s) to enable for local caching.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "local", [*modes])

    @jsii.member(jsii_name="none")
    @classmethod
    def none(cls) -> "Cache":
        """
        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "none", [])


class _CacheProxy(Cache):
    pass

class CfnProject(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codebuild.CfnProject"):
    """A CloudFormation ``AWS::CodeBuild::Project``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html
    Stability:
        experimental
    cloudformationResource:
        AWS::CodeBuild::Project
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, artifacts: typing.Union[aws_cdk.cdk.Token, "ArtifactsProperty"], environment: typing.Union[aws_cdk.cdk.Token, "EnvironmentProperty"], service_role: str, source: typing.Union[aws_cdk.cdk.Token, "SourceProperty"], badge_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, cache: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["ProjectCacheProperty"]]]=None, description: typing.Optional[str]=None, encryption_key: typing.Optional[str]=None, logs_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["LogsConfigProperty"]]]=None, name: typing.Optional[str]=None, queued_timeout_in_minutes: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, secondary_artifacts: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "ArtifactsProperty"]]]]]=None, secondary_sources: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "SourceProperty"]]]]]=None, secondary_source_versions: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "ProjectSourceVersionProperty"]]]]]=None, source_version: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, timeout_in_minutes: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, triggers: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["ProjectTriggersProperty"]]]=None, vpc_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["VpcConfigProperty"]]]=None) -> None:
        """Create a new ``AWS::CodeBuild::Project``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            artifacts: ``AWS::CodeBuild::Project.Artifacts``.
            environment: ``AWS::CodeBuild::Project.Environment``.
            serviceRole: ``AWS::CodeBuild::Project.ServiceRole``.
            source: ``AWS::CodeBuild::Project.Source``.
            badgeEnabled: ``AWS::CodeBuild::Project.BadgeEnabled``.
            cache: ``AWS::CodeBuild::Project.Cache``.
            description: ``AWS::CodeBuild::Project.Description``.
            encryptionKey: ``AWS::CodeBuild::Project.EncryptionKey``.
            logsConfig: ``AWS::CodeBuild::Project.LogsConfig``.
            name: ``AWS::CodeBuild::Project.Name``.
            queuedTimeoutInMinutes: ``AWS::CodeBuild::Project.QueuedTimeoutInMinutes``.
            secondaryArtifacts: ``AWS::CodeBuild::Project.SecondaryArtifacts``.
            secondarySources: ``AWS::CodeBuild::Project.SecondarySources``.
            secondarySourceVersions: ``AWS::CodeBuild::Project.SecondarySourceVersions``.
            sourceVersion: ``AWS::CodeBuild::Project.SourceVersion``.
            tags: ``AWS::CodeBuild::Project.Tags``.
            timeoutInMinutes: ``AWS::CodeBuild::Project.TimeoutInMinutes``.
            triggers: ``AWS::CodeBuild::Project.Triggers``.
            vpcConfig: ``AWS::CodeBuild::Project.VpcConfig``.

        Stability:
            experimental
        """
        props: CfnProjectProps = {"artifacts": artifacts, "environment": environment, "serviceRole": service_role, "source": source}

        if badge_enabled is not None:
            props["badgeEnabled"] = badge_enabled

        if cache is not None:
            props["cache"] = cache

        if description is not None:
            props["description"] = description

        if encryption_key is not None:
            props["encryptionKey"] = encryption_key

        if logs_config is not None:
            props["logsConfig"] = logs_config

        if name is not None:
            props["name"] = name

        if queued_timeout_in_minutes is not None:
            props["queuedTimeoutInMinutes"] = queued_timeout_in_minutes

        if secondary_artifacts is not None:
            props["secondaryArtifacts"] = secondary_artifacts

        if secondary_sources is not None:
            props["secondarySources"] = secondary_sources

        if secondary_source_versions is not None:
            props["secondarySourceVersions"] = secondary_source_versions

        if source_version is not None:
            props["sourceVersion"] = source_version

        if tags is not None:
            props["tags"] = tags

        if timeout_in_minutes is not None:
            props["timeoutInMinutes"] = timeout_in_minutes

        if triggers is not None:
            props["triggers"] = triggers

        if vpc_config is not None:
            props["vpcConfig"] = vpc_config

        jsii.create(CfnProject, self, [scope, id, props])

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
    @jsii.member(jsii_name="projectArn")
    def project_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "projectArn")

    @property
    @jsii.member(jsii_name="projectName")
    def project_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "projectName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnProjectProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.cdk.TagManager:
        """The ``TagManager`` handles setting, removing and formatting tags.

        Tags should be managed either passing them as properties during
        initiation or by calling methods on this object. If both techniques are
        used only the tags from the TagManager will be used. ``Tag`` (aspect)
        will use the manager.

        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ArtifactsProperty(jsii.compat.TypedDict, total=False):
        artifactIdentifier: str
        """``CfnProject.ArtifactsProperty.ArtifactIdentifier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-artifacts.html#cfn-codebuild-project-artifacts-artifactidentifier
        Stability:
            experimental
        """
        encryptionDisabled: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnProject.ArtifactsProperty.EncryptionDisabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-artifacts.html#cfn-codebuild-project-artifacts-encryptiondisabled
        Stability:
            experimental
        """
        location: str
        """``CfnProject.ArtifactsProperty.Location``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-artifacts.html#cfn-codebuild-project-artifacts-location
        Stability:
            experimental
        """
        name: str
        """``CfnProject.ArtifactsProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-artifacts.html#cfn-codebuild-project-artifacts-name
        Stability:
            experimental
        """
        namespaceType: str
        """``CfnProject.ArtifactsProperty.NamespaceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-artifacts.html#cfn-codebuild-project-artifacts-namespacetype
        Stability:
            experimental
        """
        overrideArtifactName: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnProject.ArtifactsProperty.OverrideArtifactName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-artifacts.html#cfn-codebuild-project-artifacts-overrideartifactname
        Stability:
            experimental
        """
        packaging: str
        """``CfnProject.ArtifactsProperty.Packaging``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-artifacts.html#cfn-codebuild-project-artifacts-packaging
        Stability:
            experimental
        """
        path: str
        """``CfnProject.ArtifactsProperty.Path``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-artifacts.html#cfn-codebuild-project-artifacts-path
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codebuild.CfnProject.ArtifactsProperty", jsii_struct_bases=[_ArtifactsProperty])
    class ArtifactsProperty(_ArtifactsProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-artifacts.html
        Stability:
            experimental
        """
        type: str
        """``CfnProject.ArtifactsProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-artifacts.html#cfn-codebuild-project-artifacts-type
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _CloudWatchLogsConfigProperty(jsii.compat.TypedDict, total=False):
        groupName: str
        """``CfnProject.CloudWatchLogsConfigProperty.GroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-cloudwatchlogsconfig.html#cfn-codebuild-project-cloudwatchlogsconfig-groupname
        Stability:
            experimental
        """
        streamName: str
        """``CfnProject.CloudWatchLogsConfigProperty.StreamName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-cloudwatchlogsconfig.html#cfn-codebuild-project-cloudwatchlogsconfig-streamname
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codebuild.CfnProject.CloudWatchLogsConfigProperty", jsii_struct_bases=[_CloudWatchLogsConfigProperty])
    class CloudWatchLogsConfigProperty(_CloudWatchLogsConfigProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-cloudwatchlogsconfig.html
        Stability:
            experimental
        """
        status: str
        """``CfnProject.CloudWatchLogsConfigProperty.Status``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-cloudwatchlogsconfig.html#cfn-codebuild-project-cloudwatchlogsconfig-status
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _EnvironmentProperty(jsii.compat.TypedDict, total=False):
        certificate: str
        """``CfnProject.EnvironmentProperty.Certificate``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-environment.html#cfn-codebuild-project-environment-certificate
        Stability:
            experimental
        """
        environmentVariables: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnProject.EnvironmentVariableProperty"]]]
        """``CfnProject.EnvironmentProperty.EnvironmentVariables``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-environment.html#cfn-codebuild-project-environment-environmentvariables
        Stability:
            experimental
        """
        imagePullCredentialsType: str
        """``CfnProject.EnvironmentProperty.ImagePullCredentialsType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-environment.html#cfn-codebuild-project-environment-imagepullcredentialstype
        Stability:
            experimental
        """
        privilegedMode: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnProject.EnvironmentProperty.PrivilegedMode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-environment.html#cfn-codebuild-project-environment-privilegedmode
        Stability:
            experimental
        """
        registryCredential: typing.Union[aws_cdk.cdk.Token, "CfnProject.RegistryCredentialProperty"]
        """``CfnProject.EnvironmentProperty.RegistryCredential``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-environment.html#cfn-codebuild-project-environment-registrycredential
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codebuild.CfnProject.EnvironmentProperty", jsii_struct_bases=[_EnvironmentProperty])
    class EnvironmentProperty(_EnvironmentProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-environment.html
        Stability:
            experimental
        """
        computeType: str
        """``CfnProject.EnvironmentProperty.ComputeType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-environment.html#cfn-codebuild-project-environment-computetype
        Stability:
            experimental
        """

        image: str
        """``CfnProject.EnvironmentProperty.Image``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-environment.html#cfn-codebuild-project-environment-image
        Stability:
            experimental
        """

        type: str
        """``CfnProject.EnvironmentProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-environment.html#cfn-codebuild-project-environment-type
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _EnvironmentVariableProperty(jsii.compat.TypedDict, total=False):
        type: str
        """``CfnProject.EnvironmentVariableProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-environmentvariable.html#cfn-codebuild-project-environmentvariable-type
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codebuild.CfnProject.EnvironmentVariableProperty", jsii_struct_bases=[_EnvironmentVariableProperty])
    class EnvironmentVariableProperty(_EnvironmentVariableProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-environmentvariable.html
        Stability:
            experimental
        """
        name: str
        """``CfnProject.EnvironmentVariableProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-environmentvariable.html#cfn-codebuild-project-environmentvariable-name
        Stability:
            experimental
        """

        value: str
        """``CfnProject.EnvironmentVariableProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-environmentvariable.html#cfn-codebuild-project-environmentvariable-value
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codebuild.CfnProject.GitSubmodulesConfigProperty", jsii_struct_bases=[])
    class GitSubmodulesConfigProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-gitsubmodulesconfig.html
        Stability:
            experimental
        """
        fetchSubmodules: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnProject.GitSubmodulesConfigProperty.FetchSubmodules``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-gitsubmodulesconfig.html#cfn-codebuild-project-gitsubmodulesconfig-fetchsubmodules
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codebuild.CfnProject.LogsConfigProperty", jsii_struct_bases=[])
    class LogsConfigProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-logsconfig.html
        Stability:
            experimental
        """
        cloudWatchLogs: typing.Union[aws_cdk.cdk.Token, "CfnProject.CloudWatchLogsConfigProperty"]
        """``CfnProject.LogsConfigProperty.CloudWatchLogs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-logsconfig.html#cfn-codebuild-project-logsconfig-cloudwatchlogs
        Stability:
            experimental
        """

        s3Logs: typing.Union[aws_cdk.cdk.Token, "CfnProject.S3LogsConfigProperty"]
        """``CfnProject.LogsConfigProperty.S3Logs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-logsconfig.html#cfn-codebuild-project-logsconfig-s3logs
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ProjectCacheProperty(jsii.compat.TypedDict, total=False):
        location: str
        """``CfnProject.ProjectCacheProperty.Location``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-projectcache.html#cfn-codebuild-project-projectcache-location
        Stability:
            experimental
        """
        modes: typing.List[str]
        """``CfnProject.ProjectCacheProperty.Modes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-projectcache.html#cfn-codebuild-project-projectcache-modes
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codebuild.CfnProject.ProjectCacheProperty", jsii_struct_bases=[_ProjectCacheProperty])
    class ProjectCacheProperty(_ProjectCacheProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-projectcache.html
        Stability:
            experimental
        """
        type: str
        """``CfnProject.ProjectCacheProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-projectcache.html#cfn-codebuild-project-projectcache-type
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ProjectSourceVersionProperty(jsii.compat.TypedDict, total=False):
        sourceVersion: str
        """``CfnProject.ProjectSourceVersionProperty.SourceVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-projectsourceversion.html#cfn-codebuild-project-projectsourceversion-sourceversion
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codebuild.CfnProject.ProjectSourceVersionProperty", jsii_struct_bases=[_ProjectSourceVersionProperty])
    class ProjectSourceVersionProperty(_ProjectSourceVersionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-projectsourceversion.html
        Stability:
            experimental
        """
        sourceIdentifier: str
        """``CfnProject.ProjectSourceVersionProperty.SourceIdentifier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-projectsourceversion.html#cfn-codebuild-project-projectsourceversion-sourceidentifier
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codebuild.CfnProject.ProjectTriggersProperty", jsii_struct_bases=[])
    class ProjectTriggersProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-projecttriggers.html
        Stability:
            experimental
        """
        filterGroups: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnProject.WebhookFilterProperty"]]]]]
        """``CfnProject.ProjectTriggersProperty.FilterGroups``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-projecttriggers.html#cfn-codebuild-project-projecttriggers-filtergroups
        Stability:
            experimental
        """

        webhook: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnProject.ProjectTriggersProperty.Webhook``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-projecttriggers.html#cfn-codebuild-project-projecttriggers-webhook
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codebuild.CfnProject.RegistryCredentialProperty", jsii_struct_bases=[])
    class RegistryCredentialProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-registrycredential.html
        Stability:
            experimental
        """
        credential: str
        """``CfnProject.RegistryCredentialProperty.Credential``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-registrycredential.html#cfn-codebuild-project-registrycredential-credential
        Stability:
            experimental
        """

        credentialProvider: str
        """``CfnProject.RegistryCredentialProperty.CredentialProvider``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-registrycredential.html#cfn-codebuild-project-registrycredential-credentialprovider
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _S3LogsConfigProperty(jsii.compat.TypedDict, total=False):
        encryptionDisabled: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnProject.S3LogsConfigProperty.EncryptionDisabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-s3logsconfig.html#cfn-codebuild-project-s3logsconfig-encryptiondisabled
        Stability:
            experimental
        """
        location: str
        """``CfnProject.S3LogsConfigProperty.Location``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-s3logsconfig.html#cfn-codebuild-project-s3logsconfig-location
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codebuild.CfnProject.S3LogsConfigProperty", jsii_struct_bases=[_S3LogsConfigProperty])
    class S3LogsConfigProperty(_S3LogsConfigProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-s3logsconfig.html
        Stability:
            experimental
        """
        status: str
        """``CfnProject.S3LogsConfigProperty.Status``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-s3logsconfig.html#cfn-codebuild-project-s3logsconfig-status
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _SourceAuthProperty(jsii.compat.TypedDict, total=False):
        resource: str
        """``CfnProject.SourceAuthProperty.Resource``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-sourceauth.html#cfn-codebuild-project-sourceauth-resource
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codebuild.CfnProject.SourceAuthProperty", jsii_struct_bases=[_SourceAuthProperty])
    class SourceAuthProperty(_SourceAuthProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-sourceauth.html
        Stability:
            experimental
        """
        type: str
        """``CfnProject.SourceAuthProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-sourceauth.html#cfn-codebuild-project-sourceauth-type
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _SourceProperty(jsii.compat.TypedDict, total=False):
        auth: typing.Union[aws_cdk.cdk.Token, "CfnProject.SourceAuthProperty"]
        """``CfnProject.SourceProperty.Auth``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-source.html#cfn-codebuild-project-source-auth
        Stability:
            experimental
        """
        buildSpec: str
        """``CfnProject.SourceProperty.BuildSpec``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-source.html#cfn-codebuild-project-source-buildspec
        Stability:
            experimental
        """
        gitCloneDepth: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnProject.SourceProperty.GitCloneDepth``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-source.html#cfn-codebuild-project-source-gitclonedepth
        Stability:
            experimental
        """
        gitSubmodulesConfig: typing.Union[aws_cdk.cdk.Token, "CfnProject.GitSubmodulesConfigProperty"]
        """``CfnProject.SourceProperty.GitSubmodulesConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-source.html#cfn-codebuild-project-source-gitsubmodulesconfig
        Stability:
            experimental
        """
        insecureSsl: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnProject.SourceProperty.InsecureSsl``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-source.html#cfn-codebuild-project-source-insecuressl
        Stability:
            experimental
        """
        location: str
        """``CfnProject.SourceProperty.Location``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-source.html#cfn-codebuild-project-source-location
        Stability:
            experimental
        """
        reportBuildStatus: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnProject.SourceProperty.ReportBuildStatus``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-source.html#cfn-codebuild-project-source-reportbuildstatus
        Stability:
            experimental
        """
        sourceIdentifier: str
        """``CfnProject.SourceProperty.SourceIdentifier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-source.html#cfn-codebuild-project-source-sourceidentifier
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codebuild.CfnProject.SourceProperty", jsii_struct_bases=[_SourceProperty])
    class SourceProperty(_SourceProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-source.html
        Stability:
            experimental
        """
        type: str
        """``CfnProject.SourceProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-source.html#cfn-codebuild-project-source-type
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codebuild.CfnProject.VpcConfigProperty", jsii_struct_bases=[])
    class VpcConfigProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-vpcconfig.html
        Stability:
            experimental
        """
        securityGroupIds: typing.List[str]
        """``CfnProject.VpcConfigProperty.SecurityGroupIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-vpcconfig.html#cfn-codebuild-project-vpcconfig-securitygroupids
        Stability:
            experimental
        """

        subnets: typing.List[str]
        """``CfnProject.VpcConfigProperty.Subnets``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-vpcconfig.html#cfn-codebuild-project-vpcconfig-subnets
        Stability:
            experimental
        """

        vpcId: str
        """``CfnProject.VpcConfigProperty.VpcId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-vpcconfig.html#cfn-codebuild-project-vpcconfig-vpcid
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _WebhookFilterProperty(jsii.compat.TypedDict, total=False):
        excludeMatchedPattern: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnProject.WebhookFilterProperty.ExcludeMatchedPattern``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-webhookfilter.html#cfn-codebuild-project-webhookfilter-excludematchedpattern
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codebuild.CfnProject.WebhookFilterProperty", jsii_struct_bases=[_WebhookFilterProperty])
    class WebhookFilterProperty(_WebhookFilterProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-webhookfilter.html
        Stability:
            experimental
        """
        pattern: str
        """``CfnProject.WebhookFilterProperty.Pattern``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-webhookfilter.html#cfn-codebuild-project-webhookfilter-pattern
        Stability:
            experimental
        """

        type: str
        """``CfnProject.WebhookFilterProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-webhookfilter.html#cfn-codebuild-project-webhookfilter-type
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnProjectProps(jsii.compat.TypedDict, total=False):
    badgeEnabled: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::CodeBuild::Project.BadgeEnabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-badgeenabled
    Stability:
        experimental
    """
    cache: typing.Union[aws_cdk.cdk.Token, "CfnProject.ProjectCacheProperty"]
    """``AWS::CodeBuild::Project.Cache``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-cache
    Stability:
        experimental
    """
    description: str
    """``AWS::CodeBuild::Project.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-description
    Stability:
        experimental
    """
    encryptionKey: str
    """``AWS::CodeBuild::Project.EncryptionKey``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-encryptionkey
    Stability:
        experimental
    """
    logsConfig: typing.Union[aws_cdk.cdk.Token, "CfnProject.LogsConfigProperty"]
    """``AWS::CodeBuild::Project.LogsConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-logsconfig
    Stability:
        experimental
    """
    name: str
    """``AWS::CodeBuild::Project.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-name
    Stability:
        experimental
    """
    queuedTimeoutInMinutes: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::CodeBuild::Project.QueuedTimeoutInMinutes``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-queuedtimeoutinminutes
    Stability:
        experimental
    """
    secondaryArtifacts: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnProject.ArtifactsProperty"]]]
    """``AWS::CodeBuild::Project.SecondaryArtifacts``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-secondaryartifacts
    Stability:
        experimental
    """
    secondarySources: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnProject.SourceProperty"]]]
    """``AWS::CodeBuild::Project.SecondarySources``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-secondarysources
    Stability:
        experimental
    """
    secondarySourceVersions: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnProject.ProjectSourceVersionProperty"]]]
    """``AWS::CodeBuild::Project.SecondarySourceVersions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-secondarysourceversions
    Stability:
        experimental
    """
    sourceVersion: str
    """``AWS::CodeBuild::Project.SourceVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-sourceversion
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::CodeBuild::Project.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-tags
    Stability:
        experimental
    """
    timeoutInMinutes: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::CodeBuild::Project.TimeoutInMinutes``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-timeoutinminutes
    Stability:
        experimental
    """
    triggers: typing.Union[aws_cdk.cdk.Token, "CfnProject.ProjectTriggersProperty"]
    """``AWS::CodeBuild::Project.Triggers``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-triggers
    Stability:
        experimental
    """
    vpcConfig: typing.Union[aws_cdk.cdk.Token, "CfnProject.VpcConfigProperty"]
    """``AWS::CodeBuild::Project.VpcConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-vpcconfig
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-codebuild.CfnProjectProps", jsii_struct_bases=[_CfnProjectProps])
class CfnProjectProps(_CfnProjectProps):
    """Properties for defining a ``AWS::CodeBuild::Project``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html
    Stability:
        experimental
    """
    artifacts: typing.Union[aws_cdk.cdk.Token, "CfnProject.ArtifactsProperty"]
    """``AWS::CodeBuild::Project.Artifacts``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-artifacts
    Stability:
        experimental
    """

    environment: typing.Union[aws_cdk.cdk.Token, "CfnProject.EnvironmentProperty"]
    """``AWS::CodeBuild::Project.Environment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-environment
    Stability:
        experimental
    """

    serviceRole: str
    """``AWS::CodeBuild::Project.ServiceRole``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-servicerole
    Stability:
        experimental
    """

    source: typing.Union[aws_cdk.cdk.Token, "CfnProject.SourceProperty"]
    """``AWS::CodeBuild::Project.Source``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-source
    Stability:
        experimental
    """

class CodePipelineBuildArtifacts(BuildArtifacts, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codebuild.CodePipelineBuildArtifacts"):
    """CodePipeline Artifact definition for a CodeBuild Project. *Note*: this type cannot be used as a secondary artifact, and because of that, you're not allowed to specify an identifier for it.

    Stability:
        experimental
    """
    def __init__(self) -> None:
        """
        Stability:
            experimental
        """
        jsii.create(CodePipelineBuildArtifacts, self, [])

    @property
    @jsii.member(jsii_name="type")
    def _type(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "type")


class CodePipelineSource(BuildSource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codebuild.CodePipelineSource"):
    """CodePipeline Source definition for a CodeBuild Project. *Note*: this type cannot be used as a secondary source, and because of that, you're not allowed to specify an identifier for it.

    Stability:
        experimental
    """
    def __init__(self) -> None:
        """
        Stability:
            experimental
        """
        jsii.create(CodePipelineSource, self, [])

    @property
    @jsii.member(jsii_name="type")
    def type(self) -> "SourceType":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "type")


@jsii.data_type(jsii_type="@aws-cdk/aws-codebuild.CommonProjectProps", jsii_struct_bases=[])
class CommonProjectProps(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    allowAllOutbound: bool
    """Whether to allow the CodeBuild to send all network traffic.

    If set to false, you must individually add traffic rules to allow the
    CodeBuild project to connect to network targets.

    Only used if 'vpc' is supplied.

    Default:
        true

    Stability:
        experimental
    """

    badge: bool
    """Indicates whether AWS CodeBuild generates a publicly accessible URL for your project's build badge.

    For more information, see Build Badges Sample
    in the AWS CodeBuild User Guide.

    Default:
        false

    Stability:
        experimental
    """

    buildScriptAsset: aws_cdk.assets.Asset
    """Run a script from an asset as build script.

    If supplied together with buildSpec, the asset script will be run
    *after* the existing commands in buildspec.

    This feature can also be used without a source, to simply run an
    arbitrary script in a serverless way.

    Default:
        - No asset build script.

    Stability:
        experimental
    """

    buildScriptAssetEntrypoint: str
    """The script in the asset to run.

    Default:
        build.sh

    Stability:
        experimental
    """

    buildSpec: typing.Any
    """Filename or contents of buildspec in JSON format.

    Default:
        - Empty buildspec.

    See:
        https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html#build-spec-ref-example
    Stability:
        experimental
    """

    cache: "Cache"
    """Caching strategy to use.

    Default:
        Cache.none

    Stability:
        experimental
    """

    description: str
    """A description of the project.

    Use the description to identify the purpose
    of the project.

    Default:
        - No description.

    Stability:
        experimental
    """

    encryptionKey: aws_cdk.aws_kms.IKey
    """Encryption key to use to read and write artifacts.

    Default:
        - The AWS-managed CMK for Amazon Simple Storage Service (Amazon S3) is used.

    Stability:
        experimental
    """

    environment: "BuildEnvironment"
    """Build environment to use for the build.

    Default:
        BuildEnvironment.LinuxBuildImage.STANDARD_1_0

    Stability:
        experimental
    """

    environmentVariables: typing.Mapping[str,"BuildEnvironmentVariable"]
    """Additional environment variables to add to the build environment.

    Default:
        - No additional environment variables are specified.

    Stability:
        experimental
    """

    projectName: str
    """The physical, human-readable name of the CodeBuild Project.

    Default:
        - Name is automatically generated.

    Stability:
        experimental
    """

    role: aws_cdk.aws_iam.IRole
    """Service Role to assume while running the build.

    Default:
        - A role will be created.

    Stability:
        experimental
    """

    securityGroups: typing.List[aws_cdk.aws_ec2.ISecurityGroup]
    """What security group to associate with the codebuild project's network interfaces. If no security group is identified, one will be created automatically.

    Only used if 'vpc' is supplied.

    Default:
        - Security group will be automatically created.

    Stability:
        experimental
    """

    subnetSelection: aws_cdk.aws_ec2.SubnetSelection
    """Where to place the network interfaces within the VPC.

    Only used if 'vpc' is supplied.

    Default:
        - All private subnets.

    Stability:
        experimental
    """

    timeout: jsii.Number
    """The number of minutes after which AWS CodeBuild stops the build if it's not complete.

    For valid values, see the timeoutInMinutes field in the AWS
    CodeBuild User Guide.

    Default:
        60

    Stability:
        experimental
    """

    vpc: aws_cdk.aws_ec2.IVpc
    """VPC network to place codebuild network interfaces.

    Specify this if the codebuild project needs to access resources in a VPC.

    Default:
        - No VPC is specified.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-codebuild.ComputeType")
class ComputeType(enum.Enum):
    """Build machine compute type.

    Stability:
        experimental
    """
    Small = "Small"
    """
    Stability:
        experimental
    """
    Medium = "Medium"
    """
    Stability:
        experimental
    """
    Large = "Large"
    """
    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-codebuild.EventAction")
class EventAction(enum.Enum):
    """The types of webhook event actions.

    Stability:
        experimental
    """
    PUSH = "PUSH"
    """A push (of a branch, or a tag) to the repository.

    Stability:
        experimental
    """
    PULL_REQUEST_CREATED = "PULL_REQUEST_CREATED"
    """Creating a Pull Request.

    Stability:
        experimental
    """
    PULL_REQUEST_UPDATED = "PULL_REQUEST_UPDATED"
    """Updating an Pull Request.

    Stability:
        experimental
    """
    PULL_REQUEST_REOPENED = "PULL_REQUEST_REOPENED"
    """Re-opening a previously closed Pull Request. Note that this event is only supported for GitHub and GitHubEnterprise sources.

    Stability:
        experimental
    """

class FilterGroup(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codebuild.FilterGroup"):
    """An object that represents a group of filter conditions for a webhook. Every condition in a given FilterGroup must be true in order for the whole group to be true. You construct instances of it by calling the {@link #inEventOf} static factory method, and then calling various ``andXyz`` instance methods to create modified instances of it (this class is immutable).

    You pass instances of this class to the ``webhookFilters`` property when constructing a source.

    Stability:
        experimental
    """
    @jsii.member(jsii_name="inEventOf")
    @classmethod
    def in_event_of(cls, *actions: "EventAction") -> "FilterGroup":
        """Creates a new event FilterGroup that triggers on any of the provided actions.

        Arguments:
            actions: the actions to trigger the webhook on.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "inEventOf", [*actions])

    @jsii.member(jsii_name="andActorAccountIs")
    def and_actor_account_is(self, pattern: str) -> "FilterGroup":
        """Create a new FilterGroup with an added condition: the account ID of the actor initiating the event must match the given pattern.

        Arguments:
            pattern: a regular expression.

        Stability:
            experimental
        """
        return jsii.invoke(self, "andActorAccountIs", [pattern])

    @jsii.member(jsii_name="andActorAccountIsNot")
    def and_actor_account_is_not(self, pattern: str) -> "FilterGroup":
        """Create a new FilterGroup with an added condition: the account ID of the actor initiating the event must not match the given pattern.

        Arguments:
            pattern: a regular expression.

        Stability:
            experimental
        """
        return jsii.invoke(self, "andActorAccountIsNot", [pattern])

    @jsii.member(jsii_name="andBaseBranchIs")
    def and_base_branch_is(self, branch_name: str) -> "FilterGroup":
        """Create a new FilterGroup with an added condition: the Pull Request that is the source of the event must target the given base branch. Note that you cannot use this method if this Group contains the ``PUSH`` event action.

        Arguments:
            branchName: the name of the branch (can be a regular expression).

        Stability:
            experimental
        """
        return jsii.invoke(self, "andBaseBranchIs", [branch_name])

    @jsii.member(jsii_name="andBaseBranchIsNot")
    def and_base_branch_is_not(self, branch_name: str) -> "FilterGroup":
        """Create a new FilterGroup with an added condition: the Pull Request that is the source of the event must not target the given base branch. Note that you cannot use this method if this Group contains the ``PUSH`` event action.

        Arguments:
            branchName: the name of the branch (can be a regular expression).

        Stability:
            experimental
        """
        return jsii.invoke(self, "andBaseBranchIsNot", [branch_name])

    @jsii.member(jsii_name="andBaseRefIs")
    def and_base_ref_is(self, pattern: str) -> "FilterGroup":
        """Create a new FilterGroup with an added condition: the Pull Request that is the source of the event must target the given Git reference. Note that you cannot use this method if this Group contains the ``PUSH`` event action.

        Arguments:
            pattern: a regular expression.

        Stability:
            experimental
        """
        return jsii.invoke(self, "andBaseRefIs", [pattern])

    @jsii.member(jsii_name="andBaseRefIsNot")
    def and_base_ref_is_not(self, pattern: str) -> "FilterGroup":
        """Create a new FilterGroup with an added condition: the Pull Request that is the source of the event must not target the given Git reference. Note that you cannot use this method if this Group contains the ``PUSH`` event action.

        Arguments:
            pattern: a regular expression.

        Stability:
            experimental
        """
        return jsii.invoke(self, "andBaseRefIsNot", [pattern])

    @jsii.member(jsii_name="andBranchIs")
    def and_branch_is(self, branch_name: str) -> "FilterGroup":
        """Create a new FilterGroup with an added condition: the event must affect the given branch.

        Arguments:
            branchName: the name of the branch (can be a regular expression).

        Stability:
            experimental
        """
        return jsii.invoke(self, "andBranchIs", [branch_name])

    @jsii.member(jsii_name="andBranchIsNot")
    def and_branch_is_not(self, branch_name: str) -> "FilterGroup":
        """Create a new FilterGroup with an added condition: the event must not affect the given branch.

        Arguments:
            branchName: the name of the branch (can be a regular expression).

        Stability:
            experimental
        """
        return jsii.invoke(self, "andBranchIsNot", [branch_name])

    @jsii.member(jsii_name="andFilePathIs")
    def and_file_path_is(self, pattern: str) -> "FilterGroup":
        """Create a new FilterGroup with an added condition: the push that is the source of the event must affect a file that matches the given pattern. Note that you can only use this method if this Group contains only the ``PUSH`` event action, and only for GitHub and GitHubEnterprise sources.

        Arguments:
            pattern: a regular expression.

        Stability:
            experimental
        """
        return jsii.invoke(self, "andFilePathIs", [pattern])

    @jsii.member(jsii_name="andFilePathIsNot")
    def and_file_path_is_not(self, pattern: str) -> "FilterGroup":
        """Create a new FilterGroup with an added condition: the push that is the source of the event must not affect a file that matches the given pattern. Note that you can only use this method if this Group contains only the ``PUSH`` event action, and only for GitHub and GitHubEnterprise sources.

        Arguments:
            pattern: a regular expression.

        Stability:
            experimental
        """
        return jsii.invoke(self, "andFilePathIsNot", [pattern])

    @jsii.member(jsii_name="andHeadRefIs")
    def and_head_ref_is(self, pattern: str) -> "FilterGroup":
        """Create a new FilterGroup with an added condition: the event must affect a Git reference (ie., a branch or a tag) that matches the given pattern.

        Arguments:
            pattern: a regular expression.

        Stability:
            experimental
        """
        return jsii.invoke(self, "andHeadRefIs", [pattern])

    @jsii.member(jsii_name="andHeadRefIsNot")
    def and_head_ref_is_not(self, pattern: str) -> "FilterGroup":
        """Create a new FilterGroup with an added condition: the event must not affect a Git reference (ie., a branch or a tag) that matches the given pattern.

        Arguments:
            pattern: a regular expression.

        Stability:
            experimental
        """
        return jsii.invoke(self, "andHeadRefIsNot", [pattern])

    @jsii.member(jsii_name="andTagIs")
    def and_tag_is(self, tag_name: str) -> "FilterGroup":
        """Create a new FilterGroup with an added condition: the event must affect the given tag.

        Arguments:
            tagName: the name of the tag (can be a regular expression).

        Stability:
            experimental
        """
        return jsii.invoke(self, "andTagIs", [tag_name])

    @jsii.member(jsii_name="andTagIsNot")
    def and_tag_is_not(self, tag_name: str) -> "FilterGroup":
        """Create a new FilterGroup with an added condition: the event must not affect the given tag.

        Arguments:
            tagName: the name of the tag (can be a regular expression).

        Stability:
            experimental
        """
        return jsii.invoke(self, "andTagIsNot", [tag_name])


class GitBuildSource(BuildSource, metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/aws-codebuild.GitBuildSource"):
    """A common superclass of all build sources that are backed by Git.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _GitBuildSourceProxy

    def __init__(self, *, clone_depth: typing.Optional[jsii.Number]=None, identifier: typing.Optional[str]=None) -> None:
        """
        Arguments:
            props: -
            cloneDepth: The depth of history to download. Minimum value is 0. If this value is 0, greater than 25, or not provided, then the full history is downloaded with each build of the project.
            identifier: The source identifier. This property is required on secondary sources.

        Stability:
            experimental
        """
        props: GitBuildSourceProps = {}

        if clone_depth is not None:
            props["cloneDepth"] = clone_depth

        if identifier is not None:
            props["identifier"] = identifier

        jsii.create(GitBuildSource, self, [props])


class _GitBuildSourceProxy(GitBuildSource, jsii.proxy_for(BuildSource)):
    pass

class CodeCommitSource(GitBuildSource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codebuild.CodeCommitSource"):
    """CodeCommit Source definition for a CodeBuild project.

    Stability:
        experimental
    """
    def __init__(self, *, repository: aws_cdk.aws_codecommit.IRepository, clone_depth: typing.Optional[jsii.Number]=None, identifier: typing.Optional[str]=None) -> None:
        """
        Arguments:
            props: -
            repository: 
            cloneDepth: The depth of history to download. Minimum value is 0. If this value is 0, greater than 25, or not provided, then the full history is downloaded with each build of the project.
            identifier: The source identifier. This property is required on secondary sources.

        Stability:
            experimental
        """
        props: CodeCommitSourceProps = {"repository": repository}

        if clone_depth is not None:
            props["cloneDepth"] = clone_depth

        if identifier is not None:
            props["identifier"] = identifier

        jsii.create(CodeCommitSource, self, [props])

    @jsii.member(jsii_name="toSourceProperty")
    def _to_source_property(self) -> typing.Any:
        """
        Stability:
            experimental
        """
        return jsii.invoke(self, "toSourceProperty", [])

    @property
    @jsii.member(jsii_name="type")
    def type(self) -> "SourceType":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "type")


@jsii.data_type(jsii_type="@aws-cdk/aws-codebuild.GitBuildSourceProps", jsii_struct_bases=[BuildSourceProps])
class GitBuildSourceProps(BuildSourceProps, jsii.compat.TypedDict, total=False):
    """The construction properties common to all build sources that are backed by Git.

    Stability:
        experimental
    """
    cloneDepth: jsii.Number
    """The depth of history to download.

    Minimum value is 0.
    If this value is 0, greater than 25, or not provided,
    then the full history is downloaded with each build of the project.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-codebuild.CodeCommitSourceProps", jsii_struct_bases=[GitBuildSourceProps])
class CodeCommitSourceProps(GitBuildSourceProps, jsii.compat.TypedDict):
    """Construction properties for {@link CodeCommitSource}.

    Stability:
        experimental
    """
    repository: aws_cdk.aws_codecommit.IRepository
    """
    Stability:
        experimental
    """

@jsii.interface(jsii_type="@aws-cdk/aws-codebuild.IBuildImage")
class IBuildImage(jsii.compat.Protocol):
    """Represents a Docker image used for the CodeBuild Project builds. Use the concrete subclasses, either: {@link LinuxBuildImage} or {@link WindowsBuildImage}.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IBuildImageProxy

    @property
    @jsii.member(jsii_name="defaultComputeType")
    def default_compute_type(self) -> "ComputeType":
        """The default {@link ComputeType} to use with this image, if one was not specified in {@link BuildEnvironment#computeType} explicitly.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="imageId")
    def image_id(self) -> str:
        """The Docker image identifier that the build environment uses.

        See:
            https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-available.html
        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="type")
    def type(self) -> str:
        """The type of build environment.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="runScriptBuildspec")
    def run_script_buildspec(self, entrypoint: str) -> typing.Any:
        """Make a buildspec to run the indicated script.

        Arguments:
            entrypoint: -

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="validate")
    def validate(self, *, build_image: typing.Optional["IBuildImage"]=None, compute_type: typing.Optional["ComputeType"]=None, environment_variables: typing.Optional[typing.Mapping[str,"BuildEnvironmentVariable"]]=None, privileged: typing.Optional[bool]=None) -> typing.List[str]:
        """Allows the image a chance to validate whether the passed configuration is correct.

        Arguments:
            buildEnvironment: the current build environment.
            buildImage: The image used for the builds. Default: LinuxBuildImage.STANDARD_1_0
            computeType: The type of compute to use for this build. See the {@link ComputeType} enum for the possible values. Default: taken from {@link #buildImage#defaultComputeType}
            environmentVariables: The environment variables that your builds can use.
            privileged: Indicates how the project builds Docker images. Specify true to enable running the Docker daemon inside a Docker container. This value must be set to true only if this build project will be used to build Docker images, and the specified build environment image is not one provided by AWS CodeBuild with Docker support. Otherwise, all associated builds that attempt to interact with the Docker daemon will fail. Default: false

        Stability:
            experimental
        """
        ...


class _IBuildImageProxy():
    """Represents a Docker image used for the CodeBuild Project builds. Use the concrete subclasses, either: {@link LinuxBuildImage} or {@link WindowsBuildImage}.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-codebuild.IBuildImage"
    @property
    @jsii.member(jsii_name="defaultComputeType")
    def default_compute_type(self) -> "ComputeType":
        """The default {@link ComputeType} to use with this image, if one was not specified in {@link BuildEnvironment#computeType} explicitly.

        Stability:
            experimental
        """
        return jsii.get(self, "defaultComputeType")

    @property
    @jsii.member(jsii_name="imageId")
    def image_id(self) -> str:
        """The Docker image identifier that the build environment uses.

        See:
            https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-available.html
        Stability:
            experimental
        """
        return jsii.get(self, "imageId")

    @property
    @jsii.member(jsii_name="type")
    def type(self) -> str:
        """The type of build environment.

        Stability:
            experimental
        """
        return jsii.get(self, "type")

    @jsii.member(jsii_name="runScriptBuildspec")
    def run_script_buildspec(self, entrypoint: str) -> typing.Any:
        """Make a buildspec to run the indicated script.

        Arguments:
            entrypoint: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "runScriptBuildspec", [entrypoint])

    @jsii.member(jsii_name="validate")
    def validate(self, *, build_image: typing.Optional["IBuildImage"]=None, compute_type: typing.Optional["ComputeType"]=None, environment_variables: typing.Optional[typing.Mapping[str,"BuildEnvironmentVariable"]]=None, privileged: typing.Optional[bool]=None) -> typing.List[str]:
        """Allows the image a chance to validate whether the passed configuration is correct.

        Arguments:
            buildEnvironment: the current build environment.
            buildImage: The image used for the builds. Default: LinuxBuildImage.STANDARD_1_0
            computeType: The type of compute to use for this build. See the {@link ComputeType} enum for the possible values. Default: taken from {@link #buildImage#defaultComputeType}
            environmentVariables: The environment variables that your builds can use.
            privileged: Indicates how the project builds Docker images. Specify true to enable running the Docker daemon inside a Docker container. This value must be set to true only if this build project will be used to build Docker images, and the specified build environment image is not one provided by AWS CodeBuild with Docker support. Otherwise, all associated builds that attempt to interact with the Docker daemon will fail. Default: false

        Stability:
            experimental
        """
        build_environment: BuildEnvironment = {}

        if build_image is not None:
            build_environment["buildImage"] = build_image

        if compute_type is not None:
            build_environment["computeType"] = compute_type

        if environment_variables is not None:
            build_environment["environmentVariables"] = environment_variables

        if privileged is not None:
            build_environment["privileged"] = privileged

        return jsii.invoke(self, "validate", [build_environment])


@jsii.interface(jsii_type="@aws-cdk/aws-codebuild.IProject")
class IProject(aws_cdk.cdk.IResource, aws_cdk.aws_iam.IGrantable, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IProjectProxy

    @property
    @jsii.member(jsii_name="projectArn")
    def project_arn(self) -> str:
        """The ARN of this Project.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="projectName")
    def project_name(self) -> str:
        """The human-visible name of this Project.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        """The IAM service Role of this Project.

        Undefined for imported Projects.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metric")
    def metric(self, metric_name: str, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """
        Arguments:
            metricName: The name of the metric.
            props: Customization properties.
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Returns:
            a CloudWatch metric associated with this build project.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricBuilds")
    def metric_builds(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Measures the number of builds triggered.

        Units: Count

        Valid CloudWatch statistics: Sum

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Default:
            sum over 5 minutes

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricDuration")
    def metric_duration(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Measures the duration of all builds over time.

        Units: Seconds

        Valid CloudWatch statistics: Average (recommended), Maximum, Minimum

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Default:
            average over 5 minutes

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricFailedBuilds")
    def metric_failed_builds(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Measures the number of builds that failed because of client error or because of a timeout.

        Units: Count

        Valid CloudWatch statistics: Sum

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Default:
            sum over 5 minutes

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricSucceededBuilds")
    def metric_succeeded_builds(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Measures the number of successful builds.

        Units: Count

        Valid CloudWatch statistics: Sum

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Default:
            sum over 5 minutes

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="onBuildFailed")
    def on_build_failed(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines an event rule which triggers when a build fails.

        Arguments:
            id: -
            options: -
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="onBuildStarted")
    def on_build_started(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines an event rule which triggers when a build starts.

        Arguments:
            id: -
            options: -
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="onBuildSucceeded")
    def on_build_succeeded(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines an event rule which triggers when a build completes successfully.

        Arguments:
            id: -
            options: -
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="onEvent")
    def on_event(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule triggered when something happens with this project.

        Arguments:
            id: -
            options: -
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        See:
            https://docs.aws.amazon.com/codebuild/latest/userguide/sample-build-notifications.html
        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="onPhaseChange")
    def on_phase_change(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule that triggers upon phase change of this build project.

        Arguments:
            id: -
            options: -
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        See:
            https://docs.aws.amazon.com/codebuild/latest/userguide/sample-build-notifications.html
        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule triggered when the build project state changes.

        You can filter specific build status events using an event
        pattern filter on the ``build-status`` detail field::

           const rule = project.onStateChange('OnBuildStarted', target);
           rule.addEventPattern({
             detail: {
               'build-status': [
                 "IN_PROGRESS",
                 "SUCCEEDED",
                 "FAILED",
                 "STOPPED"
               ]
             }
           });

        You can also use the methods ``onBuildFailed`` and ``onBuildSucceeded`` to define rules for
        these specific state changes.

        To access fields from the event in the event target input,
        use the static fields on the ``StateChangeEvent`` class.

        Arguments:
            id: -
            options: -
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        See:
            https://docs.aws.amazon.com/codebuild/latest/userguide/sample-build-notifications.html
        Stability:
            experimental
        """
        ...


class _IProjectProxy(jsii.proxy_for(aws_cdk.cdk.IResource), jsii.proxy_for(aws_cdk.aws_iam.IGrantable)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-codebuild.IProject"
    @property
    @jsii.member(jsii_name="projectArn")
    def project_arn(self) -> str:
        """The ARN of this Project.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "projectArn")

    @property
    @jsii.member(jsii_name="projectName")
    def project_name(self) -> str:
        """The human-visible name of this Project.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "projectName")

    @property
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        """The IAM service Role of this Project.

        Undefined for imported Projects.

        Stability:
            experimental
        """
        return jsii.get(self, "role")

    @jsii.member(jsii_name="metric")
    def metric(self, metric_name: str, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """
        Arguments:
            metricName: The name of the metric.
            props: Customization properties.
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Returns:
            a CloudWatch metric associated with this build project.

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metric", [metric_name, props])

    @jsii.member(jsii_name="metricBuilds")
    def metric_builds(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Measures the number of builds triggered.

        Units: Count

        Valid CloudWatch statistics: Sum

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Default:
            sum over 5 minutes

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricBuilds", [props])

    @jsii.member(jsii_name="metricDuration")
    def metric_duration(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Measures the duration of all builds over time.

        Units: Seconds

        Valid CloudWatch statistics: Average (recommended), Maximum, Minimum

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Default:
            average over 5 minutes

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricDuration", [props])

    @jsii.member(jsii_name="metricFailedBuilds")
    def metric_failed_builds(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Measures the number of builds that failed because of client error or because of a timeout.

        Units: Count

        Valid CloudWatch statistics: Sum

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Default:
            sum over 5 minutes

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricFailedBuilds", [props])

    @jsii.member(jsii_name="metricSucceededBuilds")
    def metric_succeeded_builds(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Measures the number of successful builds.

        Units: Count

        Valid CloudWatch statistics: Sum

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Default:
            sum over 5 minutes

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricSucceededBuilds", [props])

    @jsii.member(jsii_name="onBuildFailed")
    def on_build_failed(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines an event rule which triggers when a build fails.

        Arguments:
            id: -
            options: -
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        options: aws_cdk.aws_events.OnEventOptions = {"target": target}

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        return jsii.invoke(self, "onBuildFailed", [id, options])

    @jsii.member(jsii_name="onBuildStarted")
    def on_build_started(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines an event rule which triggers when a build starts.

        Arguments:
            id: -
            options: -
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        options: aws_cdk.aws_events.OnEventOptions = {"target": target}

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        return jsii.invoke(self, "onBuildStarted", [id, options])

    @jsii.member(jsii_name="onBuildSucceeded")
    def on_build_succeeded(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines an event rule which triggers when a build completes successfully.

        Arguments:
            id: -
            options: -
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        options: aws_cdk.aws_events.OnEventOptions = {"target": target}

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        return jsii.invoke(self, "onBuildSucceeded", [id, options])

    @jsii.member(jsii_name="onEvent")
    def on_event(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule triggered when something happens with this project.

        Arguments:
            id: -
            options: -
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        See:
            https://docs.aws.amazon.com/codebuild/latest/userguide/sample-build-notifications.html
        Stability:
            experimental
        """
        options: aws_cdk.aws_events.OnEventOptions = {"target": target}

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        return jsii.invoke(self, "onEvent", [id, options])

    @jsii.member(jsii_name="onPhaseChange")
    def on_phase_change(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule that triggers upon phase change of this build project.

        Arguments:
            id: -
            options: -
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        See:
            https://docs.aws.amazon.com/codebuild/latest/userguide/sample-build-notifications.html
        Stability:
            experimental
        """
        options: aws_cdk.aws_events.OnEventOptions = {"target": target}

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        return jsii.invoke(self, "onPhaseChange", [id, options])

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule triggered when the build project state changes.

        You can filter specific build status events using an event
        pattern filter on the ``build-status`` detail field::

           const rule = project.onStateChange('OnBuildStarted', target);
           rule.addEventPattern({
             detail: {
               'build-status': [
                 "IN_PROGRESS",
                 "SUCCEEDED",
                 "FAILED",
                 "STOPPED"
               ]
             }
           });

        You can also use the methods ``onBuildFailed`` and ``onBuildSucceeded`` to define rules for
        these specific state changes.

        To access fields from the event in the event target input,
        use the static fields on the ``StateChangeEvent`` class.

        Arguments:
            id: -
            options: -
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        See:
            https://docs.aws.amazon.com/codebuild/latest/userguide/sample-build-notifications.html
        Stability:
            experimental
        """
        options: aws_cdk.aws_events.OnEventOptions = {"target": target}

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        return jsii.invoke(self, "onStateChange", [id, options])


@jsii.implements(IBuildImage)
class LinuxBuildImage(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codebuild.LinuxBuildImage"):
    """A CodeBuild image running Linux.

    This class has a bunch of public constants that represent the most popular images.

    You can also specify a custom image using one of the static methods:

    - LinuxBuildImage.fromDockerHub(image)
    - LinuxBuildImage.fromEcrRepository(repo[, tag])
    - LinuxBuildImage.fromAsset(parent, id, props)

    See:
        https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-available.html
    Stability:
        experimental
    """
    @jsii.member(jsii_name="fromAsset")
    @classmethod
    def from_asset(cls, scope: aws_cdk.cdk.Construct, id: str, *, directory: str, build_args: typing.Optional[typing.Mapping[str,str]]=None, repository_name: typing.Optional[str]=None, exclude: typing.Optional[typing.List[str]]=None, follow: typing.Optional[aws_cdk.assets.FollowMode]=None) -> "LinuxBuildImage":
        """Uses an Docker image asset as a Linux build image.

        Arguments:
            scope: -
            id: -
            props: -
            directory: The directory where the Dockerfile is stored.
            buildArgs: Build args to pass to the ``docker build`` command. Default: no build args are passed
            repositoryName: ECR repository name. Specify this property if you need to statically address the image, e.g. from a Kubernetes Pod. Note, this is only the repository name, without the registry and the tag parts. Default: automatically derived from the asset's ID.
            exclude: Glob patterns to exclude from the copy. Default: nothing is excluded
            follow: A strategy for how to handle symlinks. Default: Never

        Stability:
            experimental
        """
        props: aws_cdk.assets_docker.DockerImageAssetProps = {"directory": directory}

        if build_args is not None:
            props["buildArgs"] = build_args

        if repository_name is not None:
            props["repositoryName"] = repository_name

        if exclude is not None:
            props["exclude"] = exclude

        if follow is not None:
            props["follow"] = follow

        return jsii.sinvoke(cls, "fromAsset", [scope, id, props])

    @jsii.member(jsii_name="fromDockerHub")
    @classmethod
    def from_docker_hub(cls, name: str) -> "LinuxBuildImage":
        """
        Arguments:
            name: -

        Returns:
            a Linux build image from a Docker Hub image.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromDockerHub", [name])

    @jsii.member(jsii_name="fromEcrRepository")
    @classmethod
    def from_ecr_repository(cls, repository: aws_cdk.aws_ecr.IRepository, tag: typing.Optional[str]=None) -> "LinuxBuildImage":
        """
        Arguments:
            repository: The ECR repository.
            tag: Image tag (default "latest").

        Returns:
            A Linux build image from an ECR repository.
            
            NOTE: if the repository is external (i.e. imported), then we won't be able to add
            a resource policy statement for it so CodeBuild can pull the image.

        See:
            https://docs.aws.amazon.com/codebuild/latest/userguide/sample-ecr.html
        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromEcrRepository", [repository, tag])

    @jsii.member(jsii_name="runScriptBuildspec")
    def run_script_buildspec(self, entrypoint: str) -> typing.Any:
        """Make a buildspec to run the indicated script.

        Arguments:
            entrypoint: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "runScriptBuildspec", [entrypoint])

    @jsii.member(jsii_name="validate")
    def validate(self, *, build_image: typing.Optional["IBuildImage"]=None, compute_type: typing.Optional["ComputeType"]=None, environment_variables: typing.Optional[typing.Mapping[str,"BuildEnvironmentVariable"]]=None, privileged: typing.Optional[bool]=None) -> typing.List[str]:
        """Allows the image a chance to validate whether the passed configuration is correct.

        Arguments:
            _: -
            buildImage: The image used for the builds. Default: LinuxBuildImage.STANDARD_1_0
            computeType: The type of compute to use for this build. See the {@link ComputeType} enum for the possible values. Default: taken from {@link #buildImage#defaultComputeType}
            environmentVariables: The environment variables that your builds can use.
            privileged: Indicates how the project builds Docker images. Specify true to enable running the Docker daemon inside a Docker container. This value must be set to true only if this build project will be used to build Docker images, and the specified build environment image is not one provided by AWS CodeBuild with Docker support. Otherwise, all associated builds that attempt to interact with the Docker daemon will fail. Default: false

        Stability:
            experimental
        """
        _: BuildEnvironment = {}

        if build_image is not None:
            _["buildImage"] = build_image

        if compute_type is not None:
            _["computeType"] = compute_type

        if environment_variables is not None:
            _["environmentVariables"] = environment_variables

        if privileged is not None:
            _["privileged"] = privileged

        return jsii.invoke(self, "validate", [_])

    @classproperty
    @jsii.member(jsii_name="STANDARD_1_0")
    def STANDARD_1_0(cls) -> "LinuxBuildImage":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "STANDARD_1_0")

    @classproperty
    @jsii.member(jsii_name="STANDARD_2_0")
    def STANDARD_2_0(cls) -> "LinuxBuildImage":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "STANDARD_2_0")

    @classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_ANDROID_JAVA8_24_4_1")
    def UBUNTU_14_04_ANDROID_JAV_A8_24_4_1(cls) -> "LinuxBuildImage":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "UBUNTU_14_04_ANDROID_JAVA8_24_4_1")

    @classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_ANDROID_JAVA8_26_1_1")
    def UBUNTU_14_04_ANDROID_JAV_A8_26_1_1(cls) -> "LinuxBuildImage":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "UBUNTU_14_04_ANDROID_JAVA8_26_1_1")

    @classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_BASE")
    def UBUNTU_14_04_BASE(cls) -> "LinuxBuildImage":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "UBUNTU_14_04_BASE")

    @classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_DOCKER_17_09_0")
    def UBUNTU_14_04_DOCKER_17_09_0(cls) -> "LinuxBuildImage":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "UBUNTU_14_04_DOCKER_17_09_0")

    @classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_DOCKER_18_09_0")
    def UBUNTU_14_04_DOCKER_18_09_0(cls) -> "LinuxBuildImage":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "UBUNTU_14_04_DOCKER_18_09_0")

    @classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_DOTNET_CORE_1_1")
    def UBUNTU_14_04_DOTNET_CORE_1_1(cls) -> "LinuxBuildImage":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "UBUNTU_14_04_DOTNET_CORE_1_1")

    @classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_DOTNET_CORE_2_0")
    def UBUNTU_14_04_DOTNET_CORE_2_0(cls) -> "LinuxBuildImage":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "UBUNTU_14_04_DOTNET_CORE_2_0")

    @classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_DOTNET_CORE_2_1")
    def UBUNTU_14_04_DOTNET_CORE_2_1(cls) -> "LinuxBuildImage":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "UBUNTU_14_04_DOTNET_CORE_2_1")

    @classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_GOLANG_1_10")
    def UBUNTU_14_04_GOLANG_1_10(cls) -> "LinuxBuildImage":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "UBUNTU_14_04_GOLANG_1_10")

    @classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_GOLANG_1_11")
    def UBUNTU_14_04_GOLANG_1_11(cls) -> "LinuxBuildImage":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "UBUNTU_14_04_GOLANG_1_11")

    @classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_NODEJS_10_1_0")
    def UBUNTU_14_04_NODEJS_10_1_0(cls) -> "LinuxBuildImage":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "UBUNTU_14_04_NODEJS_10_1_0")

    @classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_NODEJS_10_14_1")
    def UBUNTU_14_04_NODEJS_10_14_1(cls) -> "LinuxBuildImage":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "UBUNTU_14_04_NODEJS_10_14_1")

    @classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_NODEJS_6_3_1")
    def UBUNTU_14_04_NODEJS_6_3_1(cls) -> "LinuxBuildImage":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "UBUNTU_14_04_NODEJS_6_3_1")

    @classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_NODEJS_8_11_0")
    def UBUNTU_14_04_NODEJS_8_11_0(cls) -> "LinuxBuildImage":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "UBUNTU_14_04_NODEJS_8_11_0")

    @classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_OPEN_JDK_11")
    def UBUNTU_14_04_OPEN_JDK_11(cls) -> "LinuxBuildImage":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "UBUNTU_14_04_OPEN_JDK_11")

    @classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_OPEN_JDK_8")
    def UBUNTU_14_04_OPEN_JDK_8(cls) -> "LinuxBuildImage":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "UBUNTU_14_04_OPEN_JDK_8")

    @classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_OPEN_JDK_9")
    def UBUNTU_14_04_OPEN_JDK_9(cls) -> "LinuxBuildImage":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "UBUNTU_14_04_OPEN_JDK_9")

    @classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_PHP_5_6")
    def UBUNTU_14_04_PHP_5_6(cls) -> "LinuxBuildImage":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "UBUNTU_14_04_PHP_5_6")

    @classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_PHP_7_0")
    def UBUNTU_14_04_PHP_7_0(cls) -> "LinuxBuildImage":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "UBUNTU_14_04_PHP_7_0")

    @classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_PHP_7_1")
    def UBUNTU_14_04_PHP_7_1(cls) -> "LinuxBuildImage":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "UBUNTU_14_04_PHP_7_1")

    @classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_PYTHON_2_7_12")
    def UBUNTU_14_04_PYTHON_2_7_12(cls) -> "LinuxBuildImage":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "UBUNTU_14_04_PYTHON_2_7_12")

    @classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_PYTHON_3_3_6")
    def UBUNTU_14_04_PYTHON_3_3_6(cls) -> "LinuxBuildImage":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "UBUNTU_14_04_PYTHON_3_3_6")

    @classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_PYTHON_3_4_5")
    def UBUNTU_14_04_PYTHON_3_4_5(cls) -> "LinuxBuildImage":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "UBUNTU_14_04_PYTHON_3_4_5")

    @classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_PYTHON_3_5_2")
    def UBUNTU_14_04_PYTHON_3_5_2(cls) -> "LinuxBuildImage":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "UBUNTU_14_04_PYTHON_3_5_2")

    @classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_PYTHON_3_6_5")
    def UBUNTU_14_04_PYTHON_3_6_5(cls) -> "LinuxBuildImage":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "UBUNTU_14_04_PYTHON_3_6_5")

    @classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_PYTHON_3_7_1")
    def UBUNTU_14_04_PYTHON_3_7_1(cls) -> "LinuxBuildImage":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "UBUNTU_14_04_PYTHON_3_7_1")

    @classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_RUBY_2_2_5")
    def UBUNTU_14_04_RUBY_2_2_5(cls) -> "LinuxBuildImage":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "UBUNTU_14_04_RUBY_2_2_5")

    @classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_RUBY_2_3_1")
    def UBUNTU_14_04_RUBY_2_3_1(cls) -> "LinuxBuildImage":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "UBUNTU_14_04_RUBY_2_3_1")

    @classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_RUBY_2_5_1")
    def UBUNTU_14_04_RUBY_2_5_1(cls) -> "LinuxBuildImage":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "UBUNTU_14_04_RUBY_2_5_1")

    @classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_RUBY_2_5_3")
    def UBUNTU_14_04_RUBY_2_5_3(cls) -> "LinuxBuildImage":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "UBUNTU_14_04_RUBY_2_5_3")

    @property
    @jsii.member(jsii_name="defaultComputeType")
    def default_compute_type(self) -> "ComputeType":
        """The default {@link ComputeType} to use with this image, if one was not specified in {@link BuildEnvironment#computeType} explicitly.

        Stability:
            experimental
        """
        return jsii.get(self, "defaultComputeType")

    @property
    @jsii.member(jsii_name="imageId")
    def image_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "imageId")

    @property
    @jsii.member(jsii_name="type")
    def type(self) -> str:
        """The type of build environment.

        Stability:
            experimental
        """
        return jsii.get(self, "type")


@jsii.enum(jsii_type="@aws-cdk/aws-codebuild.LocalCacheMode")
class LocalCacheMode(enum.Enum):
    """Local cache modes to enable for the CodeBuild Project.

    Stability:
        experimental
    """
    Source = "Source"
    """Caches Git metadata for primary and secondary sources.

    Stability:
        experimental
    """
    DockerLayer = "DockerLayer"
    """Caches existing Docker layers.

    Stability:
        experimental
    """
    Custom = "Custom"
    """Caches directories you specify in the buildspec file.

    Stability:
        experimental
    """

class NoBuildArtifacts(BuildArtifacts, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codebuild.NoBuildArtifacts"):
    """A ``NO_ARTIFACTS`` CodeBuild Project Artifact definition. This is the default artifact type, if none was specified when creating the Project (and the source was not specified to be CodePipeline). *Note*: the ``NO_ARTIFACTS`` type cannot be used as a secondary artifact, and because of that, you're not allowed to specify an identifier for it.

    Stability:
        experimental
    """
    def __init__(self) -> None:
        """
        Stability:
            experimental
        """
        jsii.create(NoBuildArtifacts, self, [])

    @property
    @jsii.member(jsii_name="type")
    def _type(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "type")


class NoSource(BuildSource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codebuild.NoSource"):
    """A ``NO_SOURCE`` CodeBuild Project Source definition. This is the default source type, if none was specified when creating the Project. *Note*: the ``NO_SOURCE`` type cannot be used as a secondary source, and because of that, you're not allowed to specify an identifier for it.

    Stability:
        experimental
    """
    def __init__(self) -> None:
        """
        Stability:
            experimental
        """
        jsii.create(NoSource, self, [])

    @property
    @jsii.member(jsii_name="type")
    def type(self) -> "SourceType":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "type")


class PhaseChangeEvent(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codebuild.PhaseChangeEvent"):
    """Event fields for the CodeBuild "phase change" event.

    See:
        https://docs.aws.amazon.com/codebuild/latest/userguide/sample-build-notifications.html#sample-build-notifications-ref
    Stability:
        experimental
    """
    @classproperty
    @jsii.member(jsii_name="buildComplete")
    def build_complete(cls) -> str:
        """Whether the build is complete.

        Stability:
            experimental
        """
        return jsii.sget(cls, "buildComplete")

    @classproperty
    @jsii.member(jsii_name="buildId")
    def build_id(cls) -> str:
        """The triggering build's id.

        Stability:
            experimental
        """
        return jsii.sget(cls, "buildId")

    @classproperty
    @jsii.member(jsii_name="completedPhase")
    def completed_phase(cls) -> str:
        """The phase that was just completed.

        Stability:
            experimental
        """
        return jsii.sget(cls, "completedPhase")

    @classproperty
    @jsii.member(jsii_name="completedPhaseDurationSeconds")
    def completed_phase_duration_seconds(cls) -> str:
        """The duration of the completed phase.

        Stability:
            experimental
        """
        return jsii.sget(cls, "completedPhaseDurationSeconds")

    @classproperty
    @jsii.member(jsii_name="completedPhaseStatus")
    def completed_phase_status(cls) -> str:
        """The status of the completed phase.

        Stability:
            experimental
        """
        return jsii.sget(cls, "completedPhaseStatus")

    @classproperty
    @jsii.member(jsii_name="projectName")
    def project_name(cls) -> str:
        """The triggering build's project name.

        Stability:
            experimental
        """
        return jsii.sget(cls, "projectName")


@jsii.data_type(jsii_type="@aws-cdk/aws-codebuild.PipelineProjectProps", jsii_struct_bases=[CommonProjectProps])
class PipelineProjectProps(CommonProjectProps, jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    pass

@jsii.implements(IProject)
class Project(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codebuild.Project"):
    """A representation of a CodeBuild Project.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, artifacts: typing.Optional["BuildArtifacts"]=None, secondary_artifacts: typing.Optional[typing.List["BuildArtifacts"]]=None, secondary_sources: typing.Optional[typing.List["BuildSource"]]=None, source: typing.Optional["BuildSource"]=None, allow_all_outbound: typing.Optional[bool]=None, badge: typing.Optional[bool]=None, build_script_asset: typing.Optional[aws_cdk.assets.Asset]=None, build_script_asset_entrypoint: typing.Optional[str]=None, build_spec: typing.Any=None, cache: typing.Optional["Cache"]=None, description: typing.Optional[str]=None, encryption_key: typing.Optional[aws_cdk.aws_kms.IKey]=None, environment: typing.Optional["BuildEnvironment"]=None, environment_variables: typing.Optional[typing.Mapping[str,"BuildEnvironmentVariable"]]=None, project_name: typing.Optional[str]=None, role: typing.Optional[aws_cdk.aws_iam.IRole]=None, security_groups: typing.Optional[typing.List[aws_cdk.aws_ec2.ISecurityGroup]]=None, subnet_selection: typing.Optional[aws_cdk.aws_ec2.SubnetSelection]=None, timeout: typing.Optional[jsii.Number]=None, vpc: typing.Optional[aws_cdk.aws_ec2.IVpc]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            artifacts: Defines where build artifacts will be stored. Could be: PipelineBuildArtifacts, NoBuildArtifacts and S3BucketBuildArtifacts. Default: NoBuildArtifacts
            secondaryArtifacts: The secondary artifacts for the Project. Can also be added after the Project has been created by using the {@link Project#addSecondaryArtifact} method. Default: - No secondary artifacts.
            secondarySources: The secondary sources for the Project. Can be also added after the Project has been created by using the {@link Project#addSecondarySource} method. Default: - No secondary sources.
            source: The source of the build. *Note*: if {@link NoSource} is given as the source, then you need to provide an explicit ``buildSpec``. Default: - NoSource
            allowAllOutbound: Whether to allow the CodeBuild to send all network traffic. If set to false, you must individually add traffic rules to allow the CodeBuild project to connect to network targets. Only used if 'vpc' is supplied. Default: true
            badge: Indicates whether AWS CodeBuild generates a publicly accessible URL for your project's build badge. For more information, see Build Badges Sample in the AWS CodeBuild User Guide. Default: false
            buildScriptAsset: Run a script from an asset as build script. If supplied together with buildSpec, the asset script will be run *after* the existing commands in buildspec. This feature can also be used without a source, to simply run an arbitrary script in a serverless way. Default: - No asset build script.
            buildScriptAssetEntrypoint: The script in the asset to run. Default: build.sh
            buildSpec: Filename or contents of buildspec in JSON format. Default: - Empty buildspec.
            cache: Caching strategy to use. Default: Cache.none
            description: A description of the project. Use the description to identify the purpose of the project. Default: - No description.
            encryptionKey: Encryption key to use to read and write artifacts. Default: - The AWS-managed CMK for Amazon Simple Storage Service (Amazon S3) is used.
            environment: Build environment to use for the build. Default: BuildEnvironment.LinuxBuildImage.STANDARD_1_0
            environmentVariables: Additional environment variables to add to the build environment. Default: - No additional environment variables are specified.
            projectName: The physical, human-readable name of the CodeBuild Project. Default: - Name is automatically generated.
            role: Service Role to assume while running the build. Default: - A role will be created.
            securityGroups: What security group to associate with the codebuild project's network interfaces. If no security group is identified, one will be created automatically. Only used if 'vpc' is supplied. Default: - Security group will be automatically created.
            subnetSelection: Where to place the network interfaces within the VPC. Only used if 'vpc' is supplied. Default: - All private subnets.
            timeout: The number of minutes after which AWS CodeBuild stops the build if it's not complete. For valid values, see the timeoutInMinutes field in the AWS CodeBuild User Guide. Default: 60
            vpc: VPC network to place codebuild network interfaces. Specify this if the codebuild project needs to access resources in a VPC. Default: - No VPC is specified.

        Stability:
            experimental
        """
        props: ProjectProps = {}

        if artifacts is not None:
            props["artifacts"] = artifacts

        if secondary_artifacts is not None:
            props["secondaryArtifacts"] = secondary_artifacts

        if secondary_sources is not None:
            props["secondarySources"] = secondary_sources

        if source is not None:
            props["source"] = source

        if allow_all_outbound is not None:
            props["allowAllOutbound"] = allow_all_outbound

        if badge is not None:
            props["badge"] = badge

        if build_script_asset is not None:
            props["buildScriptAsset"] = build_script_asset

        if build_script_asset_entrypoint is not None:
            props["buildScriptAssetEntrypoint"] = build_script_asset_entrypoint

        if build_spec is not None:
            props["buildSpec"] = build_spec

        if cache is not None:
            props["cache"] = cache

        if description is not None:
            props["description"] = description

        if encryption_key is not None:
            props["encryptionKey"] = encryption_key

        if environment is not None:
            props["environment"] = environment

        if environment_variables is not None:
            props["environmentVariables"] = environment_variables

        if project_name is not None:
            props["projectName"] = project_name

        if role is not None:
            props["role"] = role

        if security_groups is not None:
            props["securityGroups"] = security_groups

        if subnet_selection is not None:
            props["subnetSelection"] = subnet_selection

        if timeout is not None:
            props["timeout"] = timeout

        if vpc is not None:
            props["vpc"] = vpc

        jsii.create(Project, self, [scope, id, props])

    @jsii.member(jsii_name="fromProjectArn")
    @classmethod
    def from_project_arn(cls, scope: aws_cdk.cdk.Construct, id: str, project_arn: str) -> "IProject":
        """
        Arguments:
            scope: -
            id: -
            projectArn: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromProjectArn", [scope, id, project_arn])

    @jsii.member(jsii_name="fromProjectName")
    @classmethod
    def from_project_name(cls, scope: aws_cdk.cdk.Construct, id: str, project_name: str) -> "IProject":
        """Import a Project defined either outside the CDK, or in a different CDK Stack (and exported using the {@link export} method).

        Arguments:
            scope: the parent Construct for this Construct.
            id: the logical name of this Construct.
            projectName: the name of the project to import.

        Returns:
            a reference to the existing Project

        Stability:
            experimental
        note:
            if you're importing a CodeBuild Project for use
            in a CodePipeline, make sure the existing Project
            has permissions to access the S3 Bucket of that Pipeline -
            otherwise, builds in that Pipeline will always fail.
        """
        return jsii.sinvoke(cls, "fromProjectName", [scope, id, project_name])

    @jsii.member(jsii_name="addSecondaryArtifact")
    def add_secondary_artifact(self, secondary_artifact: "BuildArtifacts") -> typing.Any:
        """Adds a secondary artifact to the Project.

        Arguments:
            secondaryArtifact: the artifact to add as a secondary artifact.

        See:
            https://docs.aws.amazon.com/codebuild/latest/userguide/sample-multi-in-out.html
        Stability:
            experimental
        """
        return jsii.invoke(self, "addSecondaryArtifact", [secondary_artifact])

    @jsii.member(jsii_name="addSecondarySource")
    def add_secondary_source(self, secondary_source: "BuildSource") -> None:
        """Adds a secondary source to the Project.

        Arguments:
            secondarySource: the source to add as a secondary source.

        See:
            https://docs.aws.amazon.com/codebuild/latest/userguide/sample-multi-in-out.html
        Stability:
            experimental
        """
        return jsii.invoke(self, "addSecondarySource", [secondary_source])

    @jsii.member(jsii_name="addToRoleInlinePolicy")
    def add_to_role_inline_policy(self, statement: aws_cdk.aws_iam.PolicyStatement) -> None:
        """Add a permission only if there's a policy attached.

        Arguments:
            statement: The permissions statement to add.

        Stability:
            experimental
        """
        return jsii.invoke(self, "addToRoleInlinePolicy", [statement])

    @jsii.member(jsii_name="addToRolePolicy")
    def add_to_role_policy(self, statement: aws_cdk.aws_iam.PolicyStatement) -> None:
        """Add a permission only if there's a policy attached.

        Arguments:
            statement: The permissions statement to add.

        Stability:
            experimental
        """
        return jsii.invoke(self, "addToRolePolicy", [statement])

    @jsii.member(jsii_name="metric")
    def metric(self, metric_name: str, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """
        Arguments:
            metricName: The name of the metric.
            props: Customization properties.
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Returns:
            a CloudWatch metric associated with this build project.

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metric", [metric_name, props])

    @jsii.member(jsii_name="metricBuilds")
    def metric_builds(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Measures the number of builds triggered.

        Units: Count

        Valid CloudWatch statistics: Sum

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Default:
            sum over 5 minutes

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricBuilds", [props])

    @jsii.member(jsii_name="metricDuration")
    def metric_duration(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Measures the duration of all builds over time.

        Units: Seconds

        Valid CloudWatch statistics: Average (recommended), Maximum, Minimum

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Default:
            average over 5 minutes

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricDuration", [props])

    @jsii.member(jsii_name="metricFailedBuilds")
    def metric_failed_builds(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Measures the number of builds that failed because of client error or because of a timeout.

        Units: Count

        Valid CloudWatch statistics: Sum

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Default:
            sum over 5 minutes

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricFailedBuilds", [props])

    @jsii.member(jsii_name="metricSucceededBuilds")
    def metric_succeeded_builds(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Measures the number of successful builds.

        Units: Count

        Valid CloudWatch statistics: Sum

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Default:
            sum over 5 minutes

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricSucceededBuilds", [props])

    @jsii.member(jsii_name="onBuildFailed")
    def on_build_failed(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines an event rule which triggers when a build fails.

        To access fields from the event in the event target input,
        use the static fields on the ``StateChangeEvent`` class.

        Arguments:
            id: -
            options: -
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        options: aws_cdk.aws_events.OnEventOptions = {"target": target}

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        return jsii.invoke(self, "onBuildFailed", [id, options])

    @jsii.member(jsii_name="onBuildStarted")
    def on_build_started(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines an event rule which triggers when a build starts.

        To access fields from the event in the event target input,
        use the static fields on the ``StateChangeEvent`` class.

        Arguments:
            id: -
            options: -
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        options: aws_cdk.aws_events.OnEventOptions = {"target": target}

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        return jsii.invoke(self, "onBuildStarted", [id, options])

    @jsii.member(jsii_name="onBuildSucceeded")
    def on_build_succeeded(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines an event rule which triggers when a build completes successfully.

        To access fields from the event in the event target input,
        use the static fields on the ``StateChangeEvent`` class.

        Arguments:
            id: -
            options: -
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        options: aws_cdk.aws_events.OnEventOptions = {"target": target}

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        return jsii.invoke(self, "onBuildSucceeded", [id, options])

    @jsii.member(jsii_name="onEvent")
    def on_event(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule triggered when something happens with this project.

        Arguments:
            id: -
            options: -
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        See:
            https://docs.aws.amazon.com/codebuild/latest/userguide/sample-build-notifications.html
        Stability:
            experimental
        """
        options: aws_cdk.aws_events.OnEventOptions = {"target": target}

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        return jsii.invoke(self, "onEvent", [id, options])

    @jsii.member(jsii_name="onPhaseChange")
    def on_phase_change(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule that triggers upon phase change of this build project.

        Arguments:
            id: -
            options: -
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        See:
            https://docs.aws.amazon.com/codebuild/latest/userguide/sample-build-notifications.html
        Stability:
            experimental
        """
        options: aws_cdk.aws_events.OnEventOptions = {"target": target}

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        return jsii.invoke(self, "onPhaseChange", [id, options])

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule triggered when the build project state changes.

        You can filter specific build status events using an event
        pattern filter on the ``build-status`` detail field::

           const rule = project.onStateChange('OnBuildStarted', target);
           rule.addEventPattern({
             detail: {
               'build-status': [
                 "IN_PROGRESS",
                 "SUCCEEDED",
                 "FAILED",
                 "STOPPED"
               ]
             }
           });

        You can also use the methods ``onBuildFailed`` and ``onBuildSucceeded`` to define rules for
        these specific state changes.

        To access fields from the event in the event target input,
        use the static fields on the ``StateChangeEvent`` class.

        Arguments:
            id: -
            options: -
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        See:
            https://docs.aws.amazon.com/codebuild/latest/userguide/sample-build-notifications.html
        Stability:
            experimental
        """
        options: aws_cdk.aws_events.OnEventOptions = {"target": target}

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        return jsii.invoke(self, "onStateChange", [id, options])

    @jsii.member(jsii_name="validate")
    def _validate(self) -> typing.List[str]:
        """Validate the current construct.

        This method can be implemented by derived constructs in order to perform
        validation logic. It is called on all constructs before synthesis.

        Stability:
            experimental
        override:
            true
        """
        return jsii.invoke(self, "validate", [])

    @property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> aws_cdk.aws_iam.IPrincipal:
        """The principal to grant permissions to.

        Stability:
            experimental
        """
        return jsii.get(self, "grantPrincipal")

    @property
    @jsii.member(jsii_name="projectArn")
    def project_arn(self) -> str:
        """The ARN of the project.

        Stability:
            experimental
        """
        return jsii.get(self, "projectArn")

    @property
    @jsii.member(jsii_name="projectName")
    def project_name(self) -> str:
        """The name of the project.

        Stability:
            experimental
        """
        return jsii.get(self, "projectName")

    @property
    @jsii.member(jsii_name="securityGroups")
    def security_groups(self) -> typing.List[aws_cdk.aws_ec2.ISecurityGroup]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "securityGroups")

    @property
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        """The IAM role for this project.

        Stability:
            experimental
        """
        return jsii.get(self, "role")


class PipelineProject(Project, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codebuild.PipelineProject"):
    """A convenience class for CodeBuild Projects that are used in CodePipeline.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, allow_all_outbound: typing.Optional[bool]=None, badge: typing.Optional[bool]=None, build_script_asset: typing.Optional[aws_cdk.assets.Asset]=None, build_script_asset_entrypoint: typing.Optional[str]=None, build_spec: typing.Any=None, cache: typing.Optional["Cache"]=None, description: typing.Optional[str]=None, encryption_key: typing.Optional[aws_cdk.aws_kms.IKey]=None, environment: typing.Optional["BuildEnvironment"]=None, environment_variables: typing.Optional[typing.Mapping[str,"BuildEnvironmentVariable"]]=None, project_name: typing.Optional[str]=None, role: typing.Optional[aws_cdk.aws_iam.IRole]=None, security_groups: typing.Optional[typing.List[aws_cdk.aws_ec2.ISecurityGroup]]=None, subnet_selection: typing.Optional[aws_cdk.aws_ec2.SubnetSelection]=None, timeout: typing.Optional[jsii.Number]=None, vpc: typing.Optional[aws_cdk.aws_ec2.IVpc]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            allowAllOutbound: Whether to allow the CodeBuild to send all network traffic. If set to false, you must individually add traffic rules to allow the CodeBuild project to connect to network targets. Only used if 'vpc' is supplied. Default: true
            badge: Indicates whether AWS CodeBuild generates a publicly accessible URL for your project's build badge. For more information, see Build Badges Sample in the AWS CodeBuild User Guide. Default: false
            buildScriptAsset: Run a script from an asset as build script. If supplied together with buildSpec, the asset script will be run *after* the existing commands in buildspec. This feature can also be used without a source, to simply run an arbitrary script in a serverless way. Default: - No asset build script.
            buildScriptAssetEntrypoint: The script in the asset to run. Default: build.sh
            buildSpec: Filename or contents of buildspec in JSON format. Default: - Empty buildspec.
            cache: Caching strategy to use. Default: Cache.none
            description: A description of the project. Use the description to identify the purpose of the project. Default: - No description.
            encryptionKey: Encryption key to use to read and write artifacts. Default: - The AWS-managed CMK for Amazon Simple Storage Service (Amazon S3) is used.
            environment: Build environment to use for the build. Default: BuildEnvironment.LinuxBuildImage.STANDARD_1_0
            environmentVariables: Additional environment variables to add to the build environment. Default: - No additional environment variables are specified.
            projectName: The physical, human-readable name of the CodeBuild Project. Default: - Name is automatically generated.
            role: Service Role to assume while running the build. Default: - A role will be created.
            securityGroups: What security group to associate with the codebuild project's network interfaces. If no security group is identified, one will be created automatically. Only used if 'vpc' is supplied. Default: - Security group will be automatically created.
            subnetSelection: Where to place the network interfaces within the VPC. Only used if 'vpc' is supplied. Default: - All private subnets.
            timeout: The number of minutes after which AWS CodeBuild stops the build if it's not complete. For valid values, see the timeoutInMinutes field in the AWS CodeBuild User Guide. Default: 60
            vpc: VPC network to place codebuild network interfaces. Specify this if the codebuild project needs to access resources in a VPC. Default: - No VPC is specified.

        Stability:
            experimental
        """
        props: PipelineProjectProps = {}

        if allow_all_outbound is not None:
            props["allowAllOutbound"] = allow_all_outbound

        if badge is not None:
            props["badge"] = badge

        if build_script_asset is not None:
            props["buildScriptAsset"] = build_script_asset

        if build_script_asset_entrypoint is not None:
            props["buildScriptAssetEntrypoint"] = build_script_asset_entrypoint

        if build_spec is not None:
            props["buildSpec"] = build_spec

        if cache is not None:
            props["cache"] = cache

        if description is not None:
            props["description"] = description

        if encryption_key is not None:
            props["encryptionKey"] = encryption_key

        if environment is not None:
            props["environment"] = environment

        if environment_variables is not None:
            props["environmentVariables"] = environment_variables

        if project_name is not None:
            props["projectName"] = project_name

        if role is not None:
            props["role"] = role

        if security_groups is not None:
            props["securityGroups"] = security_groups

        if subnet_selection is not None:
            props["subnetSelection"] = subnet_selection

        if timeout is not None:
            props["timeout"] = timeout

        if vpc is not None:
            props["vpc"] = vpc

        jsii.create(PipelineProject, self, [scope, id, props])


@jsii.data_type(jsii_type="@aws-cdk/aws-codebuild.ProjectProps", jsii_struct_bases=[CommonProjectProps])
class ProjectProps(CommonProjectProps, jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    artifacts: "BuildArtifacts"
    """Defines where build artifacts will be stored. Could be: PipelineBuildArtifacts, NoBuildArtifacts and S3BucketBuildArtifacts.

    Default:
        NoBuildArtifacts

    Stability:
        experimental
    """

    secondaryArtifacts: typing.List["BuildArtifacts"]
    """The secondary artifacts for the Project. Can also be added after the Project has been created by using the {@link Project#addSecondaryArtifact} method.

    Default:
        - No secondary artifacts.

    See:
        https://docs.aws.amazon.com/codebuild/latest/userguide/sample-multi-in-out.html
    Stability:
        experimental
    """

    secondarySources: typing.List["BuildSource"]
    """The secondary sources for the Project. Can be also added after the Project has been created by using the {@link Project#addSecondarySource} method.

    Default:
        - No secondary sources.

    See:
        https://docs.aws.amazon.com/codebuild/latest/userguide/sample-multi-in-out.html
    Stability:
        experimental
    """

    source: "BuildSource"
    """The source of the build. *Note*: if {@link NoSource} is given as the source, then you need to provide an explicit ``buildSpec``.

    Default:
        - NoSource

    Stability:
        experimental
    """

class S3BucketBuildArtifacts(BuildArtifacts, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codebuild.S3BucketBuildArtifacts"):
    """S3 Artifact definition for a CodeBuild Project.

    Stability:
        experimental
    """
    def __init__(self, *, bucket: aws_cdk.aws_s3.IBucket, name: str, include_build_id: typing.Optional[bool]=None, package_zip: typing.Optional[bool]=None, path: typing.Optional[str]=None, identifier: typing.Optional[str]=None) -> None:
        """
        Arguments:
            props: -
            bucket: The name of the output bucket.
            name: The name of the build output ZIP file or folder inside the bucket. The full S3 object key will be "//" or "/" depending on whether ``includeBuildId`` is set to true.
            includeBuildId: Indicates if the build ID should be included in the path. If this is set to true, then the build artifact will be stored in "//". Default: true
            packageZip: If this is true, all build output will be packaged into a single .zip file. Otherwise, all files will be uploaded to /. Default: true - files will be archived
            path: The path inside of the bucket for the build output .zip file or folder. If a value is not specified, then build output will be stored at the root of the bucket (or under the directory if ``includeBuildId`` is set to true).
            identifier: The artifact identifier. This property is required on secondary artifacts.

        Stability:
            experimental
        """
        props: S3BucketBuildArtifactsProps = {"bucket": bucket, "name": name}

        if include_build_id is not None:
            props["includeBuildId"] = include_build_id

        if package_zip is not None:
            props["packageZip"] = package_zip

        if path is not None:
            props["path"] = path

        if identifier is not None:
            props["identifier"] = identifier

        jsii.create(S3BucketBuildArtifacts, self, [props])

    @jsii.member(jsii_name="toArtifactsProperty")
    def _to_artifacts_property(self) -> typing.Any:
        """
        Stability:
            experimental
        """
        return jsii.invoke(self, "toArtifactsProperty", [])

    @property
    @jsii.member(jsii_name="props")
    def props(self) -> "S3BucketBuildArtifactsProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "props")

    @property
    @jsii.member(jsii_name="type")
    def _type(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "type")


@jsii.data_type_optionals(jsii_struct_bases=[BuildArtifactsProps])
class _S3BucketBuildArtifactsProps(BuildArtifactsProps, jsii.compat.TypedDict, total=False):
    includeBuildId: bool
    """Indicates if the build ID should be included in the path.

    If this is set to true,
    then the build artifact will be stored in "//".

    Default:
        true

    Stability:
        experimental
    """
    packageZip: bool
    """If this is true, all build output will be packaged into a single .zip file. Otherwise, all files will be uploaded to /.

    Default:
        true - files will be archived

    Stability:
        experimental
    """
    path: str
    """The path inside of the bucket for the build output .zip file or folder. If a value is not specified, then build output will be stored at the root of the bucket (or under the  directory if ``includeBuildId`` is set to true).

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-codebuild.S3BucketBuildArtifactsProps", jsii_struct_bases=[_S3BucketBuildArtifactsProps])
class S3BucketBuildArtifactsProps(_S3BucketBuildArtifactsProps):
    """Construction properties for {@link S3BucketBuildArtifacts}.

    Stability:
        experimental
    """
    bucket: aws_cdk.aws_s3.IBucket
    """The name of the output bucket.

    Stability:
        experimental
    """

    name: str
    """The name of the build output ZIP file or folder inside the bucket.

    The full S3 object key will be "//" or
    "/" depending on whether ``includeBuildId`` is set to true.

    Stability:
        experimental
    """

class S3BucketSource(BuildSource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codebuild.S3BucketSource"):
    """S3 bucket definition for a CodeBuild project.

    Stability:
        experimental
    """
    def __init__(self, *, bucket: aws_cdk.aws_s3.IBucket, path: str, identifier: typing.Optional[str]=None) -> None:
        """
        Arguments:
            props: -
            bucket: 
            path: 
            identifier: The source identifier. This property is required on secondary sources.

        Stability:
            experimental
        """
        props: S3BucketSourceProps = {"bucket": bucket, "path": path}

        if identifier is not None:
            props["identifier"] = identifier

        jsii.create(S3BucketSource, self, [props])

    @jsii.member(jsii_name="toSourceProperty")
    def _to_source_property(self) -> typing.Any:
        """
        Stability:
            experimental
        """
        return jsii.invoke(self, "toSourceProperty", [])

    @property
    @jsii.member(jsii_name="type")
    def type(self) -> "SourceType":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "type")


@jsii.data_type(jsii_type="@aws-cdk/aws-codebuild.S3BucketSourceProps", jsii_struct_bases=[BuildSourceProps])
class S3BucketSourceProps(BuildSourceProps, jsii.compat.TypedDict):
    """Construction properties for {@link S3BucketSource}.

    Stability:
        experimental
    """
    bucket: aws_cdk.aws_s3.IBucket
    """
    Stability:
        experimental
    """

    path: str
    """
    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-codebuild.SourceType")
class SourceType(enum.Enum):
    """Source types for CodeBuild Project.

    Stability:
        experimental
    """
    None_ = "None"
    """
    Stability:
        experimental
    """
    CodeCommit = "CodeCommit"
    """
    Stability:
        experimental
    """
    CodePipeline = "CodePipeline"
    """
    Stability:
        experimental
    """
    GitHub = "GitHub"
    """
    Stability:
        experimental
    """
    GitHubEnterprise = "GitHubEnterprise"
    """
    Stability:
        experimental
    """
    BitBucket = "BitBucket"
    """
    Stability:
        experimental
    """
    S3 = "S3"
    """
    Stability:
        experimental
    """

class StateChangeEvent(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codebuild.StateChangeEvent"):
    """Event fields for the CodeBuild "state change" event.

    See:
        https://docs.aws.amazon.com/codebuild/latest/userguide/sample-build-notifications.html#sample-build-notifications-ref
    Stability:
        experimental
    """
    @classproperty
    @jsii.member(jsii_name="buildId")
    def build_id(cls) -> str:
        """Return the build id.

        Stability:
            experimental
        """
        return jsii.sget(cls, "buildId")

    @classproperty
    @jsii.member(jsii_name="buildStatus")
    def build_status(cls) -> str:
        """The triggering build's status.

        Stability:
            experimental
        """
        return jsii.sget(cls, "buildStatus")

    @classproperty
    @jsii.member(jsii_name="currentPhase")
    def current_phase(cls) -> str:
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "currentPhase")

    @classproperty
    @jsii.member(jsii_name="projectName")
    def project_name(cls) -> str:
        """The triggering build's project name.

        Stability:
            experimental
        """
        return jsii.sget(cls, "projectName")


class ThirdPartyGitBuildSource(GitBuildSource, metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/aws-codebuild.ThirdPartyGitBuildSource"):
    """A common superclass of all third-party build sources that are backed by Git.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _ThirdPartyGitBuildSourceProxy

    def __init__(self, *, report_build_status: typing.Optional[bool]=None, webhook: typing.Optional[bool]=None, webhook_filters: typing.Optional[typing.List["FilterGroup"]]=None, clone_depth: typing.Optional[jsii.Number]=None, identifier: typing.Optional[str]=None) -> None:
        """
        Arguments:
            props: -
            reportBuildStatus: Whether to send notifications on your build's start and end. Default: true
            webhook: Whether to create a webhook that will trigger a build every time an event happens in the repository. Default: true if any ``webhookFilters`` were provided, false otherwise
            webhookFilters: A list of webhook filters that can constraint what events in the repository will trigger a build. A build is triggered if any of the provided filter groups match. Only valid if ``webhook`` was not provided as false. Default: every push and every Pull Request (create or update) triggers a build
            cloneDepth: The depth of history to download. Minimum value is 0. If this value is 0, greater than 25, or not provided, then the full history is downloaded with each build of the project.
            identifier: The source identifier. This property is required on secondary sources.

        Stability:
            experimental
        """
        props: ThirdPartyGitBuildSourceProps = {}

        if report_build_status is not None:
            props["reportBuildStatus"] = report_build_status

        if webhook is not None:
            props["webhook"] = webhook

        if webhook_filters is not None:
            props["webhookFilters"] = webhook_filters

        if clone_depth is not None:
            props["cloneDepth"] = clone_depth

        if identifier is not None:
            props["identifier"] = identifier

        jsii.create(ThirdPartyGitBuildSource, self, [props])

    @property
    @jsii.member(jsii_name="badgeSupported")
    def badge_supported(self) -> bool:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "badgeSupported")

    @property
    @jsii.member(jsii_name="webhookFilters")
    def _webhook_filters(self) -> typing.List["FilterGroup"]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "webhookFilters")


class _ThirdPartyGitBuildSourceProxy(ThirdPartyGitBuildSource, jsii.proxy_for(GitBuildSource)):
    pass

class BitBucketSource(ThirdPartyGitBuildSource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codebuild.BitBucketSource"):
    """BitBucket Source definition for a CodeBuild project.

    Stability:
        experimental
    """
    def __init__(self, *, owner: str, repo: str, report_build_status: typing.Optional[bool]=None, webhook: typing.Optional[bool]=None, webhook_filters: typing.Optional[typing.List["FilterGroup"]]=None, clone_depth: typing.Optional[jsii.Number]=None, identifier: typing.Optional[str]=None) -> None:
        """
        Arguments:
            props: -
            owner: The BitBucket account/user that owns the repo.
            repo: The name of the repo (without the username).
            reportBuildStatus: Whether to send notifications on your build's start and end. Default: true
            webhook: Whether to create a webhook that will trigger a build every time an event happens in the repository. Default: true if any ``webhookFilters`` were provided, false otherwise
            webhookFilters: A list of webhook filters that can constraint what events in the repository will trigger a build. A build is triggered if any of the provided filter groups match. Only valid if ``webhook`` was not provided as false. Default: every push and every Pull Request (create or update) triggers a build
            cloneDepth: The depth of history to download. Minimum value is 0. If this value is 0, greater than 25, or not provided, then the full history is downloaded with each build of the project.
            identifier: The source identifier. This property is required on secondary sources.

        Stability:
            experimental
        """
        props: BitBucketSourceProps = {"owner": owner, "repo": repo}

        if report_build_status is not None:
            props["reportBuildStatus"] = report_build_status

        if webhook is not None:
            props["webhook"] = webhook

        if webhook_filters is not None:
            props["webhookFilters"] = webhook_filters

        if clone_depth is not None:
            props["cloneDepth"] = clone_depth

        if identifier is not None:
            props["identifier"] = identifier

        jsii.create(BitBucketSource, self, [props])

    @jsii.member(jsii_name="toSourceProperty")
    def _to_source_property(self) -> typing.Any:
        """
        Stability:
            experimental
        """
        return jsii.invoke(self, "toSourceProperty", [])

    @property
    @jsii.member(jsii_name="type")
    def type(self) -> "SourceType":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "type")


class GitHubEnterpriseSource(ThirdPartyGitBuildSource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codebuild.GitHubEnterpriseSource"):
    """GitHub Enterprise Source definition for a CodeBuild project.

    Stability:
        experimental
    """
    def __init__(self, *, https_clone_url: str, ignore_ssl_errors: typing.Optional[bool]=None, report_build_status: typing.Optional[bool]=None, webhook: typing.Optional[bool]=None, webhook_filters: typing.Optional[typing.List["FilterGroup"]]=None, clone_depth: typing.Optional[jsii.Number]=None, identifier: typing.Optional[str]=None) -> None:
        """
        Arguments:
            props: -
            httpsCloneUrl: The HTTPS URL of the repository in your GitHub Enterprise installation.
            ignoreSslErrors: Whether to ignore SSL errors when connecting to the repository. Default: false
            reportBuildStatus: Whether to send notifications on your build's start and end. Default: true
            webhook: Whether to create a webhook that will trigger a build every time an event happens in the repository. Default: true if any ``webhookFilters`` were provided, false otherwise
            webhookFilters: A list of webhook filters that can constraint what events in the repository will trigger a build. A build is triggered if any of the provided filter groups match. Only valid if ``webhook`` was not provided as false. Default: every push and every Pull Request (create or update) triggers a build
            cloneDepth: The depth of history to download. Minimum value is 0. If this value is 0, greater than 25, or not provided, then the full history is downloaded with each build of the project.
            identifier: The source identifier. This property is required on secondary sources.

        Stability:
            experimental
        """
        props: GitHubEnterpriseSourceProps = {"httpsCloneUrl": https_clone_url}

        if ignore_ssl_errors is not None:
            props["ignoreSslErrors"] = ignore_ssl_errors

        if report_build_status is not None:
            props["reportBuildStatus"] = report_build_status

        if webhook is not None:
            props["webhook"] = webhook

        if webhook_filters is not None:
            props["webhookFilters"] = webhook_filters

        if clone_depth is not None:
            props["cloneDepth"] = clone_depth

        if identifier is not None:
            props["identifier"] = identifier

        jsii.create(GitHubEnterpriseSource, self, [props])

    @jsii.member(jsii_name="toSourceProperty")
    def _to_source_property(self) -> typing.Any:
        """
        Stability:
            experimental
        """
        return jsii.invoke(self, "toSourceProperty", [])

    @property
    @jsii.member(jsii_name="type")
    def type(self) -> "SourceType":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "type")


class GitHubSource(ThirdPartyGitBuildSource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codebuild.GitHubSource"):
    """GitHub Source definition for a CodeBuild project.

    Stability:
        experimental
    """
    def __init__(self, *, owner: str, repo: str, report_build_status: typing.Optional[bool]=None, webhook: typing.Optional[bool]=None, webhook_filters: typing.Optional[typing.List["FilterGroup"]]=None, clone_depth: typing.Optional[jsii.Number]=None, identifier: typing.Optional[str]=None) -> None:
        """
        Arguments:
            props: -
            owner: The GitHub account/user that owns the repo.
            repo: The name of the repo (without the username).
            reportBuildStatus: Whether to send notifications on your build's start and end. Default: true
            webhook: Whether to create a webhook that will trigger a build every time an event happens in the repository. Default: true if any ``webhookFilters`` were provided, false otherwise
            webhookFilters: A list of webhook filters that can constraint what events in the repository will trigger a build. A build is triggered if any of the provided filter groups match. Only valid if ``webhook`` was not provided as false. Default: every push and every Pull Request (create or update) triggers a build
            cloneDepth: The depth of history to download. Minimum value is 0. If this value is 0, greater than 25, or not provided, then the full history is downloaded with each build of the project.
            identifier: The source identifier. This property is required on secondary sources.

        Stability:
            experimental
        """
        props: GitHubSourceProps = {"owner": owner, "repo": repo}

        if report_build_status is not None:
            props["reportBuildStatus"] = report_build_status

        if webhook is not None:
            props["webhook"] = webhook

        if webhook_filters is not None:
            props["webhookFilters"] = webhook_filters

        if clone_depth is not None:
            props["cloneDepth"] = clone_depth

        if identifier is not None:
            props["identifier"] = identifier

        jsii.create(GitHubSource, self, [props])

    @jsii.member(jsii_name="toSourceProperty")
    def _to_source_property(self) -> typing.Any:
        """
        Stability:
            experimental
        """
        return jsii.invoke(self, "toSourceProperty", [])

    @property
    @jsii.member(jsii_name="type")
    def type(self) -> "SourceType":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "type")


@jsii.data_type(jsii_type="@aws-cdk/aws-codebuild.ThirdPartyGitBuildSourceProps", jsii_struct_bases=[GitBuildSourceProps])
class ThirdPartyGitBuildSourceProps(GitBuildSourceProps, jsii.compat.TypedDict, total=False):
    """The construction properties common to all third-party build sources that are backed by Git.

    Stability:
        experimental
    """
    reportBuildStatus: bool
    """Whether to send notifications on your build's start and end.

    Default:
        true

    Stability:
        experimental
    """

    webhook: bool
    """Whether to create a webhook that will trigger a build every time an event happens in the repository.

    Default:
        true if any ``webhookFilters`` were provided, false otherwise

    Stability:
        experimental
    """

    webhookFilters: typing.List["FilterGroup"]
    """A list of webhook filters that can constraint what events in the repository will trigger a build. A build is triggered if any of the provided filter groups match. Only valid if ``webhook`` was not provided as false.

    Default:
        every push and every Pull Request (create or update) triggers a build

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-codebuild.BitBucketSourceProps", jsii_struct_bases=[ThirdPartyGitBuildSourceProps])
class BitBucketSourceProps(ThirdPartyGitBuildSourceProps, jsii.compat.TypedDict):
    """Construction properties for {@link BitBucketSource}.

    Stability:
        experimental
    """
    owner: str
    """The BitBucket account/user that owns the repo.

    Stability:
        experimental

    Example::
        'awslabs'
    """

    repo: str
    """The name of the repo (without the username).

    Stability:
        experimental

    Example::
        'aws-cdk'
    """

@jsii.data_type_optionals(jsii_struct_bases=[ThirdPartyGitBuildSourceProps])
class _GitHubEnterpriseSourceProps(ThirdPartyGitBuildSourceProps, jsii.compat.TypedDict, total=False):
    ignoreSslErrors: bool
    """Whether to ignore SSL errors when connecting to the repository.

    Default:
        false

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-codebuild.GitHubEnterpriseSourceProps", jsii_struct_bases=[_GitHubEnterpriseSourceProps])
class GitHubEnterpriseSourceProps(_GitHubEnterpriseSourceProps):
    """Construction properties for {@link GitHubEnterpriseSource}.

    Stability:
        experimental
    """
    httpsCloneUrl: str
    """The HTTPS URL of the repository in your GitHub Enterprise installation.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-codebuild.GitHubSourceProps", jsii_struct_bases=[ThirdPartyGitBuildSourceProps])
class GitHubSourceProps(ThirdPartyGitBuildSourceProps, jsii.compat.TypedDict):
    """Construction properties for {@link GitHubSource} and {@link GitHubEnterpriseSource}.

    Stability:
        experimental
    """
    owner: str
    """The GitHub account/user that owns the repo.

    Stability:
        experimental

    Example::
        'awslabs'
    """

    repo: str
    """The name of the repo (without the username).

    Stability:
        experimental

    Example::
        'aws-cdk'
    """

@jsii.implements(IBuildImage)
class WindowsBuildImage(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codebuild.WindowsBuildImage"):
    """A CodeBuild image running Windows.

    This class has a bunch of public constants that represent the most popular images.

    You can also specify a custom image using one of the static methods:

    - WindowsBuildImage.fromDockerHub(image)
    - WindowsBuildImage.fromEcrRepository(repo[, tag])
    - WindowsBuildImage.fromAsset(parent, id, props)

    See:
        https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-available.html
    Stability:
        experimental
    """
    @jsii.member(jsii_name="fromAsset")
    @classmethod
    def from_asset(cls, scope: aws_cdk.cdk.Construct, id: str, *, directory: str, build_args: typing.Optional[typing.Mapping[str,str]]=None, repository_name: typing.Optional[str]=None, exclude: typing.Optional[typing.List[str]]=None, follow: typing.Optional[aws_cdk.assets.FollowMode]=None) -> "WindowsBuildImage":
        """Uses an Docker image asset as a Windows build image.

        Arguments:
            scope: -
            id: -
            props: -
            directory: The directory where the Dockerfile is stored.
            buildArgs: Build args to pass to the ``docker build`` command. Default: no build args are passed
            repositoryName: ECR repository name. Specify this property if you need to statically address the image, e.g. from a Kubernetes Pod. Note, this is only the repository name, without the registry and the tag parts. Default: automatically derived from the asset's ID.
            exclude: Glob patterns to exclude from the copy. Default: nothing is excluded
            follow: A strategy for how to handle symlinks. Default: Never

        Stability:
            experimental
        """
        props: aws_cdk.assets_docker.DockerImageAssetProps = {"directory": directory}

        if build_args is not None:
            props["buildArgs"] = build_args

        if repository_name is not None:
            props["repositoryName"] = repository_name

        if exclude is not None:
            props["exclude"] = exclude

        if follow is not None:
            props["follow"] = follow

        return jsii.sinvoke(cls, "fromAsset", [scope, id, props])

    @jsii.member(jsii_name="fromDockerHub")
    @classmethod
    def from_docker_hub(cls, name: str) -> "WindowsBuildImage":
        """
        Arguments:
            name: -

        Returns:
            a Windows build image from a Docker Hub image.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromDockerHub", [name])

    @jsii.member(jsii_name="fromEcrRepository")
    @classmethod
    def from_ecr_repository(cls, repository: aws_cdk.aws_ecr.IRepository, tag: typing.Optional[str]=None) -> "WindowsBuildImage":
        """
        Arguments:
            repository: The ECR repository.
            tag: Image tag (default "latest").

        Returns:
            A Linux build image from an ECR repository.
            
            NOTE: if the repository is external (i.e. imported), then we won't be able to add
            a resource policy statement for it so CodeBuild can pull the image.

        See:
            https://docs.aws.amazon.com/codebuild/latest/userguide/sample-ecr.html
        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromEcrRepository", [repository, tag])

    @jsii.member(jsii_name="runScriptBuildspec")
    def run_script_buildspec(self, entrypoint: str) -> typing.Any:
        """Make a buildspec to run the indicated script.

        Arguments:
            entrypoint: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "runScriptBuildspec", [entrypoint])

    @jsii.member(jsii_name="validate")
    def validate(self, *, build_image: typing.Optional["IBuildImage"]=None, compute_type: typing.Optional["ComputeType"]=None, environment_variables: typing.Optional[typing.Mapping[str,"BuildEnvironmentVariable"]]=None, privileged: typing.Optional[bool]=None) -> typing.List[str]:
        """Allows the image a chance to validate whether the passed configuration is correct.

        Arguments:
            buildEnvironment: -
            buildImage: The image used for the builds. Default: LinuxBuildImage.STANDARD_1_0
            computeType: The type of compute to use for this build. See the {@link ComputeType} enum for the possible values. Default: taken from {@link #buildImage#defaultComputeType}
            environmentVariables: The environment variables that your builds can use.
            privileged: Indicates how the project builds Docker images. Specify true to enable running the Docker daemon inside a Docker container. This value must be set to true only if this build project will be used to build Docker images, and the specified build environment image is not one provided by AWS CodeBuild with Docker support. Otherwise, all associated builds that attempt to interact with the Docker daemon will fail. Default: false

        Stability:
            experimental
        """
        build_environment: BuildEnvironment = {}

        if build_image is not None:
            build_environment["buildImage"] = build_image

        if compute_type is not None:
            build_environment["computeType"] = compute_type

        if environment_variables is not None:
            build_environment["environmentVariables"] = environment_variables

        if privileged is not None:
            build_environment["privileged"] = privileged

        return jsii.invoke(self, "validate", [build_environment])

    @classproperty
    @jsii.member(jsii_name="WIN_SERVER_CORE_2016_BASE")
    def WIN_SERVER_CORE_2016_BASE(cls) -> "WindowsBuildImage":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "WIN_SERVER_CORE_2016_BASE")

    @property
    @jsii.member(jsii_name="defaultComputeType")
    def default_compute_type(self) -> "ComputeType":
        """The default {@link ComputeType} to use with this image, if one was not specified in {@link BuildEnvironment#computeType} explicitly.

        Stability:
            experimental
        """
        return jsii.get(self, "defaultComputeType")

    @property
    @jsii.member(jsii_name="imageId")
    def image_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "imageId")

    @property
    @jsii.member(jsii_name="type")
    def type(self) -> str:
        """The type of build environment.

        Stability:
            experimental
        """
        return jsii.get(self, "type")


__all__ = ["BitBucketSource", "BitBucketSourceProps", "BucketCacheOptions", "BuildArtifacts", "BuildArtifactsProps", "BuildEnvironment", "BuildEnvironmentVariable", "BuildEnvironmentVariableType", "BuildSource", "BuildSourceProps", "Cache", "CfnProject", "CfnProjectProps", "CodeCommitSource", "CodeCommitSourceProps", "CodePipelineBuildArtifacts", "CodePipelineSource", "CommonProjectProps", "ComputeType", "EventAction", "FilterGroup", "GitBuildSource", "GitBuildSourceProps", "GitHubEnterpriseSource", "GitHubEnterpriseSourceProps", "GitHubSource", "GitHubSourceProps", "IBuildImage", "IProject", "LinuxBuildImage", "LocalCacheMode", "NoBuildArtifacts", "NoSource", "PhaseChangeEvent", "PipelineProject", "PipelineProjectProps", "Project", "ProjectProps", "S3BucketBuildArtifacts", "S3BucketBuildArtifactsProps", "S3BucketSource", "S3BucketSourceProps", "SourceType", "StateChangeEvent", "ThirdPartyGitBuildSource", "ThirdPartyGitBuildSourceProps", "WindowsBuildImage", "__jsii_assembly__"]

publication.publish()
