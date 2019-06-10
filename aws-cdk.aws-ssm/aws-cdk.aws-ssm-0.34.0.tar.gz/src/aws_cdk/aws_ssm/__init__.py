import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_iam
import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-ssm", "0.34.0", __name__, "aws-ssm@0.34.0.jsii.tgz")
class CfnAssociation(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ssm.CfnAssociation"):
    """A CloudFormation ``AWS::SSM::Association``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-association.html
    Stability:
        experimental
    cloudformationResource:
        AWS::SSM::Association
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, association_name: typing.Optional[str]=None, document_version: typing.Optional[str]=None, instance_id: typing.Optional[str]=None, output_location: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["InstanceAssociationOutputLocationProperty"]]]=None, parameters: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.Mapping[str,typing.Union[aws_cdk.cdk.Token, "ParameterValuesProperty"]]]]]=None, schedule_expression: typing.Optional[str]=None, targets: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "TargetProperty"]]]]]=None) -> None:
        """Create a new ``AWS::SSM::Association``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::SSM::Association.Name``.
            associationName: ``AWS::SSM::Association.AssociationName``.
            documentVersion: ``AWS::SSM::Association.DocumentVersion``.
            instanceId: ``AWS::SSM::Association.InstanceId``.
            outputLocation: ``AWS::SSM::Association.OutputLocation``.
            parameters: ``AWS::SSM::Association.Parameters``.
            scheduleExpression: ``AWS::SSM::Association.ScheduleExpression``.
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
    def property_overrides(self) -> "CfnAssociationProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnAssociation.InstanceAssociationOutputLocationProperty", jsii_struct_bases=[])
    class InstanceAssociationOutputLocationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-association-instanceassociationoutputlocation.html
        Stability:
            experimental
        """
        s3Location: typing.Union[aws_cdk.cdk.Token, "CfnAssociation.S3OutputLocationProperty"]
        """``CfnAssociation.InstanceAssociationOutputLocationProperty.S3Location``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-association-instanceassociationoutputlocation.html#cfn-ssm-association-instanceassociationoutputlocation-s3location
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnAssociation.ParameterValuesProperty", jsii_struct_bases=[])
    class ParameterValuesProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-association-parametervalues.html
        Stability:
            experimental
        """
        parameterValues: typing.List[str]
        """``CfnAssociation.ParameterValuesProperty.ParameterValues``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-association-parametervalues.html#cfn-ssm-association-parametervalues-parametervalues
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnAssociation.S3OutputLocationProperty", jsii_struct_bases=[])
    class S3OutputLocationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-association-s3outputlocation.html
        Stability:
            experimental
        """
        outputS3BucketName: str
        """``CfnAssociation.S3OutputLocationProperty.OutputS3BucketName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-association-s3outputlocation.html#cfn-ssm-association-s3outputlocation-outputs3bucketname
        Stability:
            experimental
        """

        outputS3KeyPrefix: str
        """``CfnAssociation.S3OutputLocationProperty.OutputS3KeyPrefix``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-association-s3outputlocation.html#cfn-ssm-association-s3outputlocation-outputs3keyprefix
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnAssociation.TargetProperty", jsii_struct_bases=[])
    class TargetProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-association-target.html
        Stability:
            experimental
        """
        key: str
        """``CfnAssociation.TargetProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-association-target.html#cfn-ssm-association-target-key
        Stability:
            experimental
        """

        values: typing.List[str]
        """``CfnAssociation.TargetProperty.Values``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-association-target.html#cfn-ssm-association-target-values
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnAssociationProps(jsii.compat.TypedDict, total=False):
    associationName: str
    """``AWS::SSM::Association.AssociationName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-association.html#cfn-ssm-association-associationname
    Stability:
        experimental
    """
    documentVersion: str
    """``AWS::SSM::Association.DocumentVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-association.html#cfn-ssm-association-documentversion
    Stability:
        experimental
    """
    instanceId: str
    """``AWS::SSM::Association.InstanceId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-association.html#cfn-ssm-association-instanceid
    Stability:
        experimental
    """
    outputLocation: typing.Union[aws_cdk.cdk.Token, "CfnAssociation.InstanceAssociationOutputLocationProperty"]
    """``AWS::SSM::Association.OutputLocation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-association.html#cfn-ssm-association-outputlocation
    Stability:
        experimental
    """
    parameters: typing.Union[aws_cdk.cdk.Token, typing.Mapping[str,typing.Union[aws_cdk.cdk.Token, "CfnAssociation.ParameterValuesProperty"]]]
    """``AWS::SSM::Association.Parameters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-association.html#cfn-ssm-association-parameters
    Stability:
        experimental
    """
    scheduleExpression: str
    """``AWS::SSM::Association.ScheduleExpression``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-association.html#cfn-ssm-association-scheduleexpression
    Stability:
        experimental
    """
    targets: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnAssociation.TargetProperty"]]]
    """``AWS::SSM::Association.Targets``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-association.html#cfn-ssm-association-targets
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnAssociationProps", jsii_struct_bases=[_CfnAssociationProps])
class CfnAssociationProps(_CfnAssociationProps):
    """Properties for defining a ``AWS::SSM::Association``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-association.html
    Stability:
        experimental
    """
    name: str
    """``AWS::SSM::Association.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-association.html#cfn-ssm-association-name
    Stability:
        experimental
    """

class CfnDocument(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ssm.CfnDocument"):
    """A CloudFormation ``AWS::SSM::Document``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-document.html
    Stability:
        experimental
    cloudformationResource:
        AWS::SSM::Document
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, content: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token], document_type: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::SSM::Document``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            content: ``AWS::SSM::Document.Content``.
            documentType: ``AWS::SSM::Document.DocumentType``.
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
    @jsii.member(jsii_name="documentName")
    def document_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "documentName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnDocumentProps":
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
class _CfnDocumentProps(jsii.compat.TypedDict, total=False):
    documentType: str
    """``AWS::SSM::Document.DocumentType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-document.html#cfn-ssm-document-documenttype
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::SSM::Document.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-document.html#cfn-ssm-document-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnDocumentProps", jsii_struct_bases=[_CfnDocumentProps])
class CfnDocumentProps(_CfnDocumentProps):
    """Properties for defining a ``AWS::SSM::Document``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-document.html
    Stability:
        experimental
    """
    content: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
    """``AWS::SSM::Document.Content``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-document.html#cfn-ssm-document-content
    Stability:
        experimental
    """

class CfnMaintenanceWindow(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ssm.CfnMaintenanceWindow"):
    """A CloudFormation ``AWS::SSM::MaintenanceWindow``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html
    Stability:
        experimental
    cloudformationResource:
        AWS::SSM::MaintenanceWindow
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, allow_unassociated_targets: typing.Union[bool, aws_cdk.cdk.Token], cutoff: typing.Union[jsii.Number, aws_cdk.cdk.Token], duration: typing.Union[jsii.Number, aws_cdk.cdk.Token], name: str, schedule: str, description: typing.Optional[str]=None, end_date: typing.Optional[str]=None, schedule_timezone: typing.Optional[str]=None, start_date: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::SSM::MaintenanceWindow``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            allowUnassociatedTargets: ``AWS::SSM::MaintenanceWindow.AllowUnassociatedTargets``.
            cutoff: ``AWS::SSM::MaintenanceWindow.Cutoff``.
            duration: ``AWS::SSM::MaintenanceWindow.Duration``.
            name: ``AWS::SSM::MaintenanceWindow.Name``.
            schedule: ``AWS::SSM::MaintenanceWindow.Schedule``.
            description: ``AWS::SSM::MaintenanceWindow.Description``.
            endDate: ``AWS::SSM::MaintenanceWindow.EndDate``.
            scheduleTimezone: ``AWS::SSM::MaintenanceWindow.ScheduleTimezone``.
            startDate: ``AWS::SSM::MaintenanceWindow.StartDate``.
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
    @jsii.member(jsii_name="maintenanceWindowId")
    def maintenance_window_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "maintenanceWindowId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnMaintenanceWindowProps":
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
class _CfnMaintenanceWindowProps(jsii.compat.TypedDict, total=False):
    description: str
    """``AWS::SSM::MaintenanceWindow.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html#cfn-ssm-maintenancewindow-description
    Stability:
        experimental
    """
    endDate: str
    """``AWS::SSM::MaintenanceWindow.EndDate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html#cfn-ssm-maintenancewindow-enddate
    Stability:
        experimental
    """
    scheduleTimezone: str
    """``AWS::SSM::MaintenanceWindow.ScheduleTimezone``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html#cfn-ssm-maintenancewindow-scheduletimezone
    Stability:
        experimental
    """
    startDate: str
    """``AWS::SSM::MaintenanceWindow.StartDate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html#cfn-ssm-maintenancewindow-startdate
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::SSM::MaintenanceWindow.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html#cfn-ssm-maintenancewindow-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnMaintenanceWindowProps", jsii_struct_bases=[_CfnMaintenanceWindowProps])
class CfnMaintenanceWindowProps(_CfnMaintenanceWindowProps):
    """Properties for defining a ``AWS::SSM::MaintenanceWindow``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html
    Stability:
        experimental
    """
    allowUnassociatedTargets: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::SSM::MaintenanceWindow.AllowUnassociatedTargets``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html#cfn-ssm-maintenancewindow-allowunassociatedtargets
    Stability:
        experimental
    """

    cutoff: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::SSM::MaintenanceWindow.Cutoff``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html#cfn-ssm-maintenancewindow-cutoff
    Stability:
        experimental
    """

    duration: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::SSM::MaintenanceWindow.Duration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html#cfn-ssm-maintenancewindow-duration
    Stability:
        experimental
    """

    name: str
    """``AWS::SSM::MaintenanceWindow.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html#cfn-ssm-maintenancewindow-name
    Stability:
        experimental
    """

    schedule: str
    """``AWS::SSM::MaintenanceWindow.Schedule``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html#cfn-ssm-maintenancewindow-schedule
    Stability:
        experimental
    """

