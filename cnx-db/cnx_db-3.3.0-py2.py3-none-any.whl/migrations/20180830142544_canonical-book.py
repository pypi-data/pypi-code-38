# -*- coding: utf-8 -*-


def up(cursor):
    cursor.execute('''
ALTER TABLE modules ADD COLUMN canonical uuid;
ALTER TABLE latest_modules ADD COLUMN canonical uuid;

CREATE OR REPLACE FUNCTION update_latest() RETURNS trigger AS '
BEGIN
-- lastest content is the highest version that has successfully baked - states 1 and 8 (current and fallback)
-- represent some sort of success (fallback used an old recipe due to errors)
  IF (TG_OP = ''INSERT'' OR TG_OP = ''UPDATE'') AND
          ARRAY [NEW.major_version, NEW.minor_version] >= (SELECT ARRAY [major_version, minor_version]
            FROM latest_modules WHERE uuid = NEW.uuid UNION ALL SELECT ARRAY[0, NULL] LIMIT 1) AND
          NEW.stateid in (1, 8) THEN -- current and fallback
      LOCK TABLE latest_modules IN SHARE ROW EXCLUSIVE MODE;
      DELETE FROM latest_modules WHERE moduleid = NEW.moduleid OR uuid = NEW.uuid;
      INSERT into latest_modules (
                uuid, module_ident, portal_type, moduleid, version, name,
          created, revised, abstractid, stateid, doctype, licenseid,
          submitter,submitlog, parent, language,
        authors, maintainers, licensors, parentauthors, google_analytics,
                major_version, minor_version, print_style, baked, recipe, canonical)
      VALUES (
         NEW.uuid, NEW.module_ident, NEW.portal_type, NEW.moduleid, NEW.version, NEW.name,
       NEW.created, NEW.revised, NEW.abstractid, NEW.stateid, NEW.doctype, NEW.licenseid,
       NEW.submitter, NEW.submitlog, NEW.parent, NEW.language,
     NEW.authors, NEW.maintainers, NEW.licensors, NEW.parentauthors, NEW.google_analytics,
         NEW.major_version, NEW.minor_version, NEW.print_style, NEW.baked, NEW.recipe, NEW.canonical);
  END IF;

  IF TG_OP = ''UPDATE'' AND NEW.stateid in (1, 8) THEN -- current or fallback
      UPDATE latest_modules SET
        uuid=NEW.uuid,
        moduleid=NEW.moduleid,
        portal_type=NEW.portal_type,
        version=NEW.version,
        name=NEW.name,
        created=NEW.created,
        revised=NEW.revised,
        abstractid=NEW.abstractid,
        stateid=NEW.stateid,
        doctype=NEW.doctype,
        licenseid=NEW.licenseid,
    submitter=NEW.submitter,
    submitlog=NEW.submitlog,
        parent=NEW.parent,
    language=NEW.language,
    authors=NEW.authors,
    maintainers=NEW.maintainers,
    licensors=NEW.licensors,
    parentauthors=NEW.parentauthors,
    google_analytics=NEW.google_analytics,
        major_version=NEW.major_version,
        minor_version=NEW.minor_version,
        print_style=NEW.print_style,
        baked=NEW.baked,
        recipe=NEW.recipe,
        canonical=NEW.canonical
        WHERE module_ident=NEW.module_ident;
  END IF;

RETURN NEW;
END;

' LANGUAGE 'plpgsql';

CREATE OR REPLACE FUNCTION delete_from_latest() RETURNS trigger AS '
BEGIN
  DELETE FROM  latest_modules
    WHERE module_ident=OLD.module_ident;
  IF FOUND THEN
    INSERT into latest_modules (
         module_ident, portal_type, moduleid, uuid, version, name,
         created, revised, abstractid, licenseid, doctype, submitter,
         submitlog, stateid, parent, language, authors, maintainers,
         licensors, parentauthors, google_analytics, buylink,
         major_version, minor_version, print_style, baked, recipe, canonical)
    select
         module_ident, portal_type, moduleid, uuid, version, name,
         created, revised, abstractid, licenseid, doctype, submitter,
         submitlog, stateid, parent, language, authors, maintainers,
         licensors, parentauthors, google_analytics, buylink,
         major_version, minor_version, print_style, baked, recipe, canonical
    from current_modules where moduleid=OLD.moduleid;
  END IF;
  RETURN OLD;
END;
' LANGUAGE 'plpgsql';

CREATE OR REPLACE FUNCTION default_canonical_book(id uuid)
RETURNS uuid LANGUAGE SQL STRICT IMMUTABLE AS $$
WITH RECURSIVE t(node, title, parent, path, value) AS (
      SELECT nodeid, coalesce(title,name), parent_id, ARRAY[nodeid], documentid
      FROM trees tr, modules m
      WHERE m.uuid = $1
      AND tr.documentid = m.module_ident
      AND tr.parent_id IS NOT NULL
    UNION ALL
      SELECT c1.nodeid, c1.title, c1.parent_id,
             t.path || ARRAY[c1.nodeid], c1.documentid
              FROM trees c1
              JOIN t ON (c1.nodeid = t.parent)
              WHERE not nodeid = any (t.path)
        )

        SELECT uuid
        from t join modules on t.value = module_ident
        where t.parent is NULL
        ORDER BY revised, major_version, minor_version
        LIMIT 1
$$;

DROP VIEW public.current_modules;
CREATE OR REPLACE VIEW public.current_modules AS
 WITH latest_idents(module_ident) AS (
         SELECT m2.module_ident
           FROM (public.modules m2
             JOIN public.modulestates ms ON ((m2.stateid = ms.stateid)))
          WHERE ((m2.major_version = ( SELECT max(m3.major_version) AS max
                   FROM public.modules m3
                  WHERE (m2.uuid = m3.uuid))) AND ((m2.minor_version IS NULL) OR (m2.minor_version = ( SELECT max(m4.minor_version) AS max
                   FROM public.modules m4
                  WHERE ((m2.uuid = m4.uuid) AND (m2.major_version = m4.major_version))))) AND (ms.statename = ANY (ARRAY['current'::text, 'fallback'::text])))
        )
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
    m.print_style,
    m.baked,
    m.recipe,
    m.canonical
   FROM (latest_idents li
     JOIN public.modules m ON ((m.module_ident = li.module_ident)));

CREATE OR REPLACE FUNCTION set_default_canonical()
RETURNS TRIGGER AS
$$
BEGIN
  NEW.canonical = public.default_canonical_book(NEW.uuid);
  RETURN NEW;
END;
$$
    LANGUAGE plpgsql;

CREATE TRIGGER set_default_canonical_trigger
  BEFORE INSERT OR UPDATE ON modules FOR EACH ROW
  WHEN (new.canonical is NULL)
  EXECUTE PROCEDURE set_default_canonical();
''')


