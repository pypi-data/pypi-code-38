
from celery.backends.database.models import ResultModelBase
import sqlalchemy as sa
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.dialects.postgresql import BYTEA

class TaskMasterTable(ResultModelBase):
    """
        Custom Model for task master
    """

    __tablename__ = 'task_master'

    status = sa.Column(sa.Integer, default=0)
    updatetime = sa.Column(sa.DateTime, nullable=True)
    outtime = sa.Column(sa.DateTime, nullable=True)
    intime = sa.Column(sa.DateTime,nullable=True)
    uid = sa.Column(UUID(as_uuid=True),nullable=False,unique=True,primary_key=True)
    worker_id = sa.Column(UUID(as_uuid=True),nullable=True)
    lock =  sa.Column(sa.Boolean,default=0,nullable=True)
    jobtype = sa.Column(sa.Integer, default=0, nullable=True)
    error_id = sa.Column(sa.Integer, default=0,nullable=True)
    meta = sa.Column(sa.JSON, nullable=True)

    def __repr__(self):
        return '<Task {0.uid} state: {0.status}>'.format(self)


class MachineRegistryTable(ResultModelBase):
    """
        Custom Model for Machine registry
    """

    __tablename__ = 'machine_registry'

    intime = sa.Column(sa.DateTime, nullable=True)
    outtime = sa.Column(sa.DateTime, nullable=True)
    worker_id = sa.Column(UUID(as_uuid=True), unique=True,nullable=False,primary_key=True)
    jobtype = sa.Column(sa.Integer, default=0, nullable=True)
    ip_address = sa.Column(INET, nullable=True)
    meta = sa.Column(sa.JSON, nullable=True)
    flag = sa.Column(sa.Boolean,default=0)

    def __repr__(self):
        return '<Machine {0.worker_id} state: {0.jobtype}>'.format(self)


class ResultSetTable(ResultModelBase):
    """
        Custom Model for result master
    """

    __tablename__ = 'result_master'

    uid = sa.Column(UUID(as_uuid=True), unique=True, nullable=False,primary_key=True)
    intime = sa.Column(sa.DateTime, nullable=True)
    outtime = sa.Column(sa.DateTime, nullable=True)
    jobtype = sa.Column(sa.Integer, default=0, nullable=True)
    checksum = sa.Column(sa.Text)
    meta = sa.Column(sa.JSON, nullable=True)
    result_bytes = sa.Column(BYTEA,nullable=True)

    def __repr__(self):
        return '<Result {0.worker_id} state: {0.jobtype}>'.format(self)


class ConfigMasterTable(ResultModelBase):
    """
        Custom Model for Configuration
    """

    __tablename__ = 'config'

    uid = sa.Column(UUID(as_uuid=True), unique=True, nullable=False,primary_key=True)
    intime = sa.Column(sa.DateTime, nullable=True)
    updatedtime = sa.Column(sa.DateTime, nullable=True)
    meta = sa.Column(sa.JSON, nullable=True)

    def __repr__(self):
        return '<Config {0.uid} >'.format(self)

class InitMaterTable(ResultModelBase):
    """
        Custom Model for Configuration
    """
    __tablename__ = 'init_master'

    uid = sa.Column(UUID(as_uuid=True), unique=True, nullable=False, primary_key=True)
    intime = sa.Column(sa.DateTime, nullable=True)
    updatedtime = sa.Column(sa.DateTime, nullable=True)
    meta = sa.Column(sa.JSON, nullable=True)
    jobtype = sa.Column(sa.Integer, default=0, nullable=True)

    def __repr__(self):
        return '<Init {0.uid} >'.format(self)