class CfnMaintenanceWindowTask(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ssm.CfnMaintenanceWindowTask"):
    """A CloudFormation ``AWS::SSM::MaintenanceWindowTask``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html
    Stability:
        experimental
    cloudformationResource:
        AWS::SSM::MaintenanceWindowTask
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, max_concurrency: str, max_errors: str, priority: typing.Union[jsii.Number, aws_cdk.cdk.Token], service_role_arn: str, targets: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "TargetProperty"]]], task_arn: str, task_type: str, description: typing.Optional[str]=None, logging_info: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["LoggingInfoProperty"]]]=None, name: typing.Optional[str]=None, task_invocation_parameters: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["TaskInvocationParametersProperty"]]]=None, task_parameters: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.Token]]]=None, window_id: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::SSM::MaintenanceWindowTask``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            maxConcurrency: ``AWS::SSM::MaintenanceWindowTask.MaxConcurrency``.
            maxErrors: ``AWS::SSM::MaintenanceWindowTask.MaxErrors``.
            priority: ``AWS::SSM::MaintenanceWindowTask.Priority``.
            serviceRoleArn: ``AWS::SSM::MaintenanceWindowTask.ServiceRoleArn``.
            targets: ``AWS::SSM::MaintenanceWindowTask.Targets``.
            taskArn: ``AWS::SSM::MaintenanceWindowTask.TaskArn``.
            taskType: ``AWS::SSM::MaintenanceWindowTask.TaskType``.
            description: ``AWS::SSM::MaintenanceWindowTask.Description``.
            loggingInfo: ``AWS::SSM::MaintenanceWindowTask.LoggingInfo``.
            name: ``AWS::SSM::MaintenanceWindowTask.Name``.
            taskInvocationParameters: ``AWS::SSM::MaintenanceWindowTask.TaskInvocationParameters``.
            taskParameters: ``AWS::SSM::MaintenanceWindowTask.TaskParameters``.
            windowId: ``AWS::SSM::MaintenanceWindowTask.WindowId``.

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
    @jsii.member(jsii_name="maintenanceWindowTaskId")
    def maintenance_window_task_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "maintenanceWindowTaskId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnMaintenanceWindowTaskProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _LoggingInfoProperty(jsii.compat.TypedDict, total=False):
        s3Prefix: str
        """``CfnMaintenanceWindowTask.LoggingInfoProperty.S3Prefix``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-logginginfo.html#cfn-ssm-maintenancewindowtask-logginginfo-s3prefix
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnMaintenanceWindowTask.LoggingInfoProperty", jsii_struct_bases=[_LoggingInfoProperty])
    class LoggingInfoProperty(_LoggingInfoProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-logginginfo.html
        Stability:
            experimental
        """
        region: str
        """``CfnMaintenanceWindowTask.LoggingInfoProperty.Region``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-logginginfo.html#cfn-ssm-maintenancewindowtask-logginginfo-region
        Stability:
            experimental
        """

        s3Bucket: str
        """``CfnMaintenanceWindowTask.LoggingInfoProperty.S3Bucket``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-logginginfo.html#cfn-ssm-maintenancewindowtask-logginginfo-s3bucket
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnMaintenanceWindowTask.MaintenanceWindowAutomationParametersProperty", jsii_struct_bases=[])
    class MaintenanceWindowAutomationParametersProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowautomationparameters.html
        Stability:
            experimental
        """
        documentVersion: str
        """``CfnMaintenanceWindowTask.MaintenanceWindowAutomationParametersProperty.DocumentVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowautomationparameters.html#cfn-ssm-maintenancewindowtask-maintenancewindowautomationparameters-documentversion
        Stability:
            experimental
        """

        parameters: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
        """``CfnMaintenanceWindowTask.MaintenanceWindowAutomationParametersProperty.Parameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowautomationparameters.html#cfn-ssm-maintenancewindowtask-maintenancewindowautomationparameters-parameters
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnMaintenanceWindowTask.MaintenanceWindowLambdaParametersProperty", jsii_struct_bases=[])
    class MaintenanceWindowLambdaParametersProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowlambdaparameters.html
        Stability:
            experimental
        """
        clientContext: str
        """``CfnMaintenanceWindowTask.MaintenanceWindowLambdaParametersProperty.ClientContext``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowlambdaparameters.html#cfn-ssm-maintenancewindowtask-maintenancewindowlambdaparameters-clientcontext
        Stability:
            experimental
        """

        payload: str
        """``CfnMaintenanceWindowTask.MaintenanceWindowLambdaParametersProperty.Payload``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowlambdaparameters.html#cfn-ssm-maintenancewindowtask-maintenancewindowlambdaparameters-payload
        Stability:
            experimental
        """

        qualifier: str
        """``CfnMaintenanceWindowTask.MaintenanceWindowLambdaParametersProperty.Qualifier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowlambdaparameters.html#cfn-ssm-maintenancewindowtask-maintenancewindowlambdaparameters-qualifier
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnMaintenanceWindowTask.MaintenanceWindowRunCommandParametersProperty", jsii_struct_bases=[])
    class MaintenanceWindowRunCommandParametersProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowruncommandparameters.html
        Stability:
            experimental
        """
        comment: str
        """``CfnMaintenanceWindowTask.MaintenanceWindowRunCommandParametersProperty.Comment``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowruncommandparameters.html#cfn-ssm-maintenancewindowtask-maintenancewindowruncommandparameters-comment
        Stability:
            experimental
        """

        documentHash: str
        """``CfnMaintenanceWindowTask.MaintenanceWindowRunCommandParametersProperty.DocumentHash``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowruncommandparameters.html#cfn-ssm-maintenancewindowtask-maintenancewindowruncommandparameters-documenthash
        Stability:
            experimental
        """

        documentHashType: str
        """``CfnMaintenanceWindowTask.MaintenanceWindowRunCommandParametersProperty.DocumentHashType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowruncommandparameters.html#cfn-ssm-maintenancewindowtask-maintenancewindowruncommandparameters-documenthashtype
        Stability:
            experimental
        """

        notificationConfig: typing.Union[aws_cdk.cdk.Token, "CfnMaintenanceWindowTask.NotificationConfigProperty"]
        """``CfnMaintenanceWindowTask.MaintenanceWindowRunCommandParametersProperty.NotificationConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowruncommandparameters.html#cfn-ssm-maintenancewindowtask-maintenancewindowruncommandparameters-notificationconfig
        Stability:
            experimental
        """

        outputS3BucketName: str
        """``CfnMaintenanceWindowTask.MaintenanceWindowRunCommandParametersProperty.OutputS3BucketName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowruncommandparameters.html#cfn-ssm-maintenancewindowtask-maintenancewindowruncommandparameters-outputs3bucketname
        Stability:
            experimental
        """

        outputS3KeyPrefix: str
        """``CfnMaintenanceWindowTask.MaintenanceWindowRunCommandParametersProperty.OutputS3KeyPrefix``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowruncommandparameters.html#cfn-ssm-maintenancewindowtask-maintenancewindowruncommandparameters-outputs3keyprefix
        Stability:
            experimental
        """

        parameters: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
        """``CfnMaintenanceWindowTask.MaintenanceWindowRunCommandParametersProperty.Parameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowruncommandparameters.html#cfn-ssm-maintenancewindowtask-maintenancewindowruncommandparameters-parameters
        Stability:
            experimental
        """

        serviceRoleArn: str
        """``CfnMaintenanceWindowTask.MaintenanceWindowRunCommandParametersProperty.ServiceRoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowruncommandparameters.html#cfn-ssm-maintenancewindowtask-maintenancewindowruncommandparameters-servicerolearn
        Stability:
            experimental
        """

        timeoutSeconds: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnMaintenanceWindowTask.MaintenanceWindowRunCommandParametersProperty.TimeoutSeconds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowruncommandparameters.html#cfn-ssm-maintenancewindowtask-maintenancewindowruncommandparameters-timeoutseconds
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnMaintenanceWindowTask.MaintenanceWindowStepFunctionsParametersProperty", jsii_struct_bases=[])
    class MaintenanceWindowStepFunctionsParametersProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowstepfunctionsparameters.html
        Stability:
            experimental
        """
        input: str
        """``CfnMaintenanceWindowTask.MaintenanceWindowStepFunctionsParametersProperty.Input``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowstepfunctionsparameters.html#cfn-ssm-maintenancewindowtask-maintenancewindowstepfunctionsparameters-input
        Stability:
            experimental
        """

        name: str
        """``CfnMaintenanceWindowTask.MaintenanceWindowStepFunctionsParametersProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-maintenancewindowstepfunctionsparameters.html#cfn-ssm-maintenancewindowtask-maintenancewindowstepfunctionsparameters-name
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _NotificationConfigProperty(jsii.compat.TypedDict, total=False):
        notificationEvents: typing.List[str]
        """``CfnMaintenanceWindowTask.NotificationConfigProperty.NotificationEvents``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-notificationconfig.html#cfn-ssm-maintenancewindowtask-notificationconfig-notificationevents
        Stability:
            experimental
        """
        notificationType: str
        """``CfnMaintenanceWindowTask.NotificationConfigProperty.NotificationType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-notificationconfig.html#cfn-ssm-maintenancewindowtask-notificationconfig-notificationtype
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnMaintenanceWindowTask.NotificationConfigProperty", jsii_struct_bases=[_NotificationConfigProperty])
    class NotificationConfigProperty(_NotificationConfigProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-notificationconfig.html
        Stability:
            experimental
        """
        notificationArn: str
        """``CfnMaintenanceWindowTask.NotificationConfigProperty.NotificationArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-notificationconfig.html#cfn-ssm-maintenancewindowtask-notificationconfig-notificationarn
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _TargetProperty(jsii.compat.TypedDict, total=False):
        values: typing.List[str]
        """``CfnMaintenanceWindowTask.TargetProperty.Values``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-target.html#cfn-ssm-maintenancewindowtask-target-values
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnMaintenanceWindowTask.TargetProperty", jsii_struct_bases=[_TargetProperty])
    class TargetProperty(_TargetProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-target.html
        Stability:
            experimental
        """
        key: str
        """``CfnMaintenanceWindowTask.TargetProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-target.html#cfn-ssm-maintenancewindowtask-target-key
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnMaintenanceWindowTask.TaskInvocationParametersProperty", jsii_struct_bases=[])
    class TaskInvocationParametersProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-taskinvocationparameters.html
        Stability:
            experimental
        """
        maintenanceWindowAutomationParameters: typing.Union[aws_cdk.cdk.Token, "CfnMaintenanceWindowTask.MaintenanceWindowAutomationParametersProperty"]
        """``CfnMaintenanceWindowTask.TaskInvocationParametersProperty.MaintenanceWindowAutomationParameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-taskinvocationparameters.html#cfn-ssm-maintenancewindowtask-taskinvocationparameters-maintenancewindowautomationparameters
        Stability:
            experimental
        """

        maintenanceWindowLambdaParameters: typing.Union[aws_cdk.cdk.Token, "CfnMaintenanceWindowTask.MaintenanceWindowLambdaParametersProperty"]
        """``CfnMaintenanceWindowTask.TaskInvocationParametersProperty.MaintenanceWindowLambdaParameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-taskinvocationparameters.html#cfn-ssm-maintenancewindowtask-taskinvocationparameters-maintenancewindowlambdaparameters
        Stability:
            experimental
        """

        maintenanceWindowRunCommandParameters: typing.Union[aws_cdk.cdk.Token, "CfnMaintenanceWindowTask.MaintenanceWindowRunCommandParametersProperty"]
        """``CfnMaintenanceWindowTask.TaskInvocationParametersProperty.MaintenanceWindowRunCommandParameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-taskinvocationparameters.html#cfn-ssm-maintenancewindowtask-taskinvocationparameters-maintenancewindowruncommandparameters
        Stability:
            experimental
        """

        maintenanceWindowStepFunctionsParameters: typing.Union[aws_cdk.cdk.Token, "CfnMaintenanceWindowTask.MaintenanceWindowStepFunctionsParametersProperty"]
        """``CfnMaintenanceWindowTask.TaskInvocationParametersProperty.MaintenanceWindowStepFunctionsParameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtask-taskinvocationparameters.html#cfn-ssm-maintenancewindowtask-taskinvocationparameters-maintenancewindowstepfunctionsparameters
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnMaintenanceWindowTaskProps(jsii.compat.TypedDict, total=False):
    description: str
    """``AWS::SSM::MaintenanceWindowTask.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-description
    Stability:
        experimental
    """
    loggingInfo: typing.Union[aws_cdk.cdk.Token, "CfnMaintenanceWindowTask.LoggingInfoProperty"]
    """``AWS::SSM::MaintenanceWindowTask.LoggingInfo``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-logginginfo
    Stability:
        experimental
    """
    name: str
    """``AWS::SSM::MaintenanceWindowTask.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-name
    Stability:
        experimental
    """
    taskInvocationParameters: typing.Union[aws_cdk.cdk.Token, "CfnMaintenanceWindowTask.TaskInvocationParametersProperty"]
    """``AWS::SSM::MaintenanceWindowTask.TaskInvocationParameters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-taskinvocationparameters
    Stability:
        experimental
    """
    taskParameters: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
    """``AWS::SSM::MaintenanceWindowTask.TaskParameters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-taskparameters
    Stability:
        experimental
    """
    windowId: str
    """``AWS::SSM::MaintenanceWindowTask.WindowId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-windowid
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnMaintenanceWindowTaskProps", jsii_struct_bases=[_CfnMaintenanceWindowTaskProps])
class CfnMaintenanceWindowTaskProps(_CfnMaintenanceWindowTaskProps):
    """Properties for defining a ``AWS::SSM::MaintenanceWindowTask``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html
    Stability:
        experimental
    """
    maxConcurrency: str
    """``AWS::SSM::MaintenanceWindowTask.MaxConcurrency``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-maxconcurrency
    Stability:
        experimental
    """

    maxErrors: str
    """``AWS::SSM::MaintenanceWindowTask.MaxErrors``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-maxerrors
    Stability:
        experimental
    """

    priority: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::SSM::MaintenanceWindowTask.Priority``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-priority
    Stability:
        experimental
    """

    serviceRoleArn: str
    """``AWS::SSM::MaintenanceWindowTask.ServiceRoleArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-servicerolearn
    Stability:
        experimental
    """

    targets: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnMaintenanceWindowTask.TargetProperty"]]]
    """``AWS::SSM::MaintenanceWindowTask.Targets``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-targets
    Stability:
        experimental
    """

    taskArn: str
    """``AWS::SSM::MaintenanceWindowTask.TaskArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-taskarn
    Stability:
        experimental
    """

    taskType: str
    """``AWS::SSM::MaintenanceWindowTask.TaskType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtask.html#cfn-ssm-maintenancewindowtask-tasktype
    Stability:
        experimental
    """

class CfnParameter(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ssm.CfnParameter"):
    """A CloudFormation ``AWS::SSM::Parameter``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-parameter.html
    Stability:
        experimental
    cloudformationResource:
        AWS::SSM::Parameter
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, type: str, value: str, allowed_pattern: typing.Optional[str]=None, description: typing.Optional[str]=None, name: typing.Optional[str]=None, policies: typing.Optional[str]=None, tags: typing.Optional[typing.Mapping[typing.Any, typing.Any]]=None, tier: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::SSM::Parameter``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            type: ``AWS::SSM::Parameter.Type``.
            value: ``AWS::SSM::Parameter.Value``.
            allowedPattern: ``AWS::SSM::Parameter.AllowedPattern``.
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
    @jsii.member(jsii_name="parameterName")
    def parameter_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "parameterName")

    @property
    @jsii.member(jsii_name="parameterType")
    def parameter_type(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Type
        """
        return jsii.get(self, "parameterType")

    @property
    @jsii.member(jsii_name="parameterValue")
    def parameter_value(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Value
        """
        return jsii.get(self, "parameterValue")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnParameterProps":
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
class _CfnParameterProps(jsii.compat.TypedDict, total=False):
    allowedPattern: str
    """``AWS::SSM::Parameter.AllowedPattern``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-parameter.html#cfn-ssm-parameter-allowedpattern
    Stability:
        experimental
    """
    description: str
    """``AWS::SSM::Parameter.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-parameter.html#cfn-ssm-parameter-description
    Stability:
        experimental
    """
    name: str
    """``AWS::SSM::Parameter.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-parameter.html#cfn-ssm-parameter-name
    Stability:
        experimental
    """
    policies: str
    """``AWS::SSM::Parameter.Policies``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-parameter.html#cfn-ssm-parameter-policies
    Stability:
        experimental
    """
    tags: typing.Mapping[typing.Any, typing.Any]
    """``AWS::SSM::Parameter.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-parameter.html#cfn-ssm-parameter-tags
    Stability:
        experimental
    """
    tier: str
    """``AWS::SSM::Parameter.Tier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-parameter.html#cfn-ssm-parameter-tier
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnParameterProps", jsii_struct_bases=[_CfnParameterProps])
class CfnParameterProps(_CfnParameterProps):
    """Properties for defining a ``AWS::SSM::Parameter``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-parameter.html
    Stability:
        experimental
    """
    type: str
    """``AWS::SSM::Parameter.Type``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-parameter.html#cfn-ssm-parameter-type
    Stability:
        experimental
    """

    value: str
    """``AWS::SSM::Parameter.Value``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-parameter.html#cfn-ssm-parameter-value
    Stability:
        experimental
    """

class CfnPatchBaseline(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ssm.CfnPatchBaseline"):
    """A CloudFormation ``AWS::SSM::PatchBaseline``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html
    Stability:
        experimental
    cloudformationResource:
        AWS::SSM::PatchBaseline
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, approval_rules: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["RuleGroupProperty"]]]=None, approved_patches: typing.Optional[typing.List[str]]=None, approved_patches_compliance_level: typing.Optional[str]=None, approved_patches_enable_non_security: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, description: typing.Optional[str]=None, global_filters: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["PatchFilterGroupProperty"]]]=None, operating_system: typing.Optional[str]=None, patch_groups: typing.Optional[typing.List[str]]=None, rejected_patches: typing.Optional[typing.List[str]]=None, rejected_patches_action: typing.Optional[str]=None, sources: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "PatchSourceProperty"]]]]]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::SSM::PatchBaseline``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::SSM::PatchBaseline.Name``.
            approvalRules: ``AWS::SSM::PatchBaseline.ApprovalRules``.
            approvedPatches: ``AWS::SSM::PatchBaseline.ApprovedPatches``.
            approvedPatchesComplianceLevel: ``AWS::SSM::PatchBaseline.ApprovedPatchesComplianceLevel``.
            approvedPatchesEnableNonSecurity: ``AWS::SSM::PatchBaseline.ApprovedPatchesEnableNonSecurity``.
            description: ``AWS::SSM::PatchBaseline.Description``.
            globalFilters: ``AWS::SSM::PatchBaseline.GlobalFilters``.
            operatingSystem: ``AWS::SSM::PatchBaseline.OperatingSystem``.
            patchGroups: ``AWS::SSM::PatchBaseline.PatchGroups``.
            rejectedPatches: ``AWS::SSM::PatchBaseline.RejectedPatches``.
            rejectedPatchesAction: ``AWS::SSM::PatchBaseline.RejectedPatchesAction``.
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
    @jsii.member(jsii_name="patchBaselineId")
    def patch_baseline_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "patchBaselineId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnPatchBaselineProps":
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

    @jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnPatchBaseline.PatchFilterGroupProperty", jsii_struct_bases=[])
    class PatchFilterGroupProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-patchbaseline-patchfiltergroup.html
        Stability:
            experimental
        """
        patchFilters: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnPatchBaseline.PatchFilterProperty"]]]
        """``CfnPatchBaseline.PatchFilterGroupProperty.PatchFilters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-patchbaseline-patchfiltergroup.html#cfn-ssm-patchbaseline-patchfiltergroup-patchfilters
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnPatchBaseline.PatchFilterProperty", jsii_struct_bases=[])
    class PatchFilterProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-patchbaseline-patchfilter.html
        Stability:
            experimental
        """
        key: str
        """``CfnPatchBaseline.PatchFilterProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-patchbaseline-patchfilter.html#cfn-ssm-patchbaseline-patchfilter-key
        Stability:
            experimental
        """

        values: typing.List[str]
        """``CfnPatchBaseline.PatchFilterProperty.Values``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-patchbaseline-patchfilter.html#cfn-ssm-patchbaseline-patchfilter-values
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnPatchBaseline.PatchSourceProperty", jsii_struct_bases=[])
    class PatchSourceProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-patchbaseline-patchsource.html
        Stability:
            experimental
        """
        configuration: str
        """``CfnPatchBaseline.PatchSourceProperty.Configuration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-patchbaseline-patchsource.html#cfn-ssm-patchbaseline-patchsource-configuration
        Stability:
            experimental
        """

        name: str
        """``CfnPatchBaseline.PatchSourceProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-patchbaseline-patchsource.html#cfn-ssm-patchbaseline-patchsource-name
        Stability:
            experimental
        """

        products: typing.List[str]
        """``CfnPatchBaseline.PatchSourceProperty.Products``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-patchbaseline-patchsource.html#cfn-ssm-patchbaseline-patchsource-products
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnPatchBaseline.RuleGroupProperty", jsii_struct_bases=[])
    class RuleGroupProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-patchbaseline-rulegroup.html
        Stability:
            experimental
        """
        patchRules: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnPatchBaseline.RuleProperty"]]]
        """``CfnPatchBaseline.RuleGroupProperty.PatchRules``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-patchbaseline-rulegroup.html#cfn-ssm-patchbaseline-rulegroup-patchrules
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnPatchBaseline.RuleProperty", jsii_struct_bases=[])
    class RuleProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-patchbaseline-rule.html
        Stability:
            experimental
        """
        approveAfterDays: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnPatchBaseline.RuleProperty.ApproveAfterDays``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-patchbaseline-rule.html#cfn-ssm-patchbaseline-rule-approveafterdays
        Stability:
            experimental
        """

        complianceLevel: str
        """``CfnPatchBaseline.RuleProperty.ComplianceLevel``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-patchbaseline-rule.html#cfn-ssm-patchbaseline-rule-compliancelevel
        Stability:
            experimental
        """

        enableNonSecurity: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnPatchBaseline.RuleProperty.EnableNonSecurity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-patchbaseline-rule.html#cfn-ssm-patchbaseline-rule-enablenonsecurity
        Stability:
            experimental
        """

        patchFilterGroup: typing.Union[aws_cdk.cdk.Token, "CfnPatchBaseline.PatchFilterGroupProperty"]
        """``CfnPatchBaseline.RuleProperty.PatchFilterGroup``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-patchbaseline-rule.html#cfn-ssm-patchbaseline-rule-patchfiltergroup
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnPatchBaselineProps(jsii.compat.TypedDict, total=False):
    approvalRules: typing.Union[aws_cdk.cdk.Token, "CfnPatchBaseline.RuleGroupProperty"]
    """``AWS::SSM::PatchBaseline.ApprovalRules``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-approvalrules
    Stability:
        experimental
    """
    approvedPatches: typing.List[str]
    """``AWS::SSM::PatchBaseline.ApprovedPatches``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-approvedpatches
    Stability:
        experimental
    """
    approvedPatchesComplianceLevel: str
    """``AWS::SSM::PatchBaseline.ApprovedPatchesComplianceLevel``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-approvedpatchescompliancelevel
    Stability:
        experimental
    """
    approvedPatchesEnableNonSecurity: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::SSM::PatchBaseline.ApprovedPatchesEnableNonSecurity``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-approvedpatchesenablenonsecurity
    Stability:
        experimental
    """
    description: str
    """``AWS::SSM::PatchBaseline.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-description
    Stability:
        experimental
    """
    globalFilters: typing.Union[aws_cdk.cdk.Token, "CfnPatchBaseline.PatchFilterGroupProperty"]
    """``AWS::SSM::PatchBaseline.GlobalFilters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-globalfilters
    Stability:
        experimental
    """
    operatingSystem: str
    """``AWS::SSM::PatchBaseline.OperatingSystem``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-operatingsystem
    Stability:
        experimental
    """
    patchGroups: typing.List[str]
    """``AWS::SSM::PatchBaseline.PatchGroups``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-patchgroups
    Stability:
        experimental
    """
    rejectedPatches: typing.List[str]
    """``AWS::SSM::PatchBaseline.RejectedPatches``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-rejectedpatches
    Stability:
        experimental
    """
    rejectedPatchesAction: str
    """``AWS::SSM::PatchBaseline.RejectedPatchesAction``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-rejectedpatchesaction
    Stability:
        experimental
    """
    sources: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnPatchBaseline.PatchSourceProperty"]]]
    """``AWS::SSM::PatchBaseline.Sources``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-sources
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::SSM::PatchBaseline.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnPatchBaselineProps", jsii_struct_bases=[_CfnPatchBaselineProps])
class CfnPatchBaselineProps(_CfnPatchBaselineProps):
    """Properties for defining a ``AWS::SSM::PatchBaseline``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html
    Stability:
        experimental
    """
    name: str
    """``AWS::SSM::PatchBaseline.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-patchbaseline.html#cfn-ssm-patchbaseline-name
    Stability:
        experimental
    """

