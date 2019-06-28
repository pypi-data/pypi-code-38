import sqlite3
import os
from sqlalchemy import create_engine
from herb.models import *
from sqlalchemy.orm import sessionmaker

from contextlib import contextmanager


Session = sessionmaker()


def init_metadata(loc: str):
    # make matadata store directory
    try:
        os.mkdir(loc)
    except FileExistsError:
        pass

    engine = create_engine('sqlite:///' + os.path.join(str(loc), 'metadata.db'))
    Session.configure(bind=engine)
    Base.metadata.create_all(engine)


@contextmanager
def session_scope():
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


def add_file(session: Session, newfile: File):
    session.add(newfile)

    most_recent_rev = session.query(File) \
        .filter(File.path == newfile.path) \
        .filter(File.last_modified != newfile.last_modified) \
        .order_by(File.last_modified.desc()).first()

    # make sure new file was modified later
    assert most_recent_rev is None or newfile.last_modified > most_recent_rev.last_modified

    # delete outdated versions of file on same device
    session.query(File) \
        .filter(File.outdated == False) \
        .filter(File.path == newfile.path) \
        .filter(File.last_modified != newfile.last_modified) \
        .filter(File.device == newfile.device) \
        .delete()

    # flag versions of file on other devices as outdated
    session.query(File) \
        .filter(File.outdated == False) \
        .filter(File.path == newfile.path) \
        .filter(File.device != newfile.device) \
        .update({'outdated': True}, synchronize_session='fetch')


def add_device(session: Session, newdev: Device):
    session.add(newdev)
    session.commit()


def outdated_files(session: Session, dev: Device):
    return session.query(File) \
        .filter(File.outdated == True) \
        .filter(File.device == dev)


def file_vers(session: Session, path: str):
    return session.query(File) \
        .filter(File.outdated == False) \
        .filter(File.path == path) \
        .order_by(File.last_modified.desc()) \
        .first()