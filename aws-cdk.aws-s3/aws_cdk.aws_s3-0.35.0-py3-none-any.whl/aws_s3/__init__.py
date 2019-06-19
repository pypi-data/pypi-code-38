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
import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-s3", "0.35.0", __name__, "aws-s3@0.35.0.jsii.tgz")
class BlockPublicAccess(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-s3.BlockPublicAccess"):
    """
    Stability:
        experimental
    """
    def __init__(self, *, block_public_acls: typing.Optional[bool]=None, block_public_policy: typing.Optional[bool]=None, ignore_public_acls: typing.Optional[bool]=None, restrict_public_buckets: typing.Optional[bool]=None) -> None:
        """
        Arguments:
            options: -
            blockPublicAcls: Whether to block public ACLs.
            blockPublicPolicy: Whether to block public policy.
            ignorePublicAcls: Whether to ignore public ACLs.
            restrictPublicBuckets: Whether to restrict public access.

        Stability:
            experimental
        """
        options: BlockPublicAccessOptions = {}

        if block_public_acls is not None:
            options["blockPublicAcls"] = block_public_acls

        if block_public_policy is not None:
            options["blockPublicPolicy"] = block_public_policy

        if ignore_public_acls is not None:
            options["ignorePublicAcls"] = ignore_public_acls

        if restrict_public_buckets is not None:
            options["restrictPublicBuckets"] = restrict_public_buckets

        jsii.create(BlockPublicAccess, self, [options])

    @classproperty
    @jsii.member(jsii_name="BlockAcls")
    def BLOCK_ACLS(cls) -> "BlockPublicAccess":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "BlockAcls")

    @classproperty
    @jsii.member(jsii_name="BlockAll")
    def BLOCK_ALL(cls) -> "BlockPublicAccess":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "BlockAll")

    @property
    @jsii.member(jsii_name="blockPublicAcls")
    def block_public_acls(self) -> typing.Optional[bool]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "blockPublicAcls")

    @block_public_acls.setter
    def block_public_acls(self, value: typing.Optional[bool]):
        return jsii.set(self, "blockPublicAcls", value)

    @property
    @jsii.member(jsii_name="blockPublicPolicy")
    def block_public_policy(self) -> typing.Optional[bool]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "blockPublicPolicy")

    @block_public_policy.setter
    def block_public_policy(self, value: typing.Optional[bool]):
        return jsii.set(self, "blockPublicPolicy", value)

    @property
    @jsii.member(jsii_name="ignorePublicAcls")
    def ignore_public_acls(self) -> typing.Optional[bool]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "ignorePublicAcls")

    @ignore_public_acls.setter
    def ignore_public_acls(self, value: typing.Optional[bool]):
        return jsii.set(self, "ignorePublicAcls", value)

    @property
    @jsii.member(jsii_name="restrictPublicBuckets")
    def restrict_public_buckets(self) -> typing.Optional[bool]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "restrictPublicBuckets")

    @restrict_public_buckets.setter
    def restrict_public_buckets(self, value: typing.Optional[bool]):
        return jsii.set(self, "restrictPublicBuckets", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-s3.BlockPublicAccessOptions", jsii_struct_bases=[])
class BlockPublicAccessOptions(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    blockPublicAcls: bool
    """Whether to block public ACLs.

    See:
        https://docs.aws.amazon.com/AmazonS3/latest/dev/access-control-block-public-access.html#access-control-block-public-access-options
    Stability:
        experimental
    """

    blockPublicPolicy: bool
    """Whether to block public policy.

    See:
        https://docs.aws.amazon.com/AmazonS3/latest/dev/access-control-block-public-access.html#access-control-block-public-access-options
    Stability:
        experimental
    """

    ignorePublicAcls: bool
    """Whether to ignore public ACLs.

    See:
        https://docs.aws.amazon.com/AmazonS3/latest/dev/access-control-block-public-access.html#access-control-block-public-access-options
    Stability:
        experimental
    """

    restrictPublicBuckets: bool
    """Whether to restrict public access.

    See:
        https://docs.aws.amazon.com/AmazonS3/latest/dev/access-control-block-public-access.html#access-control-block-public-access-options
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-s3.BucketAttributes", jsii_struct_bases=[])
class BucketAttributes(jsii.compat.TypedDict, total=False):
    """A reference to a bucket.

    The easiest way to instantiate is to call
    ``bucket.export()``. Then, the consumer can use ``Bucket.import(this, ref)`` and
    get a ``Bucket``.

    Stability:
        experimental
    """
    bucketArn: str
    """The ARN of the bucket.

    At least one of bucketArn or bucketName must be
    defined in order to initialize a bucket ref.

    Stability:
        experimental
    """

    bucketDomainName: str
    """The domain name of the bucket.

    Default:
        Inferred from bucket name

    Stability:
        experimental
    """

    bucketDualStackDomainName: str
    """The IPv6 DNS name of the specified bucket.

    Stability:
        experimental
    """

    bucketName: str
    """The name of the bucket.

    If the underlying value of ARN is a string, the
    name will be parsed from the ARN. Otherwise, the name is optional, but
    some features that require the bucket name such as auto-creating a bucket
    policy, won't work.

    Stability:
        experimental
    """

    bucketRegionalDomainName: str
    """The regional domain name of the specified bucket.

    Stability:
        experimental
    """

    bucketWebsiteNewUrlFormat: bool
    """The format of the website URL of the bucket.

    This should be true for
    regions launched since 2014.

    Default:
        false

    Stability:
        experimental
    """

    bucketWebsiteUrl: str
    """The website URL of the bucket (if static web hosting is enabled).

    Default:
        Inferred from bucket name

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-s3.BucketEncryption")
class BucketEncryption(enum.Enum):
    """What kind of server-side encryption to apply to this bucket.

    Stability:
        experimental
    """
    Unencrypted = "Unencrypted"
    """Objects in the bucket are not encrypted.

    Stability:
        experimental
    """
    KmsManaged = "KmsManaged"
    """Server-side KMS encryption with a master key managed by KMS.

    Stability:
        experimental
    """
    S3Managed = "S3Managed"
    """Server-side encryption with a master key managed by S3.

    Stability:
        experimental
    """
    Kms = "Kms"
    """Server-side encryption with a KMS key managed by the user. If ``encryptionKey`` is specified, this key will be used, otherwise, one will be defined.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _BucketMetrics(jsii.compat.TypedDict, total=False):
    prefix: str
    """The prefix that an object must have to be included in the metrics results.

    Stability:
        experimental
    """
    tagFilters: typing.Mapping[str,typing.Any]
    """Specifies a list of tag filters to use as a metrics configuration filter. The metrics configuration includes only objects that meet the filter's criteria.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-s3.BucketMetrics", jsii_struct_bases=[_BucketMetrics])
class BucketMetrics(_BucketMetrics):
    """Specifies a metrics configuration for the CloudWatch request metrics from an Amazon S3 bucket.

    Stability:
        experimental
    """
    id: str
    """The ID used to identify the metrics configuration.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _BucketNotificationDestinationConfig(jsii.compat.TypedDict, total=False):
    dependencies: typing.List[aws_cdk.cdk.IDependable]
    """Any additional dependencies that should be resolved before the bucket notification can be configured (for example, the SNS Topic Policy resource).

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-s3.BucketNotificationDestinationConfig", jsii_struct_bases=[_BucketNotificationDestinationConfig])
class BucketNotificationDestinationConfig(_BucketNotificationDestinationConfig):
    """Represents the properties of a notification destination.

    Stability:
        experimental
    """
    arn: str
    """The ARN of the destination (i.e. Lambda, SNS, SQS).

    Stability:
        experimental
    """

    type: "BucketNotificationDestinationType"
    """The notification type.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-s3.BucketNotificationDestinationType")
class BucketNotificationDestinationType(enum.Enum):
    """Supported types of notification destinations.

    Stability:
        experimental
    """
    Lambda = "Lambda"
    """
    Stability:
        experimental
    """
    Queue = "Queue"
    """
    Stability:
        experimental
    """
    Topic = "Topic"
    """
    Stability:
        experimental
    """

class BucketPolicy(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-s3.BucketPolicy"):
    """Applies an Amazon S3 bucket policy to an Amazon S3 bucket.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, bucket: "IBucket") -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            bucket: The Amazon S3 bucket that the policy applies to.

        Stability:
            experimental
        """
        props: BucketPolicyProps = {"bucket": bucket}

        jsii.create(BucketPolicy, self, [scope, id, props])

    @property
    @jsii.member(jsii_name="document")
    def document(self) -> aws_cdk.aws_iam.PolicyDocument:
        """A policy document containing permissions to add to the specified bucket. For more information, see Access Policy Language Overview in the Amazon Simple Storage Service Developer Guide.

        Stability:
            experimental
        """
        return jsii.get(self, "document")


@jsii.data_type(jsii_type="@aws-cdk/aws-s3.BucketPolicyProps", jsii_struct_bases=[])
class BucketPolicyProps(jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    bucket: "IBucket"
    """The Amazon S3 bucket that the policy applies to.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-s3.BucketProps", jsii_struct_bases=[])
class BucketProps(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    blockPublicAccess: "BlockPublicAccess"
    """The block public access configuration of this bucket.

    Default:
        false New buckets and objects don't allow public access, but users can modify bucket
        policies or object permissions to allow public access.

    See:
        https://docs.aws.amazon.com/AmazonS3/latest/dev/access-control-block-public-access.html
    Stability:
        experimental
    """

    bucketName: aws_cdk.cdk.PhysicalName
    """Physical name of this bucket.

    Default:
        - Assigned by CloudFormation (recommended).

    Stability:
        experimental
    """

    cors: typing.List["CorsRule"]
    """The CORS configuration of this bucket.

    Default:
        - No CORS configuration.

    See:
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-cors.html
    Stability:
        experimental
    """

    encryption: "BucketEncryption"
    """The kind of server-side encryption to apply to this bucket.

    If you choose KMS, you can specify a KMS key via ``encryptionKey``. If
    encryption key is not specified, a key will automatically be created.

    Default:
        - ``Kms`` if ``encryptionKey`` is specified, or ``Unencrypted`` otherwise.

    Stability:
        experimental
    """

    encryptionKey: aws_cdk.aws_kms.IKey
    """External KMS key to use for bucket encryption.

    The 'encryption' property must be either not specified or set to "Kms".
    An error will be emitted if encryption is set to "Unencrypted" or
    "Managed".

    Default:
        - If encryption is set to "Kms" and this property is undefined,
          a new KMS key will be created and associated with this bucket.

    Stability:
        experimental
    """

    lifecycleRules: typing.List["LifecycleRule"]
    """Rules that define how Amazon S3 manages objects during their lifetime.

    Default:
        - No lifecycle rules.

    Stability:
        experimental
    """

    metrics: typing.List["BucketMetrics"]
    """The metrics configuration of this bucket.

    Default:
        - No metrics configuration.

    See:
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-metricsconfiguration.html
    Stability:
        experimental
    """

    publicReadAccess: bool
    """Grants public read access to all objects in the bucket. Similar to calling ``bucket.grantPublicAccess()``.

    Default:
        false

    Stability:
        experimental
    """

    removalPolicy: aws_cdk.cdk.RemovalPolicy
    """Policy to apply when the bucket is removed from this stack.

    Default:
        - The bucket will be orphaned.

    Stability:
        experimental
    """

    versioned: bool
    """Whether this bucket should have versioning turned on or not.

    Default:
        false

    Stability:
        experimental
    """

    websiteErrorDocument: str
    """The name of the error document (e.g. "404.html") for the website. ``websiteIndexDocument`` must also be set if this is set.

    Default:
        - No error document.

    Stability:
        experimental
    """

    websiteIndexDocument: str
    """The name of the index document (e.g. "index.html") for the website. Enables static website hosting for this bucket.

    Default:
        - No index document.

    Stability:
        experimental
    """

class CfnBucket(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-s3.CfnBucket"):
    """A CloudFormation ``AWS::S3::Bucket``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html
    Stability:
        experimental
    cloudformationResource:
        AWS::S3::Bucket
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, accelerate_configuration: typing.Optional[typing.Union[typing.Optional["AccelerateConfigurationProperty"], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, access_control: typing.Optional[str]=None, analytics_configurations: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "AnalyticsConfigurationProperty"]]]]]=None, bucket_encryption: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["BucketEncryptionProperty"]]]=None, bucket_name: typing.Optional[str]=None, cors_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["CorsConfigurationProperty"]]]=None, inventory_configurations: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "InventoryConfigurationProperty"]]]]]=None, lifecycle_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["LifecycleConfigurationProperty"]]]=None, logging_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["LoggingConfigurationProperty"]]]=None, metrics_configurations: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "MetricsConfigurationProperty"]]]]]=None, notification_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["NotificationConfigurationProperty"]]]=None, object_lock_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["ObjectLockConfigurationProperty"]]]=None, object_lock_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, public_access_block_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["PublicAccessBlockConfigurationProperty"]]]=None, replication_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["ReplicationConfigurationProperty"]]]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, versioning_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["VersioningConfigurationProperty"]]]=None, website_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["WebsiteConfigurationProperty"]]]=None) -> None:
        """Create a new ``AWS::S3::Bucket``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            accelerateConfiguration: ``AWS::S3::Bucket.AccelerateConfiguration``.
            accessControl: ``AWS::S3::Bucket.AccessControl``.
            analyticsConfigurations: ``AWS::S3::Bucket.AnalyticsConfigurations``.
            bucketEncryption: ``AWS::S3::Bucket.BucketEncryption``.
            bucketName: ``AWS::S3::Bucket.BucketName``.
            corsConfiguration: ``AWS::S3::Bucket.CorsConfiguration``.
            inventoryConfigurations: ``AWS::S3::Bucket.InventoryConfigurations``.
            lifecycleConfiguration: ``AWS::S3::Bucket.LifecycleConfiguration``.
            loggingConfiguration: ``AWS::S3::Bucket.LoggingConfiguration``.
            metricsConfigurations: ``AWS::S3::Bucket.MetricsConfigurations``.
            notificationConfiguration: ``AWS::S3::Bucket.NotificationConfiguration``.
            objectLockConfiguration: ``AWS::S3::Bucket.ObjectLockConfiguration``.
            objectLockEnabled: ``AWS::S3::Bucket.ObjectLockEnabled``.
            publicAccessBlockConfiguration: ``AWS::S3::Bucket.PublicAccessBlockConfiguration``.
            replicationConfiguration: ``AWS::S3::Bucket.ReplicationConfiguration``.
            tags: ``AWS::S3::Bucket.Tags``.
            versioningConfiguration: ``AWS::S3::Bucket.VersioningConfiguration``.
            websiteConfiguration: ``AWS::S3::Bucket.WebsiteConfiguration``.

        Stability:
            experimental
        """
        props: CfnBucketProps = {}

        if accelerate_configuration is not None:
            props["accelerateConfiguration"] = accelerate_configuration

        if access_control is not None:
            props["accessControl"] = access_control

        if analytics_configurations is not None:
            props["analyticsConfigurations"] = analytics_configurations

        if bucket_encryption is not None:
            props["bucketEncryption"] = bucket_encryption

        if bucket_name is not None:
            props["bucketName"] = bucket_name

        if cors_configuration is not None:
            props["corsConfiguration"] = cors_configuration

        if inventory_configurations is not None:
            props["inventoryConfigurations"] = inventory_configurations

        if lifecycle_configuration is not None:
            props["lifecycleConfiguration"] = lifecycle_configuration

        if logging_configuration is not None:
            props["loggingConfiguration"] = logging_configuration

        if metrics_configurations is not None:
            props["metricsConfigurations"] = metrics_configurations

        if notification_configuration is not None:
            props["notificationConfiguration"] = notification_configuration

        if object_lock_configuration is not None:
            props["objectLockConfiguration"] = object_lock_configuration

        if object_lock_enabled is not None:
            props["objectLockEnabled"] = object_lock_enabled

        if public_access_block_configuration is not None:
            props["publicAccessBlockConfiguration"] = public_access_block_configuration

        if replication_configuration is not None:
            props["replicationConfiguration"] = replication_configuration

        if tags is not None:
            props["tags"] = tags

        if versioning_configuration is not None:
            props["versioningConfiguration"] = versioning_configuration

        if website_configuration is not None:
            props["websiteConfiguration"] = website_configuration

        jsii.create(CfnBucket, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="cfnResourceTypeName")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            experimental
        """
        return jsii.sget(cls, "cfnResourceTypeName")

    @property
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "attrArn")

    @property
    @jsii.member(jsii_name="attrDomainName")
    def attr_domain_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            DomainName
        """
        return jsii.get(self, "attrDomainName")

    @property
    @jsii.member(jsii_name="attrDualStackDomainName")
    def attr_dual_stack_domain_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            DualStackDomainName
        """
        return jsii.get(self, "attrDualStackDomainName")

    @property
    @jsii.member(jsii_name="attrRegionalDomainName")
    def attr_regional_domain_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            RegionalDomainName
        """
        return jsii.get(self, "attrRegionalDomainName")

    @property
    @jsii.member(jsii_name="attrWebsiteUrl")
    def attr_website_url(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            WebsiteURL
        """
        return jsii.get(self, "attrWebsiteUrl")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.cdk.TagManager:
        """``AWS::S3::Bucket.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="accelerateConfiguration")
    def accelerate_configuration(self) -> typing.Optional[typing.Union[typing.Optional["AccelerateConfigurationProperty"], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::S3::Bucket.AccelerateConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-accelerateconfiguration
        Stability:
            experimental
        """
        return jsii.get(self, "accelerateConfiguration")

    @accelerate_configuration.setter
    def accelerate_configuration(self, value: typing.Optional[typing.Union[typing.Optional["AccelerateConfigurationProperty"], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "accelerateConfiguration", value)

    @property
    @jsii.member(jsii_name="accessControl")
    def access_control(self) -> typing.Optional[str]:
        """``AWS::S3::Bucket.AccessControl``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-accesscontrol
        Stability:
            experimental
        """
        return jsii.get(self, "accessControl")

    @access_control.setter
    def access_control(self, value: typing.Optional[str]):
        return jsii.set(self, "accessControl", value)

    @property
    @jsii.member(jsii_name="analyticsConfigurations")
    def analytics_configurations(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "AnalyticsConfigurationProperty"]]]]]:
        """``AWS::S3::Bucket.AnalyticsConfigurations``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-analyticsconfigurations
        Stability:
            experimental
        """
        return jsii.get(self, "analyticsConfigurations")

    @analytics_configurations.setter
    def analytics_configurations(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "AnalyticsConfigurationProperty"]]]]]):
        return jsii.set(self, "analyticsConfigurations", value)

    @property
    @jsii.member(jsii_name="bucketEncryption")
    def bucket_encryption(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["BucketEncryptionProperty"]]]:
        """``AWS::S3::Bucket.BucketEncryption``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-bucketencryption
        Stability:
            experimental
        """
        return jsii.get(self, "bucketEncryption")

    @bucket_encryption.setter
    def bucket_encryption(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["BucketEncryptionProperty"]]]):
        return jsii.set(self, "bucketEncryption", value)

    @property
    @jsii.member(jsii_name="bucketName")
    def bucket_name(self) -> typing.Optional[str]:
        """``AWS::S3::Bucket.BucketName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-name
        Stability:
            experimental
        """
        return jsii.get(self, "bucketName")

    @bucket_name.setter
    def bucket_name(self, value: typing.Optional[str]):
        return jsii.set(self, "bucketName", value)

    @property
    @jsii.member(jsii_name="corsConfiguration")
    def cors_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["CorsConfigurationProperty"]]]:
        """``AWS::S3::Bucket.CorsConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-crossoriginconfig
        Stability:
            experimental
        """
        return jsii.get(self, "corsConfiguration")

    @cors_configuration.setter
    def cors_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["CorsConfigurationProperty"]]]):
        return jsii.set(self, "corsConfiguration", value)

    @property
    @jsii.member(jsii_name="inventoryConfigurations")
    def inventory_configurations(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "InventoryConfigurationProperty"]]]]]:
        """``AWS::S3::Bucket.InventoryConfigurations``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-inventoryconfigurations
        Stability:
            experimental
        """
        return jsii.get(self, "inventoryConfigurations")

    @inventory_configurations.setter
    def inventory_configurations(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "InventoryConfigurationProperty"]]]]]):
        return jsii.set(self, "inventoryConfigurations", value)

    @property
    @jsii.member(jsii_name="lifecycleConfiguration")
    def lifecycle_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["LifecycleConfigurationProperty"]]]:
        """``AWS::S3::Bucket.LifecycleConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-lifecycleconfig
        Stability:
            experimental
        """
        return jsii.get(self, "lifecycleConfiguration")

    @lifecycle_configuration.setter
    def lifecycle_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["LifecycleConfigurationProperty"]]]):
        return jsii.set(self, "lifecycleConfiguration", value)

    @property
    @jsii.member(jsii_name="loggingConfiguration")
    def logging_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["LoggingConfigurationProperty"]]]:
        """``AWS::S3::Bucket.LoggingConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-loggingconfig
        Stability:
            experimental
        """
        return jsii.get(self, "loggingConfiguration")

    @logging_configuration.setter
    def logging_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["LoggingConfigurationProperty"]]]):
        return jsii.set(self, "loggingConfiguration", value)

    @property
    @jsii.member(jsii_name="metricsConfigurations")
    def metrics_configurations(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "MetricsConfigurationProperty"]]]]]:
        """``AWS::S3::Bucket.MetricsConfigurations``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-metricsconfigurations
        Stability:
            experimental
        """
        return jsii.get(self, "metricsConfigurations")

    @metrics_configurations.setter
    def metrics_configurations(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "MetricsConfigurationProperty"]]]]]):
        return jsii.set(self, "metricsConfigurations", value)

    @property
    @jsii.member(jsii_name="notificationConfiguration")
    def notification_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["NotificationConfigurationProperty"]]]:
        """``AWS::S3::Bucket.NotificationConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-notification
        Stability:
            experimental
        """
        return jsii.get(self, "notificationConfiguration")

    @notification_configuration.setter
    def notification_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["NotificationConfigurationProperty"]]]):
        return jsii.set(self, "notificationConfiguration", value)

    @property
    @jsii.member(jsii_name="objectLockConfiguration")
    def object_lock_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["ObjectLockConfigurationProperty"]]]:
        """``AWS::S3::Bucket.ObjectLockConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-objectlockconfiguration
        Stability:
            experimental
        """
        return jsii.get(self, "objectLockConfiguration")

    @object_lock_configuration.setter
    def object_lock_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["ObjectLockConfigurationProperty"]]]):
        return jsii.set(self, "objectLockConfiguration", value)

    @property
    @jsii.member(jsii_name="objectLockEnabled")
    def object_lock_enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::S3::Bucket.ObjectLockEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-objectlockenabled
        Stability:
            experimental
        """
        return jsii.get(self, "objectLockEnabled")

    @object_lock_enabled.setter
    def object_lock_enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "objectLockEnabled", value)

    @property
    @jsii.member(jsii_name="publicAccessBlockConfiguration")
    def public_access_block_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["PublicAccessBlockConfigurationProperty"]]]:
        """``AWS::S3::Bucket.PublicAccessBlockConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-publicaccessblockconfiguration
        Stability:
            experimental
        """
        return jsii.get(self, "publicAccessBlockConfiguration")

    @public_access_block_configuration.setter
    def public_access_block_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["PublicAccessBlockConfigurationProperty"]]]):
        return jsii.set(self, "publicAccessBlockConfiguration", value)

    @property
    @jsii.member(jsii_name="replicationConfiguration")
    def replication_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["ReplicationConfigurationProperty"]]]:
        """``AWS::S3::Bucket.ReplicationConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-replicationconfiguration
        Stability:
            experimental
        """
        return jsii.get(self, "replicationConfiguration")

    @replication_configuration.setter
    def replication_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["ReplicationConfigurationProperty"]]]):
        return jsii.set(self, "replicationConfiguration", value)

    @property
    @jsii.member(jsii_name="versioningConfiguration")
    def versioning_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["VersioningConfigurationProperty"]]]:
        """``AWS::S3::Bucket.VersioningConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-versioning
        Stability:
            experimental
        """
        return jsii.get(self, "versioningConfiguration")

    @versioning_configuration.setter
    def versioning_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["VersioningConfigurationProperty"]]]):
        return jsii.set(self, "versioningConfiguration", value)

    @property
    @jsii.member(jsii_name="websiteConfiguration")
    def website_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["WebsiteConfigurationProperty"]]]:
        """``AWS::S3::Bucket.WebsiteConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-websiteconfiguration
        Stability:
            experimental
        """
        return jsii.get(self, "websiteConfiguration")

    @website_configuration.setter
    def website_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["WebsiteConfigurationProperty"]]]):
        return jsii.set(self, "websiteConfiguration", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.AbortIncompleteMultipartUploadProperty", jsii_struct_bases=[])
    class AbortIncompleteMultipartUploadProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-abortincompletemultipartupload.html
        Stability:
            experimental
        """
        daysAfterInitiation: jsii.Number
        """``CfnBucket.AbortIncompleteMultipartUploadProperty.DaysAfterInitiation``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-abortincompletemultipartupload.html#cfn-s3-bucket-abortincompletemultipartupload-daysafterinitiation
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.AccelerateConfigurationProperty", jsii_struct_bases=[])
    class AccelerateConfigurationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-accelerateconfiguration.html
        Stability:
            experimental
        """
        accelerationStatus: str
        """``CfnBucket.AccelerateConfigurationProperty.AccelerationStatus``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-accelerateconfiguration.html#cfn-s3-bucket-accelerateconfiguration-accelerationstatus
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.AccessControlTranslationProperty", jsii_struct_bases=[])
    class AccessControlTranslationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-accesscontroltranslation.html
        Stability:
            experimental
        """
        owner: str
        """``CfnBucket.AccessControlTranslationProperty.Owner``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-accesscontroltranslation.html#cfn-s3-bucket-accesscontroltranslation-owner
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _AnalyticsConfigurationProperty(jsii.compat.TypedDict, total=False):
        prefix: str
        """``CfnBucket.AnalyticsConfigurationProperty.Prefix``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-analyticsconfiguration.html#cfn-s3-bucket-analyticsconfiguration-prefix
        Stability:
            experimental
        """
        tagFilters: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.TagFilterProperty"]]]
        """``CfnBucket.AnalyticsConfigurationProperty.TagFilters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-analyticsconfiguration.html#cfn-s3-bucket-analyticsconfiguration-tagfilters
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.AnalyticsConfigurationProperty", jsii_struct_bases=[_AnalyticsConfigurationProperty])
    class AnalyticsConfigurationProperty(_AnalyticsConfigurationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-analyticsconfiguration.html
        Stability:
            experimental
        """
        id: str
        """``CfnBucket.AnalyticsConfigurationProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-analyticsconfiguration.html#cfn-s3-bucket-analyticsconfiguration-id
        Stability:
            experimental
        """

        storageClassAnalysis: typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.StorageClassAnalysisProperty"]
        """``CfnBucket.AnalyticsConfigurationProperty.StorageClassAnalysis``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-analyticsconfiguration.html#cfn-s3-bucket-analyticsconfiguration-storageclassanalysis
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.BucketEncryptionProperty", jsii_struct_bases=[])
    class BucketEncryptionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-bucketencryption.html
        Stability:
            experimental
        """
        serverSideEncryptionConfiguration: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.ServerSideEncryptionRuleProperty"]]]
        """``CfnBucket.BucketEncryptionProperty.ServerSideEncryptionConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-bucketencryption.html#cfn-s3-bucket-bucketencryption-serversideencryptionconfiguration
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.CorsConfigurationProperty", jsii_struct_bases=[])
    class CorsConfigurationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-cors.html
        Stability:
            experimental
        """
        corsRules: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.CorsRuleProperty"]]]
        """``CfnBucket.CorsConfigurationProperty.CorsRules``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-cors.html#cfn-s3-bucket-cors-corsrule
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _CorsRuleProperty(jsii.compat.TypedDict, total=False):
        allowedHeaders: typing.List[str]
        """``CfnBucket.CorsRuleProperty.AllowedHeaders``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-cors-corsrule.html#cfn-s3-bucket-cors-corsrule-allowedheaders
        Stability:
            experimental
        """
        exposedHeaders: typing.List[str]
        """``CfnBucket.CorsRuleProperty.ExposedHeaders``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-cors-corsrule.html#cfn-s3-bucket-cors-corsrule-exposedheaders
        Stability:
            experimental
        """
        id: str
        """``CfnBucket.CorsRuleProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-cors-corsrule.html#cfn-s3-bucket-cors-corsrule-id
        Stability:
            experimental
        """
        maxAge: jsii.Number
        """``CfnBucket.CorsRuleProperty.MaxAge``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-cors-corsrule.html#cfn-s3-bucket-cors-corsrule-maxage
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.CorsRuleProperty", jsii_struct_bases=[_CorsRuleProperty])
    class CorsRuleProperty(_CorsRuleProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-cors-corsrule.html
        Stability:
            experimental
        """
        allowedMethods: typing.List[str]
        """``CfnBucket.CorsRuleProperty.AllowedMethods``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-cors-corsrule.html#cfn-s3-bucket-cors-corsrule-allowedmethods
        Stability:
            experimental
        """

        allowedOrigins: typing.List[str]
        """``CfnBucket.CorsRuleProperty.AllowedOrigins``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-cors-corsrule.html#cfn-s3-bucket-cors-corsrule-allowedorigins
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.DataExportProperty", jsii_struct_bases=[])
    class DataExportProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-dataexport.html
        Stability:
            experimental
        """
        destination: typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.DestinationProperty"]
        """``CfnBucket.DataExportProperty.Destination``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-dataexport.html#cfn-s3-bucket-dataexport-destination
        Stability:
            experimental
        """

        outputSchemaVersion: str
        """``CfnBucket.DataExportProperty.OutputSchemaVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-dataexport.html#cfn-s3-bucket-dataexport-outputschemaversion
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.DefaultRetentionProperty", jsii_struct_bases=[])
    class DefaultRetentionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-defaultretention.html
        Stability:
            experimental
        """
        days: jsii.Number
        """``CfnBucket.DefaultRetentionProperty.Days``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-defaultretention.html#cfn-s3-bucket-defaultretention-days
        Stability:
            experimental
        """

        mode: str
        """``CfnBucket.DefaultRetentionProperty.Mode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-defaultretention.html#cfn-s3-bucket-defaultretention-mode
        Stability:
            experimental
        """

        years: jsii.Number
        """``CfnBucket.DefaultRetentionProperty.Years``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-defaultretention.html#cfn-s3-bucket-defaultretention-years
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _DestinationProperty(jsii.compat.TypedDict, total=False):
        bucketAccountId: str
        """``CfnBucket.DestinationProperty.BucketAccountId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-destination.html#cfn-s3-bucket-destination-bucketaccountid
        Stability:
            experimental
        """
        prefix: str
        """``CfnBucket.DestinationProperty.Prefix``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-destination.html#cfn-s3-bucket-destination-prefix
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.DestinationProperty", jsii_struct_bases=[_DestinationProperty])
    class DestinationProperty(_DestinationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-destination.html
        Stability:
            experimental
        """
        bucketArn: str
        """``CfnBucket.DestinationProperty.BucketArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-destination.html#cfn-s3-bucket-destination-bucketarn
        Stability:
            experimental
        """

        format: str
        """``CfnBucket.DestinationProperty.Format``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-destination.html#cfn-s3-bucket-destination-format
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.EncryptionConfigurationProperty", jsii_struct_bases=[])
    class EncryptionConfigurationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-encryptionconfiguration.html
        Stability:
            experimental
        """
        replicaKmsKeyId: str
        """``CfnBucket.EncryptionConfigurationProperty.ReplicaKmsKeyID``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-encryptionconfiguration.html#cfn-s3-bucket-encryptionconfiguration-replicakmskeyid
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.FilterRuleProperty", jsii_struct_bases=[])
    class FilterRuleProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-notificationconfiguration-config-filter-s3key-rules.html
        Stability:
            experimental
        """
        name: str
        """``CfnBucket.FilterRuleProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-notificationconfiguration-config-filter-s3key-rules.html#cfn-s3-bucket-notificationconfiguraiton-config-filter-s3key-rules-name
        Stability:
            experimental
        """

        value: str
        """``CfnBucket.FilterRuleProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-notificationconfiguration-config-filter-s3key-rules.html#cfn-s3-bucket-notificationconfiguraiton-config-filter-s3key-rules-value
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _InventoryConfigurationProperty(jsii.compat.TypedDict, total=False):
        optionalFields: typing.List[str]
        """``CfnBucket.InventoryConfigurationProperty.OptionalFields``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-inventoryconfiguration.html#cfn-s3-bucket-inventoryconfiguration-optionalfields
        Stability:
            experimental
        """
        prefix: str
        """``CfnBucket.InventoryConfigurationProperty.Prefix``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-inventoryconfiguration.html#cfn-s3-bucket-inventoryconfiguration-prefix
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.InventoryConfigurationProperty", jsii_struct_bases=[_InventoryConfigurationProperty])
    class InventoryConfigurationProperty(_InventoryConfigurationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-inventoryconfiguration.html
        Stability:
            experimental
        """
        destination: typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.DestinationProperty"]
        """``CfnBucket.InventoryConfigurationProperty.Destination``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-inventoryconfiguration.html#cfn-s3-bucket-inventoryconfiguration-destination
        Stability:
            experimental
        """

        enabled: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnBucket.InventoryConfigurationProperty.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-inventoryconfiguration.html#cfn-s3-bucket-inventoryconfiguration-enabled
        Stability:
            experimental
        """

        id: str
        """``CfnBucket.InventoryConfigurationProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-inventoryconfiguration.html#cfn-s3-bucket-inventoryconfiguration-id
        Stability:
            experimental
        """

        includedObjectVersions: str
        """``CfnBucket.InventoryConfigurationProperty.IncludedObjectVersions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-inventoryconfiguration.html#cfn-s3-bucket-inventoryconfiguration-includedobjectversions
        Stability:
            experimental
        """

        scheduleFrequency: str
        """``CfnBucket.InventoryConfigurationProperty.ScheduleFrequency``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-inventoryconfiguration.html#cfn-s3-bucket-inventoryconfiguration-schedulefrequency
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _LambdaConfigurationProperty(jsii.compat.TypedDict, total=False):
        filter: typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.NotificationFilterProperty"]
        """``CfnBucket.LambdaConfigurationProperty.Filter``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-notificationconfig-lambdaconfig.html#cfn-s3-bucket-notificationconfig-lambdaconfig-filter
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.LambdaConfigurationProperty", jsii_struct_bases=[_LambdaConfigurationProperty])
    class LambdaConfigurationProperty(_LambdaConfigurationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-notificationconfig-lambdaconfig.html
        Stability:
            experimental
        """
        event: str
        """``CfnBucket.LambdaConfigurationProperty.Event``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-notificationconfig-lambdaconfig.html#cfn-s3-bucket-notificationconfig-lambdaconfig-event
        Stability:
            experimental
        """

        function: str
        """``CfnBucket.LambdaConfigurationProperty.Function``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-notificationconfig-lambdaconfig.html#cfn-s3-bucket-notificationconfig-lambdaconfig-function
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.LifecycleConfigurationProperty", jsii_struct_bases=[])
    class LifecycleConfigurationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-lifecycleconfig.html
        Stability:
            experimental
        """
        rules: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.RuleProperty"]]]
        """``CfnBucket.LifecycleConfigurationProperty.Rules``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-lifecycleconfig.html#cfn-s3-bucket-lifecycleconfig-rules
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.LoggingConfigurationProperty", jsii_struct_bases=[])
    class LoggingConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-loggingconfig.html
        Stability:
            experimental
        """
        destinationBucketName: str
        """``CfnBucket.LoggingConfigurationProperty.DestinationBucketName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-loggingconfig.html#cfn-s3-bucket-loggingconfig-destinationbucketname
        Stability:
            experimental
        """

        logFilePrefix: str
        """``CfnBucket.LoggingConfigurationProperty.LogFilePrefix``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-loggingconfig.html#cfn-s3-bucket-loggingconfig-logfileprefix
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _MetricsConfigurationProperty(jsii.compat.TypedDict, total=False):
        prefix: str
        """``CfnBucket.MetricsConfigurationProperty.Prefix``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-metricsconfiguration.html#cfn-s3-bucket-metricsconfiguration-prefix
        Stability:
            experimental
        """
        tagFilters: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.TagFilterProperty"]]]
        """``CfnBucket.MetricsConfigurationProperty.TagFilters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-metricsconfiguration.html#cfn-s3-bucket-metricsconfiguration-tagfilters
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.MetricsConfigurationProperty", jsii_struct_bases=[_MetricsConfigurationProperty])
    class MetricsConfigurationProperty(_MetricsConfigurationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-metricsconfiguration.html
        Stability:
            experimental
        """
        id: str
        """``CfnBucket.MetricsConfigurationProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-metricsconfiguration.html#cfn-s3-bucket-metricsconfiguration-id
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.NoncurrentVersionTransitionProperty", jsii_struct_bases=[])
    class NoncurrentVersionTransitionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-lifecycleconfig-rule-noncurrentversiontransition.html
        Stability:
            experimental
        """
        storageClass: str
        """``CfnBucket.NoncurrentVersionTransitionProperty.StorageClass``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-lifecycleconfig-rule-noncurrentversiontransition.html#cfn-s3-bucket-lifecycleconfig-rule-noncurrentversiontransition-storageclass
        Stability:
            experimental
        """

        transitionInDays: jsii.Number
        """``CfnBucket.NoncurrentVersionTransitionProperty.TransitionInDays``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-lifecycleconfig-rule-noncurrentversiontransition.html#cfn-s3-bucket-lifecycleconfig-rule-noncurrentversiontransition-transitionindays
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.NotificationConfigurationProperty", jsii_struct_bases=[])
    class NotificationConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-notificationconfig.html
        Stability:
            experimental
        """
        lambdaConfigurations: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.LambdaConfigurationProperty"]]]
        """``CfnBucket.NotificationConfigurationProperty.LambdaConfigurations``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-notificationconfig.html#cfn-s3-bucket-notificationconfig-lambdaconfig
        Stability:
            experimental
        """

        queueConfigurations: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.QueueConfigurationProperty"]]]
        """``CfnBucket.NotificationConfigurationProperty.QueueConfigurations``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-notificationconfig.html#cfn-s3-bucket-notificationconfig-queueconfig
        Stability:
            experimental
        """

        topicConfigurations: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.TopicConfigurationProperty"]]]
        """``CfnBucket.NotificationConfigurationProperty.TopicConfigurations``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-notificationconfig.html#cfn-s3-bucket-notificationconfig-topicconfig
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.NotificationFilterProperty", jsii_struct_bases=[])
    class NotificationFilterProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-notificationconfiguration-config-filter.html
        Stability:
            experimental
        """
        s3Key: typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.S3KeyFilterProperty"]
        """``CfnBucket.NotificationFilterProperty.S3Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-notificationconfiguration-config-filter.html#cfn-s3-bucket-notificationconfiguraiton-config-filter-s3key
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.ObjectLockConfigurationProperty", jsii_struct_bases=[])
    class ObjectLockConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-objectlockconfiguration.html
        Stability:
            experimental
        """
        objectLockEnabled: str
        """``CfnBucket.ObjectLockConfigurationProperty.ObjectLockEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-objectlockconfiguration.html#cfn-s3-bucket-objectlockconfiguration-objectlockenabled
        Stability:
            experimental
        """

        rule: typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.ObjectLockRuleProperty"]
        """``CfnBucket.ObjectLockConfigurationProperty.Rule``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-objectlockconfiguration.html#cfn-s3-bucket-objectlockconfiguration-rule
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.ObjectLockRuleProperty", jsii_struct_bases=[])
    class ObjectLockRuleProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-objectlockrule.html
        Stability:
            experimental
        """
        defaultRetention: typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.DefaultRetentionProperty"]
        """``CfnBucket.ObjectLockRuleProperty.DefaultRetention``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-objectlockrule.html#cfn-s3-bucket-objectlockrule-defaultretention
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.PublicAccessBlockConfigurationProperty", jsii_struct_bases=[])
    class PublicAccessBlockConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-publicaccessblockconfiguration.html
        Stability:
            experimental
        """
        blockPublicAcls: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnBucket.PublicAccessBlockConfigurationProperty.BlockPublicAcls``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-publicaccessblockconfiguration.html#cfn-s3-bucket-publicaccessblockconfiguration-blockpublicacls
        Stability:
            experimental
        """

        blockPublicPolicy: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnBucket.PublicAccessBlockConfigurationProperty.BlockPublicPolicy``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-publicaccessblockconfiguration.html#cfn-s3-bucket-publicaccessblockconfiguration-blockpublicpolicy
        Stability:
            experimental
        """

        ignorePublicAcls: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnBucket.PublicAccessBlockConfigurationProperty.IgnorePublicAcls``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-publicaccessblockconfiguration.html#cfn-s3-bucket-publicaccessblockconfiguration-ignorepublicacls
        Stability:
            experimental
        """

        restrictPublicBuckets: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnBucket.PublicAccessBlockConfigurationProperty.RestrictPublicBuckets``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-publicaccessblockconfiguration.html#cfn-s3-bucket-publicaccessblockconfiguration-restrictpublicbuckets
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _QueueConfigurationProperty(jsii.compat.TypedDict, total=False):
        filter: typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.NotificationFilterProperty"]
        """``CfnBucket.QueueConfigurationProperty.Filter``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-notificationconfig-queueconfig.html#cfn-s3-bucket-notificationconfig-queueconfig-filter
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.QueueConfigurationProperty", jsii_struct_bases=[_QueueConfigurationProperty])
    class QueueConfigurationProperty(_QueueConfigurationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-notificationconfig-queueconfig.html
        Stability:
            experimental
        """
        event: str
        """``CfnBucket.QueueConfigurationProperty.Event``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-notificationconfig-queueconfig.html#cfn-s3-bucket-notificationconfig-queueconfig-event
        Stability:
            experimental
        """

        queue: str
        """``CfnBucket.QueueConfigurationProperty.Queue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-notificationconfig-queueconfig.html#cfn-s3-bucket-notificationconfig-queueconfig-queue
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _RedirectAllRequestsToProperty(jsii.compat.TypedDict, total=False):
        protocol: str
        """``CfnBucket.RedirectAllRequestsToProperty.Protocol``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-websiteconfiguration-redirectallrequeststo.html#cfn-s3-websiteconfiguration-redirectallrequeststo-protocol
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.RedirectAllRequestsToProperty", jsii_struct_bases=[_RedirectAllRequestsToProperty])
    class RedirectAllRequestsToProperty(_RedirectAllRequestsToProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-websiteconfiguration-redirectallrequeststo.html
        Stability:
            experimental
        """
        hostName: str
        """``CfnBucket.RedirectAllRequestsToProperty.HostName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-websiteconfiguration-redirectallrequeststo.html#cfn-s3-websiteconfiguration-redirectallrequeststo-hostname
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.RedirectRuleProperty", jsii_struct_bases=[])
    class RedirectRuleProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-websiteconfiguration-routingrules-redirectrule.html
        Stability:
            experimental
        """
        hostName: str
        """``CfnBucket.RedirectRuleProperty.HostName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-websiteconfiguration-routingrules-redirectrule.html#cfn-s3-websiteconfiguration-redirectrule-hostname
        Stability:
            experimental
        """

        httpRedirectCode: str
        """``CfnBucket.RedirectRuleProperty.HttpRedirectCode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-websiteconfiguration-routingrules-redirectrule.html#cfn-s3-websiteconfiguration-redirectrule-httpredirectcode
        Stability:
            experimental
        """

        protocol: str
        """``CfnBucket.RedirectRuleProperty.Protocol``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-websiteconfiguration-routingrules-redirectrule.html#cfn-s3-websiteconfiguration-redirectrule-protocol
        Stability:
            experimental
        """

        replaceKeyPrefixWith: str
        """``CfnBucket.RedirectRuleProperty.ReplaceKeyPrefixWith``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-websiteconfiguration-routingrules-redirectrule.html#cfn-s3-websiteconfiguration-redirectrule-replacekeyprefixwith
        Stability:
            experimental
        """

        replaceKeyWith: str
        """``CfnBucket.RedirectRuleProperty.ReplaceKeyWith``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-websiteconfiguration-routingrules-redirectrule.html#cfn-s3-websiteconfiguration-redirectrule-replacekeywith
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.ReplicationConfigurationProperty", jsii_struct_bases=[])
    class ReplicationConfigurationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-replicationconfiguration.html
        Stability:
            experimental
        """
        role: str
        """``CfnBucket.ReplicationConfigurationProperty.Role``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-replicationconfiguration.html#cfn-s3-bucket-replicationconfiguration-role
        Stability:
            experimental
        """

        rules: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.ReplicationRuleProperty"]]]
        """``CfnBucket.ReplicationConfigurationProperty.Rules``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-replicationconfiguration.html#cfn-s3-bucket-replicationconfiguration-rules
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ReplicationDestinationProperty(jsii.compat.TypedDict, total=False):
        accessControlTranslation: typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.AccessControlTranslationProperty"]
        """``CfnBucket.ReplicationDestinationProperty.AccessControlTranslation``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-replicationconfiguration-rules-destination.html#cfn-s3-bucket-replicationdestination-accesscontroltranslation
        Stability:
            experimental
        """
        account: str
        """``CfnBucket.ReplicationDestinationProperty.Account``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-replicationconfiguration-rules-destination.html#cfn-s3-bucket-replicationdestination-account
        Stability:
            experimental
        """
        encryptionConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.EncryptionConfigurationProperty"]
        """``CfnBucket.ReplicationDestinationProperty.EncryptionConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-replicationconfiguration-rules-destination.html#cfn-s3-bucket-replicationdestination-encryptionconfiguration
        Stability:
            experimental
        """
        storageClass: str
        """``CfnBucket.ReplicationDestinationProperty.StorageClass``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-replicationconfiguration-rules-destination.html#cfn-s3-bucket-replicationconfiguration-rules-destination-storageclass
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.ReplicationDestinationProperty", jsii_struct_bases=[_ReplicationDestinationProperty])
    class ReplicationDestinationProperty(_ReplicationDestinationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-replicationconfiguration-rules-destination.html
        Stability:
            experimental
        """
        bucket: str
        """``CfnBucket.ReplicationDestinationProperty.Bucket``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-replicationconfiguration-rules-destination.html#cfn-s3-bucket-replicationconfiguration-rules-destination-bucket
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ReplicationRuleProperty(jsii.compat.TypedDict, total=False):
        id: str
        """``CfnBucket.ReplicationRuleProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-replicationconfiguration-rules.html#cfn-s3-bucket-replicationconfiguration-rules-id
        Stability:
            experimental
        """
        sourceSelectionCriteria: typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.SourceSelectionCriteriaProperty"]
        """``CfnBucket.ReplicationRuleProperty.SourceSelectionCriteria``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-replicationconfiguration-rules.html#cfn-s3-bucket-replicationrule-sourceselectioncriteria
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.ReplicationRuleProperty", jsii_struct_bases=[_ReplicationRuleProperty])
    class ReplicationRuleProperty(_ReplicationRuleProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-replicationconfiguration-rules.html
        Stability:
            experimental
        """
        destination: typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.ReplicationDestinationProperty"]
        """``CfnBucket.ReplicationRuleProperty.Destination``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-replicationconfiguration-rules.html#cfn-s3-bucket-replicationconfiguration-rules-destination
        Stability:
            experimental
        """

        prefix: str
        """``CfnBucket.ReplicationRuleProperty.Prefix``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-replicationconfiguration-rules.html#cfn-s3-bucket-replicationconfiguration-rules-prefix
        Stability:
            experimental
        """

        status: str
        """``CfnBucket.ReplicationRuleProperty.Status``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-replicationconfiguration-rules.html#cfn-s3-bucket-replicationconfiguration-rules-status
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.RoutingRuleConditionProperty", jsii_struct_bases=[])
    class RoutingRuleConditionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-websiteconfiguration-routingrules-routingrulecondition.html
        Stability:
            experimental
        """
        httpErrorCodeReturnedEquals: str
        """``CfnBucket.RoutingRuleConditionProperty.HttpErrorCodeReturnedEquals``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-websiteconfiguration-routingrules-routingrulecondition.html#cfn-s3-websiteconfiguration-routingrules-routingrulecondition-httperrorcodereturnedequals
        Stability:
            experimental
        """

        keyPrefixEquals: str
        """``CfnBucket.RoutingRuleConditionProperty.KeyPrefixEquals``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-websiteconfiguration-routingrules-routingrulecondition.html#cfn-s3-websiteconfiguration-routingrules-routingrulecondition-keyprefixequals
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _RoutingRuleProperty(jsii.compat.TypedDict, total=False):
        routingRuleCondition: typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.RoutingRuleConditionProperty"]
        """``CfnBucket.RoutingRuleProperty.RoutingRuleCondition``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-websiteconfiguration-routingrules.html#cfn-s3-websiteconfiguration-routingrules-routingrulecondition
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.RoutingRuleProperty", jsii_struct_bases=[_RoutingRuleProperty])
    class RoutingRuleProperty(_RoutingRuleProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-websiteconfiguration-routingrules.html
        Stability:
            experimental
        """
        redirectRule: typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.RedirectRuleProperty"]
        """``CfnBucket.RoutingRuleProperty.RedirectRule``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-websiteconfiguration-routingrules.html#cfn-s3-websiteconfiguration-routingrules-redirectrule
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _RuleProperty(jsii.compat.TypedDict, total=False):
        abortIncompleteMultipartUpload: typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.AbortIncompleteMultipartUploadProperty"]
        """``CfnBucket.RuleProperty.AbortIncompleteMultipartUpload``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-lifecycleconfig-rule.html#cfn-s3-bucket-rule-abortincompletemultipartupload
        Stability:
            experimental
        """
        expirationDate: typing.Union[datetime.datetime, aws_cdk.cdk.IResolvable]
        """``CfnBucket.RuleProperty.ExpirationDate``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-lifecycleconfig-rule.html#cfn-s3-bucket-lifecycleconfig-rule-expirationdate
        Stability:
            experimental
        """
        expirationInDays: jsii.Number
        """``CfnBucket.RuleProperty.ExpirationInDays``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-lifecycleconfig-rule.html#cfn-s3-bucket-lifecycleconfig-rule-expirationindays
        Stability:
            experimental
        """
        id: str
        """``CfnBucket.RuleProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-lifecycleconfig-rule.html#cfn-s3-bucket-lifecycleconfig-rule-id
        Stability:
            experimental
        """
        noncurrentVersionExpirationInDays: jsii.Number
        """``CfnBucket.RuleProperty.NoncurrentVersionExpirationInDays``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-lifecycleconfig-rule.html#cfn-s3-bucket-lifecycleconfig-rule-noncurrentversionexpirationindays
        Stability:
            experimental
        """
        noncurrentVersionTransition: typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.NoncurrentVersionTransitionProperty"]
        """``CfnBucket.RuleProperty.NoncurrentVersionTransition``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-lifecycleconfig-rule.html#cfn-s3-bucket-lifecycleconfig-rule-noncurrentversiontransition
        Stability:
            experimental
        """
        noncurrentVersionTransitions: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.NoncurrentVersionTransitionProperty"]]]
        """``CfnBucket.RuleProperty.NoncurrentVersionTransitions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-lifecycleconfig-rule.html#cfn-s3-bucket-lifecycleconfig-rule-noncurrentversiontransitions
        Stability:
            experimental
        """
        prefix: str
        """``CfnBucket.RuleProperty.Prefix``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-lifecycleconfig-rule.html#cfn-s3-bucket-lifecycleconfig-rule-prefix
        Stability:
            experimental
        """
        tagFilters: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.TagFilterProperty"]]]
        """``CfnBucket.RuleProperty.TagFilters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-lifecycleconfig-rule.html#cfn-s3-bucket-rule-tagfilters
        Stability:
            experimental
        """
        transition: typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.TransitionProperty"]
        """``CfnBucket.RuleProperty.Transition``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-lifecycleconfig-rule.html#cfn-s3-bucket-lifecycleconfig-rule-transition
        Stability:
            experimental
        """
        transitions: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.TransitionProperty"]]]
        """``CfnBucket.RuleProperty.Transitions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-lifecycleconfig-rule.html#cfn-s3-bucket-lifecycleconfig-rule-transitions
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.RuleProperty", jsii_struct_bases=[_RuleProperty])
    class RuleProperty(_RuleProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-lifecycleconfig-rule.html
        Stability:
            experimental
        """
        status: str
        """``CfnBucket.RuleProperty.Status``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-lifecycleconfig-rule.html#cfn-s3-bucket-lifecycleconfig-rule-status
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.S3KeyFilterProperty", jsii_struct_bases=[])
    class S3KeyFilterProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-notificationconfiguration-config-filter-s3key.html
        Stability:
            experimental
        """
        rules: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.FilterRuleProperty"]]]
        """``CfnBucket.S3KeyFilterProperty.Rules``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-notificationconfiguration-config-filter-s3key.html#cfn-s3-bucket-notificationconfiguraiton-config-filter-s3key-rules
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ServerSideEncryptionByDefaultProperty(jsii.compat.TypedDict, total=False):
        kmsMasterKeyId: str
        """``CfnBucket.ServerSideEncryptionByDefaultProperty.KMSMasterKeyID``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-serversideencryptionbydefault.html#cfn-s3-bucket-serversideencryptionbydefault-kmsmasterkeyid
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.ServerSideEncryptionByDefaultProperty", jsii_struct_bases=[_ServerSideEncryptionByDefaultProperty])
    class ServerSideEncryptionByDefaultProperty(_ServerSideEncryptionByDefaultProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-serversideencryptionbydefault.html
        Stability:
            experimental
        """
        sseAlgorithm: str
        """``CfnBucket.ServerSideEncryptionByDefaultProperty.SSEAlgorithm``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-serversideencryptionbydefault.html#cfn-s3-bucket-serversideencryptionbydefault-ssealgorithm
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.ServerSideEncryptionRuleProperty", jsii_struct_bases=[])
    class ServerSideEncryptionRuleProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-serversideencryptionrule.html
        Stability:
            experimental
        """
        serverSideEncryptionByDefault: typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.ServerSideEncryptionByDefaultProperty"]
        """``CfnBucket.ServerSideEncryptionRuleProperty.ServerSideEncryptionByDefault``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-serversideencryptionrule.html#cfn-s3-bucket-serversideencryptionrule-serversideencryptionbydefault
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.SourceSelectionCriteriaProperty", jsii_struct_bases=[])
    class SourceSelectionCriteriaProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-sourceselectioncriteria.html
        Stability:
            experimental
        """
        sseKmsEncryptedObjects: typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.SseKmsEncryptedObjectsProperty"]
        """``CfnBucket.SourceSelectionCriteriaProperty.SseKmsEncryptedObjects``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-sourceselectioncriteria.html#cfn-s3-bucket-sourceselectioncriteria-ssekmsencryptedobjects
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.SseKmsEncryptedObjectsProperty", jsii_struct_bases=[])
    class SseKmsEncryptedObjectsProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-ssekmsencryptedobjects.html
        Stability:
            experimental
        """
        status: str
        """``CfnBucket.SseKmsEncryptedObjectsProperty.Status``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-ssekmsencryptedobjects.html#cfn-s3-bucket-ssekmsencryptedobjects-status
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.StorageClassAnalysisProperty", jsii_struct_bases=[])
    class StorageClassAnalysisProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-storageclassanalysis.html
        Stability:
            experimental
        """
        dataExport: typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.DataExportProperty"]
        """``CfnBucket.StorageClassAnalysisProperty.DataExport``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-storageclassanalysis.html#cfn-s3-bucket-storageclassanalysis-dataexport
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.TagFilterProperty", jsii_struct_bases=[])
    class TagFilterProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-tagfilter.html
        Stability:
            experimental
        """
        key: str
        """``CfnBucket.TagFilterProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-tagfilter.html#cfn-s3-bucket-tagfilter-key
        Stability:
            experimental
        """

        value: str
        """``CfnBucket.TagFilterProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-tagfilter.html#cfn-s3-bucket-tagfilter-value
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _TopicConfigurationProperty(jsii.compat.TypedDict, total=False):
        filter: typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.NotificationFilterProperty"]
        """``CfnBucket.TopicConfigurationProperty.Filter``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-notificationconfig-topicconfig.html#cfn-s3-bucket-notificationconfig-topicconfig-filter
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.TopicConfigurationProperty", jsii_struct_bases=[_TopicConfigurationProperty])
    class TopicConfigurationProperty(_TopicConfigurationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-notificationconfig-topicconfig.html
        Stability:
            experimental
        """
        event: str
        """``CfnBucket.TopicConfigurationProperty.Event``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-notificationconfig-topicconfig.html#cfn-s3-bucket-notificationconfig-topicconfig-event
        Stability:
            experimental
        """

        topic: str
        """``CfnBucket.TopicConfigurationProperty.Topic``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-notificationconfig-topicconfig.html#cfn-s3-bucket-notificationconfig-topicconfig-topic
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _TransitionProperty(jsii.compat.TypedDict, total=False):
        transitionDate: typing.Union[datetime.datetime, aws_cdk.cdk.IResolvable]
        """``CfnBucket.TransitionProperty.TransitionDate``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-lifecycleconfig-rule-transition.html#cfn-s3-bucket-lifecycleconfig-rule-transition-transitiondate
        Stability:
            experimental
        """
        transitionInDays: jsii.Number
        """``CfnBucket.TransitionProperty.TransitionInDays``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-lifecycleconfig-rule-transition.html#cfn-s3-bucket-lifecycleconfig-rule-transition-transitionindays
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.TransitionProperty", jsii_struct_bases=[_TransitionProperty])
    class TransitionProperty(_TransitionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-lifecycleconfig-rule-transition.html
        Stability:
            experimental
        """
        storageClass: str
        """``CfnBucket.TransitionProperty.StorageClass``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-lifecycleconfig-rule-transition.html#cfn-s3-bucket-lifecycleconfig-rule-transition-storageclass
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.VersioningConfigurationProperty", jsii_struct_bases=[])
    class VersioningConfigurationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-versioningconfig.html
        Stability:
            experimental
        """
        status: str
        """``CfnBucket.VersioningConfigurationProperty.Status``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-versioningconfig.html#cfn-s3-bucket-versioningconfig-status
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucket.WebsiteConfigurationProperty", jsii_struct_bases=[])
    class WebsiteConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-websiteconfiguration.html
        Stability:
            experimental
        """
        errorDocument: str
        """``CfnBucket.WebsiteConfigurationProperty.ErrorDocument``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-websiteconfiguration.html#cfn-s3-websiteconfiguration-errordocument
        Stability:
            experimental
        """

        indexDocument: str
        """``CfnBucket.WebsiteConfigurationProperty.IndexDocument``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-websiteconfiguration.html#cfn-s3-websiteconfiguration-indexdocument
        Stability:
            experimental
        """

        redirectAllRequestsTo: typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.RedirectAllRequestsToProperty"]
        """``CfnBucket.WebsiteConfigurationProperty.RedirectAllRequestsTo``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-websiteconfiguration.html#cfn-s3-websiteconfiguration-redirectallrequeststo
        Stability:
            experimental
        """

        routingRules: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.RoutingRuleProperty"]]]
        """``CfnBucket.WebsiteConfigurationProperty.RoutingRules``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-websiteconfiguration.html#cfn-s3-websiteconfiguration-routingrules
        Stability:
            experimental
        """


class CfnBucketPolicy(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-s3.CfnBucketPolicy"):
    """A CloudFormation ``AWS::S3::BucketPolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-policy.html
    Stability:
        experimental
    cloudformationResource:
        AWS::S3::BucketPolicy
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, bucket: str, policy_document: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.IResolvable]) -> None:
        """Create a new ``AWS::S3::BucketPolicy``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            bucket: ``AWS::S3::BucketPolicy.Bucket``.
            policyDocument: ``AWS::S3::BucketPolicy.PolicyDocument``.

        Stability:
            experimental
        """
        props: CfnBucketPolicyProps = {"bucket": bucket, "policyDocument": policy_document}

        jsii.create(CfnBucketPolicy, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="cfnResourceTypeName")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            experimental
        """
        return jsii.sget(cls, "cfnResourceTypeName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> str:
        """``AWS::S3::BucketPolicy.Bucket``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-policy.html#aws-properties-s3-policy-bucket
        Stability:
            experimental
        """
        return jsii.get(self, "bucket")

    @bucket.setter
    def bucket(self, value: str):
        return jsii.set(self, "bucket", value)

    @property
    @jsii.member(jsii_name="policyDocument")
    def policy_document(self) -> typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.IResolvable]:
        """``AWS::S3::BucketPolicy.PolicyDocument``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-policy.html#aws-properties-s3-policy-policydocument
        Stability:
            experimental
        """
        return jsii.get(self, "policyDocument")

    @policy_document.setter
    def policy_document(self, value: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.IResolvable]):
        return jsii.set(self, "policyDocument", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucketPolicyProps", jsii_struct_bases=[])
class CfnBucketPolicyProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::S3::BucketPolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-policy.html
    Stability:
        experimental
    """
    bucket: str
    """``AWS::S3::BucketPolicy.Bucket``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-policy.html#aws-properties-s3-policy-bucket
    Stability:
        experimental
    """

    policyDocument: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.IResolvable]
    """``AWS::S3::BucketPolicy.PolicyDocument``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-policy.html#aws-properties-s3-policy-policydocument
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-s3.CfnBucketProps", jsii_struct_bases=[])
class CfnBucketProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::S3::Bucket``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html
    Stability:
        experimental
    """
    accelerateConfiguration: typing.Union["CfnBucket.AccelerateConfigurationProperty", aws_cdk.cdk.IResolvable]
    """``AWS::S3::Bucket.AccelerateConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-accelerateconfiguration
    Stability:
        experimental
    """

    accessControl: str
    """``AWS::S3::Bucket.AccessControl``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-accesscontrol
    Stability:
        experimental
    """

    analyticsConfigurations: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.AnalyticsConfigurationProperty"]]]
    """``AWS::S3::Bucket.AnalyticsConfigurations``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-analyticsconfigurations
    Stability:
        experimental
    """

    bucketEncryption: typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.BucketEncryptionProperty"]
    """``AWS::S3::Bucket.BucketEncryption``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-bucketencryption
    Stability:
        experimental
    """

    bucketName: str
    """``AWS::S3::Bucket.BucketName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-name
    Stability:
        experimental
    """

    corsConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.CorsConfigurationProperty"]
    """``AWS::S3::Bucket.CorsConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-crossoriginconfig
    Stability:
        experimental
    """

    inventoryConfigurations: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.InventoryConfigurationProperty"]]]
    """``AWS::S3::Bucket.InventoryConfigurations``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-inventoryconfigurations
    Stability:
        experimental
    """

    lifecycleConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.LifecycleConfigurationProperty"]
    """``AWS::S3::Bucket.LifecycleConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-lifecycleconfig
    Stability:
        experimental
    """

    loggingConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.LoggingConfigurationProperty"]
    """``AWS::S3::Bucket.LoggingConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-loggingconfig
    Stability:
        experimental
    """

    metricsConfigurations: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.MetricsConfigurationProperty"]]]
    """``AWS::S3::Bucket.MetricsConfigurations``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-metricsconfigurations
    Stability:
        experimental
    """

    notificationConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.NotificationConfigurationProperty"]
    """``AWS::S3::Bucket.NotificationConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-notification
    Stability:
        experimental
    """

    objectLockConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.ObjectLockConfigurationProperty"]
    """``AWS::S3::Bucket.ObjectLockConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-objectlockconfiguration
    Stability:
        experimental
    """

    objectLockEnabled: typing.Union[bool, aws_cdk.cdk.IResolvable]
    """``AWS::S3::Bucket.ObjectLockEnabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-objectlockenabled
    Stability:
        experimental
    """

    publicAccessBlockConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.PublicAccessBlockConfigurationProperty"]
    """``AWS::S3::Bucket.PublicAccessBlockConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-publicaccessblockconfiguration
    Stability:
        experimental
    """

    replicationConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.ReplicationConfigurationProperty"]
    """``AWS::S3::Bucket.ReplicationConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-replicationconfiguration
    Stability:
        experimental
    """

    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::S3::Bucket.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-tags
    Stability:
        experimental
    """

    versioningConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.VersioningConfigurationProperty"]
    """``AWS::S3::Bucket.VersioningConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-versioning
    Stability:
        experimental
    """

    websiteConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnBucket.WebsiteConfigurationProperty"]
    """``AWS::S3::Bucket.WebsiteConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-websiteconfiguration
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CorsRule(jsii.compat.TypedDict, total=False):
    allowedHeaders: typing.List[str]
    """Headers that are specified in the Access-Control-Request-Headers header.

    Default:
        - No headers allowed.

    Stability:
        experimental
    """
    exposedHeaders: typing.List[str]
    """One or more headers in the response that you want customers to be able to access from their applications.

    Default:
        - No headers exposed.

    Stability:
        experimental
    """
    id: str
    """A unique identifier for this rule.

    Default:
        - No id specified.

    Stability:
        experimental
    """
    maxAge: jsii.Number
    """The time in seconds that your browser is to cache the preflight response for the specified resource.

    Default:
        - No caching.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-s3.CorsRule", jsii_struct_bases=[_CorsRule])
class CorsRule(_CorsRule):
    """Specifies a cross-origin access rule for an Amazon S3 bucket.

    Stability:
        experimental
    """
    allowedMethods: typing.List["HttpMethods"]
    """An HTTP method that you allow the origin to execute.

    Stability:
        experimental
    """

    allowedOrigins: typing.List[str]
    """One or more origins you want customers to be able to access the bucket from.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-s3.EventType")
class EventType(enum.Enum):
    """Notification event types.

    Stability:
        experimental
    """
    ObjectCreated = "ObjectCreated"
    """Amazon S3 APIs such as PUT, POST, and COPY can create an object.

    Using
    these event types, you can enable notification when an object is created
    using a specific API, or you can use the s3:ObjectCreated:* event type to
    request notification regardless of the API that was used to create an
    object.

    Stability:
        experimental
    """
    ObjectCreatedPut = "ObjectCreatedPut"
    """Amazon S3 APIs such as PUT, POST, and COPY can create an object.

    Using
    these event types, you can enable notification when an object is created
    using a specific API, or you can use the s3:ObjectCreated:* event type to
    request notification regardless of the API that was used to create an
    object.

    Stability:
        experimental
    """
    ObjectCreatedPost = "ObjectCreatedPost"
    """Amazon S3 APIs such as PUT, POST, and COPY can create an object.

    Using
    these event types, you can enable notification when an object is created
    using a specific API, or you can use the s3:ObjectCreated:* event type to
    request notification regardless of the API that was used to create an
    object.

    Stability:
        experimental
    """
    ObjectCreatedCopy = "ObjectCreatedCopy"
    """Amazon S3 APIs such as PUT, POST, and COPY can create an object.

    Using
    these event types, you can enable notification when an object is created
    using a specific API, or you can use the s3:ObjectCreated:* event type to
    request notification regardless of the API that was used to create an
    object.

    Stability:
        experimental
    """
    ObjectCreatedCompleteMultipartUpload = "ObjectCreatedCompleteMultipartUpload"
    """Amazon S3 APIs such as PUT, POST, and COPY can create an object.

    Using
    these event types, you can enable notification when an object is created
    using a specific API, or you can use the s3:ObjectCreated:* event type to
    request notification regardless of the API that was used to create an
    object.

    Stability:
        experimental
    """
    ObjectRemoved = "ObjectRemoved"
    """By using the ObjectRemoved event types, you can enable notification when an object or a batch of objects is removed from a bucket.

    You can request notification when an object is deleted or a versioned
    object is permanently deleted by using the s3:ObjectRemoved:Delete event
    type. Or you can request notification when a delete marker is created for
    a versioned object by using s3:ObjectRemoved:DeleteMarkerCreated. For
    information about deleting versioned objects, see Deleting Object
    Versions. You can also use a wildcard s3:ObjectRemoved:* to request
    notification anytime an object is deleted.

    You will not receive event notifications from automatic deletes from
    lifecycle policies or from failed operations.

    Stability:
        experimental
    """
    ObjectRemovedDelete = "ObjectRemovedDelete"
    """By using the ObjectRemoved event types, you can enable notification when an object or a batch of objects is removed from a bucket.

    You can request notification when an object is deleted or a versioned
    object is permanently deleted by using the s3:ObjectRemoved:Delete event
    type. Or you can request notification when a delete marker is created for
    a versioned object by using s3:ObjectRemoved:DeleteMarkerCreated. For
    information about deleting versioned objects, see Deleting Object
    Versions. You can also use a wildcard s3:ObjectRemoved:* to request
    notification anytime an object is deleted.

    You will not receive event notifications from automatic deletes from
    lifecycle policies or from failed operations.

    Stability:
        experimental
    """
    ObjectRemovedDeleteMarkerCreated = "ObjectRemovedDeleteMarkerCreated"
    """By using the ObjectRemoved event types, you can enable notification when an object or a batch of objects is removed from a bucket.

    You can request notification when an object is deleted or a versioned
    object is permanently deleted by using the s3:ObjectRemoved:Delete event
    type. Or you can request notification when a delete marker is created for
    a versioned object by using s3:ObjectRemoved:DeleteMarkerCreated. For
    information about deleting versioned objects, see Deleting Object
    Versions. You can also use a wildcard s3:ObjectRemoved:* to request
    notification anytime an object is deleted.

    You will not receive event notifications from automatic deletes from
    lifecycle policies or from failed operations.

    Stability:
        experimental
    """
    ReducedRedundancyLostObject = "ReducedRedundancyLostObject"
    """You can use this event type to request Amazon S3 to send a notification message when Amazon S3 detects that an object of the RRS storage class is lost.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-s3.HttpMethods")
class HttpMethods(enum.Enum):
    """All http request methods.

    Stability:
        experimental
    """
    GET = "GET"
    """The GET method requests a representation of the specified resource.

    Stability:
        experimental
    """
    PUT = "PUT"
    """The PUT method replaces all current representations of the target resource with the request payload.

    Stability:
        experimental
    """
    HEAD = "HEAD"
    """The HEAD method asks for a response identical to that of a GET request, but without the response body.

    Stability:
        experimental
    """
    POST = "POST"
    """The POST method is used to submit an entity to the specified resource, often causing a change in state or side effects on the server.

    Stability:
        experimental
    """
    DELETE = "DELETE"
    """The DELETE method deletes the specified resource.

    Stability:
        experimental
    """

@jsii.interface(jsii_type="@aws-cdk/aws-s3.IBucket")
class IBucket(aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IBucketProxy

    @property
    @jsii.member(jsii_name="bucketArn")
    def bucket_arn(self) -> str:
        """The ARN of the bucket.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="bucketDomainName")
    def bucket_domain_name(self) -> str:
        """The IPv4 DNS name of the specified bucket.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="bucketDualStackDomainName")
    def bucket_dual_stack_domain_name(self) -> str:
        """The IPv6 DNS name of the specified bucket.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="bucketName")
    def bucket_name(self) -> str:
        """The name of the bucket.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="bucketRegionalDomainName")
    def bucket_regional_domain_name(self) -> str:
        """The regional domain name of the specified bucket.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="bucketWebsiteUrl")
    def bucket_website_url(self) -> str:
        """The URL of the static website.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="encryptionKey")
    def encryption_key(self) -> typing.Optional[aws_cdk.aws_kms.IKey]:
        """Optional KMS encryption key associated with this bucket.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="policy")
    def policy(self) -> typing.Optional["BucketPolicy"]:
        """The resource policy assoicated with this bucket.

        If ``autoCreatePolicy`` is true, a ``BucketPolicy`` will be created upon the
        first call to addToResourcePolicy(s).

        Stability:
            experimental
        """
        ...

    @policy.setter
    def policy(self, value: typing.Optional["BucketPolicy"]):
        ...

    @jsii.member(jsii_name="addToResourcePolicy")
    def add_to_resource_policy(self, permission: aws_cdk.aws_iam.PolicyStatement) -> None:
        """Adds a statement to the resource policy for a principal (i.e. account/role/service) to perform actions on this bucket and/or it's contents. Use ``bucketArn`` and ``arnForObjects(keys)`` to obtain ARNs for this bucket or objects.

        Arguments:
            permission: -

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="arnForObjects")
    def arn_for_objects(self, key_pattern: str) -> str:
        """Returns an ARN that represents all objects within the bucket that match the key pattern specified.

        To represent all keys, specify ``"*"``.

        Arguments:
            keyPattern: -

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="grantDelete")
    def grant_delete(self, identity: aws_cdk.aws_iam.IGrantable, objects_key_pattern: typing.Any=None) -> aws_cdk.aws_iam.Grant:
        """Grants s3:DeleteObject* permission to an IAM pricipal for objects in this bucket.

        Arguments:
            identity: The principal.
            objectsKeyPattern: Restrict the permission to a certain key pattern (default '*').

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="grantPublicAccess")
    def grant_public_access(self, key_prefix: typing.Optional[str]=None, *allowed_actions: str) -> aws_cdk.aws_iam.Grant:
        """Allows unrestricted access to objects from this bucket.

        IMPORTANT: This permission allows anyone to perform actions on S3 objects
        in this bucket, which is useful for when you configure your bucket as a
        website and want everyone to be able to read objects in the bucket without
        needing to authenticate.

        Without arguments, this method will grant read ("s3:GetObject") access to
        all objects ("*") in the bucket.

        The method returns the ``iam.Grant`` object, which can then be modified
        as needed. For example, you can add a condition that will restrict access only
        to an IPv4 range like this::

            const grant = bucket.grantPublicAccess();
            grant.resourceStatement!.addCondition(‘IpAddress’, { “aws:SourceIp”: “54.240.143.0/24” });

        Arguments:
            keyPrefix: the prefix of S3 object keys (e.g. ``home/*``). Default is "*".
            allowedActions: the set of S3 actions to allow. Default is "s3:GetObject".

        Returns:
            The ``iam.PolicyStatement`` object, which can be used to apply e.g. conditions.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="grantPut")
    def grant_put(self, identity: aws_cdk.aws_iam.IGrantable, objects_key_pattern: typing.Any=None) -> aws_cdk.aws_iam.Grant:
        """Grants s3:PutObject* and s3:Abort* permissions for this bucket to an IAM principal.

        If encryption is used, permission to use the key to encrypt the contents
        of written files will also be granted to the same principal.

        Arguments:
            identity: The principal.
            objectsKeyPattern: Restrict the permission to a certain key pattern (default '*').

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="grantRead")
    def grant_read(self, identity: aws_cdk.aws_iam.IGrantable, objects_key_pattern: typing.Any=None) -> aws_cdk.aws_iam.Grant:
        """Grant read permissions for this bucket and it's contents to an IAM principal (Role/Group/User).

        If encryption is used, permission to use the key to decrypt the contents
        of the bucket will also be granted to the same principal.

        Arguments:
            identity: The principal.
            objectsKeyPattern: Restrict the permission to a certain key pattern (default '*').

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="grantReadWrite")
    def grant_read_write(self, identity: aws_cdk.aws_iam.IGrantable, objects_key_pattern: typing.Any=None) -> aws_cdk.aws_iam.Grant:
        """Grants read/write permissions for this bucket and it's contents to an IAM principal (Role/Group/User).

        If an encryption key is used, permission to use the key for
        encrypt/decrypt will also be granted.

        Arguments:
            identity: The principal.
            objectsKeyPattern: Restrict the permission to a certain key pattern (default '*').

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="grantWrite")
    def grant_write(self, identity: aws_cdk.aws_iam.IGrantable, objects_key_pattern: typing.Any=None) -> aws_cdk.aws_iam.Grant:
        """Grant write permissions to this bucket to an IAM principal.

        If encryption is used, permission to use the key to encrypt the contents
        of written files will also be granted to the same principal.

        Arguments:
            identity: The principal.
            objectsKeyPattern: Restrict the permission to a certain key pattern (default '*').

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="onCloudTrailEvent")
    def on_cloud_trail_event(self, id: str, *, paths: typing.Optional[typing.List[str]]=None, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Define a CloudWatch event that triggers when something happens to this repository.

        Requires that there exists at least one CloudTrail Trail in your account
        that captures the event. This method will not create the Trail.

        Arguments:
            id: The id of the rule.
            options: Options for adding the rule.
            paths: Only watch changes to these object paths. Default: - Watch changes to all objects
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="onCloudTrailPutObject")
    def on_cloud_trail_put_object(self, id: str, *, paths: typing.Optional[typing.List[str]]=None, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines an AWS CloudWatch event rule that can trigger a target when an image is pushed to this repository.

        Requires that there exists at least one CloudTrail Trail in your account
        that captures the event. This method will not create the Trail.

        Arguments:
            id: The id of the rule.
            options: Options for adding the rule.
            paths: Only watch changes to these object paths. Default: - Watch changes to all objects
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="urlForObject")
    def url_for_object(self, key: typing.Optional[str]=None) -> str:
        """The https URL of an S3 object.

        For example:

        Arguments:
            key: The S3 key of the object. If not specified, the URL of the bucket is returned.

        Returns:
            an ObjectS3Url token

        Stability:
            experimental

        Example::
            https://s3.cn-north-1.amazonaws.com.cn/china-bucket/mykey
        """
        ...


class _IBucketProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-s3.IBucket"
    @property
    @jsii.member(jsii_name="bucketArn")
    def bucket_arn(self) -> str:
        """The ARN of the bucket.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "bucketArn")

    @property
    @jsii.member(jsii_name="bucketDomainName")
    def bucket_domain_name(self) -> str:
        """The IPv4 DNS name of the specified bucket.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "bucketDomainName")

    @property
    @jsii.member(jsii_name="bucketDualStackDomainName")
    def bucket_dual_stack_domain_name(self) -> str:
        """The IPv6 DNS name of the specified bucket.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "bucketDualStackDomainName")

    @property
    @jsii.member(jsii_name="bucketName")
    def bucket_name(self) -> str:
        """The name of the bucket.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "bucketName")

    @property
    @jsii.member(jsii_name="bucketRegionalDomainName")
    def bucket_regional_domain_name(self) -> str:
        """The regional domain name of the specified bucket.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "bucketRegionalDomainName")

    @property
    @jsii.member(jsii_name="bucketWebsiteUrl")
    def bucket_website_url(self) -> str:
        """The URL of the static website.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "bucketWebsiteUrl")

    @property
    @jsii.member(jsii_name="encryptionKey")
    def encryption_key(self) -> typing.Optional[aws_cdk.aws_kms.IKey]:
        """Optional KMS encryption key associated with this bucket.

        Stability:
            experimental
        """
        return jsii.get(self, "encryptionKey")

    @property
    @jsii.member(jsii_name="policy")
    def policy(self) -> typing.Optional["BucketPolicy"]:
        """The resource policy assoicated with this bucket.

        If ``autoCreatePolicy`` is true, a ``BucketPolicy`` will be created upon the
        first call to addToResourcePolicy(s).

        Stability:
            experimental
        """
        return jsii.get(self, "policy")

    @policy.setter
    def policy(self, value: typing.Optional["BucketPolicy"]):
        return jsii.set(self, "policy", value)

    @jsii.member(jsii_name="addToResourcePolicy")
    def add_to_resource_policy(self, permission: aws_cdk.aws_iam.PolicyStatement) -> None:
        """Adds a statement to the resource policy for a principal (i.e. account/role/service) to perform actions on this bucket and/or it's contents. Use ``bucketArn`` and ``arnForObjects(keys)`` to obtain ARNs for this bucket or objects.

        Arguments:
            permission: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addToResourcePolicy", [permission])

    @jsii.member(jsii_name="arnForObjects")
    def arn_for_objects(self, key_pattern: str) -> str:
        """Returns an ARN that represents all objects within the bucket that match the key pattern specified.

        To represent all keys, specify ``"*"``.

        Arguments:
            keyPattern: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "arnForObjects", [key_pattern])

    @jsii.member(jsii_name="grantDelete")
    def grant_delete(self, identity: aws_cdk.aws_iam.IGrantable, objects_key_pattern: typing.Any=None) -> aws_cdk.aws_iam.Grant:
        """Grants s3:DeleteObject* permission to an IAM pricipal for objects in this bucket.

        Arguments:
            identity: The principal.
            objectsKeyPattern: Restrict the permission to a certain key pattern (default '*').

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantDelete", [identity, objects_key_pattern])

    @jsii.member(jsii_name="grantPublicAccess")
    def grant_public_access(self, key_prefix: typing.Optional[str]=None, *allowed_actions: str) -> aws_cdk.aws_iam.Grant:
        """Allows unrestricted access to objects from this bucket.

        IMPORTANT: This permission allows anyone to perform actions on S3 objects
        in this bucket, which is useful for when you configure your bucket as a
        website and want everyone to be able to read objects in the bucket without
        needing to authenticate.

        Without arguments, this method will grant read ("s3:GetObject") access to
        all objects ("*") in the bucket.

        The method returns the ``iam.Grant`` object, which can then be modified
        as needed. For example, you can add a condition that will restrict access only
        to an IPv4 range like this::

            const grant = bucket.grantPublicAccess();
            grant.resourceStatement!.addCondition(‘IpAddress’, { “aws:SourceIp”: “54.240.143.0/24” });

        Arguments:
            keyPrefix: the prefix of S3 object keys (e.g. ``home/*``). Default is "*".
            allowedActions: the set of S3 actions to allow. Default is "s3:GetObject".

        Returns:
            The ``iam.PolicyStatement`` object, which can be used to apply e.g. conditions.

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantPublicAccess", [key_prefix, *allowed_actions])

    @jsii.member(jsii_name="grantPut")
    def grant_put(self, identity: aws_cdk.aws_iam.IGrantable, objects_key_pattern: typing.Any=None) -> aws_cdk.aws_iam.Grant:
        """Grants s3:PutObject* and s3:Abort* permissions for this bucket to an IAM principal.

        If encryption is used, permission to use the key to encrypt the contents
        of written files will also be granted to the same principal.

        Arguments:
            identity: The principal.
            objectsKeyPattern: Restrict the permission to a certain key pattern (default '*').

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantPut", [identity, objects_key_pattern])

    @jsii.member(jsii_name="grantRead")
    def grant_read(self, identity: aws_cdk.aws_iam.IGrantable, objects_key_pattern: typing.Any=None) -> aws_cdk.aws_iam.Grant:
        """Grant read permissions for this bucket and it's contents to an IAM principal (Role/Group/User).

        If encryption is used, permission to use the key to decrypt the contents
        of the bucket will also be granted to the same principal.

        Arguments:
            identity: The principal.
            objectsKeyPattern: Restrict the permission to a certain key pattern (default '*').

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantRead", [identity, objects_key_pattern])

    @jsii.member(jsii_name="grantReadWrite")
    def grant_read_write(self, identity: aws_cdk.aws_iam.IGrantable, objects_key_pattern: typing.Any=None) -> aws_cdk.aws_iam.Grant:
        """Grants read/write permissions for this bucket and it's contents to an IAM principal (Role/Group/User).

        If an encryption key is used, permission to use the key for
        encrypt/decrypt will also be granted.

        Arguments:
            identity: The principal.
            objectsKeyPattern: Restrict the permission to a certain key pattern (default '*').

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantReadWrite", [identity, objects_key_pattern])

    @jsii.member(jsii_name="grantWrite")
    def grant_write(self, identity: aws_cdk.aws_iam.IGrantable, objects_key_pattern: typing.Any=None) -> aws_cdk.aws_iam.Grant:
        """Grant write permissions to this bucket to an IAM principal.

        If encryption is used, permission to use the key to encrypt the contents
        of written files will also be granted to the same principal.

        Arguments:
            identity: The principal.
            objectsKeyPattern: Restrict the permission to a certain key pattern (default '*').

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantWrite", [identity, objects_key_pattern])

    @jsii.member(jsii_name="onCloudTrailEvent")
    def on_cloud_trail_event(self, id: str, *, paths: typing.Optional[typing.List[str]]=None, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Define a CloudWatch event that triggers when something happens to this repository.

        Requires that there exists at least one CloudTrail Trail in your account
        that captures the event. This method will not create the Trail.

        Arguments:
            id: The id of the rule.
            options: Options for adding the rule.
            paths: Only watch changes to these object paths. Default: - Watch changes to all objects
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        options: OnCloudTrailBucketEventOptions = {"target": target}

        if paths is not None:
            options["paths"] = paths

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        return jsii.invoke(self, "onCloudTrailEvent", [id, options])

    @jsii.member(jsii_name="onCloudTrailPutObject")
    def on_cloud_trail_put_object(self, id: str, *, paths: typing.Optional[typing.List[str]]=None, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines an AWS CloudWatch event rule that can trigger a target when an image is pushed to this repository.

        Requires that there exists at least one CloudTrail Trail in your account
        that captures the event. This method will not create the Trail.

        Arguments:
            id: The id of the rule.
            options: Options for adding the rule.
            paths: Only watch changes to these object paths. Default: - Watch changes to all objects
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        options: OnCloudTrailBucketEventOptions = {"target": target}

        if paths is not None:
            options["paths"] = paths

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        return jsii.invoke(self, "onCloudTrailPutObject", [id, options])

    @jsii.member(jsii_name="urlForObject")
    def url_for_object(self, key: typing.Optional[str]=None) -> str:
        """The https URL of an S3 object.

        For example:

        Arguments:
            key: The S3 key of the object. If not specified, the URL of the bucket is returned.

        Returns:
            an ObjectS3Url token

        Stability:
            experimental

        Example::
            https://s3.cn-north-1.amazonaws.com.cn/china-bucket/mykey
        """
        return jsii.invoke(self, "urlForObject", [key])


@jsii.implements(IBucket)
class Bucket(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-s3.Bucket"):
    """An S3 bucket with associated policy objects.

    This bucket does not yet have all features that exposed by the underlying
    BucketResource.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, block_public_access: typing.Optional["BlockPublicAccess"]=None, bucket_name: typing.Optional[aws_cdk.cdk.PhysicalName]=None, cors: typing.Optional[typing.List["CorsRule"]]=None, encryption: typing.Optional["BucketEncryption"]=None, encryption_key: typing.Optional[aws_cdk.aws_kms.IKey]=None, lifecycle_rules: typing.Optional[typing.List["LifecycleRule"]]=None, metrics: typing.Optional[typing.List["BucketMetrics"]]=None, public_read_access: typing.Optional[bool]=None, removal_policy: typing.Optional[aws_cdk.cdk.RemovalPolicy]=None, versioned: typing.Optional[bool]=None, website_error_document: typing.Optional[str]=None, website_index_document: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            blockPublicAccess: The block public access configuration of this bucket. Default: false New buckets and objects don't allow public access, but users can modify bucket policies or object permissions to allow public access.
            bucketName: Physical name of this bucket. Default: - Assigned by CloudFormation (recommended).
            cors: The CORS configuration of this bucket. Default: - No CORS configuration.
            encryption: The kind of server-side encryption to apply to this bucket. If you choose KMS, you can specify a KMS key via ``encryptionKey``. If encryption key is not specified, a key will automatically be created. Default: - ``Kms`` if ``encryptionKey`` is specified, or ``Unencrypted`` otherwise.
            encryptionKey: External KMS key to use for bucket encryption. The 'encryption' property must be either not specified or set to "Kms". An error will be emitted if encryption is set to "Unencrypted" or "Managed". Default: - If encryption is set to "Kms" and this property is undefined, a new KMS key will be created and associated with this bucket.
            lifecycleRules: Rules that define how Amazon S3 manages objects during their lifetime. Default: - No lifecycle rules.
            metrics: The metrics configuration of this bucket. Default: - No metrics configuration.
            publicReadAccess: Grants public read access to all objects in the bucket. Similar to calling ``bucket.grantPublicAccess()``. Default: false
            removalPolicy: Policy to apply when the bucket is removed from this stack. Default: - The bucket will be orphaned.
            versioned: Whether this bucket should have versioning turned on or not. Default: false
            websiteErrorDocument: The name of the error document (e.g. "404.html") for the website. ``websiteIndexDocument`` must also be set if this is set. Default: - No error document.
            websiteIndexDocument: The name of the index document (e.g. "index.html") for the website. Enables static website hosting for this bucket. Default: - No index document.

        Stability:
            experimental
        """
        props: BucketProps = {}

        if block_public_access is not None:
            props["blockPublicAccess"] = block_public_access

        if bucket_name is not None:
            props["bucketName"] = bucket_name

        if cors is not None:
            props["cors"] = cors

        if encryption is not None:
            props["encryption"] = encryption

        if encryption_key is not None:
            props["encryptionKey"] = encryption_key

        if lifecycle_rules is not None:
            props["lifecycleRules"] = lifecycle_rules

        if metrics is not None:
            props["metrics"] = metrics

        if public_read_access is not None:
            props["publicReadAccess"] = public_read_access

        if removal_policy is not None:
            props["removalPolicy"] = removal_policy

        if versioned is not None:
            props["versioned"] = versioned

        if website_error_document is not None:
            props["websiteErrorDocument"] = website_error_document

        if website_index_document is not None:
            props["websiteIndexDocument"] = website_index_document

        jsii.create(Bucket, self, [scope, id, props])

    @jsii.member(jsii_name="fromBucketArn")
    @classmethod
    def from_bucket_arn(cls, scope: aws_cdk.cdk.Construct, id: str, bucket_arn: str) -> "IBucket":
        """
        Arguments:
            scope: -
            id: -
            bucketArn: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromBucketArn", [scope, id, bucket_arn])

    @jsii.member(jsii_name="fromBucketAttributes")
    @classmethod
    def from_bucket_attributes(cls, scope: aws_cdk.cdk.Construct, id: str, *, bucket_arn: typing.Optional[str]=None, bucket_domain_name: typing.Optional[str]=None, bucket_dual_stack_domain_name: typing.Optional[str]=None, bucket_name: typing.Optional[str]=None, bucket_regional_domain_name: typing.Optional[str]=None, bucket_website_new_url_format: typing.Optional[bool]=None, bucket_website_url: typing.Optional[str]=None) -> "IBucket":
        """Creates a Bucket construct that represents an external bucket.

        Arguments:
            scope: The parent creating construct (usually ``this``).
            id: The construct's name.
            attrs: A ``BucketAttributes`` object. Can be obtained from a call to ``bucket.export()`` or manually created.
            bucketArn: The ARN of the bucket. At least one of bucketArn or bucketName must be defined in order to initialize a bucket ref.
            bucketDomainName: The domain name of the bucket. Default: Inferred from bucket name
            bucketDualStackDomainName: The IPv6 DNS name of the specified bucket.
            bucketName: The name of the bucket. If the underlying value of ARN is a string, the name will be parsed from the ARN. Otherwise, the name is optional, but some features that require the bucket name such as auto-creating a bucket policy, won't work.
            bucketRegionalDomainName: The regional domain name of the specified bucket.
            bucketWebsiteNewUrlFormat: The format of the website URL of the bucket. This should be true for regions launched since 2014. Default: false
            bucketWebsiteUrl: The website URL of the bucket (if static web hosting is enabled). Default: Inferred from bucket name

        Stability:
            experimental
        """
        attrs: BucketAttributes = {}

        if bucket_arn is not None:
            attrs["bucketArn"] = bucket_arn

        if bucket_domain_name is not None:
            attrs["bucketDomainName"] = bucket_domain_name

        if bucket_dual_stack_domain_name is not None:
            attrs["bucketDualStackDomainName"] = bucket_dual_stack_domain_name

        if bucket_name is not None:
            attrs["bucketName"] = bucket_name

        if bucket_regional_domain_name is not None:
            attrs["bucketRegionalDomainName"] = bucket_regional_domain_name

        if bucket_website_new_url_format is not None:
            attrs["bucketWebsiteNewUrlFormat"] = bucket_website_new_url_format

        if bucket_website_url is not None:
            attrs["bucketWebsiteUrl"] = bucket_website_url

        return jsii.sinvoke(cls, "fromBucketAttributes", [scope, id, attrs])

    @jsii.member(jsii_name="fromBucketName")
    @classmethod
    def from_bucket_name(cls, scope: aws_cdk.cdk.Construct, id: str, bucket_name: str) -> "IBucket":
        """
        Arguments:
            scope: -
            id: -
            bucketName: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromBucketName", [scope, id, bucket_name])

    @jsii.member(jsii_name="addCorsRule")
    def add_cors_rule(self, *, allowed_methods: typing.List["HttpMethods"], allowed_origins: typing.List[str], allowed_headers: typing.Optional[typing.List[str]]=None, exposed_headers: typing.Optional[typing.List[str]]=None, id: typing.Optional[str]=None, max_age: typing.Optional[jsii.Number]=None) -> None:
        """Adds a cross-origin access configuration for objects in an Amazon S3 bucket.

        Arguments:
            rule: The CORS configuration rule to add.
            allowedMethods: An HTTP method that you allow the origin to execute.
            allowedOrigins: One or more origins you want customers to be able to access the bucket from.
            allowedHeaders: Headers that are specified in the Access-Control-Request-Headers header. Default: - No headers allowed.
            exposedHeaders: One or more headers in the response that you want customers to be able to access from their applications. Default: - No headers exposed.
            id: A unique identifier for this rule. Default: - No id specified.
            maxAge: The time in seconds that your browser is to cache the preflight response for the specified resource. Default: - No caching.

        Stability:
            experimental
        """
        rule: CorsRule = {"allowedMethods": allowed_methods, "allowedOrigins": allowed_origins}

        if allowed_headers is not None:
            rule["allowedHeaders"] = allowed_headers

        if exposed_headers is not None:
            rule["exposedHeaders"] = exposed_headers

        if id is not None:
            rule["id"] = id

        if max_age is not None:
            rule["maxAge"] = max_age

        return jsii.invoke(self, "addCorsRule", [rule])

    @jsii.member(jsii_name="addEventNotification")
    def add_event_notification(self, event: "EventType", dest: "IBucketNotificationDestination", *, prefix: typing.Optional[str]=None, suffix: typing.Optional[str]=None) -> None:
        """Adds a bucket notification event destination.

        Arguments:
            event: The event to trigger the notification.
            dest: The notification destination (Lambda, SNS Topic or SQS Queue).
            filters: S3 object key filter rules to determine which objects trigger this event. Each filter must include a ``prefix`` and/or ``suffix`` that will be matched against the s3 object key. Refer to the S3 Developer Guide for details about allowed filter rules.
            prefix: S3 keys must have the specified prefix.
            suffix: S3 keys must have the specified suffix.

        See:
            https://docs.aws.amazon.com/AmazonS3/latest/dev/NotificationHowTo.html
        Stability:
            experimental

        Example::
               bucket.addEventNotification(EventType.OnObjectCreated, myLambda, 'home/myusername/*')
        """
        filters: NotificationKeyFilter = {}

        if prefix is not None:
            filters["prefix"] = prefix

        if suffix is not None:
            filters["suffix"] = suffix

        return jsii.invoke(self, "addEventNotification", [event, dest, *filters])

    @jsii.member(jsii_name="addLifecycleRule")
    def add_lifecycle_rule(self, *, abort_incomplete_multipart_upload_after_days: typing.Optional[jsii.Number]=None, enabled: typing.Optional[bool]=None, expiration_date: typing.Optional[datetime.datetime]=None, expiration_in_days: typing.Optional[jsii.Number]=None, id: typing.Optional[str]=None, noncurrent_version_expiration_in_days: typing.Optional[jsii.Number]=None, noncurrent_version_transitions: typing.Optional[typing.List["NoncurrentVersionTransition"]]=None, prefix: typing.Optional[str]=None, tag_filters: typing.Optional[typing.Mapping[str,typing.Any]]=None, transitions: typing.Optional[typing.List["Transition"]]=None) -> None:
        """Add a lifecycle rule to the bucket.

        Arguments:
            rule: The rule to add.
            abortIncompleteMultipartUploadAfterDays: Specifies a lifecycle rule that aborts incomplete multipart uploads to an Amazon S3 bucket. The AbortIncompleteMultipartUpload property type creates a lifecycle rule that aborts incomplete multipart uploads to an Amazon S3 bucket. When Amazon S3 aborts a multipart upload, it deletes all parts associated with the multipart upload. Default: Incomplete uploads are never aborted
            enabled: Whether this rule is enabled. Default: true
            expirationDate: Indicates when objects are deleted from Amazon S3 and Amazon Glacier. The date value must be in ISO 8601 format. The time is always midnight UTC. If you specify an expiration and transition time, you must use the same time unit for both properties (either in days or by date). The expiration time must also be later than the transition time. Default: No expiration date
            expirationInDays: Indicates the number of days after creation when objects are deleted from Amazon S3 and Amazon Glacier. If you specify an expiration and transition time, you must use the same time unit for both properties (either in days or by date). The expiration time must also be later than the transition time. Default: No expiration timeout
            id: A unique identifier for this rule. The value cannot be more than 255 characters.
            noncurrentVersionExpirationInDays: Time between when a new version of the object is uploaded to the bucket and when old versions of the object expire. For buckets with versioning enabled (or suspended), specifies the time, in days, between when a new version of the object is uploaded to the bucket and when old versions of the object expire. When object versions expire, Amazon S3 permanently deletes them. If you specify a transition and expiration time, the expiration time must be later than the transition time. Default: No noncurrent version expiration
            noncurrentVersionTransitions: One or more transition rules that specify when non-current objects transition to a specified storage class. Only for for buckets with versioning enabled (or suspended). If you specify a transition and expiration time, the expiration time must be later than the transition time.
            prefix: Object key prefix that identifies one or more objects to which this rule applies. Default: Rule applies to all objects
            tagFilters: The TagFilter property type specifies tags to use to identify a subset of objects for an Amazon S3 bucket. Default: Rule applies to all objects
            transitions: One or more transition rules that specify when an object transitions to a specified storage class. If you specify an expiration and transition time, you must use the same time unit for both properties (either in days or by date). The expiration time must also be later than the transition time. Default: No transition rules

        Stability:
            experimental
        """
        rule: LifecycleRule = {}

        if abort_incomplete_multipart_upload_after_days is not None:
            rule["abortIncompleteMultipartUploadAfterDays"] = abort_incomplete_multipart_upload_after_days

        if enabled is not None:
            rule["enabled"] = enabled

        if expiration_date is not None:
            rule["expirationDate"] = expiration_date

        if expiration_in_days is not None:
            rule["expirationInDays"] = expiration_in_days

        if id is not None:
            rule["id"] = id

        if noncurrent_version_expiration_in_days is not None:
            rule["noncurrentVersionExpirationInDays"] = noncurrent_version_expiration_in_days

        if noncurrent_version_transitions is not None:
            rule["noncurrentVersionTransitions"] = noncurrent_version_transitions

        if prefix is not None:
            rule["prefix"] = prefix

        if tag_filters is not None:
            rule["tagFilters"] = tag_filters

        if transitions is not None:
            rule["transitions"] = transitions

        return jsii.invoke(self, "addLifecycleRule", [rule])

    @jsii.member(jsii_name="addMetric")
    def add_metric(self, *, id: str, prefix: typing.Optional[str]=None, tag_filters: typing.Optional[typing.Mapping[str,typing.Any]]=None) -> None:
        """Adds a metrics configuration for the CloudWatch request metrics from the bucket.

        Arguments:
            metric: The metric configuration to add.
            id: The ID used to identify the metrics configuration.
            prefix: The prefix that an object must have to be included in the metrics results.
            tagFilters: Specifies a list of tag filters to use as a metrics configuration filter. The metrics configuration includes only objects that meet the filter's criteria.

        Stability:
            experimental
        """
        metric: BucketMetrics = {"id": id}

        if prefix is not None:
            metric["prefix"] = prefix

        if tag_filters is not None:
            metric["tagFilters"] = tag_filters

        return jsii.invoke(self, "addMetric", [metric])

    @jsii.member(jsii_name="addObjectCreatedNotification")
    def add_object_created_notification(self, dest: "IBucketNotificationDestination", *, prefix: typing.Optional[str]=None, suffix: typing.Optional[str]=None) -> None:
        """Subscribes a destination to receive notificatins when an object is created in the bucket.

        This is identical to calling
        ``onEvent(EventType.ObjectCreated)``.

        Arguments:
            dest: The notification destination (see onEvent).
            filters: Filters (see onEvent).
            prefix: S3 keys must have the specified prefix.
            suffix: S3 keys must have the specified suffix.

        Stability:
            experimental
        """
        filters: NotificationKeyFilter = {}

        if prefix is not None:
            filters["prefix"] = prefix

        if suffix is not None:
            filters["suffix"] = suffix

        return jsii.invoke(self, "addObjectCreatedNotification", [dest, *filters])

    @jsii.member(jsii_name="addObjectRemovedNotification")
    def add_object_removed_notification(self, dest: "IBucketNotificationDestination", *, prefix: typing.Optional[str]=None, suffix: typing.Optional[str]=None) -> None:
        """Subscribes a destination to receive notificatins when an object is removed from the bucket.

        This is identical to calling
        ``onEvent(EventType.ObjectRemoved)``.

        Arguments:
            dest: The notification destination (see onEvent).
            filters: Filters (see onEvent).
            prefix: S3 keys must have the specified prefix.
            suffix: S3 keys must have the specified suffix.

        Stability:
            experimental
        """
        filters: NotificationKeyFilter = {}

        if prefix is not None:
            filters["prefix"] = prefix

        if suffix is not None:
            filters["suffix"] = suffix

        return jsii.invoke(self, "addObjectRemovedNotification", [dest, *filters])

    @jsii.member(jsii_name="addToResourcePolicy")
    def add_to_resource_policy(self, permission: aws_cdk.aws_iam.PolicyStatement) -> None:
        """Adds a statement to the resource policy for a principal (i.e. account/role/service) to perform actions on this bucket and/or it's contents. Use ``bucketArn`` and ``arnForObjects(keys)`` to obtain ARNs for this bucket or objects.

        Arguments:
            permission: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addToResourcePolicy", [permission])

    @jsii.member(jsii_name="arnForObjects")
    def arn_for_objects(self, key_pattern: str) -> str:
        """Returns an ARN that represents all objects within the bucket that match the key pattern specified.

        To represent all keys, specify ``"*"``.

        If you specify multiple components for keyPattern, they will be concatenated::

        arnForObjects('home/', team, '/', user, '/*')

        Arguments:
            keyPattern: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "arnForObjects", [key_pattern])

    @jsii.member(jsii_name="grantDelete")
    def grant_delete(self, identity: aws_cdk.aws_iam.IGrantable, objects_key_pattern: typing.Any=None) -> aws_cdk.aws_iam.Grant:
        """Grants s3:DeleteObject* permission to an IAM pricipal for objects in this bucket.

        Arguments:
            identity: The principal.
            objectsKeyPattern: Restrict the permission to a certain key pattern (default '*').

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantDelete", [identity, objects_key_pattern])

    @jsii.member(jsii_name="grantPublicAccess")
    def grant_public_access(self, key_prefix: typing.Optional[str]=None, *allowed_actions: str) -> aws_cdk.aws_iam.Grant:
        """Allows unrestricted access to objects from this bucket.

        IMPORTANT: This permission allows anyone to perform actions on S3 objects
        in this bucket, which is useful for when you configure your bucket as a
        website and want everyone to be able to read objects in the bucket without
        needing to authenticate.

        Without arguments, this method will grant read ("s3:GetObject") access to
        all objects ("*") in the bucket.

        The method returns the ``iam.Grant`` object, which can then be modified
        as needed. For example, you can add a condition that will restrict access only
        to an IPv4 range like this::

            const grant = bucket.grantPublicAccess();
            grant.resourceStatement!.addCondition(‘IpAddress’, { “aws:SourceIp”: “54.240.143.0/24” });

        Arguments:
            keyPrefix: the prefix of S3 object keys (e.g. ``home/*``). Default is "*".
            allowedActions: the set of S3 actions to allow. Default is "s3:GetObject".

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantPublicAccess", [key_prefix, *allowed_actions])

    @jsii.member(jsii_name="grantPut")
    def grant_put(self, identity: aws_cdk.aws_iam.IGrantable, objects_key_pattern: typing.Any=None) -> aws_cdk.aws_iam.Grant:
        """Grants s3:PutObject* and s3:Abort* permissions for this bucket to an IAM principal.

        If encryption is used, permission to use the key to encrypt the contents
        of written files will also be granted to the same principal.

        Arguments:
            identity: The principal.
            objectsKeyPattern: Restrict the permission to a certain key pattern (default '*').

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantPut", [identity, objects_key_pattern])

    @jsii.member(jsii_name="grantRead")
    def grant_read(self, identity: aws_cdk.aws_iam.IGrantable, objects_key_pattern: typing.Any=None) -> aws_cdk.aws_iam.Grant:
        """Grant read permissions for this bucket and it's contents to an IAM principal (Role/Group/User).

        If encryption is used, permission to use the key to decrypt the contents
        of the bucket will also be granted to the same principal.

        Arguments:
            identity: The principal.
            objectsKeyPattern: Restrict the permission to a certain key pattern (default '*').

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantRead", [identity, objects_key_pattern])

    @jsii.member(jsii_name="grantReadWrite")
    def grant_read_write(self, identity: aws_cdk.aws_iam.IGrantable, objects_key_pattern: typing.Any=None) -> aws_cdk.aws_iam.Grant:
        """Grants read/write permissions for this bucket and it's contents to an IAM principal (Role/Group/User).

        If an encryption key is used, permission to use the key for
        encrypt/decrypt will also be granted.

        Arguments:
            identity: The principal.
            objectsKeyPattern: Restrict the permission to a certain key pattern (default '*').

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantReadWrite", [identity, objects_key_pattern])

    @jsii.member(jsii_name="grantWrite")
    def grant_write(self, identity: aws_cdk.aws_iam.IGrantable, objects_key_pattern: typing.Any=None) -> aws_cdk.aws_iam.Grant:
        """Grant write permissions to this bucket to an IAM principal.

        If encryption is used, permission to use the key to encrypt the contents
        of written files will also be granted to the same principal.

        Arguments:
            identity: The principal.
            objectsKeyPattern: Restrict the permission to a certain key pattern (default '*').

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantWrite", [identity, objects_key_pattern])

    @jsii.member(jsii_name="onCloudTrailEvent")
    def on_cloud_trail_event(self, id: str, *, paths: typing.Optional[typing.List[str]]=None, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Define a CloudWatch event that triggers when something happens to this repository.

        Requires that there exists at least one CloudTrail Trail in your account
        that captures the event. This method will not create the Trail.

        Arguments:
            id: The id of the rule.
            options: Options for adding the rule.
            paths: Only watch changes to these object paths. Default: - Watch changes to all objects
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        options: OnCloudTrailBucketEventOptions = {"target": target}

        if paths is not None:
            options["paths"] = paths

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        return jsii.invoke(self, "onCloudTrailEvent", [id, options])

    @jsii.member(jsii_name="onCloudTrailPutObject")
    def on_cloud_trail_put_object(self, id: str, *, paths: typing.Optional[typing.List[str]]=None, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines an AWS CloudWatch event rule that can trigger a target when an image is pushed to this repository.

        Requires that there exists at least one CloudTrail Trail in your account
        that captures the event. This method will not create the Trail.

        Arguments:
            id: The id of the rule.
            options: Options for adding the rule.
            paths: Only watch changes to these object paths. Default: - Watch changes to all objects
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        options: OnCloudTrailBucketEventOptions = {"target": target}

        if paths is not None:
            options["paths"] = paths

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        return jsii.invoke(self, "onCloudTrailPutObject", [id, options])

    @jsii.member(jsii_name="urlForObject")
    def url_for_object(self, key: typing.Optional[str]=None) -> str:
        """The https URL of an S3 object.

        For example:

        Arguments:
            key: The S3 key of the object. If not specified, the URL of the bucket is returned.

        Returns:
            an ObjectS3Url token

        Stability:
            experimental

        Example::
            https://s3.cn-north-1.amazonaws.com.cn/china-bucket/mykey
        """
        return jsii.invoke(self, "urlForObject", [key])

    @property
    @jsii.member(jsii_name="bucketArn")
    def bucket_arn(self) -> str:
        """The ARN of the bucket.

        Stability:
            experimental
        """
        return jsii.get(self, "bucketArn")

    @property
    @jsii.member(jsii_name="bucketDomainName")
    def bucket_domain_name(self) -> str:
        """The IPv4 DNS name of the specified bucket.

        Stability:
            experimental
        """
        return jsii.get(self, "bucketDomainName")

    @property
    @jsii.member(jsii_name="bucketDualStackDomainName")
    def bucket_dual_stack_domain_name(self) -> str:
        """The IPv6 DNS name of the specified bucket.

        Stability:
            experimental
        """
        return jsii.get(self, "bucketDualStackDomainName")

    @property
    @jsii.member(jsii_name="bucketName")
    def bucket_name(self) -> str:
        """The name of the bucket.

        Stability:
            experimental
        """
        return jsii.get(self, "bucketName")

    @property
    @jsii.member(jsii_name="bucketRegionalDomainName")
    def bucket_regional_domain_name(self) -> str:
        """The regional domain name of the specified bucket.

        Stability:
            experimental
        """
        return jsii.get(self, "bucketRegionalDomainName")

    @property
    @jsii.member(jsii_name="bucketWebsiteUrl")
    def bucket_website_url(self) -> str:
        """The URL of the static website.

        Stability:
            experimental
        """
        return jsii.get(self, "bucketWebsiteUrl")

    @property
    @jsii.member(jsii_name="encryptionKey")
    def encryption_key(self) -> typing.Optional[aws_cdk.aws_kms.IKey]:
        """Optional KMS encryption key associated with this bucket.

        Stability:
            experimental
        """
        return jsii.get(self, "encryptionKey")

    @property
    @jsii.member(jsii_name="autoCreatePolicy")
    def _auto_create_policy(self) -> bool:
        """Indicates if a bucket resource policy should automatically created upon the first call to ``addToResourcePolicy``.

        Stability:
            experimental
        """
        return jsii.get(self, "autoCreatePolicy")

    @_auto_create_policy.setter
    def _auto_create_policy(self, value: bool):
        return jsii.set(self, "autoCreatePolicy", value)

    @property
    @jsii.member(jsii_name="disallowPublicAccess")
    def _disallow_public_access(self) -> typing.Optional[bool]:
        """Whether to disallow public access.

        Stability:
            experimental
        """
        return jsii.get(self, "disallowPublicAccess")

    @_disallow_public_access.setter
    def _disallow_public_access(self, value: typing.Optional[bool]):
        return jsii.set(self, "disallowPublicAccess", value)

    @property
    @jsii.member(jsii_name="policy")
    def policy(self) -> typing.Optional["BucketPolicy"]:
        """The resource policy assoicated with this bucket.

        If ``autoCreatePolicy`` is true, a ``BucketPolicy`` will be created upon the
        first call to addToResourcePolicy(s).

        Stability:
            experimental
        """
        return jsii.get(self, "policy")

    @policy.setter
    def policy(self, value: typing.Optional["BucketPolicy"]):
        return jsii.set(self, "policy", value)


@jsii.interface(jsii_type="@aws-cdk/aws-s3.IBucketNotificationDestination")
class IBucketNotificationDestination(jsii.compat.Protocol):
    """Implemented by constructs that can be used as bucket notification destinations.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IBucketNotificationDestinationProxy

    @jsii.member(jsii_name="bind")
    def bind(self, scope: aws_cdk.cdk.Construct, bucket: "IBucket") -> "BucketNotificationDestinationConfig":
        """Registers this resource to receive notifications for the specified bucket.

        This method will only be called once for each destination/bucket
        pair and the result will be cached, so there is no need to implement
        idempotency in each destination.

        Arguments:
            scope: -
            bucket: The bucket object to bind to.

        Stability:
            experimental
        """
        ...


