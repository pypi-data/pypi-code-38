import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_cloudformation
import aws_cdk.aws_codebuild
import aws_cdk.aws_codepipeline
import aws_cdk.aws_codepipeline_actions
import aws_cdk.aws_events
import aws_cdk.aws_iam
import aws_cdk.core
import aws_cdk.cx_api
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/app-delivery", "0.36.0", __name__, "app-delivery@0.36.0.jsii.tgz")
@jsii.implements(aws_cdk.aws_codepipeline.IAction)
class PipelineDeployStackAction(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/app-delivery.PipelineDeployStackAction"):
    """A class to deploy a stack that is part of a CDK App, using CodePipeline. This composite Action takes care of preparing and executing a CloudFormation ChangeSet.

    It currently does *not* support stacks that make use of ``Asset``s, and
    requires the deployed stack is in the same account and region where the
    CodePipeline is hosted.

    Stability:
        experimental
    """
    def __init__(self, *, admin_permissions: bool, input: aws_cdk.aws_codepipeline.Artifact, stack: aws_cdk.core.Stack, capabilities: typing.Optional[typing.List[aws_cdk.aws_cloudformation.CloudFormationCapabilities]]=None, change_set_name: typing.Optional[str]=None, create_change_set_run_order: typing.Optional[jsii.Number]=None, execute_change_set_run_order: typing.Optional[jsii.Number]=None, role: typing.Optional[aws_cdk.aws_iam.IRole]=None) -> None:
        """
        Arguments:
            props: -
            admin_permissions: Whether to grant admin permissions to CloudFormation while deploying this template. Setting this to ``true`` affects the defaults for ``role`` and ``capabilities``, if you don't specify any alternatives. The default role that will be created for you will have admin (i.e., ``*``) permissions on all resources, and the deployment will have named IAM capabilities (i.e., able to create all IAM resources). This is a shorthand that you can use if you fully trust the templates that are deployed in this pipeline. If you want more fine-grained permissions, use ``addToRolePolicy`` and ``capabilities`` to control what the CloudFormation deployment is allowed to do.
            input: The CodePipeline artifact that holds the synthesized app, which is the contents of the ``<directory>`` when running ``cdk synth -o <directory>``.
            stack: The CDK stack to be deployed.
            capabilities: Acknowledge certain changes made as part of deployment. For stacks that contain certain resources, explicit acknowledgement that AWS CloudFormation might create or update those resources. For example, you must specify AnonymousIAM if your stack template contains AWS Identity and Access Management (IAM) resources. For more information Default: [AnonymousIAM, AutoExpand], unless ``adminPermissions`` is true
            change_set_name: The name to use when creating a ChangeSet for the stack. Default: CDK-CodePipeline-ChangeSet
            create_change_set_run_order: The runOrder for the CodePipeline action creating the ChangeSet. Default: 1
            execute_change_set_run_order: The runOrder for the CodePipeline action executing the ChangeSet. Default: ``createChangeSetRunOrder + 1``
            role: IAM role to assume when deploying changes. If not specified, a fresh role is created. The role is created with zero permissions unless ``adminPermissions`` is true, in which case the role will have admin permissions. Default: A fresh role with admin or no permissions (depending on the value of ``adminPermissions``).

        Stability:
            experimental
        """
        props: PipelineDeployStackActionProps = {"adminPermissions": admin_permissions, "input": input, "stack": stack}

        if capabilities is not None:
            props["capabilities"] = capabilities

        if change_set_name is not None:
            props["changeSetName"] = change_set_name

        if create_change_set_run_order is not None:
            props["createChangeSetRunOrder"] = create_change_set_run_order

        if execute_change_set_run_order is not None:
            props["executeChangeSetRunOrder"] = execute_change_set_run_order

        if role is not None:
            props["role"] = role

        jsii.create(PipelineDeployStackAction, self, [props])

    @jsii.member(jsii_name="addToDeploymentRolePolicy")
    def add_to_deployment_role_policy(self, statement: aws_cdk.aws_iam.PolicyStatement) -> None:
        """Add policy statements to the role deploying the stack.

        This role is passed to CloudFormation and must have the IAM permissions
        necessary to deploy the stack or you can grant this role ``adminPermissions``
        by using that option during creation. If you do not grant
        ``adminPermissions`` you need to identify the proper statements to add to
        this role based on the CloudFormation Resources in your stack.

        Arguments:
            statement: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addToDeploymentRolePolicy", [statement])

    @jsii.member(jsii_name="bind")
    def bind(self, scope: aws_cdk.core.Construct, stage: aws_cdk.aws_codepipeline.IStage, *, role: aws_cdk.aws_iam.IRole) -> aws_cdk.aws_codepipeline.ActionConfig:
        """
        Arguments:
            scope: -
            stage: -
            options: -
            role: 

        Stability:
            experimental
        """
        options: aws_cdk.aws_codepipeline.ActionBindOptions = {"role": role}

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

    @property
    @jsii.member(jsii_name="actionProperties")
    def action_properties(self) -> aws_cdk.aws_codepipeline.ActionProperties:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "actionProperties")

    @property
    @jsii.member(jsii_name="deploymentRole")
    def deployment_role(self) -> aws_cdk.aws_iam.IRole:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "deploymentRole")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _PipelineDeployStackActionProps(jsii.compat.TypedDict, total=False):
    capabilities: typing.List[aws_cdk.aws_cloudformation.CloudFormationCapabilities]
    """Acknowledge certain changes made as part of deployment.

    For stacks that contain certain resources, explicit acknowledgement that AWS CloudFormation
    might create or update those resources. For example, you must specify AnonymousIAM if your
    stack template contains AWS Identity and Access Management (IAM) resources. For more
    information

    Default:
        [AnonymousIAM, AutoExpand], unless ``adminPermissions`` is true

    See:
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-iam-template.html#using-iam-capabilities
    Stability:
        experimental
    """
    changeSetName: str
    """The name to use when creating a ChangeSet for the stack.

    Default:
        CDK-CodePipeline-ChangeSet

    Stability:
        experimental
    """
    createChangeSetRunOrder: jsii.Number
    """The runOrder for the CodePipeline action creating the ChangeSet.

    Default:
        1

    Stability:
        experimental
    """
    executeChangeSetRunOrder: jsii.Number
    """The runOrder for the CodePipeline action executing the ChangeSet.

    Default:
        ``createChangeSetRunOrder + 1``

    Stability:
        experimental
    """
    role: aws_cdk.aws_iam.IRole
    """IAM role to assume when deploying changes.

    If not specified, a fresh role is created. The role is created with zero
    permissions unless ``adminPermissions`` is true, in which case the role will have
    admin permissions.

    Default:
        A fresh role with admin or no permissions (depending on the value of ``adminPermissions``).

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/app-delivery.PipelineDeployStackActionProps", jsii_struct_bases=[_PipelineDeployStackActionProps])
class PipelineDeployStackActionProps(_PipelineDeployStackActionProps):
    """
    Stability:
        experimental
    """
    adminPermissions: bool
    """Whether to grant admin permissions to CloudFormation while deploying this template.

    Setting this to ``true`` affects the defaults for ``role`` and ``capabilities``, if you
    don't specify any alternatives.

    The default role that will be created for you will have admin (i.e., ``*``)
    permissions on all resources, and the deployment will have named IAM
    capabilities (i.e., able to create all IAM resources).

    This is a shorthand that you can use if you fully trust the templates that
    are deployed in this pipeline. If you want more fine-grained permissions,
    use ``addToRolePolicy`` and ``capabilities`` to control what the CloudFormation
    deployment is allowed to do.

    Stability:
        experimental
    """

    input: aws_cdk.aws_codepipeline.Artifact
    """The CodePipeline artifact that holds the synthesized app, which is the contents of the ``<directory>`` when running ``cdk synth -o <directory>``.

    Stability:
        experimental
    """

    stack: aws_cdk.core.Stack
    """The CDK stack to be deployed.

    Stability:
        experimental
    """

__all__ = ["PipelineDeployStackAction", "PipelineDeployStackActionProps", "__jsii_assembly__"]

publication.publish()
