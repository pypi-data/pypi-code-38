from abc import ABC
from abc import abstractmethod

from geoalchemy2 import functions as geo_func
from geoalchemy2.types import Geometry
from sqlalchemy import func
from sqlalchemy import not_
from sqlalchemy import types


class BaseCheck(ABC):
    """Base class for all checks.

    A Check defines a constraint on a specific column and its table.
    One can validate if the constrain holds using the method `get_invalid()`.
    This method will return a list of rows (as named_tuples) which are invalid.
    """

    def __init__(self, column):
        self.column = column
        self.table = column.table

    @abstractmethod
    def get_invalid(self, session):
        """Return a list of rows (named_tuples) which are invalid.

        What is invalid is defined in the check. Returns an empty list if no
        invalid rows are present.

        :param session: sqlalchemy.orm.session.Session
        :return: list of named_tuples or empty list if there are no invalid
            rows
        """
        pass

    def get_valid(self, session):
        """Return a list of rows (named_tuples) which are valid.

        :param session: sqlalchemy.orm.session.Session
        :return: list of named_tuples or empty list if there are no valid rows
        """
        all_rows = self.to_check(session)
        invalid_row_ids = set([row.id for row in self.get_invalid(session)])
        valid = []
        for row in all_rows:
            if row.id not in invalid_row_ids:
                valid.append(row)
        return valid

    def to_check(self, session):
        """Return a Query object filtering on the rows this check is applied.

        :param session: sqlalchemy.orm.session.Session
        :return: sqlalchemy.Query
        """
        return session.query(self.table)

    def description(self):
        """Return a string explaining why rows are invalid according to this
        check.

        :return: string
        """
        return "Invalid value in column '%s'" % self.column

    def __repr__(self):
        return "<%s: %s.%s>" % (
            type(self).__name__,
            self.table.name,
            self.column.name
        )


