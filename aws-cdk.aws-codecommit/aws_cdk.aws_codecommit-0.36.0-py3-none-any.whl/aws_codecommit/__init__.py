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
import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-codecommit", "0.36.0", __name__, "aws-codecommit@0.36.0.jsii.tgz")
class CfnRepository(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codecommit.CfnRepository"):
    """A CloudFormation ``AWS::CodeCommit::Repository``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codecommit-repository.html
    Stability:
        stable
    cloudformationResource:
        AWS::CodeCommit::Repository
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, repository_name: str, code: typing.Optional[typing.Union[typing.Optional["CodeProperty"], typing.Optional[aws_cdk.core.IResolvable]]]=None, repository_description: typing.Optional[str]=None, triggers: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "RepositoryTriggerProperty"]]]]]=None) -> None:
        """Create a new ``AWS::CodeCommit::Repository``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            repository_name: ``AWS::CodeCommit::Repository.RepositoryName``.
            code: ``AWS::CodeCommit::Repository.Code``.
            repository_description: ``AWS::CodeCommit::Repository.RepositoryDescription``.
            triggers: ``AWS::CodeCommit::Repository.Triggers``.

        Stability:
            experimental
        """
        props: CfnRepositoryProps = {"repositoryName": repository_name}

        if code is not None:
            props["code"] = code

        if repository_description is not None:
            props["repositoryDescription"] = repository_description

        if triggers is not None:
            props["triggers"] = triggers

        jsii.create(CfnRepository, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "attrArn")

    @property
    @jsii.member(jsii_name="attrCloneUrlHttp")
    def attr_clone_url_http(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            CloneUrlHttp
        """
        return jsii.get(self, "attrCloneUrlHttp")

    @property
    @jsii.member(jsii_name="attrCloneUrlSsh")
    def attr_clone_url_ssh(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            CloneUrlSsh
        """
        return jsii.get(self, "attrCloneUrlSsh")

    @property
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Name
        """
        return jsii.get(self, "attrName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="repositoryName")
    def repository_name(self) -> str:
        """``AWS::CodeCommit::Repository.RepositoryName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codecommit-repository.html#cfn-codecommit-repository-repositoryname
        Stability:
            stable
        """
        return jsii.get(self, "repositoryName")

    @repository_name.setter
    def repository_name(self, value: str):
        return jsii.set(self, "repositoryName", value)

    @property
    @jsii.member(jsii_name="code")
    def code(self) -> typing.Optional[typing.Union[typing.Optional["CodeProperty"], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::CodeCommit::Repository.Code``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codecommit-repository.html#cfn-codecommit-repository-code
        Stability:
            stable
        """
        return jsii.get(self, "code")

    @code.setter
    def code(self, value: typing.Optional[typing.Union[typing.Optional["CodeProperty"], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "code", value)

    @property
    @jsii.member(jsii_name="repositoryDescription")
    def repository_description(self) -> typing.Optional[str]:
        """``AWS::CodeCommit::Repository.RepositoryDescription``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codecommit-repository.html#cfn-codecommit-repository-repositorydescription
        Stability:
            stable
        """
        return jsii.get(self, "repositoryDescription")

    @repository_description.setter
    def repository_description(self, value: typing.Optional[str]):
        return jsii.set(self, "repositoryDescription", value)

    @property
    @jsii.member(jsii_name="triggers")
    def triggers(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "RepositoryTriggerProperty"]]]]]:
        """``AWS::CodeCommit::Repository.Triggers``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codecommit-repository.html#cfn-codecommit-repository-triggers
        Stability:
            stable
        """
        return jsii.get(self, "triggers")

    @triggers.setter
    def triggers(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "RepositoryTriggerProperty"]]]]]):
        return jsii.set(self, "triggers", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-codecommit.CfnRepository.CodeProperty", jsii_struct_bases=[])
    class CodeProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codecommit-repository-code.html
        Stability:
            stable
        """
        s3: typing.Union[aws_cdk.core.IResolvable, "CfnRepository.S3Property"]
        """``CfnRepository.CodeProperty.S3``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codecommit-repository-code.html#cfn-codecommit-repository-code-s3
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codecommit.CfnRepository.RepositoryTriggerProperty", jsii_struct_bases=[])
    class RepositoryTriggerProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codecommit-repository-repositorytrigger.html
        Stability:
            stable
        """
        branches: typing.List[str]
        """``CfnRepository.RepositoryTriggerProperty.Branches``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codecommit-repository-repositorytrigger.html#cfn-codecommit-repository-repositorytrigger-branches
        Stability:
            stable
        """

        customData: str
        """``CfnRepository.RepositoryTriggerProperty.CustomData``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codecommit-repository-repositorytrigger.html#cfn-codecommit-repository-repositorytrigger-customdata
        Stability:
            stable
        """

        destinationArn: str
        """``CfnRepository.RepositoryTriggerProperty.DestinationArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codecommit-repository-repositorytrigger.html#cfn-codecommit-repository-repositorytrigger-destinationarn
        Stability:
            stable
        """

        events: typing.List[str]
        """``CfnRepository.RepositoryTriggerProperty.Events``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codecommit-repository-repositorytrigger.html#cfn-codecommit-repository-repositorytrigger-events
        Stability:
            stable
        """

        name: str
        """``CfnRepository.RepositoryTriggerProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codecommit-repository-repositorytrigger.html#cfn-codecommit-repository-repositorytrigger-name
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _S3Property(jsii.compat.TypedDict, total=False):
        objectVersion: str
        """``CfnRepository.S3Property.ObjectVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codecommit-repository-s3.html#cfn-codecommit-repository-s3-objectversion
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codecommit.CfnRepository.S3Property", jsii_struct_bases=[_S3Property])
    class S3Property(_S3Property):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codecommit-repository-s3.html
        Stability:
            stable
        """
        bucket: str
        """``CfnRepository.S3Property.Bucket``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codecommit-repository-s3.html#cfn-codecommit-repository-s3-bucket
        Stability:
            stable
        """

        key: str
        """``CfnRepository.S3Property.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codecommit-repository-s3.html#cfn-codecommit-repository-s3-key
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnRepositoryProps(jsii.compat.TypedDict, total=False):
    code: typing.Union["CfnRepository.CodeProperty", aws_cdk.core.IResolvable]
    """``AWS::CodeCommit::Repository.Code``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codecommit-repository.html#cfn-codecommit-repository-code
    Stability:
        stable
    """
    repositoryDescription: str
    """``AWS::CodeCommit::Repository.RepositoryDescription``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codecommit-repository.html#cfn-codecommit-repository-repositorydescription
    Stability:
        stable
    """
    triggers: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnRepository.RepositoryTriggerProperty"]]]
    """``AWS::CodeCommit::Repository.Triggers``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codecommit-repository.html#cfn-codecommit-repository-triggers
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-codecommit.CfnRepositoryProps", jsii_struct_bases=[_CfnRepositoryProps])
class CfnRepositoryProps(_CfnRepositoryProps):
    """Properties for defining a ``AWS::CodeCommit::Repository``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codecommit-repository.html
    Stability:
        stable
    """
    repositoryName: str
    """``AWS::CodeCommit::Repository.RepositoryName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codecommit-repository.html#cfn-codecommit-repository-repositoryname
    Stability:
        stable
    """

@jsii.interface(jsii_type="@aws-cdk/aws-codecommit.IRepository")
class IRepository(aws_cdk.core.IResource, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IRepositoryProxy

    @property
    @jsii.member(jsii_name="repositoryArn")
    def repository_arn(self) -> str:
        """The ARN of this Repository.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="repositoryCloneUrlHttp")
    def repository_clone_url_http(self) -> str:
        """The HTTP clone URL.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="repositoryCloneUrlSsh")
    def repository_clone_url_ssh(self) -> str:
        """The SSH clone URL.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="repositoryName")
    def repository_name(self) -> str:
        """The human-visible name of this Repository.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @jsii.member(jsii_name="onCommentOnCommit")
    def on_comment_on_commit(self, id: str, *, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers when a comment is made on a commit.

        Arguments:
            id: -
            options: -
            description: A description of the rule's purpose. Default: - No description
            event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
            rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
            target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="onCommentOnPullRequest")
    def on_comment_on_pull_request(self, id: str, *, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers when a comment is made on a pull request.

        Arguments:
            id: -
            options: -
            description: A description of the rule's purpose. Default: - No description
            event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
            rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
            target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="onCommit")
    def on_commit(self, id: str, *, branches: typing.Optional[typing.List[str]]=None, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers when a commit is pushed to a branch.

        Arguments:
            id: -
            options: -
            branches: The branch to monitor. Default: - All branches
            description: A description of the rule's purpose. Default: - No description
            event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
            rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
            target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="onEvent")
    def on_event(self, id: str, *, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers for repository events.

        Use
        ``rule.addEventPattern(pattern)`` to specify a filter.

        Arguments:
            id: -
            options: -
            description: A description of the rule's purpose. Default: - No description
            event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
            rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
            target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="onPullRequestStateChange")
    def on_pull_request_state_change(self, id: str, *, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers when a pull request state is changed.

        Arguments:
            id: -
            options: -
            description: A description of the rule's purpose. Default: - No description
            event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
            rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
            target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="onReferenceCreated")
    def on_reference_created(self, id: str, *, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers when a reference is created (i.e. a new branch/tag is created) to the repository.

        Arguments:
            id: -
            options: -
            description: A description of the rule's purpose. Default: - No description
            event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
            rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
            target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="onReferenceDeleted")
    def on_reference_deleted(self, id: str, *, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers when a reference is delete (i.e. a branch/tag is deleted) from the repository.

        Arguments:
            id: -
            options: -
            description: A description of the rule's purpose. Default: - No description
            event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
            rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
            target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="onReferenceUpdated")
    def on_reference_updated(self, id: str, *, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers when a reference is updated (i.e. a commit is pushed to an existing or new branch) from the repository.

        Arguments:
            id: -
            options: -
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
        """Defines a CloudWatch event rule which triggers when a "CodeCommit Repository State Change" event occurs.

        Arguments:
            id: -
            options: -
            description: A description of the rule's purpose. Default: - No description
            event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
            rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
            target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        Stability:
            experimental
        """
        ...


class _IRepositoryProxy(jsii.proxy_for(aws_cdk.core.IResource)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-codecommit.IRepository"
    @property
    @jsii.member(jsii_name="repositoryArn")
    def repository_arn(self) -> str:
        """The ARN of this Repository.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "repositoryArn")

    @property
    @jsii.member(jsii_name="repositoryCloneUrlHttp")
    def repository_clone_url_http(self) -> str:
        """The HTTP clone URL.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "repositoryCloneUrlHttp")

    @property
    @jsii.member(jsii_name="repositoryCloneUrlSsh")
    def repository_clone_url_ssh(self) -> str:
        """The SSH clone URL.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "repositoryCloneUrlSsh")

    @property
    @jsii.member(jsii_name="repositoryName")
    def repository_name(self) -> str:
        """The human-visible name of this Repository.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "repositoryName")

    @jsii.member(jsii_name="onCommentOnCommit")
    def on_comment_on_commit(self, id: str, *, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers when a comment is made on a commit.

        Arguments:
            id: -
            options: -
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

        return jsii.invoke(self, "onCommentOnCommit", [id, options])

    @jsii.member(jsii_name="onCommentOnPullRequest")
    def on_comment_on_pull_request(self, id: str, *, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers when a comment is made on a pull request.

        Arguments:
            id: -
            options: -
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

        return jsii.invoke(self, "onCommentOnPullRequest", [id, options])

    @jsii.member(jsii_name="onCommit")
    def on_commit(self, id: str, *, branches: typing.Optional[typing.List[str]]=None, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers when a commit is pushed to a branch.

        Arguments:
            id: -
            options: -
            branches: The branch to monitor. Default: - All branches
            description: A description of the rule's purpose. Default: - No description
            event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
            rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
            target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        Stability:
            experimental
        """
        options: OnCommitOptions = {}

        if branches is not None:
            options["branches"] = branches

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        if target is not None:
            options["target"] = target

        return jsii.invoke(self, "onCommit", [id, options])

    @jsii.member(jsii_name="onEvent")
    def on_event(self, id: str, *, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers for repository events.

        Use
        ``rule.addEventPattern(pattern)`` to specify a filter.

        Arguments:
            id: -
            options: -
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

    @jsii.member(jsii_name="onPullRequestStateChange")
    def on_pull_request_state_change(self, id: str, *, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers when a pull request state is changed.

        Arguments:
            id: -
            options: -
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

        return jsii.invoke(self, "onPullRequestStateChange", [id, options])

    @jsii.member(jsii_name="onReferenceCreated")
    def on_reference_created(self, id: str, *, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers when a reference is created (i.e. a new branch/tag is created) to the repository.

        Arguments:
            id: -
            options: -
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

        return jsii.invoke(self, "onReferenceCreated", [id, options])

    @jsii.member(jsii_name="onReferenceDeleted")
    def on_reference_deleted(self, id: str, *, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers when a reference is delete (i.e. a branch/tag is deleted) from the repository.

        Arguments:
            id: -
            options: -
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

        return jsii.invoke(self, "onReferenceDeleted", [id, options])

    @jsii.member(jsii_name="onReferenceUpdated")
    def on_reference_updated(self, id: str, *, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers when a reference is updated (i.e. a commit is pushed to an existing or new branch) from the repository.

        Arguments:
            id: -
            options: -
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

        return jsii.invoke(self, "onReferenceUpdated", [id, options])

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(self, id: str, *, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers when a "CodeCommit Repository State Change" event occurs.

        Arguments:
            id: -
            options: -
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


@jsii.data_type(jsii_type="@aws-cdk/aws-codecommit.OnCommitOptions", jsii_struct_bases=[aws_cdk.aws_events.OnEventOptions])
class OnCommitOptions(aws_cdk.aws_events.OnEventOptions, jsii.compat.TypedDict, total=False):
    """Options for the onCommit() method.

    Stability:
        experimental
    """
    branches: typing.List[str]
    """The branch to monitor.

    Default:
        - All branches

    Stability:
        experimental
    """

class ReferenceEvent(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codecommit.ReferenceEvent"):
    """Fields of CloudWatch Events that change references.

    See:
        https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/EventTypes.html#codebuild_event_type
    Stability:
        experimental
    """
    @classproperty
    @jsii.member(jsii_name="commitId")
    def commit_id(cls) -> str:
        """Commit id this reference now points to.

        Stability:
            experimental
        """
        return jsii.sget(cls, "commitId")

    @classproperty
    @jsii.member(jsii_name="eventType")
    def event_type(cls) -> str:
        """The type of reference event.

        'referenceCreated', 'referenceUpdated' or 'referenceDeleted'

        Stability:
            experimental
        """
        return jsii.sget(cls, "eventType")

    @classproperty
    @jsii.member(jsii_name="referenceFullName")
    def reference_full_name(cls) -> str:
        """Full reference name.

        For example, 'refs/tags/myTag'

        Stability:
            experimental
        """
        return jsii.sget(cls, "referenceFullName")

    @classproperty
    @jsii.member(jsii_name="referenceName")
    def reference_name(cls) -> str:
        """Name of reference changed (branch or tag name).

        Stability:
            experimental
        """
        return jsii.sget(cls, "referenceName")

    @classproperty
    @jsii.member(jsii_name="referenceType")
    def reference_type(cls) -> str:
        """Type of reference changed.

        'branch' or 'tag'

        Stability:
            experimental
        """
        return jsii.sget(cls, "referenceType")

    @classproperty
    @jsii.member(jsii_name="repositoryId")
    def repository_id(cls) -> str:
        """Id of the CodeCommit repository.

        Stability:
            experimental
        """
        return jsii.sget(cls, "repositoryId")

    @classproperty
    @jsii.member(jsii_name="repositoryName")
    def repository_name(cls) -> str:
        """Name of the CodeCommit repository.

        Stability:
            experimental
        """
        return jsii.sget(cls, "repositoryName")


@jsii.implements(IRepository)
class Repository(aws_cdk.core.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codecommit.Repository"):
    """Provides a CodeCommit Repository.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, repository_name: str, description: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            repository_name: Name of the repository. This property is required for all CodeCommit repositories.
            description: A description of the repository. Use the description to identify the purpose of the repository. Default: - No description.

        Stability:
            experimental
        """
        props: RepositoryProps = {"repositoryName": repository_name}

        if description is not None:
            props["description"] = description

        jsii.create(Repository, self, [scope, id, props])

    @jsii.member(jsii_name="fromRepositoryArn")
    @classmethod
    def from_repository_arn(cls, scope: aws_cdk.core.Construct, id: str, repository_arn: str) -> "IRepository":
        """Imports a codecommit repository.

        Arguments:
            scope: -
            id: -
            repository_arn: (e.g. ``arn:aws:codecommit:us-east-1:123456789012:MyDemoRepo``).

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromRepositoryArn", [scope, id, repository_arn])

    @jsii.member(jsii_name="fromRepositoryName")
    @classmethod
    def from_repository_name(cls, scope: aws_cdk.core.Construct, id: str, repository_name: str) -> "IRepository":
        """
        Arguments:
            scope: -
            id: -
            repository_name: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromRepositoryName", [scope, id, repository_name])

    @jsii.member(jsii_name="notify")
    def notify(self, arn: str, *, branches: typing.Optional[typing.List[str]]=None, custom_data: typing.Optional[str]=None, events: typing.Optional[typing.List["RepositoryEventTrigger"]]=None, name: typing.Optional[str]=None) -> "Repository":
        """Create a trigger to notify another service to run actions on repository events.

        Arguments:
            arn: Arn of the resource that repository events will notify.
            options: Trigger options to run actions.
            branches: The names of the branches in the AWS CodeCommit repository that contain events that you want to include in the trigger. If you don't specify at least one branch, the trigger applies to all branches.
            custom_data: When an event is triggered, additional information that AWS CodeCommit includes when it sends information to the target.
            events: The repository events for which AWS CodeCommit sends information to the target, which you specified in the DestinationArn property.If you don't specify events, the trigger runs for all repository events.
            name: A name for the trigger.Triggers on a repository must have unique names.

        Stability:
            experimental
        """
        options: RepositoryTriggerOptions = {}

        if branches is not None:
            options["branches"] = branches

        if custom_data is not None:
            options["customData"] = custom_data

        if events is not None:
            options["events"] = events

        if name is not None:
            options["name"] = name

        return jsii.invoke(self, "notify", [arn, options])

    @jsii.member(jsii_name="onCommentOnCommit")
    def on_comment_on_commit(self, id: str, *, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers when a comment is made on a commit.

        Arguments:
            id: -
            options: -
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

        return jsii.invoke(self, "onCommentOnCommit", [id, options])

    @jsii.member(jsii_name="onCommentOnPullRequest")
    def on_comment_on_pull_request(self, id: str, *, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers when a comment is made on a pull request.

        Arguments:
            id: -
            options: -
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

        return jsii.invoke(self, "onCommentOnPullRequest", [id, options])

    @jsii.member(jsii_name="onCommit")
    def on_commit(self, id: str, *, branches: typing.Optional[typing.List[str]]=None, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers when a commit is pushed to a branch.

        Arguments:
            id: -
            options: -
            branches: The branch to monitor. Default: - All branches
            description: A description of the rule's purpose. Default: - No description
            event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
            rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
            target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        Stability:
            experimental
        """
        options: OnCommitOptions = {}

        if branches is not None:
            options["branches"] = branches

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        if target is not None:
            options["target"] = target

        return jsii.invoke(self, "onCommit", [id, options])

    @jsii.member(jsii_name="onEvent")
    def on_event(self, id: str, *, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers for repository events.

        Use
        ``rule.addEventPattern(pattern)`` to specify a filter.

        Arguments:
            id: -
            options: -
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

    @jsii.member(jsii_name="onPullRequestStateChange")
    def on_pull_request_state_change(self, id: str, *, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers when a pull request state is changed.

        Arguments:
            id: -
            options: -
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

        return jsii.invoke(self, "onPullRequestStateChange", [id, options])

    @jsii.member(jsii_name="onReferenceCreated")
    def on_reference_created(self, id: str, *, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers when a reference is created (i.e. a new branch/tag is created) to the repository.

        Arguments:
            id: -
            options: -
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

        return jsii.invoke(self, "onReferenceCreated", [id, options])

    @jsii.member(jsii_name="onReferenceDeleted")
    def on_reference_deleted(self, id: str, *, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers when a reference is delete (i.e. a branch/tag is deleted) from the repository.

        Arguments:
            id: -
            options: -
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

        return jsii.invoke(self, "onReferenceDeleted", [id, options])

    @jsii.member(jsii_name="onReferenceUpdated")
    def on_reference_updated(self, id: str, *, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers when a reference is updated (i.e. a commit is pushed to an existing or new branch) from the repository.

        Arguments:
            id: -
            options: -
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

        return jsii.invoke(self, "onReferenceUpdated", [id, options])

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(self, id: str, *, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers when a "CodeCommit Repository State Change" event occurs.

        Arguments:
            id: -
            options: -
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

    @property
    @jsii.member(jsii_name="repositoryArn")
    def repository_arn(self) -> str:
        """The ARN of this Repository.

        Stability:
            experimental
        """
        return jsii.get(self, "repositoryArn")

    @property
    @jsii.member(jsii_name="repositoryCloneUrlHttp")
    def repository_clone_url_http(self) -> str:
        """The HTTP clone URL.

        Stability:
            experimental
        """
        return jsii.get(self, "repositoryCloneUrlHttp")

    @property
    @jsii.member(jsii_name="repositoryCloneUrlSsh")
    def repository_clone_url_ssh(self) -> str:
        """The SSH clone URL.

        Stability:
            experimental
        """
        return jsii.get(self, "repositoryCloneUrlSsh")

    @property
    @jsii.member(jsii_name="repositoryName")
    def repository_name(self) -> str:
        """The human-visible name of this Repository.

        Stability:
            experimental
        """
        return jsii.get(self, "repositoryName")


@jsii.enum(jsii_type="@aws-cdk/aws-codecommit.RepositoryEventTrigger")
class RepositoryEventTrigger(enum.Enum):
    """Repository events that will cause the trigger to run actions in another service.

    Stability:
        experimental
    """
    ALL = "ALL"
    """
    Stability:
        experimental
    """
    UPDATE_REF = "UPDATE_REF"
    """
    Stability:
        experimental
    """
    CREATE_REF = "CREATE_REF"
    """
    Stability:
        experimental
    """
    DELETE_REF = "DELETE_REF"
    """
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _RepositoryProps(jsii.compat.TypedDict, total=False):
    description: str
    """A description of the repository.

    Use the description to identify the
    purpose of the repository.

    Default:
        - No description.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-codecommit.RepositoryProps", jsii_struct_bases=[_RepositoryProps])
class RepositoryProps(_RepositoryProps):
    """
    Stability:
        experimental
    """
    repositoryName: str
    """Name of the repository.

    This property is required for all CodeCommit repositories.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-codecommit.RepositoryTriggerOptions", jsii_struct_bases=[])
class RepositoryTriggerOptions(jsii.compat.TypedDict, total=False):
    """Creates for a repository trigger to an SNS topic or Lambda function.

    Stability:
        experimental
    """
    branches: typing.List[str]
    """The names of the branches in the AWS CodeCommit repository that contain events that you want to include in the trigger.

    If you don't specify at
    least one branch, the trigger applies to all branches.

    Stability:
        experimental
    """

    customData: str
    """When an event is triggered, additional information that AWS CodeCommit includes when it sends information to the target.

    Stability:
        experimental
    """

    events: typing.List["RepositoryEventTrigger"]
    """The repository events for which AWS CodeCommit sends information to the target, which you specified in the DestinationArn property.If you don't specify events, the trigger runs for all repository events.

    Stability:
        experimental
    """

    name: str
    """A name for the trigger.Triggers on a repository must have unique names.

    Stability:
        experimental
    """

__all__ = ["CfnRepository", "CfnRepositoryProps", "IRepository", "OnCommitOptions", "ReferenceEvent", "Repository", "RepositoryEventTrigger", "RepositoryProps", "RepositoryTriggerOptions", "__jsii_assembly__"]

publication.publish()
