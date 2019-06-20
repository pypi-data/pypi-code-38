"""Add ModuleBuid.ref_build_context.

Revision ID: caeae7a4f537
Revises: 9ca1c166f426
Create Date: 2018-04-18 13:37:40.365129

"""

# revision identifiers, used by Alembic.
revision = 'caeae7a4f537'
down_revision = '9ca1c166f426'

from alembic import op
import sqlalchemy as sa

# Data migration imports
from module_build_service import Modulemd
import hashlib
import json
from collections import OrderedDict


modulebuild = sa.Table(
    'module_builds',
    sa.MetaData(),
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('modulemd', sa.String()),
    sa.Column('build_context', sa.String()),
    sa.Column('runtime_context', sa.String()),
)


def upgrade():
    connection = op.get_bind()
    with op.batch_alter_table('module_builds') as b:
        b.alter_column('build_context', new_column_name='ref_build_context')

    op.add_column('module_builds', sa.Column('build_context', sa.String()))

    # Determine what the contexts should be based on the modulemd
    for build in connection.execute(modulebuild.select()):
        if not build.modulemd:
            continue
        try:
            mmd = Modulemd.ModuleStream.read_string(build.modulemd, True)
            mmd = mmd.upgrade(Modulemd.ModuleStreamVersionEnum.TWO)
        except Exception:
            # If the modulemd isn't parseable then skip this build
            continue

        mbs_xmd = mmd.get_xmd().get('mbs', {})
        # Skip the non-MSE builds, so the "context" will be set default one
        # in models.ModuleBuild.
        if not mbs_xmd.get("mse"):
            continue

        # It's possible this module build was built before MBS filled out xmd or before MBS
        # filled out the requires in xmd
        if 'buildrequires' not in mbs_xmd:
            continue
        # Get the streams of buildrequires and hash it.
        mmd_formatted_buildrequires = {
            dep: info['stream'] for dep, info in mbs_xmd["buildrequires"].items()}
        property_json = json.dumps(OrderedDict(sorted(mmd_formatted_buildrequires.items())))
        context = hashlib.sha1(property_json).hexdigest()

        # Update the database now
        connection.execute(
            modulebuild.update().where(modulebuild.c.id == build.id).values(
                build_context=context))


def downgrade():
    op.drop_column('module_builds', 'build_context')
    with op.batch_alter_table('module_builds') as b:
        b.alter_column('ref_build_context', new_column_name='build_context')
