"""Populate the database with the available atomic data.
Currently populates g-values and photoionization rates. If the database does
not exist, it will be created. By default, the tables will only be created if

"""
import os
from .photolossrates import make_photo_table
from .g_values import make_gvalue_table
from .database_connect import database_connect


def initialize_atomicdata(force=False):
    """Populate the database with available atomic data if nececssary.

    **Parameters**

    database
        Name of the PostgeSQL database to use. Default is 'thesolarsystemmb'
        and there should be no reason to change this. This database is used
        for all nexoclom modules.

    force
        By default, the database tables are only created if they do not already
        exist. Set force to True to force the tables to be remade. This would
        be necessary if there are updates to the atomic data.

    **Output**
    No output.
    """
    # Get database name and port
    database, port = database_connect(return_con=False)

    # Verify database is running
    status = os.popen('pg_ctl status').read()
    if 'no server running' in status:
        os.system(f'pg_ctl -D $HOME/.postgres/main/ -p {port}'
                  '-l $HOME/.postgres/logfile start')
    else:
        pass

    # Create database if necessary
    with database_connect(database='postgres') as con:
        cur = con.cursor()
        cur.execute('select datname from pg_database')
        dbs = [r[0] for r in cur.fetchall()]

        if database not in dbs:
            print(f'Creating database {database}')
            cur.execute(f'create database {database}')
        else:
            pass

    # Populate the database tables
    with database_connect() as con:
        cur = con.cursor()
        cur.execute('select table_name from information_schema.tables')
        tables = [r[0] for r in cur.fetchall()]

    if ('gvalues' not in tables) or (force):
        print('Making gvalue table')
        make_gvalue_table()
    else:
        pass

    if ('photorates' not in tables) or (force):
        print('Making photorates table')
        make_photo_table()
    else:
        pass
