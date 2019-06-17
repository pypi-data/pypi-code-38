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

"""Add a 'security' flag to Teams

Revision ID: 064
Revises: 063
Create Date: 2019-03-04 16:24:44.264120

"""

# revision identifiers, used by Alembic.
revision = '064'
down_revision = '063'


from alembic import op
import sqlalchemy as sa


def upgrade(active_plugins=None, options=None):
    op.add_column('teams', sa.Column('security', sa.Boolean(), nullable=True))


def downgrade(active_plugins=None, options=None):
    op.drop_column('teams', 'security')
