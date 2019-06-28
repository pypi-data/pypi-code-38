# -*- coding: utf-8 -*-


def up(cursor):
    """Fix bad minor_versions for major_version = 2 modules"""

    cursor.execute("""CREATE SCHEMA IF NOT EXISTS datamigrations""")

    cursor.execute("""
    CREATE TABLE datamigrations.bad_minor_vers as SELECT * from modules
        WHERE substring(version,0,strpos(version,'.'))::int +
        substring(version,strpos(version,'.')+1)::int - 1 != major_version;

""")
    cursor.execute("""
    UPDATE modules SET major_version =
                     substring(version,0,strpos(version,'.'))::int +
                     substring(version,strpos(version,'.')+1)::int - 1
      WHERE substring(version,0,strpos(version,'.'))::int +
      substring(version,strpos(version,'.')+1)::int - 1 != major_version;

""")


def down(cursor):
    """Put the bad values back?!"""
    cursor.execute("""UPDATE modules
        SET major_version = b.major_version
        FROM datamigrations.bad_minor_vers b
        WHERE modules.module_ident = b.module_ident;
    DROP TABLE datamigrations.bad_minor_vers;
""")
