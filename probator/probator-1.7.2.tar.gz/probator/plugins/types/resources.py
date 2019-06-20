import logging
import re
from abc import abstractmethod, ABC
from dataclasses import dataclass
from datetime import datetime, timedelta

from flask import session
from probator.plugins.types.accounts import BaseAccount
from sqlalchemy import func, or_, and_, cast, DATETIME
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import aliased

from probator import get_plugin_by_name
from probator.constants import RGX_EMAIL_VALIDATION_PATTERN, PLUGIN_NAMESPACES
from probator.database import db
from probator.exceptions import ResourceException, ProbatorError
from probator.schema import Tag, Account, Resource, ResourceType, ResourceProperty, ResourceMapping
from probator.utils import is_truthy, to_camelcase, NotificationContact, parse_date


@dataclass
class ResourceProp(object):
    key: str
    name: str
    type: str
    show: bool = True
    primary: bool = False
    resource_reference: bool = False


class BaseResource(ABC):
    """Base type object for resource objects"""
    resource_properties = []

    def __init__(self, resource):
        self.resource = resource
        self.log = logging.getLogger(self.__class__.__module__)

    def __getattr__(self, item):
        for prop in self.resource_properties:
            if prop.key == item:
                if prop.type == 'datetime':
                    return parse_date(self.get_property(item).value)

                elif prop.type == 'bool':
                    return is_truthy(self.get_property(item).value)

                return self.get_property(item).value

        raise AttributeError(f'{self.__class__.__name__} has no attribute {item}')

    def __str__(self):
        if self.location:
            return f'{self.account.account_name} / {self.location} / {self.id}'
        else:
            return f'{self.account.account_name} / {self.id}'

    # region Object properties
    @property
    def id(self):
        return self.resource.resource_id

    @property
    def tags(self):
        return self.resource.tags

    @property
    def properties(self):
        return self.resource.properties

    @property
    def account_id(self):
        """Returns the ID of the account that owns the resource

        Returns:
            `int`
        """
        return self.resource.account_id

    @property
    def account(self):
        """Return the Account object for the instance

        Returns:
            `Account`
        """
        return BaseAccount.get_typed_account(self.resource.account)

    @property
    def location(self):
        """Returns the location of the resource, or None

        Returns:
            `str`, `None`
        """
        return self.resource.location

    @property
    def parents(self):
        """Returns a list of parent objects (objects which the resource is attached to) if any, else `None`

        Returns:
            `list` of :obj:`Resource`, `None`
        """
        return list(map(BaseResource.get_typed_resource, self.resource.parents))

    @property
    def children(self):
        """Returns a list of child objects (objects which are attached to the resource) if any, else `None`

        Returns:
            `list` of :obj:`Resource`, `None`
        """
        return list(map(BaseResource.get_typed_resource, self.resource.children))

    @property
    def created(self):
        """Time the resource was created

        Returns:
            `datetime`
        """
        return self.resource.created

    @property
    def updated(self):
        """Time the resource was last updated

        Returns:
            `datetime`
        """
        return self.resource.updated

    @property
    @abstractmethod
    def resource_type(self):
        """The ResourceType of the object"""

    @property
    @abstractmethod
    def resource_name(self):
        """Human friendly name of the resource type"""

    @property
    @abstractmethod
    def resource_group(self):
        """Resource group name"""
    # endregion

    # region Static and Class methods
    @staticmethod
    def get(resource_id):
        """Returns the class object identified by `resource_id`

        Args:
            resource_id (str): Unique EC2 Instance ID to load from database

        Returns:
            EC2 Instance object if found, else None
        """
        resource = Resource.get(resource_id)

        if not resource:
            return None

        resource_type = ResourceType.get(resource.resource_type_id).resource_type
        resource_class = get_plugin_by_name(PLUGIN_NAMESPACES['types'], resource_type)

        return resource_class(resource)

    @classmethod
    def create(cls, resource_id, *, account_id, properties=None, tags=None, location=None, auto_add=True, auto_commit=False):
        """Creates a new Resource object with the properties and tags provided

        Args:
            resource_id (str): Unique identifier for the resource object
            account_id (int): Account ID which owns the resource
            properties (dict): Dictionary of properties for the resource object.
            tags (dict): Key / value dictionary of tags. Values must be `str` types
            location (str): Location of the resource, if applicable
            auto_add (bool): Automatically add the new resource to the DB session. Default: True
            auto_commit (bool): Automatically commit the change to the database. Default: False
        """
        if cls.get(resource_id):
            raise ResourceException(f'Resource {resource_id} already exists')

        res = Resource()
        res.resource_id = resource_id
        res.account_id = account_id
        res.location = location
        res.resource_type_id = ResourceType.get(cls.resource_type).resource_type_id

        if properties:
            for name, value in properties.items():
                prop = ResourceProperty()
                prop.resource_id = res.resource_id
                prop.name = name
                prop.value = value.isoformat() if type(value) == datetime else value
                res.properties.append(prop)
                db.session.add(prop)

        if tags:
            for key, value in tags.items():
                if type(value) != str:
                    raise ValueError(f'Invalid object type for tag value: {key}')

                tag = Tag()
                tag.resource_id = resource_id
                tag.key = key
                tag.value = value
                res.tags.append(tag)
                db.session.add(tag)

        if auto_add:
            db.session.add(res)

            if auto_commit:
                db.session.commit()

            return cls.get(res.resource_id)
        else:
            return cls(res)

    @classmethod
    def get_all(cls, account=None, location=None, include_disabled=False):
        """Returns a list of all resources for a given account, location and resource type.

        Attributes:
            account (:obj:`Account`): Account owning the resources
            location (`str`): Location of the resources to return (region)
            include_disabled (`bool`): Include resources from disabled accounts (default: False)

        Returns:
            `dict` of Resource objects, keyed by the resource ID
        """
        if cls == BaseResource:
            raise ProbatorError('get_all on BaseResource is not supported')

        qry = db.Resource.filter(
            Resource.resource_type_id == ResourceType.get(cls.resource_type).resource_type_id
        )

        if account:
            qry = qry.filter(Resource.account_id == account.account_id)

        if not include_disabled:
            qry = qry.join(Account, Resource.account_id == Account.account_id).filter(Account.enabled == 1)

        if location:
            qry = qry.filter(Resource.location == location)

        return {res.resource_id: cls(res) for res in qry.all()}

    @classmethod
    def find(cls, *, limit=25, page=0, accounts=None, locations=None, resources=None,
             resource_types=None, parent_id=None, properties=None, include_disabled=False, return_query=False):
        """Find resources based on the provided filters.

        If `return_query` a sub-class of `sqlalchemy.orm.Query` is returned instead of the resource list.

        Args:
            limit (`int`): Number of results to return. Default: 100
            page (`int`): Pagination offset for results. Default: 0
            accounts (`list` of `int`): A list of account id's to limit the returned resources to
            locations (`list` of `str`): A list of locations as strings to limit the search for
            resources ('list' of `str`): A list of resource_ids
            resource_types (`list` of `str`): A list of resource types
            parent_id (`str`): ID of parent resource. If set, only return child objects of `parent_id`
            properties (`dict`): A `dict` containing property name and value pairs. Values can be either a str or a list
            of strings, in which case a boolean OR search is performed on the values
            include_disabled (`bool`): Include resources from disabled accounts. Default: False
            return_query (`bool`): Returns the query object prior to adding the limit and offset functions. Allows for
            sub-classes to amend the search feature with extra conditions. The calling function must handle pagination
            on its own

        Returns:
            `list` of `Resource`, `sqlalchemy.orm.Query`
        """
        qry = db.Resource.order_by(Resource.resource_type_id, Resource.resource_id)

        if cls != BaseResource or resource_types:
            qry = qry.join(
                ResourceType, Resource.resource_type_id == ResourceType.resource_type_id
            ).filter(
                ResourceType.resource_type.in_(resource_types or [cls.resource_type])
            )

        if session:
            qry = qry.filter(Resource.account_id.in_(session['accounts']))

        if not include_disabled:
            qry = qry.join(Account, Resource.account_id == Account.account_id).filter(Account.enabled == 1)

        if accounts:
            qry = qry.filter(Resource.account_id.in_([Account.get(acct).account_id for acct in accounts]))

        if locations:
            qry = qry.filter(Resource.location.in_(locations))

        if resources:
            qry = qry.filter(Resource.resource_id.in_(resources))

        if parent_id:
            qry = qry.join(ResourceMapping, Resource.resource_id == ResourceMapping.child).filter(
                ResourceMapping.parent == parent_id
            )

        if properties:
            for prop_name, value in properties.items():
                alias = aliased(ResourceProperty)

                qry = qry.join(alias, Resource.resource_id == alias.resource_id)

                if type(value) == list:
                    where_clause = []
                    for item in value:
                        where_clause.append(alias.value == item)

                    qry = qry.filter(
                        and_(
                            alias.name == prop_name,
                            or_(*where_clause)
                        ).self_group()
                    )
                else:
                    qry = qry.filter(
                        and_(
                            alias.name == prop_name,
                            alias.value == value
                        ).self_group()
                    )

        if return_query:
            return qry

        total = qry.count()
        qry = qry.limit(limit)
        qry = qry.offset(page * limit if page > 0 else 0)

        return total, list(map(BaseResource.get_typed_resource, qry.all()))

    @staticmethod
    def get_typed_resource(resource):
        """Returns a given resource object as the proper type

        Args:
             resource (BaseResource, str, int): A resource object

        Returns:
            `resource`
        """
        if type(resource) in (int, str):
            resource = Resource.get(resource)

        elif issubclass(resource.__class__, BaseResource):
            resource = resource.resource

        resource_type = ResourceType.get(resource.resource_type_id).resource_type
        resource_class = get_plugin_by_name(PLUGIN_NAMESPACES['types'], resource_type)
        if not resource_class:
            raise ProbatorError(f'Unknown resource type: {resource_type}')

        return resource_class(resource)
    # endregion

    # region Instance methods
    def get_contacts(self):
        """Return list of `NotificationContact` for the resource

        Returns:
            `list` of `NotificationContact`
        """
        return self.account.contacts

    def get_owner_emails(self, partial_owner_match=True):
        """Return a list of email addresses associated with the instance, based on tags

        Returns:
            List of email addresses if any, else None
        """
        for tag in self.tags:
            if tag.key.lower() == 'owner':
                rgx = re.compile(RGX_EMAIL_VALIDATION_PATTERN, re.I)
                if partial_owner_match:
                    match = rgx.findall(tag.value)
                    if match:
                        return [NotificationContact('email', email) for email in match]
                else:
                    match = rgx.match(tag.value)
                    if match:
                        return [NotificationContact('email', email) for email in match.groups()]
        return None

    def get_name_or_id(self, with_id=False):
        """Return the value of the Name tag if present, else return the resource id

        Args:
            with_id (`bool`): Return the ID along with the name

        Returns:
            `str`
        """
        name = self.get_tag('Name')
        if name and len(name.value.strip()) > 0:
            return f'{name.value} ({self.id})' if with_id else name.value

        return self.id

    def get_property(self, name):
        """Return a named property for a resource, if available. Will raise an `AttributeError` if the property
        does not exist

        Args:
            name (str): Name of the property to return

        Returns:
            `ResourceProperty`
        """
        for prop in self.resource.properties:
            if prop.name == name:
                return prop

        raise AttributeError(name)

    def set_property(self, name, value):
        """Create or set the value of a property. Returns `True` if the property was created or updated, or `False` if
        there were no changes to the value of the property.

        Args:
            name (str): Name of the property to create or update
            value (any): Value of the property. This can be any type of JSON serializable data

        Returns:
            `bool`
        """
        if type(value) == datetime:
            value = value.isoformat()

        try:
            prop = self.get_property(name)
            if prop.value == value:
                return False

            prop.value = value

        except AttributeError:
            prop = ResourceProperty()
            prop.resource_id = self.id
            prop.name = name
            prop.value = value

        db.session.add(prop)

        return True

    def delete_property(self, name):
        """Removes a property from an object, by the name of the property. Returns `True` if the property was removed or
        `False` if the property didn't exist.

        Args:
            name (str): Name of the property to delete

        Returns:
            `bool`
        """
        try:
            self.log.debug(f'Removing property {name} from {self.id}')
            prop = getattr(self, name)
            self.properties.remove(prop)

            db.session.delete(prop)

            return True
        except AttributeError:
            return False

    def get_tag(self, key, *, case_sensitive=True):
        """Return a tag by key, if found

        Args:
            key (str): Name/key of the tag to locate
            case_sensitive (bool): Should tag keys be treated case-sensitive (default: true)

        Returns:
            `Tag`,`None`
        """
        key = key if case_sensitive else key.lower()
        for tag in self.resource.tags:
            if not case_sensitive:
                if tag.key.lower() == key:
                    return tag
            elif key == tag.key:
                return tag

        return None

    def set_tag(self, key, value, update_session=True):
        """Create or set the value of the tag with `key` to `value`. Returns `True` if the tag was created or updated or
        `False` if there were no changes to be made.

        Args:
            key (str): Key of the tag
            value (str): Value of the tag
            update_session (bool): Automatically add the change to the SQLAlchemy session. Default: True

        Returns:
            `bool`
        """
        existing_tags = {x.key: x for x in self.tags}
        if key in existing_tags:
            tag = existing_tags[key]

            if tag.value == value:
                return False

            tag.value = value
        else:
            tag = Tag()
            tag.resource_id = self.id
            tag.key = key
            tag.value = value
            self.tags.append(tag)

        if update_session:
            db.session.add(tag)
        return True

    def delete_tag(self, key, update_session=True):
        """Removes a tag from a resource based on the tag key. Returns `True` if the tag was removed or `False` if the
        tag didn't exist

        Args:
            key (str): Key of the tag to delete
            update_session (bool): Automatically add the change to the SQLAlchemy session. Default: True

        Returns:

        """
        existing_tags = {x.key: x for x in self.tags}
        if key in existing_tags:
            if update_session:
                db.session.delete(existing_tags[key])

            self.tags.remove(existing_tags[key])
            return True

        return False

    def save(self, *, auto_commit=False):
        """Save the resource to the database

        Args:
            auto_commit (bool): Automatically commit the transaction. Default: `False`

        Returns:
            `None`
        """
        try:
            db.session.add(self.resource)
            if auto_commit:
                db.session.commit()

        except SQLAlchemyError as ex:
            self.log.exception(f'Failed updating resource: {ex}')
            db.session.rollback()

    def delete(self, *, auto_commit=False):
        """Removes a resource from the database

        Args:
            auto_commit (bool): Automatically commit the transaction. Default: `False`

        Returns:
            `None`
        """
        try:
            db.session.delete(self.resource)
            if auto_commit:
                db.session.commit()

        except SQLAlchemyError:
            self.log.exception(f'Failed deleting resource: {self.id}')
            db.session.rollback()

    def update_resource(self, properties, tags=None):
        """Updates the resource object with the information from `data`. The changes will be added to the current
        db.session but will not be commited. The user will need to perform the commit explicitly to save the changes

        Args:
            properties (`dict`): A dictionary of properties to update
            tags (`dict`): A dictionary of tags to update

        Returns:
            True if resource object was updated, else False
        """
        updated = False

        for prop in self.resource_properties:
            if prop.key in properties:
                updated |= self.set_property(prop.key, properties[prop.key])

        if tags is not None:
            existing_tags = {x.key: x for x in self.tags}
            for key, value in list(tags.items()):
                updated |= self.set_tag(key, value)

            # Check for removed tags
            for key in list(existing_tags.keys()):
                if key not in tags:
                    updated |= self.delete_tag(key)

        if updated:
            self.resource.updated = datetime.now()

        return updated

    def add_child(self, child):
        """Add a new child object to the resource

        Args:
            child (`BaseResource`): Child resource object

        Returns:
            `None`
        """
        self.resource.children.append(child.resource)

    def delete_child(self, child):
        """Remove a child from the object

        Args:
            child (`BaseResource`): Child resource object

        Returns:
            `None`
        """
        self.resource.children.remove(child.resource)
        child.delete()

    def to_json(self, with_children=False):
        """Return a `dict` representation of the resource, including all properties and tags

        Args:
            with_children (`bool`): Return any child resource objects along with the data

        Returns:
            `dict`
        """
        res = {
            'resourceType': self.resource.resource_type_id,
            'resourceId': self.id,
            'accountId': self.resource.account_id,
            'account': self.account,
            'location': self.resource.location,
            'properties': {to_camelcase(prop.name): prop.value for prop in self.resource.properties},
            'tags': [{'key': t.key, 'value': t.value} for t in self.resource.tags]
        }

        if with_children:
            res['children'] = self.children

        return res
    # endregion


