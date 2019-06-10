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
import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-codepipeline", "0.34.0", __name__, "aws-codepipeline@0.34.0.jsii.tgz")
class Action(metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/aws-codepipeline.Action"):
    """Low-level class for generic CodePipeline Actions.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _ActionProxy

    def __init__(self, *, artifact_bounds: "ActionArtifactBounds", category: "ActionCategory", provider: str, configuration: typing.Any=None, inputs: typing.Optional[typing.List["Artifact"]]=None, outputs: typing.Optional[typing.List["Artifact"]]=None, owner: typing.Optional[str]=None, region: typing.Optional[str]=None, role: typing.Optional[aws_cdk.aws_iam.IRole]=None, version: typing.Optional[str]=None, action_name: str, run_order: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            props: -
            artifactBounds: 
            category: 
            provider: 
            configuration: 
            inputs: 
            outputs: 
            owner: 
            region: The region this Action resides in. Default: the Action resides in the same region as the Pipeline
            role: The service role that is assumed during execution of action. This role is not mandatory, however more advanced configuration may require specifying it.
            version: 
            actionName: The physical, human-readable name of the Action. Not that Action names must be unique within a single Stage.
            runOrder: The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1

        Stability:
            experimental
        """
        props: ActionProps = {"artifactBounds": artifact_bounds, "category": category, "provider": provider, "actionName": action_name}

        if configuration is not None:
            props["configuration"] = configuration

        if inputs is not None:
            props["inputs"] = inputs

        if outputs is not None:
            props["outputs"] = outputs

        if owner is not None:
            props["owner"] = owner

        if region is not None:
            props["region"] = region

        if role is not None:
            props["role"] = role

        if version is not None:
            props["version"] = version

        if run_order is not None:
            props["runOrder"] = run_order

        jsii.create(Action, self, [props])

    @jsii.member(jsii_name="addInputArtifact")
    def _add_input_artifact(self, artifact: "Artifact") -> None:
        """
        Arguments:
            artifact: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addInputArtifact", [artifact])

    @jsii.member(jsii_name="bind")
    @abc.abstractmethod
    def _bind(self, *, pipeline: "IPipeline", role: aws_cdk.aws_iam.IRole, scope: aws_cdk.cdk.Construct, stage: "IStage") -> None:
        """The method called when an Action is attached to a Pipeline. This method is guaranteed to be called only once for each Action instance.

        Arguments:
            info: -
            pipeline: The pipeline this action has been added to.
            role: The IAM Role to add the necessary permissions to.
            scope: The scope construct for this action. Can be used by the action implementation to create any resources it needs to work correctly.
            stage: The stage this action has been added to.

        Stability:
            experimental
        info:
            an instance of the {@link ActionBind} class,
            that contains the necessary information for the Action
            to configure itself, like a reference to the Pipeline, Stage, Role, etc.
        """
        ...

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(self, name: str, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None, *, description: typing.Optional[str]=None, enabled: typing.Optional[bool]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, schedule_expression: typing.Optional[str]=None, targets: typing.Optional[typing.List[aws_cdk.aws_events.IRuleTarget]]=None) -> aws_cdk.aws_events.Rule:
        """
        Arguments:
            name: -
            target: -
            options: -
            description: A description of the rule's purpose. Default: - No description.
            enabled: Indicates whether the rule is enabled. Default: true
            eventPattern: Describes which events CloudWatch Events routes to the specified target. These routed events are matched events. For more information, see Events and Event Patterns in the Amazon CloudWatch User Guide. Default: - None.
            ruleName: A name for the rule. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the rule name. For more information, see Name Type.
            scheduleExpression: The schedule or rate (frequency) that determines when CloudWatch Events runs the rule. For more information, see Schedule Expression Syntax for Rules in the Amazon CloudWatch User Guide. Default: - None.
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

        if schedule_expression is not None:
            options["scheduleExpression"] = schedule_expression

        if targets is not None:
            options["targets"] = targets

        return jsii.invoke(self, "onStateChange", [name, target, options])

    @property
    @jsii.member(jsii_name="actionName")
    def action_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "actionName")

    @property
    @jsii.member(jsii_name="category")
    def category(self) -> "ActionCategory":
        """The category of the action. The category defines which action type the owner (the entity that performs the action) performs.

        Stability:
            experimental
        """
        return jsii.get(self, "category")

    @property
    @jsii.member(jsii_name="inputs")
    def inputs(self) -> typing.List["Artifact"]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "inputs")

    @property
    @jsii.member(jsii_name="outputs")
    def outputs(self) -> typing.List["Artifact"]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "outputs")

    @property
    @jsii.member(jsii_name="owner")
    def owner(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "owner")

    @property
    @jsii.member(jsii_name="provider")
    def provider(self) -> str:
        """The service provider that the action calls.

        Stability:
            experimental
        """
        return jsii.get(self, "provider")

    @property
    @jsii.member(jsii_name="runOrder")
    def run_order(self) -> jsii.Number:
        """The order in which AWS CodePipeline runs this action. For more information, see the AWS CodePipeline User Guide.

        https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html#action-requirements

        Stability:
            experimental
        """
        return jsii.get(self, "runOrder")

    @property
    @jsii.member(jsii_name="scope")
    def _scope(self) -> aws_cdk.cdk.Construct:
        """Retrieves the Construct scope of this Action. Only available after the Action has been added to a Stage, and that Stage to a Pipeline.

        Stability:
            experimental
        """
        return jsii.get(self, "scope")

    @property
    @jsii.member(jsii_name="version")
    def version(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "version")

    @property
    @jsii.member(jsii_name="configuration")
    def configuration(self) -> typing.Any:
        """The action's configuration.

        These are key-value pairs that specify input values for an action.
        For more information, see the AWS CodePipeline User Guide.

        http://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html#action-requirements

        Stability:
            experimental
        """
        return jsii.get(self, "configuration")

    @property
    @jsii.member(jsii_name="region")
    def region(self) -> typing.Optional[str]:
        """The AWS region the given Action resides in. Note that a cross-region Pipeline requires replication buckets to function correctly. You can provide their names with the {@link PipelineProps#crossRegionReplicationBuckets} property. If you don't, the CodePipeline Construct will create new Stacks in your CDK app containing those buckets, that you will need to ``cdk deploy`` before deploying the main, Pipeline-containing Stack.

        Default:
            the Action resides in the same region as the Pipeline

        Stability:
            experimental
        """
        return jsii.get(self, "region")

    @property
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        """The service role that is assumed during execution of action. This role is not mandatory, however more advanced configuration may require specifying it.

        See:
            https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html
        Stability:
            experimental
        """
        return jsii.get(self, "role")


