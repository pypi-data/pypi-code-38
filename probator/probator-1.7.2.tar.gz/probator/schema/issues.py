from probator.schema import Account
from sqlalchemy import Column, String, ForeignKey, func
from sqlalchemy.dialects.mysql import INTEGER as Integer, JSON, DATETIME
from sqlalchemy.orm import foreign, relationship

from probator.database import db, Model
from probator.schema.base import BaseModelMixin

__all__ = ('IssueTypeModel', 'IssuePropertyModel', 'IssueModel')


class IssueTypeModel(Model, BaseModelMixin):
    """Issue type object

    Attributes:
        issue_type_id (int): Unique issue type identifier
        issue_type (str): Issue type name
    """
    __tablename__ = 'issue_types'

    issue_type_id = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    issue_type = Column(String(100), nullable=False, index=True)

    @classmethod
    def get(cls, issue_type):
        """Returns the IssueType object for `issue_type`. If no existing object was found, a new type will
        be created in the database and returned

        Args:
            issue_type (str,int,IssueType): Issue type name, id or class

        Returns:
            :obj:`IssueType`
        """
        if isinstance(issue_type, str):
            obj = getattr(db, cls.__name__).find_one(cls.issue_type == issue_type)

        elif isinstance(issue_type, int):
            obj = getattr(db, cls.__name__).find_one(cls.issue_type_id == issue_type)

        elif isinstance(issue_type, cls):
            return issue_type

        else:
            obj = None

        if not obj:
            obj = cls()
            obj.issue_type = issue_type

            db.session.add(obj)
            db.session.commit()
            db.session.refresh(obj)

        return obj


class IssuePropertyModel(Model, BaseModelMixin):
    """Issue Property object"""
    __tablename__ = 'issue_properties'

    property_id = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    issue_id = Column(
        String(256),
        ForeignKey('issues.issue_id', name='fk_issue_properties_issue_id', ondelete='CASCADE'),
        nullable=False,
        primary_key=True,
        index=True
    )
    name = Column(String(50), nullable=False, index=True)
    value = Column(JSON, nullable=False)

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"{self.__class__.__name__}({self.property_id}, '{self.issue_id}', '{self.name}', '{self.value}')"


class IssueModel(Model, BaseModelMixin):
    """Issue object

    Attributes:
        issue_id (str): Unique Issue identifier
        issue_type (str): :obj:`IssueType` reference
        created (datetime): Issue creation time
        updated (datetime): Last time the issue was updated
        properties (`list` of :obj:`IssueProperty`): List of properties of the issue
    """
    __tablename__ = 'issues'

    issue_id = Column(String(256), primary_key=True)
    issue_type_id = Column(Integer(unsigned=True), index=True)
    account_id = Column(
        Integer(unsigned=True),
        ForeignKey('accounts.account_id', name='fk_issue_account_id', ondelete='CASCADE'),
        nullable=True,
        index=True
    )
    location = Column(String(50), nullable=True, index=True)
    created = Column(DATETIME, nullable=False, server_default=func.now())
    updated = Column(DATETIME, nullable=False, server_default=func.now())
    properties = relationship(
        'IssuePropertyModel',
        lazy='select',
        uselist=True,
        primaryjoin=issue_id == foreign(IssuePropertyModel.issue_id),
        cascade='all, delete-orphan'
    )
    account = relationship(
        'Account',
        lazy='joined',
        uselist=False,
        primaryjoin=account_id == foreign(Account.account_id),
        viewonly=True
    )

    @staticmethod
    def get(issue_id):
        """Return issue by ID

        Args:
            issue_id (str): Unique Issue identifier

        Returns:
            :obj:`Issue`: Returns Issue object if found, else None
        """
        return db.IssueModel.find_one(
            IssueModel.issue_id == issue_id
        )