class AWSBaseResource(BaseResource, ABC):
    resource_group = 'AWS'


class EC2Instance(AWSBaseResource):
    """EC2 Instance"""
    resource_type = 'aws_ec2_instance'
    resource_name = 'EC2 Instance'

    resource_properties = [
        ResourceProp(key='launch_date', name='Launch Date', type='datetime'),
        ResourceProp(key='state', name='State', type='string'),
        ResourceProp(key='instance_type', name='Instance Type', type='string', primary=True),
        ResourceProp(key='private_ip', name='Private IP', type='string'),
        ResourceProp(key='private_dns', name='Private DNS', type='string'),
        ResourceProp(key='public_ip', name='Public IP', type='string'),
        ResourceProp(key='public_dns', name='Public DNS', type='string'),
        ResourceProp(key='created', name='Created', type='datetime', show=False),
        ResourceProp(key='ami_id', name='AMI Id', type='string', resource_reference=True),
        ResourceProp(key='platform', name='Platform', type='string'),
    ]

    # region Object properties

    @property
    def volumes(self):
        """Returns a list of the volumes attached to the instance

        Returns:
            `list` of `EBSVolume`
        """
        return [
            EBSVolume(res) for res in db.Resource.join(
                ResourceProperty, Resource.resource_id == ResourceProperty.resource_id
            ).filter(
                Resource.resource_type_id == ResourceType.get(EBSVolume.resource_type).resource_type_id,
                ResourceProperty.name == 'attachments',
                func.JSON_CONTAINS(ResourceProperty.value, func.JSON_QUOTE(self.id))
            ).all()
        ]
    # endregion

    @classmethod
    def search_by_age(cls, *, limit=100, page=1, accounts=None, locations=None, age=720,
                      properties=None, include_disabled=False):
        """Search for resources based on the provided filters

        Args:
            limit (`int`): Number of results to return. Default: 100
            page (`int`): Pagination offset for results. Default: 1
            accounts (`list` of `int`): A list of account id's to limit the returned resources to
            locations (`list` of `str`): A list of locations as strings to limit the search for
            age (`int`): Age of instances older than `age` days to return
            properties (`dict`): A `dict` containing property name and value pairs. Values can be either a str or a list
            of strings, in which case a boolean OR search is performed on the values
            include_disabled (`bool`): Include resources from disabled accounts. Default: False

        Returns:
            `list` of `Resource`
        """
        qry = cls.search(
            limit=limit,
            page=page,
            resource_types=[ResourceType.get(cls.resource_type).resource_type],
            accounts=accounts,
            locations=locations,
            properties=properties,
            include_disabled=include_disabled,
            return_query=True
        )

        age_alias = aliased(ResourceProperty)
        qry = (
            qry.join(age_alias, Resource.resource_id == age_alias.resource_id).filter(
                age_alias.name == 'launch_date',
                cast(func.JSON_UNQUOTE(age_alias.value), DATETIME) < datetime.now() - timedelta(days=age)
            )
        )

        total = qry.count()
        qry = qry.limit(limit)
        qry = qry.offset((page - 1) * limit if page > 1 else 0)

        return total, [cls(x) for x in qry.all()]


