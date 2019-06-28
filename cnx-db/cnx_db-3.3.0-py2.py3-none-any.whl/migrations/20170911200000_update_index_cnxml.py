# -*- coding: utf-8 -*-


def up(cursor):
    # Select all the modules that have both index.cnxml and
    # index_auto_generated.cnxml
    cursor.execute("""\
SELECT module_ident, array_agg(fileid),
       array_agg(substring(
           encode(file, 'escape') from 'cnxml-version=.....'))
    FROM module_files NATURAL JOIN files
    WHERE filename IN ('index.cnxml', 'index_auto_generated.cnxml')
    GROUP BY module_ident HAVING count(*) > 1""")
    rows = cursor.fetchall()

    if not rows:
        # nothing to do
        return

    # Create table for rollback
    module_idents = [r[0] for r in rows]
    cursor.execute("""\
CREATE TABLE datamigrations.index_auto_generated AS
    SELECT * FROM module_files
        WHERE module_ident IN %s
          AND filename IN ('index.cnxml', 'index_auto_generated.cnxml')
""", (tuple(module_idents),))

    for row in rows:
        module_ident, fileids, cnxml_versions = row
        if cnxml_versions == [None, None]:
            # Skip files that have no cnxml version
            continue
        elif cnxml_versions[0] is None:
            keep_fileid = fileids[1]
        elif cnxml_versions[1] is None:
            keep_fileid = fileids[0]
        else:
            # Choose the higher fileid if the cnxml versions are the same
            if cmp(*cnxml_versions) == 0:
                keep_fileid = max(fileids)
            elif cmp(*cnxml_versions) == 1:
                keep_fileid = fileids[0]
            else:
                keep_fileid = fileids[1]

        cursor.execute("""\
UPDATE module_files SET fileid = %s
    WHERE filename = 'index.cnxml' AND module_ident = %s""",
                       (keep_fileid, module_ident))
        cursor.execute("""\
DELETE FROM module_files
    WHERE filename = 'index_auto_generated.cnxml'
      AND module_ident = %s""", (module_ident,))


def down(cursor):
    cursor.execute("""\
SELECT 1 FROM information_schema.tables
    WHERE table_name = 'index_auto_generated'
      AND table_schema = 'datamigrations'""")
    if not cursor.fetchall():
        # nothing to rollback
        return
    cursor.execute("""\
UPDATE module_files
    SET fileid = b.fileid
    FROM datamigrations.index_auto_generated b
    WHERE module_files.module_ident = b.module_ident
      AND module_files.fileid != b.fileid
      AND module_files.filename = 'index.cnxml';
INSERT INTO module_files
    SELECT * FROM datamigrations.index_auto_generated b
        WHERE b.filename = 'index_auto_generated.cnxml'
          AND NOT EXISTS
            (SELECT 1
                FROM module_files
                WHERE module_ident = b.module_ident
                  AND filename = 'index_auto_generated.cnxml');
DROP TABLE datamigrations.index_auto_generated""")
