import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/cx-api", "0.34.0", __name__, "cx-api@0.34.0.jsii.tgz")
@jsii.data_type_optionals(jsii_struct_bases=[])
class _ArtifactManifest(jsii.compat.TypedDict, total=False):
    dependencies: typing.List[str]
    """IDs of artifacts that must be deployed before this artifact.

    Stability:
        experimental
    """
    metadata: typing.Mapping[str,typing.List["MetadataEntry"]]
    """Associated metadata.

    Stability:
        experimental
    """
    properties: typing.Mapping[str,typing.Any]
    """The set of properties for this artifact (depends on type).

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/cx-api.ArtifactManifest", jsii_struct_bases=[_ArtifactManifest])
class ArtifactManifest(_ArtifactManifest):
    """A manifest for a single artifact within the cloud assembly.

    Stability:
        experimental
    """
    environment: str
    """The environment into which this artifact is deployed.

    Stability:
        experimental
    """

    type: "ArtifactType"
    """The type of artifact.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/cx-api.ArtifactType")
class ArtifactType(enum.Enum):
    """Type of cloud artifact.

    Stability:
        experimental
    """
    None_ = "None"
    """
    Stability:
        experimental
    """
    AwsCloudFormationStack = "AwsCloudFormationStack"
    """The artifact is an AWS CloudFormation stack.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/cx-api.AssemblyBuildOptions", jsii_struct_bases=[])
class AssemblyBuildOptions(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    runtimeInfo: "RuntimeInfo"
    """Include runtime information (module versions) in manifest.

    Default:
        true

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _AssemblyManifest(jsii.compat.TypedDict, total=False):
    artifacts: typing.Mapping[str,"ArtifactManifest"]
    """The set of artifacts in this assembly.

    Stability:
        experimental
    """
    missing: typing.List["MissingContext"]
    """Missing context information.

    If this field has values, it means that the
    cloud assembly is not complete and should not be deployed.

    Stability:
        experimental
    """
    runtime: "RuntimeInfo"
    """Runtime information.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/cx-api.AssemblyManifest", jsii_struct_bases=[_AssemblyManifest])
class AssemblyManifest(_AssemblyManifest):
    """A manifest which describes the cloud assembly.

    Stability:
        experimental
    """
    version: str
    """Protocol version.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/cx-api.AvailabilityZonesContextQuery", jsii_struct_bases=[])
class AvailabilityZonesContextQuery(jsii.compat.TypedDict, total=False):
    """Query to hosted zone context provider.

    Stability:
        experimental
    """
    account: str
    """Query account.

    Stability:
        experimental
    """

    region: str
    """Query region.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _AwsCloudFormationStackProperties(jsii.compat.TypedDict, total=False):
    parameters: typing.Mapping[str,str]
    """Values for CloudFormation stack parameters that should be passed when the stack is deployed.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/cx-api.AwsCloudFormationStackProperties", jsii_struct_bases=[_AwsCloudFormationStackProperties])
class AwsCloudFormationStackProperties(_AwsCloudFormationStackProperties):
    """Artifact properties for CloudFormation stacks.

    Stability:
        experimental
    """
    templateFile: str
    """A file relative to the assembly root which contains the CloudFormation template for this stack.

    Stability:
        experimental
    """

