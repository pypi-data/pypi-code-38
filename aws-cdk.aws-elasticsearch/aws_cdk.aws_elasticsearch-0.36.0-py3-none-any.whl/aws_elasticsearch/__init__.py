import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-elasticsearch", "0.36.0", __name__, "aws-elasticsearch@0.36.0.jsii.tgz")
class CfnDomain(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-elasticsearch.CfnDomain"):
    """A CloudFormation ``AWS::Elasticsearch::Domain``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html
    Stability:
        stable
    cloudformationResource:
        AWS::Elasticsearch::Domain
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, access_policies: typing.Any=None, advanced_options: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,str]]]]=None, domain_name: typing.Optional[str]=None, ebs_options: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["EBSOptionsProperty"]]]=None, elasticsearch_cluster_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ElasticsearchClusterConfigProperty"]]]=None, elasticsearch_version: typing.Optional[str]=None, encryption_at_rest_options: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["EncryptionAtRestOptionsProperty"]]]=None, node_to_node_encryption_options: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["NodeToNodeEncryptionOptionsProperty"]]]=None, snapshot_options: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SnapshotOptionsProperty"]]]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None, vpc_options: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["VPCOptionsProperty"]]]=None) -> None:
        """Create a new ``AWS::Elasticsearch::Domain``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            access_policies: ``AWS::Elasticsearch::Domain.AccessPolicies``.
            advanced_options: ``AWS::Elasticsearch::Domain.AdvancedOptions``.
            domain_name: ``AWS::Elasticsearch::Domain.DomainName``.
            ebs_options: ``AWS::Elasticsearch::Domain.EBSOptions``.
            elasticsearch_cluster_config: ``AWS::Elasticsearch::Domain.ElasticsearchClusterConfig``.
            elasticsearch_version: ``AWS::Elasticsearch::Domain.ElasticsearchVersion``.
            encryption_at_rest_options: ``AWS::Elasticsearch::Domain.EncryptionAtRestOptions``.
            node_to_node_encryption_options: ``AWS::Elasticsearch::Domain.NodeToNodeEncryptionOptions``.
            snapshot_options: ``AWS::Elasticsearch::Domain.SnapshotOptions``.
            tags: ``AWS::Elasticsearch::Domain.Tags``.
            vpc_options: ``AWS::Elasticsearch::Domain.VPCOptions``.

        Stability:
            experimental
        """
        props: CfnDomainProps = {}

        if access_policies is not None:
            props["accessPolicies"] = access_policies

        if advanced_options is not None:
            props["advancedOptions"] = advanced_options

        if domain_name is not None:
            props["domainName"] = domain_name

        if ebs_options is not None:
            props["ebsOptions"] = ebs_options

        if elasticsearch_cluster_config is not None:
            props["elasticsearchClusterConfig"] = elasticsearch_cluster_config

        if elasticsearch_version is not None:
            props["elasticsearchVersion"] = elasticsearch_version

        if encryption_at_rest_options is not None:
            props["encryptionAtRestOptions"] = encryption_at_rest_options

        if node_to_node_encryption_options is not None:
            props["nodeToNodeEncryptionOptions"] = node_to_node_encryption_options

        if snapshot_options is not None:
            props["snapshotOptions"] = snapshot_options

        if tags is not None:
            props["tags"] = tags

        if vpc_options is not None:
            props["vpcOptions"] = vpc_options

        jsii.create(CfnDomain, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "attrArn")

    @property
    @jsii.member(jsii_name="attrDomainEndpoint")
    def attr_domain_endpoint(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            DomainEndpoint
        """
        return jsii.get(self, "attrDomainEndpoint")

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
        """``AWS::Elasticsearch::Domain.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="accessPolicies")
    def access_policies(self) -> typing.Any:
        """``AWS::Elasticsearch::Domain.AccessPolicies``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-accesspolicies
        Stability:
            stable
        """
        return jsii.get(self, "accessPolicies")

    @access_policies.setter
    def access_policies(self, value: typing.Any):
        return jsii.set(self, "accessPolicies", value)

    @property
    @jsii.member(jsii_name="advancedOptions")
    def advanced_options(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,str]]]]:
        """``AWS::Elasticsearch::Domain.AdvancedOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-advancedoptions
        Stability:
            stable
        """
        return jsii.get(self, "advancedOptions")

    @advanced_options.setter
    def advanced_options(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,str]]]]):
        return jsii.set(self, "advancedOptions", value)

    @property
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> typing.Optional[str]:
        """``AWS::Elasticsearch::Domain.DomainName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-domainname
        Stability:
            stable
        """
        return jsii.get(self, "domainName")

    @domain_name.setter
    def domain_name(self, value: typing.Optional[str]):
        return jsii.set(self, "domainName", value)

    @property
    @jsii.member(jsii_name="ebsOptions")
    def ebs_options(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["EBSOptionsProperty"]]]:
        """``AWS::Elasticsearch::Domain.EBSOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-ebsoptions
        Stability:
            stable
        """
        return jsii.get(self, "ebsOptions")

    @ebs_options.setter
    def ebs_options(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["EBSOptionsProperty"]]]):
        return jsii.set(self, "ebsOptions", value)

    @property
    @jsii.member(jsii_name="elasticsearchClusterConfig")
    def elasticsearch_cluster_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ElasticsearchClusterConfigProperty"]]]:
        """``AWS::Elasticsearch::Domain.ElasticsearchClusterConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-elasticsearchclusterconfig
        Stability:
            stable
        """
        return jsii.get(self, "elasticsearchClusterConfig")

    @elasticsearch_cluster_config.setter
    def elasticsearch_cluster_config(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ElasticsearchClusterConfigProperty"]]]):
        return jsii.set(self, "elasticsearchClusterConfig", value)

    @property
    @jsii.member(jsii_name="elasticsearchVersion")
    def elasticsearch_version(self) -> typing.Optional[str]:
        """``AWS::Elasticsearch::Domain.ElasticsearchVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-elasticsearchversion
        Stability:
            stable
        """
        return jsii.get(self, "elasticsearchVersion")

    @elasticsearch_version.setter
    def elasticsearch_version(self, value: typing.Optional[str]):
        return jsii.set(self, "elasticsearchVersion", value)

    @property
    @jsii.member(jsii_name="encryptionAtRestOptions")
    def encryption_at_rest_options(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["EncryptionAtRestOptionsProperty"]]]:
        """``AWS::Elasticsearch::Domain.EncryptionAtRestOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-encryptionatrestoptions
        Stability:
            stable
        """
        return jsii.get(self, "encryptionAtRestOptions")

    @encryption_at_rest_options.setter
    def encryption_at_rest_options(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["EncryptionAtRestOptionsProperty"]]]):
        return jsii.set(self, "encryptionAtRestOptions", value)

    @property
    @jsii.member(jsii_name="nodeToNodeEncryptionOptions")
    def node_to_node_encryption_options(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["NodeToNodeEncryptionOptionsProperty"]]]:
        """``AWS::Elasticsearch::Domain.NodeToNodeEncryptionOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-nodetonodeencryptionoptions
        Stability:
            stable
        """
        return jsii.get(self, "nodeToNodeEncryptionOptions")

    @node_to_node_encryption_options.setter
    def node_to_node_encryption_options(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["NodeToNodeEncryptionOptionsProperty"]]]):
        return jsii.set(self, "nodeToNodeEncryptionOptions", value)

    @property
    @jsii.member(jsii_name="snapshotOptions")
    def snapshot_options(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SnapshotOptionsProperty"]]]:
        """``AWS::Elasticsearch::Domain.SnapshotOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-snapshotoptions
        Stability:
            stable
        """
        return jsii.get(self, "snapshotOptions")

    @snapshot_options.setter
    def snapshot_options(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SnapshotOptionsProperty"]]]):
        return jsii.set(self, "snapshotOptions", value)

    @property
    @jsii.member(jsii_name="vpcOptions")
    def vpc_options(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["VPCOptionsProperty"]]]:
        """``AWS::Elasticsearch::Domain.VPCOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-vpcoptions
        Stability:
            stable
        """
        return jsii.get(self, "vpcOptions")

    @vpc_options.setter
    def vpc_options(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["VPCOptionsProperty"]]]):
        return jsii.set(self, "vpcOptions", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticsearch.CfnDomain.EBSOptionsProperty", jsii_struct_bases=[])
    class EBSOptionsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-ebsoptions.html
        Stability:
            stable
        """
        ebsEnabled: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnDomain.EBSOptionsProperty.EBSEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-ebsoptions.html#cfn-elasticsearch-domain-ebsoptions-ebsenabled
        Stability:
            stable
        """

        iops: jsii.Number
        """``CfnDomain.EBSOptionsProperty.Iops``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-ebsoptions.html#cfn-elasticsearch-domain-ebsoptions-iops
        Stability:
            stable
        """

        volumeSize: jsii.Number
        """``CfnDomain.EBSOptionsProperty.VolumeSize``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-ebsoptions.html#cfn-elasticsearch-domain-ebsoptions-volumesize
        Stability:
            stable
        """

        volumeType: str
        """``CfnDomain.EBSOptionsProperty.VolumeType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-ebsoptions.html#cfn-elasticsearch-domain-ebsoptions-volumetype
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticsearch.CfnDomain.ElasticsearchClusterConfigProperty", jsii_struct_bases=[])
    class ElasticsearchClusterConfigProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-elasticsearchclusterconfig.html
        Stability:
            stable
        """
        dedicatedMasterCount: jsii.Number
        """``CfnDomain.ElasticsearchClusterConfigProperty.DedicatedMasterCount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-elasticsearchclusterconfig.html#cfn-elasticsearch-domain-elasticseachclusterconfig-dedicatedmastercount
        Stability:
            stable
        """

        dedicatedMasterEnabled: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnDomain.ElasticsearchClusterConfigProperty.DedicatedMasterEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-elasticsearchclusterconfig.html#cfn-elasticsearch-domain-elasticseachclusterconfig-dedicatedmasterenabled
        Stability:
            stable
        """

        dedicatedMasterType: str
        """``CfnDomain.ElasticsearchClusterConfigProperty.DedicatedMasterType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-elasticsearchclusterconfig.html#cfn-elasticsearch-domain-elasticseachclusterconfig-dedicatedmastertype
        Stability:
            stable
        """

        instanceCount: jsii.Number
        """``CfnDomain.ElasticsearchClusterConfigProperty.InstanceCount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-elasticsearchclusterconfig.html#cfn-elasticsearch-domain-elasticseachclusterconfig-instancecount
        Stability:
            stable
        """

        instanceType: str
        """``CfnDomain.ElasticsearchClusterConfigProperty.InstanceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-elasticsearchclusterconfig.html#cfn-elasticsearch-domain-elasticseachclusterconfig-instnacetype
        Stability:
            stable
        """

        zoneAwarenessEnabled: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnDomain.ElasticsearchClusterConfigProperty.ZoneAwarenessEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-elasticsearchclusterconfig.html#cfn-elasticsearch-domain-elasticseachclusterconfig-zoneawarenessenabled
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticsearch.CfnDomain.EncryptionAtRestOptionsProperty", jsii_struct_bases=[])
    class EncryptionAtRestOptionsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-encryptionatrestoptions.html
        Stability:
            stable
        """
        enabled: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnDomain.EncryptionAtRestOptionsProperty.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-encryptionatrestoptions.html#cfn-elasticsearch-domain-encryptionatrestoptions-enabled
        Stability:
            stable
        """

        kmsKeyId: str
        """``CfnDomain.EncryptionAtRestOptionsProperty.KmsKeyId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-encryptionatrestoptions.html#cfn-elasticsearch-domain-encryptionatrestoptions-kmskeyid
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticsearch.CfnDomain.NodeToNodeEncryptionOptionsProperty", jsii_struct_bases=[])
    class NodeToNodeEncryptionOptionsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-nodetonodeencryptionoptions.html
        Stability:
            stable
        """
        enabled: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnDomain.NodeToNodeEncryptionOptionsProperty.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-nodetonodeencryptionoptions.html#cfn-elasticsearch-domain-nodetonodeencryptionoptions-enabled
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticsearch.CfnDomain.SnapshotOptionsProperty", jsii_struct_bases=[])
    class SnapshotOptionsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-snapshotoptions.html
        Stability:
            stable
        """
        automatedSnapshotStartHour: jsii.Number
        """``CfnDomain.SnapshotOptionsProperty.AutomatedSnapshotStartHour``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-snapshotoptions.html#cfn-elasticsearch-domain-snapshotoptions-automatedsnapshotstarthour
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticsearch.CfnDomain.VPCOptionsProperty", jsii_struct_bases=[])
    class VPCOptionsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-vpcoptions.html
        Stability:
            stable
        """
        securityGroupIds: typing.List[str]
        """``CfnDomain.VPCOptionsProperty.SecurityGroupIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-vpcoptions.html#cfn-elasticsearch-domain-vpcoptions-securitygroupids
        Stability:
            stable
        """

        subnetIds: typing.List[str]
        """``CfnDomain.VPCOptionsProperty.SubnetIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-vpcoptions.html#cfn-elasticsearch-domain-vpcoptions-subnetids
        Stability:
            stable
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-elasticsearch.CfnDomainProps", jsii_struct_bases=[])
class CfnDomainProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::Elasticsearch::Domain``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html
    Stability:
        stable
    """
    accessPolicies: typing.Any
    """``AWS::Elasticsearch::Domain.AccessPolicies``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-accesspolicies
    Stability:
        stable
    """

    advancedOptions: typing.Union[aws_cdk.core.IResolvable, typing.Mapping[str,str]]
    """``AWS::Elasticsearch::Domain.AdvancedOptions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-advancedoptions
    Stability:
        stable
    """

    domainName: str
    """``AWS::Elasticsearch::Domain.DomainName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-domainname
    Stability:
        stable
    """

    ebsOptions: typing.Union[aws_cdk.core.IResolvable, "CfnDomain.EBSOptionsProperty"]
    """``AWS::Elasticsearch::Domain.EBSOptions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-ebsoptions
    Stability:
        stable
    """

    elasticsearchClusterConfig: typing.Union[aws_cdk.core.IResolvable, "CfnDomain.ElasticsearchClusterConfigProperty"]
    """``AWS::Elasticsearch::Domain.ElasticsearchClusterConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-elasticsearchclusterconfig
    Stability:
        stable
    """

    elasticsearchVersion: str
    """``AWS::Elasticsearch::Domain.ElasticsearchVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-elasticsearchversion
    Stability:
        stable
    """

    encryptionAtRestOptions: typing.Union[aws_cdk.core.IResolvable, "CfnDomain.EncryptionAtRestOptionsProperty"]
    """``AWS::Elasticsearch::Domain.EncryptionAtRestOptions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-encryptionatrestoptions
    Stability:
        stable
    """

    nodeToNodeEncryptionOptions: typing.Union[aws_cdk.core.IResolvable, "CfnDomain.NodeToNodeEncryptionOptionsProperty"]
    """``AWS::Elasticsearch::Domain.NodeToNodeEncryptionOptions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-nodetonodeencryptionoptions
    Stability:
        stable
    """

    snapshotOptions: typing.Union[aws_cdk.core.IResolvable, "CfnDomain.SnapshotOptionsProperty"]
    """``AWS::Elasticsearch::Domain.SnapshotOptions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-snapshotoptions
    Stability:
        stable
    """

    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::Elasticsearch::Domain.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-tags
    Stability:
        stable
    """

    vpcOptions: typing.Union[aws_cdk.core.IResolvable, "CfnDomain.VPCOptionsProperty"]
    """``AWS::Elasticsearch::Domain.VPCOptions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-vpcoptions
    Stability:
        stable
    """

__all__ = ["CfnDomain", "CfnDomainProps", "__jsii_assembly__"]

publication.publish()
