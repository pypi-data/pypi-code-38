"""removed string field sizes

Peek Plugin Database Migration Script

Revision ID: 1b17ef0cca17
Revises: f76791d27f6d
Create Date: 2019-02-15 22:54:38.653794

"""

# revision identifiers, used by Alembic.
revision = '1b17ef0cca17'
down_revision = 'f76791d27f6d'
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.alter_column('DispBase', 'dispJson', type_=sa.String(), nullable=True,
                    schema='pl_diagram')
    op.alter_column('DispBase', 'locationJson', type_=sa.String(), nullable=True,
                    schema='pl_diagram')
    op.alter_column('DispBase', 'key', type_=sa.String(), nullable=True,
                    schema='pl_diagram')
    op.alter_column('DispBase', 'dataJson', type_=sa.String(), nullable=True,
                    schema='pl_diagram')

    op.alter_column('DispGroup', 'name', type_=sa.String(), nullable=False,
                    schema='pl_diagram')
    op.alter_column('DispText', 'geomJson', type_=sa.String(), nullable=False,
                    schema='pl_diagram')
    op.alter_column('DispPolygon', 'geomJson', type_=sa.String(), nullable=False,
                    schema='pl_diagram')
    op.alter_column('DispPolyline', 'geomJson', type_=sa.String(), nullable=False,
                    schema='pl_diagram')
    op.alter_column('DispEllipse', 'geomJson', type_=sa.String(), nullable=False,
                    schema='pl_diagram')
    op.alter_column('DispGroupPointer', 'geomJson', type_=sa.String(), nullable=False,
                    schema='pl_diagram')


def downgrade():
    op.alter_column('DispBase', 'dispJson', type_=sa.String(length=200000), nullable=True,
                    schema='pl_diagram')
    op.alter_column('DispBase', 'locationJson', type_=sa.String(length=120), nullable=True,
                    schema='pl_diagram')
    op.alter_column('DispBase', 'key', type_=sa.String(length=50), nullable=True,
                    schema='pl_diagram')
    op.alter_column('DispBase', 'dataJson', type_=sa.String(length=500), nullable=True,
                    schema='pl_diagram')

    op.alter_column('DispGroup', 'name', type_=sa.String(length=50), nullable=False,
                    schema='pl_diagram')
    op.alter_column('DispText', 'geomJson', type_=sa.String(length=2000), nullable=False,
                    schema='pl_diagram')
    op.alter_column('DispPolygon', 'geomJson', type_=sa.String(length=200000),
                    nullable=False, schema='pl_diagram')
    op.alter_column('DispPolyline', 'geomJson', type_=sa.String(length=200000),
                    nullable=False, schema='pl_diagram')
    op.alter_column('DispEllipse', 'geomJson', type_=sa.String(length=2000),
                    nullable=False, schema='pl_diagram')
    op.alter_column('DispGroupPointer', 'geomJson', type_=sa.String(length=2000),
                    nullable=False, schema='pl_diagram')