class BeanStalk(AWSBaseResource):
    """Elastic Beanstalk object"""
    resource_type = 'aws_beanstalk'
    resource_name = 'Elastic BeanStalk'
    resource_properties = [
        ResourceProp(key='environment_name', name='Environment Name', type='string', primary=True),
        ResourceProp(key='application_name', name='Application Name', type='string'),
        ResourceProp(key='cname', name='CNAME', type='string')
    ]


class CloudFrontDist(AWSBaseResource):
    """CloudFront Distribution object"""
    resource_type = 'aws_cloudfront_dist'
    resource_name = 'CloudFront Distribution'
    resource_properties = [
        ResourceProp(key='arn', name='ARN', type='string'),
        ResourceProp(key='domain_name', name='Domain Name', type='string', primary=True),
        ResourceProp(key='origins', name='Origins', type='json'),
        ResourceProp(key='enabled', name='Enabled', type='bool'),
        ResourceProp(key='type', name='Type', type='string'),
    ]


class S3Bucket(AWSBaseResource):
    """S3 Bucket object"""
    resource_type = 'aws_s3_bucket'
    resource_name = 'S3 Bucket'
    resource_properties = [
        ResourceProp(key='website_enabled', name='Website Enabled', type='bool'),
        ResourceProp(key='public', name='Public', type='bool'),
    ]