def down(cursor):
    cursor.execute('''
DROP TRIGGER set_default_canonical_trigger on modules;
DROP FUNCTION set_default_canonical();
DROP FUNCTION default_canonical_book(uuid);

DROP VIEW public.current_modules;
CREATE OR REPLACE VIEW public.current_modules AS
 WITH latest_idents(module_ident) AS (
         SELECT m2.module_ident
           FROM (public.modules m2
             JOIN public.modulestates ms ON ((m2.stateid = ms.stateid)))
          WHERE ((m2.major_version = ( SELECT max(m3.major_version) AS max
                   FROM public.modules m3
                  WHERE (m2.uuid = m3.uuid))) AND ((m2.minor_version IS NULL) OR (m2.minor_version = ( SELECT max(m4.minor_version) AS max
                   FROM public.modules m4
                  WHERE ((m2.uuid = m4.uuid) AND (m2.major_version = m4.major_version))))) AND (ms.statename = ANY (ARRAY['current'::text, 'fallback'::text])))
        )
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
    m.print_style,
    m.baked,
    m.recipe
   FROM (latest_idents li
     JOIN public.modules m ON ((m.module_ident = li.module_ident)));

CREATE OR REPLACE FUNCTION update_latest() RETURNS trigger AS '
BEGIN
-- lastest content is the highest version that has successfully baked - states 1 and 8 (current and fallback)
-- represent some sort of success (fallback used an old recipe due to errors)
  IF (TG_OP = ''INSERT'' OR TG_OP = ''UPDATE'') AND
          ARRAY [NEW.major_version, NEW.minor_version] >= (SELECT ARRAY [major_version, minor_version]
            FROM latest_modules WHERE uuid = NEW.uuid UNION ALL SELECT ARRAY[0, NULL] LIMIT 1) AND
          NEW.stateid in (1, 8) THEN -- current and fallback
      LOCK TABLE latest_modules IN SHARE ROW EXCLUSIVE MODE;
      DELETE FROM latest_modules WHERE moduleid = NEW.moduleid OR uuid = NEW.uuid;
      INSERT into latest_modules (
                uuid, module_ident, portal_type, moduleid, version, name,
          created, revised, abstractid, stateid, doctype, licenseid,
          submitter,submitlog, parent, language,
        authors, maintainers, licensors, parentauthors, google_analytics,
                major_version, minor_version, print_style, baked, recipe)
      VALUES (
         NEW.uuid, NEW.module_ident, NEW.portal_type, NEW.moduleid, NEW.version, NEW.name,
       NEW.created, NEW.revised, NEW.abstractid, NEW.stateid, NEW.doctype, NEW.licenseid,
       NEW.submitter, NEW.submitlog, NEW.parent, NEW.language,
     NEW.authors, NEW.maintainers, NEW.licensors, NEW.parentauthors, NEW.google_analytics,
         NEW.major_version, NEW.minor_version, NEW.print_style, NEW.baked, NEW.recipe);
  END IF;

  IF TG_OP = ''UPDATE'' AND NEW.stateid in (1, 8) THEN -- current or fallback
      UPDATE latest_modules SET
        uuid=NEW.uuid,
        moduleid=NEW.moduleid,
        portal_type=NEW.portal_type,
        version=NEW.version,
        name=NEW.name,
        created=NEW.created,
        revised=NEW.revised,
        abstractid=NEW.abstractid,
        stateid=NEW.stateid,
        doctype=NEW.doctype,
        licenseid=NEW.licenseid,
    submitter=NEW.submitter,
    submitlog=NEW.submitlog,
        parent=NEW.parent,
    language=NEW.language,
    authors=NEW.authors,
    maintainers=NEW.maintainers,
    licensors=NEW.licensors,
    parentauthors=NEW.parentauthors,
    google_analytics=NEW.google_analytics,
        major_version=NEW.major_version,
        minor_version=NEW.minor_version,
        print_style=NEW.print_style,
        baked=NEW.baked,
        recipe=NEW.recipe
        WHERE module_ident=NEW.module_ident;
  END IF;

RETURN NEW;
END;

' LANGUAGE 'plpgsql';

CREATE OR REPLACE FUNCTION delete_from_latest() RETURNS trigger AS '
BEGIN
  DELETE FROM  latest_modules
    WHERE module_ident=OLD.module_ident;
  IF FOUND THEN
    INSERT into latest_modules (
         module_ident, portal_type, moduleid, uuid, version, name,
         created, revised, abstractid, licenseid, doctype, submitter,
         submitlog, stateid, parent, language, authors, maintainers,
         licensors, parentauthors, google_analytics, buylink,
         major_version, minor_version, print_style, baked, recipe)
    select
         module_ident, portal_type, moduleid, uuid, version, name,
         created, revised, abstractid, licenseid, doctype, submitter,
         submitlog, stateid, parent, language, authors, maintainers,
         licensors, parentauthors, google_analytics, buylink,
         major_version, minor_version, print_style, baked, recipe
    from current_modules where moduleid=OLD.moduleid;
  END IF;
  RETURN OLD;
END;
' LANGUAGE 'plpgsql';
ALTER TABLE modules DROP COLUMN canonical;
ALTER TABLE latest_modules DROP COLUMN canonical;

    ''')
