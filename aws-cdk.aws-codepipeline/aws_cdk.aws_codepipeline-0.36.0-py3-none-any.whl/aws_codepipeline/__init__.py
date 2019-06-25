import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_events
import aws_cdk.aws_iam
import aws_cdk.aws_kms
import aws_cdk.aws_s3
import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-codepipeline", "0.36.0", __name__, "aws-codepipeline@0.36.0.jsii.tgz")
@jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.ActionArtifactBounds", jsii_struct_bases=[])
class ActionArtifactBounds(jsii.compat.TypedDict):
    """Specifies the constraints on the number of input and output artifacts an action can have.

    The constraints for each action type are documented on the
    {@link https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html Pipeline Structure Reference} page.

    Stability:
        experimental
    """
    maxInputs: jsii.Number
    """
    Stability:
        experimental
    """

    maxOutputs: jsii.Number
    """
    Stability:
        experimental
    """

    minInputs: jsii.Number
    """
    Stability:
        experimental
    """

    minOutputs: jsii.Number
    """
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.ActionBindOptions", jsii_struct_bases=[])
class ActionBindOptions(jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    role: aws_cdk.aws_iam.IRole
    """
    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-codepipeline.ActionCategory")
class ActionCategory(enum.Enum):
    """
    Stability:
        experimental
    """
    SOURCE = "SOURCE"
    """
    Stability:
        experimental
    """
    BUILD = "BUILD"
    """
    Stability:
        experimental
    """
    TEST = "TEST"
    """
    Stability:
        experimental
    """
    APPROVAL = "APPROVAL"
    """
    Stability:
        experimental
    """
    DEPLOY = "DEPLOY"
    """
    Stability:
        experimental
    """
    INVOKE = "INVOKE"
    """
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.ActionConfig", jsii_struct_bases=[])
class ActionConfig(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    configuration: typing.Any
    """
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _ActionProperties(jsii.compat.TypedDict, total=False):
    inputs: typing.List["Artifact"]
    """
    Stability:
        experimental
    """
    outputs: typing.List["Artifact"]
    """
    Stability:
        experimental
    """
    owner: str
    """
    Stability:
        experimental
    """
    region: str
    """The AWS region the given Action resides in. Note that a cross-region Pipeline requires replication buckets to function correctly. You can provide their names with the {@link PipelineProps#crossRegionReplicationBuckets} property. If you don't, the CodePipeline Construct will create new Stacks in your CDK app containing those buckets, that you will need to ``cdk deploy`` before deploying the main, Pipeline-containing Stack.

    Default:
        the Action resides in the same region as the Pipeline

    Stability:
        experimental
    """
    resource: aws_cdk.core.IResource
    """The optional resource that is backing this Action. This is used for automatically handling Actions backed by resources from a different account and/or region.

    Stability:
        experimental
    """
    role: aws_cdk.aws_iam.IRole
    """
    Stability:
        experimental
    """
    runOrder: jsii.Number
    """The order in which AWS CodePipeline runs this action. For more information, see the AWS CodePipeline User Guide.

    https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html#action-requirements

    Stability:
        experimental
    """
    version: str
    """
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.ActionProperties", jsii_struct_bases=[_ActionProperties])
class ActionProperties(_ActionProperties):
    """
    Stability:
        experimental
    """
    actionName: str
    """
    Stability:
        experimental
    """

    artifactBounds: "ActionArtifactBounds"
    """
    Stability:
        experimental
    """

    category: "ActionCategory"
    """The category of the action. The category defines which action type the owner (the entity that performs the action) performs.

    Stability:
        experimental
    """

    provider: str
    """The service provider that the action calls.

    Stability:
        experimental
    """

class Artifact(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codepipeline.Artifact"):
    """An output artifact of an action.

    Artifacts can be used as input by some actions.

    Stability:
        experimental
    """
    def __init__(self, artifact_name: typing.Optional[str]=None) -> None:
        """
        Arguments:
            artifact_name: -

        Stability:
            experimental
        """
        jsii.create(Artifact, self, [artifact_name])

    @jsii.member(jsii_name="artifact")
    @classmethod
    def artifact(cls, name: str) -> "Artifact":
        """A static factory method used to create instances of the Artifact class. Mainly meant to be used from ``decdk``.

        Arguments:
            name: the (required) name of the Artifact.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "artifact", [name])

    @jsii.member(jsii_name="atPath")
    def at_path(self, file_name: str) -> "ArtifactPath":
        """Returns an ArtifactPath for a file within this artifact. CfnOutput is in the form "::".

        Arguments:
            file_name: The name of the file.

        Stability:
            experimental
        """
        return jsii.invoke(self, "atPath", [file_name])

    @jsii.member(jsii_name="getParam")
    def get_param(self, json_file: str, key_name: str) -> str:
        """Returns a token for a value inside a JSON file within this artifact.

        Arguments:
            json_file: The JSON file name.
            key_name: The hash key.

        Stability:
            experimental
        """
        return jsii.invoke(self, "getParam", [json_file, key_name])

    @jsii.member(jsii_name="toString")
    def to_string(self) -> typing.Optional[str]:
        """
        Stability:
            experimental
        """
        return jsii.invoke(self, "toString", [])

    @property
    @jsii.member(jsii_name="bucketName")
    def bucket_name(self) -> str:
        """The artifact attribute for the name of the S3 bucket where the artifact is stored.

        Stability:
            experimental
        """
        return jsii.get(self, "bucketName")

    @property
    @jsii.member(jsii_name="objectKey")
    def object_key(self) -> str:
        """The artifact attribute for The name of the .zip file that contains the artifact that is generated by AWS CodePipeline, such as 1ABCyZZ.zip.

        Stability:
            experimental
        """
        return jsii.get(self, "objectKey")

    @property
    @jsii.member(jsii_name="s3Location")
    def s3_location(self) -> aws_cdk.aws_s3.Location:
        """Returns the location of the .zip file in S3 that this Artifact represents. Used by Lambda's ``CfnParametersCode`` when being deployed in a CodePipeline.

        Stability:
            experimental
        """
        return jsii.get(self, "s3Location")

    @property
    @jsii.member(jsii_name="url")
    def url(self) -> str:
        """The artifact attribute of the Amazon Simple Storage Service (Amazon S3) URL of the artifact, such as https://s3-us-west-2.amazonaws.com/artifactstorebucket-yivczw8jma0c/test/TemplateSo/1ABCyZZ.zip.

        Stability:
            experimental
        """
        return jsii.get(self, "url")

    @property
    @jsii.member(jsii_name="artifactName")
    def artifact_name(self) -> typing.Optional[str]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "artifactName")


