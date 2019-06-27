"""Populate database with atomic data."""
import os
import psycopg2
from atomicdataMB import make_gvalue_table, make_photo_table


def configure_database():
    """Configure database with atomic data.

    Populates gvalues and photoionization rates.
    """
    configfile = os.path.join(os.environ['HOME'], '.nexoclom')
    config = {}
    if os.path.isfile(configfile):
        for line in open(configfile, 'r').readlines():
            key, value = line.split('=')
            config[key.strip()] = value.strip()

    database = config['database']

    con = psycopg2.connect(database=database)
    con.autocommit = True
    make_gvalue_table(con)
    make_photo_table(con)
