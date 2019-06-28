# -*- coding: utf-8 -*-


# Uncomment should_run if this is a repeat migration
# def should_run(cursor):
#     # TODO return True if migration should run


def up(cursor):
    # TODO migration code
    cursor.execute("""
CREATE OR REPLACE FUNCTION replace_collxml(coll_id integer)
 RETURNS integer
 LANGUAGE plpgsql
AS $function$
  DECLARE
    existing_collxml_id integer;
    _collxml_id integer;

  BEGIN
    existing_collxml_id := (SELECT fileid FROM module_files
        WHERE module_ident = coll_id AND filename = 'collection.xml');

    SELECT fileid FROM files WHERE sha1 =
      sha1(pretty_print(legacy_collxml(coll_id, True))::text::bytea)
        INTO _collxml_id;

    IF _collxml_id IS NULL THEN
      INSERT INTO files (file, media_type) SELECT
        pretty_print(legacy_collxml(coll_id, True))::text::bytea,
        'text/xml'
        RETURNING fileid INTO _collxml_id;
    END IF;


    IF existing_collxml_id IS NULL THEN
      INSERT INTO module_files (module_ident, fileid, filename)
        VALUES ( coll_id, _collxml_id, 'collection.xml');
    ELSIF _collxml_id != existing_collxml_id THEN
      DELETE FROM module_files WHERE module_ident = coll_id AND filename = 'collection.xml';
      DELETE FROM files WHERE fileid = existing_collxml_id;
      INSERT INTO module_files (module_ident, fileid, filename)
        VALUES ( coll_id, _collxml_id, 'collection.xml');
    END IF;

    RETURN _collxml_id;
  END;

$function$
    """)


def down(cursor):
    cursor.execute("DROP FUNCTION replace_collxml(integer)")
