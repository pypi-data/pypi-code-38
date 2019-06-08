from orm_cloud.database_adapters.lucene_parser.lucene_parser import LuceneParser


class MsSqlAdapter:
    def __init__(self):
        pass

    def get_sql(self, select, table, where, sort_by=None, offset=None, limit=None):
        sql = self.create_select(select) + ' '
        sql += self.create_from(table) + ' '
        sql += self.create_where(where)
        if sort_by: sql += ' '  + self.create_sort_by(sort_by)
        if offset and limit:
            sql += ' ' + self.create_offset(offset, limit)

        return sql

    def create_select(self, fields):
        if fields == '*':
            return 'SELECT *'
        else:
            sql = 'SELECT '

            for field in fields:
                sql += '{} AS {}, '.format(field, fields[field])

            return sql.rstrip(', ')

    def create_from(self, table_or_view):
        return 'FROM {}'.format(table_or_view)

    def create_where(self, where):
        sql = 'WHERE '

        lucene_parser = LuceneParser()
        where_tuples = lucene_parser.parse(where)

        for tuple in where_tuples:
            sql += '{} {} {}'.format(tuple[0], tuple[1], tuple[2])

        return sql

    def create_sort_by(self, sort_by):
        parts = sort_by.split(',')

        sql = 'ORDER BY '
        for part in parts:
            sql += part[1:]

            if part[0] == '-':
                sql += ' DESC, '
            else:
                sql += ' ASC, '

        return sql.rstrip(', ')

    def create_limit(self, limit):
        return 'LIMIT {}'.format(limit)

    def create_offset(self, offset, limit):
        return 'OFFSET {} ROWS FETCH NEXT {} ROWS ONLY'.format(offset, limit)
