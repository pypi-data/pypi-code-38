import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_apigateway
import aws_cdk.aws_dynamodb
import aws_cdk.aws_events
import aws_cdk.aws_iam
import aws_cdk.aws_kinesis
import aws_cdk.aws_lambda
import aws_cdk.aws_s3
import aws_cdk.aws_s3_notifications
import aws_cdk.aws_sns
import aws_cdk.aws_sqs
import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-lambda-event-sources", "0.34.0", __name__, "aws-lambda-event-sources@0.34.0.jsii.tgz")
@jsii.implements(aws_cdk.aws_lambda.IEventSource)
class ApiEventSource(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-lambda-event-sources.ApiEventSource"):
    """
    Stability:
        experimental
    """
    def __init__(self, method: str, path: str, *, api_key_required: typing.Optional[bool]=None, authorization_type: typing.Optional[aws_cdk.aws_apigateway.AuthorizationType]=None, authorizer_id: typing.Optional[str]=None, method_responses: typing.Optional[typing.List[aws_cdk.aws_apigateway.MethodResponse]]=None, operation_name: typing.Optional[str]=None, request_parameters: typing.Optional[typing.Mapping[str,bool]]=None) -> None:
        """
        Arguments:
            method: -
            path: -
            options: -
            apiKeyRequired: Indicates whether the method requires clients to submit a valid API key. Default: false
            authorizationType: Method authorization. Default: None open access
            authorizerId: If ``authorizationType`` is ``Custom``, this specifies the ID of the method authorizer resource. NOTE: in the future this will be replaced with an ``IAuthorizer`` construct.
            methodResponses: The responses that can be sent to the client who calls the method. Default: None This property is not required, but if these are not supplied for a Lambda proxy integration, the Lambda function must return a value of the correct format, for the integration response to be correctly mapped to a response to the client.
            operationName: A friendly operation name for the method. For example, you can assign the OperationName of ListPets for the GET /pets method.
            requestParameters: The request parameters that API Gateway accepts. Specify request parameters as key-value pairs (string-to-Boolean mapping), with a source as the key and a Boolean as the value. The Boolean specifies whether a parameter is required. A source must match the format method.request.location.name, where the location is querystring, path, or header, and name is a valid, unique parameter name. Default: None

        Stability:
            experimental
        """
        options: aws_cdk.aws_apigateway.MethodOptions = {}

        if api_key_required is not None:
            options["apiKeyRequired"] = api_key_required

        if authorization_type is not None:
            options["authorizationType"] = authorization_type

        if authorizer_id is not None:
            options["authorizerId"] = authorizer_id

        if method_responses is not None:
            options["methodResponses"] = method_responses

        if operation_name is not None:
            options["operationName"] = operation_name

        if request_parameters is not None:
            options["requestParameters"] = request_parameters

        jsii.create(ApiEventSource, self, [method, path, options])

    @jsii.member(jsii_name="bind")
    def bind(self, target: aws_cdk.aws_lambda.IFunction) -> None:
        """Called by ``lambda.addEventSource`` to allow the event source to bind to this function.

        Arguments:
            target: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [target])

    @property
    @jsii.member(jsii_name="method")
    def method(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "method")

    @property
    @jsii.member(jsii_name="path")
    def path(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "path")

    @property
    @jsii.member(jsii_name="options")
    def options(self) -> typing.Optional[aws_cdk.aws_apigateway.MethodOptions]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "options")


@jsii.implements(aws_cdk.aws_lambda.IEventSource)
class DynamoEventSource(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-lambda-event-sources.DynamoEventSource"):
    """Use an Amazon DynamoDB stream as an event source for AWS Lambda.

    Stability:
        experimental
    """
    def __init__(self, table: aws_cdk.aws_dynamodb.Table, *, starting_position: aws_cdk.aws_lambda.StartingPosition, batch_size: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            table: -
            props: -
            startingPosition: Where to begin consuming the DynamoDB stream.
            batchSize: The largest number of records that AWS Lambda will retrieve from your event source at the time of invoking your function. Your function receives an event with all the retrieved records. Valid Range: Minimum value of 1. Maximum value of 1000. Default: 100

        Stability:
            experimental
        """
        props: DynamoEventSourceProps = {"startingPosition": starting_position}

        if batch_size is not None:
            props["batchSize"] = batch_size

        jsii.create(DynamoEventSource, self, [table, props])

    @jsii.member(jsii_name="bind")
    def bind(self, target: aws_cdk.aws_lambda.IFunction) -> None:
        """Called by ``lambda.addEventSource`` to allow the event source to bind to this function.

        Arguments:
            target: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [target])

    @property
    @jsii.member(jsii_name="props")
    def props(self) -> "DynamoEventSourceProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "props")

    @property
    @jsii.member(jsii_name="table")
    def table(self) -> aws_cdk.aws_dynamodb.Table:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "table")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _DynamoEventSourceProps(jsii.compat.TypedDict, total=False):
    batchSize: jsii.Number
    """The largest number of records that AWS Lambda will retrieve from your event source at the time of invoking your function.

    Your function receives an
    event with all the retrieved records.

    Valid Range: Minimum value of 1. Maximum value of 1000.

    Default:
        100

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-lambda-event-sources.DynamoEventSourceProps", jsii_struct_bases=[_DynamoEventSourceProps])
class DynamoEventSourceProps(_DynamoEventSourceProps):
    """
    Stability:
        experimental
    """
    startingPosition: aws_cdk.aws_lambda.StartingPosition
    """Where to begin consuming the DynamoDB stream.

    Stability:
        experimental
    """

@jsii.implements(aws_cdk.aws_lambda.IEventSource)
class KinesisEventSource(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-lambda-event-sources.KinesisEventSource"):
    """Use an Amazon Kinesis stream as an event source for AWS Lambda.

    Stability:
        experimental
    """
    def __init__(self, stream: aws_cdk.aws_kinesis.IStream, *, starting_position: aws_cdk.aws_lambda.StartingPosition, batch_size: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            stream: -
            props: -
            startingPosition: Where to begin consuming the Kinesis stream.
            batchSize: The largest number of records that AWS Lambda will retrieve from your event source at the time of invoking your function. Your function receives an event with all the retrieved records. Valid Range: Minimum value of 1. Maximum value of 10000. Default: 100

        Stability:
            experimental
        """
        props: KinesisEventSourceProps = {"startingPosition": starting_position}

        if batch_size is not None:
            props["batchSize"] = batch_size

        jsii.create(KinesisEventSource, self, [stream, props])

    @jsii.member(jsii_name="bind")
    def bind(self, target: aws_cdk.aws_lambda.IFunction) -> None:
        """Called by ``lambda.addEventSource`` to allow the event source to bind to this function.

        Arguments:
            target: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [target])

    @property
    @jsii.member(jsii_name="props")
    def props(self) -> "KinesisEventSourceProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "props")

    @property
    @jsii.member(jsii_name="stream")
    def stream(self) -> aws_cdk.aws_kinesis.IStream:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "stream")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _KinesisEventSourceProps(jsii.compat.TypedDict, total=False):
    batchSize: jsii.Number
    """The largest number of records that AWS Lambda will retrieve from your event source at the time of invoking your function.

    Your function receives an
    event with all the retrieved records.

    Valid Range: Minimum value of 1. Maximum value of 10000.

    Default:
        100

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-lambda-event-sources.KinesisEventSourceProps", jsii_struct_bases=[_KinesisEventSourceProps])
class KinesisEventSourceProps(_KinesisEventSourceProps):
    """
    Stability:
        experimental
    """
    startingPosition: aws_cdk.aws_lambda.StartingPosition
    """Where to begin consuming the Kinesis stream.

    Stability:
        experimental
    """

@jsii.implements(aws_cdk.aws_lambda.IEventSource)
class S3EventSource(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-lambda-event-sources.S3EventSource"):
    """Use S3 bucket notifications as an event source for AWS Lambda.

    Stability:
        experimental
    """
    def __init__(self, bucket: aws_cdk.aws_s3.Bucket, *, events: typing.List[aws_cdk.aws_s3.EventType], filters: typing.Optional[typing.List[aws_cdk.aws_s3.NotificationKeyFilter]]=None) -> None:
        """
        Arguments:
            bucket: -
            props: -
            events: The s3 event types that will trigger the notification.
            filters: S3 object key filter rules to determine which objects trigger this event. Each filter must include a ``prefix`` and/or ``suffix`` that will be matched against the s3 object key. Refer to the S3 Developer Guide for details about allowed filter rules.

        Stability:
            experimental
        """
        props: S3EventSourceProps = {"events": events}

        if filters is not None:
            props["filters"] = filters

        jsii.create(S3EventSource, self, [bucket, props])

    @jsii.member(jsii_name="bind")
    def bind(self, target: aws_cdk.aws_lambda.IFunction) -> None:
        """Called by ``lambda.addEventSource`` to allow the event source to bind to this function.

        Arguments:
            target: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [target])

    @property
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> aws_cdk.aws_s3.Bucket:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "bucket")

    @property
    @jsii.member(jsii_name="props")
    def props(self) -> "S3EventSourceProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "props")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _S3EventSourceProps(jsii.compat.TypedDict, total=False):
    filters: typing.List[aws_cdk.aws_s3.NotificationKeyFilter]
    """S3 object key filter rules to determine which objects trigger this event. Each filter must include a ``prefix`` and/or ``suffix`` that will be matched against the s3 object key. Refer to the S3 Developer Guide for details about allowed filter rules.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-lambda-event-sources.S3EventSourceProps", jsii_struct_bases=[_S3EventSourceProps])
class S3EventSourceProps(_S3EventSourceProps):
    """
    Stability:
        experimental
    """
    events: typing.List[aws_cdk.aws_s3.EventType]
    """The s3 event types that will trigger the notification.

    Stability:
        experimental
    """

@jsii.implements(aws_cdk.aws_lambda.IEventSource)
class SnsEventSource(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-lambda-event-sources.SnsEventSource"):
    """Use an Amazon SNS topic as an event source for AWS Lambda.

    Stability:
        experimental
    """
    def __init__(self, topic: aws_cdk.aws_sns.ITopic) -> None:
        """
        Arguments:
            topic: -

        Stability:
            experimental
        """
        jsii.create(SnsEventSource, self, [topic])

    @jsii.member(jsii_name="bind")
    def bind(self, target: aws_cdk.aws_lambda.IFunction) -> None:
        """Called by ``lambda.addEventSource`` to allow the event source to bind to this function.

        Arguments:
            target: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [target])

    @property
    @jsii.member(jsii_name="topic")
    def topic(self) -> aws_cdk.aws_sns.ITopic:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "topic")


