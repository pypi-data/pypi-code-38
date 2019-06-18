"""Add ModuleBuild.context

Revision ID: c8e2fc555399
Revises: caeae7a4f537
Create Date: 2018-04-26 22:57:11.398121

"""

# revision identifiers, used by Alembic.
revision = 'c8e2fc555399'
down_revision = 'caeae7a4f537'

from alembic import op
import sqlalchemy as sa

import hashlib


modulebuild = sa.Table(
    'module_builds',
    sa.MetaData(),
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('modulemd', sa.String()),
    sa.Column('build_context', sa.String()),
    sa.Column('runtime_context', sa.String()),
    sa.Column('context', sa.String()),
)


def upgrade():
    connection = op.get_bind()

    op.add_column('module_builds', sa.Column('context', sa.String(), nullable=False, server_default='00000000'))

    for build in connection.execute(modulebuild.select()):
        if build.build_context and build.runtime_context:
            combined_hashes = '{0}:{1}'.format(
                build.build_context, build.runtime_context).encode('utf-8')
            context = hashlib.sha1(combined_hashes).hexdigest()[:8]
            connection.execute(
                modulebuild.update().where(modulebuild.c.id == build.id).values(
                    context=context))

def downgrade():
    with op.batch_alter_table('module_builds') as b:
        b.drop_column('context')
