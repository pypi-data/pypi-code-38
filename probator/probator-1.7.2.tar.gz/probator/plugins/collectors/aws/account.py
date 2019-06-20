import time
from copy import deepcopy
from dataclasses import field, dataclass

from botocore.exceptions import ClientError
from munch import munchify
from probator.constants import NewResource
from probator.plugins.collectors.aws import AWSBaseAccountCollector
from probator.plugins.types.resources import S3Bucket, CloudFrontDist, DNSZone, DNSRecord, IAMUser, AccessKey
from probator.utils import get_resource_id
from probator.wrappers import retry, rollback


@dataclass
class BucketInfo(object):
    website: bool
    tags: dict = field(default_factory=dict)
    public: bool = False


class AWSRoute53Collector(AWSBaseAccountCollector):
    name = 'AWS Route53 Collector'

    @rollback
    def run(self):
        """Update list of Route53 DNS Zones and their records for the account

        Returns:
            `None`
        """
        self.log.debug(f'Updating Route53 information for {self.account.account_name}')

        # region Update zones
        existing_zones = DNSZone.get_all(self.account)
        zones = self.__fetch_route53_zones()
        new_resources = {}

        if zones:
            for resource_id, data in zones.items():
                tags = data.pop('tags')
                new_resources[resource_id] = NewResource(
                    resource_id=resource_id,
                    properties=data,
                    tags=tags
                )

        self.process_resources(
            resource_class=DNSZone,
            account_id=self.account.account_id,
            location=None,
            new_resources=new_resources,
            existing_resources=existing_zones
        )
        # endregion

        # region Update resource records
        for zone_id, zone in DNSZone.get_all(self.account).items():
            existing_records = {rec.id: rec for rec in zone.children}
            records = self.__fetch_route53_zone_records(zone.get_property('zone_id').value)
            new_resources = {}

            if records:
                for record_id, data in records.items():
                    new_resources[record_id] = NewResource(
                        resource_id=record_id,
                        properties=data,
                        parent=zone
                    )

                self.process_resources(
                    resource_class=DNSRecord,
                    account_id=self.account.account_id,
                    location=None,
                    new_resources=new_resources,
                    existing_resources=existing_records
                )
        # endregion

    # region Helper functions
    @retry
    def __fetch_route53_zones(self):
        """Return a list of all DNS zones hosted in Route53

        Returns:
            :obj:`list` of `dict`
        """
        done = False
        marker = None
        zones = {}
        route53 = self.session.client('route53')

        try:
            while not done:
                if marker:
                    response = route53.list_hosted_zones(Marker=marker)
                else:
                    response = route53.list_hosted_zones()

                if response['IsTruncated']:
                    marker = response['NextMarker']
                    # There is a strict ratelimit on API requests of max 5 API requests per account, per second
                    # https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/DNSLimitations.html#limits-api-requests-route-53
                    time.sleep(0.5)
                else:
                    done = True

                for zone_data in response['HostedZones']:
                    zones[get_resource_id('r53z', zone_data['Id'])] = {
                        'name': zone_data['Name'].rstrip('.'),
                        'source': f'AWS/{self.account.account_name}',
                        'comment': zone_data['Config']['Comment'] if 'Comment' in zone_data['Config'] else None,
                        'zone_id': zone_data['Id'],
                        'private_zone': zone_data['Config']['PrivateZone'],
                        'tags': self.__fetch_route53_zone_tags(zone_data['Id'])
                    }

            return munchify(zones)

        finally:
            del route53

    @retry
    def __fetch_route53_zone_records(self, zone_id):
        """Return all resource records for a specific Route53 zone

        Args:
            zone_id (`str`): Name / ID of the hosted zone

        Returns:
            `dict`
        """
        route53 = self.session.client('route53')

        done = False
        next_name = next_type = None
        records = {}

        try:
            while not done:
                if next_name and next_type:
                    response = route53.list_resource_record_sets(
                        HostedZoneId=zone_id,
                        StartRecordName=next_name,
                        StartRecordType=next_type
                    )
                else:
                    response = route53.list_resource_record_sets(HostedZoneId=zone_id)

                if response['IsTruncated']:
                    next_name = response['NextRecordName']
                    next_type = response['NextRecordType']
                    # There is a strict ratelimit on API requests of max 5 API requests per account, per second
                    # https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/DNSLimitations.html#limits-api-requests-route-53
                    time.sleep(0.5)
                else:
                    done = True

                if 'ResourceRecordSets' in response:
                    for record in response['ResourceRecordSets']:
                        # Cannot make this a list, due to a race-condition in the AWS api that might return the same
                        # record more than once, so we use a dict instead to ensure that if we get duplicate records
                        # we simply just overwrite the one already there with the same info.
                        record_id = self._get_resource_hash(zone_id, record)
                        if 'AliasTarget' in record:
                            value = record['AliasTarget']['DNSName']
                            records[record_id] = {
                                'name': record['Name'].rstrip('.'),
                                'type': 'ALIAS',
                                'ttl': 0,
                                'value': [value]
                            }
                        else:
                            value = [y['Value'] for y in record['ResourceRecords']]
                            records[record_id] = {
                                'name': record['Name'].rstrip('.'),
                                'type': record['Type'],
                                'ttl': record['TTL'],
                                'value': value
                            }

            return munchify(records)

        finally:
            del route53

    @retry
    def __fetch_route53_zone_tags(self, zone_id):
        """Return a dict with the tags for the zone

        Args:
            zone_id (`str`): ID of the hosted zone

        Returns:
            :obj:`dict` of `str`: `str`
        """
        route53 = self.session.client('route53')

        try:
            return {
                tag['Key']: tag['Value'] for tag in
                route53.list_tags_for_resource(
                    ResourceType='hostedzone',
                    ResourceId=zone_id.split('/')[-1]
                )['ResourceTagSet']['Tags']
            }

        finally:
            del route53

    @staticmethod
    def _get_resource_hash(zone_name, record):
        """Returns the last ten digits of the sha256 hash of the combined arguments. Useful for generating unique
        resource IDs

        Args:
            zone_name (`str`): The name of the DNS Zone the record belongs to
            record (`dict`): A record dict to generate the hash from

        Returns:
            `str`
        """
        record_data = deepcopy(record)
        if type(record_data.get('GeoLocation', None)) == dict:
            record_data['GeoLocation'] = ':'.join(f'{k}={v}' for k, v in record_data['GeoLocation'].items())

        args = [
            zone_name,
            record_data.get('Name', 0),
            record_data.get('Type', 0),
            record_data.get('Weight', 0),
            record_data.get('Region', 0),
            record_data.get('GeoLocation', 0),
            record_data.get('Failover', 0),
            record_data.get('HealthCheckId', 0),
            record_data.get('TrafficPolicyInstanceId', 0)
        ]

        return get_resource_id('r53r', args)
    # endregion


