# -*- coding: utf-8 -*-


def up(cursor):
    # TODO migration code
    cursor.execute("""
CREATE OR REPLACE FUNCTION rebake()
 RETURNS trigger
 LANGUAGE plpgsql
AS $$
BEGIN
  UPDATE modules SET stateid = 5
    WHERE module_ident = NEW.module_ident;
  RETURN NEW;
END;
$$;

CREATE TRIGGER ruleset_trigger
  AFTER INSERT OR UPDATE ON module_files FOR EACH ROW
  WHEN (new.filename = 'ruleset.css'::text)
  EXECUTE PROCEDURE rebake();
""")


def down(cursor):
    # TODO rollback code
    cursor.execute("""
DROP TRIGGER ruleset_trigger ON module_files;
DROP FUNCTION rebake();
""")
