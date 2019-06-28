import os, os.path
from .database_connect import database_connect


def configfile():
    """Configure external resources used in the model

    Paths are saved in $HOME/.nexoclom
    * savepath = path where output files are saved
    * datapath = path where MESSENGER data is kept
    * database = name of the postgresql database to use
    """
    # Determne the savepath
    cfile = os.path.join(os.environ['HOME'], '.nexoclom')
    savepath = None
    if os.path.isfile(cfile):
        for line in open(cfile, 'r').readlines():
            key, value = line.split('=')
            if key.strip() == 'savepath':
                savepath = value.strip()
            else:
                pass
    else:
        pass

    if savepath is None:
        savepath = input('Where should outputs be saved: ')
        with open(cfile, 'a') as f:
            f.write(f'savepath = {savepath}\n')

        # Create save directory if necessary
        if not os.path.isdir(savepath):
            try:
                os.makedirs(savepath)
            except:
                assert 0, f'Could not create directory {savepath}'

    # Create the database if necessary
    database, port = database_connect(return_con=False)
    with database_connect(database='postgres') as con:
        cur = con.cursor()
        cur.execute('select datname from pg_database')
        dbs = [r[0] for r in cur.fetchall()]

        if database not in dbs:
            print(f'Creating database {database}')
            cur.execute(f'create database {database}')
        else:
            pass

    return savepath


def set_up_output_tables():
    con = database_connect()
    cur = con.cursor()

    # drop tables if necessary
    nextables = ['outputfile', 'geometry', 'sticking_info', 'forces',
                 'spatialdist', 'speeddist', 'angulardist', 'options',
                 'modelimages', 'uvvsmodels']
    cur.execute('select table_name from information_schema.tables')
    tables = [r[0] for r in cur.fetchall()]

    for tab in nextables:
        if tab in tables:
            cur.execute(f'''DROP table {tab}''')
        else:
            pass

    # create outputfile table
    cur.execute('''CREATE TABLE outputfile (
                       idnum SERIAL PRIMARY KEY,
                       filename text UNIQUE,
                       npackets bigint,
                       totalsource float,
                       creationtime timestamp NOT NULL)''')
    print('Created outputfile table')

    # create geometry table
    cur.execute('''CREATE TABLE geometry (
                       geo_idnum bigint PRIMARY KEY,
                       planet SSObject,
                       StartPoint SSObject,
                       objects SSObject ARRAY,
                       starttime timestamp,
                       phi real ARRAY,
                       subsolarpt point,
                       TAA float)''')
    print('Created geometry table')

    # Create sticking_info table
    cur.execute('''CREATE TABLE sticking_info (
                       st_idnum bigint PRIMARY KEY,
                       stickcoef float,
                       tsurf float,
                       stickfn text,
                       stick_mapfile text,
                       epsilon float,
                       n float,
                       tmin float,
                       emitfn text,
                       accom_mapfile text,
                       accom_factor float)''')
    print('Created sticking_info table')

    # create forces table
    cur.execute('''CREATE TABLE forces (
                       f_idnum bigint PRIMARY KEY,
                       gravity boolean,
                       radpres boolean)''')
    print('Created forces table')

    # create spatialdist table
    cur.execute('''CREATE TABLE spatialdist (
                       spat_idnum bigint PRIMARY KEY,
                       type text,
                       exobase float,
                       use_map boolean,
                       mapfile text,
                       longitude float[2],
                       latitude float[2])''')
    print('Created spatialdist table')

    # create table speeddist
    cur.execute('''CREATE TABLE speeddist (
                       spd_idnum bigint PRIMARY KEY,
                       type text,
                       vprob float,
                       sigma float,
                       U float,
                       alpha float,
                       beta float,
                       temperature float,
                       delv float)''')
    print('Created speeddist table')

    # create table angulardist
    cur.execute('''CREATE TABLE angulardist (
                       ang_idnum bigint PRIMARY KEY,
                       type text,
                       azimuth float[2],
                       altitude float[2],
                       n float)''')
    print('Created angulardist table')

    ## Skipping perturbvel and plasma_info for now

    # create table options
    cur.execute('''CREATE TABLE options (
                       opt_idnum bigint PRIMARY KEY,
                       endtime float,
                       resolution float,
                       at_once boolean,
                       atom text,
                       lifetime float,
                       fullsystem boolean,
                       outeredge float,
                       motion boolean,
                       streamlines boolean,
                       nsteps int)''')
    print('Created options table')

    # Create table for model images
    cur.execute('''CREATE TABLE modelimages (
                       idnum SERIAL PRIMARY KEY,
                       out_idnum bigint,
                       quantity text,
                       origin text,
                       dims float[2],
                       center float[2],
                       width float[2],
                       subobslongitude float,
                       subobslatitude float,
                       mechanism text,
                       wavelength text,
                       filename text)''')
    print('Created modelimages table')

    # # Create table for MESSENGER comparison
    cur.execute('''CREATE TABLE uvvsmodels (
                       idnum SERIAL PRIMARY KEY,
                       out_idnum bigint,
                       quantity text,
                       orbit int,
                       dphi float,
                       mechanism text,
                       wavelength text,
                       filename text)''')
    print('Created uvvsmodels table')
    con.close()


def configure_model(force=False):
    """Ensure the database and configuration file are set up for nexoclom."""
    # Get database name and port
    database, port = database_connect(return_con=False)

    # Verify database is running
    status = os.popen('pg_ctl status').read()
    if 'no server running' in status:
        os.system(f'pg_ctl -D $HOME/.postgres/main/ -p {port}'
                  '-l $HOME/.postgres/logfile start')
    else:
        pass

    # Determine if it is necessary to create the database tables
    nextables = ['outputfile', 'geometry', 'sticking_info', 'forces',
                 'spatialdist', 'speeddist', 'angulardist', 'options',
                 'modelimages', 'uvvsmodels']

    with database_connect() as con:
        cur = con.cursor()
        cur.execute('select table_name from information_schema.tables')
        tables = [r[0] for r in cur.fetchall()]
        there = [m in tables for m in nextables]

    if (False in there) or (force):
        set_up_output_tables()
