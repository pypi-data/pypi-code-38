# -*- coding: utf-8 -*-
import os
import time
from datetime import timedelta

import requests
import rhaptos.cnxmlutils
from dbmigrator import deferred, logger


ARCHIVE_DOMAIN = os.getenv('ARCHIVE_DOMAIN')
VARNISH_HOSTS = os.getenv('VARNISH_HOSTS', '').split(',')
VARNISH_PORT = int(os.getenv('VARNISH_PORT', 80))


def _batcher(seq, size):
    for pos in range(0, len(seq), size):
        yield seq[pos:pos + size]


def should_run(cursor, limit='LIMIT 1'):
    version = rhaptos.cnxmlutils.__version__
    version_text = '%data-cnxml-to-html-ver="{}"%'.format(version)
    logger.info('Looking for {}'.format(version_text))
    cursor.execute("""\
WITH index_cnxml_html AS (
    SELECT files.fileid, module_ident, file
        FROM module_files NATURAL JOIN files
        WHERE filename = 'index.cnxml.html'
) SELECT fileid, max(module_ident)
    FROM index_cnxml_html
    WHERE convert_from(file, 'utf-8') NOT LIKE %s
    GROUP BY fileid {}""".format(limit),
                   (version_text,))
    return cursor.fetchall()


def purge_contents_cache():
    if not ARCHIVE_DOMAIN or not VARNISH_HOSTS:
        logger.warn('ARCHIVE_DOMAIN or VARNISH_HOSTS not set, not purging pages')
        return
    for varnish_host in VARNISH_HOSTS:
        resp = requests.request(
            'PURGE_REGEXP', 'http://{}:{}/contents/*'.format(
                varnish_host, VARNISH_PORT),
            headers={'Host': ARCHIVE_DOMAIN})
        if resp.status_code != 200:
            logger.error('Content purge failed:\n{}'.format(resp.text))


@deferred
def up(cursor):
    """Transform all index.cnxml to index.cnxml.html"""
    # Get all the index.cnxml.html that does not have rhaptos.cnxmlutils
    # current version
    to_transform = should_run(cursor, limit='')
    num_todo = len(to_transform)

    batch_size = 100
    logger.info('Pages to transform: {}'.format(num_todo))
    logger.info('Batch size: {}'.format(batch_size))

    start = time.time()
    guesstimate = 0.01 * num_todo
    guess_complete = guesstimate + start
    logger.info('Completion guess: '
                '"{}" ({})'.format(time.ctime(guess_complete),
                                   timedelta(0, guesstimate)))
    module_idents = tuple([i[1] for i in to_transform])

    # Check if datamigrations.index_cnxml_html exists, else create it
    cursor.execute("CREATE SCHEMA IF NOT EXISTS datamigrations")
    cursor.execute("""\
CREATE TABLE IF NOT EXISTS datamigrations.index_cnxml_html
    ( LIKE module_files )""")
    # Store module_files for modules we are going to update
    cursor.execute("""\
INSERT INTO datamigrations.index_cnxml_html
    SELECT * FROM module_files
        WHERE module_ident IN %s
          AND filename = 'index.cnxml.html'
          AND NOT EXISTS (
            SELECT 1 FROM datamigrations.index_cnxml_html b
                WHERE b.module_ident = module_files.module_ident);
UPDATE datamigrations.index_cnxml_html b
    SET fileid = module_files.fileid
    FROM module_files
    WHERE module_files.module_ident = b.module_ident
      AND module_files.filename = b.filename
      AND module_files.fileid != b.fileid
      AND module_files.module_ident IN %s""",
                   (module_idents, module_idents))

    num_complete = 0
    for batch in _batcher(to_transform, batch_size):
        module_idents = tuple([i[1] for i in batch])
        logger.debug('Transform module_idents {}'.format(module_idents))

        for fileid, module_ident in batch:
            cursor.execute("""\
WITH index_cnxml AS (
    SELECT files.fileid, file
        FROM module_files NATURAL JOIN files
        WHERE module_ident = %(module_ident)s
          AND filename = 'index.cnxml'
        LIMIT 1
), transformed AS (
    SELECT html_content(%(module_ident)s) AS content
) INSERT INTO files
    (file, media_type)
    SELECT convert_to(transformed.content, 'utf-8'), 'text/xml'
        FROM index_cnxml, transformed
        WHERE char_length(substring(encode(file, 'escape')
                                    FROM 'cnxml-version=.0.7.')) > 0
          AND NOT EXISTS (
            SELECT 1 FROM files
                WHERE sha1 = sha1(transformed.content))
RETURNING fileid""", {'module_ident': module_ident})
            new_fileid = cursor.fetchall()
            if new_fileid:
                cursor.execute("""\
UPDATE module_files SET fileid = %s
WHERE fileid = %s""", (new_fileid[0][0], fileid))

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

    purge_contents_cache()
    logger.info('Total runtime: {}'.format(timedelta(0, elapsed)))


def down(cursor):
    # Restore module_files save in datamigrations.index_cnxml_html
    cursor.execute("""\
WITH to_delete AS (
    SELECT module_ident, fileid FROM module_files
    WHERE NOT EXISTS (
        SELECT 1 FROM datamigrations.index_cnxml_html b WHERE
            b.fileid = module_files.fileid)
      AND EXISTS (
        SELECT 1 FROM datamigrations.index_cnxml_html b WHERE
            b.module_ident = module_files.module_ident)
      AND filename = 'index.cnxml.html'
), update AS (
UPDATE module_files
    SET fileid = b.fileid
    FROM datamigrations.index_cnxml_html b
    WHERE module_files.module_ident = b.module_ident
      AND module_files.fileid != b.fileid
      AND module_files.filename = 'index.cnxml.html'
)
DELETE FROM files
    WHERE EXISTS (
        SELECT 1 FROM to_delete
        WHERE to_delete.fileid = files.fileid)
        AND NOT EXISTS (
            SELECT 1 FROM module_files
            WHERE module_files.fileid = files.fileid);
DROP TABLE datamigrations.index_cnxml_html""")
    purge_contents_cache()
