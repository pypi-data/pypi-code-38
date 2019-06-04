import argparse
import logging
import pdb
from contextlib import closing, contextmanager
from pkg_resources import get_distribution
from textwrap import dedent

from dramatiq.cli import (
    LOGFORMAT,
    VERBOSITY,
)
from psycopg2 import connect

from .broker import purge


logger = logging.getLogger(__name__)


def entrypoint():
    logging.basicConfig(level=logging.INFO, format=LOGFORMAT)

    try:
        exit(main())
    except (pdb.bdb.BdbQuit, KeyboardInterrupt):
        logger.info("Interrupted.")
    except Exception:
        logger.exception('Unhandled error:')
        logger.error(
            "Please file an issue at "
            "https://gitlab.com/dalibo/dramatiq-pg/issues/new with full log.",
        )
    exit(1)


def main():
    parser = make_argument_parser()
    args = parser.parse_args()

    logging.getLogger().setLevel(VERBOSITY.get(args.verbose, logging.INFO))

    if not hasattr(args, 'command'):
        logger.error("Missing command. See --help for usage.")
        return 1
    return args.command(args)


def make_argument_parser():
    dist = get_distribution('dramatiq-pg')
    parser = argparse.ArgumentParser(
        prog="dramatiq-pg",
        description="Maintainance utility for task-queue in Postgres.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--version", action="version", version=dist.version)
    parser.add_argument(
        "--verbose", "-v", default=0, action="count",
        help="turn on verbose log output",
    )

    subparsers = parser.add_subparsers()

    subparser = subparsers.add_parser('flush')
    subparser.set_defaults(command=flush_command)

    subparser = subparsers.add_parser('purge')
    subparser.set_defaults(command=purge_command)
    subparser.add_argument(
        '--maxage', dest='purge_maxage', default='30 days',
        help=dedent("""\
        Max age of done/rejected message to keep in queue. Format is Postgres
        interval. Default is %(default)r.
        """)
    )

    subparser = subparsers.add_parser('recover')
    subparser.set_defaults(command=recover_command)
    subparser.add_argument(
        '--minage', dest='recover_minage', default='1 min',
        help=dedent("""\
        Max age of consumed message to requere. Format is Postgres
        interval. Default is %(default)r.
        """)
    )

    subparser = subparsers.add_parser('stats')
    subparser.set_defaults(command=stats_command)

    return parser


def flush_command(args):
    with transaction() as curs:
        curs.execute(dedent("""\
        DELETE FROM dramatiq.queue
         WHERE "state" IN ('queued', 'consumed');
        """))
        flushed = curs.rowcount
    logger.info("Flushed %d messages.", flushed)


def purge_command(args):
    with transaction() as curs:
        deleted = purge(curs, args.purge_maxage)
    logger.info("Deleted %d messages.", deleted)


def recover_command(args):
    with transaction() as curs:
        curs.execute(dedent("""\
        UPDATE dramatiq.queue
           SET state = 'queued'
         WHERE state = 'consumed'
           AND mtime < (NOW() AT TIME ZONE 'UTC') - interval %s;
        """), (args.recover_minage,))
        recovered = curs.rowcount
    logger.info("Recovered %s messages.", recovered)


def stats_command(args):
    with transaction() as curs:
        curs.execute(dedent("""\
        SELECT "state", count(1)
          FROM dramatiq.queue
        GROUP BY "state";
        """))
        stats = dict(curs.fetchall())

    for state in 'queued', 'consumed', 'done', 'rejected':
        print(f'{state}: {stats.get(state, 0)}')


@contextmanager
def transaction(connstring=""):
    # Manager for connecting to psycopg2 for a single transaction.
    with closing(connect(connstring)) as conn:
        with conn:
            with conn.cursor() as curs:
                yield curs


if '__main__' == __name__:
    entrypoint()
