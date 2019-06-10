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
import aws_cdk.aws_iam
import aws_cdk.cdk
import aws_cdk.cx_api
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/app-delivery", "0.34.0", __name__, "app-delivery@0.34.0.jsii.tgz")
class PipelineDeployStackAction(aws_cdk.cdk.Construct, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/app-delivery.PipelineDeployStackAction"):
    """A Construct to deploy a stack that is part of a CDK App, using CodePipeline. This composite Action takes care of preparing and executing a CloudFormation ChangeSet.

    It currently does *not* support stacks that make use of ``Asset``s, and
    requires the deployed stack is in the same account and region where the
    CodePipeline is hosted.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, admin_permissions: bool, input: aws_cdk.aws_codepipeline.Artifact, stack: aws_cdk.cdk.Stack, stage: aws_cdk.aws_codepipeline.IStage, capabilities: typing.Optional[aws_cdk.aws_cloudformation.CloudFormationCapabilities]=None, change_set_name: typing.Optional[str]=None, create_change_set_run_order: typing.Optional[jsii.Number]=None, execute_change_set_run_order: typing.Optional[jsii.Number]=None, role: typing.Optional[aws_cdk.aws_iam.IRole]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            adminPermissions: Whether to grant admin permissions to CloudFormation while deploying this template. Setting this to ``true`` affects the defaults for ``role`` and ``capabilities``, if you don't specify any alternatives. The default role that will be created for you will have admin (i.e., ``*``) permissions on all resources, and the deployment will have named IAM capabilities (i.e., able to create all IAM resources). This is a shorthand that you can use if you fully trust the templates that are deployed in this pipeline. If you want more fine-grained permissions, use ``addToRolePolicy`` and ``capabilities`` to control what the CloudFormation deployment is allowed to do.
            input: The CodePipeline artifact that holds the synthesized app, which is the contents of the ``<directory>`` when running ``cdk synth -o <directory>``.
            stack: The CDK stack to be deployed.
            stage: The CodePipeline stage in which to perform the deployment.
            capabilities: Acknowledge certain changes made as part of deployment. For stacks that contain certain resources, explicit acknowledgement that AWS CloudFormation might create or update those resources. For example, you must specify AnonymousIAM if your stack template contains AWS Identity and Access Management (IAM) resources. For more information Default: AnonymousIAM, unless ``adminPermissions`` is true
            changeSetName: The name to use when creating a ChangeSet for the stack. Default: CDK-CodePipeline-ChangeSet
            createChangeSetRunOrder: The runOrder for the CodePipeline action creating the ChangeSet. Default: 1
            executeChangeSetRunOrder: The runOrder for the CodePipeline action executing the ChangeSet. Default: ``createChangeSetRunOrder + 1``
            role: IAM role to assume when deploying changes. If not specified, a fresh role is created. The role is created with zero permissions unless ``adminPermissions`` is true, in which case the role will have admin permissions. Default: A fresh role with admin or no permissions (depending on the value of ``adminPermissions``).

        Stability:
            experimental
        """
        props: PipelineDeployStackActionProps = {"adminPermissions": admin_permissions, "input": input, "stack": stack, "stage": stage}

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

        jsii.create(PipelineDeployStackAction, self, [scope, id, props])

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

    @jsii.member(jsii_name="validate")
    def _validate(self) -> typing.List[str]:
        """Validate the current construct.

        This method can be implemented by derived constructs in order to perform
        validation logic. It is called on all constructs before synthesis.

        Stability:
            experimental
        """
        return jsii.invoke(self, "validate", [])

    @property
    @jsii.member(jsii_name="deploymentRole")
    def deployment_role(self) -> aws_cdk.aws_iam.IRole:
        """The role used by CloudFormation for the deploy action.

        Stability:
            experimental
        """
        return jsii.get(self, "deploymentRole")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _PipelineDeployStackActionProps(jsii.compat.TypedDict, total=False):
    capabilities: aws_cdk.aws_cloudformation.CloudFormationCapabilities
    """Acknowledge certain changes made as part of deployment.

    For stacks that contain certain resources, explicit acknowledgement that AWS CloudFormation
    might create or update those resources. For example, you must specify AnonymousIAM if your
    stack template contains AWS Identity and Access Management (IAM) resources. For more
    information

    Default:
        AnonymousIAM, unless ``adminPermissions`` is true

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

    stack: aws_cdk.cdk.Stack
    """The CDK stack to be deployed.

    Stability:
        experimental
    """

    stage: aws_cdk.aws_codepipeline.IStage
    """The CodePipeline stage in which to perform the deployment.

    Stability:
        experimental
    """

__all__ = ["PipelineDeployStackAction", "PipelineDeployStackActionProps", "__jsii_assembly__"]

publication.publish()