class _ActionProxy(Action):
    @jsii.member(jsii_name="bind")
    def _bind(self, *, pipeline: "IPipeline", role: aws_cdk.aws_iam.IRole, scope: aws_cdk.cdk.Construct, stage: "IStage") -> None:
        """The method called when an Action is attached to a Pipeline. This method is guaranteed to be called only once for each Action instance.

        Arguments:
            info: -
            pipeline: The pipeline this action has been added to.
            role: The IAM Role to add the necessary permissions to.
            scope: The scope construct for this action. Can be used by the action implementation to create any resources it needs to work correctly.
            stage: The stage this action has been added to.

        Stability:
            experimental
        info:
            an instance of the {@link ActionBind} class,
            that contains the necessary information for the Action
            to configure itself, like a reference to the Pipeline, Stage, Role, etc.
        """
        info: ActionBind = {"pipeline": pipeline, "role": role, "scope": scope, "stage": stage}

        return jsii.invoke(self, "bind", [info])


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

@jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.ActionBind", jsii_struct_bases=[])
class ActionBind(jsii.compat.TypedDict):
    """The interface used in the {@link Action#bind()} callback.

    Stability:
        experimental
    """
    pipeline: "IPipeline"
    """The pipeline this action has been added to.

    Stability:
        experimental
    """

    role: aws_cdk.aws_iam.IRole
    """The IAM Role to add the necessary permissions to.

    Stability:
        experimental
    """

    scope: aws_cdk.cdk.Construct
    """The scope construct for this action. Can be used by the action implementation to create any resources it needs to work correctly.

    Stability:
        experimental
    """

    stage: "IStage"
    """The stage this action has been added to.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-codepipeline.ActionCategory")
class ActionCategory(enum.Enum):
    """
    Stability:
        experimental
    """
    Source = "Source"
    """
    Stability:
        experimental
    """
    Build = "Build"
    """
    Stability:
        experimental
    """
    Test = "Test"
    """
    Stability:
        experimental
    """
    Approval = "Approval"
    """
    Stability:
        experimental
    """
    Deploy = "Deploy"
    """
    Stability:
        experimental
    """
    Invoke = "Invoke"
    """
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
            artifactName: -

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
            fileName: The name of the file.

        Stability:
            experimental
        """
        return jsii.invoke(self, "atPath", [file_name])

    @jsii.member(jsii_name="getParam")
    def get_param(self, json_file: str, key_name: str) -> str:
        """Returns a token for a value inside a JSON file within this artifact.

        Arguments:
            jsonFile: The JSON file name.
            keyName: The hash key.

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
    @jsii.member(jsii_name="s3Coordinates")
    def s3_coordinates(self) -> aws_cdk.aws_s3.Coordinates:
        """Returns the coordinates of the .zip file in S3 that this Artifact represents. Used by Lambda's ``CfnParametersCode`` when being deployed in a CodePipeline.

        Stability:
            experimental
        """
        return jsii.get(self, "s3Coordinates")

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
            fileName: -

        Stability:
            experimental
        """
        jsii.create(ArtifactPath, self, [artifact, file_name])

    @jsii.member(jsii_name="artifactPath")
    @classmethod
    def artifact_path(cls, artifact_name: str, file_name: str) -> "ArtifactPath":
        """
        Arguments:
            artifactName: -
            fileName: -

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


