# -*- coding: utf-8 -*-
def up(cursor):
    cursor.execute("""
CREATE TRIGGER collection_html_abstract_trigger
  AFTER INSERT OR UPDATE ON modules FOR EACH ROW
  WHEN (new.portal_type = 'Collection'::text)
  EXECUTE PROCEDURE module_html_abstract();
""")


def down(cursor):
    cursor.execute("DROP TRIGGER collection_html_abstract_trigger ON modules")
