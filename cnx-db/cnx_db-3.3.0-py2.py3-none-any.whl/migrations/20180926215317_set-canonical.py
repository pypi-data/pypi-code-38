# -*- coding: utf-8 -*-
import time
from datetime import timedelta

from dbmigrator import deferred, logger


def _batcher(seq, size):
    for pos in range(0, len(seq), size):
        yield seq[pos:pos + size]


def should_run(cursor, limit='limit 1'):
    cursor.execute("SELECT module_ident FROM modules WHERE canonical is null"
                   " AND portal_type in ('Module', 'CompositeModule')"
                   " {}".format(limit))
    return cursor.fetchall()


@deferred
def up(cursor):
    """Add canonical for all that do not have it"""
    to_update = should_run(cursor, limit='')
    num_todo = len(to_update)

    batch_size = 1000
    logger.info('Pages to update: {}'.format(num_todo))
    logger.info('Batch size: {}'.format(batch_size))

    start = time.time()
    guesstimate = 0.01 * num_todo
    guess_complete = guesstimate + start
    logger.info('Completion guess: '
                '"{}" ({})'.format(time.ctime(guess_complete),
                                   timedelta(0, guesstimate)))

    num_complete = 0
    for batch in _batcher(to_update, batch_size):
        module_idents = tuple([i[0] for i in batch])

        cursor.execute("""UPDATE modules
            SET canonical = default_canonical_book(uuid)
            WHERE module_ident IN %s""", (module_idents,))

        cursor.connection.commit()
        num_complete += len(batch)
        percent_comp = num_complete * 100.0 / num_todo
        elapsed = time.time() - start
        remaining_est = elapsed * (num_todo - num_complete) / num_complete
        est_complete = start + elapsed + remaining_est
        logger.info('{:.1f}% complete '
                    'est: "{}" ({})'.format(percent_comp,
                                            time.ctime(est_complete),
                                            timedelta(0, remaining_est)))

    logger.info('Total runtime: {}'.format(timedelta(0, elapsed)))


def down(cursor):
    cursor.execute("UPDATE modules set canonical = NULL")