class ArtifactPath(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codepipeline.ArtifactPath"):
    """A specific file within an output artifact.

    The most common use case for this is specifying the template file
    for a CloudFormation action.

    Stability:
        experimental
    """
    def __init__(self, artifact: "Artifact", file_name: str) -> None:
        """
        Arguments:
            artifact: -
            file_name: -

        Stability:
            experimental
        """
        jsii.create(ArtifactPath, self, [artifact, file_name])

    @jsii.member(jsii_name="artifactPath")
    @classmethod
    def artifact_path(cls, artifact_name: str, file_name: str) -> "ArtifactPath":
        """
        Arguments:
            artifact_name: -
            file_name: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "artifactPath", [artifact_name, file_name])

    @property
    @jsii.member(jsii_name="artifact")
    def artifact(self) -> "Artifact":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "artifact")

    @property
    @jsii.member(jsii_name="fileName")
    def file_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "fileName")

    @property
    @jsii.member(jsii_name="location")
    def location(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "location")


class CfnCustomActionType(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codepipeline.CfnCustomActionType"):
    """A CloudFormation ``AWS::CodePipeline::CustomActionType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html
    Stability:
        stable
    cloudformationResource:
        AWS::CodePipeline::CustomActionType
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, category: str, input_artifact_details: typing.Union["ArtifactDetailsProperty", aws_cdk.core.IResolvable], output_artifact_details: typing.Union["ArtifactDetailsProperty", aws_cdk.core.IResolvable], provider: str, version: str, configuration_properties: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ConfigurationPropertiesProperty"]]]]]=None, settings: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SettingsProperty"]]]=None) -> None:
        """Create a new ``AWS::CodePipeline::CustomActionType``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            category: ``AWS::CodePipeline::CustomActionType.Category``.
            input_artifact_details: ``AWS::CodePipeline::CustomActionType.InputArtifactDetails``.
            output_artifact_details: ``AWS::CodePipeline::CustomActionType.OutputArtifactDetails``.
            provider: ``AWS::CodePipeline::CustomActionType.Provider``.
            version: ``AWS::CodePipeline::CustomActionType.Version``.
            configuration_properties: ``AWS::CodePipeline::CustomActionType.ConfigurationProperties``.
            settings: ``AWS::CodePipeline::CustomActionType.Settings``.

        Stability:
            experimental
        """
        props: CfnCustomActionTypeProps = {"category": category, "inputArtifactDetails": input_artifact_details, "outputArtifactDetails": output_artifact_details, "provider": provider, "version": version}

        if configuration_properties is not None:
            props["configurationProperties"] = configuration_properties

        if settings is not None:
            props["settings"] = settings

        jsii.create(CfnCustomActionType, self, [scope, id, props])

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
    @jsii.member(jsii_name="category")
    def category(self) -> str:
        """``AWS::CodePipeline::CustomActionType.Category``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-category
        Stability:
            stable
        """
        return jsii.get(self, "category")

    @category.setter
    def category(self, value: str):
        return jsii.set(self, "category", value)

    @property
    @jsii.member(jsii_name="inputArtifactDetails")
    def input_artifact_details(self) -> typing.Union["ArtifactDetailsProperty", aws_cdk.core.IResolvable]:
        """``AWS::CodePipeline::CustomActionType.InputArtifactDetails``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-inputartifactdetails
        Stability:
            stable
        """
        return jsii.get(self, "inputArtifactDetails")

    @input_artifact_details.setter
    def input_artifact_details(self, value: typing.Union["ArtifactDetailsProperty", aws_cdk.core.IResolvable]):
        return jsii.set(self, "inputArtifactDetails", value)

    @property
    @jsii.member(jsii_name="outputArtifactDetails")
    def output_artifact_details(self) -> typing.Union["ArtifactDetailsProperty", aws_cdk.core.IResolvable]:
        """``AWS::CodePipeline::CustomActionType.OutputArtifactDetails``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-outputartifactdetails
        Stability:
            stable
        """
        return jsii.get(self, "outputArtifactDetails")

    @output_artifact_details.setter
    def output_artifact_details(self, value: typing.Union["ArtifactDetailsProperty", aws_cdk.core.IResolvable]):
        return jsii.set(self, "outputArtifactDetails", value)

    @property
    @jsii.member(jsii_name="provider")
    def provider(self) -> str:
        """``AWS::CodePipeline::CustomActionType.Provider``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-provider
        Stability:
            stable
        """
        return jsii.get(self, "provider")

    @provider.setter
    def provider(self, value: str):
        return jsii.set(self, "provider", value)

    @property
    @jsii.member(jsii_name="version")
    def version(self) -> str:
        """``AWS::CodePipeline::CustomActionType.Version``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-version
        Stability:
            stable
        """
        return jsii.get(self, "version")

    @version.setter
    def version(self, value: str):
        return jsii.set(self, "version", value)

    @property
    @jsii.member(jsii_name="configurationProperties")
    def configuration_properties(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ConfigurationPropertiesProperty"]]]]]:
        """``AWS::CodePipeline::CustomActionType.ConfigurationProperties``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-configurationproperties
        Stability:
            stable
        """
        return jsii.get(self, "configurationProperties")

    @configuration_properties.setter
    def configuration_properties(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ConfigurationPropertiesProperty"]]]]]):
        return jsii.set(self, "configurationProperties", value)

    @property
    @jsii.member(jsii_name="settings")
    def settings(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SettingsProperty"]]]:
        """``AWS::CodePipeline::CustomActionType.Settings``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-settings
        Stability:
            stable
        """
        return jsii.get(self, "settings")

    @settings.setter
    def settings(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SettingsProperty"]]]):
        return jsii.set(self, "settings", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CfnCustomActionType.ArtifactDetailsProperty", jsii_struct_bases=[])
    class ArtifactDetailsProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-artifactdetails.html
        Stability:
            stable
        """
        maximumCount: jsii.Number
        """``CfnCustomActionType.ArtifactDetailsProperty.MaximumCount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-artifactdetails.html#cfn-codepipeline-customactiontype-artifactdetails-maximumcount
        Stability:
            stable
        """

        minimumCount: jsii.Number
        """``CfnCustomActionType.ArtifactDetailsProperty.MinimumCount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-artifactdetails.html#cfn-codepipeline-customactiontype-artifactdetails-minimumcount
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ConfigurationPropertiesProperty(jsii.compat.TypedDict, total=False):
        description: str
        """``CfnCustomActionType.ConfigurationPropertiesProperty.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-configurationproperties.html#cfn-codepipeline-customactiontype-configurationproperties-description
        Stability:
            stable
        """
        queryable: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnCustomActionType.ConfigurationPropertiesProperty.Queryable``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-configurationproperties.html#cfn-codepipeline-customactiontype-configurationproperties-queryable
        Stability:
            stable
        """
        type: str
        """``CfnCustomActionType.ConfigurationPropertiesProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-configurationproperties.html#cfn-codepipeline-customactiontype-configurationproperties-type
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CfnCustomActionType.ConfigurationPropertiesProperty", jsii_struct_bases=[_ConfigurationPropertiesProperty])
    class ConfigurationPropertiesProperty(_ConfigurationPropertiesProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-configurationproperties.html
        Stability:
            stable
        """
        key: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnCustomActionType.ConfigurationPropertiesProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-configurationproperties.html#cfn-codepipeline-customactiontype-configurationproperties-key
        Stability:
            stable
        """

        name: str
        """``CfnCustomActionType.ConfigurationPropertiesProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-configurationproperties.html#cfn-codepipeline-customactiontype-configurationproperties-name
        Stability:
            stable
        """

        required: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnCustomActionType.ConfigurationPropertiesProperty.Required``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-configurationproperties.html#cfn-codepipeline-customactiontype-configurationproperties-required
        Stability:
            stable
        """

        secret: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnCustomActionType.ConfigurationPropertiesProperty.Secret``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-configurationproperties.html#cfn-codepipeline-customactiontype-configurationproperties-secret
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CfnCustomActionType.SettingsProperty", jsii_struct_bases=[])
    class SettingsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-settings.html
        Stability:
            stable
        """
        entityUrlTemplate: str
        """``CfnCustomActionType.SettingsProperty.EntityUrlTemplate``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-settings.html#cfn-codepipeline-customactiontype-settings-entityurltemplate
        Stability:
            stable
        """

        executionUrlTemplate: str
        """``CfnCustomActionType.SettingsProperty.ExecutionUrlTemplate``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-settings.html#cfn-codepipeline-customactiontype-settings-executionurltemplate
        Stability:
            stable
        """

        revisionUrlTemplate: str
        """``CfnCustomActionType.SettingsProperty.RevisionUrlTemplate``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-settings.html#cfn-codepipeline-customactiontype-settings-revisionurltemplate
        Stability:
            stable
        """

        thirdPartyConfigurationUrl: str
        """``CfnCustomActionType.SettingsProperty.ThirdPartyConfigurationUrl``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-settings.html#cfn-codepipeline-customactiontype-settings-thirdpartyconfigurationurl
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnCustomActionTypeProps(jsii.compat.TypedDict, total=False):
    configurationProperties: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCustomActionType.ConfigurationPropertiesProperty"]]]
    """``AWS::CodePipeline::CustomActionType.ConfigurationProperties``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-configurationproperties
    Stability:
        stable
    """
    settings: typing.Union[aws_cdk.core.IResolvable, "CfnCustomActionType.SettingsProperty"]
    """``AWS::CodePipeline::CustomActionType.Settings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-settings
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CfnCustomActionTypeProps", jsii_struct_bases=[_CfnCustomActionTypeProps])
class CfnCustomActionTypeProps(_CfnCustomActionTypeProps):
    """Properties for defining a ``AWS::CodePipeline::CustomActionType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html
    Stability:
        stable
    """
    category: str
    """``AWS::CodePipeline::CustomActionType.Category``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-category
    Stability:
        stable
    """

    inputArtifactDetails: typing.Union["CfnCustomActionType.ArtifactDetailsProperty", aws_cdk.core.IResolvable]
    """``AWS::CodePipeline::CustomActionType.InputArtifactDetails``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-inputartifactdetails
    Stability:
        stable
    """

    outputArtifactDetails: typing.Union["CfnCustomActionType.ArtifactDetailsProperty", aws_cdk.core.IResolvable]
    """``AWS::CodePipeline::CustomActionType.OutputArtifactDetails``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-outputartifactdetails
    Stability:
        stable
    """

    provider: str
    """``AWS::CodePipeline::CustomActionType.Provider``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-provider
    Stability:
        stable
    """

    version: str
    """``AWS::CodePipeline::CustomActionType.Version``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-version
    Stability:
        stable
    """

class CfnPipeline(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codepipeline.CfnPipeline"):
    """A CloudFormation ``AWS::CodePipeline::Pipeline``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html
    Stability:
        stable
    cloudformationResource:
        AWS::CodePipeline::Pipeline
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, role_arn: str, stages: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "StageDeclarationProperty"]]], artifact_store: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ArtifactStoreProperty"]]]=None, artifact_stores: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ArtifactStoreMapProperty"]]]]]=None, disable_inbound_stage_transitions: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "StageTransitionProperty"]]]]]=None, name: typing.Optional[str]=None, restart_execution_on_update: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None) -> None:
        """Create a new ``AWS::CodePipeline::Pipeline``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            role_arn: ``AWS::CodePipeline::Pipeline.RoleArn``.
            stages: ``AWS::CodePipeline::Pipeline.Stages``.
            artifact_store: ``AWS::CodePipeline::Pipeline.ArtifactStore``.
            artifact_stores: ``AWS::CodePipeline::Pipeline.ArtifactStores``.
            disable_inbound_stage_transitions: ``AWS::CodePipeline::Pipeline.DisableInboundStageTransitions``.
            name: ``AWS::CodePipeline::Pipeline.Name``.
            restart_execution_on_update: ``AWS::CodePipeline::Pipeline.RestartExecutionOnUpdate``.

        Stability:
            experimental
        """
        props: CfnPipelineProps = {"roleArn": role_arn, "stages": stages}

        if artifact_store is not None:
            props["artifactStore"] = artifact_store

        if artifact_stores is not None:
            props["artifactStores"] = artifact_stores

        if disable_inbound_stage_transitions is not None:
            props["disableInboundStageTransitions"] = disable_inbound_stage_transitions

        if name is not None:
            props["name"] = name

        if restart_execution_on_update is not None:
            props["restartExecutionOnUpdate"] = restart_execution_on_update

        jsii.create(CfnPipeline, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrVersion")
    def attr_version(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Version
        """
        return jsii.get(self, "attrVersion")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> str:
        """``AWS::CodePipeline::Pipeline.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-rolearn
        Stability:
            stable
        """
        return jsii.get(self, "roleArn")

    @role_arn.setter
    def role_arn(self, value: str):
        return jsii.set(self, "roleArn", value)

    @property
    @jsii.member(jsii_name="stages")
    def stages(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "StageDeclarationProperty"]]]:
        """``AWS::CodePipeline::Pipeline.Stages``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-stages
        Stability:
            stable
        """
        return jsii.get(self, "stages")

    @stages.setter
    def stages(self, value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "StageDeclarationProperty"]]]):
        return jsii.set(self, "stages", value)

    @property
    @jsii.member(jsii_name="artifactStore")
    def artifact_store(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ArtifactStoreProperty"]]]:
        """``AWS::CodePipeline::Pipeline.ArtifactStore``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-artifactstore
        Stability:
            stable
        """
        return jsii.get(self, "artifactStore")

    @artifact_store.setter
    def artifact_store(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ArtifactStoreProperty"]]]):
        return jsii.set(self, "artifactStore", value)

    @property
    @jsii.member(jsii_name="artifactStores")
    def artifact_stores(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ArtifactStoreMapProperty"]]]]]:
        """``AWS::CodePipeline::Pipeline.ArtifactStores``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-artifactstores
        Stability:
            stable
        """
        return jsii.get(self, "artifactStores")

    @artifact_stores.setter
    def artifact_stores(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ArtifactStoreMapProperty"]]]]]):
        return jsii.set(self, "artifactStores", value)

    @property
    @jsii.member(jsii_name="disableInboundStageTransitions")
    def disable_inbound_stage_transitions(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "StageTransitionProperty"]]]]]:
        """``AWS::CodePipeline::Pipeline.DisableInboundStageTransitions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-disableinboundstagetransitions
        Stability:
            stable
        """
        return jsii.get(self, "disableInboundStageTransitions")

    @disable_inbound_stage_transitions.setter
    def disable_inbound_stage_transitions(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "StageTransitionProperty"]]]]]):
        return jsii.set(self, "disableInboundStageTransitions", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::CodePipeline::Pipeline.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="restartExecutionOnUpdate")
    def restart_execution_on_update(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::CodePipeline::Pipeline.RestartExecutionOnUpdate``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-restartexecutiononupdate
        Stability:
            stable
        """
        return jsii.get(self, "restartExecutionOnUpdate")

    @restart_execution_on_update.setter
    def restart_execution_on_update(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "restartExecutionOnUpdate", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ActionDeclarationProperty(jsii.compat.TypedDict, total=False):
        configuration: typing.Any
        """``CfnPipeline.ActionDeclarationProperty.Configuration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html#cfn-codepipeline-pipeline-stages-actions-configuration
        Stability:
            stable
        """
        inputArtifacts: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnPipeline.InputArtifactProperty"]]]
        """``CfnPipeline.ActionDeclarationProperty.InputArtifacts``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html#cfn-codepipeline-pipeline-stages-actions-inputartifacts
        Stability:
            stable
        """
        outputArtifacts: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnPipeline.OutputArtifactProperty"]]]
        """``CfnPipeline.ActionDeclarationProperty.OutputArtifacts``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html#cfn-codepipeline-pipeline-stages-actions-outputartifacts
        Stability:
            stable
        """
        region: str
        """``CfnPipeline.ActionDeclarationProperty.Region``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html#cfn-codepipeline-pipeline-stages-actions-region
        Stability:
            stable
        """
        roleArn: str
        """``CfnPipeline.ActionDeclarationProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html#cfn-codepipeline-pipeline-stages-actions-rolearn
        Stability:
            stable
        """
        runOrder: jsii.Number
        """``CfnPipeline.ActionDeclarationProperty.RunOrder``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html#cfn-codepipeline-pipeline-stages-actions-runorder
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CfnPipeline.ActionDeclarationProperty", jsii_struct_bases=[_ActionDeclarationProperty])
    class ActionDeclarationProperty(_ActionDeclarationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html
        Stability:
            stable
        """
        actionTypeId: typing.Union[aws_cdk.core.IResolvable, "CfnPipeline.ActionTypeIdProperty"]
        """``CfnPipeline.ActionDeclarationProperty.ActionTypeId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html#cfn-codepipeline-pipeline-stages-actions-actiontypeid
        Stability:
            stable
        """

        name: str
        """``CfnPipeline.ActionDeclarationProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html#cfn-codepipeline-pipeline-stages-actions-name
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CfnPipeline.ActionTypeIdProperty", jsii_struct_bases=[])
    class ActionTypeIdProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions-actiontypeid.html
        Stability:
            stable
        """
        category: str
        """``CfnPipeline.ActionTypeIdProperty.Category``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions-actiontypeid.html#cfn-codepipeline-pipeline-stages-actions-actiontypeid-category
        Stability:
            stable
        """

        owner: str
        """``CfnPipeline.ActionTypeIdProperty.Owner``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions-actiontypeid.html#cfn-codepipeline-pipeline-stages-actions-actiontypeid-owner
        Stability:
            stable
        """

        provider: str
        """``CfnPipeline.ActionTypeIdProperty.Provider``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions-actiontypeid.html#cfn-codepipeline-pipeline-stages-actions-actiontypeid-provider
        Stability:
            stable
        """

        version: str
        """``CfnPipeline.ActionTypeIdProperty.Version``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions-actiontypeid.html#cfn-codepipeline-pipeline-stages-actions-actiontypeid-version
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CfnPipeline.ArtifactStoreMapProperty", jsii_struct_bases=[])
    class ArtifactStoreMapProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstoremap.html
        Stability:
            stable
        """
        artifactStore: typing.Union[aws_cdk.core.IResolvable, "CfnPipeline.ArtifactStoreProperty"]
        """``CfnPipeline.ArtifactStoreMapProperty.ArtifactStore``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstoremap.html#cfn-codepipeline-pipeline-artifactstoremap-artifactstore
        Stability:
            stable
        """

        region: str
        """``CfnPipeline.ArtifactStoreMapProperty.Region``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstoremap.html#cfn-codepipeline-pipeline-artifactstoremap-region
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ArtifactStoreProperty(jsii.compat.TypedDict, total=False):
        encryptionKey: typing.Union[aws_cdk.core.IResolvable, "CfnPipeline.EncryptionKeyProperty"]
        """``CfnPipeline.ArtifactStoreProperty.EncryptionKey``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstore.html#cfn-codepipeline-pipeline-artifactstore-encryptionkey
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CfnPipeline.ArtifactStoreProperty", jsii_struct_bases=[_ArtifactStoreProperty])
    class ArtifactStoreProperty(_ArtifactStoreProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstore.html
        Stability:
            stable
        """
        location: str
        """``CfnPipeline.ArtifactStoreProperty.Location``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstore.html#cfn-codepipeline-pipeline-artifactstore-location
        Stability:
            stable
        """

        type: str
        """``CfnPipeline.ArtifactStoreProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstore.html#cfn-codepipeline-pipeline-artifactstore-type
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CfnPipeline.BlockerDeclarationProperty", jsii_struct_bases=[])
    class BlockerDeclarationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-blockers.html
        Stability:
            stable
        """
        name: str
        """``CfnPipeline.BlockerDeclarationProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-blockers.html#cfn-codepipeline-pipeline-stages-blockers-name
        Stability:
            stable
        """

        type: str
        """``CfnPipeline.BlockerDeclarationProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-blockers.html#cfn-codepipeline-pipeline-stages-blockers-type
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CfnPipeline.EncryptionKeyProperty", jsii_struct_bases=[])
    class EncryptionKeyProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstore-encryptionkey.html
        Stability:
            stable
        """
        id: str
        """``CfnPipeline.EncryptionKeyProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstore-encryptionkey.html#cfn-codepipeline-pipeline-artifactstore-encryptionkey-id
        Stability:
            stable
        """

        type: str
        """``CfnPipeline.EncryptionKeyProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstore-encryptionkey.html#cfn-codepipeline-pipeline-artifactstore-encryptionkey-type
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CfnPipeline.InputArtifactProperty", jsii_struct_bases=[])
    class InputArtifactProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions-inputartifacts.html
        Stability:
            stable
        """
        name: str
        """``CfnPipeline.InputArtifactProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions-inputartifacts.html#cfn-codepipeline-pipeline-stages-actions-inputartifacts-name
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CfnPipeline.OutputArtifactProperty", jsii_struct_bases=[])
    class OutputArtifactProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions-outputartifacts.html
        Stability:
            stable
        """
        name: str
        """``CfnPipeline.OutputArtifactProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions-outputartifacts.html#cfn-codepipeline-pipeline-stages-actions-outputartifacts-name
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _StageDeclarationProperty(jsii.compat.TypedDict, total=False):
        blockers: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnPipeline.BlockerDeclarationProperty"]]]
        """``CfnPipeline.StageDeclarationProperty.Blockers``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages.html#cfn-codepipeline-pipeline-stages-blockers
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CfnPipeline.StageDeclarationProperty", jsii_struct_bases=[_StageDeclarationProperty])
    class StageDeclarationProperty(_StageDeclarationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages.html
        Stability:
            stable
        """
        actions: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnPipeline.ActionDeclarationProperty"]]]
        """``CfnPipeline.StageDeclarationProperty.Actions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages.html#cfn-codepipeline-pipeline-stages-actions
        Stability:
            stable
        """

        name: str
        """``CfnPipeline.StageDeclarationProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages.html#cfn-codepipeline-pipeline-stages-name
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CfnPipeline.StageTransitionProperty", jsii_struct_bases=[])
    class StageTransitionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-disableinboundstagetransitions.html
        Stability:
            stable
        """
        reason: str
        """``CfnPipeline.StageTransitionProperty.Reason``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-disableinboundstagetransitions.html#cfn-codepipeline-pipeline-disableinboundstagetransitions-reason
        Stability:
            stable
        """

        stageName: str
        """``CfnPipeline.StageTransitionProperty.StageName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-disableinboundstagetransitions.html#cfn-codepipeline-pipeline-disableinboundstagetransitions-stagename
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnPipelineProps(jsii.compat.TypedDict, total=False):
    artifactStore: typing.Union[aws_cdk.core.IResolvable, "CfnPipeline.ArtifactStoreProperty"]
    """``AWS::CodePipeline::Pipeline.ArtifactStore``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-artifactstore
    Stability:
        stable
    """
    artifactStores: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnPipeline.ArtifactStoreMapProperty"]]]
    """``AWS::CodePipeline::Pipeline.ArtifactStores``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-artifactstores
    Stability:
        stable
    """
    disableInboundStageTransitions: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnPipeline.StageTransitionProperty"]]]
    """``AWS::CodePipeline::Pipeline.DisableInboundStageTransitions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-disableinboundstagetransitions
    Stability:
        stable
    """
    name: str
    """``AWS::CodePipeline::Pipeline.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-name
    Stability:
        stable
    """
    restartExecutionOnUpdate: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::CodePipeline::Pipeline.RestartExecutionOnUpdate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-restartexecutiononupdate
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CfnPipelineProps", jsii_struct_bases=[_CfnPipelineProps])
class CfnPipelineProps(_CfnPipelineProps):
    """Properties for defining a ``AWS::CodePipeline::Pipeline``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html
    Stability:
        stable
    """
    roleArn: str
    """``AWS::CodePipeline::Pipeline.RoleArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-rolearn
    Stability:
        stable
    """

    stages: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnPipeline.StageDeclarationProperty"]]]
    """``AWS::CodePipeline::Pipeline.Stages``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-stages
    Stability:
        stable
    """

class CfnWebhook(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codepipeline.CfnWebhook"):
    """A CloudFormation ``AWS::CodePipeline::Webhook``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html
    Stability:
        stable
    cloudformationResource:
        AWS::CodePipeline::Webhook
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, authentication: str, authentication_configuration: typing.Union[aws_cdk.core.IResolvable, "WebhookAuthConfigurationProperty"], filters: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "WebhookFilterRuleProperty"]]], target_action: str, target_pipeline: str, target_pipeline_version: jsii.Number, name: typing.Optional[str]=None, register_with_third_party: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None) -> None:
        """Create a new ``AWS::CodePipeline::Webhook``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            authentication: ``AWS::CodePipeline::Webhook.Authentication``.
            authentication_configuration: ``AWS::CodePipeline::Webhook.AuthenticationConfiguration``.
            filters: ``AWS::CodePipeline::Webhook.Filters``.
            target_action: ``AWS::CodePipeline::Webhook.TargetAction``.
            target_pipeline: ``AWS::CodePipeline::Webhook.TargetPipeline``.
            target_pipeline_version: ``AWS::CodePipeline::Webhook.TargetPipelineVersion``.
            name: ``AWS::CodePipeline::Webhook.Name``.
            register_with_third_party: ``AWS::CodePipeline::Webhook.RegisterWithThirdParty``.

        Stability:
            experimental
        """
        props: CfnWebhookProps = {"authentication": authentication, "authenticationConfiguration": authentication_configuration, "filters": filters, "targetAction": target_action, "targetPipeline": target_pipeline, "targetPipelineVersion": target_pipeline_version}

        if name is not None:
            props["name"] = name

        if register_with_third_party is not None:
            props["registerWithThirdParty"] = register_with_third_party

        jsii.create(CfnWebhook, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrUrl")
    def attr_url(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Url
        """
        return jsii.get(self, "attrUrl")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="authentication")
    def authentication(self) -> str:
        """``AWS::CodePipeline::Webhook.Authentication``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-authentication
        Stability:
            stable
        """
        return jsii.get(self, "authentication")

    @authentication.setter
    def authentication(self, value: str):
        return jsii.set(self, "authentication", value)

    @property
    @jsii.member(jsii_name="authenticationConfiguration")
    def authentication_configuration(self) -> typing.Union[aws_cdk.core.IResolvable, "WebhookAuthConfigurationProperty"]:
        """``AWS::CodePipeline::Webhook.AuthenticationConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-authenticationconfiguration
        Stability:
            stable
        """
        return jsii.get(self, "authenticationConfiguration")

    @authentication_configuration.setter
    def authentication_configuration(self, value: typing.Union[aws_cdk.core.IResolvable, "WebhookAuthConfigurationProperty"]):
        return jsii.set(self, "authenticationConfiguration", value)

    @property
    @jsii.member(jsii_name="filters")
    def filters(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "WebhookFilterRuleProperty"]]]:
        """``AWS::CodePipeline::Webhook.Filters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-filters
        Stability:
            stable
        """
        return jsii.get(self, "filters")

    @filters.setter
    def filters(self, value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "WebhookFilterRuleProperty"]]]):
        return jsii.set(self, "filters", value)

    @property
    @jsii.member(jsii_name="targetAction")
    def target_action(self) -> str:
        """``AWS::CodePipeline::Webhook.TargetAction``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-targetaction
        Stability:
            stable
        """
        return jsii.get(self, "targetAction")

    @target_action.setter
    def target_action(self, value: str):
        return jsii.set(self, "targetAction", value)

    @property
    @jsii.member(jsii_name="targetPipeline")
    def target_pipeline(self) -> str:
        """``AWS::CodePipeline::Webhook.TargetPipeline``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-targetpipeline
        Stability:
            stable
        """
        return jsii.get(self, "targetPipeline")

    @target_pipeline.setter
    def target_pipeline(self, value: str):
        return jsii.set(self, "targetPipeline", value)

    @property
    @jsii.member(jsii_name="targetPipelineVersion")
    def target_pipeline_version(self) -> jsii.Number:
        """``AWS::CodePipeline::Webhook.TargetPipelineVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-targetpipelineversion
        Stability:
            stable
        """
        return jsii.get(self, "targetPipelineVersion")

    @target_pipeline_version.setter
    def target_pipeline_version(self, value: jsii.Number):
        return jsii.set(self, "targetPipelineVersion", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::CodePipeline::Webhook.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="registerWithThirdParty")
    def register_with_third_party(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::CodePipeline::Webhook.RegisterWithThirdParty``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-registerwiththirdparty
        Stability:
            stable
        """
        return jsii.get(self, "registerWithThirdParty")

    @register_with_third_party.setter
    def register_with_third_party(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "registerWithThirdParty", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CfnWebhook.WebhookAuthConfigurationProperty", jsii_struct_bases=[])
    class WebhookAuthConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-webhook-webhookauthconfiguration.html
        Stability:
            stable
        """
        allowedIpRange: str
        """``CfnWebhook.WebhookAuthConfigurationProperty.AllowedIPRange``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-webhook-webhookauthconfiguration.html#cfn-codepipeline-webhook-webhookauthconfiguration-allowediprange
        Stability:
            stable
        """

        secretToken: str
        """``CfnWebhook.WebhookAuthConfigurationProperty.SecretToken``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-webhook-webhookauthconfiguration.html#cfn-codepipeline-webhook-webhookauthconfiguration-secrettoken
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _WebhookFilterRuleProperty(jsii.compat.TypedDict, total=False):
        matchEquals: str
        """``CfnWebhook.WebhookFilterRuleProperty.MatchEquals``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-webhook-webhookfilterrule.html#cfn-codepipeline-webhook-webhookfilterrule-matchequals
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CfnWebhook.WebhookFilterRuleProperty", jsii_struct_bases=[_WebhookFilterRuleProperty])
    class WebhookFilterRuleProperty(_WebhookFilterRuleProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-webhook-webhookfilterrule.html
        Stability:
            stable
        """
        jsonPath: str
        """``CfnWebhook.WebhookFilterRuleProperty.JsonPath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-webhook-webhookfilterrule.html#cfn-codepipeline-webhook-webhookfilterrule-jsonpath
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnWebhookProps(jsii.compat.TypedDict, total=False):
    name: str
    """``AWS::CodePipeline::Webhook.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-name
    Stability:
        stable
    """
    registerWithThirdParty: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::CodePipeline::Webhook.RegisterWithThirdParty``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-registerwiththirdparty
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CfnWebhookProps", jsii_struct_bases=[_CfnWebhookProps])
class CfnWebhookProps(_CfnWebhookProps):
    """Properties for defining a ``AWS::CodePipeline::Webhook``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html
    Stability:
        stable
    """
    authentication: str
    """``AWS::CodePipeline::Webhook.Authentication``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-authentication
    Stability:
        stable
    """

    authenticationConfiguration: typing.Union[aws_cdk.core.IResolvable, "CfnWebhook.WebhookAuthConfigurationProperty"]
    """``AWS::CodePipeline::Webhook.AuthenticationConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-authenticationconfiguration
    Stability:
        stable
    """

    filters: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnWebhook.WebhookFilterRuleProperty"]]]
    """``AWS::CodePipeline::Webhook.Filters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-filters
    Stability:
        stable
    """

    targetAction: str
    """``AWS::CodePipeline::Webhook.TargetAction``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-targetaction
    Stability:
        stable
    """

    targetPipeline: str
    """``AWS::CodePipeline::Webhook.TargetPipeline``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-targetpipeline
    Stability:
        stable
    """

    targetPipelineVersion: jsii.Number
    """``AWS::CodePipeline::Webhook.TargetPipelineVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-targetpipelineversion
    Stability:
        stable
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CommonActionProps(jsii.compat.TypedDict, total=False):
    runOrder: jsii.Number
    """The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute.

    Default:
        1

    See:
        https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CommonActionProps", jsii_struct_bases=[_CommonActionProps])
class CommonActionProps(_CommonActionProps):
    """Common properties shared by all Actions.

    Stability:
        experimental
    """
    actionName: str
    """The physical, human-readable name of the Action. Not that Action names must be unique within a single Stage.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CrossRegionSupport", jsii_struct_bases=[])
class CrossRegionSupport(jsii.compat.TypedDict):
    """An interface representing resources generated in order to support the cross-region capabilities of CodePipeline. You get instances of this interface from the {@link Pipeline#crossRegionSupport} property.

    Stability:
        experimental
    """
    replicationBucket: aws_cdk.aws_s3.IBucket
    """The replication Bucket used by CodePipeline to operate in this region. Belongs to {@link stack}.

    Stability:
        experimental
    """

    stack: aws_cdk.core.Stack
    """The Stack that has been created to house the replication Bucket required for this  region.

    Stability:
        experimental
    """

@jsii.interface(jsii_type="@aws-cdk/aws-codepipeline.IAction")
class IAction(jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IActionProxy

    @property
    @jsii.member(jsii_name="actionProperties")
    def action_properties(self) -> "ActionProperties":
        """
        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="bind")
    def bind(self, scope: aws_cdk.core.Construct, stage: "IStage", *, role: aws_cdk.aws_iam.IRole) -> "ActionConfig":
        """
        Arguments:
            scope: -
            stage: -
            options: -
            role: 

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(self, name: str, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None, *, description: typing.Optional[str]=None, enabled: typing.Optional[bool]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, schedule: typing.Optional[aws_cdk.aws_events.Schedule]=None, targets: typing.Optional[typing.List[aws_cdk.aws_events.IRuleTarget]]=None) -> aws_cdk.aws_events.Rule:
        """
        Arguments:
            name: -
            target: -
            options: -
            description: A description of the rule's purpose. Default: - No description.
            enabled: Indicates whether the rule is enabled. Default: true
            event_pattern: Describes which events CloudWatch Events routes to the specified target. These routed events are matched events. For more information, see Events and Event Patterns in the Amazon CloudWatch User Guide. Default: - None.
            rule_name: A name for the rule. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the rule name. For more information, see Name Type.
            schedule: The schedule or rate (frequency) that determines when CloudWatch Events runs the rule. For more information, see Schedule Expression Syntax for Rules in the Amazon CloudWatch User Guide. Default: - None.
            targets: Targets to invoke when this rule matches an event. Input will be the full matched event. If you wish to specify custom target input, use ``addTarget(target[, inputOptions])``. Default: - No targets.

        Stability:
            experimental
        """
        ...


class _IActionProxy():
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-codepipeline.IAction"
    @property
    @jsii.member(jsii_name="actionProperties")
    def action_properties(self) -> "ActionProperties":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "actionProperties")

    @jsii.member(jsii_name="bind")
    def bind(self, scope: aws_cdk.core.Construct, stage: "IStage", *, role: aws_cdk.aws_iam.IRole) -> "ActionConfig":
        """
        Arguments:
            scope: -
            stage: -
            options: -
            role: 

        Stability:
            experimental
        """
        options: ActionBindOptions = {"role": role}

        return jsii.invoke(self, "bind", [scope, stage, options])

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(self, name: str, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None, *, description: typing.Optional[str]=None, enabled: typing.Optional[bool]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, schedule: typing.Optional[aws_cdk.aws_events.Schedule]=None, targets: typing.Optional[typing.List[aws_cdk.aws_events.IRuleTarget]]=None) -> aws_cdk.aws_events.Rule:
        """
        Arguments:
            name: -
            target: -
            options: -
            description: A description of the rule's purpose. Default: - No description.
            enabled: Indicates whether the rule is enabled. Default: true
            event_pattern: Describes which events CloudWatch Events routes to the specified target. These routed events are matched events. For more information, see Events and Event Patterns in the Amazon CloudWatch User Guide. Default: - None.
            rule_name: A name for the rule. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the rule name. For more information, see Name Type.
            schedule: The schedule or rate (frequency) that determines when CloudWatch Events runs the rule. For more information, see Schedule Expression Syntax for Rules in the Amazon CloudWatch User Guide. Default: - None.
            targets: Targets to invoke when this rule matches an event. Input will be the full matched event. If you wish to specify custom target input, use ``addTarget(target[, inputOptions])``. Default: - No targets.

        Stability:
            experimental
        """
        options: aws_cdk.aws_events.RuleProps = {}

        if description is not None:
            options["description"] = description

        if enabled is not None:
            options["enabled"] = enabled

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        if schedule is not None:
            options["schedule"] = schedule

        if targets is not None:
            options["targets"] = targets

        return jsii.invoke(self, "onStateChange", [name, target, options])


@jsii.interface(jsii_type="@aws-cdk/aws-codepipeline.IPipeline")
class IPipeline(aws_cdk.core.IResource, jsii.compat.Protocol):
    """The abstract view of an AWS CodePipeline as required and used by Actions. It extends {@link events.IRuleTarget}, so this interface can be used as a Target for CloudWatch Events.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IPipelineProxy

    @property
    @jsii.member(jsii_name="artifactBucket")
    def artifact_bucket(self) -> aws_cdk.aws_s3.IBucket:
        """
        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="pipelineArn")
    def pipeline_arn(self) -> str:
        """The ARN of the Pipeline.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="pipelineName")
    def pipeline_name(self) -> str:
        """The name of the Pipeline.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @jsii.member(jsii_name="onEvent")
    def on_event(self, id: str, *, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None) -> aws_cdk.aws_events.Rule:
        """Define an event rule triggered by this CodePipeline.

        Arguments:
            id: Identifier for this event handler.
            options: Additional options to pass to the event rule.
            description: A description of the rule's purpose. Default: - No description
            event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
            rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
            target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(self, id: str, *, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None) -> aws_cdk.aws_events.Rule:
        """Define an event rule triggered by the "CodePipeline Pipeline Execution State Change" event emitted from this pipeline.

        Arguments:
            id: Identifier for this event handler.
            options: Additional options to pass to the event rule.
            description: A description of the rule's purpose. Default: - No description
            event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
            rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
            target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        Stability:
            experimental
        """
        ...


class _IPipelineProxy(jsii.proxy_for(aws_cdk.core.IResource)):
    """The abstract view of an AWS CodePipeline as required and used by Actions. It extends {@link events.IRuleTarget}, so this interface can be used as a Target for CloudWatch Events.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-codepipeline.IPipeline"
    @property
    @jsii.member(jsii_name="artifactBucket")
    def artifact_bucket(self) -> aws_cdk.aws_s3.IBucket:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "artifactBucket")

    @property
    @jsii.member(jsii_name="pipelineArn")
    def pipeline_arn(self) -> str:
        """The ARN of the Pipeline.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "pipelineArn")

    @property
    @jsii.member(jsii_name="pipelineName")
    def pipeline_name(self) -> str:
        """The name of the Pipeline.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "pipelineName")

    @jsii.member(jsii_name="onEvent")
    def on_event(self, id: str, *, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None) -> aws_cdk.aws_events.Rule:
        """Define an event rule triggered by this CodePipeline.

        Arguments:
            id: Identifier for this event handler.
            options: Additional options to pass to the event rule.
            description: A description of the rule's purpose. Default: - No description
            event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
            rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
            target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        Stability:
            experimental
        """
        options: aws_cdk.aws_events.OnEventOptions = {}

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        if target is not None:
            options["target"] = target

        return jsii.invoke(self, "onEvent", [id, options])

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(self, id: str, *, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None) -> aws_cdk.aws_events.Rule:
        """Define an event rule triggered by the "CodePipeline Pipeline Execution State Change" event emitted from this pipeline.

        Arguments:
            id: Identifier for this event handler.
            options: Additional options to pass to the event rule.
            description: A description of the rule's purpose. Default: - No description
            event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
            rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
            target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        Stability:
            experimental
        """
        options: aws_cdk.aws_events.OnEventOptions = {}

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        if target is not None:
            options["target"] = target

        return jsii.invoke(self, "onStateChange", [id, options])


@jsii.interface(jsii_type="@aws-cdk/aws-codepipeline.IStage")
class IStage(jsii.compat.Protocol):
    """The abstract interface of a Pipeline Stage that is used by Actions.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IStageProxy

    @property
    @jsii.member(jsii_name="pipeline")
    def pipeline(self) -> "IPipeline":
        """
        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="stageName")
    def stage_name(self) -> str:
        """The physical, human-readable name of this Pipeline Stage.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="addAction")
    def add_action(self, action: "IAction") -> None:
        """
        Arguments:
            action: -

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(self, name: str, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None, *, description: typing.Optional[str]=None, enabled: typing.Optional[bool]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, schedule: typing.Optional[aws_cdk.aws_events.Schedule]=None, targets: typing.Optional[typing.List[aws_cdk.aws_events.IRuleTarget]]=None) -> aws_cdk.aws_events.Rule:
        """
        Arguments:
            name: -
            target: -
            options: -
            description: A description of the rule's purpose. Default: - No description.
            enabled: Indicates whether the rule is enabled. Default: true
            event_pattern: Describes which events CloudWatch Events routes to the specified target. These routed events are matched events. For more information, see Events and Event Patterns in the Amazon CloudWatch User Guide. Default: - None.
            rule_name: A name for the rule. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the rule name. For more information, see Name Type.
            schedule: The schedule or rate (frequency) that determines when CloudWatch Events runs the rule. For more information, see Schedule Expression Syntax for Rules in the Amazon CloudWatch User Guide. Default: - None.
            targets: Targets to invoke when this rule matches an event. Input will be the full matched event. If you wish to specify custom target input, use ``addTarget(target[, inputOptions])``. Default: - No targets.

        Stability:
            experimental
        """
        ...


class _IStageProxy():
    """The abstract interface of a Pipeline Stage that is used by Actions.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-codepipeline.IStage"
    @property
    @jsii.member(jsii_name="pipeline")
    def pipeline(self) -> "IPipeline":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "pipeline")

    @property
    @jsii.member(jsii_name="stageName")
    def stage_name(self) -> str:
        """The physical, human-readable name of this Pipeline Stage.

        Stability:
            experimental
        """
        return jsii.get(self, "stageName")

    @jsii.member(jsii_name="addAction")
    def add_action(self, action: "IAction") -> None:
        """
        Arguments:
            action: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addAction", [action])

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(self, name: str, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None, *, description: typing.Optional[str]=None, enabled: typing.Optional[bool]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, schedule: typing.Optional[aws_cdk.aws_events.Schedule]=None, targets: typing.Optional[typing.List[aws_cdk.aws_events.IRuleTarget]]=None) -> aws_cdk.aws_events.Rule:
        """
        Arguments:
            name: -
            target: -
            options: -
            description: A description of the rule's purpose. Default: - No description.
            enabled: Indicates whether the rule is enabled. Default: true
            event_pattern: Describes which events CloudWatch Events routes to the specified target. These routed events are matched events. For more information, see Events and Event Patterns in the Amazon CloudWatch User Guide. Default: - None.
            rule_name: A name for the rule. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the rule name. For more information, see Name Type.
            schedule: The schedule or rate (frequency) that determines when CloudWatch Events runs the rule. For more information, see Schedule Expression Syntax for Rules in the Amazon CloudWatch User Guide. Default: - None.
            targets: Targets to invoke when this rule matches an event. Input will be the full matched event. If you wish to specify custom target input, use ``addTarget(target[, inputOptions])``. Default: - No targets.

        Stability:
            experimental
        """
        options: aws_cdk.aws_events.RuleProps = {}

        if description is not None:
            options["description"] = description

        if enabled is not None:
            options["enabled"] = enabled

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        if schedule is not None:
            options["schedule"] = schedule

        if targets is not None:
            options["targets"] = targets

        return jsii.invoke(self, "onStateChange", [name, target, options])


@jsii.implements(IPipeline)
class Pipeline(aws_cdk.core.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codepipeline.Pipeline"):
    """An AWS CodePipeline pipeline with its associated IAM role and S3 bucket.

    Stability:
        experimental

    Example::
        // create a pipeline
        const pipeline = new Pipeline(this, 'Pipeline');
        
        // add a stage
        const sourceStage = pipeline.addStage({ name: 'Source' });
        
        // add a source action to the stage
        sourceStage.addAction(new codepipeline_actions.CodeCommitSourceAction({
          actionName: 'Source',
          outputArtifactName: 'SourceArtifact',
          repository: repo,
        }));
        
        // ... add more stages
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, artifact_bucket: typing.Optional[aws_cdk.aws_s3.IBucket]=None, cross_region_replication_buckets: typing.Optional[typing.Mapping[str,aws_cdk.aws_s3.IBucket]]=None, pipeline_name: typing.Optional[str]=None, restart_execution_on_update: typing.Optional[bool]=None, role: typing.Optional[aws_cdk.aws_iam.IRole]=None, stages: typing.Optional[typing.List["StageProps"]]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            artifact_bucket: The S3 bucket used by this Pipeline to store artifacts. Default: - A new S3 bucket will be created.
            cross_region_replication_buckets: A map of region to S3 bucket name used for cross-region CodePipeline. For every Action that you specify targeting a different region than the Pipeline itself, if you don't provide an explicit Bucket for that region using this property, the construct will automatically create a Stack containing an S3 Bucket in that region. Default: - None.
            pipeline_name: Name of the pipeline. Default: - AWS CloudFormation generates an ID and uses that for the pipeline name.
            restart_execution_on_update: Indicates whether to rerun the AWS CodePipeline pipeline after you update it. Default: false
            role: The IAM role to be assumed by this Pipeline. Default: a new IAM role will be created.
            stages: The list of Stages, in order, to create this Pipeline with. You can always add more Stages later by calling {@link Pipeline#addStage}. Default: - None.

        Stability:
            experimental
        """
        props: PipelineProps = {}

        if artifact_bucket is not None:
            props["artifactBucket"] = artifact_bucket

        if cross_region_replication_buckets is not None:
            props["crossRegionReplicationBuckets"] = cross_region_replication_buckets

        if pipeline_name is not None:
            props["pipelineName"] = pipeline_name

        if restart_execution_on_update is not None:
            props["restartExecutionOnUpdate"] = restart_execution_on_update

        if role is not None:
            props["role"] = role

        if stages is not None:
            props["stages"] = stages

        jsii.create(Pipeline, self, [scope, id, props])

    @jsii.member(jsii_name="addStage")
    def add_stage(self, *, placement: typing.Optional["StagePlacement"]=None, stage_name: str, actions: typing.Optional[typing.List["IAction"]]=None) -> "IStage":
        """Creates a new Stage, and adds it to this Pipeline.

        Arguments:
            props: the creation properties of the new Stage.
            placement: 
            stage_name: The physical, human-readable name to assign to this Pipeline Stage.
            actions: The list of Actions to create this Stage with. You can always add more Actions later by calling {@link IStage#addAction}.

        Returns:
            the newly created Stage

        Stability:
            experimental
        """
        props: StageOptions = {"stageName": stage_name}

        if placement is not None:
            props["placement"] = placement

        if actions is not None:
            props["actions"] = actions

        return jsii.invoke(self, "addStage", [props])

    @jsii.member(jsii_name="addToRolePolicy")
    def add_to_role_policy(self, statement: aws_cdk.aws_iam.PolicyStatement) -> None:
        """Adds a statement to the pipeline role.

        Arguments:
            statement: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addToRolePolicy", [statement])

    @jsii.member(jsii_name="onEvent")
    def on_event(self, id: str, *, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None) -> aws_cdk.aws_events.Rule:
        """Defines an event rule triggered by this CodePipeline.

        Arguments:
            id: Identifier for this event handler.
            options: Additional options to pass to the event rule.
            description: A description of the rule's purpose. Default: - No description
            event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
            rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
            target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        Stability:
            experimental
        """
        options: aws_cdk.aws_events.OnEventOptions = {}

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        if target is not None:
            options["target"] = target

        return jsii.invoke(self, "onEvent", [id, options])

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(self, id: str, *, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None) -> aws_cdk.aws_events.Rule:
        """Defines an event rule triggered by the "CodePipeline Pipeline Execution State Change" event emitted from this pipeline.

        Arguments:
            id: Identifier for this event handler.
            options: Additional options to pass to the event rule.
            description: A description of the rule's purpose. Default: - No description
            event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
            rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
            target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        Stability:
            experimental
        """
        options: aws_cdk.aws_events.OnEventOptions = {}

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        if target is not None:
            options["target"] = target

        return jsii.invoke(self, "onStateChange", [id, options])

    @jsii.member(jsii_name="validate")
    def _validate(self) -> typing.List[str]:
        """Validate the pipeline structure.

        Validation happens according to the rules documented at

        https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html#pipeline-requirements

        Stability:
            experimental
        override:
            true
        """
        return jsii.invoke(self, "validate", [])

    @property
    @jsii.member(jsii_name="artifactBucket")
    def artifact_bucket(self) -> aws_cdk.aws_s3.IBucket:
        """Bucket used to store output artifacts.

        Stability:
            experimental
        """
        return jsii.get(self, "artifactBucket")

    @property
    @jsii.member(jsii_name="crossRegionSupport")
    def cross_region_support(self) -> typing.Mapping[str,"CrossRegionSupport"]:
        """Returns all of the {@link CrossRegionSupportStack}s that were generated automatically when dealing with Actions that reside in a different region than the Pipeline itself.

        Stability:
            experimental
        """
        return jsii.get(self, "crossRegionSupport")

    @property
    @jsii.member(jsii_name="pipelineArn")
    def pipeline_arn(self) -> str:
        """ARN of this pipeline.

        Stability:
            experimental
        """
        return jsii.get(self, "pipelineArn")

    @property
    @jsii.member(jsii_name="pipelineName")
    def pipeline_name(self) -> str:
        """The name of the pipeline.

        Stability:
            experimental
        """
        return jsii.get(self, "pipelineName")

    @property
    @jsii.member(jsii_name="pipelineVersion")
    def pipeline_version(self) -> str:
        """The version of the pipeline.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "pipelineVersion")

    @property
    @jsii.member(jsii_name="role")
    def role(self) -> aws_cdk.aws_iam.IRole:
        """The IAM role AWS CodePipeline will use to perform actions or assume roles for actions with a more specific IAM role.

        Stability:
            experimental
        """
        return jsii.get(self, "role")

    @property
    @jsii.member(jsii_name="stageCount")
    def stage_count(self) -> jsii.Number:
        """Get the number of Stages in this Pipeline.

        Stability:
            experimental
        """
        return jsii.get(self, "stageCount")


@jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.PipelineProps", jsii_struct_bases=[])
class PipelineProps(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    artifactBucket: aws_cdk.aws_s3.IBucket
    """The S3 bucket used by this Pipeline to store artifacts.

    Default:
        - A new S3 bucket will be created.

    Stability:
        experimental
    """

    crossRegionReplicationBuckets: typing.Mapping[str,aws_cdk.aws_s3.IBucket]
    """A map of region to S3 bucket name used for cross-region CodePipeline. For every Action that you specify targeting a different region than the Pipeline itself, if you don't provide an explicit Bucket for that region using this property, the construct will automatically create a Stack containing an S3 Bucket in that region.

    Default:
        - None.

    Stability:
        experimental
    """

    pipelineName: str
    """Name of the pipeline.

    Default:
        - AWS CloudFormation generates an ID and uses that for the pipeline name.

    Stability:
        experimental
    """

    restartExecutionOnUpdate: bool
    """Indicates whether to rerun the AWS CodePipeline pipeline after you update it.

    Default:
        false

    Stability:
        experimental
    """

    role: aws_cdk.aws_iam.IRole
    """The IAM role to be assumed by this Pipeline.

    Default:
        a new IAM role will be created.

    Stability:
        experimental
    """

    stages: typing.List["StageProps"]
    """The list of Stages, in order, to create this Pipeline with. You can always add more Stages later by calling {@link Pipeline#addStage}.

    Default:
        - None.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.StagePlacement", jsii_struct_bases=[])
class StagePlacement(jsii.compat.TypedDict, total=False):
    """Allows you to control where to place a new Stage when it's added to the Pipeline. Note that you can provide only one of the below properties - specifying more than one will result in a validation error.

    See:
        #justAfter
    Stability:
        experimental
    """
    justAfter: "IStage"
    """Inserts the new Stage as a child of the given Stage (changing its current child Stage, if it had one).

    Stability:
        experimental
    """

    rightBefore: "IStage"
    """Inserts the new Stage as a parent of the given Stage (changing its current parent Stage, if it had one).

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _StageProps(jsii.compat.TypedDict, total=False):
    actions: typing.List["IAction"]
    """The list of Actions to create this Stage with. You can always add more Actions later by calling {@link IStage#addAction}.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.StageProps", jsii_struct_bases=[_StageProps])
class StageProps(_StageProps):
    """Construction properties of a Pipeline Stage.

    Stability:
        experimental
    """
    stageName: str
    """The physical, human-readable name to assign to this Pipeline Stage.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.StageOptions", jsii_struct_bases=[StageProps])
class StageOptions(StageProps, jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    placement: "StagePlacement"
    """
    Stability:
        experimental
    """

__all__ = ["ActionArtifactBounds", "ActionBindOptions", "ActionCategory", "ActionConfig", "ActionProperties", "Artifact", "ArtifactPath", "CfnCustomActionType", "CfnCustomActionTypeProps", "CfnPipeline", "CfnPipelineProps", "CfnWebhook", "CfnWebhookProps", "CommonActionProps", "CrossRegionSupport", "IAction", "IPipeline", "IStage", "Pipeline", "PipelineProps", "StageOptions", "StagePlacement", "StageProps", "__jsii_assembly__"]

publication.publish()
