import logging
from abc import abstractmethod, ABC
from dataclasses import dataclass
from datetime import datetime

from probator import get_plugin_by_name, PLUGIN_NAMESPACES
from probator.database import db
from probator.exceptions import IssueException, ProbatorError
from probator.schema import IssuePropertyModel, IssueModel, IssueTypeModel, Account
from probator.utils import to_camelcase, parse_date, is_truthy
from sqlalchemy import or_, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import aliased


@dataclass
class IssueProp(object):
    key: str
    name: str
    type: str
    show: bool = True
    primary: bool = False
    resource_reference: bool = False
    account_reference: bool = False


class BaseIssue(ABC):
    issue_properties = []

    """Base type object for issue objects"""
    def __init__(self, issue):
        self.issue = issue
        self.log = logging.getLogger(self.__class__.__module__)

    def __getattr__(self, item):
        for prop in self.issue_properties:
            if prop.key == item:
                if prop.type == 'datetime':
                    return parse_date(self.get_property(item).value)

                elif prop.type == 'bool':
                    return is_truthy(self.get_property(item).value)

                return self.get_property(item).value

        raise AttributeError(f'{self.__class__.__name__} has no attribute {item}')

    def __str__(self):
        return f'<{self.__class__.__name__} issue_id={self.id}>'

    # region Static and Class methods
    @staticmethod
    def get(issue_id):
        """Returns the class object identified by `issue_id`

        Args:
            issue_id (str): Unique issue ID

        Returns:
            Issue object if found, else None
        """
        issue = IssueModel.get(issue_id)

        if not issue:
            return None

        issue_type = IssueTypeModel.get(issue.issue_type_id).issue_type
        issue_class = get_plugin_by_name(PLUGIN_NAMESPACES['issues'], issue_type)

        return issue_class(issue)

    @classmethod
    def create(cls, issue_id, *, properties, account_id=None, location=None, auto_add=True, auto_commit=False):
        """Creates a new Issue object with the properties and tags provided

        Args:
            issue_id (`str`): Unique identifier for the issue object
            properties (`dict`): Dictionary of properties for the issue object.
            account_id (`int`): ID of account where the issue was discovered, if applicable
            location (`str`): Location of the issue, if applicable
            auto_add (`bool`): Automatically add the new issue to the DB session. Default: True
            auto_commit (`bool`): Automatically commit the change to the database. Default: False
        """
        if cls.get(issue_id):
            raise IssueException('Issue {issue_id} already exists')

        issue = IssueModel()
        issue.issue_id = issue_id
        issue.issue_type_id = IssueTypeModel.get(cls.issue_type).issue_type_id
        issue.account_id = account_id
        issue.location = location

        for cls_prop in cls.issue_properties:
            if cls_prop.key not in properties:
                raise ProbatorError(f'Missing required property: {cls_prop.key}')

            value = properties[cls_prop.key]
            prop = IssuePropertyModel()
            prop.issue_id = issue.issue_id
            prop.name = cls_prop.key
            prop.value = value.isoformat() if type(value) == datetime else value
            issue.properties.append(prop)
            db.session.add(prop)

        if auto_add:
            db.session.add(issue)

            if auto_commit:
                db.session.commit()

            return cls.get(issue.issue_id)
        else:
            return cls(issue)

    @classmethod
    def get_all(cls):
        """Returns a list of all issues for a given issue type.

        Returns:
            `list` - list of issue objects
        """
        if cls == BaseIssue:
            raise ProbatorError('get_all on BaseIssue is not supported')

        qry = db.IssueModel.filter(
            IssueModel.issue_type_id == IssueTypeModel.get(cls.issue_type).issue_type_id
        )

        return {res.issue_id: cls(res) for res in qry.all()}

    @staticmethod
    def get_typed_issue(issue):
        """Returns a given issue object as the proper type

        Args:
             issue (BaseIssue, str, int): An issue object

        Returns:
            `issue`
        """
        if type(issue) in (int, str):
            issue = IssueModel.get(issue)

        elif issubclass(issue.__class__, BaseIssue):
            issue = issue.issue

        issue_type = IssueTypeModel.get(issue.issue_type_id).issue_type
        issue_class = get_plugin_by_name(PLUGIN_NAMESPACES['issues'], issue_type)
        if not issue_class:
            raise ProbatorError(f'Unknown issue type: {issue_type}')

        return issue_class(issue)

    @classmethod
    def find(cls, *, limit=25, page=0, accounts=None, locations=None, issue_types=None, properties=None, return_query=False):
        """Search for issues based on the provided filters

        Args:
            limit (`int`): Number of results to return. Default: 25
            page (`int`): Pagination offset for results. Default: 0
            accounts (`list` of `str`): List of accounts to search by
            locations (`list` of `str`): List of locations to search by
            issue_types (`list` of `str`): List of Issue types to return
            properties (`dict`): A `dict` containing property name and value pairs. Values can be either a str or a list
            of strings, in which case a boolean OR search is performed on the values
            return_query (`bool`): Returns the query object prior to adding the limit and offset functions. Allows for
            sub-classes to amend the search feature with extra conditions. The calling function must handle pagination
            on its own

        Returns:
            `list` of `Issue`, `sqlalchemy.orm.Query`
        """
        qry = db.IssueModel.order_by(IssueModel.issue_type_id, IssueModel.issue_id)

        if cls != BaseIssue or issue_types:
            qry = qry.join(IssueTypeModel, IssueModel.issue_type_id == IssueTypeModel.issue_type_id).filter(
                IssueTypeModel.issue_type.in_(issue_types or [cls.issue_type])
            )

        if accounts:
            qry = qry.filter(IssueModel.account_id.in_([Account.get(acct).account_id for acct in accounts]))

        if locations:
            qry = qry.filter(IssueModel.location.in_(locations))

        if properties:
            for prop_name, value in properties.items():
                alias = aliased(IssuePropertyModel)
                qry = qry.join(alias, IssueModel.issue_id == alias.issue_id)
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

        return total, list(map(BaseIssue.get_typed_issue, qry.all()))
    # endregion

    # region Instance methods
    def update_issue(self, properties):
        """Updates the issue object

        The changes will be added to the current db.session but will not be commited. The user will need to perform the
        commit explicitly to save the changes

        Args:
            properties (`dict`): A dictionary of properties to update

        Returns:
            True if issue object was updated, else False
        """
        updated = False

        for prop in self.issue_properties:
            if prop.key in properties:
                updated |= self.set_property(prop.key, properties[prop.key])

        if updated:
            self.issue.updated = datetime.now()

        return updated

    def get_property(self, item):
        """Return a named property for an issue, if available. Will raise an `AttributeError` if the property
        does not exist

        Args:
            item (str): Name of the property to return

        Returns:
            `IssueProperty`
        """
        for prop in self.issue.properties:
            if prop.name == item:
                return prop

        raise AttributeError(item)

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
        else:
            value = value

        try:
            prop = self.get_property(name)
            if prop.value == value:
                return False

            prop.value = value

        except AttributeError:
            prop = IssuePropertyModel()
            prop.issue_id = self.id
            prop.name = name
            prop.value = value

        db.session.add(prop)

        return True

    def delete_property(self, name):
        try:
            self.log.debug(f'Removing property {name} from {self.id}')
            prop = getattr(self, name)
            db.session.delete(prop)
            self.properties.remove(prop)

            return True
        except AttributeError:
            return False

    def save(self, *, auto_commit=True):
        try:
            db.session.add(self.issue)
            if auto_commit:
                db.session.commit()

        except SQLAlchemyError as ex:
            self.log.exception(f'Failed updating issue: {ex}')
            db.session.rollback()

    def delete(self, *, auto_commit=True):
        try:
            db.session.delete(self.issue)
            if auto_commit:
                db.session.commit()

        except SQLAlchemyError:
            self.log.exception(f'Failed deleting issue: {self.id}')
            db.session.rollback()

    def to_json(self):
        return {
            'issueType': self.issue.issue_type_id,
            'issueId': self.id,
            'accountId': self.account_id,
            'account': self.account,
            'location': self.location,
            'created': self.created.isoformat(),
            'updated': self.updated.isoformat(),
            'properties': {to_camelcase(prop.name): prop.value for prop in self.issue.properties}
        }
    # endregion

    # region Object properties
    @property
    def id(self):
        """Return the issue id

        Returns:
            `str`
        """
        return self.issue.issue_id

    @property
    def properties(self):
        """Return all properties for the object

        Returns:
            `list` of :obj:`IssuePropertyModel`
        """
        return self.issue.properties

    @property
    def account_id(self):
        """Returns the ID of the account that owns the resource

        Returns:
            `int`
        """
        return self.issue.account_id

    @property
    def account(self):
        """Return the Account object for the instance

        Returns:
            `Account`
        """
        return self.issue.account

    @property
    def location(self):
        """Returns the location of the resource, or None

        Returns:
            `str`, `None`
        """
        return self.issue.location

    @property
    def created(self):
        """Time the issue was created

        Returns:
            `datetime`
        """
        return self.issue.created

    @property
    def updated(self):
        """Time the issue was last modified

        Returns:
            `datetime`
        """
        return self.issue.updated

    @property
    @abstractmethod
    def issue_type(self):
        """The IssueType of the object"""

    @property
    @abstractmethod
    def issue_name(self):
        """Human friendly name of the issue type"""
    # endregion


class DomainHijackIssue(BaseIssue):
    """Domain Hijacking Issue"""
    issue_type = 'domain_hijacking'
    issue_name = 'Domain Hijacking'
    issue_properties = [
        IssueProp(key='issue_hash', name='Issue Hash', type='string', show=False),
        IssueProp(key='source', name='Source', type='string'),
        IssueProp(key='description', name='Description', type='string', primary=True),
        IssueProp(key='state', name='State', type='string'),
        IssueProp(key='start', name='Start Time', type='datetime'),
        IssueProp(key='end', name='End', type='datetime'),
        IssueProp(key='last_alert', name='Last Alert', type='datetime'),
    ]
