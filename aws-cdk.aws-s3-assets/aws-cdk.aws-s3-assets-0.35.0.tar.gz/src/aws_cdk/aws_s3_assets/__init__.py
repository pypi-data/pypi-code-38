import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.assets
import aws_cdk.aws_iam
import aws_cdk.aws_s3
import aws_cdk.cdk
import aws_cdk.cx_api
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-s3-assets", "0.35.0", __name__, "aws-s3-assets@0.35.0.jsii.tgz")
@jsii.implements(aws_cdk.assets.IAsset)
class Asset(aws_cdk.cdk.Construct, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-s3-assets.Asset"):
    """An asset represents a local file or directory, which is automatically uploaded to S3 and then can be referenced within a CDK application.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, path: str, readers: typing.Optional[typing.List[aws_cdk.aws_iam.IGrantable]]=None, exclude: typing.Optional[typing.List[str]]=None, follow: typing.Optional[aws_cdk.assets.FollowMode]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            path: The disk location of the asset. The path should refer to one of the following: - A regular file or a .zip file, in which case the file will be uploaded as-is to S3. - A directory, in which case it will be archived into a .zip file and uploaded to S3.
            readers: A list of principals that should be able to read this asset from S3. You can use ``asset.grantRead(principal)`` to grant read permissions later. Default: - No principals that can read file asset.
            exclude: Glob patterns to exclude from the copy. Default: nothing is excluded
            follow: A strategy for how to handle symlinks. Default: Never

        Stability:
            experimental
        """
        props: AssetProps = {"path": path}

        if readers is not None:
            props["readers"] = readers

        if exclude is not None:
            props["exclude"] = exclude

        if follow is not None:
            props["follow"] = follow

        jsii.create(Asset, self, [scope, id, props])

    @jsii.member(jsii_name="addResourceMetadata")
    def add_resource_metadata(self, resource: aws_cdk.cdk.CfnResource, resource_property: str) -> None:
        """Adds CloudFormation template metadata to the specified resource with information that indicates which resource property is mapped to this local asset.

        This can be used by tools such as SAM CLI to provide local
        experience such as local invocation and debugging of Lambda functions.

        Asset metadata will only be included if the stack is synthesized with the
        "aws:cdk:enable-asset-metadata" context key defined, which is the default
        behavior when synthesizing via the CDK Toolkit.

        Arguments:
            resource: The CloudFormation resource which is using this asset [disable-awslint:ref-via-interface].
            resourceProperty: The property name where this asset is referenced (e.g. "Code" for AWS::Lambda::Function).

        See:
            https://github.com/awslabs/aws-cdk/issues/1432
        Stability:
            experimental
        """
        return jsii.invoke(self, "addResourceMetadata", [resource, resource_property])

    @jsii.member(jsii_name="grantRead")
    def grant_read(self, grantee: aws_cdk.aws_iam.IGrantable) -> None:
        """Grants read permissions to the principal on the asset's S3 object.

        Arguments:
            grantee: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantRead", [grantee])

    @property
    @jsii.member(jsii_name="artifactHash")
    def artifact_hash(self) -> str:
        """A hash of the bundle for of this asset, which is only available at deployment time.

        As this is
        a late-bound token, it may not be used in construct IDs, but can be passed as a resource
        property in order to force a change on a resource when an asset is effectively updated. This is
        more reliable than ``sourceHash`` in particular for assets which bundling phase involve external
        resources that can change over time (such as Docker image builds).

        Stability:
            experimental
        """
        return jsii.get(self, "artifactHash")

    @property
    @jsii.member(jsii_name="assetPath")
    def asset_path(self) -> str:
        """The path to the asset (stringinfied token).

        If asset staging is disabled, this will just be the original path.
        If asset staging is enabled it will be the staged path.

        Stability:
            experimental
        """
        return jsii.get(self, "assetPath")

    @property
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> aws_cdk.aws_s3.IBucket:
        """The S3 bucket in which this asset resides.

        Stability:
            experimental
        """
        return jsii.get(self, "bucket")

    @property
    @jsii.member(jsii_name="isZipArchive")
    def is_zip_archive(self) -> bool:
        """Indicates if this asset is a zip archive.

        Allows constructs to ensure that the
        correct file type was used.

        Stability:
            experimental
        """
        return jsii.get(self, "isZipArchive")

    @property
    @jsii.member(jsii_name="s3BucketName")
    def s3_bucket_name(self) -> str:
        """Attribute that represents the name of the bucket this asset exists in.

        Stability:
            experimental
        """
        return jsii.get(self, "s3BucketName")

    @property
    @jsii.member(jsii_name="s3ObjectKey")
    def s3_object_key(self) -> str:
        """Attribute which represents the S3 object key of this asset.

        Stability:
            experimental
        """
        return jsii.get(self, "s3ObjectKey")

    @property
    @jsii.member(jsii_name="s3Url")
    def s3_url(self) -> str:
        """Attribute which represents the S3 URL of this asset.

        Stability:
            experimental

        Example::
            https://s3.us-west-1.amazonaws.com/bucket/key
        """
        return jsii.get(self, "s3Url")

    @property
    @jsii.member(jsii_name="sourceHash")
    def source_hash(self) -> str:
        """A hash of the source of this asset, which is available at construction time.

        As this is a plain
        string, it can be used in construct IDs in order to enforce creation of a new resource when
        the content hash has changed.

        Stability:
            experimental
        """
        return jsii.get(self, "sourceHash")


@jsii.enum(jsii_type="@aws-cdk/aws-s3-assets.AssetPackaging")
class AssetPackaging(enum.Enum):
    """Defines the way an asset is packaged before it is uploaded to S3.

    Stability:
        experimental
    """
    ZipDirectory = "ZipDirectory"
    """Path refers to a directory on disk, the contents of the directory is archived into a .zip.

    Stability:
        experimental
    """
    File = "File"
    """Path refers to a single file on disk.

    The file is uploaded as-is.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[aws_cdk.assets.CopyOptions])
class _AssetProps(aws_cdk.assets.CopyOptions, jsii.compat.TypedDict, total=False):
    readers: typing.List[aws_cdk.aws_iam.IGrantable]
    """A list of principals that should be able to read this asset from S3. You can use ``asset.grantRead(principal)`` to grant read permissions later.

    Default:
        - No principals that can read file asset.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-s3-assets.AssetProps", jsii_struct_bases=[_AssetProps])
class AssetProps(_AssetProps):
    """
    Stability:
        experimental
    """
    path: str
    """The disk location of the asset.

    The path should refer to one of the following:

    - A regular file or a .zip file, in which case the file will be uploaded as-is to S3.
    - A directory, in which case it will be archived into a .zip file and uploaded to S3.

    Stability:
        experimental
    """

__all__ = ["Asset", "AssetPackaging", "AssetProps", "__jsii_assembly__"]

publication.publish()