class EBSSnapshot(AWSBaseResource):
    """EBS Snapshot object"""
    resource_type = 'aws_ebs_snapshot'
    resource_name = 'EBS Snapshot'
    resource_properties = [
        ResourceProp(key='state', name='State', type='string'),
        ResourceProp(key='state_message', name='State Message', type='string'),
        ResourceProp(key='encrypted', name='Encrypted', type='string', primary=True),
        ResourceProp(key='kms_key_id', name='KMS Key ID', type='string'),
        ResourceProp(key='volume_id', name='Volume ID', type='string', resource_reference=True),
        ResourceProp(key='volume_size', name='Volume Size', type='string'),
    ]


class EBSVolume(AWSBaseResource):
    """EBS Volume object"""
    resource_type = 'aws_ebs_volume'
    resource_name = 'EBS Volume'

    resource_properties = [
        ResourceProp(key='create_time', name='Creation Time', type='datetime'),
        ResourceProp(key='state', name='State', type='string'),
        ResourceProp(key='iops', name='IOPS', type='string'),
        ResourceProp(key='encrypted', name='Encrypted', type='bool', primary=True),
        ResourceProp(key='kms_key_id', name='KMS Key ID', type='string'),
        ResourceProp(key='snapshot_id', name='Snapshot ID', type='string', resource_reference=True),
        ResourceProp(key='size', name='Size', type='string'),
        ResourceProp(key='attachments', name='Attachments', type='dict'),
        ResourceProp(key='volume_type', name='Volume Type', type='string'),
    ]


