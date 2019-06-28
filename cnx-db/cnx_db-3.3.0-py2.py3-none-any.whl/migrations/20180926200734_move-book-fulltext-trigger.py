# -*- coding: utf-8 -*-


# Uncomment should_run if this is a repeat migration
# def should_run(cursor):
#     # TODO return True if migration should run


def up(cursor):
    cursor.execute("""
CREATE OR REPLACE FUNCTION index_fulltext_book_trigger()
  RETURNS TRIGGER AS $$
  BEGIN
    DELETE from modulefti WHERE module_ident = NEW.documentid;
    PERFORM insert_book_fti(NEW.documentid);
    RETURN NULL;
  END;
  $$
  LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS index_fulltext_book ON latest_modules;
CREATE TRIGGER index_fulltext_book
  AFTER INSERT OR UPDATE ON trees
    FOR EACH row WHEN (NEW.parent_id is NULL)
      EXECUTE PROCEDURE index_fulltext_book_trigger();
      """)


def down(cursor):
    cursor.execute("""
CREATE OR REPLACE FUNCTION index_fulltext_book_trigger()
  RETURNS TRIGGER AS $$
  BEGIN
    DELETE from modulefti WHERE module_ident = NEW.module_ident;
    PERFORM insert_book_fti(NEW.module_ident);
    RETURN NULL;
  END;
  $$
  LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS index_fulltext_book ON trees;
CREATE TRIGGER index_fulltext_book
  AFTER INSERT OR UPDATE ON latest_modules
    FOR EACH row WHEN (NEW.portal_type =  'Collection')
      EXECUTE PROCEDURE index_fulltext_book_trigger();
      """)
