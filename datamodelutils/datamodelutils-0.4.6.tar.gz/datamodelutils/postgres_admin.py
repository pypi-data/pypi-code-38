# -*- coding: utf-8 -*-
"""
gdcdatamodel.gdc_postgres_admin
----------------------------------

Module for stateful management of a GDC PostgreSQL installation.
"""
import argparse
import json
import logging
import random
import time
import os

from collections import namedtuple
import sqlalchemy as sa
from sqlalchemy import MetaData, Table
from sqlalchemy.exc import OperationalError

from . import models

from dictionaryutils import DataDictionary, dictionary
from psqlgraph import (
    create_all,
    Node,
    Edge,
    PsqlGraphDriver,
)

logging.basicConfig()
logger = logging.getLogger("gdc_postgres_admin")
logger.setLevel(logging.INFO)

name_root = "table_creator_"
app_name = "{}{}".format(name_root, random.randint(1000, 9999))
no_kill_list = []
BlockingQueryResult = namedtuple('BlockingQueryResult', [
    'blocked_appname',
    'blocked_pid',
    'blocking_appname',
    'blocking_pid',
    'blocking_statement',
])


# See https://wiki.postgresql.org/wiki/Lock_Monitoring
BLOCKING_SQL = """

SELECT
    blocked_activity.application_name  AS blocked_appname,
    blocked_locks.pid                  AS blocked_pid,

    blocking_activity.application_name AS blocking_appname,
    blocking_locks.pid                 AS blocking_pid,

    blocking_activity.query            AS blocking_statement

FROM pg_catalog.pg_locks               blocked_locks

JOIN pg_catalog.pg_stat_activity       blocked_activity
    ON blocked_activity.pid            = blocked_locks.pid

JOIN pg_catalog.pg_locks               blocking_locks
    ON  blocking_locks.locktype        = blocked_locks.locktype
    AND blocking_locks.DATABASE        IS NOT DISTINCT FROM blocked_locks.DATABASE
    AND blocking_locks.relation        IS NOT DISTINCT FROM blocked_locks.relation
    AND blocking_locks.page            IS NOT DISTINCT FROM blocked_locks.page
    AND blocking_locks.tuple           IS NOT DISTINCT FROM blocked_locks.tuple
    AND blocking_locks.virtualxid      IS NOT DISTINCT FROM blocked_locks.virtualxid
    AND blocking_locks.transactionid   IS NOT DISTINCT FROM blocked_locks.transactionid
    AND blocking_locks.classid         IS NOT DISTINCT FROM blocked_locks.classid
    AND blocking_locks.objid           IS NOT DISTINCT FROM blocked_locks.objid
    AND blocking_locks.objsubid        IS NOT DISTINCT FROM blocked_locks.objsubid
    AND blocking_locks.pid             != blocked_locks.pid

JOIN pg_catalog.pg_stat_activity blocking_activity
     ON blocking_activity.pid          = blocking_locks.pid

WHERE NOT blocked_locks.GRANTED
      AND blocked_activity.application_name = :app_name;

"""


GRANT_READ_PRIVS_SQL = """
BEGIN;
GRANT SELECT ON TABLE {table} TO {user};
COMMIT;
"""

GRANT_WRITE_PRIVS_SQL = """
BEGIN;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE {table} TO {user};
COMMIT;
"""

REVOKE_READ_PRIVS_SQL = """
BEGIN;
REVOKE SELECT, INSERT, UPDATE, DELETE ON TABLE {table} FROM {user};
COMMIT;
"""

REVOKE_WRITE_PRIVS_SQL = """
BEGIN;
REVOKE INSERT, UPDATE, DELETE ON TABLE {table} FROM {user};
COMMIT;
"""


def execute(driver, sql, *args, **kwargs):
    statement = sa.sql.text(sql)
    logger.debug(statement)
    return driver.engine.execute(statement, *args, **kwargs)


