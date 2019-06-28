# -*- coding: utf-8 -*-


def up(cursor):
    cursor.execute("""
CREATE OR REPLACE VIEW all_current_modules AS
WITH latest_idents(module_ident) AS (
         SELECT m2.module_ident
           FROM modules m2
             JOIN modulestates ms ON m2.stateid = ms.stateid
           WHERE m2.major_version = (
              SELECT max(m3.major_version) AS max
                   FROM modules m3
                  WHERE m2.uuid = m3.uuid
            )
            AND
            (m2.minor_version IS NULL OR
             m2.minor_version = (
                SELECT max(m4.minor_version) AS max
                   FROM modules m4
                  WHERE m2.uuid = m4.uuid AND
                        m2.major_version = m4.major_version
                )
            )
        )
 SELECT m.module_ident,
    m.moduleid,
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
    m.portal_type,
    m.uuid,
    m.major_version,
    m.minor_version,
    m.google_analytics,
    m.buylink,
    m.print_style,
    m.baked,
    m.recipe
   FROM latest_idents li
     JOIN modules m ON m.module_ident = li.module_ident
    """)


def down(cursor):
    cursor.execute("DROP VIEW all_current_modules")
