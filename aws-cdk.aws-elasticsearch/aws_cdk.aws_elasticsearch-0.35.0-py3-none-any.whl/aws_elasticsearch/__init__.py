import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-elasticsearch", "0.35.0", __name__, "aws-elasticsearch@0.35.0.jsii.tgz")
class CfnDomain(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-elasticsearch.CfnDomain"):
    """A CloudFormation ``AWS::Elasticsearch::Domain``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Elasticsearch::Domain
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, access_policies: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, advanced_options: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.Mapping[str,str]]]]=None, domain_name: typing.Optional[str]=None, ebs_options: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["EBSOptionsProperty"]]]=None, elasticsearch_cluster_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["ElasticsearchClusterConfigProperty"]]]=None, elasticsearch_version: typing.Optional[str]=None, encryption_at_rest_options: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["EncryptionAtRestOptionsProperty"]]]=None, node_to_node_encryption_options: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["NodeToNodeEncryptionOptionsProperty"]]]=None, snapshot_options: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["SnapshotOptionsProperty"]]]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, vpc_options: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["VPCOptionsProperty"]]]=None) -> None:
        """Create a new ``AWS::Elasticsearch::Domain``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            accessPolicies: ``AWS::Elasticsearch::Domain.AccessPolicies``.
            advancedOptions: ``AWS::Elasticsearch::Domain.AdvancedOptions``.
            domainName: ``AWS::Elasticsearch::Domain.DomainName``.
            ebsOptions: ``AWS::Elasticsearch::Domain.EBSOptions``.
            elasticsearchClusterConfig: ``AWS::Elasticsearch::Domain.ElasticsearchClusterConfig``.
            elasticsearchVersion: ``AWS::Elasticsearch::Domain.ElasticsearchVersion``.
            encryptionAtRestOptions: ``AWS::Elasticsearch::Domain.EncryptionAtRestOptions``.
            nodeToNodeEncryptionOptions: ``AWS::Elasticsearch::Domain.NodeToNodeEncryptionOptions``.
            snapshotOptions: ``AWS::Elasticsearch::Domain.SnapshotOptions``.
            tags: ``AWS::Elasticsearch::Domain.Tags``.
            vpcOptions: ``AWS::Elasticsearch::Domain.VPCOptions``.

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
    @jsii.member(jsii_name="attrDomainEndpoint")
    def attr_domain_endpoint(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            DomainEndpoint
        """
        return jsii.get(self, "attrDomainEndpoint")

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
        """``AWS::Elasticsearch::Domain.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="accessPolicies")
    def access_policies(self) -> typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::Elasticsearch::Domain.AccessPolicies``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-accesspolicies
        Stability:
            experimental
        """
        return jsii.get(self, "accessPolicies")

    @access_policies.setter
    def access_policies(self, value: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "accessPolicies", value)

    @property
    @jsii.member(jsii_name="advancedOptions")
    def advanced_options(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.Mapping[str,str]]]]:
        """``AWS::Elasticsearch::Domain.AdvancedOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-advancedoptions
        Stability:
            experimental
        """
        return jsii.get(self, "advancedOptions")

    @advanced_options.setter
    def advanced_options(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.Mapping[str,str]]]]):
        return jsii.set(self, "advancedOptions", value)

    @property
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> typing.Optional[str]:
        """``AWS::Elasticsearch::Domain.DomainName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-domainname
        Stability:
            experimental
        """
        return jsii.get(self, "domainName")

    @domain_name.setter
    def domain_name(self, value: typing.Optional[str]):
        return jsii.set(self, "domainName", value)

    @property
    @jsii.member(jsii_name="ebsOptions")
    def ebs_options(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["EBSOptionsProperty"]]]:
        """``AWS::Elasticsearch::Domain.EBSOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-ebsoptions
        Stability:
            experimental
        """
        return jsii.get(self, "ebsOptions")

    @ebs_options.setter
    def ebs_options(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["EBSOptionsProperty"]]]):
        return jsii.set(self, "ebsOptions", value)

    @property
    @jsii.member(jsii_name="elasticsearchClusterConfig")
    def elasticsearch_cluster_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["ElasticsearchClusterConfigProperty"]]]:
        """``AWS::Elasticsearch::Domain.ElasticsearchClusterConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-elasticsearchclusterconfig
        Stability:
            experimental
        """
        return jsii.get(self, "elasticsearchClusterConfig")

    @elasticsearch_cluster_config.setter
    def elasticsearch_cluster_config(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["ElasticsearchClusterConfigProperty"]]]):
        return jsii.set(self, "elasticsearchClusterConfig", value)

    @property
    @jsii.member(jsii_name="elasticsearchVersion")
    def elasticsearch_version(self) -> typing.Optional[str]:
        """``AWS::Elasticsearch::Domain.ElasticsearchVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-elasticsearchversion
        Stability:
            experimental
        """
        return jsii.get(self, "elasticsearchVersion")

    @elasticsearch_version.setter
    def elasticsearch_version(self, value: typing.Optional[str]):
        return jsii.set(self, "elasticsearchVersion", value)

    @property
    @jsii.member(jsii_name="encryptionAtRestOptions")
    def encryption_at_rest_options(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["EncryptionAtRestOptionsProperty"]]]:
        """``AWS::Elasticsearch::Domain.EncryptionAtRestOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-encryptionatrestoptions
        Stability:
            experimental
        """
        return jsii.get(self, "encryptionAtRestOptions")

    @encryption_at_rest_options.setter
    def encryption_at_rest_options(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["EncryptionAtRestOptionsProperty"]]]):
        return jsii.set(self, "encryptionAtRestOptions", value)

    @property
    @jsii.member(jsii_name="nodeToNodeEncryptionOptions")
    def node_to_node_encryption_options(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["NodeToNodeEncryptionOptionsProperty"]]]:
        """``AWS::Elasticsearch::Domain.NodeToNodeEncryptionOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-nodetonodeencryptionoptions
        Stability:
            experimental
        """
        return jsii.get(self, "nodeToNodeEncryptionOptions")

    @node_to_node_encryption_options.setter
    def node_to_node_encryption_options(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["NodeToNodeEncryptionOptionsProperty"]]]):
        return jsii.set(self, "nodeToNodeEncryptionOptions", value)

    @property
    @jsii.member(jsii_name="snapshotOptions")
    def snapshot_options(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["SnapshotOptionsProperty"]]]:
        """``AWS::Elasticsearch::Domain.SnapshotOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-snapshotoptions
        Stability:
            experimental
        """
        return jsii.get(self, "snapshotOptions")

    @snapshot_options.setter
    def snapshot_options(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["SnapshotOptionsProperty"]]]):
        return jsii.set(self, "snapshotOptions", value)

    @property
    @jsii.member(jsii_name="vpcOptions")
    def vpc_options(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["VPCOptionsProperty"]]]:
        """``AWS::Elasticsearch::Domain.VPCOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-vpcoptions
        Stability:
            experimental
        """
        return jsii.get(self, "vpcOptions")

    @vpc_options.setter
    def vpc_options(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["VPCOptionsProperty"]]]):
        return jsii.set(self, "vpcOptions", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticsearch.CfnDomain.EBSOptionsProperty", jsii_struct_bases=[])
    class EBSOptionsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-ebsoptions.html
        Stability:
            experimental
        """
        ebsEnabled: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnDomain.EBSOptionsProperty.EBSEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-ebsoptions.html#cfn-elasticsearch-domain-ebsoptions-ebsenabled
        Stability:
            experimental
        """

        iops: jsii.Number
        """``CfnDomain.EBSOptionsProperty.Iops``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-ebsoptions.html#cfn-elasticsearch-domain-ebsoptions-iops
        Stability:
            experimental
        """

        volumeSize: jsii.Number
        """``CfnDomain.EBSOptionsProperty.VolumeSize``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-ebsoptions.html#cfn-elasticsearch-domain-ebsoptions-volumesize
        Stability:
            experimental
        """

        volumeType: str
        """``CfnDomain.EBSOptionsProperty.VolumeType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-ebsoptions.html#cfn-elasticsearch-domain-ebsoptions-volumetype
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticsearch.CfnDomain.ElasticsearchClusterConfigProperty", jsii_struct_bases=[])
    class ElasticsearchClusterConfigProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-elasticsearchclusterconfig.html
        Stability:
            experimental
        """
        dedicatedMasterCount: jsii.Number
        """``CfnDomain.ElasticsearchClusterConfigProperty.DedicatedMasterCount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-elasticsearchclusterconfig.html#cfn-elasticsearch-domain-elasticseachclusterconfig-dedicatedmastercount
        Stability:
            experimental
        """

        dedicatedMasterEnabled: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnDomain.ElasticsearchClusterConfigProperty.DedicatedMasterEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-elasticsearchclusterconfig.html#cfn-elasticsearch-domain-elasticseachclusterconfig-dedicatedmasterenabled
        Stability:
            experimental
        """

        dedicatedMasterType: str
        """``CfnDomain.ElasticsearchClusterConfigProperty.DedicatedMasterType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-elasticsearchclusterconfig.html#cfn-elasticsearch-domain-elasticseachclusterconfig-dedicatedmastertype
        Stability:
            experimental
        """

        instanceCount: jsii.Number
        """``CfnDomain.ElasticsearchClusterConfigProperty.InstanceCount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-elasticsearchclusterconfig.html#cfn-elasticsearch-domain-elasticseachclusterconfig-instancecount
        Stability:
            experimental
        """

        instanceType: str
        """``CfnDomain.ElasticsearchClusterConfigProperty.InstanceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-elasticsearchclusterconfig.html#cfn-elasticsearch-domain-elasticseachclusterconfig-instnacetype
        Stability:
            experimental
        """

        zoneAwarenessEnabled: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnDomain.ElasticsearchClusterConfigProperty.ZoneAwarenessEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-elasticsearchclusterconfig.html#cfn-elasticsearch-domain-elasticseachclusterconfig-zoneawarenessenabled
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticsearch.CfnDomain.EncryptionAtRestOptionsProperty", jsii_struct_bases=[])
    class EncryptionAtRestOptionsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-encryptionatrestoptions.html
        Stability:
            experimental
        """
        enabled: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnDomain.EncryptionAtRestOptionsProperty.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-encryptionatrestoptions.html#cfn-elasticsearch-domain-encryptionatrestoptions-enabled
        Stability:
            experimental
        """

        kmsKeyId: str
        """``CfnDomain.EncryptionAtRestOptionsProperty.KmsKeyId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-encryptionatrestoptions.html#cfn-elasticsearch-domain-encryptionatrestoptions-kmskeyid
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticsearch.CfnDomain.NodeToNodeEncryptionOptionsProperty", jsii_struct_bases=[])
    class NodeToNodeEncryptionOptionsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-nodetonodeencryptionoptions.html
        Stability:
            experimental
        """
        enabled: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnDomain.NodeToNodeEncryptionOptionsProperty.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-nodetonodeencryptionoptions.html#cfn-elasticsearch-domain-nodetonodeencryptionoptions-enabled
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticsearch.CfnDomain.SnapshotOptionsProperty", jsii_struct_bases=[])
    class SnapshotOptionsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-snapshotoptions.html
        Stability:
            experimental
        """
        automatedSnapshotStartHour: jsii.Number
        """``CfnDomain.SnapshotOptionsProperty.AutomatedSnapshotStartHour``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-snapshotoptions.html#cfn-elasticsearch-domain-snapshotoptions-automatedsnapshotstarthour
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticsearch.CfnDomain.VPCOptionsProperty", jsii_struct_bases=[])
    class VPCOptionsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-vpcoptions.html
        Stability:
            experimental
        """
        securityGroupIds: typing.List[str]
        """``CfnDomain.VPCOptionsProperty.SecurityGroupIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-vpcoptions.html#cfn-elasticsearch-domain-vpcoptions-securitygroupids
        Stability:
            experimental
        """

        subnetIds: typing.List[str]
        """``CfnDomain.VPCOptionsProperty.SubnetIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticsearch-domain-vpcoptions.html#cfn-elasticsearch-domain-vpcoptions-subnetids
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-elasticsearch.CfnDomainProps", jsii_struct_bases=[])
class CfnDomainProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::Elasticsearch::Domain``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html
    Stability:
        experimental
    """
    accessPolicies: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.IResolvable]
    """``AWS::Elasticsearch::Domain.AccessPolicies``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-accesspolicies
    Stability:
        experimental
    """

    advancedOptions: typing.Union[aws_cdk.cdk.IResolvable, typing.Mapping[str,str]]
    """``AWS::Elasticsearch::Domain.AdvancedOptions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-advancedoptions
    Stability:
        experimental
    """

    domainName: str
    """``AWS::Elasticsearch::Domain.DomainName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-domainname
    Stability:
        experimental
    """

    ebsOptions: typing.Union[aws_cdk.cdk.IResolvable, "CfnDomain.EBSOptionsProperty"]
    """``AWS::Elasticsearch::Domain.EBSOptions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-ebsoptions
    Stability:
        experimental
    """

    elasticsearchClusterConfig: typing.Union[aws_cdk.cdk.IResolvable, "CfnDomain.ElasticsearchClusterConfigProperty"]
    """``AWS::Elasticsearch::Domain.ElasticsearchClusterConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-elasticsearchclusterconfig
    Stability:
        experimental
    """

    elasticsearchVersion: str
    """``AWS::Elasticsearch::Domain.ElasticsearchVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-elasticsearchversion
    Stability:
        experimental
    """

    encryptionAtRestOptions: typing.Union[aws_cdk.cdk.IResolvable, "CfnDomain.EncryptionAtRestOptionsProperty"]
    """``AWS::Elasticsearch::Domain.EncryptionAtRestOptions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-encryptionatrestoptions
    Stability:
        experimental
    """

    nodeToNodeEncryptionOptions: typing.Union[aws_cdk.cdk.IResolvable, "CfnDomain.NodeToNodeEncryptionOptionsProperty"]
    """``AWS::Elasticsearch::Domain.NodeToNodeEncryptionOptions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-nodetonodeencryptionoptions
    Stability:
        experimental
    """

    snapshotOptions: typing.Union[aws_cdk.cdk.IResolvable, "CfnDomain.SnapshotOptionsProperty"]
    """``AWS::Elasticsearch::Domain.SnapshotOptions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-snapshotoptions
    Stability:
        experimental
    """

    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::Elasticsearch::Domain.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-tags
    Stability:
        experimental
    """

    vpcOptions: typing.Union[aws_cdk.cdk.IResolvable, "CfnDomain.VPCOptionsProperty"]
    """``AWS::Elasticsearch::Domain.VPCOptions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-vpcoptions
    Stability:
        experimental
    """

__all__ = ["CfnDomain", "CfnDomainProps", "__jsii_assembly__"]

publication.publish()
