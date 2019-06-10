import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.assets
import aws_cdk.aws_cloudformation
import aws_cdk.aws_ecr
import aws_cdk.aws_iam
import aws_cdk.aws_lambda
import aws_cdk.aws_s3
import aws_cdk.cdk
import aws_cdk.cx_api
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/assets-docker", "0.34.0", __name__, "assets-docker@0.34.0.jsii.tgz")
@jsii.implements(aws_cdk.assets.IAsset)
class DockerImageAsset(aws_cdk.cdk.Construct, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/assets-docker.DockerImageAsset"):
    """An asset that represents a Docker image.

    The image will be created in build time and uploaded to an ECR repository.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, directory: str, build_args: typing.Optional[typing.Mapping[str,str]]=None, repository_name: typing.Optional[str]=None, exclude: typing.Optional[typing.List[str]]=None, follow: typing.Optional[aws_cdk.assets.FollowMode]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            directory: The directory where the Dockerfile is stored.
            buildArgs: Build args to pass to the ``docker build`` command. Default: no build args are passed
            repositoryName: ECR repository name. Specify this property if you need to statically address the image, e.g. from a Kubernetes Pod. Note, this is only the repository name, without the registry and the tag parts. Default: automatically derived from the asset's ID.
            exclude: Glob patterns to exclude from the copy. Default: nothing is excluded
            follow: A strategy for how to handle symlinks. Default: Never

        Stability:
            experimental
        """
        props: DockerImageAssetProps = {"directory": directory}

        if build_args is not None:
            props["buildArgs"] = build_args

        if repository_name is not None:
            props["repositoryName"] = repository_name

        if exclude is not None:
            props["exclude"] = exclude

        if follow is not None:
            props["follow"] = follow

        jsii.create(DockerImageAsset, self, [scope, id, props])

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

    @property
    @jsii.member(jsii_name="imageUri")
    def image_uri(self) -> str:
        """The full URI of the image (including a tag).

        Use this reference to pull
        the asset.

        Stability:
            experimental
        """
        return jsii.get(self, "imageUri")

    @image_uri.setter
    def image_uri(self, value: str):
        return jsii.set(self, "imageUri", value)

    @property
    @jsii.member(jsii_name="repository")
    def repository(self) -> aws_cdk.aws_ecr.IRepository:
        """Repository where the image is stored.

        Stability:
            experimental
        """
        return jsii.get(self, "repository")

    @repository.setter
    def repository(self, value: aws_cdk.aws_ecr.IRepository):
        return jsii.set(self, "repository", value)


@jsii.data_type_optionals(jsii_struct_bases=[aws_cdk.assets.CopyOptions])
class _DockerImageAssetProps(aws_cdk.assets.CopyOptions, jsii.compat.TypedDict, total=False):
    buildArgs: typing.Mapping[str,str]
    """Build args to pass to the ``docker build`` command.

    Default:
        no build args are passed

    Stability:
        experimental
    """
    repositoryName: str
    """ECR repository name.

    Specify this property if you need to statically address the image, e.g.
    from a Kubernetes Pod. Note, this is only the repository name, without the
    registry and the tag parts.

    Default:
        automatically derived from the asset's ID.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/assets-docker.DockerImageAssetProps", jsii_struct_bases=[_DockerImageAssetProps])
class DockerImageAssetProps(_DockerImageAssetProps):
    """
    Stability:
        experimental
    """
    directory: str
    """The directory where the Dockerfile is stored.

    Stability:
        experimental
    """

__all__ = ["DockerImageAsset", "DockerImageAssetProps", "__jsii_assembly__"]

publication.publish()
