# encoding: utf-8
from __future__ import absolute_import, division, print_function

import re
import sys
import traceback
import types
from collections import defaultdict
from datetime import datetime

from sqlalchemy import MetaData, Table, create_engine, exc
from sqlalchemy.engine import reflection
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.elements import True_

from .errors import InvalidOperationError
from .instance.db_objects import Base, name_to_dbo_field
from .logger import logger
from .utils import hexdigest, parse_timestamp, print_table


def connect_to_db(db_config, *, verbose=False):

    if db_config.connection_string.startswith("sqlite"):
        from sqlite3 import dbapi2 as sqlite

        engine = create_engine(db_config.connection_string, module=sqlite, echo=verbose)
    else:
        # pool_pre_ping: check if connection is valid befor submitting a 
        # command, if not: remove old connections from pool and setup fresh one.
        engine = create_engine(db_config.connection_string, echo=verbose, pool_pre_ping=True)
    try:
        engine.connect()
    except exc.OperationalError as e:
        raise InvalidOperationError(
            "could not connect to {}. Error is {}".format(
                db_config.connection_string, e
            )
        ) from None
    logger().info("connected to db %s", db_config.connection_string)
    return engine


_open_sessions = {}


_existing_handler = sys.excepthook


def print_open_sessions():
    if not _open_sessions:
        return
    print(" DUMP OPEN SESSIONS ".center(80, "-"), file=sys.stderr)
    print(file=sys.stderr)

    for session, (tb, when) in _open_sessions.items():
        print(session, "was created", when, ">",  file=sys.stderr)
        for line in tb:
            print("   ", line.rstrip(), file=sys.stderr)
        print("-" * 80, file=sys.stderr)
        print(file=sys.stderr)


_hook_is_installed = False


def install_excepthook():
    def new_excepthook(*a, **kw):
        print_open_sessions()
        _existing_handler(*a, **kw)

    global _hook_is_installed
    if not _hook_is_installed:
        sys.excepthook = new_excepthook
        _hook_is_installed = True


def _close(self):
    del _open_sessions[self]
    # no super() available here, so:
    self.__class__.close(self)


def create_session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    # attach method to existing object:
    session.close = types.MethodType(_close, session)
    # extract caller, remove this function from the traceback:
    _open_sessions[session] = (traceback.format_stack()[:-1], datetime.now())

    # we yield dbos which usually get invalid (expire) after commit, then attributes can
    # not be accessed any more and eg pretty_printing in tests fails. we disable this:
    session.expire_on_commit = False
    return session


def setup_db(db_config, *, verbose=False, Base=Base):
    """creates tables in database"""
    if check_if_tables_exist(db_config):
        raise InvalidOperationError(
            "use setup_fresh_db, the tables in {!r} already exist".format(
                db_config.connection_string
            )
        )
    engine = connect_to_db(db_config, verbose=verbose)
    Base.metadata.create_all(engine)
    logger().info("created all tables of db {}".format(db_config.connection_string))
    return engine


def check_if_tables_exist(db_config, *, verbose=False, Base=Base):
    engine = connect_to_db(db_config, verbose=verbose)
    declared_names = Base.metadata.tables.keys()
    existing_names = reflection.Inspector.from_engine(engine).get_table_names()
    return bool(set(declared_names) & set(existing_names))


def setup_fresh_db(db_config, *, verbose=False, Base=Base):
    """creates tables in database, deletes already existing data if present"""
    if not check_if_tables_exist(db_config):
        raise InvalidOperationError(
            "use setup_db, the tables in {!r} do not exist".format(
                db_config.connection_string
            )
        )
    engine = connect_to_db(db_config, verbose=verbose)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    logger().info(
        "droped and created all tables of db {}".format(db_config.connection_string)
    )
    return engine


def get_table_names():
    """fetches all table names for Dbo classes declared here"""

    dbo_classes = [
        dbo_class
        for dbo_class in Base._decl_class_registry.values()
        if hasattr(dbo_class, "__tablename__")
    ]
    return sorted(dbo_class.__tablename__ for dbo_class in dbo_classes)


