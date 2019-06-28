# -*- coding: utf-8 -*-


def up(cursor):
    cursor.execute("""
    CREATE OR REPLACE FUNCTION index_fulltext_book_trigger() RETURNS trigger
        LANGUAGE plpgsql
        AS $_$
      BEGIN
        DELETE from modulefti WHERE module_ident = NEW.module_ident;
        PERFORM insert_book_fti(NEW.module_ident);
        RETURN NULL;
      END;
      $_$;

    CREATE AGGREGATE tsvector_agg (
          BASETYPE = tsvector,
          SFUNC = tsvector_concat,
          STYPE = tsvector,
          INITCOND = ''
        );

    CREATE OR REPLACE FUNCTION insert_book_fti(bookid integer) RETURNS void
        LANGUAGE sql
        AS $_$
        WITH RECURSIVE t(node, parent, document, path) AS (
            SELECT tr.nodeid, tr.parent_id, tr.documentid, ARRAY[tr.nodeid]
            FROM trees tr
            WHERE tr.documentid = bookid and tr.is_collated = 'False'
          UNION ALL
            SELECT c.nodeid, c.parent_id, c.documentid, path || ARRAY[c.nodeid]
            FROM trees c JOIN t ON c.parent_id = t.node
            WHERE NOT c.nodeid = ANY(t.path)
          )
        INSERT INTO modulefti (module_ident, module_idx)
             SELECT bookid, tsvector_agg(mf.module_idx)
          FROM t JOIN modulefti mf
            ON t.document = mf.module_ident JOIN modules m
            ON t.document = m.module_ident
          WHERE m.portal_type IN ('Module','CompositeModule')
        $_$;

    CREATE TRIGGER index_fulltext_book
        AFTER INSERT OR UPDATE ON latest_modules
        FOR EACH ROW
        WHEN ((new.portal_type = 'Collection'::text))
        EXECUTE PROCEDURE index_fulltext_book_trigger();
    """)


def down(cursor):
    cursor.execute("""
    DROP TRIGGER index_fulltext_book ON latest_modules;
    DROP FUNCTION insert_book_fti(bookid integer);
    DROP FUNCTION index_fulltext_book_trigger();
    DROP AGGREGATE tsvector_agg(tsvector);
    """)
