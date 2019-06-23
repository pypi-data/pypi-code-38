"""Payload Envelope

Peek Plugin Database Migration Script

Revision ID: deab93942032
Revises: 2119b6aab2c5
Create Date: 2018-05-06 13:20:16.345837

"""

# revision identifiers, used by Alembic.
revision = 'deab93942032'
down_revision = '2119b6aab2c5'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2
from sqlalchemy.dialects import postgresql

def upgrade():
    op.alter_column('Task', 'onCompletedPayload',new_column_name='onCompletedPayloadEnvelope', schema='pl_inbox')
    op.alter_column('Task', 'onDeletedPayload',new_column_name='onDeletedPayloadEnvelope', schema='pl_inbox')
    op.alter_column('Task', 'onDeliveredPayload',new_column_name='onDeliveredPayloadEnvelope', schema='pl_inbox')
    op.alter_column('Task', 'onDialogConfirmPayload',new_column_name='onDialogConfirmPayloadEnvelope', schema='pl_inbox')
    op.alter_column('TaskAction', 'onActionPayload',new_column_name='onActionPayloadEnvelope', schema='pl_inbox')


def downgrade():
    op.alter_column('Task', 'onCompletedPayloadEnvelope',new_column_name='onCompletedPayload', schema='pl_inbox')
    op.alter_column('Task', 'onDeletedPayloadEnvelope',new_column_name='onDeletedPayload', schema='pl_inbox')
    op.alter_column('Task', 'onDeliveredPayloadEnvelope',new_column_name='onDeliveredPayload', schema='pl_inbox')
    op.alter_column('Task', 'onDialogConfirmPayloadEnvelope',new_column_name='onDialogConfirmPayload', schema='pl_inbox')
    op.alter_column('TaskAction', 'onActionPayloadEnvelope',new_column_name='onActionPayload', schema='pl_inbox')