def get_driver(host, user, password, database):
    return PsqlGraphDriver(
        host=host,
        user=user,
        password=password,
        database=database,
        set_flush_timestamps=True,
        connect_args={"application_name": app_name},
    )


def execute_for_all_graph_tables(driver, sql, *args, **kwargs):
    """Execute a SQL statment that has a python format variable {table}
    to be replaced with the tablename for all Node and Edge tables

    """
    for cls in Node.__subclasses__() + Edge.__subclasses__():
        _kwargs = dict(kwargs, **{'table': cls.__tablename__})
        statement = sql.format(**_kwargs)
        execute(driver, statement)


def grant_read_permissions_to_graph(driver, user):
    execute_for_all_graph_tables(driver, GRANT_READ_PRIVS_SQL, user=user)


def grant_write_permissions_to_graph(driver, user):
    execute_for_all_graph_tables(driver, GRANT_WRITE_PRIVS_SQL, user=user)


def revoke_read_permissions_to_graph(driver, user):
    execute_for_all_graph_tables(driver, REVOKE_READ_PRIVS_SQL, user=user)


def revoke_write_permissions_to_graph(driver, user):
    execute_for_all_graph_tables(driver, REVOKE_WRITE_PRIVS_SQL, user=user)


def migrate_transaction_snapshots(driver):
    """
    Updates to TransactionSnapshot table:
        - change old `id` column to `entity_id`, which is no longer unique or primary
          key
        - add new serial `id` column as primary key
    """
    md = MetaData(bind=driver.engine)
    tablename = models.submission.TransactionSnapshot.__tablename__
    snapshots_table = Table(tablename, md, autoload=True)
    if "entity_id" not in snapshots_table.c:
        # change existing `id` column to `entity_id` which is just node UUID, doesn't
        # have to be unique, should not be used as primary key
        try:
            execute(
                driver,
                "ALTER TABLE {name} DROP CONSTRAINT {name}_pkey;".format(name=tablename),
            )
        except sa.exc.ProgrammingError:
            pass
        execute(
            driver,
            "ALTER TABLE {} RENAME id TO entity_id;".format(tablename),
        )
        execute(
            driver,
            "ALTER TABLE {} ALTER COLUMN entity_id DROP NOT NULL;".format(tablename),
        )
        # make new serial `id` column which *is* used for primary key
        execute(
            driver,
            "ALTER TABLE {} ADD COLUMN id SERIAL PRIMARY KEY;".format(tablename),
        )


def get_schema_hash():
    """Get hash of currently loaded dictionary.

    The suffix number indicates the times that software upgrade introduces new database
    schema changes for the same dictionary. Please increase this number if new logic of
    schema migration is added.
    """
    return str(hash(json.dumps(dictionary.schema) + '2'))


def check_version(driver):
    """
    check if current database schema version matches the version currently
    loaded in memory. False if the database doesn't track version
    """
    if 'root' in dictionary.schema:
        if not (driver.engine.dialect.has_table(driver.engine, 'node_root')):
            return False
        with driver.session_scope():
            root_node = driver.nodes(models.Root).first()
            if not root_node:
                return False
            return get_schema_hash() == root_node.schema_version
    return False


def update_version(driver, session):
    """
    set schema version stored in root node to current version
    """
    if 'root' in dictionary.schema:
        root = driver.nodes(models.Root).first()
        current_version = get_schema_hash()
        logger.info('Set database version to {}'.format(current_version))
        if root:
            root.schema_version = current_version
        else:
            root = models.Root(node_id='root', schema_version=current_version)
        session.merge(root)
        session.flush()


