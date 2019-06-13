# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#

"""Associate multiple projects with teams

Revision ID: 065
Revises: 064
Create Date: 2019-03-07 11:25:31.308033

"""

# revision identifiers, used by Alembic.
revision = '065'
down_revision = '064'


from alembic import op
import sqlalchemy as sa


def upgrade(active_plugins=None, options=None):
    op.create_table('project_teams',
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], )
    )
    dialect = op.get_bind().engine.dialect
    if dialect.supports_alter:
        op.drop_constraint('projects_ibfk_1', 'projects', type_='foreignkey')
        op.drop_column('projects', 'team_id')


def downgrade(active_plugins=None, options=None):
    dialect = op.get_bind().engine.dialect
    if dialect.supports_alter:
        op.add_column('projects', sa.Column(
            'team_id', sa.Integer(), autoincrement=False, nullable=True))
        op.create_foreign_key(
            'projects_ibfk_1', 'projects', 'teams', ['team_id'], ['id'])
    op.drop_table('project_teams')