class CloudArtifact(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cx-api.CloudArtifact"):
    """Represents an artifact within a cloud assembly.

    Stability:
        experimental
    """
    def __init__(self, assembly: "CloudAssembly", id: str, *, environment: str, type: "ArtifactType", dependencies: typing.Optional[typing.List[str]]=None, metadata: typing.Optional[typing.Mapping[str,typing.List["MetadataEntry"]]]=None, properties: typing.Optional[typing.Mapping[str,typing.Any]]=None) -> None:
        """
        Arguments:
            assembly: -
            id: -
            manifest: -
            environment: The environment into which this artifact is deployed.
            type: The type of artifact.
            dependencies: IDs of artifacts that must be deployed before this artifact.
            metadata: Associated metadata.
            properties: The set of properties for this artifact (depends on type).

        Stability:
            experimental
        """
        manifest: ArtifactManifest = {"environment": environment, "type": type}

        if dependencies is not None:
            manifest["dependencies"] = dependencies

        if metadata is not None:
            manifest["metadata"] = metadata

        if properties is not None:
            manifest["properties"] = properties

        jsii.create(CloudArtifact, self, [assembly, id, manifest])

    @jsii.member(jsii_name="from")
    @classmethod
    def from_(cls, assembly: "CloudAssembly", id: str, *, environment: str, type: "ArtifactType", dependencies: typing.Optional[typing.List[str]]=None, metadata: typing.Optional[typing.Mapping[str,typing.List["MetadataEntry"]]]=None, properties: typing.Optional[typing.Mapping[str,typing.Any]]=None) -> "CloudArtifact":
        """Returns a subclass of ``CloudArtifact`` based on the artifact type defined in the artifact manifest.

        Arguments:
            assembly: The cloud assembly from which to load the artifact.
            id: The artifact ID.
            artifact: The artifact manifest.
            environment: The environment into which this artifact is deployed.
            type: The type of artifact.
            dependencies: IDs of artifacts that must be deployed before this artifact.
            metadata: Associated metadata.
            properties: The set of properties for this artifact (depends on type).

        Stability:
            experimental
        """
        artifact: ArtifactManifest = {"environment": environment, "type": type}

        if dependencies is not None:
            artifact["dependencies"] = dependencies

        if metadata is not None:
            artifact["metadata"] = metadata

        if properties is not None:
            artifact["properties"] = properties

        return jsii.sinvoke(cls, "from", [assembly, id, artifact])

    @jsii.member(jsii_name="findMetadataByType")
    def find_metadata_by_type(self, type: str) -> typing.List["MetadataEntryResult"]:
        """
        Arguments:
            type: -

        Returns:
            all the metadata entries of a specific type in this artifact.

        Stability:
            experimental
        """
        return jsii.invoke(self, "findMetadataByType", [type])

    @property
    @jsii.member(jsii_name="assembly")
    def assembly(self) -> "CloudAssembly":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "assembly")

    @property
    @jsii.member(jsii_name="dependencies")
    def dependencies(self) -> typing.List["CloudArtifact"]:
        """Returns all the artifacts that this artifact depends on.

        Stability:
            experimental
        """
        return jsii.get(self, "dependencies")

    @property
    @jsii.member(jsii_name="environment")
    def environment(self) -> "Environment":
        """The environment into which to deploy this artifact.

        Stability:
            experimental
        """
        return jsii.get(self, "environment")

    @property
    @jsii.member(jsii_name="id")
    def id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "id")

    @property
    @jsii.member(jsii_name="manifest")
    def manifest(self) -> "ArtifactManifest":
        """The artifact's manifest.

        Stability:
            experimental
        """
        return jsii.get(self, "manifest")

    @property
    @jsii.member(jsii_name="messages")
    def messages(self) -> typing.List["SynthesisMessage"]:
        """The set of messages extracted from the artifact's metadata.

        Stability:
            experimental
        """
        return jsii.get(self, "messages")