class CfnResourceDataSync(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ssm.CfnResourceDataSync"):
    """A CloudFormation ``AWS::SSM::ResourceDataSync``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-resourcedatasync.html
    Stability:
        experimental
    cloudformationResource:
        AWS::SSM::ResourceDataSync
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, bucket_name: str, bucket_region: str, sync_format: str, sync_name: str, bucket_prefix: typing.Optional[str]=None, kms_key_arn: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::SSM::ResourceDataSync``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            bucketName: ``AWS::SSM::ResourceDataSync.BucketName``.
            bucketRegion: ``AWS::SSM::ResourceDataSync.BucketRegion``.
            syncFormat: ``AWS::SSM::ResourceDataSync.SyncFormat``.
            syncName: ``AWS::SSM::ResourceDataSync.SyncName``.
            bucketPrefix: ``AWS::SSM::ResourceDataSync.BucketPrefix``.
            kmsKeyArn: ``AWS::SSM::ResourceDataSync.KMSKeyArn``.

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
    def property_overrides(self) -> "CfnResourceDataSyncProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="resourceDataSyncName")
    def resource_data_sync_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "resourceDataSyncName")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnResourceDataSyncProps(jsii.compat.TypedDict, total=False):
    bucketPrefix: str
    """``AWS::SSM::ResourceDataSync.BucketPrefix``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-resourcedatasync.html#cfn-ssm-resourcedatasync-bucketprefix
    Stability:
        experimental
    """
    kmsKeyArn: str
    """``AWS::SSM::ResourceDataSync.KMSKeyArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-resourcedatasync.html#cfn-ssm-resourcedatasync-kmskeyarn
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ssm.CfnResourceDataSyncProps", jsii_struct_bases=[_CfnResourceDataSyncProps])
class CfnResourceDataSyncProps(_CfnResourceDataSyncProps):
    """Properties for defining a ``AWS::SSM::ResourceDataSync``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-resourcedatasync.html
    Stability:
        experimental
    """
    bucketName: str
    """``AWS::SSM::ResourceDataSync.BucketName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-resourcedatasync.html#cfn-ssm-resourcedatasync-bucketname
    Stability:
        experimental
    """

    bucketRegion: str
    """``AWS::SSM::ResourceDataSync.BucketRegion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-resourcedatasync.html#cfn-ssm-resourcedatasync-bucketregion
    Stability:
        experimental
    """

    syncFormat: str
    """``AWS::SSM::ResourceDataSync.SyncFormat``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-resourcedatasync.html#cfn-ssm-resourcedatasync-syncformat
    Stability:
        experimental
    """

    syncName: str
    """``AWS::SSM::ResourceDataSync.SyncName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-resourcedatasync.html#cfn-ssm-resourcedatasync-syncname
    Stability:
        experimental
    """

@jsii.interface(jsii_type="@aws-cdk/aws-ssm.IParameter")
class IParameter(aws_cdk.cdk.IResource, jsii.compat.Protocol):
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


class _IParameterProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
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

    name: str
    """The name of the parameter.

    Default:
        a name will be generated by CloudFormation

    Stability:
        experimental
    """

class ParameterStoreSecureString(aws_cdk.cdk.CfnDynamicReference, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ssm.ParameterStoreSecureString"):
    """References a secret value in AWS Systems Manager Parameter Store.

    It is not possible to retrieve the "latest" value of a secret.
    Use Secrets Manager if you need that ability.

    See:
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/dynamic-references.html
    Stability:
        experimental
    """
    def __init__(self, *, parameter_name: str, version: jsii.Number) -> None:
        """
        Arguments:
            props: -
            parameterName: The name of the parameter store secure string value.
            version: The version number of the value you wish to retrieve.

        Stability:
            experimental
        """
        props: ParameterStoreSecureStringProps = {"parameterName": parameter_name, "version": version}

        jsii.create(ParameterStoreSecureString, self, [props])


@jsii.data_type(jsii_type="@aws-cdk/aws-ssm.ParameterStoreSecureStringProps", jsii_struct_bases=[])
class ParameterStoreSecureStringProps(jsii.compat.TypedDict):
    """Properties for a ParameterStoreValue.

    Stability:
        experimental
    """
    parameterName: str
    """The name of the parameter store secure string value.

    Stability:
        experimental
    """

    version: jsii.Number
    """The version number of the value you wish to retrieve.

    Stability:
        experimental
    """

class ParameterStoreString(aws_cdk.cdk.Construct, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ssm.ParameterStoreString"):
    """References a public value in AWS Systems Manager Parameter Store.

    See:
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/dynamic-references.html
    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, parameter_name: str, version: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            parameterName: The name of the parameter store value.
            version: The version number of the value you wish to retrieve. Default: The latest version will be retrieved.

        Stability:
            experimental
        """
        props: ParameterStoreStringProps = {"parameterName": parameter_name}

        if version is not None:
            props["version"] = version

        jsii.create(ParameterStoreString, self, [scope, id, props])

    @property
    @jsii.member(jsii_name="stringValue")
    def string_value(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "stringValue")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _ParameterStoreStringProps(jsii.compat.TypedDict, total=False):
    version: jsii.Number
    """The version number of the value you wish to retrieve.

    Default:
        The latest version will be retrieved.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ssm.ParameterStoreStringProps", jsii_struct_bases=[_ParameterStoreStringProps])
class ParameterStoreStringProps(_ParameterStoreStringProps):
    """Properties for a ParameterStoreValue.

    Stability:
        experimental
    """
    parameterName: str
    """The name of the parameter store value.

    Stability:
        experimental
    """

@jsii.implements(IStringListParameter, IParameter)
class StringListParameter(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ssm.StringListParameter"):
    """Creates a new StringList SSM Parameter.

    Stability:
        experimental
    resource:
        AWS::SSM::Parameter
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, string_list_value: typing.List[str], allowed_pattern: typing.Optional[str]=None, description: typing.Optional[str]=None, name: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            stringListValue: The values of the parameter. It may not reference another parameter and ``{{}}`` cannot be used in the value.
            allowedPattern: A regular expression used to validate the parameter value. For example, for String types with values restricted to numbers, you can specify the following: ``^\d+$`` Default: no validation is performed
            description: Information about the parameter that you want to add to the system. Default: none
            name: The name of the parameter. Default: a name will be generated by CloudFormation

        Stability:
            experimental
        """
        props: StringListParameterProps = {"stringListValue": string_list_value}

        if allowed_pattern is not None:
            props["allowedPattern"] = allowed_pattern

        if description is not None:
            props["description"] = description

        if name is not None:
            props["name"] = name

        jsii.create(StringListParameter, self, [scope, id, props])

    @jsii.member(jsii_name="fromStringListParameterName")
    @classmethod
    def from_string_list_parameter_name(cls, scope: aws_cdk.cdk.Construct, id: str, string_list_parameter_name: str) -> "IStringListParameter":
        """Imports an external parameter of type string list.

        Arguments:
            scope: -
            id: -
            stringListParameterName: -

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
class StringParameter(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ssm.StringParameter"):
    """Creates a new String SSM Parameter.

    Stability:
        experimental
    resource:
        AWS::SSM::Parameter
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, string_value: str, allowed_pattern: typing.Optional[str]=None, description: typing.Optional[str]=None, name: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            stringValue: The value of the parameter. It may not reference another parameter and ``{{}}`` cannot be used in the value.
            allowedPattern: A regular expression used to validate the parameter value. For example, for String types with values restricted to numbers, you can specify the following: ``^\d+$`` Default: no validation is performed
            description: Information about the parameter that you want to add to the system. Default: none
            name: The name of the parameter. Default: a name will be generated by CloudFormation

        Stability:
            experimental
        """
        props: StringParameterProps = {"stringValue": string_value}

        if allowed_pattern is not None:
            props["allowedPattern"] = allowed_pattern

        if description is not None:
            props["description"] = description

        if name is not None:
            props["name"] = name

        jsii.create(StringParameter, self, [scope, id, props])

    @jsii.member(jsii_name="fromStringParameterName")
    @classmethod
    def from_string_parameter_name(cls, scope: aws_cdk.cdk.Construct, id: str, string_parameter_name: str) -> "IStringParameter":
        """Imports an external string parameter.

        Arguments:
            scope: -
            id: -
            stringParameterName: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromStringParameterName", [scope, id, string_parameter_name])

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

__all__ = ["CfnAssociation", "CfnAssociationProps", "CfnDocument", "CfnDocumentProps", "CfnMaintenanceWindow", "CfnMaintenanceWindowProps", "CfnMaintenanceWindowTask", "CfnMaintenanceWindowTaskProps", "CfnParameter", "CfnParameterProps", "CfnPatchBaseline", "CfnPatchBaselineProps", "CfnResourceDataSync", "CfnResourceDataSyncProps", "IParameter", "IStringListParameter", "IStringParameter", "ParameterOptions", "ParameterStoreSecureString", "ParameterStoreSecureStringProps", "ParameterStoreString", "ParameterStoreStringProps", "StringListParameter", "StringListParameterProps", "StringParameter", "StringParameterProps", "__jsii_assembly__"]

publication.publish()
