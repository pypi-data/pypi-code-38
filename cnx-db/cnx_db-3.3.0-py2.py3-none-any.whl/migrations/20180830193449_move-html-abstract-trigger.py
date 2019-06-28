# -*- coding: utf-8 -*-


def up(cursor):
    cursor.execute('''
CREATE OR REPLACE FUNCTION module_html_abstract ()
  RETURNS TRIGGER
AS $$
DECLARE
  has_html text;
BEGIN
  SELECT html INTO has_html FROM abstracts a JOIN modules m ON a.abstractid = m.abstractid WHERE module_ident = NEW.module_ident;
  IF has_html IS NULL
    THEN
      UPDATE abstracts SET html = html_abstract(NEW.module_ident)
        WHERE abstractid = NEW.abstractid;
  END IF;
RETURN NEW;
END;
$$ LANGUAGE PLPGSQL;

DROP TRIGGER module_html_abstract_trigger ON modules;

CREATE TRIGGER module_html_abstract_trigger
  AFTER INSERT OR UPDATE ON module_files FOR EACH ROW
  WHEN (new.filename = 'index.cnxml'::text)
   EXECUTE PROCEDURE module_html_abstract();
''')


def down(cursor):
    cursor.execute('''
CREATE OR REPLACE FUNCTION module_html_abstract ()
  RETURNS TRIGGER
AS $$
DECLARE
  has_html text;
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

DROP TRIGGER module_html_abstract_trigger ON module_files;

CREATE TRIGGER module_html_abstract_trigger
  AFTER INSERT OR UPDATE ON modules FOR EACH ROW
   EXECUTE PROCEDURE module_html_abstract();
''')
