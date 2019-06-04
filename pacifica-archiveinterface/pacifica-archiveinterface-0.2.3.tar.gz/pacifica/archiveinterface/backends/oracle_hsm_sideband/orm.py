#!/usr/bin/python
# -*- coding: utf-8 -*-
"""ORM for the sideband database."""
# disabling some pylint checks due to this being a database model
# things like too few methods and invalid class attributes like id
# pylint: disable=too-few-public-methods
# pylint: disable=invalid-name

from peewee import MySQLDatabase, CharField
from peewee import IntegerField, BigIntegerField
from peewee import Model, CompositeKey, FloatField
from ...config import get_config

MYSQL_ADDR = get_config().get('hsm_sideband', 'host')
MYSQL_PORT = get_config().get('hsm_sideband', 'port')
MYSQL_USER = get_config().get('hsm_sideband', 'user')
MYSQL_PASS = get_config().get('hsm_sideband', 'password')
MYSQL_SCHEMA = get_config().get('hsm_sideband', 'schema')

DB = MySQLDatabase(MYSQL_SCHEMA,
                   host=MYSQL_ADDR,
                   port=int(MYSQL_PORT),
                   user=MYSQL_USER,
                   passwd=MYSQL_PASS)


class BaseModel(Model):
    """Base class models inherit from.

    Has Connection pieces.
    """

    @classmethod
    def database_connect(cls):
        """Make sure database is connected.

        Dont reopen connection.
        """
        # pylint: disable=no-member
        if cls._meta.database.is_closed():
            cls._meta.database.connect()
        # pylint: enable=no-member

    @classmethod
    def database_close(cls):
        """Close the database connection."""
        # pylint: disable=no-member
        if not cls._meta.database.is_closed():
            cls._meta.database.close()
        # pylint: enable=no-member

    class Meta(object):
        """Meta object containing the database connection."""

        database = DB

    def reload(self):
        """Reload my current state from the DB."""
        newer_self = self.get(self._meta.primary_key == self._get_pk_value())
        for field_name in self._meta.fields.keys():
            val = getattr(newer_self, field_name)
            setattr(self, field_name, val)
        self._dirty.clear()


class SamArchive(BaseModel):
    """Model for sam_archive table in the sideband database."""

    copy = IntegerField()
    create_time = IntegerField(null=True)
    gen = IntegerField()
    ino = IntegerField()
    media_type = CharField()
    offset = IntegerField()
    position = BigIntegerField()
    seq = IntegerField()
    size = BigIntegerField()
    stale = IntegerField(null=True)
    vsn = CharField()

    class Meta(object):
        """Contain index/key info for table."""

        db_table = 'sam_archive'
        indexes = (
            (('ino', 'gen', 'copy', 'seq'), True),
            (('media_type', 'vsn'), False),
        )
        primary_key = CompositeKey('copy', 'gen', 'ino', 'seq')


class SamFile(BaseModel):
    """Model for sam_file table in the sideband database."""

    gen = IntegerField()
    ino = IntegerField()
    name = CharField()
    name_hash = IntegerField()
    p_gen = IntegerField()
    p_ino = IntegerField()

    class Meta(object):
        """Contain index/key info for table."""

        db_table = 'sam_file'
        indexes = (
            (('ino', 'gen'), False),
            (('p_ino', 'p_gen', 'name_hash', 'name'), True),
        )
        primary_key = CompositeKey('name', 'name_hash', 'p_gen', 'p_ino')


class SamInode(BaseModel):
    """Model for sam_inode table in the sideband database."""

    create_time = IntegerField(null=True)
    csum = CharField(null=True)
    gen = IntegerField()
    gid = IntegerField()
    ino = IntegerField()
    modify_time = IntegerField(null=True)
    online = IntegerField()
    size = BigIntegerField(null=True)
    type = IntegerField()
    uid = IntegerField()

    class Meta(object):
        """Contain index/key info for table."""

        db_table = 'sam_inode'
        indexes = (
            (('ino', 'gen'), True),
        )
        primary_key = CompositeKey('gen', 'ino')


class SamPath(BaseModel):
    """Model for sam_path table in the sideband database."""

    gen = IntegerField()
    ino = IntegerField()
    path = CharField(index=True, null=True)

    class Meta(object):
        """Contain index/key info for table."""

        db_table = 'sam_path'
        indexes = (
            (('ino', 'gen'), True),
        )
        primary_key = CompositeKey('gen', 'ino')


class SamVersion(BaseModel):
    """Model for sam_version table in the sideband database."""

    id = IntegerField()
    version = FloatField()

    class Meta(object):
        """Contain index/key info for table."""

        db_table = 'sam_version'
