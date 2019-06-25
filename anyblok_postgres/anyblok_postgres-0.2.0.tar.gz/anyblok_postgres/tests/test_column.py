# This file is a part of the AnyBlok / Postgres project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from decimal import Decimal
from datetime import date, datetime, timezone
from anyblok.tests.testcase import DBTestCase
from anyblok.tests.test_column import simple_column
from anyblok_postgres.column import Jsonb, LargeObject
from anyblok_postgres import column as pgcol

from os import urandom


class TestColumns(DBTestCase):

    def test_jsonb(self):
        registry = self.init_registry(simple_column, ColumnType=Jsonb)
        val = {'a': 'Test'}
        test = registry.Test.insert(col=val)
        self.assertEqual(test.col, val)

    def test_jsonb_update(self):
        registry = self.init_registry(simple_column, ColumnType=Jsonb)
        test = registry.Test.insert(col={'a': 'test'})
        test.col['b'] = 'test'
        self.assertEqual(test.col, {'a': 'test', 'b': 'test'})

    def test_jsonb_simple_filter(self):
        registry = self.init_registry(simple_column, ColumnType=Jsonb)
        Test = registry.Test
        Test.insert(col={'a': 'test'})
        Test.insert(col={'a': 'test'})
        Test.insert(col={'b': 'test'})
        self.assertEqual(
            Test.query().filter(Test.col['a'].astext == 'test').count(), 2)

    def test_jsonb_null(self):
        registry = self.init_registry(simple_column, ColumnType=Jsonb)
        Test = registry.Test
        Test.insert(col=None)
        Test.insert(col=None)
        Test.insert(col={'a': 'test'})
        self.assertEqual(Test.query().filter(Test.col.is_(None)).count(), 2)
        self.assertEqual(Test.query().filter(Test.col.isnot(None)).count(), 1)

    def assert_query_contains(self, Model, c, expected):
        """Useful factorisation for range types."""
        self.assertEqual(
            set(Model.query().filter(Model.col.contains(c)).all()),
            set(expected))

    def test_int4range(self):
        registry = self.init_registry(simple_column,
                                      ColumnType=pgcol.Int4Range)
        Test = registry.Test
        t1 = Test.insert(col="[1,3)")
        t2 = Test.insert(col="(4,8)")
        self.assert_query_contains(Test, 2, [t1])
        self.assert_query_contains(Test, 4, ())
        self.assert_query_contains(Test, "[5,6]", [t2])

    def test_int8_range(self):
        registry = self.init_registry(simple_column,
                                      ColumnType=pgcol.Int8Range)
        Test = registry.Test
        t1 = Test.insert(col="[1,3)")
        bigint = 1 << 32  # PG's max for plain integer is 2**31-1
        t2 = Test.insert(col="({},{})".format(bigint, bigint*2))
        self.assert_query_contains(Test, bigint, ())
        self.assert_query_contains(Test, bigint + 10, [t2])
        self.assert_query_contains(Test,
                                   "({}, {})".format(bigint, bigint + 10),
                                   [t2])

        # just plain '2' literal wouldn't work as-is because it's
        # not passed as 2::bigint to PG
        self.assert_query_contains(Test, "[2, 2]", [t1])

    def test_numrange(self):
        registry = self.init_registry(simple_column,
                                      ColumnType=pgcol.NumRange)
        Test = registry.Test
        t1 = Test.insert(col="[1.5, 3)")
        t2 = Test.insert(col="(4, 7.5)")
        self.assert_query_contains(Test, Decimal(2.1), [t1])
        self.assert_query_contains(Test, Decimal('7.5'), ())
        self.assert_query_contains(Test, "[5,6]", [t2])

        # unfortunately, even Decimal(2) doesn't work, it gets passed as just
        # '2', so we need an explict range here too
        self.assert_query_contains(Test, "[2, 2]", [t1])

    def test_daterange(self):
        registry = self.init_registry(simple_column,
                                      ColumnType=pgcol.DateRange)
        Test = registry.Test
        t1 = Test.insert(col="['2001-03-12', '2002-01-01']")
        t2 = Test.insert(col="['2018-01-01', '2019-01-01')")
        self.assert_query_contains(Test, date(2001, 4, 7), [t1])
        self.assert_query_contains(Test, date(2019, 1, 1), ())
        self.assert_query_contains(Test, "['2018-02-01', '2018-03-01']", [t2])

    def test_tsrange(self):
        registry = self.init_registry(simple_column,
                                      ColumnType=pgcol.TsRange)
        Test = registry.Test
        t1 = Test.insert(col="['2001-03-12', '2002-01-01 00:00:00']")
        t2 = Test.insert(col="['2018-01-01', '2019-01-01')")
        self.assert_query_contains(Test, datetime(2001, 4, 7, 11, 0, 6), [t1])
        self.assert_query_contains(Test, datetime(2019, 1, 1), ())
        self.assert_query_contains(Test, "['2018-02-01', '2018-03-01']", [t2])

    def test_tstzrange(self):
        registry = self.init_registry(simple_column,
                                      ColumnType=pgcol.TsTzRange)
        Test = registry.Test
        utc = timezone.utc
        t1 = Test.insert(
            col="['2001-03-12 00:00:00+01', '2002-01-01 00:00:00+01']")
        t2 = Test.insert(
            col="['2018-01-01 00:00:00-03', '2019-01-01 00:00:00-03')")
        self.assert_query_contains(Test,
                                   datetime(2001, 4, 7, 11, 0, 6, tzinfo=utc),
                                   [t1])
        self.assert_query_contains(Test,
                                   datetime(2018, 1, 1, tzinfo=utc),
                                   ())
        self.assert_query_contains(Test, "['2018-02-01', '2018-03-01']", [t2])

    def test_large_object(self):
        registry = self.init_registry(simple_column, ColumnType=LargeObject)
        hugefile = urandom(1000)
        test = registry.Test.insert(col=hugefile)
        self.assertEqual(test.col, hugefile)
        oid1 = registry.execute('select col from test').fetchone()[0]
        self.assertNotEqual(oid1, hugefile)
        hugefile2 = urandom(1000)
        test.col = hugefile2
        registry.flush()
        self.assertNotEqual(test.col, hugefile)
        self.assertEqual(test.col, hugefile2)
        oid2 = registry.execute('select col from test').fetchone()[0]
        self.assertEqual(oid1, oid2)