class AMI(AWSBaseResource):
    """AMI object"""
    resource_type = 'aws_ami'
    resource_name = 'AMI'
    resource_properties = [
        ResourceProp(key='architecture', name='Architecture', type='string'),
        ResourceProp(key='description', name='Description', type='string'),
        ResourceProp(key='name', name='Name', type='string', primary=True),
        ResourceProp(key='platform', name='Platform', type='string'),
        ResourceProp(key='state', name='State', type='string')
    ]


class DNSZone(BaseResource):
    """DNS Zone object"""
    resource_type = 'dns_zone'
    resource_name = 'DNS Zone'
    resource_group = 'DNS'
    resource_properties = [
        ResourceProp(key='name', name='Name', type='string', primary=True),
        ResourceProp(key='source', name='Source', type='string'),
        ResourceProp(key='private_zone', name='Private Zone', type='string'),
        ResourceProp(key='comment', name='Comment', type='string'),
    ]


class DNSRecord(BaseResource):
    """DNS Record object"""
    resource_type = 'dns_record'
    resource_name = 'DNS Record'
    resource_group = 'DNS'
    resource_properties = [
        ResourceProp(key='name', name='Name', type='string', primary=True),
        ResourceProp(key='type', name='Type', type='string'),
        ResourceProp(key='ttl', name='TTL', type='string'),
        ResourceProp(key='value', name='Value', type='string'),
    ]


