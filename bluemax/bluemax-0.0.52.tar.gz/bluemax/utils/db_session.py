from contextlib import contextmanager
from tornado.options import options
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import reflection
from sqlalchemy.sql.schema import MetaData, ForeignKeyConstraint, Table
from sqlalchemy.sql.ddl import DropConstraint, DropTable
import logging


class db:
    Session = None
    Engine = None
    url = None


Sessions = {}


def setup_db(base_name="default", db_url=None):
    logging.info("setUp(%r)", base_name)
    global Sessions
    if Sessions.get(base_name) is None:
        _db = db()
        _db.url = db_url if db_url else getattr(options, f"{base_name}_db_url")
        logging.info("connecting to db: %s", _db.url)
        _db.Session, _db.Engine = connect(_db.url)
        Sessions[base_name] = _db
    session = Sessions[base_name]
    return session.Engine, session.Session


def connect(db_url, echo=False):
    Engine = create_engine(db_url, echo=echo)
    Session = sessionmaker(bind=Engine)
    return Session, Engine


@contextmanager
def session(Session):
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def session_scope(base_name="default", db_url=None):
    """Provide a transactional scope around a series of operations."""
    global Sessions
    if Sessions.get(base_name) is None:
        setup_db(base_name, db_url)
    return session(Sessions[base_name].Session)


def drop_all(session):
    """
        drops current schema
    """
    inspector = reflection.Inspector.from_engine(session.bind)

    # gather all data first before dropping anything.
    # some DBs lock after things have been dropped in
    # a transaction.

    metadata = MetaData()

    tbs = []
    all_fks = []

    for table_name in inspector.get_table_names():
        fks = []
        for fk in inspector.get_foreign_keys(table_name):
            if not fk["name"]:
                continue
            fks.append(ForeignKeyConstraint((), (), name=fk["name"]))
        t = Table(table_name, metadata, *fks)
        tbs.append(t)
        all_fks.extend(fks)

    for fkc in all_fks:
        session.execute(DropConstraint(fkc))

    for table in tbs:
        session.execute(DropTable(table))

    session.commit()
