import logging

from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import Boolean, Integer, String, DateTime

from .DeclarativeBase import DeclarativeBase
from vortex.Tuple import Tuple, addTupleType

from peek_core_device._private.PluginNames import deviceTuplePrefix

logger = logging.getLogger(__name__)


@addTupleType
class DeviceInfoTuple(Tuple, DeclarativeBase):
    """ DeviceInfoTuple

    This table stores information about devices.

    """
    __tablename__ = 'DeviceInfo'
    __tupleType__ = deviceTuplePrefix + 'DeviceInfoTuple'

    TYPE_MOBILE_IOS = "mobile-ios"
    TYPE_MOBILE_ANDROUD = "mobile-android"
    TYPE_MOBILE_WEB = "mobile-web"
    TYPE_DESKTOP_WEB = "desktop-web"
    TYPE_DESKTOP_WINDOWS = "desktop-windows"
    TYPE_DESKTOP_MACOS = "desktop-macos"

    id = Column(Integer, primary_key=True)
    description = Column(String(100), nullable=False, unique=True)
    deviceId = Column(String(50), nullable=False, unique=True)
    deviceType = Column(String(20), nullable=False)
    deviceToken = Column(String(50), nullable=False, unique=True)
    appVersion = Column(String(15), nullable=False)
    updateVersion = Column(String(15))  # Null means it hasn't updated
    lastOnline = Column(DateTime(True))
    lastUpdateCheck = Column(DateTime(True))
    createdDate = Column(DateTime(True), nullable=False)
    isOnline = Column(Boolean, nullable=False, server_default='0')
    isEnrolled = Column(Boolean, nullable=False, server_default='0')
