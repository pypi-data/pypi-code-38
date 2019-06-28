# -*- coding: utf-8 -*-


# Uncomment should_run if this is a repeat migration
# def should_run(cursor):
#     # TODO return True if migration should run


def up(cursor):
    cursor.execute("""
CREATE OR REPLACE FUNCTION legacy_mdml_inner (
    mod_ident int,
    recurse bool default False,
    repo text default 'https://legacy.cnx.org/content')
RETURNS XML
IMMUTABLE STRICT
AS
$$
SELECT
  xmlconcat(
      xmlcomment(E' WARNING! The \\'metadata\\' section is read only. Do not edit below. Changes to the metadata section in the source will not be saved. '),

      xmlelement(name "md:repository", legacy_mdml_inner.repo),
      xmlelement(name "md:content-url", legacy_mdml_inner.repo || '/' || m.moduleid||'/'|| m.version),

      xmlelement(name "md:content-id", m.moduleid),
      xmlelement(name "md:title", m.name),

      xmlelement(name "md:version", m.version),
      xmlelement(name "md:created", m.created),
      xmlelement(name "md:revised", m.revised),
      xmlelement(name "md:language", m.language),

      xmlelement(name "md:license", xmlattributes(l.url as "url"),
        l.name),

      xmlcomment(E' For information on license requirements for use or modification, see license url in the above <md:license> element.
           For information on formatting required attribution, see the URL:
             CONTENT_URL/content_info#cnx_cite_header
           where CONTENT_URL is the value provided above in the <md:content-url> element.
      '),

      xmlelement(name "md:actors",
        (SELECT xmlagg(
            xmlelement(name "md:person", xmlattributes(a.personid as "userid"),
              xmlelement(name "md:firstname", a.firstname),
              xmlelement(name "md:surname", a.surname),
              xmlelement(name "md:fullname", a.fullname),
              xmlelement(name "md:email", a.email))
            ) FROM ( SELECT distinct p.* from persons p,
                moduleoptionalroles mor
                right join modules mod on mor.module_ident = mod.module_ident
                WHERE

                (p.personid = any (mod.authors) or
                    p.personid = any (mod.maintainers) or
                    p.personid = any (mod.licensors) or
                    p.personid = any (mor.personids)
                )

                and mod.module_ident = m.module_ident
                  ) as a
          )
      ),

      xmlelement(name "md:roles",
            xmlelement(name "md:role", xmlattributes('author' as "type"), array_to_string(m.authors,' ')),
            xmlelement(name "md:role", xmlattributes('maintainer' as "type"), array_to_string(m.maintainers,' ')),
            xmlelement(name "md:role", xmlattributes('licensor' as "type"), array_to_string(m.licensors,' ')),
            (SELECT xmlelement(name "md:role", xmlattributes(roleparam as "type"), array_to_string(personids, ' ')) FROM
                roles r join moduleoptionalroles mor on r.roleid = mor.roleid WHERE mor.module_ident = m.module_ident
            )
      ),

      xmlelement(name "md:abstract", ab.abstract),

      (SELECT xmlelement(name "md:subjectlist",
              xmlagg( xmlelement(name "md:subject", t.tag))
          )
          FROM moduletags mt join tags t on mt.tagid = t.tagid
          WHERE mt.module_ident = m.module_ident and t.scheme = 'ISKME subject'
          HAVING count(*) > 0
      ),

      (SELECT xmlelement(name "md:keywordlist",
          xmlagg( xmlelement(name "md:keyword", k.word))
          )
          FROM modulekeywords mk join keywords k on mk.keywordid = k.keywordid
          WHERE mk.module_ident = m.module_ident
          HAVING count(*) > 0
      ),
      (SELECT xmlelement(name "md:derived-from",
            xmlattributes(
            legacy_mdml_inner.repo || '/' || p.moduleid||'/'|| p.version as "url"),
            CASE
                WHEN legacy_mdml_inner.recurse = True
                    THEN legacy_mdml_inner(m.parent, legacy_mdml_inner.recurse, legacy_mdml_inner.repo)
                ELSE
                    NULL
            END
        )
            FROM modules p
            WHERE p.module_ident = m.parent
      )
  )
FROM
    modules m
        join licenses l on m.licenseid = l.licenseid
        join abstracts ab on m.abstractid = ab.abstractid
WHERE
    m.module_ident = legacy_mdml_inner.mod_ident

GROUP BY m.module_ident, m.moduleid, m.name, m.version, m.created, m.revised, m.language, l.url, l.name, ab.abstract
$$
LANGUAGE SQL;
    """)

    cursor.execute("""

CREATE OR REPLACE FUNCTION legacy_content(nodeid int,
    repo text default 'https://legacy.cnx.org/content')
RETURNS xml
IMMUTABLE STRICT
LANGUAGE SQL
AS
$$
SELECT
    xmlelement(name "col:content",
    (SELECT xmlagg(
            CASE WHEN c.portal_type in ('Module','CompositeModule')
                THEN legacy_module(c.nodeid, legacy_content.repo)
                WHEN c.portal_type in ('SubCollection','CompositeSubCollection')
                THEN legacy_subcol(c.nodeid, legacy_content.repo)
            END)
            FROM (SELECT nodeid, portal_type FROM trees t JOIN modules m
                ON t.documentid = m.module_ident
                WHERE parent_id = legacy_content.nodeid
                ORDER BY childorder) AS c
            )
        )
$$;
    """)