def create_graph_tables(driver, timeout):
    """
    create graph tables
    Args:
        driver: sqlalchemy driver
        timeout (int): timeout for transaction
    Returns:
        None
    """
    def _run(connection):
        create_all(connection)

        # migrate indexes
        exist_index_uniqueness = dict(iter(connection.execute(
            "SELECT i.relname, ix.indisunique "
            "FROM pg_class i, pg_index ix "
            "WHERE i.oid = ix.indexrelid")))
        for cls in Node.__subclasses__() + Edge.__subclasses__():
            for index in cls.__table__.indexes:
                uniq = exist_index_uniqueness.get(index.name, None)
                if uniq is None:
                    # create the missing index
                    index.create(connection)
                elif index.unique != uniq:
                    # recreate indexes whose uniqueness changed
                    index.drop(connection)
                    index.create(connection)

        # https://github.com/uc-cdis/sheepdog/pull/217
        connection.execute(
                "CREATE INDEX IF NOT EXISTS snapshot_transaction_idx "
                "ON {} ( transaction_id )".format(
                    models.submission.TransactionSnapshot.__tablename__))
        connection.execute(
                "CREATE INDEX IF NOT EXISTS document_transaction_idx "
                "ON {} ( transaction_id )".format(
                    models.submission.TransactionDocument.__tablename__))

    _create_tables(driver, _run, timeout)


def create_all_tables(driver, timeout):
    """
    create submission tables
    Args:
        driver: sqlalchemy driver
        timeout (int): timeout for transaction
    Returns:
        None
    """
    _create_tables(
        driver, models.submission.Base.metadata.create_all, timeout)
    create_graph_tables(driver, timeout)


def _create_tables(driver, create_all, timeout):
    """
    create tables

    Args:
        driver: sqlalchemy driver
        create_all (function): create_all function that creates all tables
        timeout (int): timeout for transaction
    Returns:
        None

    """
    logger.info('Creating tables (timeout: %d)', timeout)
    with driver.session_scope() as session:
        connection = session.connection()
        logger.info("Setting lock_timeout to %d", timeout)

        timeout_str = '{}s'.format(int(timeout+1))
        connection.execute("SET LOCAL lock_timeout = %s;", timeout_str)

        create_all(connection)
        update_version(driver, session)


def is_blocked_by_no_kill(blocking):
    for proc in blocking:
        if proc.blocking_appname in no_kill_list:
            print 'Blocked by no-kill process {}, {}: {}'.format(
                proc.blocking_appname, proc.blocking_pid,
                proc.blocking_statement)
            return True
    return False


def lookup_blocking_psql_backend_processes(driver):
    """
    """

    sql_cmd = sa.sql.text(BLOCKING_SQL)
    conn = driver.connect()
    blocking = conn.execute(sql_cmd, app_name=app_name)
    return [BlockingQueryResult(*b) for b in blocking]


def kill_blocking_psql_backend_processes(driver):
    """Query the postgres backend tables for the process that is blocking
    this app, as identified by the `app_name`.

    .. warning:: **THIS COMMAND KILLS OTHER PEOPLES POSTGRES QUERIES.**

    It is sometimes necessary to kill other peoples queries in order
    to gain a write lock on a table to ALTER it for a foreign-key from
    a new table.

    There is a list at the top of this module that specifies which
    processes are 'no-kill'.  There currently are none, but a good
    exmaple of one that you might want to put in there is the
    Elasticsearch build process, since you might not want to kill a 5h
    long process 4h in.

    """

    blockers = lookup_blocking_psql_backend_processes(driver)

    if is_blocked_by_no_kill(blockers):
        logger.warn("Process blocked by a 'no-kill' process. "
                    "Refusing to kill it")
        return

    if not blockers:
        logger.warning("Found %d blocking processes!", len(blockers))
    else:
        logger.info("Found %d blocking processes", len(blockers))

    for result in blockers:
        logger.warning(
            'Killing blocking backend process: name({})\tpid({}): {}'.format(
                result.blocking_appname,
                result.blocking_pid,
                result.blocking_statement)
        )

        # Kill anything in the way, it was deemed of low importance
        sql_cmd = 'SELECT pg_terminate_backend({blocking_pid});'.format(
            blocking_pid=result.blocking_pid
        )
        execute(driver, sql_cmd)