class _IBucketNotificationDestinationProxy():
    """Implemented by constructs that can be used as bucket notification destinations.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-s3.IBucketNotificationDestination"
    @jsii.member(jsii_name="bind")
    def bind(self, scope: aws_cdk.cdk.Construct, bucket: "IBucket") -> "BucketNotificationDestinationConfig":
        """Registers this resource to receive notifications for the specified bucket.

        This method will only be called once for each destination/bucket
        pair and the result will be cached, so there is no need to implement
        idempotency in each destination.

        Arguments:
            scope: -
            bucket: The bucket object to bind to.

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [scope, bucket])


@jsii.data_type(jsii_type="@aws-cdk/aws-s3.LifecycleRule", jsii_struct_bases=[])
class LifecycleRule(jsii.compat.TypedDict, total=False):
    """Declaration of a Life cycle rule.

    Stability:
        experimental
    """
    abortIncompleteMultipartUploadAfterDays: jsii.Number
    """Specifies a lifecycle rule that aborts incomplete multipart uploads to an Amazon S3 bucket.

    The AbortIncompleteMultipartUpload property type creates a lifecycle
    rule that aborts incomplete multipart uploads to an Amazon S3 bucket.
    When Amazon S3 aborts a multipart upload, it deletes all parts
    associated with the multipart upload.

    Default:
        Incomplete uploads are never aborted

    Stability:
        experimental
    """

    enabled: bool
    """Whether this rule is enabled.

    Default:
        true

    Stability:
        experimental
    """

    expirationDate: datetime.datetime
    """Indicates when objects are deleted from Amazon S3 and Amazon Glacier.

    The date value must be in ISO 8601 format. The time is always midnight UTC.

    If you specify an expiration and transition time, you must use the same
    time unit for both properties (either in days or by date). The
    expiration time must also be later than the transition time.

    Default:
        No expiration date

    Stability:
        experimental
    """

    expirationInDays: jsii.Number
    """Indicates the number of days after creation when objects are deleted from Amazon S3 and Amazon Glacier.

    If you specify an expiration and transition time, you must use the same
    time unit for both properties (either in days or by date). The
    expiration time must also be later than the transition time.

    Default:
        No expiration timeout

    Stability:
        experimental
    """

    id: str
    """A unique identifier for this rule.

    The value cannot be more than 255 characters.

    Stability:
        experimental
    """

    noncurrentVersionExpirationInDays: jsii.Number
    """Time between when a new version of the object is uploaded to the bucket and when old versions of the object expire.

    For buckets with versioning enabled (or suspended), specifies the time,
    in days, between when a new version of the object is uploaded to the
    bucket and when old versions of the object expire. When object versions
    expire, Amazon S3 permanently deletes them. If you specify a transition
    and expiration time, the expiration time must be later than the
    transition time.

    Default:
        No noncurrent version expiration

    Stability:
        experimental
    """

    noncurrentVersionTransitions: typing.List["NoncurrentVersionTransition"]
    """One or more transition rules that specify when non-current objects transition to a specified storage class.

    Only for for buckets with versioning enabled (or suspended).

    If you specify a transition and expiration time, the expiration time
    must be later than the transition time.

    Stability:
        experimental
    """

    prefix: str
    """Object key prefix that identifies one or more objects to which this rule applies.

    Default:
        Rule applies to all objects

    Stability:
        experimental
    """

    tagFilters: typing.Mapping[str,typing.Any]
    """The TagFilter property type specifies tags to use to identify a subset of objects for an Amazon S3 bucket.

    Default:
        Rule applies to all objects

    Stability:
        experimental
    """

    transitions: typing.List["Transition"]
    """One or more transition rules that specify when an object transitions to a specified storage class.

    If you specify an expiration and transition time, you must use the same
    time unit for both properties (either in days or by date). The
    expiration time must also be later than the transition time.

    Default:
        No transition rules

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-s3.Location", jsii_struct_bases=[])
class Location(jsii.compat.TypedDict):
    """An interface that represents the location of a specific object in an S3 Bucket.

    Stability:
        experimental
    """
    bucketName: str
    """The name of the S3 Bucket the object is in.

    Stability:
        experimental
    """

    objectKey: str
    """The path inside the Bucket where the object is located at.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-s3.NoncurrentVersionTransition", jsii_struct_bases=[])
