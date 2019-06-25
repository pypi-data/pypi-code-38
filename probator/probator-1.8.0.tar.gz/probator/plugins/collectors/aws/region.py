from botocore.exceptions import ClientError
from munch import munchify
from probator.config import dbconfig
from probator.constants import NewResource, ConfigOption
from probator.plugins.collectors.aws import AWSBaseRegionCollector
from probator.plugins.types.resources import (
    AMI, BeanStalk, EBSSnapshot, EBSVolume, EC2Instance, ELB, ENI, LoadBalancer, VPC, RDSInstance, EKSCluster
)
from probator.utils import to_utc_date, get_resource_id
from probator.wrappers import retry, rollback


class AWSEC2InstanceCollector(AWSBaseRegionCollector):
    name = 'AWS EC2 Instance Collector'

    @rollback
    @retry
    def run(self):
        """Update list of EC2 Instances for the account / region

        Returns:
            `None`
        """
        self.log.debug(f'Updating EC2Instances for {self.account.account_name}/{self.region}')
        ec2 = self.session.resource('ec2', region_name=self.region)

        try:
            existing_instances = EC2Instance.get_all(self.account, self.region)
            api_instances = {x.id: x for x in ec2.instances.all()}
            new_resources = {}

            if api_instances:
                for instance_id, instance_data in api_instances.items():
                    if instance_data.state['Name'] == 'terminated':
                        continue

                    tags = {tag['Key']: tag['Value'] for tag in instance_data.tags or {}}
                    properties = {
                        'launch_date': to_utc_date(instance_data.launch_time).isoformat(),
                        'state': instance_data.state['Name'],
                        'instance_type': instance_data.instance_type,
                        'public_ip': getattr(instance_data, 'public_ip_address', None),
                        'public_dns': getattr(instance_data, 'public_dns_address', None),
                        'private_ip': instance_data.private_ip_address,
                        'private_dns': getattr(instance_data, 'private_dns_name', None),
                        'ami_id': instance_data.image_id,
                        'platform': instance_data.platform or 'linux'
                    }

                    new_resources[instance_id] = NewResource(
                        resource_id=instance_id,
                        properties=properties,
                        tags=tags
                    )

            self.process_resources(
                resource_class=EC2Instance,
                account_id=self.account.account_id,
                location=self.region,
                new_resources=new_resources,
                existing_resources=existing_instances
            )

        finally:
            del ec2


class AWSEBSVolumeCollector(AWSBaseRegionCollector):
    name = 'AWS EBS Volume Collector'

    @rollback
    @retry
    def run(self):
        """Update list of EBS Volumes for the account / region

        Returns:
            `None`
        """
        self.log.debug(f'Updating EBSVolumes for {self.account.account_name}/{self.region}')
        ec2 = self.session.resource('ec2', region_name=self.region)

        try:
            existing_volumes = EBSVolume.get_all(self.account, self.region)
            volumes = {x.id: x for x in ec2.volumes.all()}
            new_resources = {}

            if volumes:
                for data in volumes.values():
                    properties = {
                        'create_time': data.create_time,
                        'encrypted': data.encrypted,
                        'iops': data.iops or 0,
                        'kms_key_id': data.kms_key_id,
                        'size': data.size,
                        'state': data.state,
                        'snapshot_id': data.snapshot_id,
                        'volume_type': data.volume_type,
                        'attachments': sorted(x['InstanceId'] for x in data.attachments)
                    }
                    tags = {t['Key']: t['Value'] for t in data.tags or {}}

                    new_resources[data.id] = NewResource(
                        resource_id=data.id,
                        properties=properties,
                        tags=tags
                    )

            self.process_resources(
                resource_class=EBSVolume,
                account_id=self.account.account_id,
                location=self.region,
                new_resources=new_resources,
                existing_resources=existing_volumes
            )

        finally:
            del ec2