class VPC(AWSBaseResource):
    """VPC Object"""
    resource_type = 'aws_vpc'
    resource_name = 'VPC'
    resource_properties = [
        ResourceProp(key='cidr_v4', name='IPv4 CIDR', type='string', primary=True),
        ResourceProp(key='is_default', name='Default VPC', type='bool'),
        ResourceProp(key='state', name='State', type='string'),
        ResourceProp(key='vpc_flow_logs_status', name='VPC Flow Log Status', type='string'),
        ResourceProp(key='vpc_flow_logs_log_group', name='VPC Flow Log Group', type='string'),
    ]


class ELB(AWSBaseResource):
    """ELB object"""
    resource_type = 'aws_elb'
    resource_name = 'Classic Load Balancer'
    resource_properties = [
        ResourceProp(key='name', name='Name', type='string', primary=True),
        ResourceProp(key='dns_name', name='DNS Name', type='string'),
        ResourceProp(key='canonical_hosted_zone_name', name='Custom Domain Name', type='string'),
        ResourceProp(key='instances', name='Instances', type='list', resource_reference=True),
        ResourceProp(key='vpc_id', name='VPC ID', type='string', resource_reference=True),
        ResourceProp(key='metrics', name='Metrics', type='dict'),
        ResourceProp(key='state', name='State', type='string', show=False),
    ]


