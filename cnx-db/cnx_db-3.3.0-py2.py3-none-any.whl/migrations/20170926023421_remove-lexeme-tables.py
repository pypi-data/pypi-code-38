# -*- coding: utf-8 -*-


def up(cursor):
    cursor.execute("""
    CREATE OR REPLACE FUNCTION count_collated_lexemes(myident integer, bookident integer, mysearch text) RETURNS bigint
        LANGUAGE sql STABLE
        AS $_$
    WITH lexemes AS (SELECT word, nentry FROM ts_stat('SELECT module_idx FROM collated_fti WHERE item = ' || myident || ' and context = ' || bookident)),
         words AS (select regexp_split_to_table(mysearch,' ') AS qwords)
        SELECT SUM(nentry)::bigint FROM lexemes, words WHERE word @@ plainto_tsquery(qwords);
        $_$;

    CREATE OR REPLACE FUNCTION count_lexemes(myident integer, mysearch text) RETURNS bigint
        LANGUAGE sql STABLE
        AS $_$
    WITH lexemes AS (SELECT word, nentry FROM ts_stat('SELECT module_idx FROM modulefti WHERE module_ident = ' || myident)),
         words AS (select regexp_split_to_table(mysearch,' ') AS qwords)
        SELECT SUM(nentry)::bigint FROM lexemes, words WHERE word @@ plainto_tsquery(qwords);
        $_$;

    ALTER TABLE IF EXISTS modulefti_lexemes DROP CONSTRAINT IF EXISTS modulefti_lexemes_module_ident_fkey;

    ALTER TABLE IF EXISTS collated_fti_lexemes DROP CONSTRAINT IF EXISTS collated_fti_lexemes_context_fkey;

    ALTER TABLE IF EXISTS collated_fti_lexemes DROP CONSTRAINT IF EXISTS collated_fti_lexemes_item_fkey;

    DROP INDEX IF EXISTS collated_fti_lexemes_item_fkey;

    DROP INDEX IF EXISTS collated_fti_lexemes_context_fkey;

    DROP INDEX IF EXISTS collated_fti_lexemes_context_item_idx;

    DROP TRIGGER IF EXISTS index_fulltext_lexeme ON modulefti;

    DROP TRIGGER IF EXISTS index_collated_fulltext_lexeme ON collated_fti;

    DROP INDEX IF EXISTS modulefti_lexemes_module_ident;

    DROP TABLE IF EXISTS collated_fti_lexemes;

    DROP TABLE IF EXISTS modulefti_lexemes;

    DROP FUNCTION IF EXISTS index_fulltext_lexeme_update_trigger();

    DROP FUNCTION IF EXISTS index_collated_fulltext_lexeme_update_trigger();
    """)


def down(cursor):
    cursor.execute("""
CREATE TABLE collated_fti_lexemes (
    item integer,
    context integer,
    lexeme text,
    positions integer[]);

CREATE TABLE modulefti_lexemes (
    module_ident integer,
    lexeme text,
    positions integer[]);

CREATE OR REPLACE FUNCTION count_collated_lexemes(myident integer, bookident integer, mysearch text) RETURNS bigint
    LANGUAGE sql STABLE
    AS $_$
     select sum(array_length(positions,1))
            from collated_fti_lexemes,
                 regexp_split_to_table(strip(to_tsvector(mysearch))::text,' ') s
            where item = myident and context = bookident and lexeme = substr(s,2,length(s)-2)
$_$;


CREATE OR REPLACE FUNCTION count_lexemes(myident integer, mysearch text) RETURNS bigint
    LANGUAGE sql STABLE
    AS $_$
     select sum(array_length(positions,1))
            from modulefti_lexemes,
                 regexp_split_to_table(strip(to_tsvector(mysearch))::text,' ') s
            where module_ident = myident and lexeme = substr(s,2,length(s)-2)
$_$;

CREATE FUNCTION index_collated_fulltext_lexeme_update_trigger() RETURNS trigger
    LANGUAGE plpgsql
    AS $_$
  BEGIN

    DELETE from collated_fti_lexemes where item = NEW.item AND context = NEW.context;

    INSERT into collated_fti_lexemes (item, context, lexeme, positions)
       (with lex as (SELECT regexp_split_to_table(NEW.module_idx::text, E' \\'') as t )
       SELECT NEW.item, NEW.context,
              substring(t,1,strpos(t,E'\\':')-1),
              ('{'||substring(t,strpos(t,E'\\':')+2)||'}')::int[] from lex) ;

  RETURN NEW;
  END;
  $_$;

CREATE FUNCTION index_fulltext_lexeme_update_trigger() RETURNS trigger
    LANGUAGE plpgsql
    AS $_$
  BEGIN

    DELETE from modulefti_lexemes where module_ident = NEW.module_ident;

    INSERT into modulefti_lexemes (module_ident, lexeme, positions)
       (with lex as (SELECT regexp_split_to_table(NEW.module_idx::text, E' \\'') as t )
       SELECT NEW.module_ident,
              substring(t,1,strpos(t,E'\\':')-1),
              ('{'||substring(t,strpos(t,E'\\':')+2)||'}')::int[] from lex) ;

  RETURN NEW;
  END;
  $_$;

CREATE INDEX collated_fti_lexemes_context_fkey ON collated_fti_lexemes (context);

CREATE INDEX collated_fti_lexemes_context_item_idx ON collated_fti_lexemes (context, item);

CREATE INDEX collated_fti_lexemes_item_fkey ON collated_fti_lexemes (item);

CREATE INDEX modulefti_lexemes_module_ident ON modulefti_lexemes (module_ident);

CREATE TRIGGER index_collated_fulltext_lexeme
    BEFORE INSERT OR UPDATE ON collated_fti
    FOR EACH ROW
    EXECUTE PROCEDURE index_collated_fulltext_lexeme_update_trigger();

CREATE TRIGGER index_fulltext_lexeme
    BEFORE INSERT OR UPDATE ON modulefti
    FOR EACH ROW
    EXECUTE PROCEDURE index_fulltext_lexeme_update_trigger();

ALTER TABLE collated_fti_lexemes ADD CONSTRAINT collated_fti_lexemes_context_fkey FOREIGN KEY (context) REFERENCES modules (module_ident) ON DELETE CASCADE;

ALTER TABLE collated_fti_lexemes ADD CONSTRAINT collated_fti_lexemes_item_fkey FOREIGN KEY (item) REFERENCES modules (module_ident) ON DELETE CASCADE;

ALTER TABLE modulefti_lexemes ADD CONSTRAINT modulefti_lexemes_module_ident_fkey FOREIGN KEY (module_ident) REFERENCES modules (module_ident) ON DELETE CASCADE;
    """)
