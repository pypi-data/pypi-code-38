# -*- coding: utf-8 -*-


def up(cursor):
    cursor.execute("""
        ALTER TABLE modulekeywords DROP CONSTRAINT
        modulekeywords_module_ident_fkey;

        ALTER TABLE modulekeywords ADD FOREIGN KEY
        (module_ident) REFERENCES modules(module_ident)
        ON DELETE CASCADE DEFERRABLE""")

    cursor.execute("""
        ALTER TABLE moduletags DROP CONSTRAINT
        moduletags_module_ident_fkey;

        ALTER TABLE moduletags ADD FOREIGN KEY
        (module_ident) REFERENCES modules(module_ident)
        ON DELETE CASCADE DEFERRABLE""")

    cursor.execute("""
        ALTER TABLE module_files DROP CONSTRAINT
        module_files_module_ident_fkey;

        ALTER TABLE module_files ADD FOREIGN KEY
        (module_ident) REFERENCES modules(module_ident)
        ON DELETE CASCADE""")

    cursor.execute("""
        ALTER TABLE collated_file_associations DROP CONSTRAINT
        collated_file_associations_context_fkey;

        ALTER TABLE collated_file_associations ADD FOREIGN KEY
        (context) REFERENCES modules(module_ident)
        ON DELETE CASCADE;

        ALTER TABLE collated_file_associations DROP CONSTRAINT
        collated_file_associations_item_fkey;

        ALTER TABLE collated_file_associations ADD FOREIGN KEY
        (item) REFERENCES modules(module_ident)
        ON DELETE CASCADE;

        ALTER TABLE collated_file_associations DROP CONSTRAINT
        collated_file_associations_fileid_fkey;

        ALTER TABLE collated_file_associations ADD FOREIGN KEY
        (fileid) REFERENCES files(fileid)
        ON DELETE CASCADE""")

    cursor.execute("""
        ALTER TABLE document_baking_result_associations DROP CONSTRAINT
        document_baking_result_associations_module_ident_fkey;

        ALTER TABLE document_baking_result_associations ADD FOREIGN KEY
        (module_ident) REFERENCES modules(module_ident)
        ON DELETE CASCADE""")

    # Need to close transaction to allow concurrent index creation
    cursor.execute('COMMIT')
    cursor.execute("""
        CREATE INDEX CONCURRENTLY
            collated_file_associations_context_fkey
                ON collated_file_associations (context);
    """)
    cursor.execute("""
        CREATE INDEX CONCURRENTLY
            collated_file_associations_item_fkey
                ON collated_file_associations (item);
    """)
    cursor.execute("""
        CREATE INDEX CONCURRENTLY collated_fti_context_fkey
            ON collated_fti (context);
    """)
    cursor.execute("""
        CREATE INDEX CONCURRENTLY collated_fti_item_fkey
            ON collated_fti (item);
    """)
    cursor.execute("""
        CREATE INDEX CONCURRENTLY
            collated_fti_lexemes_context_fkey
                ON collated_fti_lexemes (context);
    """)
    cursor.execute("""
        CREATE INDEX CONCURRENTLY collated_fti_lexemes_item_fkey
            ON collated_fti_lexemes (item);
    """)
    cursor.execute("""
        CREATE INDEX CONCURRENTLY
            document_baking_result_associations_module_ident_fkey
                ON document_baking_result_associations (module_ident);
    """)
    cursor.execute("""
        CREATE INDEX CONCURRENTLY document_hits_documentid_fkey
            ON document_hits (documentid);
    """)
    cursor.execute("""
        CREATE INDEX CONCURRENTLY moduleratings_module_ident_fkey
            ON moduleratings (module_ident);
    """)
    cursor.execute("""
        CREATE INDEX CONCURRENTLY moduletags_module_ident_fkey
            ON moduletags (module_ident);
    """)


def down(cursor):
    # Need to close transaction to allow concurrent index deletion
    cursor.execute('COMMIT')
    cursor.execute("""
        DROP INDEX CONCURRENTLY
            collated_file_associations_context_fkey;
    """)
    cursor.execute("""
        DROP INDEX CONCURRENTLY
            collated_file_associations_item_fkey;
    """)
    cursor.execute("""
        DROP INDEX CONCURRENTLY collated_fti_context_fkey;
    """)
    cursor.execute("""
        DROP INDEX CONCURRENTLY collated_fti_item_fkey;
    """)
    cursor.execute("""
        DROP INDEX CONCURRENTLY
            collated_fti_lexemes_context_fkey;
    """)
    cursor.execute("""
        DROP INDEX CONCURRENTLY collated_fti_lexemes_item_fkey;
    """)
    cursor.execute("""
        DROP INDEX CONCURRENTLY
            document_baking_result_associations_module_ident_fkey;
    """)
    cursor.execute("""
        DROP INDEX CONCURRENTLY document_hits_documentid_fkey;
    """)
    cursor.execute("""
        DROP INDEX CONCURRENTLY moduleratings_module_ident_fkey;
    """)
    cursor.execute("""
        DROP INDEX CONCURRENTLY moduletags_module_ident_fkey;
    """)

    cursor.execute("""
        ALTER TABLE modulekeywords DROP CONSTRAINT
        modulekeywords_module_ident_fkey;

        ALTER TABLE modulekeywords ADD FOREIGN KEY
        (module_ident) REFERENCES modules(module_ident)
         DEFERRABLE""")

    cursor.execute("""
        ALTER TABLE moduletags DROP CONSTRAINT
        moduletags_module_ident_fkey;

        ALTER TABLE moduletags ADD FOREIGN KEY
        (module_ident) REFERENCES modules(module_ident)
         DEFERRABLE""")

    cursor.execute("""
        ALTER TABLE module_files DROP CONSTRAINT
        module_files_module_ident_fkey;

        ALTER TABLE module_files ADD FOREIGN KEY
        (module_ident) REFERENCES modules(module_ident)
        """)

    cursor.execute("""
        ALTER TABLE collated_file_associations DROP CONSTRAINT
        collated_file_associations_context_fkey;

        ALTER TABLE collated_file_associations ADD FOREIGN KEY
        (context) REFERENCES modules(module_ident);

        ALTER TABLE collated_file_associations DROP CONSTRAINT
        collated_file_associations_item_fkey;

        ALTER TABLE collated_file_associations ADD FOREIGN KEY
        (item) REFERENCES modules(module_ident);

        ALTER TABLE collated_file_associations DROP CONSTRAINT
        collated_file_associations_fileid_fkey;

        ALTER TABLE collated_file_associations ADD FOREIGN KEY
        (fileid) REFERENCES files(fileid)
        """)

    cursor.execute("""
        ALTER TABLE document_baking_result_associations DROP CONSTRAINT
        document_baking_result_associations_module_ident_fkey;

        ALTER TABLE document_baking_result_associations ADD FOREIGN KEY
        (module_ident) REFERENCES modules(module_ident)
        """)