class AWSEBSSnapshotCollector(AWSBaseRegionCollector):
    name = 'AWS EBS Snapshot Collector'

    @rollback
    @retry
    def run(self):
        """Update list of EBS Snapshots for the account / region

        Returns:
            `None`
        """
        self.log.debug(f'Updating EBSSnapshots for {self.account.account_name}/{self.region}')
        ec2 = self.session.resource('ec2', region_name=self.region)

        try:
            existing_snapshots = EBSSnapshot.get_all(self.account, self.region)
            snapshots = {x.id: x for x in ec2.snapshots.filter(OwnerIds=[self.account.account_number])}
            new_resources = {}

            if snapshots:
                for data in snapshots.values():
                    properties = {
                        'create_time': data.start_time,
                        'encrypted': data.encrypted,
                        'kms_key_id': data.kms_key_id,
                        'state': data.state,
                        'state_message': data.state_message,
                        'volume_id': data.volume_id,
                        'volume_size': data.volume_size,
                    }
                    tags = {t['Key']: t['Value'] for t in data.tags or {}}

                    new_resources[data.id] = NewResource(
                        resource_id=data.id,
                        properties=properties,
                        tags=tags
                    )

            self.process_resources(
                resource_class=EBSSnapshot,
                account_id=self.account.account_id,
                location=self.region,
                new_resources=new_resources,
                existing_resources=existing_snapshots
            )

        finally:
            del ec2


class AWSAMICollector(AWSBaseRegionCollector):
    name = 'AWS AMI Collector'

    @rollback
    @retry
    def run(self):
        """Update list of AMIs for the account / region

        Returns:
            `None`
        """
        self.log.debug(f'Updating AMIs for {self.account.account_name}/{self.region}')
        ec2 = self.session.resource('ec2', region_name=self.region)

        try:
            existing_images = AMI.get_all(self.account, self.region)
            images = {x.id: x for x in ec2.images.filter(Owners=['self'])}
            new_resources = {}

            if images:
                for data in images.values():
                    properties = {
                        'architecture': data.architecture,
                        'description': data.description,
                        'name': data.name,
                        'platform': data.platform or 'Linux',
                        'state': data.state,
                    }
                    tags = {tag['Key']: tag['Value'] for tag in data.tags or {}}

                    new_resources[data.id] = NewResource(
                        resource_id=data.id,
                        properties=properties,
                        tags=tags
                    )

            self.process_resources(
                resource_class=AMI,
                account_id=self.account.account_id,
                location=self.region,
                new_resources=new_resources,
                existing_resources=existing_images
            )

        finally:
            del ec2


class AWSBeanStalkCollector(AWSBaseRegionCollector):
    name = 'AWS BeanStalk Collector'

    def run(self):
        self.update_beanstalks()

    @rollback
    def update_beanstalks(self):
        """Update list of Elastic BeanStalks for the account / region

        Returns:
            `None`
        """
        self.log.debug(f'Updating ElasticBeanStalk environments for {self.account.account_name}/{self.region}')

        beanstalks = self._get_beanstalks()
        existing_beanstalks = BeanStalk.get_all(self.account, self.region)
        new_resources = {}

        if beanstalks:
            for beanstalk_id, data in beanstalks.items():
                new_resources[beanstalk_id] = NewResource(
                    resource_id=beanstalk_id,
                    properties=data['properties'],
                    tags=data['tags']
                )

        self.process_resources(
            resource_class=BeanStalk,
            account_id=self.account.account_id,
            location=self.region,
            new_resources=new_resources,
            existing_resources=existing_beanstalks
        )

    @retry
    def _get_beanstalks(self):
        ebclient = self.session.client('elasticbeanstalk', region_name=self.region)

        try:
            beanstalks = {}
            for env in ebclient.describe_environments(IncludeDeleted=False)['Environments']:
                # Only get information for HTTP (non-worker) Beanstalks
                if env['Tier']['Type'] == 'Standard':
                    if 'CNAME' in env:
                        tags = {
                            tag['Key']: tag['Value'] for tag in ebclient.list_tags_for_resource(
                                ResourceArn=env['environment_arn']
                            ).get('ResourceTags')
                        }
                        beanstalks[env['EnvironmentId']] = {
                            'environment_arn': env['EnvironmentArn'],
                            'properties': {
                                'environment_name': env['EnvironmentName'],
                                'application_name': env['ApplicationName'],
                                'cname': env['CNAME']
                            },
                            'tags': tags
                        }

            return beanstalks
        finally:
            del ebclient


