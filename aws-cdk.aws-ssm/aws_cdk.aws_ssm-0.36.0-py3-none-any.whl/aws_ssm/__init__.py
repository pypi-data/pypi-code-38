import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_iam
import aws_cdk.core
import aws_cdk.cx_api
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-ssm", "0.36.0", __name__, "aws-ssm@0.36.0.jsii.tgz")
class CfnAssociation(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ssm.CfnAssociation"):
    """A CloudFormation ``AWS::SSM::Association``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-association.html
    Stability:
        stable
    cloudformationResource:
        AWS::SSM::Association
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, association_name: typing.Optional[str]=None, document_version: typing.Optional[str]=None, instance_id: typing.Optional[str]=None, output_location: typing.Optional[typing.Union[typing.Optional["InstanceAssociationOutputLocationProperty"], typing.Optional[aws_cdk.core.IResolvable]]]=None, parameters: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,typing.Union[aws_cdk.core.IResolvable, "ParameterValuesProperty"]]]]]=None, schedule_expression: typing.Optional[str]=None, targets: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "TargetProperty"]]]]]=None) -> None:
        """Create a new ``AWS::SSM::Association``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::SSM::Association.Name``.
            association_name: ``AWS::SSM::Association.AssociationName``.
            document_version: ``AWS::SSM::Association.DocumentVersion``.
            instance_id: ``AWS::SSM::Association.InstanceId``.
            output_location: ``AWS::SSM::Association.OutputLocation``.
            parameters: ``AWS::SSM::Association.Parameters``.
            schedule_expression: ``AWS::SSM::Association.ScheduleExpression``.
            targets: ``AWS::SSM::Association.Targets``.

        Stability:
            experimental
        """
        props: CfnAssociationProps = {"name": name}

        if association_name is not None:
            props["associationName"] = association_name

        if document_version is not None:
            props["documentVersion"] = document_version

        if instance_id is not None:
            props["instanceId"] = instance_id

        if output_location is not None:
            props["outputLocation"] = output_location

        if parameters is not None:
            props["parameters"] = parameters

        if schedule_expression is not None:
            props["scheduleExpression"] = schedule_expression

        if targets is not None:
            props["targets"] = targets

        jsii.create(CfnAssociation, self, [scope, id, props])

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
        """``AWS::SSM::Association.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-association.html#cfn-ssm-association-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="associationName")
    def association_name(self) -> typing.Optional[str]:
        """``AWS::SSM::Association.AssociationName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-association.html#cfn-ssm-association-associationname
        Stability:
            stable
        """
        return jsii.get(self, "associationName")

    @association_name.setter
    def association_name(self, value: typing.Optional[str]):
        return jsii.set(self, "associationName", value)

    @property
    @jsii.member(jsii_name="documentVersion")
    def document_version(self) -> typing.Optional[str]:
        """``AWS::SSM::Association.DocumentVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-association.html#cfn-ssm-association-documentversion
        Stability:
            stable
        """
        return jsii.get(self, "documentVersion")

    @document_version.setter
    def document_version(self, value: typing.Optional[str]):
        return jsii.set(self, "documentVersion", value)

    @property
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> typing.Optional[str]:
        """``AWS::SSM::Association.InstanceId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-association.html#cfn-ssm-association-instanceid
        Stability:
            stable
        """
        return jsii.get(self, "instanceId")

    @instance_id.setter
    def instance_id(self, value: typing.Optional[str]):
        return jsii.set(self, "instanceId", value)

    @property
    @jsii.member(jsii_name="outputLocation")
    def output_location(self) -> typing.Optional[typing.Union[typing.Optional["InstanceAssociationOutputLocationProperty"], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::SSM::Association.OutputLocation``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-association.html#cfn-ssm-association-outputlocation
        Stability:
            stable
        """
        return jsii.get(self, "outputLocation")

    @output_location.setter
    def output_location(self, value: typing.Optional[typing.Union[typing.Optional["InstanceAssociationOutputLocationProperty"], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "outputLocation", value)

    @property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,typing.Union[aws_cdk.core.IResolvable, "ParameterValuesProperty"]]]]]:
        """``AWS::SSM::Association.Parameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-association.html#cfn-ssm-association-parameters
        Stability:
            stable
        """
        return jsii.get(self, "parameters")

    @parameters.setter
    def parameters(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,typing.Union[aws_cdk.core.IResolvable, "ParameterValuesProperty"]]]]]):
        return jsii.set(self, "parameters", value)

    @property
    @jsii.member(jsii_name="scheduleExpression")
    def schedule_expression(self) -> typing.Optional[str]:
        """``AWS::SSM::Association.ScheduleExpression``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-association.html#cfn-ssm-association-scheduleexpression
        Stability:
            stable
        """
        return jsii.get(self, "scheduleExpression")

    @schedule_expression.setter
    def schedule_expression(self, value: typing.Optional[str]):
        return jsii.set(self, "scheduleExpression", value)

    @property
    @jsii.member(jsii_name="targets")
    def targets(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "TargetProperty"]]]]]:
        """``AWS::SSM::Association.Targets``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-association.html#cfn-ssm-association-targets
        Stability:
            stable
        """
        return jsii.get(self, "targets")

    @targets.setter
    def targets(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "TargetProperty"]]]]]):
        return jsii.set(self, "targets", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnAssociation.InstanceAssociationOutputLocationProperty", jsii_struct_bases=[])
    class InstanceAssociationOutputLocationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-association-instanceassociationoutputlocation.html
        Stability:
            stable
        """
        s3Location: typing.Union[aws_cdk.core.IResolvable, "CfnAssociation.S3OutputLocationProperty"]
        """``CfnAssociation.InstanceAssociationOutputLocationProperty.S3Location``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-association-instanceassociationoutputlocation.html#cfn-ssm-association-instanceassociationoutputlocation-s3location
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnAssociation.ParameterValuesProperty", jsii_struct_bases=[])
    class ParameterValuesProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-association-parametervalues.html
        Stability:
            stable
        """
        parameterValues: typing.List[str]
        """``CfnAssociation.ParameterValuesProperty.ParameterValues``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-association-parametervalues.html#cfn-ssm-association-parametervalues-parametervalues
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnAssociation.S3OutputLocationProperty", jsii_struct_bases=[])
    class S3OutputLocationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-association-s3outputlocation.html
        Stability:
            stable
        """
        outputS3BucketName: str
        """``CfnAssociation.S3OutputLocationProperty.OutputS3BucketName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-association-s3outputlocation.html#cfn-ssm-association-s3outputlocation-outputs3bucketname
        Stability:
            stable
        """

        outputS3KeyPrefix: str
        """``CfnAssociation.S3OutputLocationProperty.OutputS3KeyPrefix``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-association-s3outputlocation.html#cfn-ssm-association-s3outputlocation-outputs3keyprefix
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnAssociation.TargetProperty", jsii_struct_bases=[])
    class TargetProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-association-target.html
        Stability:
            stable
        """
        key: str
        """``CfnAssociation.TargetProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-association-target.html#cfn-ssm-association-target-key
        Stability:
            stable
        """

        values: typing.List[str]
        """``CfnAssociation.TargetProperty.Values``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-association-target.html#cfn-ssm-association-target-values
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnAssociationProps(jsii.compat.TypedDict, total=False):
    associationName: str
    """``AWS::SSM::Association.AssociationName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-association.html#cfn-ssm-association-associationname
    Stability:
        stable
    """
    documentVersion: str
    """``AWS::SSM::Association.DocumentVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-association.html#cfn-ssm-association-documentversion
    Stability:
        stable
    """
    instanceId: str
    """``AWS::SSM::Association.InstanceId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-association.html#cfn-ssm-association-instanceid
    Stability:
        stable
    """
    outputLocation: typing.Union["CfnAssociation.InstanceAssociationOutputLocationProperty", aws_cdk.core.IResolvable]
    """``AWS::SSM::Association.OutputLocation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-association.html#cfn-ssm-association-outputlocation
    Stability:
        stable
    """
    parameters: typing.Union[aws_cdk.core.IResolvable, typing.Mapping[str,typing.Union[aws_cdk.core.IResolvable, "CfnAssociation.ParameterValuesProperty"]]]
    """``AWS::SSM::Association.Parameters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-association.html#cfn-ssm-association-parameters
    Stability:
        stable
    """
    scheduleExpression: str
    """``AWS::SSM::Association.ScheduleExpression``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-association.html#cfn-ssm-association-scheduleexpression
    Stability:
        stable
    """
    targets: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnAssociation.TargetProperty"]]]
    """``AWS::SSM::Association.Targets``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-association.html#cfn-ssm-association-targets
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnAssociationProps", jsii_struct_bases=[_CfnAssociationProps])
class CfnAssociationProps(_CfnAssociationProps):
    """Properties for defining a ``AWS::SSM::Association``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-association.html
    Stability:
        stable
    """
    name: str
    """``AWS::SSM::Association.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-association.html#cfn-ssm-association-name
    Stability:
        stable
    """

class CfnDocument(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ssm.CfnDocument"):
    """A CloudFormation ``AWS::SSM::Document``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-document.html
    Stability:
        stable
    cloudformationResource:
        AWS::SSM::Document
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, content: typing.Any, document_type: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::SSM::Document``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            content: ``AWS::SSM::Document.Content``.
            document_type: ``AWS::SSM::Document.DocumentType``.
            tags: ``AWS::SSM::Document.Tags``.

        Stability:
            experimental
        """
        props: CfnDocumentProps = {"content": content}

        if document_type is not None:
            props["documentType"] = document_type

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnDocument, self, [scope, id, props])

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
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::SSM::Document.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-document.html#cfn-ssm-document-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="content")
    def content(self) -> typing.Any:
        """``AWS::SSM::Document.Content``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-document.html#cfn-ssm-document-content
        Stability:
            stable
        """
        return jsii.get(self, "content")

    @content.setter
    def content(self, value: typing.Any):
        return jsii.set(self, "content", value)

    @property
    @jsii.member(jsii_name="documentType")
    def document_type(self) -> typing.Optional[str]:
        """``AWS::SSM::Document.DocumentType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-document.html#cfn-ssm-document-documenttype
        Stability:
            stable
        """
        return jsii.get(self, "documentType")

    @document_type.setter
    def document_type(self, value: typing.Optional[str]):
        return jsii.set(self, "documentType", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnDocumentProps(jsii.compat.TypedDict, total=False):
    documentType: str
    """``AWS::SSM::Document.DocumentType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-document.html#cfn-ssm-document-documenttype
    Stability:
        stable
    """
    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::SSM::Document.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-document.html#cfn-ssm-document-tags
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnDocumentProps", jsii_struct_bases=[_CfnDocumentProps])
class CfnDocumentProps(_CfnDocumentProps):
    """Properties for defining a ``AWS::SSM::Document``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-document.html
    Stability:
        stable
    """
    content: typing.Any
    """``AWS::SSM::Document.Content``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-document.html#cfn-ssm-document-content
    Stability:
        stable
    """

class CfnMaintenanceWindow(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ssm.CfnMaintenanceWindow"):
    """A CloudFormation ``AWS::SSM::MaintenanceWindow``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html
    Stability:
        stable
    cloudformationResource:
        AWS::SSM::MaintenanceWindow
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, allow_unassociated_targets: typing.Union[bool, aws_cdk.core.IResolvable], cutoff: jsii.Number, duration: jsii.Number, name: str, schedule: str, description: typing.Optional[str]=None, end_date: typing.Optional[str]=None, schedule_timezone: typing.Optional[str]=None, start_date: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::SSM::MaintenanceWindow``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            allow_unassociated_targets: ``AWS::SSM::MaintenanceWindow.AllowUnassociatedTargets``.
            cutoff: ``AWS::SSM::MaintenanceWindow.Cutoff``.
            duration: ``AWS::SSM::MaintenanceWindow.Duration``.
            name: ``AWS::SSM::MaintenanceWindow.Name``.
            schedule: ``AWS::SSM::MaintenanceWindow.Schedule``.
            description: ``AWS::SSM::MaintenanceWindow.Description``.
            end_date: ``AWS::SSM::MaintenanceWindow.EndDate``.
            schedule_timezone: ``AWS::SSM::MaintenanceWindow.ScheduleTimezone``.
            start_date: ``AWS::SSM::MaintenanceWindow.StartDate``.
            tags: ``AWS::SSM::MaintenanceWindow.Tags``.

        Stability:
            experimental
        """
        props: CfnMaintenanceWindowProps = {"allowUnassociatedTargets": allow_unassociated_targets, "cutoff": cutoff, "duration": duration, "name": name, "schedule": schedule}

        if description is not None:
            props["description"] = description

        if end_date is not None:
            props["endDate"] = end_date

        if schedule_timezone is not None:
            props["scheduleTimezone"] = schedule_timezone

        if start_date is not None:
            props["startDate"] = start_date

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnMaintenanceWindow, self, [scope, id, props])

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
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::SSM::MaintenanceWindow.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html#cfn-ssm-maintenancewindow-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="allowUnassociatedTargets")
    def allow_unassociated_targets(self) -> typing.Union[bool, aws_cdk.core.IResolvable]:
        """``AWS::SSM::MaintenanceWindow.AllowUnassociatedTargets``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html#cfn-ssm-maintenancewindow-allowunassociatedtargets
        Stability:
            stable
        """
        return jsii.get(self, "allowUnassociatedTargets")

    @allow_unassociated_targets.setter
    def allow_unassociated_targets(self, value: typing.Union[bool, aws_cdk.core.IResolvable]):
        return jsii.set(self, "allowUnassociatedTargets", value)

    @property
    @jsii.member(jsii_name="cutoff")
    def cutoff(self) -> jsii.Number:
        """``AWS::SSM::MaintenanceWindow.Cutoff``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html#cfn-ssm-maintenancewindow-cutoff
        Stability:
            stable
        """
        return jsii.get(self, "cutoff")

    @cutoff.setter
    def cutoff(self, value: jsii.Number):
        return jsii.set(self, "cutoff", value)

    @property
    @jsii.member(jsii_name="duration")
    def duration(self) -> jsii.Number:
        """``AWS::SSM::MaintenanceWindow.Duration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html#cfn-ssm-maintenancewindow-duration
        Stability:
            stable
        """
        return jsii.get(self, "duration")

    @duration.setter
    def duration(self, value: jsii.Number):
        return jsii.set(self, "duration", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::SSM::MaintenanceWindow.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html#cfn-ssm-maintenancewindow-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="schedule")
    def schedule(self) -> str:
        """``AWS::SSM::MaintenanceWindow.Schedule``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html#cfn-ssm-maintenancewindow-schedule
        Stability:
            stable
        """
        return jsii.get(self, "schedule")

    @schedule.setter
    def schedule(self, value: str):
        return jsii.set(self, "schedule", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::SSM::MaintenanceWindow.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html#cfn-ssm-maintenancewindow-description
        Stability:
            stable
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="endDate")
    def end_date(self) -> typing.Optional[str]:
        """``AWS::SSM::MaintenanceWindow.EndDate``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html#cfn-ssm-maintenancewindow-enddate
        Stability:
            stable
        """
        return jsii.get(self, "endDate")

    @end_date.setter
    def end_date(self, value: typing.Optional[str]):
        return jsii.set(self, "endDate", value)

    @property
    @jsii.member(jsii_name="scheduleTimezone")
    def schedule_timezone(self) -> typing.Optional[str]:
        """``AWS::SSM::MaintenanceWindow.ScheduleTimezone``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html#cfn-ssm-maintenancewindow-scheduletimezone
        Stability:
            stable
        """
        return jsii.get(self, "scheduleTimezone")

    @schedule_timezone.setter
    def schedule_timezone(self, value: typing.Optional[str]):
        return jsii.set(self, "scheduleTimezone", value)

    @property
    @jsii.member(jsii_name="startDate")
    def start_date(self) -> typing.Optional[str]:
        """``AWS::SSM::MaintenanceWindow.StartDate``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html#cfn-ssm-maintenancewindow-startdate
        Stability:
            stable
        """
        return jsii.get(self, "startDate")

    @start_date.setter
    def start_date(self, value: typing.Optional[str]):
        return jsii.set(self, "startDate", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnMaintenanceWindowProps(jsii.compat.TypedDict, total=False):
    description: str
    """``AWS::SSM::MaintenanceWindow.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html#cfn-ssm-maintenancewindow-description
    Stability:
        stable
    """
    endDate: str
    """``AWS::SSM::MaintenanceWindow.EndDate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html#cfn-ssm-maintenancewindow-enddate
    Stability:
        stable
    """
    scheduleTimezone: str
    """``AWS::SSM::MaintenanceWindow.ScheduleTimezone``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html#cfn-ssm-maintenancewindow-scheduletimezone
    Stability:
        stable
    """
    startDate: str
    """``AWS::SSM::MaintenanceWindow.StartDate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html#cfn-ssm-maintenancewindow-startdate
    Stability:
        stable
    """
    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::SSM::MaintenanceWindow.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html#cfn-ssm-maintenancewindow-tags
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnMaintenanceWindowProps", jsii_struct_bases=[_CfnMaintenanceWindowProps])
class CfnMaintenanceWindowProps(_CfnMaintenanceWindowProps):
    """Properties for defining a ``AWS::SSM::MaintenanceWindow``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html
    Stability:
        stable
    """
    allowUnassociatedTargets: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::SSM::MaintenanceWindow.AllowUnassociatedTargets``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html#cfn-ssm-maintenancewindow-allowunassociatedtargets
    Stability:
        stable
    """

    cutoff: jsii.Number
    """``AWS::SSM::MaintenanceWindow.Cutoff``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html#cfn-ssm-maintenancewindow-cutoff
    Stability:
        stable
    """

    duration: jsii.Number
    """``AWS::SSM::MaintenanceWindow.Duration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html#cfn-ssm-maintenancewindow-duration
    Stability:
        stable
    """

    name: str
    """``AWS::SSM::MaintenanceWindow.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html#cfn-ssm-maintenancewindow-name
    Stability:
        stable
    """

    schedule: str
    """``AWS::SSM::MaintenanceWindow.Schedule``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html#cfn-ssm-maintenancewindow-schedule
    Stability:
        stable
    """

class CfnMaintenanceWindowTask(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ssm.CfnMaintenanceWindowTask"):
    """A CloudFormation ``AWS::SSM::MaintenanceWindowTask``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html
    Stability:
        stable
    cloudformationResource:
        AWS::SSM::MaintenanceWindowTask
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, max_concurrency: str, max_errors: str, priority: jsii.Number, service_role_arn: str, targets: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "TargetProperty"]]], task_arn: str, task_type: str, description: typing.Optional[str]=None, logging_info: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LoggingInfoProperty"]]]=None, name: typing.Optional[str]=None, task_invocation_parameters: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["TaskInvocationParametersProperty"]]]=None, task_parameters: typing.Any=None, window_id: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::SSM::MaintenanceWindowTask``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            max_concurrency: ``AWS::SSM::MaintenanceWindowTask.MaxConcurrency``.
            max_errors: ``AWS::SSM::MaintenanceWindowTask.MaxErrors``.
            priority: ``AWS::SSM::MaintenanceWindowTask.Priority``.
            service_role_arn: ``AWS::SSM::MaintenanceWindowTask.ServiceRoleArn``.
            targets: ``AWS::SSM::MaintenanceWindowTask.Targets``.
            task_arn: ``AWS::SSM::MaintenanceWindowTask.TaskArn``.
            task_type: ``AWS::SSM::MaintenanceWindowTask.TaskType``.
            description: ``AWS::SSM::MaintenanceWindowTask.Description``.
            logging_info: ``AWS::SSM::MaintenanceWindowTask.LoggingInfo``.
            name: ``AWS::SSM::MaintenanceWindowTask.Name``.
            task_invocation_parameters: ``AWS::SSM::MaintenanceWindowTask.TaskInvocationParameters``.
            task_parameters: ``AWS::SSM::MaintenanceWindowTask.TaskParameters``.
            window_id: ``AWS::SSM::MaintenanceWindowTask.WindowId``.

        Stability:
            experimental
        """
        props: CfnMaintenanceWindowTaskProps = {"maxConcurrency": max_concurrency, "maxErrors": max_errors, "priority": priority, "serviceRoleArn": service_role_arn, "targets": targets, "taskArn": task_arn, "taskType": task_type}

        if description is not None:
            props["description"] = description

        if logging_info is not None:
            props["loggingInfo"] = logging_info

        if name is not None:
            props["name"] = name

        if task_invocation_parameters is not None:
            props["taskInvocationParameters"] = task_invocation_parameters

        if task_parameters is not None:
            props["taskParameters"] = task_parameters

        if window_id is not None:
            props["windowId"] = window_id

        jsii.create(CfnMaintenanceWindowTask, self, [scope, id, props])

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
    @jsii.member(jsii_name="maxConcurrency")
    def max_concurrency(self) -> str:
        """``AWS::SSM::MaintenanceWindowTask.MaxConcurrency``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-maxconcurrency
        Stability:
            stable
        """
        return jsii.get(self, "maxConcurrency")

    @max_concurrency.setter
    def max_concurrency(self, value: str):
        return jsii.set(self, "maxConcurrency", value)

    @property
    @jsii.member(jsii_name="maxErrors")
    def max_errors(self) -> str:
        """``AWS::SSM::MaintenanceWindowTask.MaxErrors``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-maxerrors
        Stability:
            stable
        """
        return jsii.get(self, "maxErrors")

    @max_errors.setter
    def max_errors(self, value: str):
        return jsii.set(self, "maxErrors", value)

    @property
    @jsii.member(jsii_name="priority")
    def priority(self) -> jsii.Number:
        """``AWS::SSM::MaintenanceWindowTask.Priority``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-priority
        Stability:
            stable
        """
        return jsii.get(self, "priority")

    @priority.setter
    def priority(self, value: jsii.Number):
        return jsii.set(self, "priority", value)

    @property
    @jsii.member(jsii_name="serviceRoleArn")
    def service_role_arn(self) -> str:
        """``AWS::SSM::MaintenanceWindowTask.ServiceRoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-servicerolearn
        Stability:
            stable
        """
        return jsii.get(self, "serviceRoleArn")

    @service_role_arn.setter
    def service_role_arn(self, value: str):
        return jsii.set(self, "serviceRoleArn", value)

    @property
    @jsii.member(jsii_name="targets")
    def targets(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "TargetProperty"]]]:
        """``AWS::SSM::MaintenanceWindowTask.Targets``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-targets
        Stability:
            stable
        """
        return jsii.get(self, "targets")

    @targets.setter
    def targets(self, value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "TargetProperty"]]]):
        return jsii.set(self, "targets", value)

    @property
    @jsii.member(jsii_name="taskArn")
    def task_arn(self) -> str:
        """``AWS::SSM::MaintenanceWindowTask.TaskArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-taskarn
        Stability:
            stable
        """
        return jsii.get(self, "taskArn")

    @task_arn.setter
    def task_arn(self, value: str):
        return jsii.set(self, "taskArn", value)

    @property
    @jsii.member(jsii_name="taskParameters")
    def task_parameters(self) -> typing.Any:
        """``AWS::SSM::MaintenanceWindowTask.TaskParameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-taskparameters
        Stability:
            stable
        """
        return jsii.get(self, "taskParameters")

    @task_parameters.setter
    def task_parameters(self, value: typing.Any):
        return jsii.set(self, "taskParameters", value)

    @property
    @jsii.member(jsii_name="taskType")
    def task_type(self) -> str:
        """``AWS::SSM::MaintenanceWindowTask.TaskType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-tasktype
        Stability:
            stable
        """
        return jsii.get(self, "taskType")

    @task_type.setter
    def task_type(self, value: str):
        return jsii.set(self, "taskType", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::SSM::MaintenanceWindowTask.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-description
        Stability:
            stable
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="loggingInfo")
    def logging_info(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LoggingInfoProperty"]]]:
        """``AWS::SSM::MaintenanceWindowTask.LoggingInfo``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-logginginfo
        Stability:
            stable
        """
        return jsii.get(self, "loggingInfo")

    @logging_info.setter
    def logging_info(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LoggingInfoProperty"]]]):
        return jsii.set(self, "loggingInfo", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::SSM::MaintenanceWindowTask.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="taskInvocationParameters")
    def task_invocation_parameters(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["TaskInvocationParametersProperty"]]]:
        """``AWS::SSM::MaintenanceWindowTask.TaskInvocationParameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-taskinvocationparameters
        Stability:
            stable
        """
        return jsii.get(self, "taskInvocationParameters")

    @task_invocation_parameters.setter
    def task_invocation_parameters(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["TaskInvocationParametersProperty"]]]):
        return jsii.set(self, "taskInvocationParameters", value)

    @property
    @jsii.member(jsii_name="windowId")
    def window_id(self) -> typing.Optional[str]:
        """``AWS::SSM::MaintenanceWindowTask.WindowId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-windowid
        Stability:
            stable
        """
        return jsii.get(self, "windowId")

    @window_id.setter
    def window_id(self, value: typing.Optional[str]):
        return jsii.set(self, "windowId", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _LoggingInfoProperty(jsii.compat.TypedDict, total=False):
        s3Prefix: str
        """``CfnMaintenanceWindowTask.LoggingInfoProperty.S3Prefix``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-logginginfo.html#cfn-ssm-maintenancewindowtask-logginginfo-s3prefix
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnMaintenanceWindowTask.LoggingInfoProperty", jsii_struct_bases=[_LoggingInfoProperty])
    class LoggingInfoProperty(_LoggingInfoProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-logginginfo.html
        Stability:
            stable
        """
        region: str
        """``CfnMaintenanceWindowTask.LoggingInfoProperty.Region``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-logginginfo.html#cfn-ssm-maintenancewindowtask-logginginfo-region
        Stability:
            stable
        """

        s3Bucket: str
        """``CfnMaintenanceWindowTask.LoggingInfoProperty.S3Bucket``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-logginginfo.html#cfn-ssm-maintenancewindowtask-logginginfo-s3bucket
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnMaintenanceWindowTask.MaintenanceWindowAutomationParametersProperty", jsii_struct_bases=[])
    class MaintenanceWindowAutomationParametersProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowautomationparameters.html
        Stability:
            stable
        """
        documentVersion: str
        """``CfnMaintenanceWindowTask.MaintenanceWindowAutomationParametersProperty.DocumentVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowautomationparameters.html#cfn-ssm-maintenancewindowtask-maintenancewindowautomationparameters-documentversion
        Stability:
            stable
        """

        parameters: typing.Any
        """``CfnMaintenanceWindowTask.MaintenanceWindowAutomationParametersProperty.Parameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowautomationparameters.html#cfn-ssm-maintenancewindowtask-maintenancewindowautomationparameters-parameters
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnMaintenanceWindowTask.MaintenanceWindowLambdaParametersProperty", jsii_struct_bases=[])
    class MaintenanceWindowLambdaParametersProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowlambdaparameters.html
        Stability:
            stable
        """
        clientContext: str
        """``CfnMaintenanceWindowTask.MaintenanceWindowLambdaParametersProperty.ClientContext``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowlambdaparameters.html#cfn-ssm-maintenancewindowtask-maintenancewindowlambdaparameters-clientcontext
        Stability:
            stable
        """

        payload: str
        """``CfnMaintenanceWindowTask.MaintenanceWindowLambdaParametersProperty.Payload``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowlambdaparameters.html#cfn-ssm-maintenancewindowtask-maintenancewindowlambdaparameters-payload
        Stability:
            stable
        """

        qualifier: str
        """``CfnMaintenanceWindowTask.MaintenanceWindowLambdaParametersProperty.Qualifier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowlambdaparameters.html#cfn-ssm-maintenancewindowtask-maintenancewindowlambdaparameters-qualifier
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnMaintenanceWindowTask.MaintenanceWindowRunCommandParametersProperty", jsii_struct_bases=[])
    class MaintenanceWindowRunCommandParametersProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowruncommandparameters.html
        Stability:
            stable
        """
        comment: str
        """``CfnMaintenanceWindowTask.MaintenanceWindowRunCommandParametersProperty.Comment``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowruncommandparameters.html#cfn-ssm-maintenancewindowtask-maintenancewindowruncommandparameters-comment
        Stability:
            stable
        """

        documentHash: str
        """``CfnMaintenanceWindowTask.MaintenanceWindowRunCommandParametersProperty.DocumentHash``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowruncommandparameters.html#cfn-ssm-maintenancewindowtask-maintenancewindowruncommandparameters-documenthash
        Stability:
            stable
        """

        documentHashType: str
        """``CfnMaintenanceWindowTask.MaintenanceWindowRunCommandParametersProperty.DocumentHashType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowruncommandparameters.html#cfn-ssm-maintenancewindowtask-maintenancewindowruncommandparameters-documenthashtype
        Stability:
            stable
        """

        notificationConfig: typing.Union[aws_cdk.core.IResolvable, "CfnMaintenanceWindowTask.NotificationConfigProperty"]
        """``CfnMaintenanceWindowTask.MaintenanceWindowRunCommandParametersProperty.NotificationConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowruncommandparameters.html#cfn-ssm-maintenancewindowtask-maintenancewindowruncommandparameters-notificationconfig
        Stability:
            stable
        """

        outputS3BucketName: str
        """``CfnMaintenanceWindowTask.MaintenanceWindowRunCommandParametersProperty.OutputS3BucketName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowruncommandparameters.html#cfn-ssm-maintenancewindowtask-maintenancewindowruncommandparameters-outputs3bucketname
        Stability:
            stable
        """

        outputS3KeyPrefix: str
        """``CfnMaintenanceWindowTask.MaintenanceWindowRunCommandParametersProperty.OutputS3KeyPrefix``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowruncommandparameters.html#cfn-ssm-maintenancewindowtask-maintenancewindowruncommandparameters-outputs3keyprefix
        Stability:
            stable
        """

        parameters: typing.Any
        """``CfnMaintenanceWindowTask.MaintenanceWindowRunCommandParametersProperty.Parameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowruncommandparameters.html#cfn-ssm-maintenancewindowtask-maintenancewindowruncommandparameters-parameters
        Stability:
            stable
        """

        serviceRoleArn: str
        """``CfnMaintenanceWindowTask.MaintenanceWindowRunCommandParametersProperty.ServiceRoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowruncommandparameters.html#cfn-ssm-maintenancewindowtask-maintenancewindowruncommandparameters-servicerolearn
        Stability:
            stable
        """

        timeoutSeconds: jsii.Number
        """``CfnMaintenanceWindowTask.MaintenanceWindowRunCommandParametersProperty.TimeoutSeconds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowruncommandparameters.html#cfn-ssm-maintenancewindowtask-maintenancewindowruncommandparameters-timeoutseconds
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnMaintenanceWindowTask.MaintenanceWindowStepFunctionsParametersProperty", jsii_struct_bases=[])
    class MaintenanceWindowStepFunctionsParametersProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowstepfunctionsparameters.html
        Stability:
            stable
        """
        input: str
        """``CfnMaintenanceWindowTask.MaintenanceWindowStepFunctionsParametersProperty.Input``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowstepfunctionsparameters.html#cfn-ssm-maintenancewindowtask-maintenancewindowstepfunctionsparameters-input
        Stability:
            stable
        """

        name: str
        """``CfnMaintenanceWindowTask.MaintenanceWindowStepFunctionsParametersProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowstepfunctionsparameters.html#cfn-ssm-maintenancewindowtask-maintenancewindowstepfunctionsparameters-name
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _NotificationConfigProperty(jsii.compat.TypedDict, total=False):
        notificationEvents: typing.List[str]
        """``CfnMaintenanceWindowTask.NotificationConfigProperty.NotificationEvents``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-notificationconfig.html#cfn-ssm-maintenancewindowtask-notificationconfig-notificationevents
        Stability:
            stable
        """
        notificationType: str
        """``CfnMaintenanceWindowTask.NotificationConfigProperty.NotificationType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-notificationconfig.html#cfn-ssm-maintenancewindowtask-notificationconfig-notificationtype
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnMaintenanceWindowTask.NotificationConfigProperty", jsii_struct_bases=[_NotificationConfigProperty])
    class NotificationConfigProperty(_NotificationConfigProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-notificationconfig.html
        Stability:
            stable
        """
        notificationArn: str
        """``CfnMaintenanceWindowTask.NotificationConfigProperty.NotificationArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-notificationconfig.html#cfn-ssm-maintenancewindowtask-notificationconfig-notificationarn
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _TargetProperty(jsii.compat.TypedDict, total=False):
        values: typing.List[str]
        """``CfnMaintenanceWindowTask.TargetProperty.Values``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-target.html#cfn-ssm-maintenancewindowtask-target-values
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnMaintenanceWindowTask.TargetProperty", jsii_struct_bases=[_TargetProperty])
    class TargetProperty(_TargetProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-target.html
        Stability:
            stable
        """
        key: str
        """``CfnMaintenanceWindowTask.TargetProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-target.html#cfn-ssm-maintenancewindowtask-target-key
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnMaintenanceWindowTask.TaskInvocationParametersProperty", jsii_struct_bases=[])
    class TaskInvocationParametersProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-taskinvocationparameters.html
        Stability:
            stable
        """
        maintenanceWindowAutomationParameters: typing.Union[aws_cdk.core.IResolvable, "CfnMaintenanceWindowTask.MaintenanceWindowAutomationParametersProperty"]
        """``CfnMaintenanceWindowTask.TaskInvocationParametersProperty.MaintenanceWindowAutomationParameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-taskinvocationparameters.html#cfn-ssm-maintenancewindowtask-taskinvocationparameters-maintenancewindowautomationparameters
        Stability:
            stable
        """

        maintenanceWindowLambdaParameters: typing.Union[aws_cdk.core.IResolvable, "CfnMaintenanceWindowTask.MaintenanceWindowLambdaParametersProperty"]
        """``CfnMaintenanceWindowTask.TaskInvocationParametersProperty.MaintenanceWindowLambdaParameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-taskinvocationparameters.html#cfn-ssm-maintenancewindowtask-taskinvocationparameters-maintenancewindowlambdaparameters
        Stability:
            stable
        """

        maintenanceWindowRunCommandParameters: typing.Union[aws_cdk.core.IResolvable, "CfnMaintenanceWindowTask.MaintenanceWindowRunCommandParametersProperty"]
        """``CfnMaintenanceWindowTask.TaskInvocationParametersProperty.MaintenanceWindowRunCommandParameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-taskinvocationparameters.html#cfn-ssm-maintenancewindowtask-taskinvocationparameters-maintenancewindowruncommandparameters
        Stability:
            stable
        """

        maintenanceWindowStepFunctionsParameters: typing.Union[aws_cdk.core.IResolvable, "CfnMaintenanceWindowTask.MaintenanceWindowStepFunctionsParametersProperty"]
        """``CfnMaintenanceWindowTask.TaskInvocationParametersProperty.MaintenanceWindowStepFunctionsParameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-taskinvocationparameters.html#cfn-ssm-maintenancewindowtask-taskinvocationparameters-maintenancewindowstepfunctionsparameters
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnMaintenanceWindowTaskProps(jsii.compat.TypedDict, total=False):
    description: str
    """``AWS::SSM::MaintenanceWindowTask.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-description
    Stability:
        stable
    """
    loggingInfo: typing.Union[aws_cdk.core.IResolvable, "CfnMaintenanceWindowTask.LoggingInfoProperty"]
    """``AWS::SSM::MaintenanceWindowTask.LoggingInfo``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-logginginfo
    Stability:
        stable
    """
    name: str
    """``AWS::SSM::MaintenanceWindowTask.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-name
    Stability:
        stable
    """
    taskInvocationParameters: typing.Union[aws_cdk.core.IResolvable, "CfnMaintenanceWindowTask.TaskInvocationParametersProperty"]
    """``AWS::SSM::MaintenanceWindowTask.TaskInvocationParameters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-taskinvocationparameters
    Stability:
        stable
    """
    taskParameters: typing.Any
    """``AWS::SSM::MaintenanceWindowTask.TaskParameters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-taskparameters
    Stability:
        stable
    """
    windowId: str
    """``AWS::SSM::MaintenanceWindowTask.WindowId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-windowid
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnMaintenanceWindowTaskProps", jsii_struct_bases=[_CfnMaintenanceWindowTaskProps])
class CfnMaintenanceWindowTaskProps(_CfnMaintenanceWindowTaskProps):
    """Properties for defining a ``AWS::SSM::MaintenanceWindowTask``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html
    Stability:
        stable
    """
    maxConcurrency: str
    """``AWS::SSM::MaintenanceWindowTask.MaxConcurrency``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-maxconcurrency
    Stability:
        stable
    """

    maxErrors: str
    """``AWS::SSM::MaintenanceWindowTask.MaxErrors``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-maxerrors
    Stability:
        stable
    """

    priority: jsii.Number
    """``AWS::SSM::MaintenanceWindowTask.Priority``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-priority
    Stability:
        stable
    """

    serviceRoleArn: str
    """``AWS::SSM::MaintenanceWindowTask.ServiceRoleArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-servicerolearn
    Stability:
        stable
    """

    targets: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnMaintenanceWindowTask.TargetProperty"]]]
    """``AWS::SSM::MaintenanceWindowTask.Targets``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-targets
    Stability:
        stable
    """

    taskArn: str
    """``AWS::SSM::MaintenanceWindowTask.TaskArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-taskarn
    Stability:
        stable
    """

    taskType: str
    """``AWS::SSM::MaintenanceWindowTask.TaskType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-tasktype
    Stability:
        stable
    """

class CfnParameter(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ssm.CfnParameter"):
    """A CloudFormation ``AWS::SSM::Parameter``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-parameter.html
    Stability:
        stable
    cloudformationResource:
        AWS::SSM::Parameter
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, type: str, value: str, allowed_pattern: typing.Optional[str]=None, description: typing.Optional[str]=None, name: typing.Optional[str]=None, policies: typing.Optional[str]=None, tags: typing.Any=None, tier: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::SSM::Parameter``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            type: ``AWS::SSM::Parameter.Type``.
            value: ``AWS::SSM::Parameter.Value``.
            allowed_pattern: ``AWS::SSM::Parameter.AllowedPattern``.
            description: ``AWS::SSM::Parameter.Description``.
            name: ``AWS::SSM::Parameter.Name``.
            policies: ``AWS::SSM::Parameter.Policies``.
            tags: ``AWS::SSM::Parameter.Tags``.
            tier: ``AWS::SSM::Parameter.Tier``.

        Stability:
            experimental
        """
        props: CfnParameterProps = {"type": type, "value": value}

        if allowed_pattern is not None:
            props["allowedPattern"] = allowed_pattern

        if description is not None:
            props["description"] = description

        if name is not None:
            props["name"] = name

        if policies is not None:
            props["policies"] = policies

        if tags is not None:
            props["tags"] = tags

        if tier is not None:
            props["tier"] = tier

        jsii.create(CfnParameter, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrType")
    def attr_type(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Type
        """
        return jsii.get(self, "attrType")

    @property
    @jsii.member(jsii_name="attrValue")
    def attr_value(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Value
        """
        return jsii.get(self, "attrValue")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::SSM::Parameter.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-parameter.html#cfn-ssm-parameter-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="type")
    def type(self) -> str:
        """``AWS::SSM::Parameter.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-parameter.html#cfn-ssm-parameter-type
        Stability:
            stable
        """
        return jsii.get(self, "type")

    @type.setter
    def type(self, value: str):
        return jsii.set(self, "type", value)

    @property
    @jsii.member(jsii_name="value")
    def value(self) -> str:
        """``AWS::SSM::Parameter.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-parameter.html#cfn-ssm-parameter-value
        Stability:
            stable
        """
        return jsii.get(self, "value")

    @value.setter
    def value(self, value: str):
        return jsii.set(self, "value", value)

    @property
    @jsii.member(jsii_name="allowedPattern")
    def allowed_pattern(self) -> typing.Optional[str]:
        """``AWS::SSM::Parameter.AllowedPattern``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-parameter.html#cfn-ssm-parameter-allowedpattern
        Stability:
            stable
        """
        return jsii.get(self, "allowedPattern")

    @allowed_pattern.setter
    def allowed_pattern(self, value: typing.Optional[str]):
        return jsii.set(self, "allowedPattern", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::SSM::Parameter.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-parameter.html#cfn-ssm-parameter-description
        Stability:
            stable
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::SSM::Parameter.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-parameter.html#cfn-ssm-parameter-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="policies")
    def policies(self) -> typing.Optional[str]:
        """``AWS::SSM::Parameter.Policies``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-parameter.html#cfn-ssm-parameter-policies
        Stability:
            stable
        """
        return jsii.get(self, "policies")

    @policies.setter
    def policies(self, value: typing.Optional[str]):
        return jsii.set(self, "policies", value)

    @property
    @jsii.member(jsii_name="tier")
    def tier(self) -> typing.Optional[str]:
        """``AWS::SSM::Parameter.Tier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-parameter.html#cfn-ssm-parameter-tier
        Stability:
            stable
        """
        return jsii.get(self, "tier")

    @tier.setter
    def tier(self, value: typing.Optional[str]):
        return jsii.set(self, "tier", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnParameterProps(jsii.compat.TypedDict, total=False):
    allowedPattern: str
    """``AWS::SSM::Parameter.AllowedPattern``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-parameter.html#cfn-ssm-parameter-allowedpattern
    Stability:
        stable
    """
    description: str
    """``AWS::SSM::Parameter.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-parameter.html#cfn-ssm-parameter-description
    Stability:
        stable
    """
    name: str
    """``AWS::SSM::Parameter.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-parameter.html#cfn-ssm-parameter-name
    Stability:
        stable
    """
    policies: str
    """``AWS::SSM::Parameter.Policies``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-parameter.html#cfn-ssm-parameter-policies
    Stability:
        stable
    """
    tags: typing.Any
    """``AWS::SSM::Parameter.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-parameter.html#cfn-ssm-parameter-tags
    Stability:
        stable
    """
    tier: str
    """``AWS::SSM::Parameter.Tier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-parameter.html#cfn-ssm-parameter-tier
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnParameterProps", jsii_struct_bases=[_CfnParameterProps])
class CfnParameterProps(_CfnParameterProps):
    """Properties for defining a ``AWS::SSM::Parameter``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-parameter.html
    Stability:
        stable
    """
    type: str
    """``AWS::SSM::Parameter.Type``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-parameter.html#cfn-ssm-parameter-type
    Stability:
        stable
    """

    value: str
    """``AWS::SSM::Parameter.Value``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-parameter.html#cfn-ssm-parameter-value
    Stability:
        stable
    """

class CfnPatchBaseline(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ssm.CfnPatchBaseline"):
    """A CloudFormation ``AWS::SSM::PatchBaseline``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html
    Stability:
        stable
    cloudformationResource:
        AWS::SSM::PatchBaseline
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, approval_rules: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["RuleGroupProperty"]]]=None, approved_patches: typing.Optional[typing.List[str]]=None, approved_patches_compliance_level: typing.Optional[str]=None, approved_patches_enable_non_security: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, description: typing.Optional[str]=None, global_filters: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["PatchFilterGroupProperty"]]]=None, operating_system: typing.Optional[str]=None, patch_groups: typing.Optional[typing.List[str]]=None, rejected_patches: typing.Optional[typing.List[str]]=None, rejected_patches_action: typing.Optional[str]=None, sources: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "PatchSourceProperty"]]]]]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::SSM::PatchBaseline``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::SSM::PatchBaseline.Name``.
            approval_rules: ``AWS::SSM::PatchBaseline.ApprovalRules``.
            approved_patches: ``AWS::SSM::PatchBaseline.ApprovedPatches``.
            approved_patches_compliance_level: ``AWS::SSM::PatchBaseline.ApprovedPatchesComplianceLevel``.
            approved_patches_enable_non_security: ``AWS::SSM::PatchBaseline.ApprovedPatchesEnableNonSecurity``.
            description: ``AWS::SSM::PatchBaseline.Description``.
            global_filters: ``AWS::SSM::PatchBaseline.GlobalFilters``.
            operating_system: ``AWS::SSM::PatchBaseline.OperatingSystem``.
            patch_groups: ``AWS::SSM::PatchBaseline.PatchGroups``.
            rejected_patches: ``AWS::SSM::PatchBaseline.RejectedPatches``.
            rejected_patches_action: ``AWS::SSM::PatchBaseline.RejectedPatchesAction``.
            sources: ``AWS::SSM::PatchBaseline.Sources``.
            tags: ``AWS::SSM::PatchBaseline.Tags``.

        Stability:
            experimental
        """
        props: CfnPatchBaselineProps = {"name": name}

        if approval_rules is not None:
            props["approvalRules"] = approval_rules

        if approved_patches is not None:
            props["approvedPatches"] = approved_patches

        if approved_patches_compliance_level is not None:
            props["approvedPatchesComplianceLevel"] = approved_patches_compliance_level

        if approved_patches_enable_non_security is not None:
            props["approvedPatchesEnableNonSecurity"] = approved_patches_enable_non_security

        if description is not None:
            props["description"] = description

        if global_filters is not None:
            props["globalFilters"] = global_filters

        if operating_system is not None:
            props["operatingSystem"] = operating_system

        if patch_groups is not None:
            props["patchGroups"] = patch_groups

        if rejected_patches is not None:
            props["rejectedPatches"] = rejected_patches

        if rejected_patches_action is not None:
            props["rejectedPatchesAction"] = rejected_patches_action

        if sources is not None:
            props["sources"] = sources

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnPatchBaseline, self, [scope, id, props])

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
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::SSM::PatchBaseline.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::SSM::PatchBaseline.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="approvalRules")
    def approval_rules(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["RuleGroupProperty"]]]:
        """``AWS::SSM::PatchBaseline.ApprovalRules``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-approvalrules
        Stability:
            stable
        """
        return jsii.get(self, "approvalRules")

    @approval_rules.setter
    def approval_rules(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["RuleGroupProperty"]]]):
        return jsii.set(self, "approvalRules", value)

    @property
    @jsii.member(jsii_name="approvedPatches")
    def approved_patches(self) -> typing.Optional[typing.List[str]]:
        """``AWS::SSM::PatchBaseline.ApprovedPatches``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-approvedpatches
        Stability:
            stable
        """
        return jsii.get(self, "approvedPatches")

    @approved_patches.setter
    def approved_patches(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "approvedPatches", value)

    @property
    @jsii.member(jsii_name="approvedPatchesComplianceLevel")
    def approved_patches_compliance_level(self) -> typing.Optional[str]:
        """``AWS::SSM::PatchBaseline.ApprovedPatchesComplianceLevel``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-approvedpatchescompliancelevel
        Stability:
            stable
        """
        return jsii.get(self, "approvedPatchesComplianceLevel")

    @approved_patches_compliance_level.setter
    def approved_patches_compliance_level(self, value: typing.Optional[str]):
        return jsii.set(self, "approvedPatchesComplianceLevel", value)

    @property
    @jsii.member(jsii_name="approvedPatchesEnableNonSecurity")
    def approved_patches_enable_non_security(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::SSM::PatchBaseline.ApprovedPatchesEnableNonSecurity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-approvedpatchesenablenonsecurity
        Stability:
            stable
        """
        return jsii.get(self, "approvedPatchesEnableNonSecurity")

    @approved_patches_enable_non_security.setter
    def approved_patches_enable_non_security(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "approvedPatchesEnableNonSecurity", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::SSM::PatchBaseline.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-description
        Stability:
            stable
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="globalFilters")
    def global_filters(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["PatchFilterGroupProperty"]]]:
        """``AWS::SSM::PatchBaseline.GlobalFilters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-globalfilters
        Stability:
            stable
        """
        return jsii.get(self, "globalFilters")

    @global_filters.setter
    def global_filters(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["PatchFilterGroupProperty"]]]):
        return jsii.set(self, "globalFilters", value)

    @property
    @jsii.member(jsii_name="operatingSystem")
    def operating_system(self) -> typing.Optional[str]:
        """``AWS::SSM::PatchBaseline.OperatingSystem``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-operatingsystem
        Stability:
            stable
        """
        return jsii.get(self, "operatingSystem")

    @operating_system.setter
    def operating_system(self, value: typing.Optional[str]):
        return jsii.set(self, "operatingSystem", value)

    @property
    @jsii.member(jsii_name="patchGroups")
    def patch_groups(self) -> typing.Optional[typing.List[str]]:
        """``AWS::SSM::PatchBaseline.PatchGroups``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-patchgroups
        Stability:
            stable
        """
        return jsii.get(self, "patchGroups")

    @patch_groups.setter
    def patch_groups(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "patchGroups", value)

    @property
    @jsii.member(jsii_name="rejectedPatches")
    def rejected_patches(self) -> typing.Optional[typing.List[str]]:
        """``AWS::SSM::PatchBaseline.RejectedPatches``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-rejectedpatches
        Stability:
            stable
        """
        return jsii.get(self, "rejectedPatches")

    @rejected_patches.setter
    def rejected_patches(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "rejectedPatches", value)

    @property
    @jsii.member(jsii_name="rejectedPatchesAction")
    def rejected_patches_action(self) -> typing.Optional[str]:
        """``AWS::SSM::PatchBaseline.RejectedPatchesAction``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-rejectedpatchesaction
        Stability:
            stable
        """
        return jsii.get(self, "rejectedPatchesAction")

    @rejected_patches_action.setter
    def rejected_patches_action(self, value: typing.Optional[str]):
        return jsii.set(self, "rejectedPatchesAction", value)

    @property
    @jsii.member(jsii_name="sources")
    def sources(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "PatchSourceProperty"]]]]]:
        """``AWS::SSM::PatchBaseline.Sources``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-sources
        Stability:
            stable
        """
        return jsii.get(self, "sources")

    @sources.setter
    def sources(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "PatchSourceProperty"]]]]]):
        return jsii.set(self, "sources", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnPatchBaseline.PatchFilterGroupProperty", jsii_struct_bases=[])
    class PatchFilterGroupProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-patchbaseline-patchfiltergroup.html
        Stability:
            stable
        """
        patchFilters: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnPatchBaseline.PatchFilterProperty"]]]
        """``CfnPatchBaseline.PatchFilterGroupProperty.PatchFilters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-patchbaseline-patchfiltergroup.html#cfn-ssm-patchbaseline-patchfiltergroup-patchfilters
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnPatchBaseline.PatchFilterProperty", jsii_struct_bases=[])
    class PatchFilterProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-patchbaseline-patchfilter.html
        Stability:
            stable
        """
        key: str
        """``CfnPatchBaseline.PatchFilterProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-patchbaseline-patchfilter.html#cfn-ssm-patchbaseline-patchfilter-key
        Stability:
            stable
        """

        values: typing.List[str]
        """``CfnPatchBaseline.PatchFilterProperty.Values``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-patchbaseline-patchfilter.html#cfn-ssm-patchbaseline-patchfilter-values
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnPatchBaseline.PatchSourceProperty", jsii_struct_bases=[])
    class PatchSourceProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-patchbaseline-patchsource.html
        Stability:
            stable
        """
        configuration: str
        """``CfnPatchBaseline.PatchSourceProperty.Configuration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-patchbaseline-patchsource.html#cfn-ssm-patchbaseline-patchsource-configuration
        Stability:
            stable
        """

        name: str
        """``CfnPatchBaseline.PatchSourceProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-patchbaseline-patchsource.html#cfn-ssm-patchbaseline-patchsource-name
        Stability:
            stable
        """

        products: typing.List[str]
        """``CfnPatchBaseline.PatchSourceProperty.Products``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-patchbaseline-patchsource.html#cfn-ssm-patchbaseline-patchsource-products
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnPatchBaseline.RuleGroupProperty", jsii_struct_bases=[])
    class RuleGroupProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-patchbaseline-rulegroup.html
        Stability:
            stable
        """
        patchRules: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnPatchBaseline.RuleProperty"]]]
        """``CfnPatchBaseline.RuleGroupProperty.PatchRules``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-patchbaseline-rulegroup.html#cfn-ssm-patchbaseline-rulegroup-patchrules
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnPatchBaseline.RuleProperty", jsii_struct_bases=[])
    class RuleProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-patchbaseline-rule.html
        Stability:
            stable
        """
        approveAfterDays: jsii.Number
        """``CfnPatchBaseline.RuleProperty.ApproveAfterDays``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-patchbaseline-rule.html#cfn-ssm-patchbaseline-rule-approveafterdays
        Stability:
            stable
        """

        complianceLevel: str
        """``CfnPatchBaseline.RuleProperty.ComplianceLevel``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-patchbaseline-rule.html#cfn-ssm-patchbaseline-rule-compliancelevel
        Stability:
            stable
        """

        enableNonSecurity: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnPatchBaseline.RuleProperty.EnableNonSecurity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-patchbaseline-rule.html#cfn-ssm-patchbaseline-rule-enablenonsecurity
        Stability:
            stable
        """

        patchFilterGroup: typing.Union[aws_cdk.core.IResolvable, "CfnPatchBaseline.PatchFilterGroupProperty"]
        """``CfnPatchBaseline.RuleProperty.PatchFilterGroup``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-patchbaseline-rule.html#cfn-ssm-patchbaseline-rule-patchfiltergroup
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnPatchBaselineProps(jsii.compat.TypedDict, total=False):
    approvalRules: typing.Union[aws_cdk.core.IResolvable, "CfnPatchBaseline.RuleGroupProperty"]
    """``AWS::SSM::PatchBaseline.ApprovalRules``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-approvalrules
    Stability:
        stable
    """
    approvedPatches: typing.List[str]
    """``AWS::SSM::PatchBaseline.ApprovedPatches``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-approvedpatches
    Stability:
        stable
    """
    approvedPatchesComplianceLevel: str
    """``AWS::SSM::PatchBaseline.ApprovedPatchesComplianceLevel``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-approvedpatchescompliancelevel
    Stability:
        stable
    """
    approvedPatchesEnableNonSecurity: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::SSM::PatchBaseline.ApprovedPatchesEnableNonSecurity``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-approvedpatchesenablenonsecurity
    Stability:
        stable
    """
    description: str
    """``AWS::SSM::PatchBaseline.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-description
    Stability:
        stable
    """
    globalFilters: typing.Union[aws_cdk.core.IResolvable, "CfnPatchBaseline.PatchFilterGroupProperty"]
    """``AWS::SSM::PatchBaseline.GlobalFilters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-globalfilters
    Stability:
        stable
    """
    operatingSystem: str
    """``AWS::SSM::PatchBaseline.OperatingSystem``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-operatingsystem
    Stability:
        stable
    """
    patchGroups: typing.List[str]
    """``AWS::SSM::PatchBaseline.PatchGroups``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-patchgroups
    Stability:
        stable
    """
    rejectedPatches: typing.List[str]
    """``AWS::SSM::PatchBaseline.RejectedPatches``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-rejectedpatches
    Stability:
        stable
    """
    rejectedPatchesAction: str
    """``AWS::SSM::PatchBaseline.RejectedPatchesAction``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-rejectedpatchesaction
    Stability:
        stable
    """
    sources: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnPatchBaseline.PatchSourceProperty"]]]
    """``AWS::SSM::PatchBaseline.Sources``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-sources
    Stability:
        stable
    """
    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::SSM::PatchBaseline.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-tags
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnPatchBaselineProps", jsii_struct_bases=[_CfnPatchBaselineProps])
class CfnPatchBaselineProps(_CfnPatchBaselineProps):
    """Properties for defining a ``AWS::SSM::PatchBaseline``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html
    Stability:
        stable
    """
    name: str
    """``AWS::SSM::PatchBaseline.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-name
    Stability:
        stable
    """

class CfnResourceDataSync(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ssm.CfnResourceDataSync"):
    """A CloudFormation ``AWS::SSM::ResourceDataSync``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-resourcedatasync.html
    Stability:
        stable
    cloudformationResource:
        AWS::SSM::ResourceDataSync
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, bucket_name: str, bucket_region: str, sync_format: str, sync_name: str, bucket_prefix: typing.Optional[str]=None, kms_key_arn: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::SSM::ResourceDataSync``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            bucket_name: ``AWS::SSM::ResourceDataSync.BucketName``.
            bucket_region: ``AWS::SSM::ResourceDataSync.BucketRegion``.
            sync_format: ``AWS::SSM::ResourceDataSync.SyncFormat``.
            sync_name: ``AWS::SSM::ResourceDataSync.SyncName``.
            bucket_prefix: ``AWS::SSM::ResourceDataSync.BucketPrefix``.
            kms_key_arn: ``AWS::SSM::ResourceDataSync.KMSKeyArn``.

        Stability:
            experimental
        """
        props: CfnResourceDataSyncProps = {"bucketName": bucket_name, "bucketRegion": bucket_region, "syncFormat": sync_format, "syncName": sync_name}

        if bucket_prefix is not None:
            props["bucketPrefix"] = bucket_prefix

        if kms_key_arn is not None:
            props["kmsKeyArn"] = kms_key_arn

        jsii.create(CfnResourceDataSync, self, [scope, id, props])

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
    @jsii.member(jsii_name="bucketName")
    def bucket_name(self) -> str:
        """``AWS::SSM::ResourceDataSync.BucketName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-resourcedatasync.html#cfn-ssm-resourcedatasync-bucketname
        Stability:
            stable
        """
        return jsii.get(self, "bucketName")

    @bucket_name.setter
    def bucket_name(self, value: str):
        return jsii.set(self, "bucketName", value)

    @property
    @jsii.member(jsii_name="bucketRegion")
    def bucket_region(self) -> str:
        """``AWS::SSM::ResourceDataSync.BucketRegion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-resourcedatasync.html#cfn-ssm-resourcedatasync-bucketregion
        Stability:
            stable
        """
        return jsii.get(self, "bucketRegion")

    @bucket_region.setter
    def bucket_region(self, value: str):
        return jsii.set(self, "bucketRegion", value)

    @property
    @jsii.member(jsii_name="syncFormat")
    def sync_format(self) -> str:
        """``AWS::SSM::ResourceDataSync.SyncFormat``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-resourcedatasync.html#cfn-ssm-resourcedatasync-syncformat
        Stability:
            stable
        """
        return jsii.get(self, "syncFormat")

    @sync_format.setter
    def sync_format(self, value: str):
        return jsii.set(self, "syncFormat", value)

    @property
    @jsii.member(jsii_name="syncName")
    def sync_name(self) -> str:
        """``AWS::SSM::ResourceDataSync.SyncName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-resourcedatasync.html#cfn-ssm-resourcedatasync-syncname
        Stability:
            stable
        """
        return jsii.get(self, "syncName")

    @sync_name.setter
    def sync_name(self, value: str):
        return jsii.set(self, "syncName", value)

    @property
    @jsii.member(jsii_name="bucketPrefix")
    def bucket_prefix(self) -> typing.Optional[str]:
        """``AWS::SSM::ResourceDataSync.BucketPrefix``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-resourcedatasync.html#cfn-ssm-resourcedatasync-bucketprefix
        Stability:
            stable
        """
        return jsii.get(self, "bucketPrefix")

    @bucket_prefix.setter
    def bucket_prefix(self, value: typing.Optional[str]):
        return jsii.set(self, "bucketPrefix", value)

    @property
    @jsii.member(jsii_name="kmsKeyArn")
    def kms_key_arn(self) -> typing.Optional[str]:
        """``AWS::SSM::ResourceDataSync.KMSKeyArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-resourcedatasync.html#cfn-ssm-resourcedatasync-kmskeyarn
        Stability:
            stable
        """
        return jsii.get(self, "kmsKeyArn")

    @kms_key_arn.setter
    def kms_key_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "kmsKeyArn", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnResourceDataSyncProps(jsii.compat.TypedDict, total=False):
    bucketPrefix: str
    """``AWS::SSM::ResourceDataSync.BucketPrefix``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-resourcedatasync.html#cfn-ssm-resourcedatasync-bucketprefix
    Stability:
        stable
    """
    kmsKeyArn: str
    """``AWS::SSM::ResourceDataSync.KMSKeyArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-resourcedatasync.html#cfn-ssm-resourcedatasync-kmskeyarn
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnResourceDataSyncProps", jsii_struct_bases=[_CfnResourceDataSyncProps])
class CfnResourceDataSyncProps(_CfnResourceDataSyncProps):
    """Properties for defining a ``AWS::SSM::ResourceDataSync``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-resourcedatasync.html
    Stability:
        stable
    """
    bucketName: str
    """``AWS::SSM::ResourceDataSync.BucketName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-resourcedatasync.html#cfn-ssm-resourcedatasync-bucketname
    Stability:
        stable
    """

    bucketRegion: str
    """``AWS::SSM::ResourceDataSync.BucketRegion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-resourcedatasync.html#cfn-ssm-resourcedatasync-bucketregion
    Stability:
        stable
    """

    syncFormat: str
    """``AWS::SSM::ResourceDataSync.SyncFormat``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-resourcedatasync.html#cfn-ssm-resourcedatasync-syncformat
    Stability:
        stable
    """

    syncName: str
    """``AWS::SSM::ResourceDataSync.SyncName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-resourcedatasync.html#cfn-ssm-resourcedatasync-syncname
    Stability:
        stable
    """

@jsii.interface(jsii_type="@aws-cdk/aws-ssm.IParameter")
class IParameter(aws_cdk.core.IResource, jsii.compat.Protocol):
    """An SSM Parameter reference.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IParameterProxy

    @property
    @jsii.member(jsii_name="parameterArn")
    def parameter_arn(self) -> str:
        """The ARN of the SSM Parameter resource.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="parameterName")
    def parameter_name(self) -> str:
        """The name of the SSM Parameter resource.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="parameterType")
    def parameter_type(self) -> str:
        """The type of the SSM Parameter resource.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @jsii.member(jsii_name="grantRead")
    def grant_read(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grants read (DescribeParameter, GetParameter, GetParameterHistory) permissions on the SSM Parameter.

        Arguments:
            grantee: the role to be granted read-only access to the parameter.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="grantWrite")
    def grant_write(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grants write (PutParameter) permissions on the SSM Parameter.

        Arguments:
            grantee: the role to be granted write access to the parameter.

        Stability:
            experimental
        """
        ...


class _IParameterProxy(jsii.proxy_for(aws_cdk.core.IResource)):
    """An SSM Parameter reference.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-ssm.IParameter"
    @property
    @jsii.member(jsii_name="parameterArn")
    def parameter_arn(self) -> str:
        """The ARN of the SSM Parameter resource.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "parameterArn")

    @property
    @jsii.member(jsii_name="parameterName")
    def parameter_name(self) -> str:
        """The name of the SSM Parameter resource.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "parameterName")

    @property
    @jsii.member(jsii_name="parameterType")
    def parameter_type(self) -> str:
        """The type of the SSM Parameter resource.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "parameterType")

    @jsii.member(jsii_name="grantRead")
    def grant_read(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grants read (DescribeParameter, GetParameter, GetParameterHistory) permissions on the SSM Parameter.

        Arguments:
            grantee: the role to be granted read-only access to the parameter.

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantRead", [grantee])

    @jsii.member(jsii_name="grantWrite")
    def grant_write(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grants write (PutParameter) permissions on the SSM Parameter.

        Arguments:
            grantee: the role to be granted write access to the parameter.

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantWrite", [grantee])


@jsii.interface(jsii_type="@aws-cdk/aws-ssm.IStringListParameter")
class IStringListParameter(IParameter, jsii.compat.Protocol):
    """A StringList SSM Parameter.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IStringListParameterProxy

    @property
    @jsii.member(jsii_name="stringListValue")
    def string_list_value(self) -> typing.List[str]:
        """The parameter value.

        Value must not nest another parameter. Do not use {{}} in the value. Values in the array
        cannot contain commas (``,``).

        Stability:
            experimental
        attribute:
            parameterValue
        """
        ...


class _IStringListParameterProxy(jsii.proxy_for(IParameter)):
    """A StringList SSM Parameter.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-ssm.IStringListParameter"
    @property
    @jsii.member(jsii_name="stringListValue")
    def string_list_value(self) -> typing.List[str]:
        """The parameter value.

        Value must not nest another parameter. Do not use {{}} in the value. Values in the array
        cannot contain commas (``,``).

        Stability:
            experimental
        attribute:
            parameterValue
        """
        return jsii.get(self, "stringListValue")


@jsii.interface(jsii_type="@aws-cdk/aws-ssm.IStringParameter")
class IStringParameter(IParameter, jsii.compat.Protocol):
    """A String SSM Parameter.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IStringParameterProxy

    @property
    @jsii.member(jsii_name="stringValue")
    def string_value(self) -> str:
        """The parameter value.

        Value must not nest another parameter. Do not use {{}} in the value.

        Stability:
            experimental
        attribute:
            parameterValue
        """
        ...


class _IStringParameterProxy(jsii.proxy_for(IParameter)):
    """A String SSM Parameter.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-ssm.IStringParameter"
    @property
    @jsii.member(jsii_name="stringValue")
    def string_value(self) -> str:
        """The parameter value.

        Value must not nest another parameter. Do not use {{}} in the value.

        Stability:
            experimental
        attribute:
            parameterValue
        """
        return jsii.get(self, "stringValue")


@jsii.data_type(jsii_type="@aws-cdk/aws-ssm.ParameterOptions", jsii_struct_bases=[])
class ParameterOptions(jsii.compat.TypedDict, total=False):
    """Properties needed to create a new SSM Parameter.

    Stability:
        experimental
    """
    allowedPattern: str
    """A regular expression used to validate the parameter value.

    For example, for String types with values restricted to
    numbers, you can specify the following: ``^\d+$``

    Default:
        no validation is performed

    Stability:
        experimental
    """

    description: str
    """Information about the parameter that you want to add to the system.

    Default:
        none

    Stability:
        experimental
    """

    parameterName: str
    """The name of the parameter.

    Default:
        - a name will be generated by CloudFormation

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ssm.SecureStringParameterAttributes", jsii_struct_bases=[])
class SecureStringParameterAttributes(jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    parameterName: str
    """The name of the parameter store value.

    Stability:
        experimental
    """

    version: jsii.Number
    """The version number of the value you wish to retrieve.

    This is required for secure strings.

    Stability:
        experimental
    """

@jsii.implements(IStringListParameter, IParameter)
class StringListParameter(aws_cdk.core.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ssm.StringListParameter"):
    """Creates a new StringList SSM Parameter.

    Stability:
        experimental
    resource:
        AWS::SSM::Parameter
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, string_list_value: typing.List[str], allowed_pattern: typing.Optional[str]=None, description: typing.Optional[str]=None, parameter_name: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            string_list_value: The values of the parameter. It may not reference another parameter and ``{{}}`` cannot be used in the value.
            allowed_pattern: A regular expression used to validate the parameter value. For example, for String types with values restricted to numbers, you can specify the following: ``^\d+$`` Default: no validation is performed
            description: Information about the parameter that you want to add to the system. Default: none
            parameter_name: The name of the parameter. Default: - a name will be generated by CloudFormation

        Stability:
            experimental
        """
        props: StringListParameterProps = {"stringListValue": string_list_value}

        if allowed_pattern is not None:
            props["allowedPattern"] = allowed_pattern

        if description is not None:
            props["description"] = description

        if parameter_name is not None:
            props["parameterName"] = parameter_name

        jsii.create(StringListParameter, self, [scope, id, props])

    @jsii.member(jsii_name="fromStringListParameterName")
    @classmethod
    def from_string_list_parameter_name(cls, scope: aws_cdk.core.Construct, id: str, string_list_parameter_name: str) -> "IStringListParameter":
        """Imports an external parameter of type string list.

        Arguments:
            scope: -
            id: -
            string_list_parameter_name: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromStringListParameterName", [scope, id, string_list_parameter_name])

    @jsii.member(jsii_name="grantRead")
    def grant_read(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grants read (DescribeParameter, GetParameter, GetParameterHistory) permissions on the SSM Parameter.

        Arguments:
            grantee: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantRead", [grantee])

    @jsii.member(jsii_name="grantWrite")
    def grant_write(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grants write (PutParameter) permissions on the SSM Parameter.

        Arguments:
            grantee: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantWrite", [grantee])

    @property
    @jsii.member(jsii_name="parameterArn")
    def parameter_arn(self) -> str:
        """The ARN of the SSM Parameter resource.

        Stability:
            experimental
        """
        return jsii.get(self, "parameterArn")

    @property
    @jsii.member(jsii_name="parameterName")
    def parameter_name(self) -> str:
        """The name of the SSM Parameter resource.

        Stability:
            experimental
        """
        return jsii.get(self, "parameterName")

    @property
    @jsii.member(jsii_name="parameterType")
    def parameter_type(self) -> str:
        """The type of the SSM Parameter resource.

        Stability:
            experimental
        """
        return jsii.get(self, "parameterType")

    @property
    @jsii.member(jsii_name="stringListValue")
    def string_list_value(self) -> typing.List[str]:
        """The parameter value.

        Value must not nest another parameter. Do not use {{}} in the value. Values in the array
        cannot contain commas (``,``).

        Stability:
            experimental
        """
        return jsii.get(self, "stringListValue")


@jsii.data_type(jsii_type="@aws-cdk/aws-ssm.StringListParameterProps", jsii_struct_bases=[ParameterOptions])
class StringListParameterProps(ParameterOptions, jsii.compat.TypedDict):
    """Properties needed to create a StringList SSM Parameter.

    Stability:
        experimental
    """
    stringListValue: typing.List[str]
    """The values of the parameter.

    It may not reference another parameter and ``{{}}`` cannot be used in the value.

    Stability:
        experimental
    """

@jsii.implements(IStringParameter, IParameter)
class StringParameter(aws_cdk.core.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ssm.StringParameter"):
    """Creates a new String SSM Parameter.

    Stability:
        experimental
    resource:
        AWS::SSM::Parameter
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, string_value: str, allowed_pattern: typing.Optional[str]=None, description: typing.Optional[str]=None, parameter_name: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            string_value: The value of the parameter. It may not reference another parameter and ``{{}}`` cannot be used in the value.
            allowed_pattern: A regular expression used to validate the parameter value. For example, for String types with values restricted to numbers, you can specify the following: ``^\d+$`` Default: no validation is performed
            description: Information about the parameter that you want to add to the system. Default: none
            parameter_name: The name of the parameter. Default: - a name will be generated by CloudFormation

        Stability:
            experimental
        """
        props: StringParameterProps = {"stringValue": string_value}

        if allowed_pattern is not None:
            props["allowedPattern"] = allowed_pattern

        if description is not None:
            props["description"] = description

        if parameter_name is not None:
            props["parameterName"] = parameter_name

        jsii.create(StringParameter, self, [scope, id, props])

    @jsii.member(jsii_name="fromSecureStringParameterAttributes")
    @classmethod
    def from_secure_string_parameter_attributes(cls, scope: aws_cdk.core.Construct, id: str, *, parameter_name: str, version: jsii.Number) -> "IStringParameter":
        """Imports a secure string parameter from the SSM parameter store.

        Arguments:
            scope: -
            id: -
            attrs: -
            parameter_name: The name of the parameter store value.
            version: The version number of the value you wish to retrieve. This is required for secure strings.

        Stability:
            experimental
        """
        attrs: SecureStringParameterAttributes = {"parameterName": parameter_name, "version": version}

        return jsii.sinvoke(cls, "fromSecureStringParameterAttributes", [scope, id, attrs])

    @jsii.member(jsii_name="fromStringParameterAttributes")
    @classmethod
    def from_string_parameter_attributes(cls, scope: aws_cdk.core.Construct, id: str, *, parameter_name: str, version: typing.Optional[jsii.Number]=None) -> "IStringParameter":
        """Imports an external string parameter with name and optional version.

        Arguments:
            scope: -
            id: -
            attrs: -
            parameter_name: The name of the parameter store value.
            version: The version number of the value you wish to retrieve. Default: The latest version will be retrieved.

        Stability:
            experimental
        """
        attrs: StringParameterAttributes = {"parameterName": parameter_name}

        if version is not None:
            attrs["version"] = version

        return jsii.sinvoke(cls, "fromStringParameterAttributes", [scope, id, attrs])

    @jsii.member(jsii_name="fromStringParameterName")
    @classmethod
    def from_string_parameter_name(cls, scope: aws_cdk.core.Construct, id: str, string_parameter_name: str) -> "IStringParameter":
        """Imports an external string parameter by name.

        Arguments:
            scope: -
            id: -
            string_parameter_name: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromStringParameterName", [scope, id, string_parameter_name])

    @jsii.member(jsii_name="valueForSecureStringParameter")
    @classmethod
    def value_for_secure_string_parameter(cls, scope: aws_cdk.core.Construct, parameter_name: str, version: jsii.Number) -> str:
        """Returns a token that will resolve (during deployment).

        Arguments:
            scope: Some scope within a stack.
            parameter_name: The name of the SSM parameter.
            version: The parameter version (required for secure strings).

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "valueForSecureStringParameter", [scope, parameter_name, version])

    @jsii.member(jsii_name="valueForStringParameter")
    @classmethod
    def value_for_string_parameter(cls, scope: aws_cdk.core.Construct, parameter_name: str, version: typing.Optional[jsii.Number]=None) -> str:
        """Returns a token that will resolve (during deployment) to the string value of an SSM string parameter.

        Arguments:
            scope: Some scope within a stack.
            parameter_name: The name of the SSM parameter.
            version: The parameter version (recommended in order to ensure that the value won't change during deployment).

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "valueForStringParameter", [scope, parameter_name, version])

    @jsii.member(jsii_name="valueFromLookup")
    @classmethod
    def value_from_lookup(cls, scope: aws_cdk.core.Construct, parameter_name: str) -> str:
        """Reads the value of an SSM parameter during synthesis through an environmental context provider.

        Requires that the stack this scope is defined in will have explicit
        account/region information. Otherwise, it will fail during synthesis.

        Arguments:
            scope: -
            parameter_name: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "valueFromLookup", [scope, parameter_name])

    @jsii.member(jsii_name="grantRead")
    def grant_read(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grants read (DescribeParameter, GetParameter, GetParameterHistory) permissions on the SSM Parameter.

        Arguments:
            grantee: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantRead", [grantee])

    @jsii.member(jsii_name="grantWrite")
    def grant_write(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grants write (PutParameter) permissions on the SSM Parameter.

        Arguments:
            grantee: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantWrite", [grantee])

    @property
    @jsii.member(jsii_name="parameterArn")
    def parameter_arn(self) -> str:
        """The ARN of the SSM Parameter resource.

        Stability:
            experimental
        """
        return jsii.get(self, "parameterArn")

    @property
    @jsii.member(jsii_name="parameterName")
    def parameter_name(self) -> str:
        """The name of the SSM Parameter resource.

        Stability:
            experimental
        """
        return jsii.get(self, "parameterName")

    @property
    @jsii.member(jsii_name="parameterType")
    def parameter_type(self) -> str:
        """The type of the SSM Parameter resource.

        Stability:
            experimental
        """
        return jsii.get(self, "parameterType")

    @property
    @jsii.member(jsii_name="stringValue")
    def string_value(self) -> str:
        """The parameter value.

        Value must not nest another parameter. Do not use {{}} in the value.

        Stability:
            experimental
        """
        return jsii.get(self, "stringValue")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _StringParameterAttributes(jsii.compat.TypedDict, total=False):
    version: jsii.Number
    """The version number of the value you wish to retrieve.

    Default:
        The latest version will be retrieved.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ssm.StringParameterAttributes", jsii_struct_bases=[_StringParameterAttributes])
class StringParameterAttributes(_StringParameterAttributes):
    """
    Stability:
        experimental
    """
    parameterName: str
    """The name of the parameter store value.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ssm.StringParameterProps", jsii_struct_bases=[ParameterOptions])
class StringParameterProps(ParameterOptions, jsii.compat.TypedDict):
    """Properties needed to create a String SSM parameter.

    Stability:
        experimental
    """
    stringValue: str
    """The value of the parameter.

    It may not reference another parameter and ``{{}}`` cannot be used in the value.

    Stability:
        experimental
    """

__all__ = ["CfnAssociation", "CfnAssociationProps", "CfnDocument", "CfnDocumentProps", "CfnMaintenanceWindow", "CfnMaintenanceWindowProps", "CfnMaintenanceWindowTask", "CfnMaintenanceWindowTaskProps", "CfnParameter", "CfnParameterProps", "CfnPatchBaseline", "CfnPatchBaselineProps", "CfnResourceDataSync", "CfnResourceDataSyncProps", "IParameter", "IStringListParameter", "IStringParameter", "ParameterOptions", "SecureStringParameterAttributes", "StringListParameter", "StringListParameterProps", "StringParameter", "StringParameterAttributes", "StringParameterProps", "__jsii_assembly__"]

publication.publish()
