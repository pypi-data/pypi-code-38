# -*- coding: utf-8 -*-
import time
from datetime import timedelta
from dbmigrator import deferred, logger


def _batcher(seq, size):
    for pos in range(0, len(seq), size):
        yield seq[pos:pos + size]


def should_run(cursor):
    return len(_need_collxml(cursor)) > 0


def _need_collxml(cursor):
    cursor.execute("""
SELECT module_ident FROM modules m join trees t
  ON m.module_ident = t.documentid
  WHERE portal_type = 'Collection'
          AND t.parent_id is NULL
          AND NOT EXISTS (
            SELECT 1 FROM module_files mf2
              WHERE m.module_ident = mf2.module_ident
                AND filename = 'collection.xml')
  ORDER BY module_ident DESC;
""")
    res = cursor.fetchall()
    return res


def _build_collxml(collid, cursor):
    cursor.execute("""
    WITH collxml as (
        INSERT INTO files (file, media_type)
            SELECT pretty_print(legacy_collxml(%s, True))::text::bytea,
                  'text/xml'
        RETURNING fileid)
    INSERT INTO module_files (module_ident, fileid, filename)
            SELECT %s, fileid, 'collection.xml' from collxml""",
                   (collid, collid))


@deferred
def up(cursor):
    to_build = _need_collxml(cursor)
    num_todo = len(to_build)

    batch_size = 100
    logger.info('collection.xml to generate: {}'.format(num_todo))
    logger.info('Batch size: {}'.format(batch_size))

    start = time.time()
    guesstimate = 0.01 * num_todo
    guess_complete = guesstimate + start
    logger.info('Completion guess: '
                '"{}" ({})'.format(time.ctime(guess_complete),
                                   timedelta(0, guesstimate)))

    num_complete = 0
    for batch in _batcher(to_build, batch_size):
        coll_idents = tuple([i[0] for i in batch])
        logger.debug('coll_idents {}'.format(coll_idents))

        for coll_ident in coll_idents:
            _build_collxml(coll_ident, cursor)

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
    # TODO rollback code
    pass
