"""Added polyline startKey endKey

Peek Plugin Database Migration Script

Revision ID: 558bc7fc4d36
Revises: 24b83c5e7e31
Create Date: 2017-09-23 14:34:32.435996

"""

# revision identifiers, used by Alembic.
revision = '558bc7fc4d36'
down_revision = '24b83c5e7e31'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():
    op.add_column('DispPolyline', sa.Column('endKey', sa.String(length=50), nullable=True), schema='pl_diagram')
    op.add_column('DispPolyline', sa.Column('startKey', sa.String(length=50), nullable=True), schema='pl_diagram')
    op.create_index('idx_DispPolyline_endKey', 'DispPolyline', ['endKey'], unique=False, schema='pl_diagram')
    op.create_index('idx_DispPolyline_startKey', 'DispPolyline', ['startKey'], unique=False, schema='pl_diagram')



def downgrade():
    op.drop_index('idx_DispPolyline_startKey', table_name='DispPolyline', schema='pl_diagram')
    op.drop_index('idx_DispPolyline_endKey', table_name='DispPolyline', schema='pl_diagram')
    op.drop_column('DispPolyline', 'startKey', schema='pl_diagram')
    op.drop_column('DispPolyline', 'endKey', schema='pl_diagram')