class CfnCustomActionType(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codepipeline.CfnCustomActionType"):
    """A CloudFormation ``AWS::CodePipeline::CustomActionType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html
    Stability:
        experimental
    cloudformationResource:
        AWS::CodePipeline::CustomActionType
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, category: str, input_artifact_details: typing.Union[aws_cdk.cdk.Token, "ArtifactDetailsProperty"], output_artifact_details: typing.Union[aws_cdk.cdk.Token, "ArtifactDetailsProperty"], provider: str, configuration_properties: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "ConfigurationPropertiesProperty"]]]]]=None, settings: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["SettingsProperty"]]]=None, version: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::CodePipeline::CustomActionType``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            category: ``AWS::CodePipeline::CustomActionType.Category``.
            inputArtifactDetails: ``AWS::CodePipeline::CustomActionType.InputArtifactDetails``.
            outputArtifactDetails: ``AWS::CodePipeline::CustomActionType.OutputArtifactDetails``.
            provider: ``AWS::CodePipeline::CustomActionType.Provider``.
            configurationProperties: ``AWS::CodePipeline::CustomActionType.ConfigurationProperties``.
            settings: ``AWS::CodePipeline::CustomActionType.Settings``.
            version: ``AWS::CodePipeline::CustomActionType.Version``.

        Stability:
            experimental
        """
        props: CfnCustomActionTypeProps = {"category": category, "inputArtifactDetails": input_artifact_details, "outputArtifactDetails": output_artifact_details, "provider": provider}

        if configuration_properties is not None:
            props["configurationProperties"] = configuration_properties

        if settings is not None:
            props["settings"] = settings

        if version is not None:
            props["version"] = version

        jsii.create(CfnCustomActionType, self, [scope, id, props])

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
    @jsii.member(jsii_name="customActionTypeName")
    def custom_action_type_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "customActionTypeName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnCustomActionTypeProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CfnCustomActionType.ArtifactDetailsProperty", jsii_struct_bases=[])
    class ArtifactDetailsProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-artifactdetails.html
        Stability:
            experimental
        """
        maximumCount: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnCustomActionType.ArtifactDetailsProperty.MaximumCount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-artifactdetails.html#cfn-codepipeline-customactiontype-artifactdetails-maximumcount
        Stability:
            experimental
        """

        minimumCount: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnCustomActionType.ArtifactDetailsProperty.MinimumCount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-artifactdetails.html#cfn-codepipeline-customactiontype-artifactdetails-minimumcount
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ConfigurationPropertiesProperty(jsii.compat.TypedDict, total=False):
        description: str
        """``CfnCustomActionType.ConfigurationPropertiesProperty.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-configurationproperties.html#cfn-codepipeline-customactiontype-configurationproperties-description
        Stability:
            experimental
        """
        queryable: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnCustomActionType.ConfigurationPropertiesProperty.Queryable``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-configurationproperties.html#cfn-codepipeline-customactiontype-configurationproperties-queryable
        Stability:
            experimental
        """
        type: str
        """``CfnCustomActionType.ConfigurationPropertiesProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-configurationproperties.html#cfn-codepipeline-customactiontype-configurationproperties-type
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CfnCustomActionType.ConfigurationPropertiesProperty", jsii_struct_bases=[_ConfigurationPropertiesProperty])
    class ConfigurationPropertiesProperty(_ConfigurationPropertiesProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-configurationproperties.html
        Stability:
            experimental
        """
        key: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnCustomActionType.ConfigurationPropertiesProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-configurationproperties.html#cfn-codepipeline-customactiontype-configurationproperties-key
        Stability:
            experimental
        """

        name: str
        """``CfnCustomActionType.ConfigurationPropertiesProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-configurationproperties.html#cfn-codepipeline-customactiontype-configurationproperties-name
        Stability:
            experimental
        """

        required: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnCustomActionType.ConfigurationPropertiesProperty.Required``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-configurationproperties.html#cfn-codepipeline-customactiontype-configurationproperties-required
        Stability:
            experimental
        """

        secret: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnCustomActionType.ConfigurationPropertiesProperty.Secret``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-configurationproperties.html#cfn-codepipeline-customactiontype-configurationproperties-secret
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CfnCustomActionType.SettingsProperty", jsii_struct_bases=[])
    class SettingsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-settings.html
        Stability:
            experimental
        """
        entityUrlTemplate: str
        """``CfnCustomActionType.SettingsProperty.EntityUrlTemplate``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-settings.html#cfn-codepipeline-customactiontype-settings-entityurltemplate
        Stability:
            experimental
        """

        executionUrlTemplate: str
        """``CfnCustomActionType.SettingsProperty.ExecutionUrlTemplate``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-settings.html#cfn-codepipeline-customactiontype-settings-executionurltemplate
        Stability:
            experimental
        """

        revisionUrlTemplate: str
        """``CfnCustomActionType.SettingsProperty.RevisionUrlTemplate``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-settings.html#cfn-codepipeline-customactiontype-settings-revisionurltemplate
        Stability:
            experimental
        """

        thirdPartyConfigurationUrl: str
        """``CfnCustomActionType.SettingsProperty.ThirdPartyConfigurationUrl``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-settings.html#cfn-codepipeline-customactiontype-settings-thirdpartyconfigurationurl
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnCustomActionTypeProps(jsii.compat.TypedDict, total=False):
    configurationProperties: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnCustomActionType.ConfigurationPropertiesProperty"]]]
    """``AWS::CodePipeline::CustomActionType.ConfigurationProperties``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-configurationproperties
    Stability:
        experimental
    """
    settings: typing.Union[aws_cdk.cdk.Token, "CfnCustomActionType.SettingsProperty"]
    """``AWS::CodePipeline::CustomActionType.Settings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-settings
    Stability:
        experimental
    """
    version: str
    """``AWS::CodePipeline::CustomActionType.Version``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-version
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CfnCustomActionTypeProps", jsii_struct_bases=[_CfnCustomActionTypeProps])
class CfnCustomActionTypeProps(_CfnCustomActionTypeProps):
    """Properties for defining a ``AWS::CodePipeline::CustomActionType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html
    Stability:
        experimental
    """
    category: str
    """``AWS::CodePipeline::CustomActionType.Category``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-category
    Stability:
        experimental
    """

    inputArtifactDetails: typing.Union[aws_cdk.cdk.Token, "CfnCustomActionType.ArtifactDetailsProperty"]
    """``AWS::CodePipeline::CustomActionType.InputArtifactDetails``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-inputartifactdetails
    Stability:
        experimental
    """

    outputArtifactDetails: typing.Union[aws_cdk.cdk.Token, "CfnCustomActionType.ArtifactDetailsProperty"]
    """``AWS::CodePipeline::CustomActionType.OutputArtifactDetails``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-outputartifactdetails
    Stability:
        experimental
    """

    provider: str
    """``AWS::CodePipeline::CustomActionType.Provider``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-provider
    Stability:
        experimental
    """

class CfnPipeline(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codepipeline.CfnPipeline"):
    """A CloudFormation ``AWS::CodePipeline::Pipeline``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html
    Stability:
        experimental
    cloudformationResource:
        AWS::CodePipeline::Pipeline
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, role_arn: str, stages: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "StageDeclarationProperty"]]], artifact_store: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["ArtifactStoreProperty"]]]=None, artifact_stores: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "ArtifactStoreMapProperty"]]]]]=None, disable_inbound_stage_transitions: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "StageTransitionProperty"]]]]]=None, name: typing.Optional[str]=None, restart_execution_on_update: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None) -> None:
        """Create a new ``AWS::CodePipeline::Pipeline``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            roleArn: ``AWS::CodePipeline::Pipeline.RoleArn``.
            stages: ``AWS::CodePipeline::Pipeline.Stages``.
            artifactStore: ``AWS::CodePipeline::Pipeline.ArtifactStore``.
            artifactStores: ``AWS::CodePipeline::Pipeline.ArtifactStores``.
            disableInboundStageTransitions: ``AWS::CodePipeline::Pipeline.DisableInboundStageTransitions``.
            name: ``AWS::CodePipeline::Pipeline.Name``.
            restartExecutionOnUpdate: ``AWS::CodePipeline::Pipeline.RestartExecutionOnUpdate``.

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
    @jsii.member(jsii_name="pipelineName")
    def pipeline_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "pipelineName")

    @property
    @jsii.member(jsii_name="pipelineVersion")
    def pipeline_version(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Version
        """
        return jsii.get(self, "pipelineVersion")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnPipelineProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ActionDeclarationProperty(jsii.compat.TypedDict, total=False):
        configuration: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
        """``CfnPipeline.ActionDeclarationProperty.Configuration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html#cfn-codepipeline-pipeline-stages-actions-configuration
        Stability:
            experimental
        """
        inputArtifacts: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnPipeline.InputArtifactProperty"]]]
        """``CfnPipeline.ActionDeclarationProperty.InputArtifacts``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html#cfn-codepipeline-pipeline-stages-actions-inputartifacts
        Stability:
            experimental
        """
        outputArtifacts: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnPipeline.OutputArtifactProperty"]]]
        """``CfnPipeline.ActionDeclarationProperty.OutputArtifacts``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html#cfn-codepipeline-pipeline-stages-actions-outputartifacts
        Stability:
            experimental
        """
        region: str
        """``CfnPipeline.ActionDeclarationProperty.Region``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html#cfn-codepipeline-pipeline-stages-actions-region
        Stability:
            experimental
        """
        roleArn: str
        """``CfnPipeline.ActionDeclarationProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html#cfn-codepipeline-pipeline-stages-actions-rolearn
        Stability:
            experimental
        """
        runOrder: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnPipeline.ActionDeclarationProperty.RunOrder``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html#cfn-codepipeline-pipeline-stages-actions-runorder
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CfnPipeline.ActionDeclarationProperty", jsii_struct_bases=[_ActionDeclarationProperty])
    class ActionDeclarationProperty(_ActionDeclarationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html
        Stability:
            experimental
        """
        actionTypeId: typing.Union[aws_cdk.cdk.Token, "CfnPipeline.ActionTypeIdProperty"]
        """``CfnPipeline.ActionDeclarationProperty.ActionTypeId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html#cfn-codepipeline-pipeline-stages-actions-actiontypeid
        Stability:
            experimental
        """

        name: str
        """``CfnPipeline.ActionDeclarationProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html#cfn-codepipeline-pipeline-stages-actions-name
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CfnPipeline.ActionTypeIdProperty", jsii_struct_bases=[])
    class ActionTypeIdProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions-actiontypeid.html
        Stability:
            experimental
        """
        category: str
        """``CfnPipeline.ActionTypeIdProperty.Category``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions-actiontypeid.html#cfn-codepipeline-pipeline-stages-actions-actiontypeid-category
        Stability:
            experimental
        """

        owner: str
        """``CfnPipeline.ActionTypeIdProperty.Owner``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions-actiontypeid.html#cfn-codepipeline-pipeline-stages-actions-actiontypeid-owner
        Stability:
            experimental
        """

        provider: str
        """``CfnPipeline.ActionTypeIdProperty.Provider``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions-actiontypeid.html#cfn-codepipeline-pipeline-stages-actions-actiontypeid-provider
        Stability:
            experimental
        """

        version: str
        """``CfnPipeline.ActionTypeIdProperty.Version``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions-actiontypeid.html#cfn-codepipeline-pipeline-stages-actions-actiontypeid-version
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CfnPipeline.ArtifactStoreMapProperty", jsii_struct_bases=[])
    class ArtifactStoreMapProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstoremap.html
        Stability:
            experimental
        """
        artifactStore: typing.Union[aws_cdk.cdk.Token, "CfnPipeline.ArtifactStoreProperty"]
        """``CfnPipeline.ArtifactStoreMapProperty.ArtifactStore``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstoremap.html#cfn-codepipeline-pipeline-artifactstoremap-artifactstore
        Stability:
            experimental
        """

        region: str
        """``CfnPipeline.ArtifactStoreMapProperty.Region``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstoremap.html#cfn-codepipeline-pipeline-artifactstoremap-region
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ArtifactStoreProperty(jsii.compat.TypedDict, total=False):
        encryptionKey: typing.Union[aws_cdk.cdk.Token, "CfnPipeline.EncryptionKeyProperty"]
        """``CfnPipeline.ArtifactStoreProperty.EncryptionKey``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstore.html#cfn-codepipeline-pipeline-artifactstore-encryptionkey
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CfnPipeline.ArtifactStoreProperty", jsii_struct_bases=[_ArtifactStoreProperty])
    class ArtifactStoreProperty(_ArtifactStoreProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstore.html
        Stability:
            experimental
        """
        location: str
        """``CfnPipeline.ArtifactStoreProperty.Location``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstore.html#cfn-codepipeline-pipeline-artifactstore-location
        Stability:
            experimental
        """

        type: str
        """``CfnPipeline.ArtifactStoreProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstore.html#cfn-codepipeline-pipeline-artifactstore-type
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CfnPipeline.BlockerDeclarationProperty", jsii_struct_bases=[])
    class BlockerDeclarationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-blockers.html
        Stability:
            experimental
        """
        name: str
        """``CfnPipeline.BlockerDeclarationProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-blockers.html#cfn-codepipeline-pipeline-stages-blockers-name
        Stability:
            experimental
        """

        type: str
        """``CfnPipeline.BlockerDeclarationProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-blockers.html#cfn-codepipeline-pipeline-stages-blockers-type
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CfnPipeline.EncryptionKeyProperty", jsii_struct_bases=[])
    class EncryptionKeyProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstore-encryptionkey.html
        Stability:
            experimental
        """
        id: str
        """``CfnPipeline.EncryptionKeyProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstore-encryptionkey.html#cfn-codepipeline-pipeline-artifactstore-encryptionkey-id
        Stability:
            experimental
        """

        type: str
        """``CfnPipeline.EncryptionKeyProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstore-encryptionkey.html#cfn-codepipeline-pipeline-artifactstore-encryptionkey-type
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CfnPipeline.InputArtifactProperty", jsii_struct_bases=[])
    class InputArtifactProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions-inputartifacts.html
        Stability:
            experimental
        """
        name: str
        """``CfnPipeline.InputArtifactProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions-inputartifacts.html#cfn-codepipeline-pipeline-stages-actions-inputartifacts-name
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CfnPipeline.OutputArtifactProperty", jsii_struct_bases=[])
    class OutputArtifactProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions-outputartifacts.html
        Stability:
            experimental
        """
        name: str
        """``CfnPipeline.OutputArtifactProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions-outputartifacts.html#cfn-codepipeline-pipeline-stages-actions-outputartifacts-name
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _StageDeclarationProperty(jsii.compat.TypedDict, total=False):
        blockers: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnPipeline.BlockerDeclarationProperty"]]]
        """``CfnPipeline.StageDeclarationProperty.Blockers``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages.html#cfn-codepipeline-pipeline-stages-blockers
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CfnPipeline.StageDeclarationProperty", jsii_struct_bases=[_StageDeclarationProperty])
    class StageDeclarationProperty(_StageDeclarationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages.html
        Stability:
            experimental
        """
        actions: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnPipeline.ActionDeclarationProperty"]]]
        """``CfnPipeline.StageDeclarationProperty.Actions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages.html#cfn-codepipeline-pipeline-stages-actions
        Stability:
            experimental
        """

        name: str
        """``CfnPipeline.StageDeclarationProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages.html#cfn-codepipeline-pipeline-stages-name
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CfnPipeline.StageTransitionProperty", jsii_struct_bases=[])
    class StageTransitionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-disableinboundstagetransitions.html
        Stability:
            experimental
        """
        reason: str
        """``CfnPipeline.StageTransitionProperty.Reason``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-disableinboundstagetransitions.html#cfn-codepipeline-pipeline-disableinboundstagetransitions-reason
        Stability:
            experimental
        """

        stageName: str
        """``CfnPipeline.StageTransitionProperty.StageName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-disableinboundstagetransitions.html#cfn-codepipeline-pipeline-disableinboundstagetransitions-stagename
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnPipelineProps(jsii.compat.TypedDict, total=False):
    artifactStore: typing.Union[aws_cdk.cdk.Token, "CfnPipeline.ArtifactStoreProperty"]
    """``AWS::CodePipeline::Pipeline.ArtifactStore``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-artifactstore
    Stability:
        experimental
    """
    artifactStores: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnPipeline.ArtifactStoreMapProperty"]]]
    """``AWS::CodePipeline::Pipeline.ArtifactStores``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-artifactstores
    Stability:
        experimental
    """
    disableInboundStageTransitions: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnPipeline.StageTransitionProperty"]]]
    """``AWS::CodePipeline::Pipeline.DisableInboundStageTransitions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-disableinboundstagetransitions
    Stability:
        experimental
    """
    name: str
    """``AWS::CodePipeline::Pipeline.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-name
    Stability:
        experimental
    """
    restartExecutionOnUpdate: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::CodePipeline::Pipeline.RestartExecutionOnUpdate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-restartexecutiononupdate
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CfnPipelineProps", jsii_struct_bases=[_CfnPipelineProps])
class CfnPipelineProps(_CfnPipelineProps):
    """Properties for defining a ``AWS::CodePipeline::Pipeline``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html
    Stability:
        experimental
    """
    roleArn: str
    """``AWS::CodePipeline::Pipeline.RoleArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-rolearn
    Stability:
        experimental
    """

    stages: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnPipeline.StageDeclarationProperty"]]]
    """``AWS::CodePipeline::Pipeline.Stages``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-stages
    Stability:
        experimental
    """

class CfnWebhook(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codepipeline.CfnWebhook"):
    """A CloudFormation ``AWS::CodePipeline::Webhook``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html
    Stability:
        experimental
    cloudformationResource:
        AWS::CodePipeline::Webhook
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, authentication: str, authentication_configuration: typing.Union[aws_cdk.cdk.Token, "WebhookAuthConfigurationProperty"], filters: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "WebhookFilterRuleProperty"]]], target_action: str, target_pipeline: str, target_pipeline_version: typing.Union[jsii.Number, aws_cdk.cdk.Token], name: typing.Optional[str]=None, register_with_third_party: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None) -> None:
        """Create a new ``AWS::CodePipeline::Webhook``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            authentication: ``AWS::CodePipeline::Webhook.Authentication``.
            authenticationConfiguration: ``AWS::CodePipeline::Webhook.AuthenticationConfiguration``.
            filters: ``AWS::CodePipeline::Webhook.Filters``.
            targetAction: ``AWS::CodePipeline::Webhook.TargetAction``.
            targetPipeline: ``AWS::CodePipeline::Webhook.TargetPipeline``.
            targetPipelineVersion: ``AWS::CodePipeline::Webhook.TargetPipelineVersion``.
            name: ``AWS::CodePipeline::Webhook.Name``.
            registerWithThirdParty: ``AWS::CodePipeline::Webhook.RegisterWithThirdParty``.

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
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnWebhookProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="webhookName")
    def webhook_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "webhookName")

    @property
    @jsii.member(jsii_name="webhookUrl")
    def webhook_url(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Url
        """
        return jsii.get(self, "webhookUrl")

    @jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CfnWebhook.WebhookAuthConfigurationProperty", jsii_struct_bases=[])
    class WebhookAuthConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-webhook-webhookauthconfiguration.html
        Stability:
            experimental
        """
        allowedIpRange: str
        """``CfnWebhook.WebhookAuthConfigurationProperty.AllowedIPRange``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-webhook-webhookauthconfiguration.html#cfn-codepipeline-webhook-webhookauthconfiguration-allowediprange
        Stability:
            experimental
        """

        secretToken: str
        """``CfnWebhook.WebhookAuthConfigurationProperty.SecretToken``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-webhook-webhookauthconfiguration.html#cfn-codepipeline-webhook-webhookauthconfiguration-secrettoken
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _WebhookFilterRuleProperty(jsii.compat.TypedDict, total=False):
        matchEquals: str
        """``CfnWebhook.WebhookFilterRuleProperty.MatchEquals``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-webhook-webhookfilterrule.html#cfn-codepipeline-webhook-webhookfilterrule-matchequals
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CfnWebhook.WebhookFilterRuleProperty", jsii_struct_bases=[_WebhookFilterRuleProperty])
    class WebhookFilterRuleProperty(_WebhookFilterRuleProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-webhook-webhookfilterrule.html
        Stability:
            experimental
        """
        jsonPath: str
        """``CfnWebhook.WebhookFilterRuleProperty.JsonPath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-webhook-webhookfilterrule.html#cfn-codepipeline-webhook-webhookfilterrule-jsonpath
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnWebhookProps(jsii.compat.TypedDict, total=False):
    name: str
    """``AWS::CodePipeline::Webhook.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-name
    Stability:
        experimental
    """
    registerWithThirdParty: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::CodePipeline::Webhook.RegisterWithThirdParty``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-registerwiththirdparty
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.CfnWebhookProps", jsii_struct_bases=[_CfnWebhookProps])
class CfnWebhookProps(_CfnWebhookProps):
    """Properties for defining a ``AWS::CodePipeline::Webhook``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html
    Stability:
        experimental
    """
    authentication: str
    """``AWS::CodePipeline::Webhook.Authentication``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-authentication
    Stability:
        experimental
    """

    authenticationConfiguration: typing.Union[aws_cdk.cdk.Token, "CfnWebhook.WebhookAuthConfigurationProperty"]
    """``AWS::CodePipeline::Webhook.AuthenticationConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-authenticationconfiguration
    Stability:
        experimental
    """

    filters: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnWebhook.WebhookFilterRuleProperty"]]]
    """``AWS::CodePipeline::Webhook.Filters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-filters
    Stability:
        experimental
    """

    targetAction: str
    """``AWS::CodePipeline::Webhook.TargetAction``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-targetaction
    Stability:
        experimental
    """

    targetPipeline: str
    """``AWS::CodePipeline::Webhook.TargetPipeline``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-targetpipeline
    Stability:
        experimental
    """

    targetPipelineVersion: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::CodePipeline::Webhook.TargetPipelineVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-targetpipelineversion
    Stability:
        experimental
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

@jsii.data_type_optionals(jsii_struct_bases=[CommonActionProps])
class _ActionProps(CommonActionProps, jsii.compat.TypedDict, total=False):
    configuration: typing.Any
    """
    Stability:
        experimental
    """
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
    """The region this Action resides in.

    Default:
        the Action resides in the same region as the Pipeline

    Stability:
        experimental
    """
    role: aws_cdk.aws_iam.IRole
    """The service role that is assumed during execution of action. This role is not mandatory, however more advanced configuration may require specifying it.

    See:
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html
    Stability:
        experimental
    """
    version: str
    """
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.ActionProps", jsii_struct_bases=[_ActionProps])
class ActionProps(_ActionProps):
    """Construction properties of the low-level {@link Action Action class}.

    Stability:
        experimental
    """
    artifactBounds: "ActionArtifactBounds"
    """
    Stability:
        experimental
    """

    category: "ActionCategory"
    """
    Stability:
        experimental
    """

    provider: str
    """
    Stability:
        experimental
    """

