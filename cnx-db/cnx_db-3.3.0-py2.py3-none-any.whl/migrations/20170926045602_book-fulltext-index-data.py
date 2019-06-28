# -*- coding: utf-8 -*-
import time
from datetime import timedelta

from dbmigrator import deferred, logger


def _batcher(seq, size):
    for pos in range(0, len(seq), size):
        yield seq[pos:pos + size]


def should_run(cursor):
    cursor.execute("""
    SELECT module_ident FROM latest_modules lm WHERE
    portal_type = 'Collection' AND
    NOT EXISTS (SELECT 1 FROM modulefti mf
        WHERE lm.module_ident = mf.module_ident)""")
    return cursor.fetchall()


@deferred
def up(cursor):
    """Create fulltext indexes for books"""
    to_index = should_run(cursor)
    num_todo = len(to_index)

    batch_size = 100
    logger.info('Books to index {}'.format(num_todo))
    logger.info('Batch size: {}'.format(batch_size))

    start = time.time()
    guesstimate = 0.01 * num_todo
    guess_complete = guesstimate + start
    logger.info('Completion guess: '
                '"{}" ({})'.format(time.ctime(guess_complete),
                                   timedelta(0, guesstimate)))

    module_idents = tuple([i[0] for i in to_index])
    num_complete = 0
    for batch in _batcher(module_idents, batch_size):

        for module_ident in batch:
            cursor.execute("SELECT insert_book_fti(%(module_ident)s)",
                           {'module_ident': module_ident})

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
    """Delete book fulltext indexes"""
    cursor.execute("""\
            DELETE FROM modulefti mf WHERE EXISTS
                (SELECT 1 FROM modules m
                    WHERE m.module_ident = mf.module_ident)
""")
