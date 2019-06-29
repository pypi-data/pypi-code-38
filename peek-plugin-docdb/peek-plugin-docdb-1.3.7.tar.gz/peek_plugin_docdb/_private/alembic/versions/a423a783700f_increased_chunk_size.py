"""Increased chunk size

Peek Plugin Database Migration Script

Revision ID: a423a783700f
Revises: c1d2d5475c64
Create Date: 2018-07-04 21:23:03.688758

"""

# revision identifiers, used by Alembic.
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from peek_plugin_docdb._private.worker.tasks._CalcChunkKey import makeChunkKey

revision = 'a423a783700f'
down_revision = 'c1d2d5475c64'
branch_labels = None
depends_on = None

from alembic import op

from sqlalchemy import Column
from sqlalchemy import Integer, String

import logging

logger = logging.getLogger(__name__)

__DeclarativeBase = declarative_base(metadata=MetaData(schema="pl_docdb"))


class __DocDbModelSet(__DeclarativeBase):
    __tablename__ = 'DocDbModelSet'

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String, nullable=False, unique=True)


class __DocDbDocument(__DeclarativeBase):
    __tablename__ = 'DocDbDocument'

    id = Column(Integer, primary_key=True, autoincrement=True)
    modelSetId = Column(Integer)
    key = Column(String)
    chunkKey = Column(String)


def _loadSearchObjects(session):
    FETCH_SIZE = 5000
    lastOffset = 0
    while True:
        rows = (
            session.query(__DocDbDocument)
                .order_by(__DocDbDocument.id)
                .offset(lastOffset)
                .limit(FETCH_SIZE)
                .yield_per(FETCH_SIZE)
                .all()
        )
        if not rows: return
        logger.info("Loading %s-%s for %s",
                    lastOffset, lastOffset+FETCH_SIZE,
                    __DocDbDocument.__name__)
        yield rows
        lastOffset += FETCH_SIZE


def upgrade():
    bind = op.get_bind()
    session = sessionmaker()(bind=bind)

    modelKeysById = {o.id: o.key for o in session.query(__DocDbModelSet)}

    for rows in _loadSearchObjects(session):
        for item in rows:
            item.chunkKey = makeChunkKey(modelKeysById[item.modelSetId], item.key)
        session.commit()
        session.expunge_all()

    session.close()

    op.execute('TRUNCATE TABLE pl_docdb."DocDbEncodedChunkTuple" ')
    op.execute('TRUNCATE TABLE pl_docdb."DocDbChunkQueue" ')

    op.execute('''INSERT INTO pl_docdb."DocDbChunkQueue"
                            ("modelSetId", "chunkKey")
                            SELECT DISTINCT "modelSetId", "chunkKey"
                            FROM pl_docdb."DocDbDocument"
                         ''')


def downgrade():
    raise NotImplementedError("Downgrade not implemented")