class CloudAssembly(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cx-api.CloudAssembly"):
    """Represents a deployable cloud application.

    Stability:
        experimental
    """
    def __init__(self, directory: str) -> None:
        """Reads a cloud assembly from the specified directory.

        Arguments:
            directory: The root directory of the assembly.

        Stability:
            experimental
        """
        jsii.create(CloudAssembly, self, [directory])

    @jsii.member(jsii_name="getStack")
    def get_stack(self, stack_name: str) -> "CloudFormationStackArtifact":
        """Returns a CloudFormation stack artifact from this assembly.

        Arguments:
            stackName: the name of the CloudFormation stack.

        Returns:
            a ``CloudFormationStackArtifact`` object.

        Stability:
            experimental
        throws:
            if there is no stack artifact by that name
        """
        return jsii.invoke(self, "getStack", [stack_name])

    @jsii.member(jsii_name="tryGetArtifact")
    def try_get_artifact(self, id: str) -> typing.Optional["CloudArtifact"]:
        """Attempts to find an artifact with a specific identity.

        Arguments:
            id: The artifact ID.

        Returns:
            A ``CloudArtifact`` object or ``undefined`` if the artifact does not exist in this assembly.

        Stability:
            experimental
        """
        return jsii.invoke(self, "tryGetArtifact", [id])

    @property
    @jsii.member(jsii_name="artifacts")
    def artifacts(self) -> typing.List["CloudArtifact"]:
        """All artifacts included in this assembly.

        Stability:
            experimental
        """
        return jsii.get(self, "artifacts")

    @property
    @jsii.member(jsii_name="directory")
    def directory(self) -> str:
        """The root directory of the cloud assembly.

        Stability:
            experimental
        """
        return jsii.get(self, "directory")

    @property
    @jsii.member(jsii_name="manifest")
    def manifest(self) -> "AssemblyManifest":
        """The raw assembly manifest.

        Stability:
            experimental
        """
        return jsii.get(self, "manifest")

    @property
    @jsii.member(jsii_name="runtime")
    def runtime(self) -> "RuntimeInfo":
        """Runtime information such as module versions used to synthesize this assembly.

        Stability:
            experimental
        """
        return jsii.get(self, "runtime")

    @property
    @jsii.member(jsii_name="stacks")
    def stacks(self) -> typing.List["CloudFormationStackArtifact"]:
        """
        Returns:
            all the CloudFormation stack artifacts that are included in this assembly.

        Stability:
            experimental
        """
        return jsii.get(self, "stacks")

    @property
    @jsii.member(jsii_name="version")
    def version(self) -> str:
        """The schema version of the assembly manifest.

        Stability:
            experimental
        """
        return jsii.get(self, "version")


class CloudAssemblyBuilder(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cx-api.CloudAssemblyBuilder"):
    """Can be used to build a cloud assembly.

    Stability:
        experimental
    """
    def __init__(self, outdir: typing.Optional[str]=None) -> None:
        """Initializes a cloud assembly builder.

        Arguments:
            outdir: The output directory, uses temporary directory if undefined.

        Stability:
            experimental
        """
        jsii.create(CloudAssemblyBuilder, self, [outdir])

    @jsii.member(jsii_name="addArtifact")
    def add_artifact(self, id: str, *, environment: str, type: "ArtifactType", dependencies: typing.Optional[typing.List[str]]=None, metadata: typing.Optional[typing.Mapping[str,typing.List["MetadataEntry"]]]=None, properties: typing.Optional[typing.Mapping[str,typing.Any]]=None) -> None:
        """Adds an artifact into the cloud assembly.

        Arguments:
            id: The ID of the artifact.
            manifest: The artifact manifest.
            environment: The environment into which this artifact is deployed.
            type: The type of artifact.
            dependencies: IDs of artifacts that must be deployed before this artifact.
            metadata: Associated metadata.
            properties: The set of properties for this artifact (depends on type).

        Stability:
            experimental
        """
        manifest: ArtifactManifest = {"environment": environment, "type": type}

        if dependencies is not None:
            manifest["dependencies"] = dependencies

        if metadata is not None:
            manifest["metadata"] = metadata

        if properties is not None:
            manifest["properties"] = properties

        return jsii.invoke(self, "addArtifact", [id, manifest])

    @jsii.member(jsii_name="addMissing")
    def add_missing(self, *, key: str, props: typing.Mapping[str,typing.Any], provider: str) -> None:
        """Reports that some context is missing in order for this cloud assembly to be fully synthesized.

        Arguments:
            missing: Missing context information.
            key: The missing context key.
            props: A set of provider-specific options.
            provider: The provider from which we expect this context key to be obtained.

        Stability:
            experimental
        """
        missing: MissingContext = {"key": key, "props": props, "provider": provider}

        return jsii.invoke(self, "addMissing", [missing])

    @jsii.member(jsii_name="build")
    def build(self, *, runtime_info: typing.Optional["RuntimeInfo"]=None) -> "CloudAssembly":
        """Finalizes the cloud assembly into the output directory returns a ``CloudAssembly`` object that can be used to inspect the assembly.

        Arguments:
            options: -
            runtimeInfo: Include runtime information (module versions) in manifest. Default: true

        Stability:
            experimental
        """
        options: AssemblyBuildOptions = {}

        if runtime_info is not None:
            options["runtimeInfo"] = runtime_info

        return jsii.invoke(self, "build", [options])

    @property
    @jsii.member(jsii_name="outdir")
    def outdir(self) -> str:
        """The root directory of the resulting cloud assembly.

        Stability:
            experimental
        """
        return jsii.get(self, "outdir")


class CloudFormationStackArtifact(CloudArtifact, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cx-api.CloudFormationStackArtifact"):
    """
    Stability:
        experimental
    """
    def __init__(self, assembly: "CloudAssembly", name: str, *, environment: str, type: "ArtifactType", dependencies: typing.Optional[typing.List[str]]=None, metadata: typing.Optional[typing.Mapping[str,typing.List["MetadataEntry"]]]=None, properties: typing.Optional[typing.Mapping[str,typing.Any]]=None) -> None:
        """
        Arguments:
            assembly: -
            name: -
            artifact: -
            environment: The environment into which this artifact is deployed.
            type: The type of artifact.
            dependencies: IDs of artifacts that must be deployed before this artifact.
            metadata: Associated metadata.
            properties: The set of properties for this artifact (depends on type).

        Stability:
            experimental
        """
        artifact: ArtifactManifest = {"environment": environment, "type": type}

        if dependencies is not None:
            artifact["dependencies"] = dependencies

        if metadata is not None:
            artifact["metadata"] = metadata

        if properties is not None:
            artifact["properties"] = properties

        jsii.create(CloudFormationStackArtifact, self, [assembly, name, artifact])

    @property
    @jsii.member(jsii_name="assets")
    def assets(self) -> typing.List[typing.Union["FileAssetMetadataEntry", "ContainerImageAssetMetadataEntry"]]:
        """Any assets associated with this stack.

        Stability:
            experimental
        """
        return jsii.get(self, "assets")

    @property
    @jsii.member(jsii_name="originalName")
    def original_name(self) -> str:
        """The original name as defined in the CDK app.

        Stability:
            experimental
        """
        return jsii.get(self, "originalName")

    @property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Mapping[str,str]:
        """CloudFormation parameters to pass to the stack.

        Stability:
            experimental
        """
        return jsii.get(self, "parameters")

    @property
    @jsii.member(jsii_name="template")
    def template(self) -> typing.Any:
        """The CloudFormation template for this stack.

        Stability:
            experimental
        """
        return jsii.get(self, "template")

    @property
    @jsii.member(jsii_name="templateFile")
    def template_file(self) -> str:
        """The file name of the template.

        Stability:
            experimental
        """
        return jsii.get(self, "templateFile")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """The name of this stack.

        This is read/write and can be used to rename the stack.

        Stability:
            experimental
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _ContainerImageAssetMetadataEntry(jsii.compat.TypedDict, total=False):
    buildArgs: typing.Mapping[str,str]
    """Build args to pass to the ``docker build`` command.

    Default:
        no build args are passed

    Stability:
        experimental
    """
    repositoryName: str
    """ECR repository name, if omitted a default name based on the asset's ID is used instead.

    Specify this property if you need to statically
    address the image, e.g. from a Kubernetes Pod.
    Note, this is only the repository name, without the registry and
    the tag parts.

    Default:
        automatically derived from the asset's ID.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/cx-api.ContainerImageAssetMetadataEntry", jsii_struct_bases=[_ContainerImageAssetMetadataEntry])
class ContainerImageAssetMetadataEntry(_ContainerImageAssetMetadataEntry):
    """
    Stability:
        experimental
    """
    id: str
    """Logical identifier for the asset.

    Stability:
        experimental
    """

    imageNameParameter: str
    """ECR Repository name and repo digest (separated by "@sha256:") where this image is stored.

    Stability:
        experimental
    """

    packaging: str
    """Type of asset.

    Stability:
        experimental
    """

    path: str
    """Path on disk to the asset.

    Stability:
        experimental
    """

    sourceHash: str
    """The hash of the source directory used to build the asset.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/cx-api.Environment", jsii_struct_bases=[])
class Environment(jsii.compat.TypedDict):
    """Models an AWS execution environment, for use within the CDK toolkit.

    Stability:
        experimental
    """
    account: str
    """The 12-digit AWS account ID for the account this environment deploys into.

    Stability:
        experimental
    """

    name: str
    """The arbitrary name of this environment (user-set, or at least user-meaningful).

    Stability:
        experimental
    """

    region: str
    """The AWS region name where this environment deploys into.

    Stability:
        experimental
    """

class EnvironmentUtils(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cx-api.EnvironmentUtils"):
    """
    Stability:
        experimental
    """
    def __init__(self) -> None:
        jsii.create(EnvironmentUtils, self, [])

    @jsii.member(jsii_name="format")
    @classmethod
    def format(cls, account: str, region: str) -> str:
        """
        Arguments:
            account: -
            region: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "format", [account, region])

    @jsii.member(jsii_name="parse")
    @classmethod
    def parse(cls, environment: str) -> "Environment":
        """
        Arguments:
            environment: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "parse", [environment])


@jsii.data_type(jsii_type="@aws-cdk/cx-api.FileAssetMetadataEntry", jsii_struct_bases=[])
class FileAssetMetadataEntry(jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    artifactHashParameter: str
    """The name of the parameter where the hash of the bundled asset should be passed in.

    Stability:
        experimental
    """

    id: str
    """Logical identifier for the asset.

    Stability:
        experimental
    """

    packaging: str
    """Requested packaging style.

    Stability:
        experimental
    """

    path: str
    """Path on disk to the asset.

    Stability:
        experimental
    """

    s3BucketParameter: str
    """Name of parameter where S3 bucket should be passed in.

    Stability:
        experimental
    """

    s3KeyParameter: str
    """Name of parameter where S3 key should be passed in.

    Stability:
        experimental
    """

    sourceHash: str
    """The hash of the source directory used to build the asset.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _HostedZoneContextQuery(jsii.compat.TypedDict, total=False):
    account: str
    """Query account.

    Stability:
        experimental
    """
    privateZone: bool
    """True if the zone you want to find is a private hosted zone.

    Stability:
        experimental
    """
    region: str
    """Query region.

    Stability:
        experimental
    """
    vpcId: str
    """The VPC ID to that the private zone must be associated with.

    If you provide VPC ID and privateZone is false, this will return no results
    and raise an error.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/cx-api.HostedZoneContextQuery", jsii_struct_bases=[_HostedZoneContextQuery])
class HostedZoneContextQuery(_HostedZoneContextQuery):
    """Query to hosted zone context provider.

    Stability:
        experimental
    """
    domainName: str
    """The domain name e.g. example.com to lookup.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _MetadataEntry(jsii.compat.TypedDict, total=False):
    data: typing.Any
    """The data.

    Stability:
        experimental
    """
    trace: typing.List[str]
    """A stack trace for when the entry was created.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/cx-api.MetadataEntry", jsii_struct_bases=[_MetadataEntry])
class MetadataEntry(_MetadataEntry):
    """An metadata entry in the construct.

    Stability:
        experimental
    """
    type: str
    """The type of the metadata entry.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/cx-api.MetadataEntryResult", jsii_struct_bases=[MetadataEntry])
class MetadataEntryResult(MetadataEntry, jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    path: str
    """The path in which this entry was defined.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/cx-api.MissingContext", jsii_struct_bases=[])
class MissingContext(jsii.compat.TypedDict):
    """Represents a missing piece of context.

    Stability:
        experimental
    """
    key: str
    """The missing context key.

    Stability:
        experimental
    """

    props: typing.Mapping[str,typing.Any]
    """A set of provider-specific options.

    Stability:
        experimental
    """

    provider: str
    """The provider from which we expect this context key to be obtained.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/cx-api.RuntimeInfo", jsii_struct_bases=[])
class RuntimeInfo(jsii.compat.TypedDict):
    """Information about the application's runtime components.

    Stability:
        experimental
    """
    libraries: typing.Mapping[str,str]
    """The list of libraries loaded in the application, associated with their versions.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/cx-api.SSMParameterContextQuery", jsii_struct_bases=[])
class SSMParameterContextQuery(jsii.compat.TypedDict, total=False):
    """Query to hosted zone context provider.

    Stability:
        experimental
    """
    account: str
    """Query account.

    Stability:
        experimental
    """

    parameterName: str
    """Parameter name to query.

    Stability:
        experimental
    """

    region: str
    """Query region.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/cx-api.SynthesisMessage", jsii_struct_bases=[])
class SynthesisMessage(jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    entry: "MetadataEntry"
    """
    Stability:
        experimental
    """

    id: str
    """
    Stability:
        experimental
    """

    level: "SynthesisMessageLevel"
    """
    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/cx-api.SynthesisMessageLevel")
class SynthesisMessageLevel(enum.Enum):
    """
    Stability:
        experimental
    """
    INFO = "INFO"
    """
    Stability:
        experimental
    """
    WARNING = "WARNING"
    """
    Stability:
        experimental
    """
    ERROR = "ERROR"
    """
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _VpcContextQuery(jsii.compat.TypedDict, total=False):
    account: str
    """Query account.

    Stability:
        experimental
    """
    region: str
    """Query region.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/cx-api.VpcContextQuery", jsii_struct_bases=[_VpcContextQuery])
class VpcContextQuery(_VpcContextQuery):
    """Query input for looking up a VPC.

    Stability:
        experimental
    """
    filter: typing.Mapping[str,str]
    """Filters to apply to the VPC.

    Filter parameters are the same as passed to DescribeVpcs.

    See:
        https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeVpcs.html
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _VpcContextResponse(jsii.compat.TypedDict, total=False):
    isolatedSubnetIds: typing.List[str]
    """IDs of all isolated subnets.

    Element count: #(availabilityZones) · #(isolatedGroups)

    Stability:
        experimental
    """
    isolatedSubnetNames: typing.List[str]
    """Name of isolated subnet groups.

    Element count: #(isolatedGroups)

    Stability:
        experimental
    """
    privateSubnetIds: typing.List[str]
    """IDs of all private subnets.

    Element count: #(availabilityZones) · #(privateGroups)

    Stability:
        experimental
    """
    privateSubnetNames: typing.List[str]
    """Name of private subnet groups.

    Element count: #(privateGroups)

    Stability:
        experimental
    """
    publicSubnetIds: typing.List[str]
    """IDs of all public subnets.

    Element count: #(availabilityZones) · #(publicGroups)

    Stability:
        experimental
    """
    publicSubnetNames: typing.List[str]
    """Name of public subnet groups.

    Element count: #(publicGroups)

    Stability:
        experimental
    """
    vpnGatewayId: str
    """The VPN gateway ID.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/cx-api.VpcContextResponse", jsii_struct_bases=[_VpcContextResponse])
class VpcContextResponse(_VpcContextResponse):
    """Properties of a discovered VPC.

    Stability:
        experimental
    """
    availabilityZones: typing.List[str]
    """AZs.

    Stability:
        experimental
    """

    vpcId: str
    """VPC id.

    Stability:
        experimental
    """

__all__ = ["ArtifactManifest", "ArtifactType", "AssemblyBuildOptions", "AssemblyManifest", "AvailabilityZonesContextQuery", "AwsCloudFormationStackProperties", "CloudArtifact", "CloudAssembly", "CloudAssemblyBuilder", "CloudFormationStackArtifact", "ContainerImageAssetMetadataEntry", "Environment", "EnvironmentUtils", "FileAssetMetadataEntry", "HostedZoneContextQuery", "MetadataEntry", "MetadataEntryResult", "MissingContext", "RuntimeInfo", "SSMParameterContextQuery", "SynthesisMessage", "SynthesisMessageLevel", "VpcContextQuery", "VpcContextResponse", "__jsii_assembly__"]

publication.publish()
