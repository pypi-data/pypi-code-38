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
import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-ecr", "0.34.0", __name__, "aws-ecr@0.34.0.jsii.tgz")
class CfnRepository(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ecr.CfnRepository"):
    """A CloudFormation ``AWS::ECR::Repository``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecr-repository.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ECR::Repository
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, lifecycle_policy: typing.Optional[typing.Union[typing.Optional["LifecyclePolicyProperty"], typing.Optional[aws_cdk.cdk.Token]]]=None, repository_name: typing.Optional[str]=None, repository_policy_text: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.Token]]]=None) -> None:
        """Create a new ``AWS::ECR::Repository``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            lifecyclePolicy: ``AWS::ECR::Repository.LifecyclePolicy``.
            repositoryName: ``AWS::ECR::Repository.RepositoryName``.
            repositoryPolicyText: ``AWS::ECR::Repository.RepositoryPolicyText``.

        Stability:
            experimental
        """
        props: CfnRepositoryProps = {}

        if lifecycle_policy is not None:
            props["lifecyclePolicy"] = lifecycle_policy

        if repository_name is not None:
            props["repositoryName"] = repository_name

        if repository_policy_text is not None:
            props["repositoryPolicyText"] = repository_policy_text

        jsii.create(CfnRepository, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnRepositoryProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="repositoryArn")
    def repository_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "repositoryArn")

    @property
    @jsii.member(jsii_name="repositoryName")
    def repository_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "repositoryName")

    @jsii.data_type(jsii_type="@aws-cdk/aws-ecr.CfnRepository.LifecyclePolicyProperty", jsii_struct_bases=[])
    class LifecyclePolicyProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecr-repository-lifecyclepolicy.html
        Stability:
            experimental
        """
        lifecyclePolicyText: str
        """``CfnRepository.LifecyclePolicyProperty.LifecyclePolicyText``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecr-repository-lifecyclepolicy.html#cfn-ecr-repository-lifecyclepolicy-lifecyclepolicytext
        Stability:
            experimental
        """

        registryId: str
        """``CfnRepository.LifecyclePolicyProperty.RegistryId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecr-repository-lifecyclepolicy.html#cfn-ecr-repository-lifecyclepolicy-registryid
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-ecr.CfnRepositoryProps", jsii_struct_bases=[])
class CfnRepositoryProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::ECR::Repository``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecr-repository.html
    Stability:
        experimental
    """
    lifecyclePolicy: typing.Union["CfnRepository.LifecyclePolicyProperty", aws_cdk.cdk.Token]
    """``AWS::ECR::Repository.LifecyclePolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecr-repository.html#cfn-ecr-repository-lifecyclepolicy
    Stability:
        experimental
    """

    repositoryName: str
    """``AWS::ECR::Repository.RepositoryName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecr-repository.html#cfn-ecr-repository-repositoryname
    Stability:
        experimental
    """

    repositoryPolicyText: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
    """``AWS::ECR::Repository.RepositoryPolicyText``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecr-repository.html#cfn-ecr-repository-repositorypolicytext
    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-ecr.CountType")
class CountType(enum.Enum):
    """Select images based on counts.

    Stability:
        experimental
    """
    ImageCountMoreThan = "ImageCountMoreThan"
    """Set a limit on the number of images in your repository.

    Stability:
        experimental
    """
    SinceImagePushed = "SinceImagePushed"
    """Set an age limit on the images in your repository.

    Stability:
        experimental
    """

@jsii.interface(jsii_type="@aws-cdk/aws-ecr.IRepository")
class IRepository(aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """Represents an ECR repository.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IRepositoryProxy

    @property
    @jsii.member(jsii_name="repositoryArn")
    def repository_arn(self) -> str:
        """The ARN of the repository.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="repositoryName")
    def repository_name(self) -> str:
        """The name of the repository.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="repositoryUri")
    def repository_uri(self) -> str:
        """The URI of this repository (represents the latest image):.

        ACCOUNT.dkr.ecr.REGION.amazonaws.com/REPOSITORY

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @jsii.member(jsii_name="addToResourcePolicy")
    def add_to_resource_policy(self, statement: aws_cdk.aws_iam.PolicyStatement) -> None:
        """Add a policy statement to the repository's resource policy.

        Arguments:
            statement: -

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="grant")
    def grant(self, grantee: aws_cdk.aws_iam.IGrantable, *actions: str) -> aws_cdk.aws_iam.Grant:
        """Grant the given principal identity permissions to perform the actions on this repository.

        Arguments:
            grantee: -
            actions: -

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="grantPull")
    def grant_pull(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grant the given identity permissions to pull images in this repository.

        Arguments:
            grantee: -

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="grantPullPush")
    def grant_pull_push(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grant the given identity permissions to pull and push images to this repository.

        Arguments:
            grantee: -

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="onCloudTrailEvent")
    def on_cloud_trail_event(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Define a CloudWatch event that triggers when something happens to this repository.

        Requires that there exists at least one CloudTrail Trail in your account
        that captures the event. This method will not create the Trail.

        Arguments:
            id: The id of the rule.
            options: Options for adding the rule.
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="onCloudTrailImagePushed")
    def on_cloud_trail_image_pushed(self, id: str, *, image_tag: typing.Optional[str]=None, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines an AWS CloudWatch event rule that can trigger a target when an image is pushed to this repository.

        Requires that there exists at least one CloudTrail Trail in your account
        that captures the event. This method will not create the Trail.

        Arguments:
            id: The id of the rule.
            options: Options for adding the rule.
            imageTag: Only watch changes to this image tag. Default: - Watch changes to all tags
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="repositoryUriForTag")
    def repository_uri_for_tag(self, tag: typing.Optional[str]=None) -> str:
        """Returns the URI of the repository for a certain tag. Can be used in ``docker push/pull``.

        ACCOUNT.dkr.ecr.REGION.amazonaws.com/REPOSITORY[:TAG]

        Arguments:
            tag: Image tag to use (tools usually default to "latest" if omitted).

        Stability:
            experimental
        """
        ...


class _IRepositoryProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
    """Represents an ECR repository.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-ecr.IRepository"
    @property
    @jsii.member(jsii_name="repositoryArn")
    def repository_arn(self) -> str:
        """The ARN of the repository.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "repositoryArn")

    @property
    @jsii.member(jsii_name="repositoryName")
    def repository_name(self) -> str:
        """The name of the repository.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "repositoryName")

    @property
    @jsii.member(jsii_name="repositoryUri")
    def repository_uri(self) -> str:
        """The URI of this repository (represents the latest image):.

        ACCOUNT.dkr.ecr.REGION.amazonaws.com/REPOSITORY

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "repositoryUri")

    @jsii.member(jsii_name="addToResourcePolicy")
    def add_to_resource_policy(self, statement: aws_cdk.aws_iam.PolicyStatement) -> None:
        """Add a policy statement to the repository's resource policy.

        Arguments:
            statement: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addToResourcePolicy", [statement])

    @jsii.member(jsii_name="grant")
    def grant(self, grantee: aws_cdk.aws_iam.IGrantable, *actions: str) -> aws_cdk.aws_iam.Grant:
        """Grant the given principal identity permissions to perform the actions on this repository.

        Arguments:
            grantee: -
            actions: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grant", [grantee, *actions])

    @jsii.member(jsii_name="grantPull")
    def grant_pull(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grant the given identity permissions to pull images in this repository.

        Arguments:
            grantee: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantPull", [grantee])

    @jsii.member(jsii_name="grantPullPush")
    def grant_pull_push(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grant the given identity permissions to pull and push images to this repository.

        Arguments:
            grantee: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantPullPush", [grantee])

    @jsii.member(jsii_name="onCloudTrailEvent")
    def on_cloud_trail_event(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Define a CloudWatch event that triggers when something happens to this repository.

        Requires that there exists at least one CloudTrail Trail in your account
        that captures the event. This method will not create the Trail.

        Arguments:
            id: The id of the rule.
            options: Options for adding the rule.
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

        return jsii.invoke(self, "onCloudTrailEvent", [id, options])

    @jsii.member(jsii_name="onCloudTrailImagePushed")
    def on_cloud_trail_image_pushed(self, id: str, *, image_tag: typing.Optional[str]=None, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines an AWS CloudWatch event rule that can trigger a target when an image is pushed to this repository.

        Requires that there exists at least one CloudTrail Trail in your account
        that captures the event. This method will not create the Trail.

        Arguments:
            id: The id of the rule.
            options: Options for adding the rule.
            imageTag: Only watch changes to this image tag. Default: - Watch changes to all tags
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        options: OnCloudTrailImagePushedOptions = {"target": target}

        if image_tag is not None:
            options["imageTag"] = image_tag

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        return jsii.invoke(self, "onCloudTrailImagePushed", [id, options])

    @jsii.member(jsii_name="repositoryUriForTag")
    def repository_uri_for_tag(self, tag: typing.Optional[str]=None) -> str:
        """Returns the URI of the repository for a certain tag. Can be used in ``docker push/pull``.

        ACCOUNT.dkr.ecr.REGION.amazonaws.com/REPOSITORY[:TAG]

        Arguments:
            tag: Image tag to use (tools usually default to "latest" if omitted).

        Stability:
            experimental
        """
        return jsii.invoke(self, "repositoryUriForTag", [tag])


@jsii.data_type(jsii_type="@aws-cdk/aws-ecr.LifecycleRule", jsii_struct_bases=[])
class LifecycleRule(jsii.compat.TypedDict, total=False):
    """An ECR life cycle rule.

    Stability:
        experimental
    """
    description: str
    """Describes the purpose of the rule.

    Default:
        No description

    Stability:
        experimental
    """

    maxImageAgeDays: jsii.Number
    """The maximum age of images to retain.

    Specify exactly one of maxImageCount and maxImageAgeDays.

    Stability:
        experimental
    """

    maxImageCount: jsii.Number
    """The maximum number of images to retain.

    Specify exactly one of maxImageCount and maxImageAgeDays.

    Stability:
        experimental
    """

    rulePriority: jsii.Number
    """Controls the order in which rules are evaluated (low to high).

    All rules must have a unique priority, where lower numbers have
    higher precedence. The first rule that matches is applied to an image.

    There can only be one rule with a tagStatus of Any, and it must have
    the highest rulePriority.

    All rules without a specified priority will have incrementing priorities
    automatically assigned to them, higher than any rules that DO have priorities.

    Default:
        Automatically assigned

    Stability:
        experimental
    """

    tagPrefixList: typing.List[str]
    """Select images that have ALL the given prefixes in their tag.

    Only if tagStatus == TagStatus.Tagged

    Stability:
        experimental
    """

    tagStatus: "TagStatus"
    """Select images based on tags.

    Only one rule is allowed to select untagged images, and it must
    have the highest rulePriority.

    Default:
        TagStatus.Tagged if tagPrefixList is given, TagStatus.Any otherwise

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ecr.OnCloudTrailImagePushedOptions", jsii_struct_bases=[aws_cdk.aws_events.OnEventOptions])
class OnCloudTrailImagePushedOptions(aws_cdk.aws_events.OnEventOptions, jsii.compat.TypedDict, total=False):
    """Options for the onCloudTrailImagePushed method.

    Stability:
        experimental
    """
    imageTag: str
    """Only watch changes to this image tag.

    Default:
        - Watch changes to all tags

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ecr.RepositoryAttributes", jsii_struct_bases=[])
class RepositoryAttributes(jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    repositoryArn: str
    """
    Stability:
        experimental
    """

    repositoryName: str
    """
    Stability:
        experimental
    """

@jsii.implements(IRepository)
class RepositoryBase(aws_cdk.cdk.Resource, metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/aws-ecr.RepositoryBase"):
    """Base class for ECR repository.

    Reused between imported repositories and owned repositories.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _RepositoryBaseProxy

    def __init__(self, scope: aws_cdk.cdk.Construct, id: str) -> None:
        """Creates a new construct node.

        Arguments:
            scope: The scope in which to define this construct.
            id: The scoped construct ID. Must be unique amongst siblings. If the ID includes a path separator (``/``), then it will be replaced by double dash ``--``.

        Stability:
            experimental
        """
        jsii.create(RepositoryBase, self, [scope, id])

    @jsii.member(jsii_name="addToResourcePolicy")
    @abc.abstractmethod
    def add_to_resource_policy(self, statement: aws_cdk.aws_iam.PolicyStatement) -> None:
        """Add a policy statement to the repository's resource policy.

        Arguments:
            statement: -

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="grant")
    def grant(self, grantee: aws_cdk.aws_iam.IGrantable, *actions: str) -> aws_cdk.aws_iam.Grant:
        """Grant the given principal identity permissions to perform the actions on this repository.

        Arguments:
            grantee: -
            actions: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grant", [grantee, *actions])

    @jsii.member(jsii_name="grantPull")
    def grant_pull(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grant the given identity permissions to use the images in this repository.

        Arguments:
            grantee: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantPull", [grantee])

    @jsii.member(jsii_name="grantPullPush")
    def grant_pull_push(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grant the given identity permissions to pull and push images to this repository.

        Arguments:
            grantee: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantPullPush", [grantee])

    @jsii.member(jsii_name="onCloudTrailEvent")
    def on_cloud_trail_event(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Define a CloudWatch event that triggers when something happens to this repository.

        Requires that there exists at least one CloudTrail Trail in your account
        that captures the event. This method will not create the Trail.

        Arguments:
            id: The id of the rule.
            options: Options for adding the rule.
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

        return jsii.invoke(self, "onCloudTrailEvent", [id, options])

    @jsii.member(jsii_name="onCloudTrailImagePushed")
    def on_cloud_trail_image_pushed(self, id: str, *, image_tag: typing.Optional[str]=None, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines an AWS CloudWatch event rule that can trigger a target when an image is pushed to this repository.

        Requires that there exists at least one CloudTrail Trail in your account
        that captures the event. This method will not create the Trail.

        Arguments:
            id: The id of the rule.
            options: Options for adding the rule.
            imageTag: Only watch changes to this image tag. Default: - Watch changes to all tags
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        options: OnCloudTrailImagePushedOptions = {"target": target}

        if image_tag is not None:
            options["imageTag"] = image_tag

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        return jsii.invoke(self, "onCloudTrailImagePushed", [id, options])

    @jsii.member(jsii_name="repositoryUriForTag")
    def repository_uri_for_tag(self, tag: typing.Optional[str]=None) -> str:
        """Returns the URL of the repository. Can be used in ``docker push/pull``.

        ACCOUNT.dkr.ecr.REGION.amazonaws.com/REPOSITORY[:TAG]

        Arguments:
            tag: Optional image tag.

        Stability:
            experimental
        """
        return jsii.invoke(self, "repositoryUriForTag", [tag])

    @property
    @jsii.member(jsii_name="repositoryArn")
    @abc.abstractmethod
    def repository_arn(self) -> str:
        """The ARN of the repository.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="repositoryName")
    @abc.abstractmethod
    def repository_name(self) -> str:
        """The name of the repository.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="repositoryUri")
    def repository_uri(self) -> str:
        """The URI of this repository (represents the latest image):.

        ACCOUNT.dkr.ecr.REGION.amazonaws.com/REPOSITORY

        Stability:
            experimental
        """
        return jsii.get(self, "repositoryUri")


class _RepositoryBaseProxy(RepositoryBase, jsii.proxy_for(aws_cdk.cdk.Resource)):
    @jsii.member(jsii_name="addToResourcePolicy")
    def add_to_resource_policy(self, statement: aws_cdk.aws_iam.PolicyStatement) -> None:
        """Add a policy statement to the repository's resource policy.

        Arguments:
            statement: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addToResourcePolicy", [statement])

    @property
    @jsii.member(jsii_name="repositoryArn")
    def repository_arn(self) -> str:
        """The ARN of the repository.

        Stability:
            experimental
        """
        return jsii.get(self, "repositoryArn")

    @property
    @jsii.member(jsii_name="repositoryName")
    def repository_name(self) -> str:
        """The name of the repository.

        Stability:
            experimental
        """
        return jsii.get(self, "repositoryName")


class Repository(RepositoryBase, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ecr.Repository"):
    """Define an ECR repository.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, lifecycle_registry_id: typing.Optional[str]=None, lifecycle_rules: typing.Optional[typing.List["LifecycleRule"]]=None, repository_name: typing.Optional[str]=None, retain: typing.Optional[bool]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            lifecycleRegistryId: The AWS account ID associated with the registry that contains the repository. Default: The default registry is assumed.
            lifecycleRules: Life cycle rules to apply to this registry. Default: No life cycle rules
            repositoryName: Name for this repository. Default: Automatically generated name.
            retain: Retain the repository on stack deletion. If you don't set this to true, the registry must be empty, otherwise your stack deletion will fail. Default: false

        Stability:
            experimental
        """
        props: RepositoryProps = {}

        if lifecycle_registry_id is not None:
            props["lifecycleRegistryId"] = lifecycle_registry_id

        if lifecycle_rules is not None:
            props["lifecycleRules"] = lifecycle_rules

        if repository_name is not None:
            props["repositoryName"] = repository_name

        if retain is not None:
            props["retain"] = retain

        jsii.create(Repository, self, [scope, id, props])

    @jsii.member(jsii_name="arnForLocalRepository")
    @classmethod
    def arn_for_local_repository(cls, repository_name: str, scope: aws_cdk.cdk.IConstruct) -> str:
        """Returns an ECR ARN for a repository that resides in the same account/region as the current stack.

        Arguments:
            repositoryName: -
            scope: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "arnForLocalRepository", [repository_name, scope])

    @jsii.member(jsii_name="fromRepositoryArn")
    @classmethod
    def from_repository_arn(cls, scope: aws_cdk.cdk.Construct, id: str, repository_arn: str) -> "IRepository":
        """
        Arguments:
            scope: -
            id: -
            repositoryArn: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromRepositoryArn", [scope, id, repository_arn])

    @jsii.member(jsii_name="fromRepositoryAttributes")
    @classmethod
    def from_repository_attributes(cls, scope: aws_cdk.cdk.Construct, id: str, *, repository_arn: str, repository_name: str) -> "IRepository":
        """Import a repository.

        Arguments:
            scope: -
            id: -
            attrs: -
            repositoryArn: 
            repositoryName: 

        Stability:
            experimental
        """
        attrs: RepositoryAttributes = {"repositoryArn": repository_arn, "repositoryName": repository_name}

        return jsii.sinvoke(cls, "fromRepositoryAttributes", [scope, id, attrs])

    @jsii.member(jsii_name="fromRepositoryName")
    @classmethod
    def from_repository_name(cls, scope: aws_cdk.cdk.Construct, id: str, repository_name: str) -> "IRepository":
        """
        Arguments:
            scope: -
            id: -
            repositoryName: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromRepositoryName", [scope, id, repository_name])

    @jsii.member(jsii_name="addLifecycleRule")
    def add_lifecycle_rule(self, *, description: typing.Optional[str]=None, max_image_age_days: typing.Optional[jsii.Number]=None, max_image_count: typing.Optional[jsii.Number]=None, rule_priority: typing.Optional[jsii.Number]=None, tag_prefix_list: typing.Optional[typing.List[str]]=None, tag_status: typing.Optional["TagStatus"]=None) -> None:
        """Add a life cycle rule to the repository.

        Life cycle rules automatically expire images from the repository that match
        certain conditions.

        Arguments:
            rule: -
            description: Describes the purpose of the rule. Default: No description
            maxImageAgeDays: The maximum age of images to retain. Specify exactly one of maxImageCount and maxImageAgeDays.
            maxImageCount: The maximum number of images to retain. Specify exactly one of maxImageCount and maxImageAgeDays.
            rulePriority: Controls the order in which rules are evaluated (low to high). All rules must have a unique priority, where lower numbers have higher precedence. The first rule that matches is applied to an image. There can only be one rule with a tagStatus of Any, and it must have the highest rulePriority. All rules without a specified priority will have incrementing priorities automatically assigned to them, higher than any rules that DO have priorities. Default: Automatically assigned
            tagPrefixList: Select images that have ALL the given prefixes in their tag. Only if tagStatus == TagStatus.Tagged
            tagStatus: Select images based on tags. Only one rule is allowed to select untagged images, and it must have the highest rulePriority. Default: TagStatus.Tagged if tagPrefixList is given, TagStatus.Any otherwise

        Stability:
            experimental
        """
        rule: LifecycleRule = {}

        if description is not None:
            rule["description"] = description

        if max_image_age_days is not None:
            rule["maxImageAgeDays"] = max_image_age_days

        if max_image_count is not None:
            rule["maxImageCount"] = max_image_count

        if rule_priority is not None:
            rule["rulePriority"] = rule_priority

        if tag_prefix_list is not None:
            rule["tagPrefixList"] = tag_prefix_list

        if tag_status is not None:
            rule["tagStatus"] = tag_status

        return jsii.invoke(self, "addLifecycleRule", [rule])

    @jsii.member(jsii_name="addToResourcePolicy")
    def add_to_resource_policy(self, statement: aws_cdk.aws_iam.PolicyStatement) -> None:
        """Add a policy statement to the repository's resource policy.

        Arguments:
            statement: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addToResourcePolicy", [statement])

    @property
    @jsii.member(jsii_name="repositoryArn")
    def repository_arn(self) -> str:
        """The ARN of the repository.

        Stability:
            experimental
        """
        return jsii.get(self, "repositoryArn")

    @property
    @jsii.member(jsii_name="repositoryName")
    def repository_name(self) -> str:
        """The name of the repository.

        Stability:
            experimental
        """
        return jsii.get(self, "repositoryName")


@jsii.data_type(jsii_type="@aws-cdk/aws-ecr.RepositoryProps", jsii_struct_bases=[])
class RepositoryProps(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    lifecycleRegistryId: str
    """The AWS account ID associated with the registry that contains the repository.

    Default:
        The default registry is assumed.

    See:
        https://docs.aws.amazon.com/AmazonECR/latest/APIReference/API_PutLifecyclePolicy.html
    Stability:
        experimental
    """

    lifecycleRules: typing.List["LifecycleRule"]
    """Life cycle rules to apply to this registry.

    Default:
        No life cycle rules

    Stability:
        experimental
    """

    repositoryName: str
    """Name for this repository.

    Default:
        Automatically generated name.

    Stability:
        experimental
    """

    retain: bool
    """Retain the repository on stack deletion.

    If you don't set this to true, the registry must be empty, otherwise
    your stack deletion will fail.

    Default:
        false

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-ecr.TagStatus")
class TagStatus(enum.Enum):
    """Select images based on tags.

    Stability:
        experimental
    """
    Any = "Any"
    """Rule applies to all images.

    Stability:
        experimental
    """
    Tagged = "Tagged"
    """Rule applies to tagged images.

    Stability:
        experimental
    """
    Untagged = "Untagged"
    """Rule applies to untagged images.

    Stability:
        experimental
    """

__all__ = ["CfnRepository", "CfnRepositoryProps", "CountType", "IRepository", "LifecycleRule", "OnCloudTrailImagePushedOptions", "Repository", "RepositoryAttributes", "RepositoryBase", "RepositoryProps", "TagStatus", "__jsii_assembly__"]

publication.publish()
