import os
import psycopg2


def database_connect(database=None, port=None, return_con=True):
    """Wrapper for psycopg2.connect() that determines which database and port to use.

    :return:
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