@jsii.implements(aws_cdk.aws_lambda.IEventSource)
class SqsEventSource(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-lambda-event-sources.SqsEventSource"):
    """Use an Amazon SQS queue as an event source for AWS Lambda.

    Stability:
        experimental
    """
    def __init__(self, queue: aws_cdk.aws_sqs.IQueue, *, batch_size: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            queue: -
            props: -
            batchSize: The largest number of records that AWS Lambda will retrieve from your event source at the time of invoking your function. Your function receives an event with all the retrieved records. Valid Range: Minimum value of 1. Maximum value of 10. Default: 10

        Stability:
            experimental
        """
        props: SqsEventSourceProps = {}

        if batch_size is not None:
            props["batchSize"] = batch_size

        jsii.create(SqsEventSource, self, [queue, props])

    @jsii.member(jsii_name="bind")
    def bind(self, target: aws_cdk.aws_lambda.IFunction) -> None:
        """Called by ``lambda.addEventSource`` to allow the event source to bind to this function.

        Arguments:
            target: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [target])

    @property
    @jsii.member(jsii_name="props")
    def props(self) -> "SqsEventSourceProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "props")

    @property
    @jsii.member(jsii_name="queue")
    def queue(self) -> aws_cdk.aws_sqs.IQueue:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "queue")


@jsii.data_type(jsii_type="@aws-cdk/aws-lambda-event-sources.SqsEventSourceProps", jsii_struct_bases=[])
class SqsEventSourceProps(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    batchSize: jsii.Number
    """The largest number of records that AWS Lambda will retrieve from your event source at the time of invoking your function.

    Your function receives an
    event with all the retrieved records.

    Valid Range: Minimum value of 1. Maximum value of 10.

    Default:
        10

    Stability:
        experimental
    """

__all__ = ["ApiEventSource", "DynamoEventSource", "DynamoEventSourceProps", "KinesisEventSource", "KinesisEventSourceProps", "S3EventSource", "S3EventSourceProps", "SnsEventSource", "SqsEventSource", "SqsEventSourceProps", "__jsii_assembly__"]

publication.publish()
