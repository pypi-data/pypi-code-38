"""Add an association table for module buildrequires

Revision ID: 526fb7d445f7
Revises: 9d5e6938588f
Create Date: 2018-10-11 12:46:36.060460

"""

# revision identifiers, used by Alembic.
revision = '526fb7d445f7'
down_revision = '9d5e6938588f'

from alembic import op
import sqlalchemy as sa

# Data migration imports
from module_build_service import Modulemd, conf
from module_build_service.models import ModuleBuild

# Data migration tables
mb = sa.Table(
    'module_builds',
    sa.MetaData(),
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('name', sa.String()),
    sa.Column('stream', sa.String()),
    sa.Column('version', sa.String()),
    sa.Column('context', sa.String()),
    sa.Column('stream_version', sa.Integer()),
    sa.Column('modulemd', sa.String())
)

mb_to_mbr = sa.Table(
    'module_builds_to_module_buildrequires',
    sa.MetaData(),
    sa.Column('module_id', sa.Integer(), nullable=False),
    sa.Column('module_buildrequire_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['module_id'], ['module_builds.id']),
    sa.ForeignKeyConstraint(['module_buildrequire_id'], ['module_builds.id']),
    sa.UniqueConstraint('module_id', 'module_buildrequire_id')
)


def upgrade():
    with op.batch_alter_table('module_builds', schema=None) as batch_op:
        batch_op.add_column(sa.Column('stream_version', sa.Integer()))

    op.create_table(
        'module_builds_to_module_buildrequires',
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.Column('module_buildrequire_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['module_buildrequire_id'], ['module_builds.id']),
        sa.ForeignKeyConstraint(['module_id'], ['module_builds.id']),
        sa.UniqueConstraint('module_id', 'module_buildrequire_id')
    )

    connection = op.get_bind()
    # Create all the base module buildrequire entries
    for build in connection.execute(mb.select()):
        if not build.modulemd:
            # If the modulemd is empty, skip this build
            continue

        brs = None
        try:
            mmd = Modulemd.ModuleStream.read_string(build.modulemd, True)
            mmd = mmd.upgrade(Modulemd.ModuleStreamVersionEnum.TWO)
            brs = mmd.get_xmd()['mbs']['buildrequires']
        except Exception:
            # If the modulemd isn't parseable then skip this build
            continue

        for base_module in conf.base_module_names:
            base_module_dict = brs.get(base_module)
            if not base_module_dict:
                # If this base module isn't a buildrequire, continue to see if the next one is
                continue

            select = mb.select()\
                .where(mb.c.name == base_module)\
                .where(mb.c.stream == base_module_dict['stream'])\
                .where(mb.c.version == base_module_dict['version'])\
                .where(mb.c.context == base_module_dict.get('context'))
            br = connection.execute(select).fetchone()
            if not br:
                # If the buildrequire isn't in the datbase, then skip it
                continue

            connection.execute(mb_to_mbr.insert().values(
                module_id=build.id,
                module_buildrequire_id=br.id
            ))

    for base_module in conf.base_module_names:
        for build in connection.execute(mb.select().where(mb.c.name == base_module)):
            stream_version = ModuleBuild.get_stream_version(build.stream)
            if not stream_version:
                # If a stream version isn't parseable, then skip it
                continue
            connection.execute(mb.update().where(mb.c.id == build.id).values(
                stream_version=stream_version))


def downgrade():
    with op.batch_alter_table('module_builds', schema=None) as batch_op:
        batch_op.drop_column(sa.Column('stream_version'))
    op.drop_table('module_builds_to_module_buildrequires')
