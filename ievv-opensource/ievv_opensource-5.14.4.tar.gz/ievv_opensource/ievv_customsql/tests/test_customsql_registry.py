from django import test

from ievv_opensource.ievv_customsql import customsql_registry


class TestRegistry(test.TestCase):
    def test_add(self):
        class MockCustomSql(customsql_registry.AbstractCustomSql):
            pass

        mockregistry = customsql_registry.MockableRegistry()
        mockregistry.add('myapp', MockCustomSql)
        self.assertIn(MockCustomSql, mockregistry._customsql_classes)
        self.assertIn('myapp', mockregistry._customsql_classes_by_appname_map)
        self.assertIn(MockCustomSql, mockregistry._customsql_classes_by_appname_map['myapp'])

    def test_add_multiple_to_same_appname(self):
        class MockCustomSql1(customsql_registry.AbstractCustomSql):
            pass

        class MockCustomSql2(customsql_registry.AbstractCustomSql):
            pass

        mockregistry = customsql_registry.MockableRegistry()
        mockregistry.add('myapp', MockCustomSql1)
        mockregistry.add('myapp', MockCustomSql2)
        self.assertIn(MockCustomSql1, mockregistry._customsql_classes)
        self.assertIn(MockCustomSql2, mockregistry._customsql_classes)
        self.assertIn('myapp', mockregistry._customsql_classes_by_appname_map)
        self.assertIn(MockCustomSql1, mockregistry._customsql_classes_by_appname_map['myapp'])
        self.assertIn(MockCustomSql2, mockregistry._customsql_classes_by_appname_map['myapp'])

    def test_remove(self):
        class MockCustomSql(customsql_registry.AbstractCustomSql):
            pass

        mockregistry = customsql_registry.MockableRegistry()
        mockregistry.add('myapp', MockCustomSql)

        mockregistry.remove('myapp', MockCustomSql)
        self.assertNotIn(MockCustomSql, mockregistry._customsql_classes)
        self.assertNotIn('myapp', mockregistry._customsql_classes_by_appname_map)

    def test_contains(self):
        class MockCustomSql(customsql_registry.AbstractCustomSql):
            pass

        mockregistry = customsql_registry.MockableRegistry()
        self.assertFalse(MockCustomSql in mockregistry)
        mockregistry.add('myapp', MockCustomSql)
        self.assertTrue(MockCustomSql in mockregistry)

    def test_remove_one_of_multiple_in_same_app(self):
        class MockCustomSql1(customsql_registry.AbstractCustomSql):
            pass

        class MockCustomSql2(customsql_registry.AbstractCustomSql):
            pass

        mockregistry = customsql_registry.MockableRegistry()
        mockregistry.add('myapp', MockCustomSql1)
        mockregistry.add('myapp', MockCustomSql2)

        mockregistry.remove('myapp', MockCustomSql2)
        self.assertNotIn(MockCustomSql2, mockregistry._customsql_classes)
        self.assertNotIn(MockCustomSql2, mockregistry._customsql_classes_by_appname_map['myapp'])
        self.assertIn(MockCustomSql1, mockregistry._customsql_classes)
        self.assertIn('myapp', mockregistry._customsql_classes_by_appname_map)

    def test_iter(self):
        class MockCustomSql1(customsql_registry.AbstractCustomSql):
            pass

        class MockCustomSql2(customsql_registry.AbstractCustomSql):
            pass

        class MockCustomSql3(customsql_registry.AbstractCustomSql):
            pass

        mockregistry = customsql_registry.MockableRegistry()
        mockregistry.add('my_first_app', MockCustomSql1)
        mockregistry.add('my_first_app', MockCustomSql2)
        mockregistry.add('my_second_app', MockCustomSql3)

        iter_list = list(mockregistry)
        self.assertTrue(isinstance(iter_list[0], MockCustomSql1))
        self.assertTrue(isinstance(iter_list[1], MockCustomSql2))
        self.assertTrue(isinstance(iter_list[2], MockCustomSql3))

    def test_iter_appnames(self):
        class MockCustomSql1(customsql_registry.AbstractCustomSql):
            pass

        class MockCustomSql2(customsql_registry.AbstractCustomSql):
            pass

        class MockCustomSql3(customsql_registry.AbstractCustomSql):
            pass

        mockregistry = customsql_registry.MockableRegistry()
        mockregistry.add('my_first_app', MockCustomSql1)
        mockregistry.add('my_first_app', MockCustomSql2)
        mockregistry.add('my_second_app', MockCustomSql3)

        self.assertEqual(['my_first_app', 'my_second_app'],
                         list(mockregistry.iter_appnames()))

    def test_iter_customsql_in_appname(self):
        class MockCustomSql1(customsql_registry.AbstractCustomSql):
            pass

        class MockCustomSql2(customsql_registry.AbstractCustomSql):
            pass

        class MockCustomSql3(customsql_registry.AbstractCustomSql):
            pass

        mockregistry = customsql_registry.MockableRegistry()
        mockregistry.add('my_first_app', MockCustomSql1)
        mockregistry.add('my_first_app', MockCustomSql2)
        mockregistry.add('my_second_app', MockCustomSql3)

        iter_list = list(mockregistry.iter_customsql_in_app('my_first_app'))
        self.assertEqual(2, len(iter_list))
        self.assertTrue(isinstance(iter_list[0], MockCustomSql1))
        self.assertTrue(isinstance(iter_list[1], MockCustomSql2))


