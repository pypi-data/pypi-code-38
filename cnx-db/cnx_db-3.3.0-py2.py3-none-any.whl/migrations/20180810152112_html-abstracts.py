# -*- coding: utf-8 -*-


# Uncomment should_run if this is a repeat migration
# def should_run(cursor):
#     # TODO return True if migration should run


def up(cursor):
    # Add trigger to transform abstracts

    cursor.execute('''
CREATE OR REPLACE FUNCTION module_html_abstract ()
  RETURNS TRIGGER
AS $$
DECLARE
  has_html integer;
BEGIN
  SELECT html INTO has_html FROM abstracts where abstractid = NEW.abstractid;
  IF has_html IS NULL
    THEN
      UPDATE abstracts SET html = html_abstract(NEW.module_ident)
        WHERE abstractid = NEW.abstractid;
  END IF;
RETURN NEW;
END;
$$ LANGUAGE PLPGSQL;


CREATE TRIGGER module_html_abstract_trigger
  AFTER INSERT OR UPDATE ON modules FOR EACH ROW
  EXECUTE PROCEDURE module_html_abstract();
''')

    cursor.execute('''
WITH mods AS (SELECT a.abstractid AS ab_id, first(module_ident) AS module_ident
FROM abstracts a JOIN modules m ON a.abstractid = m.abstractid
WHERE html IS NULL GROUP BY a.abstractid)
UPDATE abstracts SET html = html_abstract(module_ident)
FROM mods WHERE abstractid = ab_id;
''')


def down(cursor):
    # Drop function and trigger
    cursor.execute('DROP FUNCTION module_html_abstract() CASCADE')
