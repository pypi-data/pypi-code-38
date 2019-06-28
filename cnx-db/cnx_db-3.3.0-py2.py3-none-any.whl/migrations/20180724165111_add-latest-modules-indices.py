# -*- coding: utf-8 -*-


# Uncomment should_run if this is a repeat migration
# def should_run(cursor):
#     # TODO return True if migration should run


def up(cursor):
    cursor.execute("""
           CREATE FUNCTION year(ts timestamptz)
               RETURNS DOUBLE PRECISION IMMUTABLE AS $$
               SELECT EXTRACT(year from ts)
               $$ LANGUAGE SQL;""")
    cursor.execute("""
        	CREATE INDEX latest_modules_gin_authors_idx ON latest_modules using gin(authors);
       		CREATE INDEX latest_modules_publication_year_idx ON latest_modules (year(revised));
        """)



def down(cursor):
    cursor.execute("""
    		DROP INDEX latest_modules_gin_authors_idx;
    		DROP INDEX latest_modules_publication_year_idx;
    		DROP FUNCTION year(timestamptz);
    	""")