class AWSVPCCollector(AWSBaseRegionCollector):
    name = 'AWS VPC Collector'

    @rollback
    def run(self):
        """Update list of VPCs for the account / region

        Returns:
            `None`
        """
        self.log.debug(f'Updating VPCs for {self.account.account_name}/{self.region}')

        existing_vpcs = VPC.get_all(self.account, self.region)
        api_vpcs = self._get_vpcs()
        new_resources = {}

        if api_vpcs:
            for resource_id, data in api_vpcs.items():
                new_resources[resource_id] = NewResource(
                    resource_id=resource_id,
                    properties=data['properties'],
                    tags=data['tags']
                )

        self.process_resources(
            resource_class=VPC,
            account_id=self.account.account_id,
            location=self.region,
            new_resources=new_resources,
            existing_resources=existing_vpcs
        )

    def _get_vpcs(self):
        ec2 = self.session.resource('ec2', region_name=self.region)
        ec2_client = self.session.client('ec2', region_name=self.region)
        vpcs = {}

        try:
            api_vpcs = {x.id: x for x in ec2.vpcs.all()}

            for data in api_vpcs.values():
                flow_logs = ec2_client.describe_flow_logs(
                    Filters=[
                        {
                            'Name': 'resource-id',
                            'Values': [data.vpc_id]
                        }
                    ]
                ).get('FlowLogs', None)

                if flow_logs and len(flow_logs) > 0:
                    log_status = flow_logs[0].get('FlowLogStatus', 'INACTIVE')
                    log_group = flow_logs[0].get('LogGroupName', None)

                else:
                    log_status = 'INACTIVE'
                    log_group = None

                vpcs[data.vpc_id] = {
                    'properties': {
                        'cidr_v4': data.cidr_block,
                        'is_default': data.is_default,
                        'state': data.state,
                        'vpc_flow_logs_status': log_status,
                        'vpc_flow_logs_group': log_group
                    },
                    'tags': {t['Key']: t['Value'] for t in data.tags or {}}
                }

            return vpcs
        finally:
            del ec2
            del ec2_client


class AWSClassicLoadBalancerCollector(AWSBaseRegionCollector):
    name = 'AWS Classic Load Balancer Collector'

    @rollback
    def run(self):
        """Update list of ELBs for the account / region

        Returns:
            `None`
        """
        self.log.debug(f'Updating ELBs for {self.account.account_name}/{self.region}')

        api_elbs = self._get_load_balancers()
        existing_elbs = ELB.get_all(self.account, self.region)
        new_resources = {}

        if api_elbs:
            for elb_identifier, data in api_elbs.items():
                tags = {tag['Key']: tag['Value'] for tag in data.get('Tags', {})}
                properties = {
                    'name': data['LoadBalancerName'],
                    'dns_name': data['DNSName'],
                    'instances': sorted(instance['InstanceId'] for instance in data['Instances']),
                    'vpc_id': data.get('VPCId', 'no vpc'),
                    'state': 'not_reported',
                    'canonical_hosted_zone_name': data.get('CanonicalHostedZoneName', None)
                }

                new_resources[elb_identifier] = NewResource(
                    resource_id=elb_identifier,
                    properties=properties,
                    tags=tags
                )

        self.process_resources(
            resource_class=ELB,
            account_id=self.account.account_id,
            location=self.region,
            new_resources=new_resources,
            existing_resources=existing_elbs
        )

    @retry
    def _get_load_balancers(self):
        load_balancers = {}
        elb = self.session.client('elb', region_name=self.region)

        try:
            done = False
            marker = None
            while not done:
                if marker:
                    response = elb.describe_load_balancers(Marker=marker)
                else:
                    response = elb.describe_load_balancers()

                if 'NextMarker' in response:
                    marker = response['NextMarker']
                else:
                    done = True

                for lb in response.get('LoadBalancerDescriptions', []):
                    elb_id = f'elb-{self.account.account_name}:{self.region}:{lb["LoadBalancerName"]}'
                    load_balancers[elb_id] = lb

            return load_balancers
        finally:
            del elb