class AWSS3Collector(AWSBaseAccountCollector):
    name = 'AWS S3 Collector'

    def run(self):
        self.update_s3buckets()

    @rollback
    @retry
    def update_s3buckets(self):
        """Update list of S3 Buckets for the account

        Returns:
            `None`
        """
        self.log.debug(f'Updating S3Buckets for {self.account.account_name}')
        s3 = self.session.resource('s3')

        try:
            buckets = {bucket.name: bucket for bucket in s3.buckets.all()}
            existing_buckets = S3Bucket.get_all(self.account)
            new_resources = {}

            if buckets:
                for bucket in buckets.values():
                    resource_id = f's3-{bucket.name}'
                    bucket_info = self._get_bucket_information(bucket)

                    new_resources[resource_id] = NewResource(
                        resource_id=resource_id,
                        properties={
                            'website_enabled': bucket_info.website,
                            'public': bucket_info.public,
                        },
                        tags=bucket_info.tags
                    )

            self.process_resources(
                resource_class=S3Bucket,
                account_id=self.account.account_id,
                location=None,
                new_resources=new_resources,
                existing_resources=existing_buckets
            )

        finally:
            del s3

    def _get_bucket_information(self, bucket):
        """Collect extra bucket information

        Args:
            bucket (`S3Bucket`): Boto3 S3Bucket object

        Returns:
            `BucketInfo`
        """
        return BucketInfo(
            website=self._get_bucket_website(bucket=bucket),
            tags=self._get_bucket_tags(bucket=bucket),
            public=self._get_bucket_public(bucket=bucket)
        )

    @retry
    def _get_bucket_website(self, *, bucket):
        """Check if a bucket is configured as a static website

        Args:
            bucket (:boto3:Bucket): Bucket object

        Returns:
            `bool` - `True` if website is enabled, else `False`
        """
        try:
            if bucket.Website().index_document:
                return True

        except ClientError as e:
            code = e.response['Error']['Code']
            if code == 'NoSuchWebsiteConfiguration':
                return False

            elif code == 'AccessDenied':
                self.log.debug(f'Bucket ACL is prevents gathering website information on {self.account.account_name} / {bucket.name}')

        return False

    @retry
    def _get_bucket_tags(self, *, bucket):
        """Return dict of tags on bucket

        Args:
            bucket (:boto3:Bucket): Bucket object

        Returns:
            `dict` - A dictionary of key/value tags
        """
        try:
            return {t['Key']: t['Value'] for t in bucket.Tagging().tag_set}

        except ClientError:
            return {}

    @retry
    def _get_bucket_public(self, *, bucket):
        """Check if the public has been set to be publicly accessible

        Args:
            bucket (:boto3:Bucket): Bucket object

        Returns:
            :obj:bool - `True` if bucket is public, else `False`
        """
        s3 = self.session.client('s3')

        try:
            res = s3.get_bucket_policy_status(Bucket=bucket.name)

            return res['PolicyStatus']['IsPublic']

        except ClientError as ex:
            rex = ex.response['Error']['Code']

            if 'AccessDenied' in rex:
                self.log.info(f'Unable to get public status due to ACL limiting access for {self.account.account_name}/{bucket.name}')
                return False

            elif 'NoSuchBucketPolicy' not in rex:
                raise

        finally:
            del s3

        return False


