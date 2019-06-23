"""enabled postgis

Revision ID: 3aa82a9abe67
Revises: 5ad8b58df646
Create Date: 2015-06-02 22:09:51.824555

"""

# revision identifiers, used by Alembic.
revision = '3aa82a9abe67'
down_revision = '5ad8b58df646'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():

  sql = '''
          -- Enable PostGIS (includes raster)
          CREATE EXTENSION postgis;
          -- Enable Topology
          CREATE EXTENSION postgis_topology;
          -- fuzzy matching needed for Tiger
          CREATE EXTENSION fuzzystrmatch;
          -- Enable US Tiger Geocoder
          CREATE EXTENSION postgis_tiger_geocoder;
          -- commit
          COMMIT;
          '''
  # op.execute(sql)


def downgrade():
    pass