def down(cursor):
    cursor.execute("""
CREATE OR REPLACE FUNCTION legacy_mdml_inner (
    mod_ident int,
    recurse bool default False,
    repo text default 'https://legacy.cnx.org/content')
RETURNS XML
IMMUTABLE STRICT
AS
$$
SELECT
  xmlconcat(
      xmlcomment(E' WARNING! The \\'metadata\\' section is read only. Do not edit below. Changes to the metadata section in the source will not be saved. '),

      xmlelement(name "md:repository", legacy_mdml_inner.repo),
      xmlelement(name "md:content-url", legacy_mdml_inner.repo || '/' || m.moduleid||'/'|| m.version),

      xmlelement(name "md:content-id", m.moduleid),
      xmlelement(name "md:title", m.name),

      xmlelement(name "md:version", m.version),
      xmlelement(name "md:created", m.created),
      xmlelement(name "md:revised", m.revised),
      xmlelement(name "md:language", m.language),

      xmlelement(name "md:license", xmlattributes(l.url as "url"),
        l.name),

      xmlcomment(E' For information on license requirements for use or modification, see license url in the above <md:license> element.
           For information on formatting required attribution, see the URL:
             CONTENT_URL/content_info#cnx_cite_header
           where CONTENT_URL is the value provided above in the <md:content-url> element.
      '),

      xmlelement(name "md:actors",
        (SELECT xmlagg(
            xmlelement(name "md:person", xmlattributes(a.personid as "userid"),
              xmlelement(name "md:firstname", a.firstname),
              xmlelement(name "md:surname", a.surname),
              xmlelement(name "md:fullname", a.fullname),
              xmlelement(name "md:email", a.email))
            ) FROM ( SELECT distinct p.* from persons p,
                moduleoptionalroles mor
                right join modules mod on mor.module_ident = mod.module_ident
                WHERE

                (p.personid = any (mod.authors) or
                    p.personid = any (mod.maintainers) or
                    p.personid = any (mod.licensors) or
                    p.personid = any (mor.personids)
                )

                and mod.module_ident = m.module_ident
                  ) as a
          )
      ),

      xmlelement(name "md:roles",
            xmlelement(name "md:role", xmlattributes('authors' as "type"), array_to_string(m.authors,' ')),
            xmlelement(name "md:role", xmlattributes('maintainers' as "type"), array_to_string(m.maintainers,' ')),
            xmlelement(name "md:role", xmlattributes('licensors' as "type"), array_to_string(m.licensors,' ')),
            (SELECT xmlelement(name "md:role", xmlattributes(roleparam as "type"), array_to_string(personids, ' ')) FROM
                roles r join moduleoptionalroles mor on r.roleid = mor.roleid WHERE mor.module_ident = m.module_ident
            )
      ),

      xmlelement(name "md:abstract", ab.abstract),

      (SELECT xmlelement(name "md:subjectlist",
              xmlagg( xmlelement(name "md:subject", t.tag))
          )
          FROM moduletags mt join tags t on mt.tagid = t.tagid
          WHERE mt.module_ident = m.module_ident and t.scheme = 'ISKME subject'
          HAVING count(*) > 0
      ),

      (SELECT xmlelement(name "md:keywordlist",
          xmlagg( xmlelement(name "md:keyword", k.word))
          )
          FROM modulekeywords mk join keywords k on mk.keywordid = k.keywordid
          WHERE mk.module_ident = m.module_ident
          HAVING count(*) > 0
      ),
      (SELECT xmlelement(name "md:derived-from",
            xmlattributes(
            legacy_mdml_inner.repo || '/' || p.moduleid||'/'|| p.version as "url"),
            CASE
                WHEN legacy_mdml_inner.recurse = True
                    THEN legacy_mdml_inner(m.parent, legacy_mdml_inner.recurse, legacy_mdml_inner.repo)
                ELSE
                    NULL
            END
        )
            FROM modules p
            WHERE p.module_ident = m.parent
      )
  )
FROM
    modules m
        join licenses l on m.licenseid = l.licenseid
        join abstracts ab on m.abstractid = ab.abstractid
WHERE
    m.module_ident = legacy_mdml_inner.mod_ident

GROUP BY m.module_ident, m.moduleid, m.name, m.version, m.created, m.revised, m.language, l.url, l.name, ab.abstract
$$
LANGUAGE SQL;
    """)

    cursor.execute("""

CREATE OR REPLACE FUNCTION legacy_content(nodeid int,
    repo text default 'https://legacy.cnx.org/content')
RETURNS xml
IMMUTABLE STRICT
LANGUAGE SQL
AS
$$
SELECT
    xmlelement(name "col:content",
    (SELECT xmlagg(
            CASE WHEN portal_type in ('Module','CompositeModule')
                THEN legacy_module(t.nodeid, legacy_content.repo)
                WHEN portal_type in ('SubCollection','CompositeSubCollection')
                THEN legacy_subcol(t.nodeid, legacy_content.repo)
            END)
            FROM trees t join modules m on t.documentid = m.module_ident
                WHERE parent_id = legacy_content.nodeid
            )
        )
$$;
    """)
