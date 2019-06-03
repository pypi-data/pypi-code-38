from datetime import date

ADMIN_USER = 'postgres'
DEFAULT_PORT = 5432
DEFAULT_HOST = '127.0.0.1'


def enter(db_name, options=None):
    return 'psql --host=127.0.0.1 {options} {db_name}'.format(
        db_name=db_name,
        options=' %s ' % options if options else ' ')


def psql(query, host=None, port=None, db_name=None, user=None):
    return 'psql{host}{port}{user}{command}{db_name}'.format(
        host=' --host=%s' % host if host else '',
        port=' --port=%s' % port if port else '',
        user=' --user=%s' % user if user else '',
        command=' --command="%s"' % query,
        db_name=' %s' % db_name if db_name else '')


def psql_from_file(filepath, db_name=None, user=None):
    return 'psql --host=127.0.0.1{user}{db_name} < {filepath}'.format(
        user=' --user=%s' % user if user else '',
        db_name=' %s' % db_name if db_name else '',
        filepath=filepath)


def create_pgpass_line(database, username, password, host='127.0.0.1', port=DEFAULT_PORT):
    return '{host}:{port}:{database}:{username}:{password}'.format(
        host=host,
        database=database,
        port=port,
        username=username,
        password=password)


def backup(db_name, port=DEFAULT_PORT, options=None):
    """
    Backup
    
    --no-owner: exclude permission statements
    --create: include db schema
    """
    return 'pg_dump{host}{port} --no-owner --create{options}{db_name} > {filename}'.format(
        host=' --host=127.0.0.1',
        port=' --port=%s' % port,
        options=' %s ' % options if options else ' ',
        db_name=db_name,
        filename='%s_backup_%s.sql' % (db_name, date.today().isoformat()))


def restore(filepath, db_name=None, options=None):
    return 'pg_restore --host=127.0.0.1{options} {db_name} {filepath}'.format(
        options=' %s' % options if options else '',
        db_name='--dbname=%s' % db_name if db_name else '',
        filepath=filepath)