class LoadBalancer(AWSBaseResource):
    """Load Balancer object"""
    resource_type = 'aws_lb'
    resource_name = 'Load Balancer'
    resource_properties = [
        ResourceProp(key='arn', name='ARN', type='string'),
        ResourceProp(key='name', name='Name', type='string', primary=True),
        ResourceProp(key='dns_name', name='DNS Name', type='string'),
        ResourceProp(key='vpc_id', name='VPC ID', type='string', resource_reference=True),
        ResourceProp(key='scheme', name='Scheme', type='string'),
        ResourceProp(key='type', name='Type', type='string'),
        ResourceProp(key='state', name='State', type='string'),
    ]


class ENI(AWSBaseResource):
    """ElasticNetworkInterface object"""
    resource_type = 'aws_eni'
    resource_name = 'ENI'
    resource_properties = [
        ResourceProp(key='vpc_id', name='VPC ID', type='string'),
        ResourceProp(key='instance_id', name='Instance ID', type='string', resource_reference=True),
        ResourceProp(key='status', name='Status', type='string'),
        ResourceProp(key='primary_ip', name='Primary Private IP', type='string', primary=True),
        ResourceProp(key='secondary_ip', name='Secondary Private IP', type='list'),
        ResourceProp(key='public_ip', name='Public IP', type='string'),
        ResourceProp(key='requester_id', name='Requester ID', type='string'),
        ResourceProp(key='attachment_owner', name='Attachment Owner', type='string'),
        ResourceProp(key='description', name='Description', type='string'),
    ]


class RDSInstance(AWSBaseResource):
    """RDS Instance object"""
    resource_type = 'aws_rds_instance'
    resource_name = 'RDS Instance'
    resource_properties = [
        ResourceProp(key='instance_identifier', name='Instance Identifier', type='string', primary=True),
        ResourceProp(key='instance_class', name='Instance Class', type='string'),
        ResourceProp(key='status', name='Status', type='string'),
        ResourceProp(key='dbname', name='Database Name', type='string'),
        ResourceProp(key='allocated_storage', name='Allocated Storage', type='int'),
        ResourceProp(key='multi_az', name='Multi AZ', type='bool'),
        ResourceProp(key='engine', name='Engine', type='string'),
        ResourceProp(key='engine_version', name='Engine Version', type='string'),
        ResourceProp(key='encrypted', name='Encrypted', type='bool'),
    ]


class AccessKey(AWSBaseResource):
    """AWS Access Key object"""
    resource_type = 'aws_access_key'
    resource_name = 'Access Key'
    resource_properties = [
        ResourceProp(key='create_date', name='Key Created', type='datetime', primary=True),
        ResourceProp(key='last_used', name='Last Used', type='datetime'),
        ResourceProp(key='status', name='Status', type='string'),
    ]


class IAMUser(AWSBaseResource):
    """IAM User object"""
    resource_type = 'aws_iam_user'
    resource_name = 'IAM User'
    resource_properties = [
        ResourceProp(key='name', name='Username', type='string', primary=True),
        ResourceProp(key='arn', name='ARN', type='string'),
        ResourceProp(key='creation_time', name='Creation Time', type='datetime'),
        ResourceProp(key='path', name='Path', type='string'),
        ResourceProp(key='has_password', name='Has Password', type='bool'),
    ]


class EKSCluster(AWSBaseResource):
    """EKS Cluster object"""
    resource_type = 'aws_eks_cluster'
    resource_name = 'EKS Cluster'
    resource_properties = [
        ResourceProp(key='name', name='Name', type='string', primary=True),
        ResourceProp(key='arn', name='ARN', type='string'),
        ResourceProp(key='vpc_id', name='VPC ID', type='string', resource_reference=True),
        ResourceProp(key='subnets', name='Subnets', type='list', resource_reference=True),
        ResourceProp(key='status', name='Status', type='string'),
        ResourceProp(key='version', name='Version', type='string'),
        ResourceProp(key='platform_version', name='Platform Version', type='string'),
    ]
