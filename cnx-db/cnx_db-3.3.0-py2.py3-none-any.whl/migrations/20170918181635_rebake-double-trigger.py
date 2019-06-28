# -*- coding: utf-8 -*-


def up(cursor):
    cursor.execute("""
    CREATE OR REPLACE FUNCTION rebake()
     RETURNS trigger
     LANGUAGE plpgsql
    AS $$
    BEGIN
      UPDATE modules SET stateid = 5
        WHERE module_ident = NEW.module_ident and stateid not in (5, 6);
      RETURN NEW;
    END;
    $$;
    """)


def down(cursor):
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
    $$
    """)
