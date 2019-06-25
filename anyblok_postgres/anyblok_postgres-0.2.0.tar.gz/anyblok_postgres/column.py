# This file is a part of the AnyBlok / Postgres api project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2018 Georges RACINET <gracinet@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy import select, and_
from anyblok.column import Column
from anyblok.common import anyblok_column_prefix

json_null = object()


class Jsonb(Column):
    """PostgreSQL JSONB column

    ::

        from anyblok.declarations import Declarations
        from anyblok_postgres.column import Jsonb


        @Declarations.register(Declarations.Model)
        class Test:

            x = Jsonb()

    """
    sqlalchemy_type = pg.JSONB(none_as_null=True)


class Int4Range(Column):
    """PostgreSQL int4range column.

    Example usage, with this declaration::

        from anyblok.declarations import Declarations
        from anyblok_postgres.column import Jsonb


        @Declarations.register(Declarations.Model)
        class Test:

            col = Int4Range()

    one can perfom these::

        Test.insert(col="[1,3)")
        Test.insert(col="(4,8)")
        Test.query().filter(Test.col.contains(2))
        Test.query().filter(Test.col.contains([5, 6))

    """
    sqlalchemy_type = pg.INT4RANGE


class Int8Range(Column):
    """PostgreSQL int8range column.

    Usage is similar to  see :class:`Int4Range`.
    See also https://www.postgresql.org/docs/current/rangetypes.html

    Caveat (at least with psycopg2):

    In containment queries, passing integers that are within
    PostgreSQL's regular 'integer' type doesn't work because it lacks the
    ``::bigint`` cast. One workaround is to pass it as an inclusive 0 length
    range in string form such as::

        Test.query(Test.col.contains('[1, 1]')

    """
    sqlalchemy_type = pg.INT8RANGE


class NumRange(Column):
    """PostgreSQL numrange column.

    Usage is similar to  see :class:`Int4Range`, with
    :class:`decimal.Decimal` instances instead of integers.

    Caveat (at least with psycopg2):

    In containment queries, passing values that are integers or
    :class:`Decimal` instances equal to integers, such as ``Decimal('1')``
    doesn't work because they end up as litteral SQL integers, without the
    ``::numeric`` cast.

    One workaround is to pass them as inclusive 0 length ranges in string
    representation, such as::

        Test.query(Test.col.contains('[1, 1]')

    """
    sqlalchemy_type = pg.NUMRANGE


class DateRange(Column):
    """PostgreSQL daterange column.

    This range column can be used with Python :class:`date` instances.

    Example usage, with this declaration::

        from anyblok.declarations import Declarations
        from anyblok_postgres.column import Jsonb


        @Declarations.register(Declarations.Model)
        class Test:

            col = DateRange()

    one can perform these::

        Test.insert(col="['2001-03-12', '2002-01-01']")
        Test.insert(col="['2018-01-01', '2019-01-01')")
        Test.query().filter(Test.col.contains(date(2001, 4, 7)))
        Test.query().filter(Test.col.contains("['2018-02-01', '2018-03-01']")

    """
    sqlalchemy_type = pg.DATERANGE


class TsRange(Column):
    """PostgreSQL tsrange column (timestamps without time zones).

    This range column can be used with "naive" Python :class:`datetime`
    instances. Apart from that, usage is similar to :class:`DateRange`
    """
    sqlalchemy_type = pg.TSRANGE


class TsTzRange(Column):
    """PostgreSQL tstzrange column (timestamps with time zones).

    See also https://www.postgresql.org/docs/current/rangetypes.html

    This range column can be used with "non-naive" (i.e., with explicit
    ``tzinfo``) Python :class:`datetime`instances.
    Apart from taht, usage is similar to :class:`DateRange`
    """
    sqlalchemy_type = pg.TSTZRANGE


class LargeObject(Column):
    """PostgreSQL JSONB column

    ::

        from anyblok.declarations import Declarations
        from anyblok_postgres.column import LargeObject


        @Declarations.register(Declarations.Model)
        class Test:

            x = LargeObject()

        -----------------------------

        test = Test.insert()
        test.x = hugefile
        test.x  # get the huge file

    """
    sqlalchemy_type = pg.OID

    def __init__(self, *args, **kwargs):
        self.keep_blob = kwargs.pop('keep_blob', False)
        super(LargeObject, self).__init__(*args, **kwargs)

    def wrap_setter_column(self, fieldname):
        attr_name = anyblok_column_prefix + fieldname

        def setter_column(model_self, value):
            action_todos = set()
            if fieldname in model_self.loaded_columns:
                action_todos = model_self.registry.expire_attributes.get(
                    model_self.__registry_name__, {}).get(fieldname, set())

            self.expire_related_attribute(model_self, action_todos)
            pks = model_self.to_primary_keys()
            table = model_self.__table__.c
            dbfname = self.db_column_name or fieldname
            query = select([getattr(table, dbfname)])
            where_clause = [getattr(table, x) == y for x, y in pks.items()]
            if len(where_clause) == 1:
                where_clause = where_clause[0]
            else:
                where_clause = and_(*where_clause)

            query = query.where(where_clause)
            oldvalue = model_self.registry.execute(query).fetchone()
            if oldvalue:
                oldvalue = oldvalue[0]

            value = self.setter_format_value(
                value, oldvalue, model_self.registry)
            res = setattr(model_self, attr_name, value)
            self.expire_related_attribute(model_self, action_todos)
            return res

        return setter_column

    def setter_format_value(self, value, oldvalue, registry):
        if value is not None:
            cursor = registry.session.connection().connection.cursor()
            oid = oldvalue or 0
            if self.keep_blob:
                oid = 0

            lobj = cursor.connection.lobject(oid, 'wb')
            lobj.write(value)
            value = lobj.oid
            cursor.close()
        elif oldvalue and not self.keep_blob:
            cursor = registry.session.connection().connection.cursor()
            lobj = cursor.connection.lobject(oldvalue)
            lobj.unlink()
            cursor.close()

        return value

    def wrap_getter_column(self, fieldname):
        """Return a default getter for the field

        :param fieldname: name of the field
        """
        attr_name = anyblok_column_prefix + fieldname

        def getter_column(model_self):
            return self.getter_format_value(
                getattr(model_self, attr_name),
                model_self.registry
            )

        return getter_column

    def getter_format_value(self, value, registry):
        if value is not None:
            cursor = registry.session.connection().connection.cursor()
            lobj = cursor.connection.lobject(value, 'rb')
            return lobj.read()