class AWSLoadBalancerCollector(AWSBaseRegionCollector):
    name = 'AWS Load Balancer Collector'

    def run(self):
        """Update list of Load Balancers

        Returns:
            `None`
        """
        self.log.debug(f'Updating Load Balancers for {self.account.account_name}/{self.region}')

        existing_lbs = LoadBalancer.get_all(self.account, self.region)
        api_lbs = self._get_loadbalancers()
        new_resources = {}

        if api_lbs:
            for lb_identifier, data in api_lbs.items():
                resource_id = get_resource_id('awslb', self.account.account_name, self.region, data.LoadBalancerName)
                tags = {tag['Key']: tag['Value'] for tag in data.get('Tags', {})}
                properties = {
                    'arn': data.LoadBalancerArn,
                    'name': data.LoadBalancerName,
                    'dns_name': data.DNSName,
                    'vpc_id': data.get('VpcId'),
                    'state': data.State['Code'],
                    'scheme': data.Scheme,
                    'type': data.Type,
                }

                new_resources[resource_id] = NewResource(
                    resource_id=resource_id,
                    properties=properties,
                    tags=tags,
                )

        self.process_resources(
            resource_class=LoadBalancer,
            account_id=self.account.account_id,
            location=self.region,
            new_resources=new_resources,
            existing_resources=existing_lbs
        )

    @rollback
    @retry
    def _get_loadbalancers(self):
        """Get load balancers from AWS

        Returns:
            `dict` - Returns a dict of resource objects
        """
        elb = self.session.client('elbv2', region_name=self.region)

        try:
            lbs = {}
            done = False
            marker = None
            while not done:
                if marker:
                    response = elb.describe_load_balancers(Marker=marker)
                else:
                    response = elb.describe_load_balancers()

                if 'NextMarker' in response:
                    marker = response['NextMarker']
                else:
                    done = True

                for lb in response.get('LoadBalancers', []):
                    elb_id = get_resource_id('awslb', self.account.account_name, self.region, lb['LoadBalancerName'])
                    lbs[elb_id] = munchify(lb)

            return lbs
        finally:
            del elb
        # endregion


class AWSENICollector(AWSBaseRegionCollector):
    name = 'AWS ENI Collector'

    @rollback
    @retry
    def run(self):
        self.log.debug(f'Updating ENIs for {self.account.account_name}/{self.region}')

        ec2 = self.session.resource('ec2', region_name=self.region)
        existing_enis = ENI.get_all(self.account, self.region)
        new_resources = {}

        try:
            enis = {x.id: x for x in ec2.network_interfaces.all()}
            if enis:
                for iface in enis.values():
                    instance_id = None
                    if iface.attachment:
                        instance_id = iface.attachment.get('InstanceId', None)

                    public_ip = None
                    if iface.association_attribute:
                        public_ip = iface.association_attribute.get('PublicIp', None)

                    secondary_ips = [ip['PrivateIpAddress'] for ip in iface.private_ip_addresses if not ip['Primary']]

                    tags = {tag['Key']: tag['Value'] for tag in iface.tag_set or {}}
                    properties = {
                        'vpc_id': iface.vpc_id,
                        'instance_id': instance_id,
                        'status': iface.status,
                        'primary_ip': iface.private_ip_address,
                        'secondary_ips': secondary_ips,
                        'public_ip': public_ip,
                        'attachment_owner': iface.attachment.get('InstanceOwnerId') if iface.attachment else None,
                        'description': iface.description,
                    }

                    new_resources[iface.id] = NewResource(
                        resource_id=iface.id,
                        properties=properties,
                        tags=tags
                    )

            self.process_resources(
                resource_class=ENI,
                account_id=self.account.account_id,
                location=self.region,
                new_resources=new_resources,
                existing_resources=existing_enis
            )
        finally:
            del ec2


