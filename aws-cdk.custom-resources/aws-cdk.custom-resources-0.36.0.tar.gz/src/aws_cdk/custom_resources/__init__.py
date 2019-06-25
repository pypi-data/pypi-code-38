import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_cloudformation
import aws_cdk.aws_iam
import aws_cdk.aws_lambda
import aws_cdk.aws_sns
import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/custom-resources", "0.36.0", __name__, "custom-resources@0.36.0.jsii.tgz")
class AwsCustomResource(aws_cdk.core.Construct, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/custom-resources.AwsCustomResource"):
    """
    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, on_create: typing.Optional["AwsSdkCall"]=None, on_delete: typing.Optional["AwsSdkCall"]=None, on_update: typing.Optional["AwsSdkCall"]=None, policy_statements: typing.Optional[typing.List[aws_cdk.aws_iam.PolicyStatement]]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            on_create: The AWS SDK call to make when the resource is created. At least onCreate, onUpdate or onDelete must be specified. Default: the call when the resource is updated
            on_delete: THe AWS SDK call to make when the resource is deleted. Default: no call
            on_update: The AWS SDK call to make when the resource is updated. Default: no call
            policy_statements: The IAM policy statements to allow the different calls. Use only if resource restriction is needed. Default: extract the permissions from the calls

        Stability:
            experimental
        """
        props: AwsCustomResourceProps = {}

        if on_create is not None:
            props["onCreate"] = on_create

        if on_delete is not None:
            props["onDelete"] = on_delete

        if on_update is not None:
            props["onUpdate"] = on_update

        if policy_statements is not None:
            props["policyStatements"] = policy_statements

        jsii.create(AwsCustomResource, self, [scope, id, props])

    @jsii.member(jsii_name="getData")
    def get_data(self, data_path: str) -> aws_cdk.core.IResolvable:
        """Returns response data for the AWS SDK call.

        Example for S3 / listBucket : 'Buckets.0.Name'

        Arguments:
            data_path: the path to the data.

        Stability:
            experimental
        """
        return jsii.invoke(self, "getData", [data_path])


@jsii.data_type(jsii_type="@aws-cdk/custom-resources.AwsCustomResourceProps", jsii_struct_bases=[])
class AwsCustomResourceProps(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    onCreate: "AwsSdkCall"
    """The AWS SDK call to make when the resource is created. At least onCreate, onUpdate or onDelete must be specified.

    Default:
        the call when the resource is updated

    Stability:
        experimental
    """

    onDelete: "AwsSdkCall"
    """THe AWS SDK call to make when the resource is deleted.

    Default:
        no call

    Stability:
        experimental
    """

    onUpdate: "AwsSdkCall"
    """The AWS SDK call to make when the resource is updated.

    Default:
        no call

    Stability:
        experimental
    """

    policyStatements: typing.List[aws_cdk.aws_iam.PolicyStatement]
    """The IAM policy statements to allow the different calls.

    Use only if
    resource restriction is needed.

    Default:
        extract the permissions from the calls

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _AwsSdkCall(jsii.compat.TypedDict, total=False):
    apiVersion: str
    """API version to use for the service.

    Default:
        use latest available API version

    See:
        https://docs.aws.amazon.com/sdk-for-javascript/v2/developer-guide/locking-api-versions.html
    Stability:
        experimental
    """
    catchErrorPattern: str
    """The regex pattern to use to catch API errors.

    The ``code`` property of the
    ``Error`` object will be tested against this pattern. If there is a match an
    error will not be thrown.

    Default:
        do not catch errors

    Stability:
        experimental
    """
    outputPath: str
    """Restrict the data returned by the custom resource to a specific path in the API response.

    Use this to limit the data returned by the custom
    resource if working with API calls that could potentially result in custom
    response objects exceeding the hard limit of 4096 bytes.

    Example for ECS / updateService: 'service.deploymentConfiguration.maximumPercent'

    Default:
        return all data

    Stability:
        experimental
    """
    parameters: typing.Any
    """The parameters for the service action.

    See:
        https://docs.aws.amazon.com/AWSJavaScriptSDK/latest/index.html
    Stability:
        experimental
    """
    physicalResourceId: str
    """The physical resource id of the custom resource for this call.

    Either
    ``physicalResourceId`` or ``physicalResourceIdPath`` must be specified for
    onCreate or onUpdate calls.

    Default:
        no physical resource id

    Stability:
        experimental
    """
    physicalResourceIdPath: str
    """The path to the data in the API call response to use as the physical resource id.

    Either ``physicalResourceId`` or ``physicalResourceIdPath``
    must be specified for onCreate or onUpdate calls.

    Default:
        no path

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/custom-resources.AwsSdkCall", jsii_struct_bases=[_AwsSdkCall])
class AwsSdkCall(_AwsSdkCall):
    """An AWS SDK call.

    Stability:
        experimental
    """
    action: str
    """The service action to call.

    See:
        https://docs.aws.amazon.com/AWSJavaScriptSDK/latest/index.html
    Stability:
        experimental
    """

    service: str
    """The service to call.

    See:
        https://docs.aws.amazon.com/AWSJavaScriptSDK/latest/index.html
    Stability:
        experimental
    """

__all__ = ["AwsCustomResource", "AwsCustomResourceProps", "AwsSdkCall", "__jsii_assembly__"]

publication.publish()
