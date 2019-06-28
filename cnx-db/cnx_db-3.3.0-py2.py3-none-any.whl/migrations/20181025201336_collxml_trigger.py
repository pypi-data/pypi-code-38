# -*- coding: utf-8 -*-


# Uncomment should_run if this is a repeat migration
# def should_run(cursor):
#     # TODO return True if migration should run


def up(cursor):
    cursor.execute("""
CREATE OR REPLACE FUNCTION gen_minor_collxml()
  RETURNS TRIGGER AS $$
  DECLARE
    has_existing_collxml integer;
    _collxml_id integer;

  BEGIN
    has_existing_collxml := (SELECT fileid FROM module_files
        WHERE module_ident = NEW.module_ident
        AND filename = 'collection.xml');

    IF has_existing_collxml IS NULL THEN
      INSERT INTO files (file, media_type) SELECT
          pretty_print(legacy_collxml(NEW.module_ident, True))::text::bytea,
          'text/xml'
          RETURNING fileid INTO _collxml_id;

      INSERT INTO module_files (module_ident, fileid, filename)
          VALUES ( NEW.module_ident, _collxml_id, 'collection.xml');

    END IF;
    RETURN NEW;
  END;

$$ LANGUAGE PLPGSQL;

-- This needs to be a constraint trigger so that it can be deferred to end of
-- transaction, when all the needed rows become visible.

CREATE CONSTRAINT TRIGGER collection_minor_ver_collxml
  AFTER INSERT OR UPDATE ON modules
  DEFERRABLE
  INITIALLY DEFERRED
  FOR EACH ROW
  WHEN (new.portal_type = 'Collection'::text AND new.minor_version > 1)
  EXECUTE PROCEDURE gen_minor_collxml();
""")


def down(cursor):
    cursor.execute('DROP FUNCTION gen_minor_collxml() CASCADE')