def copy_db(
    db_config_source,
    db_config_destination,
    *,
    delete_existing,
    dont_copy=(),
    verbose=False,
    Base=Base
):
    logger().info(
        "copy tables {} -> {}".format(
            db_config_source.connection_string, db_config_destination.connection_string
        )
    )
    engine_source = connect_to_db(db_config_source, verbose=verbose)
    engine_destination = connect_to_db(db_config_destination, verbose=verbose)

    table_names_source = get_table_names(Base)
    existing_names_destination = reflection.Inspector.from_engine(
        engine_destination
    ).get_table_names()

    if set(table_names_source) & set(existing_names_destination):
        if not delete_existing:
            raise InvalidOperationError(
                "can not copy {} -> {}, some tables already exist on "
                "target db".format(
                    db_config_source.connection_string,
                    db_config_destination.connection_string,
                )
            )
    if delete_existing or not set(table_names_source) & set(existing_names_destination):
        Base.metadata.drop_all(engine_destination)
        Base.metadata.create_all(engine_destination)

    for table_name in sorted(table_names_source):
        if table_name in dont_copy:
            continue
        yield table_name
        _copy_table(
            engine_source, engine_destination, table_name, delete_existing, verbose
        )


def _copy_table(
    engine_source, engine_destination, table_name, delete_existing, verbose
):
    source = sessionmaker(bind=engine_source)()
    destination = sessionmaker(bind=engine_destination)()

    source_meta = MetaData(bind=engine_source)

    logger().info("copy schema of table {}".format(table_name))

    table = Table(table_name, source_meta, autoload=True)

    Base = declarative_base()

    class NewRecord(Base):
        __table__ = table

    columns = table.columns.keys()
    logger().info("copy rows of table {}".format(table_name))
    for record in source.query(table).all():
        data = dict([(str(column), getattr(record, column)) for column in columns])
        destination.merge(NewRecord(**data))

    logger().info("commit changes for table {}".format(table_name))
    destination.commit()


def _dump_table(
    engine, source, source_meta, table_name, indent="", file=sys.stdout, max_rows=None
):
    table = Table(table_name, source_meta, autoload=True)
    columns = table.columns.keys()
    # primary_key = table.primary_key.columns.keys()[0]
    # primary_column = getattr(table, primary_key)
    rows = []
    for record in source.query(table).all():
        row = []
        for column in columns:
            data = getattr(record, column)
            if isinstance(data, bytes):
                data = hexdigest(data)
            row.append(data)
        rows.append(row)

    rows.sort()
    print_table(columns, rows, indent=indent, file=file, max_rows=max_rows)


def dump_db(db_config, table_names=None, file=sys.stdout, max_rows=None):
    engine = connect_to_db(db_config)
    source = sessionmaker(bind=engine)()
    source_meta = MetaData(bind=engine)
    if table_names is None:
        table_names = reflection.Inspector.from_engine(engine).get_table_names()

    for table_name in table_names:
        print("table {}:".format(table_name), file=file)
        print(file=file)
        _dump_table(
            engine,
            source,
            source_meta,
            table_name,
            indent="   ",
            file=file,
            max_rows=max_rows,
        )
        print(file=file)


def get_table_names(Base=Base):
    """fetches all table names for Dbo classes declared here"""

    dbo_classes = [
        dbo_class
        for dbo_class in Base._decl_class_registry.values()
        if hasattr(dbo_class, "__tablename__")
    ]
    return sorted(dbo_class.__tablename__ for dbo_class in dbo_classes)


def filters_to_sqlalchemy_expression(filters, name_to_dbo_field=name_to_dbo_field):

    parser = defaultdict(lambda: str)
    parser["timestamp"] = parse_timestamp

    filters = [f.strip() for filter_ in filters for f in filter_.split(",")]
    expression = True_()
    fields = []
    messages = []
    for filter_ in filters:
        expr_fields = re.split("(==|<=|<|>=|>)", filter_)
        if len(expr_fields) != 3:
            message = (
                "filter {} has not the form FIELD CMP VALUE "
                "with CMP in (==, <=, <, >=, >)".format(filter_)
            )
            messages.append(message)
        else:
            name, cmp_, value = expr_fields
            fields.append((name.strip(), cmp_, value.strip()))

    for (name, cmp_, value), filter_ in zip(fields, filters):
        if name not in name_to_dbo_field:
            message = "filter {} has invalid field {}, allowed are {}".format(
                filter_, name, ", ".join(sorted(name_to_dbo_field.keys()))
            )
            messages.append(message)
        else:
            try:
                parser[name](value)
            except ValueError as e:
                messages.append(str(e))

    if messages:
        return None, messages

    for name, cmp_, value in fields:
        value = value.strip("'").strip('"')
        value = parser[name](value)
        dbo_field = name_to_dbo_field[name]
        if cmp_ == "==":
            expression = expression & (dbo_field == value)
        elif cmp_ == ">=":
            expression = expression & (dbo_field >= value)
        elif cmp_ == "<=":
            expression = expression & (dbo_field <= value)
        elif cmp_ == ">":
            expression = expression & (dbo_field > value)
        elif cmp_ == "<":
            expression = expression & (dbo_field < value)
        else:
            assert False, "should never happen"

    return expression, []
