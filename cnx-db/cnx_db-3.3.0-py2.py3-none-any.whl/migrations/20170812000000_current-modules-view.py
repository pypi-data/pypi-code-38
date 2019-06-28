# -*- coding: utf-8 -*-


def up(cursor):
    """Replace current_modules with correct logic"""
    cursor.execute("""
DROP VIEW current_modules;
CREATE OR REPLACE VIEW current_modules AS
WITH latest_idents (module_ident) AS (
          SELECT module_ident FROM modules m2 join modulestates ms
                on m2.stateid = ms.stateid
                WHERE m2.major_version = (
                    SELECT max(major_version) FROM modules m3
                        WHERE m2.uuid = m3.uuid
                )
                AND
                (m2.minor_version IS NULL OR
                 m2.minor_version = (
                    SELECT max(minor_version) FROM modules m4
                        WHERE m2.uuid = m4.uuid AND
                        m2.major_version = m4.major_version
                    )
                )
                AND ms.statename = 'current'
        )
SELECT m.* FROM latest_idents li JOIN modules m
ON m.module_ident = li.module_ident;
""")

    cursor.execute("""UPDATE modules SET stateid = 1 WHERE stateid IS NULL""")

    cursor.execute("""CREATE TABLE datamigrations.corrected_latest AS
            SELECT * FROM current_modules cm
                WHERE NOT EXISTS (
                    SELECT 1 FROM latest_modules lm
                        WHERE cm.module_ident = lm.module_ident)""")

    cursor.execute("""CREATE TABLE datamigrations.wrong_latest AS
            SELECT * FROM latest_modules WHERE uuid IN
            (SELECT uuid FROM datamigrations.corrected_latest);
            DELETE FROM latest_modules WHERE uuid IN
            (SELECT uuid FROM datamigrations.corrected_latest);
            INSERT INTO latest_modules
                SELECT * from datamigrations.corrected_latest""")


def down(cursor):
    """Put back broken definition"""
    cursor.execute("""
SELECT m.module_ident,
    m.portal_type,
    m.moduleid,
    m.uuid,
    m.version,
    m.name,
    m.created,
    m.revised,
    m.abstractid,
    m.licenseid,
    m.doctype,
    m.submitter,
    m.submitlog,
    m.stateid,
    m.parent,
    m.language,
    m.authors,
    m.maintainers,
    m.licensors,
    m.parentauthors,
    m.google_analytics,
    m.buylink,
    m.major_version,
    m.minor_version,
    m.print_style
   FROM modules m
  WHERE m.module_ident = (( SELECT max(modules.module_ident) AS max
           FROM modules
          WHERE m.moduleid = modules.moduleid));
""")

    cursor.execute("""DELETE FROM latest_modules WHERE uuid IN
            (SELECT uuid FROM datamigrations.wrong_latest);
            INSERT INTO latest_modules
                SELECT * from datamigrations.wrong_latest;
            DROP TABLE datamigrations.wrong_latest;
            DROP TABLE datamigrations.corrected_latest;""")
