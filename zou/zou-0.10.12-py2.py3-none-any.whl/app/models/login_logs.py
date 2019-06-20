from sqlalchemy_utils import UUIDType, IPAddressType

from zou.app import db
from zou.app.models.serializer import SerializerMixin
from zou.app.models.base import BaseMixin


class LoginLog(db.Model, BaseMixin, SerializerMixin):
    """
    Table to log all web session logins. The aim is to build a table that
    helps finding suspicious behaviours.
    """
    person_id = db.Column(
        UUIDType(binary=False),
        db.ForeignKey('person.id'),
        nullable=False,
        index=True
    )
    date = db.Column(db.DateTime, nullable=False)
    ip_address = sa.Column(IPAddressType)
