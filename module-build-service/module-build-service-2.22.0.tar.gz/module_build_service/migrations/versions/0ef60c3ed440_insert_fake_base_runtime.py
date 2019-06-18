"""Do nothing.

This used to be an upgrade that inserted a fake base-runtime module, but the
code was removed as a result of
https://pagure.io/fm-orchestrator/pull-request/225

Revision ID: 0ef60c3ed440
Revises: 145347916a56
Create Date: 2016-11-17 15:39:22.984051

"""


# revision identifiers, used by Alembic.
revision = '0ef60c3ed440'
down_revision = '145347916a56'


def upgrade():
    pass

def downgrade():
    pass
