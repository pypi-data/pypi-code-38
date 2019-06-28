# -*- coding: utf-8 -*-


# Uncomment should_run if this is a repeat migration
# def should_run(cursor):
#     # TODO return True if migration should run

def up(cursor):
    # fix trigger function
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

''')


def down(cursor):
    # Break trigger function

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
''')
