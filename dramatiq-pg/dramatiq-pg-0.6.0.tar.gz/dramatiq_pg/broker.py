import json
import logging
import select
from random import randint
from textwrap import dedent

from dramatiq.broker import (
    Broker,
    Consumer,
    MessageProxy,
)
from dramatiq.common import current_millis, dq_name
from dramatiq.message import Message
from dramatiq.results import Results
from psycopg2.extensions import (
    ISOLATION_LEVEL_AUTOCOMMIT,
    Notify,
    quote_ident,
)
from psycopg2.extras import Json

from .utils import make_pool, transaction
from .results import PostgresBackend


logger = logging.getLogger(__name__)


def purge(curs, max_age='30 days'):
    # Delete old messages. Returns deleted messages.

    curs.execute(dedent("""\
    DELETE FROM dramatiq.queue
     WHERE "state" IN ('done', 'rejected')
       AND mtime <= (NOW() - interval %s);
    """), (max_age,))
    return curs.rowcount


class PostgresBroker(Broker):
    def __init__(self, *, pool=None, url="", results=True, **kw):
        super(PostgresBroker, self).__init__(**kw)
        if pool and url:
            raise ValueError("You can't set both pool and URL!")

        if not pool:
            self.pool = make_pool(url)
        else:
            # Receive a pool object to have an I/O less __init__.
            self.pool = pool
        self.backend = None
        if results:
            self.backend = PostgresBackend(pool=self.pool)
            self.add_middleware(Results(backend=self.backend))

    def consume(self, queue_name, prefetch=1, timeout=30000):
        return PostgresConsumer(
            pool=self.pool,
            queue_name=queue_name,
            prefetch=prefetch,
            timeout=timeout,
        )

    def declare_queue(self, queue_name):
        if queue_name not in self.queues:
            self.emit_before("declare_queue", queue_name)
            self.queues[queue_name] = True
            # Actually do nothing in Postgres since all queues are stored in
            # the same table.
            self.emit_after("declare_queue", queue_name)

    def enqueue(self, message, *, delay=None):
        if delay:
            message = message.copy(queue_name=dq_name(message.queue_name))
            message.options['eta'] = current_millis() + delay

        q = message.queue_name
        insert = (dedent("""\
        WITH enqueued AS (
          INSERT INTO dramatiq.queue (queue_name, message_id, "state", message)
          VALUES (%s, %s, 'queued', %s)
          ON CONFLICT (message_id)
            DO UPDATE SET "state" = 'queued', message = EXCLUDED.message
          RETURNING queue_name, message
        )
        SELECT
          pg_notify('dramatiq.' || queue_name || '.enqueue', message::text)
        FROM enqueued;
        """), (q, message.message_id, Json(message.asdict())))

        with transaction(self.pool) as curs:
            logger.debug("Upserting %s in queue %s.", message.message_id, q)
            curs.execute(*insert)
        return message


