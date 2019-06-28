# -*- coding: utf-8 -*-
from dbmigrator import super_user


def up(cursor):

    cursor.execute("""
-- Build MDML from modules table and friends "recurse" param fills in derived-from parent metadata elements
-- Note that legacy_mdml_inner returns an xml fragment with an assumed xmlns alias of md for
-- http://cnx.rice.edu/mdml, rather than a rooted document, because of how metadata is incorporated into the
-- collxml (the metadata root is in collxml NS, not mdml NS) as well as the derived-from (takes child md tags,
-- not a full metadata tag) legacy_mdml() and legacy_collxml() define those namespaces

CREATE OR REPLACE FUNCTION legacy_mdml_inner (
    mod_ident int,
    recurse bool default False,
    repo text default 'https://legacy.cnx.org/content')
RETURNS XML as
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

CREATE OR REPLACE FUNCTION legacy_mdml (
    mod_ident int,
    recurse bool default False,
    repo text default 'https://legacy.cnx.org/content')
RETURNS XML as
$$
SELECT  xmlelement(name "md:metadata", xmlattributes('http://cnx.rice.edu/mdml' as "xmlns:md"),
        legacy_mdml_inner(legacy_mdml.mod_ident, legacy_mdml.recurse, legacy_mdml.repo)
    )
$$
LANGUAGE SQL;

-- Now for COLLXML, parsed from trees and modules tables - the reverse of shred, basically
-- Each of the sub-tree functions takes a tree nodeid as primary parameter
-- this creates a leaf 'module' element

CREATE OR REPLACE FUNCTION legacy_module(nodeid int,
    repo text default 'https://legacy.cnx.org/content')
RETURNS xml
LANGUAGE SQL
AS
$$
SELECT xmlelement(name "col:module",
    xmlattributes(m.moduleid as "document",
                  ( CASE WHEN t.latest THEN 'latest'
                    ELSE m.version END ) as "version",
                  legacy_module.repo as "repository",
                  m.version as "cnxorg:version-at-this-collection-version"),
    xmlelement(name "md:title", COALESCE (t.title, m.name)
        )
    )

    FROM trees t JOIN modules m on t.documentid = module_ident
    WHERE t.nodeid = legacy_module.nodeid
$$;

-- to recurse, we need the content tag function and the subcol tag function to refer to each other, so a
-- stub function with the correct type signature, here, to be replaced w/ functional code below

CREATE OR REPLACE FUNCTION legacy_content(nodeid int,
    repo text default 'https://legacy.cnx.org/content')
RETURNS xml
LANGUAGE SQL
AS
$$
SELECT NULL::xml -- STUB redefined below due to mutual recursion w/ legacy_subcol
$$;


CREATE OR REPLACE FUNCTION legacy_subcol(nodeid int,
    repo text default 'https://legacy.cnx.org/content')
RETURNS xml
LANGUAGE SQL
AS
$$
SELECT
    xmlelement(name "col:subcollection",
    xmlelement(name "md:title", COALESCE (t.title, m.name)),
    legacy_content(legacy_subcol.nodeid, legacy_subcol.repo)
    )

    FROM trees t JOIN modules m on t.documentid = module_ident
    WHERE t.nodeid = legacy_subcol.nodeid
$$;

-- redefine or above, since needs to recurse back to subcol
-- recursion terminates on all-module subcols

CREATE OR REPLACE FUNCTION legacy_content(nodeid int,
    repo text default 'https://legacy.cnx.org/content')
RETURNS xml
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

-- Wrap it all together - takes a module_ident as primary parameter. Recurse passed down to mdml function
-- to control recursion into derived-from metadata

CREATE OR REPLACE FUNCTION legacy_collxml (ident int,
      recurse bool default False,
      repo text default 'https://legacy.cnx.org/content')
RETURNS xml
LANGUAGE SQL
AS
$$
SELECT xmlelement(name "col:collection",
             xmlattributes( 'http://cnx.rice.edu/collxml' as "xmlns",
                            'http://cnx.rice.edu/cnxml' as "xmlns:cnx",
                            'http://cnx.rice.edu/system-info' as "xmlns:cnxorg",
                            'http://cnx.rice.edu/mdml' as "xmlns:md",
                            'http://cnx.rice.edu/collxml' as "xmlns:col",
                            m.language as "xml:lang"),
    xmlelement(name "metadata",
        xmlattributes( 'http://cnx.rice.edu/mdml' as "xmlns:md",
                       '0.5' as "mdml-version"),
        legacy_mdml_inner(legacy_collxml.ident,
                          legacy_collxml.recurse,
                          legacy_collxml.repo)
    ),
    xmlelement(name "col:parameters",
        xmlelement(name "col:param",
            xmlattributes('print-style' as "name", print_style as "value")
        )
    ),
    legacy_content(nodeid, legacy_collxml.repo)
)
FROM modules m JOIN trees t ON m.module_ident = t.documentid WHERE m.module_ident = legacy_collxml.ident
$$;
""")

    cursor.execute('SELECT current_user')
    username = cursor.fetchall()[0][0]

    with super_user() as super_cursor:
        super_cursor.execute("""
CREATE OR REPLACE FUNCTION pretty_print(doc xml)
 RETURNS xml
 LANGUAGE plpythonu
AS $$
from lxml import etree
return etree.tostring(etree.fromstring(doc), pretty_print=True)
$$;
ALTER FUNCTION pretty_print(xml) OWNER TO {username}
    """.format(username=username))


def down(cursor):
    cursor.execute("""
    DROP FUNCTION legacy_collxml (int, bool, text);
    DROP FUNCTION legacy_subcol (int, text);
    DROP FUNCTION legacy_content (int, text);
    DROP FUNCTION legacy_module (int, text);
    DROP FUNCTION legacy_mdml (int, bool, text);
    DROP FUNCTION legacy_mdml_inner (int, bool, text);
    """)

    with super_user() as super_cursor:
        super_cursor.execute("""
    DROP FUNCTION pretty_print (xml);
    """)