class CrossRegionScaffolding(aws_cdk.cdk.Stack, metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/aws-codepipeline.CrossRegionScaffolding"):
    """A Stack containing resources required for the cross-region CodePipeline functionality to work.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _CrossRegionScaffoldingProxy

    def __init__(self, scope: typing.Optional[aws_cdk.cdk.Construct]=None, name: typing.Optional[str]=None, *, env: typing.Optional[aws_cdk.cdk.Environment]=None, naming_scheme: typing.Optional[aws_cdk.cdk.IAddressingScheme]=None, stack_name: typing.Optional[str]=None, tags: typing.Optional[typing.Mapping[str,str]]=None) -> None:
        """Creates a new stack.

        Arguments:
            scope: Parent of this stack, usually a Program instance.
            name: The name of the CloudFormation stack. Defaults to "Stack".
            props: Stack properties.
            env: The AWS environment (account/region) where this stack will be deployed. Default: - The ``default-account`` and ``default-region`` context parameters will be used. If they are undefined, it will not be possible to deploy the stack.
            namingScheme: Strategy for logical ID generation. Default: - The HashedNamingScheme will be used.
            stackName: Name to deploy the stack with. Default: - Derived from construct path.
            tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}

        Stability:
            experimental
        """
        props: aws_cdk.cdk.StackProps = {}

        if env is not None:
            props["env"] = env

        if naming_scheme is not None:
            props["namingScheme"] = naming_scheme

        if stack_name is not None:
            props["stackName"] = stack_name

        if tags is not None:
            props["tags"] = tags

        jsii.create(CrossRegionScaffolding, self, [scope, name, props])

    @property
    @jsii.member(jsii_name="replicationBucketName")
    @abc.abstractmethod
    def replication_bucket_name(self) -> str:
        """The name of the S3 Bucket used for replicating the Pipeline's artifacts into the region.

        Stability:
            experimental
        """
        ...


class _CrossRegionScaffoldingProxy(CrossRegionScaffolding):
    @property
    @jsii.member(jsii_name="replicationBucketName")
    def replication_bucket_name(self) -> str:
        """The name of the S3 Bucket used for replicating the Pipeline's artifacts into the region.

        Stability:
            experimental
        """
        return jsii.get(self, "replicationBucketName")


@jsii.interface(jsii_type="@aws-cdk/aws-codepipeline.IPipeline")
class IPipeline(aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """The abstract view of an AWS CodePipeline as required and used by Actions. It extends {@link events.IRuleTarget}, so this interface can be used as a Target for CloudWatch Events.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IPipelineProxy

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

    @jsii.member(jsii_name="grantBucketRead")
    def grant_bucket_read(self, identity: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grants read permissions to the Pipeline's S3 Bucket to the given Identity.

        Arguments:
            identity: the IAM Identity to grant the permissions to.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="grantBucketReadWrite")
    def grant_bucket_read_write(self, identity: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grants read & write permissions to the Pipeline's S3 Bucket to the given Identity.

        Arguments:
            identity: the IAM Identity to grant the permissions to.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="onEvent")
    def on_event(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Define an event rule triggered by this CodePipeline.

        Arguments:
            id: Identifier for this event handler.
            options: Additional options to pass to the event rule.
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Define an event rule triggered by the "CodePipeline Pipeline Execution State Change" event emitted from this pipeline.

        Arguments:
            id: Identifier for this event handler.
            options: Additional options to pass to the event rule.
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        ...


class _IPipelineProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
    """The abstract view of an AWS CodePipeline as required and used by Actions. It extends {@link events.IRuleTarget}, so this interface can be used as a Target for CloudWatch Events.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-codepipeline.IPipeline"
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

    @jsii.member(jsii_name="grantBucketRead")
    def grant_bucket_read(self, identity: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grants read permissions to the Pipeline's S3 Bucket to the given Identity.

        Arguments:
            identity: the IAM Identity to grant the permissions to.

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantBucketRead", [identity])

    @jsii.member(jsii_name="grantBucketReadWrite")
    def grant_bucket_read_write(self, identity: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grants read & write permissions to the Pipeline's S3 Bucket to the given Identity.

        Arguments:
            identity: the IAM Identity to grant the permissions to.

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantBucketReadWrite", [identity])

    @jsii.member(jsii_name="onEvent")
    def on_event(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Define an event rule triggered by this CodePipeline.

        Arguments:
            id: Identifier for this event handler.
            options: Additional options to pass to the event rule.
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

        return jsii.invoke(self, "onEvent", [id, options])

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Define an event rule triggered by the "CodePipeline Pipeline Execution State Change" event emitted from this pipeline.

        Arguments:
            id: Identifier for this event handler.
            options: Additional options to pass to the event rule.
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
    @jsii.member(jsii_name="stageName")
    def stage_name(self) -> str:
        """The physical, human-readable name of this Pipeline Stage.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="addAction")
    def add_action(self, action: "Action") -> None:
        """
        Arguments:
            action: -

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(self, name: str, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None, *, description: typing.Optional[str]=None, enabled: typing.Optional[bool]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, schedule_expression: typing.Optional[str]=None, targets: typing.Optional[typing.List[aws_cdk.aws_events.IRuleTarget]]=None) -> aws_cdk.aws_events.Rule:
        """
        Arguments:
            name: -
            target: -
            options: -
            description: A description of the rule's purpose. Default: - No description.
            enabled: Indicates whether the rule is enabled. Default: true
            eventPattern: Describes which events CloudWatch Events routes to the specified target. These routed events are matched events. For more information, see Events and Event Patterns in the Amazon CloudWatch User Guide. Default: - None.
            ruleName: A name for the rule. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the rule name. For more information, see Name Type.
            scheduleExpression: The schedule or rate (frequency) that determines when CloudWatch Events runs the rule. For more information, see Schedule Expression Syntax for Rules in the Amazon CloudWatch User Guide. Default: - None.
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
    @jsii.member(jsii_name="stageName")
    def stage_name(self) -> str:
        """The physical, human-readable name of this Pipeline Stage.

        Stability:
            experimental
        """
        return jsii.get(self, "stageName")

    @jsii.member(jsii_name="addAction")
    def add_action(self, action: "Action") -> None:
        """
        Arguments:
            action: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addAction", [action])

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(self, name: str, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None, *, description: typing.Optional[str]=None, enabled: typing.Optional[bool]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, schedule_expression: typing.Optional[str]=None, targets: typing.Optional[typing.List[aws_cdk.aws_events.IRuleTarget]]=None) -> aws_cdk.aws_events.Rule:
        """
        Arguments:
            name: -
            target: -
            options: -
            description: A description of the rule's purpose. Default: - No description.
            enabled: Indicates whether the rule is enabled. Default: true
            eventPattern: Describes which events CloudWatch Events routes to the specified target. These routed events are matched events. For more information, see Events and Event Patterns in the Amazon CloudWatch User Guide. Default: - None.
            ruleName: A name for the rule. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the rule name. For more information, see Name Type.
            scheduleExpression: The schedule or rate (frequency) that determines when CloudWatch Events runs the rule. For more information, see Schedule Expression Syntax for Rules in the Amazon CloudWatch User Guide. Default: - None.
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

        if schedule_expression is not None:
            options["scheduleExpression"] = schedule_expression

        if targets is not None:
            options["targets"] = targets

        return jsii.invoke(self, "onStateChange", [name, target, options])


