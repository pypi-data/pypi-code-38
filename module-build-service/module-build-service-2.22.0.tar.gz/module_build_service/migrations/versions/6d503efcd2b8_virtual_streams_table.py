"""Add a table for virtual streams

Revision ID: 6d503efcd2b8
Revises: 79babdadc942
Create Date: 2019-04-23 19:28:52.206109

"""

# revision identifiers, used by Alembic.
revision = '6d503efcd2b8'
down_revision = '79babdadc942'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

# Data migration imports
from module_build_service import Modulemd, conf


Base = declarative_base()

# Define the tables for the data migration
module_builds_to_virtual_streams = sa.Table(
    'module_builds_to_virtual_streams',
    Base.metadata,
    sa.Column('module_build_id', sa.Integer, sa.ForeignKey('module_builds.id')),
    sa.Column('virtual_stream_id', sa.Integer, sa.ForeignKey('virtual_streams.id')),
)


class ModuleBuild(Base):
    __tablename__ = "module_builds"
    id = sa.Column(sa.Integer, primary_key=True)
    modulemd = sa.Column(sa.String, nullable=False)
    name = sa.Column(sa.String, nullable=False)
    virtual_streams = relationship(
        'VirtualStream', secondary=module_builds_to_virtual_streams, back_populates='module_builds'
    )


class VirtualStream(Base):
    __tablename__ = 'virtual_streams'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False, unique=True)
    module_builds = relationship(
        'ModuleBuild', secondary=module_builds_to_virtual_streams, back_populates='virtual_streams'
    )


def upgrade():
    op.create_table(
        'virtual_streams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    op.create_table(
        'module_builds_to_virtual_streams',
        sa.Column('module_build_id', sa.Integer(), nullable=False),
        sa.Column('virtual_stream_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['module_build_id'], ['module_builds.id']),
        sa.ForeignKeyConstraint(['virtual_stream_id'], ['virtual_streams.id']),
        sa.UniqueConstraint(
            'module_build_id', 'virtual_stream_id', name='unique_module_to_virtual_stream'
        ),
    )

    bind = op.get_bind()
    session = sa.orm.Session(bind=bind)
    for build in session.query(ModuleBuild).all():
        # Only process base modules with modulemds set
        if build.name not in conf.base_module_names or not build.modulemd:
            continue

        try:
            mmd = Modulemd.ModuleStream.read_string(build.modulemd, True)
            mmd = mmd.upgrade(Modulemd.ModuleStreamVersionEnum.TWO)
        except Exception:
            # If the modulemd isn't parseable, then skip this build
            continue

        try:
            virtual_streams = mmd.get_xmd()['mbs']['virtual_streams']
        except KeyError:
            # If there are no virtual_streams configured, then just skip this build
            continue

        for virtual_stream in virtual_streams:
            virtual_stream_obj = session.query(VirtualStream).filter_by(name=virtual_stream).first()
            # Create the virtual stream entry if it doesn't exist
            if not virtual_stream_obj:
                virtual_stream_obj = VirtualStream(name=virtual_stream)
                session.add(virtual_stream_obj)
                session.commit()

            if virtual_stream_obj not in build.virtual_streams:
                build.virtual_streams.append(virtual_stream_obj)
                session.add(build)

        session.commit()

    # Always close the transaction
    session.commit()


def downgrade():
    op.drop_table('module_builds_to_virtual_streams')
    op.drop_table('virtual_streams')
