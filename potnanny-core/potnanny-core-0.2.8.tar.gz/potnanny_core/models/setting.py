import os
import re
import json
import hashlib
from potnanny_core.database import db_session
from potnanny_core.schemas.setting import (PollingIntervalSchema,
    TemperatureDisplaySchema, PrimitiveWirelessSettingSchema,
    VesyncAccountSchema)
from potnanny_core.models.keychain import Keychain


class SettingBase(object):
    """
    Base Class to manage named Settings in Keychain.
    Not very useful on its own. Subclasses must define their own KEY_NAME
    and marshmallow SCHEMA.
    """

    KEY_NAME = None
    SCHEMA = None

    @classmethod
    def _get_obj(cls):
        """
        Private Class method. Get db object that matches class KEY_NAME
        """

        if not cls.KEY_NAME:
            raise ValueError("No defined KEY_NAME")

        return Keychain.query.filter_by(name=cls.KEY_NAME).first()

    @classmethod
    def get(cls):
        """Class method. Get our object data."""

        return cls._get_obj()

    @classmethod
    def delete(cls):
        """Class method. Delete setting object from db."""

        obj = cls._get_obj()
        if obj:
            db_session.delete(obj)
            db_session.commit()

    @classmethod
    def set(cls, *args, **kwargs):
        """Class method. Set object data."""

        if not cls.SCHEMA:
            raise ValueError("No Schema defined for class")

        serialized, errors = cls.SCHEMA().load(kwargs)
        if errors:
            raise ValueError(errors)

        obj = cls._get_obj()
        if not obj:
            obj = Keychain(name=cls.KEY_NAME, data=json.dumps(serialized))
            db_session.add(obj)
        else:
            obj.data = json.dumps(serialized)

        db_session.commit()
        return serialized


class PollingInterval(SettingBase):
    """Class to manage app polling interval stored in Keychain."""

    KEY_NAME = 'polling_interval'
    SCHEMA = PollingIntervalSchema

    @classmethod
    def get(cls):
        obj = cls._get_obj()
        if not obj:
            return cls.set(minutes=5)

        return json.loads(obj.data)


class TemperatureDisplay(SettingBase):
    """Class for user preference of temperature display (celsius|fahrenheit)."""

    KEY_NAME = 'temperature_display'
    SCHEMA = TemperatureDisplaySchema

    @classmethod
    def get(cls):
        obj = cls._get_obj()
        if not obj:
            return cls.set(display='celsius')

        return json.loads(obj.data)


class PrimitiveWirelessSetting(SettingBase):
    """Class to manage primitive rf wireless settings stored in Keychain."""

    KEY_NAME = 'primitive_wireless'
    SCHEMA = PrimitiveWirelessSettingSchema

    @classmethod
    def create_with_defaults(cls):
        defaults = {
            'transmit_pin': 0,
            'receive_pin': 2,
            'pulse_width': 180,
            'rf_send': '/usr/local/bin/rf_send',
            'rf_scan': '/usr/local/bin/rf_scan',
        }
        return cls.set(**defaults)


class VesyncAccount(SettingBase):
    """Class to manage VeSync account data stored in Keychain."""

    KEY_NAME = 'vesync_account'
    SCHEMA = VesyncAccountSchema

    @classmethod
    def set(cls, *args, **kwargs):
        if not cls.SCHEMA:
            raise ValueError("No Schema defined for class")

        serialized, errors = cls.SCHEMA().load(kwargs)
        if errors:
            raise ValueError(errors)

        obj = cls._get_obj()
        if not obj:
            serialized['password'] = hashlib.md5(serialized['password'].encode('utf-8')).hexdigest()
            obj = Keychain(name=cls.KEY_NAME, data=json.dumps(serialized))
            db_session.add(obj)
        else:
            if serialized['password'] != json.loads(obj.data)['password']:
                # changed! password sent back does not match old one.
                # new password must be hashed before saving.
                serialized['password'] = hashlib.md5(serialized['password'].encode('utf-8')).hexdigest()

            obj.data = json.dumps(serialized)

        db_session.commit()
        return serialized