@jsii.implements(IPipeline)
class Pipeline(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codepipeline.Pipeline"):
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
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, artifact_bucket: typing.Optional[aws_cdk.aws_s3.IBucket]=None, cross_region_replication_buckets: typing.Optional[typing.Mapping[str,str]]=None, pipeline_name: typing.Optional[str]=None, restart_execution_on_update: typing.Optional[bool]=None, role: typing.Optional[aws_cdk.aws_iam.IRole]=None, stages: typing.Optional[typing.List["StageProps"]]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            artifactBucket: The S3 bucket used by this Pipeline to store artifacts. Default: - A new S3 bucket will be created.
            crossRegionReplicationBuckets: A map of region to S3 bucket name used for cross-region CodePipeline. For every Action that you specify targeting a different region than the Pipeline itself, if you don't provide an explicit Bucket for that region using this property, the construct will automatically create a scaffold Stack containing an S3 Bucket in that region. Note that you will have to ``cdk deploy`` that Stack before you can deploy your Pipeline-containing Stack. You can query the generated Stacks using the {@link Pipeline#crossRegionScaffoldStacks} property. Default: - None.
            pipelineName: Name of the pipeline. Default: - AWS CloudFormation generates an ID and uses that for the pipeline name.
            restartExecutionOnUpdate: Indicates whether to rerun the AWS CodePipeline pipeline after you update it. Default: false
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

    @jsii.member(jsii_name="fromPipelineArn")
    @classmethod
    def from_pipeline_arn(cls, scope: aws_cdk.cdk.Construct, id: str, pipeline_arn: str) -> "IPipeline":
        """Import a pipeline into this app.

        Arguments:
            scope: the scope into which to import this pipeline.
            id: -
            pipelineArn: The ARN of the pipeline (e.g. ``arn:aws:codepipeline:us-east-1:123456789012:MyDemoPipeline``).

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromPipelineArn", [scope, id, pipeline_arn])

    @jsii.member(jsii_name="addStage")
    def add_stage(self, *, placement: typing.Optional["StagePlacement"]=None, name: str, actions: typing.Optional[typing.List["Action"]]=None) -> "IStage":
        """Creates a new Stage, and adds it to this Pipeline.

        Arguments:
            props: the creation properties of the new Stage.
            placement: 
            name: The physical, human-readable name to assign to this Pipeline Stage.
            actions: The list of Actions to create this Stage with. You can always add more Actions later by calling {@link IStage#addAction}.

        Returns:
            the newly created Stage

        Stability:
            experimental
        """
        props: StageAddToPipelineProps = {"name": name}

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

    @jsii.member(jsii_name="grantBucketRead")
    def grant_bucket_read(self, identity: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grants read permissions to the Pipeline's S3 Bucket to the given Identity.

        Arguments:
            identity: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantBucketRead", [identity])

    @jsii.member(jsii_name="grantBucketReadWrite")
    def grant_bucket_read_write(self, identity: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grants read & write permissions to the Pipeline's S3 Bucket to the given Identity.

        Arguments:
            identity: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantBucketReadWrite", [identity])

    @jsii.member(jsii_name="onEvent")
    def on_event(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines an event rule triggered by this CodePipeline.

        Arguments:
            id: Identifier for this event handler.
            options: Additional options to pass to the event rule.
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

        return jsii.invoke(self, "onEvent", [id, options])

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines an event rule triggered by the "CodePipeline Pipeline Execution State Change" event emitted from this pipeline.

        Arguments:
            id: Identifier for this event handler.
            options: Additional options to pass to the event rule.
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
    @jsii.member(jsii_name="crossRegionScaffolding")
    def cross_region_scaffolding(self) -> typing.Mapping[str,"CrossRegionScaffolding"]:
        """Returns all of the {@link CrossRegionScaffoldStack}s that were generated automatically when dealing with Actions that reside in a different region than the Pipeline itself.

        Stability:
            experimental
        """
        return jsii.get(self, "crossRegionScaffolding")

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

    crossRegionReplicationBuckets: typing.Mapping[str,str]
    """A map of region to S3 bucket name used for cross-region CodePipeline. For every Action that you specify targeting a different region than the Pipeline itself, if you don't provide an explicit Bucket for that region using this property, the construct will automatically create a scaffold Stack containing an S3 Bucket in that region. Note that you will have to ``cdk deploy`` that Stack before you can deploy your Pipeline-containing Stack. You can query the generated Stacks using the {@link Pipeline#crossRegionScaffoldStacks} property.

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
        #atIndex
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
    actions: typing.List["Action"]
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
    name: str
    """The physical, human-readable name to assign to this Pipeline Stage.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-codepipeline.StageAddToPipelineProps", jsii_struct_bases=[StageProps])
class StageAddToPipelineProps(StageProps, jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    placement: "StagePlacement"
    """
    Stability:
        experimental
    """

__all__ = ["Action", "ActionArtifactBounds", "ActionBind", "ActionCategory", "ActionProps", "Artifact", "ArtifactPath", "CfnCustomActionType", "CfnCustomActionTypeProps", "CfnPipeline", "CfnPipelineProps", "CfnWebhook", "CfnWebhookProps", "CommonActionProps", "CrossRegionScaffolding", "IPipeline", "IStage", "Pipeline", "PipelineProps", "StageAddToPipelineProps", "StagePlacement", "StageProps", "__jsii_assembly__"]

publication.publish()