class NoncurrentVersionTransition(jsii.compat.TypedDict):
    """Describes when noncurrent versions transition to a specified storage class.

    Stability:
        experimental
    """
    storageClass: "StorageClass"
    """The storage class to which you want the object to transition.

    Stability:
        experimental
    """

    transitionInDays: jsii.Number
    """Indicates the number of days after creation when objects are transitioned to the specified storage class.

    Default:
        No transition count.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-s3.NotificationKeyFilter", jsii_struct_bases=[])
class NotificationKeyFilter(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    prefix: str
    """S3 keys must have the specified prefix.

    Stability:
        experimental
    """

    suffix: str
    """S3 keys must have the specified suffix.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-s3.OnCloudTrailBucketEventOptions", jsii_struct_bases=[aws_cdk.aws_events.OnEventOptions])
class OnCloudTrailBucketEventOptions(aws_cdk.aws_events.OnEventOptions, jsii.compat.TypedDict, total=False):
    """Options for the onCloudTrailPutObject method.

    Stability:
        experimental
    """
    paths: typing.List[str]
    """Only watch changes to these object paths.

    Default:
        - Watch changes to all objects

    Stability:
        experimental
    """

class StorageClass(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-s3.StorageClass"):
    """Storage class to move an object to.

    Stability:
        experimental
    """
    def __init__(self, value: str) -> None:
        """
        Arguments:
            value: -

        Stability:
            experimental
        """
        jsii.create(StorageClass, self, [value])

    @jsii.member(jsii_name="toString")
    def to_string(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.invoke(self, "toString", [])

    @classproperty
    @jsii.member(jsii_name="DeepArchive")
    def DEEP_ARCHIVE(cls) -> "StorageClass":
        """Use for archiving data that rarely needs to be accessed.

        Data stored in the
        DEEP_ARCHIVE storage class has a minimum storage duration period of 180
        days and a default retrieval time of 12 hours. If you delete an object
        before the 180-day minimum, you are charged for 180 days. For pricing
        information, see Amazon S3 Pricing.

        Stability:
            experimental
        """
        return jsii.sget(cls, "DeepArchive")

    @classproperty
    @jsii.member(jsii_name="Glacier")
    def GLACIER(cls) -> "StorageClass":
        """Storage class for long-term archival that can take between minutes and hours to access.

        Use for archives where portions of the data might need to be retrieved in
        minutes. Data stored in the GLACIER storage class has a minimum storage
        duration period of 90 days and can be accessed in as little as 1-5 minutes
        using expedited retrieval. If you delete an object before the 90-day
        minimum, you are charged for 90 days.

        Stability:
            experimental
        """
        return jsii.sget(cls, "Glacier")

    @classproperty
    @jsii.member(jsii_name="InfrequentAccess")
    def INFREQUENT_ACCESS(cls) -> "StorageClass":
        """Storage class for data that is accessed less frequently, but requires rapid access when needed.

        Has lower availability than Standard storage.

        Stability:
            experimental
        """
        return jsii.sget(cls, "InfrequentAccess")

    @classproperty
    @jsii.member(jsii_name="IntelligentTiering")
    def INTELLIGENT_TIERING(cls) -> "StorageClass":
        """The INTELLIGENT_TIERING storage class is designed to optimize storage costs by automatically moving data to the most cost-effective storage access tier, without performance impact or operational overhead. INTELLIGENT_TIERING delivers automatic cost savings by moving data on a granular object level between two access tiers, a frequent access tier and a lower-cost infrequent access tier, when access patterns change. The INTELLIGENT_TIERING storage class is ideal if you want to optimize storage costs automatically for long-lived data when access patterns are unknown or unpredictable.

        Stability:
            experimental
        """
        return jsii.sget(cls, "IntelligentTiering")

    @classproperty
    @jsii.member(jsii_name="OneZoneInfrequentAccess")
    def ONE_ZONE_INFREQUENT_ACCESS(cls) -> "StorageClass":
        """Infrequent Access that's only stored in one availability zone.

        Has lower availability than standard InfrequentAccess.

        Stability:
            experimental
        """
        return jsii.sget(cls, "OneZoneInfrequentAccess")

    @property
    @jsii.member(jsii_name="value")
    def value(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "value")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _Transition(jsii.compat.TypedDict, total=False):
    transitionDate: datetime.datetime
    """Indicates when objects are transitioned to the specified storage class.

    The date value must be in ISO 8601 format. The time is always midnight UTC.

    Default:
        No transition date.

    Stability:
        experimental
    """
    transitionInDays: jsii.Number
    """Indicates the number of days after creation when objects are transitioned to the specified storage class.

    Default:
        No transition count.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-s3.Transition", jsii_struct_bases=[_Transition])
class Transition(_Transition):
    """Describes when an object transitions to a specified storage class.

    Stability:
        experimental
    """
    storageClass: "StorageClass"
    """The storage class to which you want the object to transition.

    Stability:
        experimental
    """

__all__ = ["BlockPublicAccess", "BlockPublicAccessOptions", "Bucket", "BucketAttributes", "BucketEncryption", "BucketMetrics", "BucketNotificationDestinationConfig", "BucketNotificationDestinationType", "BucketPolicy", "BucketPolicyProps", "BucketProps", "CfnBucket", "CfnBucketPolicy", "CfnBucketPolicyProps", "CfnBucketProps", "CorsRule", "EventType", "HttpMethods", "IBucket", "IBucketNotificationDestination", "LifecycleRule", "Location", "NoncurrentVersionTransition", "NotificationKeyFilter", "OnCloudTrailBucketEventOptions", "StorageClass", "Transition", "__jsii_assembly__"]

publication.publish()
