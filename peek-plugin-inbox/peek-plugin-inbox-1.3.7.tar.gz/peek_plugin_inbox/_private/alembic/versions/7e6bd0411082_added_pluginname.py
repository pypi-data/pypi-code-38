"""Added pluginName

Peek Plugin Database Migration Script

Revision ID: 7e6bd0411082
Revises: deab93942032
Create Date: 2018-12-03 01:01:08.855992

"""

# revision identifiers, used by Alembic.
revision = '7e6bd0411082'
down_revision = 'deab93942032'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():
    op.execute('TRUNCATE TABLE pl_inbox."Task" CASCADE ')
    op.execute('TRUNCATE TABLE pl_inbox."Activity" CASCADE ')

    op.drop_constraint('Activity_uniqueId_key', 'Activity', schema='pl_inbox', type_='unique')
    op.add_column('Activity', sa.Column('pluginName', sa.String(), nullable=False), schema='pl_inbox')
    op.create_index('idx_Activity_pluginName_uniqueId', 'Activity', ['pluginName', 'uniqueId'], unique=True, schema='pl_inbox')

    op.drop_constraint('Task_uniqueId_key', 'Task', schema='pl_inbox', type_='unique')
    op.add_column('Task', sa.Column('pluginName', sa.String(), nullable=False), schema='pl_inbox')
    op.create_index('idx_Task_pluginName_uniqueId', 'Task', ['pluginName', 'uniqueId'], unique=True, schema='pl_inbox')


def downgrade():
    op.drop_index('idx_Task_pluginName_uniqueId', table_name='Task', schema='pl_inbox')
    op.drop_column('Task', 'pluginName', schema='pl_inbox')
    op.create_unique_constraint('Task_uniqueId_key', 'Task', ['uniqueId'], schema='pl_inbox')

    op.drop_index('idx_Activity_pluginName_uniqueId', table_name='Activity', schema='pl_inbox')
    op.drop_column('Activity', 'pluginName', schema='pl_inbox')
    op.create_unique_constraint('Activity_uniqueId_key', 'Activity', ['uniqueId'], schema='pl_inbox')
