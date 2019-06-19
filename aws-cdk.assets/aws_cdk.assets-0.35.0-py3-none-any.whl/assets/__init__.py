import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
import aws_cdk.cx_api
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/assets", "0.35.0", __name__, "assets@0.35.0.jsii.tgz")
@jsii.data_type(jsii_type="@aws-cdk/assets.CopyOptions", jsii_struct_bases=[])
class CopyOptions(jsii.compat.TypedDict, total=False):
    """Obtains applied when copying directories into the staging location.

    Stability:
        experimental
    """
    exclude: typing.List[str]
    """Glob patterns to exclude from the copy.

    Default:
        nothing is excluded

    Stability:
        experimental
    """

    follow: "FollowMode"
    """A strategy for how to handle symlinks.

    Default:
        Never

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/assets.FollowMode")
class FollowMode(enum.Enum):
    """
    Stability:
        experimental
    """
    Never = "Never"
    """Never follow symlinks.

    Stability:
        experimental
    """
    Always = "Always"
    """Materialize all symlinks, whether they are internal or external to the source directory.

    Stability:
        experimental
    """
    External = "External"
    """Only follows symlinks that are external to the source directory.

    Stability:
        experimental
    """
    BlockExternal = "BlockExternal"
    """Forbids source from having any symlinks pointing outside of the source tree.

    This is the safest mode of operation as it ensures that copy operations
    won't materialize files from the user's file system. Internal symlinks are
    not followed.

    If the copy operation runs into an external symlink, it will fail.

    Stability:
        experimental
    """

@jsii.interface(jsii_type="@aws-cdk/assets.IAsset")
class IAsset(jsii.compat.Protocol):
    """Common interface for all assets.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IAssetProxy

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
        ...

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
        ...


class _IAssetProxy():
    """Common interface for all assets.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/assets.IAsset"
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


class Staging(aws_cdk.cdk.Construct, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/assets.Staging"):
    """Stages a file or directory from a location on the file system into a staging directory.

    This is controlled by the context key 'aws:cdk:asset-staging' and enabled
    by the CLI by default in order to ensure that when the CDK app exists, all
    assets are available for deployment. Otherwise, if an app references assets
    in temporary locations, those will not be available when it exists (see
    https://github.com/awslabs/aws-cdk/issues/1716).

    The ``stagedPath`` property is a stringified token that represents the location
    of the file or directory after staging. It will be resolved only during the
    "prepare" stage and may be either the original path or the staged path
    depending on the context setting.

    The file/directory are staged based on their content hash (fingerprint). This
    means that only if content was changed, copy will happen.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, source_path: str, exclude: typing.Optional[typing.List[str]]=None, follow: typing.Optional["FollowMode"]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            sourcePath: 
            exclude: Glob patterns to exclude from the copy. Default: nothing is excluded
            follow: A strategy for how to handle symlinks. Default: Never

        Stability:
            experimental
        """
        props: StagingProps = {"sourcePath": source_path}

        if exclude is not None:
            props["exclude"] = exclude

        if follow is not None:
            props["follow"] = follow

        jsii.create(Staging, self, [scope, id, props])

    @jsii.member(jsii_name="synthesize")
    def _synthesize(self, session: aws_cdk.cdk.ISynthesisSession) -> None:
        """Allows this construct to emit artifacts into the cloud assembly during synthesis.

        This method is usually implemented by framework-level constructs such as ``Stack`` and ``Asset``
        as they participate in synthesizing the cloud assembly.

        Arguments:
            session: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "synthesize", [session])

    @property
    @jsii.member(jsii_name="sourceHash")
    def source_hash(self) -> str:
        """A cryptographic hash of the source document(s).

        Stability:
            experimental
        """
        return jsii.get(self, "sourceHash")

    @property
    @jsii.member(jsii_name="sourcePath")
    def source_path(self) -> str:
        """The path of the asset as it was referenced by the user.

        Stability:
            experimental
        """
        return jsii.get(self, "sourcePath")

    @property
    @jsii.member(jsii_name="stagedPath")
    def staged_path(self) -> str:
        """The path to the asset (stringinfied token).

        If asset staging is disabled, this will just be the original path.
        If asset staging is enabled it will be the staged path.

        Stability:
            experimental
        """
        return jsii.get(self, "stagedPath")


@jsii.data_type(jsii_type="@aws-cdk/assets.StagingProps", jsii_struct_bases=[CopyOptions])
class StagingProps(CopyOptions, jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    sourcePath: str
    """
    Stability:
        experimental
    """

__all__ = ["CopyOptions", "FollowMode", "IAsset", "Staging", "StagingProps", "__jsii_assembly__"]

publication.publish()
