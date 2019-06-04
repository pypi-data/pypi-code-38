import os, os.path
import glob
import psycopg2


def messenger_database_setup(force=False, database='thesolarsystemmb'):
    # Verify database is running
    status = os.popen('pg_ctl status').read()
    if 'no server running' in status:
        os.system('pg_ctl -D $HOME/.postgres/main/ -l '
                  '$HOME/.postgres/logfile start')
    else:
        pass
    
    # Read the configuration file
    configfile = os.path.join(os.environ['HOME'], '.nexoclom')
    config = {}
    if os.path.isfile(configfile):
        for line in open(configfile, 'r').readlines():
            key, value = line.split('=')
            config[key.strip()] = value.strip()

        if 'database' in config:
             database = config['database']
        else:
            pass

        if 'datapath' in config:
            datapath = config['datapath']
        else:
            datapath = input('What is the path to the MESSENGER data? ')
            with open(configfile, 'a') as f:
                f.write(f'datapath = {datapath}\n')
    else:
        datapath = input('What is the path to the MESSENGER data? ')
        with open(configfile, 'w') as f:
            f.write(f'datapath = {datapath}\n')
            f.write(f'database = {database}\n')

    # Create MESSENGER database if necessary
    with psycopg2.connect(host='localhost', database='postgres') as con:
        con.autocommit = True
        cur = con.cursor()
        cur.execute('select datname from pg_database')
        dbs = [r[0] for r in cur.fetchall()]

        if database not in dbs:
            print(f'Creating database {database}')
            cur.execute(f'create database {database}')
        else:
            pass

    # Create the MESSENGER tables if necessary
    with psycopg2.connect(database=database) as con:
        con.autocommit = True
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
                os.system(f'psql -d {database} -f {dfile}')
        else:
            pass
