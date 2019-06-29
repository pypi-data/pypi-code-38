"""Increased chunk size

Peek Plugin Database Migration Script

Revision ID: c18d0a2ab678
Revises: 2c6cad1f280e
Create Date: 2018-07-04 21:56:28.319589

"""

# revision identifiers, used by Alembic.

from sqlalchemy import MetaData, Integer, String, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from peek_core_search._private.worker.tasks._CalcChunkKey import \
    makeSearchIndexChunkKey, makeSearchObjectChunkKey

revision = 'c18d0a2ab678'
down_revision = '2c6cad1f280e'
branch_labels = None
depends_on = None

from alembic import op

__DeclarativeBase = declarative_base(metadata=MetaData(schema="core_search"))

import logging
logger = logging.getLogger(__name__)

class __SearchIndex(__DeclarativeBase):
    __tablename__ = 'SearchIndex'

    id = Column(Integer, primary_key=True, autoincrement=True)

    chunkKey = Column(Integer, nullable=False)
    keyword = Column(String, nullable=False)


class __SearchObject(__DeclarativeBase):
    __tablename__ = 'SearchObject'

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String, nullable=False)
    chunkKey = Column(Integer, nullable=False)


def _loadSearchObjects(session, _Declarative):
    FETCH_SIZE = 5000
    lastOffset = 0
    while True:
        rows = (
            session.query(_Declarative)
                .order_by(_Declarative.id)
                .offset(lastOffset)
                .limit(FETCH_SIZE)
                .yield_per(FETCH_SIZE)
                .all()
        )
        if not rows: return
        logger.info("Loading %s-%s for %s",
                    lastOffset, lastOffset+FETCH_SIZE, _Declarative.__name__)
        yield rows
        lastOffset += FETCH_SIZE


def upgrade():
    bind = op.get_bind()
    session = sessionmaker()(bind=bind)

    for rows in _loadSearchObjects(session, __SearchIndex):
        for item in rows:
            item.chunkKey = makeSearchIndexChunkKey(item.keyword)
        session.commit()
        session.expunge_all()

    for rows in _loadSearchObjects(session, __SearchObject):
        for item in rows:
            item.chunkKey = makeSearchObjectChunkKey(item.id)
        session.commit()
        session.expunge_all()

    session.close()

    op.execute(' TRUNCATE TABLE core_search."EncodedSearchIndexChunk" ')
    op.execute(' TRUNCATE TABLE core_search."SearchIndexCompilerQueue" ')

    op.execute('''INSERT INTO core_search."SearchIndexCompilerQueue"
                            ("chunkKey")
                            SELECT DISTINCT "chunkKey"
                            FROM core_search."SearchIndex"
                         ''')

    op.execute(' TRUNCATE TABLE core_search."EncodedSearchObjectChunk" ')
    op.execute(' TRUNCATE TABLE core_search."SearchObjectCompilerQueue" ')

    op.execute('''INSERT INTO core_search."SearchObjectCompilerQueue"
                            ("chunkKey")
                            SELECT DISTINCT "chunkKey"
                            FROM core_search."SearchObject"
                         ''')


def downgrade():
    raise NotImplementedError("Downgrade not implemented")
