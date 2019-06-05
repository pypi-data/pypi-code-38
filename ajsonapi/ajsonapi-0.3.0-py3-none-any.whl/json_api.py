# Copyright © 2018-2019 Roel van der Goot
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
"""Module jsonapi provides class JSON_API."""

from itertools import chain

from ajsonapi.id_column import IdColumn
from ajsonapi.table import Table


class JSON_API(Table):
    """JSON_API is the base class from which users derive object model
    classes. Classes that derive from JSON_API will result in URLs and methods
    in the web server through which to manipulate the object model.
    """
    # pylint: disable=invalid-name

    @classmethod
    def __init_subclass__(cls):
        super().__init_subclass__()
        cls.id = IdColumn(cls.name)
        cls.columns.insert(0, cls.id)
        cls.constraints.insert(0, cls.id)

    @classmethod
    async def create(cls):
        """Creates the SQL table, which represents this class of the object
        model, in the database.

        Args:
            pool: Connection pool to the database in which to create the SQL
               tables for this class of the object model.
        """
        table_fields = ',\n    '.join(
            chain((col.sql() for col in cls.columns),
                  (col.sql_constraints() for col in cls.constraints)))
        stmts = (f'CREATE SEQUENCE IF NOT EXISTS seq_{cls.name};\n'
                 f'CREATE TABLE IF NOT EXISTS {cls.name} (\n'
                 f'    {table_fields}\n'
                 f');\n')
        async with cls.pool.acquire() as connection:
            await connection.execute(stmts)


def init(pool):
    """Initializes all JSON_API subclasses."""

    for json_api in JSON_API.__subclasses__():
        json_api.pool = pool