class GeneralCheck(BaseCheck):
    """Check to specify with an SQL expression what's valid/invalid.

    Either specify what is valid with `criterion_valid` or what is invalid
    with `criterion_invalid`.
    The criterion should be  a sqlalchemy.sql.expression.BinaryExpression (https://docs.sqlalchemy.org/en/13/core/sqlelement.html#sqlalchemy.sql.expression.BinaryExpression)  # noqa
    with operators being operators being column within `self.table.columns`
    """

    def __init__(self, criterion_invalid=None, criterion_valid=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.criterion_invalid = criterion_invalid
        self.criterion_valid = criterion_valid

    def get_invalid(self, session):
        if self.criterion_invalid is not None:
            q_invalid = self.to_check(session).filter(self.criterion_invalid)
            return q_invalid.all()
        elif self.criterion_valid is not None:
            q_invalid = self.to_check(session).filter(~self.criterion_valid)
            return q_invalid.all()
        else:
            raise AttributeError("No valid/invalid criterion has been specified")

    def description(self):
        if self.criterion_valid is not None:
            condition = self.criterion_valid.compile(
                compile_kwargs={"literal_binds": True}
            )
        elif self.criterion_invalid is not None:
            condition = not_(self.criterion_invalid).compile(
                compile_kwargs={"literal_binds": True}
            )
        else:
            condition = "no condition specified"
        return "'%s'" % condition


class ConditionalCheck(BaseCheck):
    """Apply an additional filter `criterion` on the specified `check`

    The `criterion` is any SQL expression object applicable to the WHERE clause
    of a select statement.
    """

    def __init__(self, criterion, check, *args, **kwargs):
        super().__init__(check.column)
        self.criterion = criterion
        self.check = check

    def to_check(self, session):
        """Return a Query object on which this check is applied"""
        return session.query(self.check.table).filter(self.criterion)

    def get_invalid(self, session):
        # TODO: find a more elegant solution for conditional checks
        # now we monkey patch the checks method `to_check` and at the end
        # reverse the monkey patch.
        check = self.check
        old_applicable_func = check.to_check  # save old method
        check.to_check = self.to_check  # patch the applicable
        result = check.get_invalid(session)
        check.to_check = old_applicable_func  # reset old method
        return result

    def description(self):
        return "When '%s' holds, then %s" % (
            self.criterion.compile(compile_kwargs={"literal_binds": True}),
            self.check.description(),
        )


class ForeignKeyCheck(BaseCheck):
    """Check all values in `column` are in `reference_column`.

    Null values are ignored."""

    def __init__(self, reference_column, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reference_column = reference_column

    def get_invalid(self, session):
        q_invalid = self.to_check(session)
        invalid_foreign_keys_query = q_invalid.filter(
            self.column.notin_(session.query(self.reference_column)),
            self.column != None,
        )
        return invalid_foreign_keys_query.all()

    def description(self):
        return "Missing foreign key in column %s, expected reference to %s." % (
            self.column,
            self.reference_column,
        )


class UniqueCheck(BaseCheck):
    """Check all values in `column` are unique

    Null values are ignored."""

    def get_invalid(self, session):
        duplicate_values = (
            session.query(self.column)
            .group_by(self.column)
            .having(func.count(self.column) > 1)
        )
        q_invalid = self.to_check(session)
        invalid_uniques_query = q_invalid.filter(
            self.column.in_(duplicate_values)
        )
        return invalid_uniques_query.all()

    def description(self):
        return "Value in %s should to be unique" % self.column


class NotNullCheck(BaseCheck):
    """"Check all values in `column` that are not null"""

    def get_invalid(self, session):
        q_invalid = self.to_check(session)
        not_null_query = q_invalid.filter(self.column == None)
        return not_null_query.all()

    def description(self):
        return "Value in %s cannot be null" % self.column


class TypeCheck(BaseCheck):
    """Check all values in `column` that are of the column defined type.

    Null values are ignored."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expected_type = _sqlalchemy_to_sqlite_type(self.column.type)

    def get_invalid(self, session):
        if "sqlite" not in session.bind.dialect.dialect_description:
            return []
        q_invalid = self.to_check(session)
        invalid_type_query = q_invalid.filter(
            func.typeof(self.column) != self.expected_type,
            func.typeof(self.column) != "null",
        )
        return invalid_type_query.all()

    def description(self):
        return "Value in %s should to be of type %s" % (
            self.column,
            self.expected_type
        )


def _sqlalchemy_to_sqlite_type(column_type):
    """Convert the sqlalchemy column type to sqlite data type

    Returns the value similar as the sqlite 'typeof' function.
    Raises TypeError if the column type is unknown.

    :param column_type: sqlalchemy.column
    :return: (str)
    """
    if isinstance(column_type, types.TypeDecorator):
        column_type = column_type.impl

    if isinstance(column_type, types.String):
        return "text"
    elif isinstance(column_type, types.Float):
        return "real"
    elif isinstance(column_type, types.Integer):
        return "integer"
    elif isinstance(column_type, types.Boolean):
        return "integer"
    elif isinstance(column_type, types.Numeric):
        return "numeric"
    elif isinstance(column_type, types.Date):
        return "text"
    elif isinstance(column_type, Geometry):
        return "blob"
    elif isinstance(column_type, types.TIMESTAMP):
        return "text"
    else:
        raise TypeError("Unknown column type: %s" % column_type)


class GeometryCheck(BaseCheck):
    """Check all values in `column` are a valid geometry.

    Null values are ignored."""

    def get_invalid(self, session):
        q_invalid = self.to_check(session)
        invalid_geometries = q_invalid.filter(
            geo_func.ST_IsValid(self.column) != True, self.column != None
        )
        return invalid_geometries.all()

    def description(self):
        return "Value in %s is invalid geometry" % self.column


class GeometryTypeCheck(BaseCheck):
    """Check all values in `column` are of geometry type in defined in
    `column`.

    Null values are ignored"""

    def get_invalid(self, session):
        expected_geometry_type = _get_geometry_type(
            self.column, dialect=session.bind.dialect.name
        )
        q_invalid = self.to_check(session)
        invalid_geometry_types_q = q_invalid.filter(
            geo_func.ST_GeometryType(self.column) != expected_geometry_type,
            self.column != None,
        )
        return invalid_geometry_types_q.all()

    def description(self):
        return "Value in %s has invalid geometry type, expected geometry " \
               "type %s" % (self.column, self.column.type.geometry_type)


def _get_geometry_type(column, dialect):
    if dialect == "sqlite":
        return column.type.geometry_type
    elif dialect == "postgresql":
        geom_type = column.type.geometry_type.capitalize()
        return "ST_%s" % geom_type
    else:
        raise TypeError("Unexpected dialect %s" % dialect)


class EnumCheck(BaseCheck):
    """Check all values in `column` are within the defined Enum values of
    `column`.

    Unexpected values are values not defined by its enum_class.

    Null values are ignored"""

    def get_invalid(self, session):
        q_invalid = self.to_check(session)
        invalid_values_q = q_invalid.filter(
            self.column.notin_(list(self.column.type.enum_class))
        )
        return invalid_values_q.all()

    def description(self):
        return (
            "Value in %s has invalid value, expected one of the "
            "following values %s" % (
                self.column,
                list(self.column.type.enum_class)
            )
        )
