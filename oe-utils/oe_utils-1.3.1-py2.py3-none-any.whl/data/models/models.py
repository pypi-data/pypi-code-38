from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime
)
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql import func

from oe_utils.data.models.meta import Base


class Wijziging(Base):
    """
    A database table configuration object containing information about the audit of a resource object.

    This object will not create the db table object.
    To create the table insert following code in the alembic migration file

    `alembic revision -m "wijzigingshistoriek"`


    from alembic import op
    import sqlalchemy as sa
    from sqlalchemy.dialects.postgresql import JSON
    from sqlalchemy.sql import func


    def upgrade():
        op.create_table('wijzigingshistoriek',
                        sa.Column('versie', sa.String(), nullable=False),
                        sa.Column('resource_object_id', sa.Integer(), nullable=False),
                        sa.Column('updated_at', sa.DateTime(timezone=True), default=func.now(), nullable=False),
                        sa.Column('updated_by', sa.String(length=255), nullable=False),
                        sa.Column('updated_by_omschrijving', sa.String(length=255), nullable=False),
                        sa.Column('resource_object_json', JSON, nullable=True),
                        sa.Column('actie', sa.String(length=50), nullable=False),
                        sa.PrimaryKeyConstraint('versie', name='wijzigingshistoriek_pk')
        )

        op.execute('GRANT ALL ON wijzigingshistoriek to <user>_dml')


    def downgrade():
        op.drop_table('wijzigingshistoriek')
    """

    __tablename__ = 'wijzigingshistoriek'
    versie = Column(String(64), primary_key=True)
    resource_object_id = Column(Integer, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_by = Column(String(255), default='https://id.erfgoed.net/actoren/501', nullable=False)
    updated_by_omschrijving = Column(String(255), default='Onroerend Erfgoed', nullable=False)
    resource_object_json = Column(MutableDict.as_mutable(JSON()), nullable=True)
    actie = Column(String(50), nullable=False)

