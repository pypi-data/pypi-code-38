import logging
import select
from contextlib import contextmanager
from urllib.parse import (
    parse_qsl,
    urlencode,
    urlparse,
)

from psycopg2.extensions import (
    ISOLATION_LEVEL_AUTOCOMMIT,
    quote_ident,
)
from psycopg2.pool import ThreadedConnectionPool


logger = logging.getLogger(__name__)


def make_pool(url):
    parts = urlparse(url)
    qs = dict(parse_qsl(parts.query))
    minconn = int(qs.pop('minconn', '0'))
    maxconn = int(qs.pop('maxconn', '16'))
    parts = parts._replace(query=urlencode(qs))
    connstring = parts.geturl()
    if ":/?" in connstring or connstring.endswith(':/'):
        # geturl replaces :/// with :/. libpq does not accept that.
        connstring = connstring.replace(':/', ':///')
    return ThreadedConnectionPool(minconn, maxconn, connstring)


@contextmanager
def transaction(pool, listen=None):
    # Manage the connection, transaction and cursor from a connection pool.
    conn = pool.getconn()

    if listen:
        # This is for NOTIFY consistency, according to psycopg2 doc.
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        channel = quote_ident(listen, conn)

    try:
        with conn:  # Wraps in a transaction.
            with conn.cursor() as curs:
                if listen:
                    curs.execute(f"LISTEN {channel};")
                yield curs
    finally:
        pool.putconn(conn)


def wait_for_notifies(conn, timeout=1000):
    rlist, *_ = select.select([conn], [], [], timeout / 1000.)
    conn.poll()
    notifies = conn.notifies[:]
    if notifies:
        logger.debug("Received %d Postgres notifies.", len(conn.notifies))
        conn.notifies[:] = []
    return notifies