def create_tables_force(driver, delay, retries, only_graph=True):
    """Create the tables and **KILL ANY BLOCKING PROCESSES**.

    This command will spawn a process to create the new tables in
    order to find out which process is blocking us.  If we didn't do
    this concurrently, then the table creation will have disappeared
    by the time we tried to find its blocker in the postgres backend
    tables.

    """

    logger.info('Running table creator named %s', app_name)
    logger.warning('Running with force=True option %s', app_name)
    if only_graph:
        target = create_graph_tables
    else:
        target = create_all_tables

    from multiprocessing import Process
    p = Process(target=create_graph_tables, args=(driver, delay))
    p.start()
    time.sleep(delay)

    if p.is_alive():
        logger.warning('Table creation blocked!')
        kill_blocking_psql_backend_processes(driver)

        #  Wait some time for table creation to proceed
        time.sleep(4)

    if p.is_alive():
        if retries <= 0:
            raise RuntimeError('Max retries exceeded.')

        logger.warning('Table creation failed, retrying.')
        return create_tables_force(driver, delay, retries-1)


def create_tables(driver, delay, retries, only_graph=True):
    """Create the tables but do not kill any blocking processes.

    This command will catch OperationalErrors signalling timeouts from
    the database when the lock was not obtained successfully within
    the `delay` period.

    """

    logger.info('Running table creator named %s', app_name)
    if only_graph:
        target = create_graph_tables
    else:
        target = create_all_tables
    try:
        return target(driver, delay)

    except OperationalError as e:
        if 'timeout' in str(e):
            logger.warning('Attempt timed out')
        else:
            raise

        if retries <= 0:
            raise RuntimeError('Max retries exceeded')

        logger.info(
            'Trying again in {} seconds ({} retries remaining)'
            .format(delay, retries))
        time.sleep(delay)

        create_tables(driver, delay, retries-1, only_graph=only_graph)


def subcommand_create_all(args):
    """
    Create all tables
    """
    return subcommand_create(args, only_graph=False)


def subcommand_create(args, only_graph=True):
    """Idempotently/safely create ALL tables in database that are required
    for the GDC.  This command will not delete/drop any data.

    """

    logger.info("Running subcommand 'create'")
    driver = get_driver(args.host, args.user, args.password, args.database)
    kwargs = dict(
        driver=driver,
        delay=args.delay,
        retries=args.retries,
        only_graph=only_graph
    )

    if args.force:
        return create_tables_force(**kwargs)
    else:
        return create_tables(**kwargs)


def subcommand_grant(args):
    """Grant permissions to a user.

    Argument ``--read`` will grant users read permissions
    Argument ``--write`` will grant users write and READ permissions
    """

    logger.info("Running subcommand 'grant'")
    driver = get_driver(args.host, args.user, args.password, args.database)

    assert args.read or args.write, 'No premission types/users specified.'

    if args.read:
        users_read = [u for u in args.read.split(',') if u]
        for user in users_read:
            grant_read_permissions_to_graph(driver, user)

    if args.write:
        users_write = [u for u in args.write.split(',') if u]
        for user in users_write:
            grant_write_permissions_to_graph(driver, user)


def subcommand_revoke(args):
    """Grant permissions to a user.

    Argument ``--read`` will revoke users' read permissions
    Argument ``--write`` will revoke users' write AND READ permissions
    """

    logger.info("Running subcommand 'revoke'")
    driver = get_driver(args.host, args.user, args.password, args.database)

    if args.read:
        users_read = [u for u in args.read.split(',') if u]
        for user in users_read:
            revoke_read_permissions_to_graph(driver, user)

    if args.write:
        users_write = [u for u in args.write.split(',') if u]
        for user in users_write:
            revoke_write_permissions_to_graph(driver, user)

def default_to_env(env):
    '''
    Helper function used by argparse so that it defaults to environment
    variable, but if it's not found, the arg is required
    Args:
        env (str): environment variable name
    Returns:
        dict passed to parser.add_argument
    '''
    key_from_env = os.environ.get(env)
    if key_from_env is not None:
        return {'default': key_from_env}
    else:
        return {'required': True}