class AWSCloudFrontCollector(AWSBaseAccountCollector):
    name = 'AWS CloudFront Collector'

    def run(self):
        self.update_cloudfront()

    @rollback
    @retry
    def update_cloudfront(self):
        """Update list of CloudFront Distributions for the account

        Returns:
            `None`
        """
        self.log.debug(f'Updating CloudFront distributions for {self.account.account_name}')
        dists = self._fetch_distributions()
        existing_dists = CloudFrontDist.get_all(self.account, None)
        new_resources = {}

        if dists:
            for resource_id, properties in dists.items():
                tags = properties.pop('tags')
                new_resources[resource_id] = NewResource(
                    resource_id=resource_id,
                    properties=properties,
                    tags=tags
                )

        self.process_resources(
            resource_class=CloudFrontDist,
            account_id=self.account.account_id,
            location=None,
            new_resources=new_resources,
            existing_resources=existing_dists
        )

    @retry
    def _fetch_distributions(self):
        cfr = self.session.client('cloudfront')

        try:
            dists = {}

            # region Web distributions
            done = False
            marker = None
            while not done:
                if marker:
                    response = cfr.list_distributions(Marker=marker)
                else:
                    response = cfr.list_distributions()

                dl = response['DistributionList']
                if dl['IsTruncated']:
                    marker = dl['NextMarker']
                else:
                    done = True

                if 'Items' in dl:
                    for dist in dl['Items']:
                        origins = []
                        for origin in dist['Origins']['Items']:
                            if 'S3OriginConfig' in origin:
                                origins.append({'type': 's3', 'source': origin['DomainName']})

                            elif 'CustomOriginConfig' in origin:
                                origins.append({'type': 'custom-http', 'source': origin['DomainName']})

                        resource_id = get_resource_id('cfd', dist['ARN'])
                        data = {
                            'arn': dist['ARN'],
                            'domain_name': dist['DomainName'],
                            'origins': origins,
                            'enabled': dist['Enabled'],
                            'type': 'web',
                            'tags': self._get_distribution_tags(cfr, dist['ARN'])
                        }
                        dists[resource_id] = data
            # endregion

            # region Streaming distributions
            done = False
            marker = None
            while not done:
                if marker:
                    response = cfr.list_streaming_distributions(Marker=marker)
                else:
                    response = cfr.list_streaming_distributions()

                dl = response['StreamingDistributionList']
                if dl['IsTruncated']:
                    marker = dl['NextMarker']
                else:
                    done = True

                if 'Items' in dl:
                    for dist in dl['Items']:
                        resource_id = get_resource_id('cfd', dist['ARN'])
                        data = {
                            'arn': dist['ARN'],
                            'name': dist['DomainName'],
                            'origins': [{'type': 's3', 'source': dist['S3Origin']['DomainName']}],
                            'enabled': dist['Enabled'],
                            'type': 'rtmp',
                            'tags': self._get_distribution_tags(cfr, dist['ARN'])
                        }
                        dists[resource_id] = data
            # endregion

            return dists
        finally:
            del cfr
        # endregion

    @retry
    def _get_distribution_tags(self, client, arn):
        """Returns a dict containing the tags for a CloudFront distribution

        Args:
            client (botocore.client.CloudFront): Boto3 CloudFront client object
            arn (str): ARN of the distribution to get tags for

        Returns:
            `dict`
        """
        tags = client.list_tags_for_resource(Resource=arn).get('Tags').get('Items')
        return {tag['Key']: tag['Value'] for tag in tags}