class AWSRDSCollector(AWSBaseRegionCollector):
    name = 'AWS RDS Collector'

    @rollback
    @retry
    def run(self):
        self.log.debug(f'Updating RDS Instances for {self.account.account_name}/{self.region}')

        rds = self.session.client('rds', region_name=self.region)
        existing_instances = RDSInstance.get_all(account=self.account, location=self.region)
        api_instances = self._get_instances()
        new_resources = {}

        try:
            if api_instances:
                for arn, data in api_instances.items():
                    tags = self._get_resource_tags(data.DBInstanceArn)
                    properties = {
                        'instance_identifier': data.DBInstanceIdentifier,
                        'instance_class': data.DBInstanceClass,
                        'status': data.DBInstanceStatus,
                        'dbname': data.get('DBName', None),
                        'allocated_storage': data.AllocatedStorage,
                        'multi_az': data.MultiAZ,
                        'engine': data.Engine,
                        'engine_version': data.EngineVersion,
                        'encrypted': data.StorageEncrypted,
                    }

                    new_resources[data.DBInstanceArn] = NewResource(
                        resource_id=data.DBInstanceArn,
                        properties=properties,
                        tags=tags
                    )

            self.process_resources(
                resource_class=RDSInstance,
                account_id=self.account.account_id,
                location=self.region,
                new_resources=new_resources,
                existing_resources=existing_instances
            )
        finally:
            del rds

    @retry
    def _get_instances(self):
        instances = {}
        rds = self.session.client('rds', region_name=self.region)
        try:
            done = False
            marker = None

            while not done:
                if marker:
                    response = rds.describe_db_instances(Marker=marker)
                else:
                    response = rds.describe_db_instances()

                if 'Marker' in response:
                    marker = response['Marker']
                else:
                    done = True

                for instance in response.get('DBInstances', []):
                    instances[instance['DBInstanceArn']] = munchify(instance)

            return instances

        finally:
            del rds

    @retry
    def _get_resource_tags(self, instance_arn):
        """Return a list of tags for a given RDS Instance

        Args:
            instance_arn:

        Returns:

        """
        rds = self.session.client('rds', region_name=self.region)

        try:
            response = rds.list_tags_for_resource(ResourceName=instance_arn)
            return {tag['Key']: tag['Value'] for tag in response.get('TagList', [])}

        except ClientError as ex:
            rex = ex.response['Error']['Code']
            if rex == 'InvalidParameterValue':
                return {}


class AWSEKSCollector(AWSBaseRegionCollector):
    options = (
        ConfigOption(
            name='eks_regions',
            default_value=[
                'us-east-1', 'us-east-2', 'us-west-2',
                'eu-west-1', 'eu-central-1', 'eu-west-2', 'eu-west-3', 'eu-north-1',
                'ap-southeast-1', 'ap-southeast-2',
                'ap-northeast-1', 'ap-northeast-2',
                'ap-south-1'
            ],
            type='array',
            description='List of supported regions for EKS'
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.supported_regions = dbconfig.get(key='eks_regions', namespace=self.ns)

    @rollback
    @retry
    def run(self):
        if self.region not in self.supported_regions:
            self.log.debug('Skipping EKS collections for unsupported regions')
            return

        self.log.debug(f'Updating EKS Clusters for {self.account.account_name}/{self.region}')

        existing_clusters = EKSCluster.get_all(account=self.account, location=self.region)
        api_clusters = self._list_clusters()
        new_resources = {}

        if api_clusters:
            for cluster_name, data in api_clusters.items():
                resource_id = get_resource_id('eks', data.get('arn'))
                vpc_config = data.get('resourcesVpcConfig', {})
                properties = {
                    'name': data.get('name'),
                    'arn': data.get('arn'),
                    'vpc_id': vpc_config.get('vpcId'),
                    'subnets': vpc_config.get('subnetIds', []),
                    'status': data.get('status'),
                    'version': data.get('version'),
                    'platform_version': data.get('platformVersion')
                }

                new_resources[resource_id] = NewResource(
                    resource_id=resource_id,
                    properties=properties
                )

        self.process_resources(
            resource_class=EKSCluster,
            account_id=self.account.account_id,
            location=self.region,
            new_resources=new_resources,
            existing_resources=existing_clusters
        )

    def _list_clusters(self):
        eks = self.session.client('eks', region_name=self.region)
        try:
            done = False
            marker = None
            clusters = {}

            while not done:
                if marker:
                    response = eks.list_clusters(nextToken=marker)
                else:
                    response = eks.list_clusters()

                if 'nextToken' in response:
                    marker = response['nextToken']
                else:
                    done = True

                for cluster_name in response.get('clusters', []):
                    cluster_info = eks.describe_cluster(name=cluster_name).get('cluster', None)
                    if cluster_info:
                        resource_id = get_resource_id('eks', cluster_info.get('arn'))
                        clusters[resource_id] = cluster_info
            return clusters
        finally:
            del eks