def add_base_args(subparser):
    subparser.add_argument("-H", "--host", type=str, action="store",
                           help="psql-server host",
                           **default_to_env('PG_HOST'))
    subparser.add_argument("-U", "--user", type=str, action="store",
                           help="psql test user",
                           **default_to_env('PG_USER'))
    subparser.add_argument("-D", "--database", type=str, action="store",
                           help="psql test database",
                           **default_to_env('PG_NAME'))
    subparser.add_argument("-P", "--password", type=str, action="store",
                           help="psql test password",
                           **default_to_env('PG_PASS'))
    # dictioanry url is optional, if not given, will use install gdcdictionary
    subparser.add_argument("--dict-url", type=str, action="store",
                           help="url to pull dictionary json",
                           default=os.environ.get('DICTIONARY_URL'))
    return subparser


def add_subcommand_create(subparsers):
    parser = add_base_args(subparsers.add_parser(
        'graph-create',
        help="Create all graph tables based on loaded dictionary"
    ))
    parser.add_argument(
        "--force", action="store_true",
        help="Hard killing blocking processes that are not in the 'no-kill' list."
    )
    parser.add_argument(
        "--delay", type=int, action="store", default=60,
        help="How many seconds to wait for blocking processes to finish before retrying (and hard killing them if used with --force)."
    )
    parser.add_argument(
        "--retries", type=int, action="store", default=10,
        help="If blocked by important process, how many times to retry after waiting `delay` seconds."
    )


def add_subcommand_create_all(subparsers):
    parser = add_base_args(subparsers.add_parser(
        'create-all',
        help="Create all tables"
    ))
    parser.add_argument(
        "--force", action="store_true",
        help="Hard killing blocking processes that are not in the 'no-kill' list."
    )
    parser.add_argument(
        "--delay", type=int, action="store", default=60,
        help="How many seconds to wait for blocking processes to finish before retrying (and hard killing them if used with --force)."
    )
    parser.add_argument(
        "--retries", type=int, action="store", default=10,
        help="If blocked by important process, how many times to retry after waiting `delay` seconds."
    )

def add_subcommand_grant(subparsers):
    parser = add_base_args(subparsers.add_parser(
        'graph-grant',
        help=subcommand_grant.__doc__
    ))
    parser.add_argument(
        "--read", type=str, action="store",
        help="Users to grant read access to (comma separated)."
    )
    parser.add_argument(
        "--write", type=str, action="store",
        help="Users to grant read/write access to (comma separated)."
    )


def add_subcommand_revoke(subparsers):
    parser = add_base_args(subparsers.add_parser(
        'graph-revoke',
        help=subcommand_revoke.__doc__
    ))
    parser.add_argument(
        "--read", type=str, action="store",
        help="Users to revoke read access from (comma separated)."
    )
    parser.add_argument(
        "--write", type=str, action="store",
        help=("Users to revoke write access from (comma separated). "
              "NOTE: The user will still have read privs!!")
    )


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="subcommand")
    add_subcommand_create_all(subparsers)
    add_subcommand_create(subparsers)
    add_subcommand_grant(subparsers)
    add_subcommand_revoke(subparsers)
    return parser

def init_datamodel(args):
    """
    register GDC models
    """
    if args.dict_url:
        d = DataDictionary(url=args.dict_url)
        dictionary.init(d)

    from gdcdatamodel import models as md  # noqa
    models.init(md)

def main(args=None):
    args = args or get_parser().parse_args()

    logger.info("[ HOST     : %-10s ]", args.host)
    logger.info("[ DATABASE : %-10s ]", args.database)
    logger.info("[ USER     : %-10s ]", args.user)
    init_datamodel(args)
    return_value = {
        'graph-create': subcommand_create,
        'create-all': subcommand_create_all,
        'graph-grant': subcommand_grant,
        'graph-revoke': subcommand_revoke,
    }[args.subcommand](args)

    logger.info("Done.")
    return return_value
