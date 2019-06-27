"""Backup data in MESSENGER database tables."""
import os
from .database_setup import database_connect


def databasebackups(database='thesolarsystemmb', port=5432):
    # Read in current config file if it exists
    configfile = os.path.join(os.environ['HOME'], '.nexoclom')
    datapath = None
    if os.path.isfile(configfile):
        for line in open(configfile, 'r').readlines():
            key, value = line.split('=')
            if key.strip() == 'datapath':
                datapath = value.strip()
            else:
                pass
    else:
        pass
    assert datapath is not None, 'Undefined datapath.'

    # Get database name and port
    database, port = database_connect(return_con=False)

    mestables = ['capointing', 'cauvvsdata', 'mesmercyear', 'mgpointing',
              'mguvvsdata', 'napointing', 'nauvvsdata']

    for table in mestables:
        print(f'Backing up {table}')
        savef = os.path.join(datapath, f'UVVS_{table}.sql')
        os.system(f"pg_dump -p port -t {table} {database} > {savef}")

if __name__ == '__main__':
    databasebackups()
