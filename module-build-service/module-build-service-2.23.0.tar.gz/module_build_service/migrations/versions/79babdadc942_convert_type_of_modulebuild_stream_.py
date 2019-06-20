"""Convert type of ModuleBuild.stream_version to float

Revision ID: 79babdadc942
Revises: 60c6093dde9e
Create Date: 2019-04-19 09:18:40.771633

"""

import math

# revision identifiers, used by Alembic.
revision = '79babdadc942'
down_revision = '60c6093dde9e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    with op.batch_alter_table('module_builds') as b:
        b.alter_column('stream_version', existing_type=sa.Integer, type_=sa.Float)


modulebuild = sa.Table(
    'module_builds',
    sa.MetaData(),
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('stream_version', sa.Float()),
)


def downgrade():
    # For PostgreSQL, changing column type from float to int causes the result
    # to not be the floor value. So, do it manually in advance.
    connection = op.get_bind()
    for build in connection.execute(modulebuild.select()):
        connection.execute(
            modulebuild.update().where(modulebuild.c.id == build.id).values(
                stream_version=math.floor(build.stream_version)))

    with op.batch_alter_table('module_builds') as b:
        b.alter_column('stream_version', existing_type=sa.Float, type_=sa.Integer)
