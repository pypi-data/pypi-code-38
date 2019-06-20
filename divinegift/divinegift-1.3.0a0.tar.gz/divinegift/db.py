from string import Template
import os
from sqlalchemy import create_engine, MetaData, Table


def get_conn(db_conn: dict):
    """
    Create connection for SQLAlchemy
    :param db_conn: DB connection (user, password, host, port, db_name, dialect)
    :return: Engine, Connection, Metadata
    """
    if db_conn.get('dialect') == 'mssql+pytds':
        from sqlalchemy.dialects import registry
        registry.register("mssql.pytds", "sqlalchemy_pytds.dialect", "MSDialect_pytds")
    if db_conn.get('db_host') and db_conn.get('db_port'):
        connect_str = '{dialect}://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'.format(**db_conn)
    else:
        connect_str = '{dialect}://{db_user}:{db_pass}@{db_name}'.format(**db_conn)
    engine = create_engine(connect_str)
    conn = engine.connect()
    metadata = MetaData()
    return engine, conn, metadata


def get_raw_conn(db_conn: dict):
    """
    Create raw connection for SQLAlchemy
    :param db_conn: DB connection (user, password, host, port, db_name, dialect)
    :return: Connection
    """
    if db_conn.get('dialect') == 'mssql+pytds':
        from sqlalchemy.dialects import registry
        registry.register("mssql.pytds", "sqlalchemy_pytds.dialect", "MSDialect_pytds")
    if db_conn.get('db_host') and db_conn.get('db_port'):
        connect_str = '{dialect}://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'.format(**db_conn)
    else:
        connect_str = '{dialect}://{db_user}:{db_pass}@{db_name}'.format(**db_conn)    
    engine = create_engine(connect_str)
    conn = engine.raw_connection()
    return conn


def close_conn(conn):
    conn.close()


def get_sql(filename: str, encoding: str = 'utf-8'):
    """
    Get sql string from file
    :param filename: File name
    :param encoding: Encoding of file
    :return: String with sql
    """
    file = open(filename, 'r', encoding=encoding)
    sql = file.read()
    file.close()
    return sql


def get_data(sql: str, db_conn: dict, encoding: str = 'utf-8', print_script=False, **kwargs):
    """
    Get raw data from sql data as dict
    :param sql: File with sql which need to execute
    :param db_conn: DB connect creditions
    :param encoding: Encoding of file
    :param kwargs: List with additional data
    :return: Dictionary
    """
    if os.path.exists(sql):
        script_t = Template(get_sql(sql, encoding))
    else:
        script_t = Template(sql)
    script = script_t.safe_substitute(**kwargs)
    if print_script:
        print(script)

    engine, conn, metadata = get_conn(db_conn)
    res = conn.execute(script)
    ress = [dict(row.items()) for row in res]
    close_conn(conn)

    return ress


def get_data_row(sql: str, db_conn: dict, index: int = 0, encoding: str = 'utf-8', **kwargs):
    """
    Get raw data from sql data as dict
    :param sql: File with sql which need to execute
    :param db_conn: DB connect creditions
    :param index: index of returning row
    :param encoding: Encoding of file
    :param kwargs: List with additional data
    :return: Dictionary
    """
    if os.path.exists(sql):
        script_t = Template(get_sql(sql, encoding))
    else:
        script_t = Template(sql)
    script = script_t.safe_substitute(**kwargs)
    #print(script)

    engine, conn, metadata = get_conn(db_conn)
    res = conn.execute(script)
    ress = [dict(row.items()) for row in res]

    try:
        ress = ress[index]
    except:
        ress = None
    close_conn(conn)

    return ress


def run_script(sql: str, db_conn: dict, encoding: str = 'utf-8', **kwargs):
    """
    Run custom script
    :param sql: File with sql which need to execute
    :param db_conn: DB connect creditions
    :param encoding: Encoding of file
    :param kwargs: List with additional data
    :return: None
    """    
    if os.path.exists(sql):
        script_t = Template(get_sql(sql, encoding))
    else:
        script_t = Template(sql)
    script = script_t.safe_substitute(**kwargs)

    engine, conn, metadata = get_conn(db_conn)
    conn.execute(script)
    close_conn(conn)


if __name__ == '__main__':
    pass
