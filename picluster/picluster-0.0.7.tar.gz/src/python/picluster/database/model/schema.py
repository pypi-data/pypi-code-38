from sqlalchemy import Column, Integer, String, DateTime, Enum, Table, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapper
import marshmallow as ma
import enum
import attr
import json
import datetime
import typing
from functools import singledispatch

# from ..db import DataBase


class TaskState(enum.Enum):
    Unknown = 0
    Created = 1
    Pending = 2
    Submitted = 3
    Running = 4
    Completed = 5
    Failed = 6


meta = MetaData()


Base = declarative_base()


class Task(Base):
    __tablename__ = "task"
    id = Column("id", Integer, primary_key=True)
    hash = Column("hash", String)
    workdir = Column("workdir", String)
    input = Column("input", postgresql.ARRAY(item_type=String))
    output = Column("output", postgresql.ARRAY(item_type=String))
    operator = Column("operator", String)
    Column("fn", String)
    Column("state", Enum(TaskState, name="state_enum", metadata=meta))
    Column("create", DateTime(timezone=True))
    Column("submit", DateTime(timezone=True))
    Column("finish", DateTime(timezone=True))
    Column("backend", Integer)
    Column("spec", postgresql.JSONB)

    def __repr__(self):
        return f"<Task(id={self.id}, type={self.type})>"


class Operator(Base):
    __tablename__ = "operator"
    id = Column("id", Integer, primary_key=True)
    type = Column("type", String)
    hash = Column("hash", String)


class OperatorType(Base):
    __tablename__ = "operator_type"
    id = Column("id", Integer, primary_key=True)
    type = Column("type", String)


Operator.type = relationship(
    "OperatorType", order_by=OperatorType.id, back_populates="operator"
)

tasks = Table(
    "tasks",
    meta,
    Column("id", Integer, primary_key=True),
    Column("type"),
    Column("hash", String),
    Column("workdir", String),
    Column("input", postgresql.ARRAY(item_type=String)),
    Column("output", postgresql.ARRAY(item_type=String)),
    Column("script", String),
    Column("fn", String),
    Column("state", Enum(TaskState, name="state_enum", metadata=meta)),
    Column("create", DateTime(timezone=True)),
    Column("submit", DateTime(timezone=True)),
    Column("finish", DateTime(timezone=True)),
    Column("backend", Integer),
    Column("spec", postgresql.JSONB),
)


@attr.s(auto_attribs=True)
class Task:
    id: typing.Optional[int] = None
    hash: typing.Optional[str] = None
    workdir: typing.Optional[str] = None
    input: typing.List[str] = ()
    output: typing.List[str] = ()
    script: typing.Optional[str] = None
    fn: typing.Optional[str] = None
    state: TaskState = TaskState.Created
    create: typing.Optional[datetime.datetime] = None
    submit: typing.Optional[datetime.datetime] = None
    finish: typing.Optional[datetime.datetime] = None
    backend: typing.Optional[str] = None
    spec: typing.Optional[dict] = None


mapper(Task, tasks)


class TaskStateField(ma.fields.Field):
    """
    Serialization/deserialization utils
    """

    def _serialize(self, value, attr, obj):
        if value is None:
            return ""
        return value.name

    def _deserialize(self, value, attr, data):
        if isinstance(value, int):
            value = int(value)
            return TaskState(value)
        elif isinstance(value, str):
            return TaskState[value]


class SpecJson(ma.fields.Field):
    """
    Serialization/deserialization utils for Json
    """

    def _serialize(self, value, attr, obj):
        if value is None:
            return str(dict())
        return json.dumps(value)

    def _deserialize(self, value, attr, data):
        if isinstance(value, str):
            return json.loads(value)
        else:
            raise ValueError(f"Spec requires a json str, got {value}")


class TasksSchema(ma.Schema):
    id = ma.fields.Integer(allow_none=False)
    hash = ma.fields.String(allow_none=True)
    workdir = ma.fields.String(allow_none=True)
    input = ma.fields.List(ma.fields.String())
    output = ma.fields.List(ma.fields.String())
    script = ma.fields.String(allow_none=True)
    fn = ma.fields.String(allow_none=True)
    state = TaskStateField(attribute="state")
    create = ma.fields.DateTime(allow_none=True)
    submit = ma.fields.DateTime(allow_none=True)
    finish = ma.fields.DateTime(allow_none=True)
    backend = ma.fields.String(allow_none=True)
    spec = SpecJson(attribute="spec")


taskSchema = TasksSchema()


# @attr.s
# class TaskSpec:
#     state = attr.ib(default=TaskState.Created.name)
#     create = attr.ib(default=None)
#     submit = attr.ib(default=None)
#     finish = attr.ib(default=None)
#     backend = attr.ib(default="picluster-neobay")
#     scheduler = attr.ib(default="slurm")


resource = Table(
    "resource",
    meta,
    Column("id", Integer, primary_key=True),
    Column("hash", String),
    Column("url", String),
    Column("spec", postgresql.JSONB),
)


@singledispatch
def serialization(t):
    raise NotImplemented


@serialization.register(Task)
def _(t):
    return taskSchema.dump(t)


def deserialization(t):
    if t == "starts":
        pass

    elif set(t.keys()).issubset(set(taskSchema.declared_fields.keys())):
        return Task(**taskSchema.load(t))