class AWSIAMUserCollector(AWSBaseAccountCollector):
    name = 'AWS CloudFront Collector'

    def run(self):
        iam = self.session.resource('iam')

        try:
            existing_users = IAMUser.get_all(self.account)
            api_users = list(iam.users.all())
            new_resources = {}

            for user_info in api_users:
                user_id = get_resource_id('iamuser', user_info.arn)
                properties = {
                    'name': user_info.name,
                    'arn': user_info.arn,
                    'creation_time': user_info.create_date,
                    'path': user_info.path,
                    'has_password': self._user_has_password(user_info.name),
                }
                tags = {tag['Key']: tag['Value'] for tag in user_info.tags or {}}
                new_resources[user_id] = NewResource(
                    resource_id=user_id,
                    properties=properties,
                    tags=tags
                )

            self.process_resources(
                resource_class=IAMUser,
                account_id=self.account.account_id,
                location=None,
                new_resources=new_resources,
                existing_resources=existing_users
            )

            for resource_id, data in new_resources.items():
                self.update_access_keys(
                    username=data.properties['name'],
                    user_id=get_resource_id('iamuser', data.properties['arn'])
                )

        finally:
            del iam

    def update_access_keys(self, *, username, user_id):
        """Update access keys for a specific user

        Args:
            username (`str`): Name of the IAM user
            user_id (`str`): The internal Probator ID for the user

        Returns:

        """
        iam = self.session.resource('iam')
        iamc = self.session.client('iam')

        try:
            api_user = iam.User(username)
            user = IAMUser.get(user_id)
            keys = api_user.access_keys.all()
            existing_keys = {key.id: key for key in user.children}
            new_resources = {}

            for key in keys:
                properties = {
                    'create_date': key.create_date,
                    'last_used': self._last_access_key_usage(key.id),
                    'status': key.status,
                }

                new_resources[key.id] = NewResource(
                    resource_id=key.id,
                    properties=properties,
                    parent=user
                )

            self.process_resources(
                resource_class=AccessKey,
                account_id=self.account.account_id,
                location=None,
                new_resources=new_resources,
                existing_resources=existing_keys
            )

        finally:
            del iam
            del iamc

    def _user_has_password(self, username):
        """Check if the user has a login profile (password)

        Args:
            username (`str`): Username to lookup

        Returns:
            `bool` - `True` if a login profile is present, else `False`
        """
        iam = self.session.client('iam')

        try:
            iam.get_login_profile(UserName=username)

            return True

        except ClientError as ex:
            rex = ex.response['Error']['Code']

            if 'NoSuchEntity' in rex:
                return False

            raise
        finally:
            del iam

    def _last_access_key_usage(self, access_key_id):
        """Return the datetime of the last usage of the access key

        Args:
            access_key_id (`str`): ID of the access key

        Returns:
            `datetime` or `None` - Return :py3:`datetime` object, or `None` if the key hasn't been used
        """
        iam = self.session.client('iam')

        try:
            res = iam.get_access_key_last_used(AccessKeyId=access_key_id)

            return res['AccessKeyLastUsed']['LastUsedDate']

        except KeyError:
            return None

        finally:
            del iam