class TestAbstractCustomSqlCreateDropStatementsFromSqlCode(test.TestCase):
    def test_drop_trigger_drop_statements_from_sql_code(self):
        result = customsql_registry.AbstractCustomSql().make_drop_trigger_statements_from_sql_code(
            """
            CREATE TRIGGER my_fancy_trigger
                BEFORE INSERT OR UPDATE ON my_table
                FOR EACH ROW
                    EXECUTE PROCEDURE my_fancy_function();
            create trigger my_simple_trigger
                after insert on my_table
                for each row
                    execute procedure my_simple_function();
            """)
        self.assertEqual(result, [
            'DROP TRIGGER IF EXISTS my_fancy_trigger ON my_table',
            'DROP TRIGGER IF EXISTS my_simple_trigger ON my_table',
        ])

    def test_make_drop_function_statements_from_sql_code(self):
        result = customsql_registry.AbstractCustomSql().make_drop_function_statements_from_sql_code(
            """
                create function mysimple_function()
                returns void as $$
                begin
                end;
                $$ language plpgsql;

                create function invalidfunction

                CREATE OR REPLACE FUNCTION myfancy_function(
                    firsarg bigint,
                    secondarg text
                )
                RETURNS text AS $$
                BEGIN
                END;
                $$ LANGUAGE plpgsql;
            """)
        self.assertEqual(result, [
            'DROP FUNCTION IF EXISTS mysimple_function () RESTRICT',
            'DROP FUNCTION IF EXISTS myfancy_function (firsarg bigint, secondarg text) RESTRICT',
        ])

    def test_make_drop_index_statements_from_sql_code(self):
        result = customsql_registry.AbstractCustomSql().make_drop_index_statements_from_sql_code(
            """
            CREATE INDEX my_search_index
                ON ievv_pageframework_pagecontent
                USING GIN (search_vector);

            create index my_other_search_index
                on ievv_pageframework_pagecontent
                using gin (search_vector);
            """)
        self.assertEqual(result, [
            'DROP INDEX IF EXISTS my_search_index RESTRICT',
            'DROP INDEX IF EXISTS my_other_search_index RESTRICT',
        ])

    def test_make_drop_type_statements_from_sql_code(self):
        result = customsql_registry.AbstractCustomSql().make_drop_type_statements_from_sql_code(
            """
            create type my_simple_type as (size bigint);

            CREATE TYPE my_fancy_type AS (
                firstarg      bigint,
                secondarg     bigint
                thirdarg      text
            );
            """)
        self.assertEqual(result, [
            'DROP TYPE IF EXISTS my_simple_type RESTRICT',
            'DROP TYPE IF EXISTS my_fancy_type RESTRICT',
        ])

    def test_make_drop_statements_from_sql_code(self):
        result = customsql_registry.AbstractCustomSql().make_drop_statements_from_sql_code(
            """
            create type my_simple_type as (size bigint);
            
            create index my_search_index
                on ievv_pageframework_pagecontent
                using gin (search_vector);
                
            create function mysimple_function()
            returns void as $$
            begin
            end;
            $$ language plpgsql;

            create trigger my_simple_trigger
            after insert on my_table
            for each row
                execute procedure my_simple_function();
            """)
        self.assertEqual(result, [
            'DROP INDEX IF EXISTS my_search_index RESTRICT',
            'DROP TYPE IF EXISTS my_simple_type RESTRICT',
            'DROP FUNCTION IF EXISTS mysimple_function () RESTRICT',
            'DROP TRIGGER IF EXISTS my_simple_trigger ON my_table',
        ])
