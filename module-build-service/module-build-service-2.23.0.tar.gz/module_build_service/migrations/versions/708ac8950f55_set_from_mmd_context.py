"""Sets the modulemd's context as the source of truth

Revision ID: 708ac8950f55
Revises: c8e2fc555399
Create Date: 2018-05-29 13:49:43.629831

"""

# revision identifiers, used by Alembic.
revision = '708ac8950f55'
down_revision = 'c8e2fc555399'

from alembic import op
import sqlalchemy as sa

# Data migration imports
from module_build_service import Modulemd
import hashlib


modulebuild = sa.Table(
    'module_builds',
    sa.MetaData(),
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('build_context', sa.String()),
    sa.Column('runtime_context', sa.String()),
    sa.Column('modulemd', sa.String()),
    sa.Column('context', sa.String()),
)


def upgrade():
    connection = op.get_bind()

    for build in connection.execute(modulebuild.select()):
        if not build.modulemd:
            continue
        try:
            mmd = Modulemd.ModuleStream.read_string(build.modulemd, True)
            mmd = mmd.upgrade(Modulemd.ModuleStreamVersionEnum.TWO)
        except Exception:
            # If the modulemd isn't parseable then skip this build
            continue

        # If the context in the modulemd doesn't match the context in the DB,
        # then set the context in the DB to the one in the modulemd
        mmd_context = mmd.get_context()
        if mmd_context and mmd_context != build.context:
            connection.execute(
                modulebuild.update().where(modulebuild.c.id == build.id).values(
                    context=mmd_context))


def downgrade():
    connection = op.get_bind()

    for build in connection.execute(modulebuild.select()):
        if build.build_context and build.runtime_context:
            combined_hashes = '{0}:{1}'.format(
                build.build_context, build.runtime_context).encode('utf-8')
            context = hashlib.sha1(combined_hashes).hexdigest()[:8]
            connection.execute(
                modulebuild.update().where(modulebuild.c.id == build.id).values(context=context))
