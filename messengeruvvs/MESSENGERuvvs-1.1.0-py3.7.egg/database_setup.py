import os, os.path
import glob
import psycopg2


def database_connect(database=None, port=None, return_con=True):
    """Wrapper for psycopg2.connect() that determines which database and port to use.

    :param database: Default = None to use value from config file
    :param port: Default = None to use value from config file
    :param return_con: False to return database name and port instead of connection
    :return: Database connection with autocommit = True unless return_con = False
    """
    configfile = os.path.join(os.environ['HOME'], '.nexoclom')
    config = {}
    if os.path.isfile(configfile):
        for line in open(configfile, 'r').readlines():
            key, value = line.split('=')
            config[key.strip()] = value.strip()

        if (database is None) and ('database' in config):
            database = config['database']
        else:
            pass

        if (port is None) and ('port' in config):
            port = int(config['port'])
        else:
            pass
    else:
        pass

    if database is None:
        database = 'thesolarsystemmb'
    else:
        pass

    if port is None:
        port = 5432
    else:
        pass

    if return_con:
        con = psycopg2.connect(database=database, port=port)
        con.autocommit = True

        return con
    else:
        return database, port

def messenger_database_setup(force=False):
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

    if datapath is None:
        datapath = input('What is the path to the MESSENGER data? ')
        with open(configfile, 'a') as f:
            f.write(f'datapath = {datapath}\n')
    else:
        pass

    # Get database name and port
    database, port = database_connect(return_con=False)

    # Verify database is running
    status = os.popen('pg_ctl status').read()
    if 'no server running' in status:
        os.system(f'pg_ctl -D $HOME/.postgres/main/ -p {port}'
                  '-l $HOME/.postgres/logfile start')
    else:
        pass

    # Create MESSENGER database if necessary
    with database_connect(database='postgres') as con:
        cur = con.cursor()
        cur.execute('select datname from pg_database')
        dbs = [r[0] for r in cur.fetchall()]

        if database not in dbs:
            print(f'Creating database {database}')
            cur.execute(f'create database {database}')
        else:
            pass

    # Create the MESSENGER tables if necessary
    with database_connect() as con:
        cur = con.cursor()
        cur.execute('select table_name from information_schema.tables')
        tables = [r[0] for r in cur.fetchall()]

        mestables = ['capointing', 'cauvvsdata', 'mesmercyear', 'mgpointing',
                     'mguvvsdata', 'napointing', 'nauvvsdata']
        there = [m in tables for m in mestables]

        if (False in there) or (force):
            # Delete any tables that may exist
            for mestab in mestables:
                if mestab in tables:
                    cur.execute(f'drop table {mestab}')
                else:
                    pass

            # Import the dumped tables
            datafiles = glob.glob(datapath+'/UVVS*sql')
            for dfile in datafiles:
                print(f'Loading {os.path.basename(dfile)}')
                os.system(f'psql -d {database} -p {port} -f {dfile}')
        else:
            pass