class PostgresConsumer(Consumer):
    def __init__(self, *, pool, queue_name, timeout, **kw):
        self.listen_conn = None
        self.notifies = []
        self.pool = pool
        self.queue_name = queue_name
        self.timeout = timeout // 1000

    def __next__(self):
        # First, open connexion and fetch missed notifies from table.
        if self.listen_conn is None:
            self.listen_conn = self.start_listening()
            # We may have received a notify between LISTEN and SELECT of
            # pending messages. That's not a problem because we are able to
            # skip spurious notifies.
            self.notifies = self.fetch_pending_notifies()
            logger.debug(
                "Found %s pending messages in queue %s.",
                len(self.notifies), self.queue_name)

        if not self.notifies:
            # Then, fetch notifies from Pg connexion.
            self.poll_for_notify()

        # If we have some notifies, loop to find one todo.
        while self.notifies:
            notify = self.notifies.pop(0)
            payload = json.loads(notify.payload)
            message = Message(**payload)
            mid = message.message_id
            if self.consume_one(message):
                return MessageProxy(message)
            else:
                logger.debug("Message %s already consumed. Skipping.", mid)

        # We have nothing to do, let's see if the queue needs some cleaning.
        self.auto_purge()

    def ack(self, message):
        with transaction(self.pool) as curs:
            channel = f"dramatiq.{message.queue_name}.ack"
            payload = Json(message.asdict())
            logger.debug(
                "Notifying %s for ACK %s.", channel, message.message_id)
            # dramatiq always ack a message, even if it has been requeued by
            # the Retries middleware. Thus, only update message in state
            # `consumed`.
            curs.execute(dedent("""\
            WITH updated AS (
              UPDATE dramatiq.queue
                 SET "state" = 'done', message = %s
               WHERE message_id = %s AND state = 'consumed'
              RETURNING message
            )
            SELECT
              pg_notify(%s, message::text)
            FROM updated;
            """), (payload, message.message_id, channel))

    def auto_purge(self):
        # Automatically purge messages every 100k iteration. Dramatiq defaults
        # to 1s. This mean about 1 purge for 28h idle.
        if randint(0, 100_000):
            return
        logger.debug("Randomly triggering garbage collector.")
        with self.listen_conn.cursor() as curs:
            deleted = purge(curs)
        logger.info("Purged %d messages in all queues.", deleted)

    def close(self):
        if self.listen_conn:
            self.pool.putconn(self.listen_conn)
            self.listen_conn = None

    def consume_one(self, message):
        # Race to process this message.
        with transaction(self.pool) as curs:
            curs.execute(dedent("""\
            UPDATE dramatiq.queue
               SET "state" = 'consumed',
                   mtime = (NOW() AT TIME ZONE 'UTC')
             WHERE message_id = %s AND "state" = 'queued';
            """), (message.message_id,))
            # If no row was updated, this mean another worker has consumed it.
            return 1 == curs.rowcount

    def nack(self, message):
        with transaction(self.pool) as curs:
            # Use the same channel as ack. Actually means done.
            channel = f"dramatiq.{message.queue_name}.ack"
            logger.debug(
                "Notifying %s for NACK %s.", channel, message.message_id)
            payload = Json(message.asdict())
            curs.execute(dedent("""\
            WITH updated AS (
              UPDATE dramatiq.queue
                 SET "state" = 'rejected', message = %s
               WHERE message_id = %s AND state <> 'rejected'
              RETURNING message
            )
            SELECT
              pg_notify(%s, message::text)
            FROM updated;
            """), (payload, message.message_id, channel))

    def fetch_pending_notifies(self):
        with self.listen_conn.cursor() as curs:
            curs.execute(dedent("""\
            SELECT message::text
              FROM dramatiq.queue
             WHERE state = 'queued' AND queue_name IN %s;
            """), ((self.queue_name, dq_name(self.queue_name)),))
            return [
                Notify(pid=0, channel=None, payload=r[0])
                for r in curs
            ]

    def requeue(self, messages):
        messages = list(messages)
        if not len(messages):
            return

        logger.debug("Batch update of messages for requeue.")
        with self.listen_conn.cursor() as curs:
            curs.execute(dedent("""\
            UPDATE dramatiq.queue
               SET state = 'queued'
            WHERE message_id IN %s;
            """), (tuple(m.message_id for m in messages),))

    def start_listening(self):
        # Opens listening connection with proper configuration.

        conn = self.pool.getconn()
        # This is for NOTIFY consistency, according to psycopg2 doc.
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        channel = quote_ident(f"dramatiq.{self.queue_name}.enqueue", conn)
        dq = dq_name(self.queue_name)
        dchannel = quote_ident(f"dramatiq.{dq}.enqueue", conn)
        with conn.cursor() as curs:
            logger.debug(
                "Listening on channels %s, %s.", channel, dchannel)
            curs.execute(f"LISTEN {channel}; LISTEN {dchannel};")
        return conn

    def poll_for_notify(self):
        rlist, *_ = select.select([self.listen_conn], [], [], self.timeout)
        self.listen_conn.poll()
        if self.listen_conn.notifies:
            self.notifies += self.listen_conn.notifies
            logger.debug(
                "Received %d Postgres notifies for queue %s.",
                len(self.listen_conn.notifies),
                self.queue_name,
            )
            self.listen_conn.notifies[:] = []
