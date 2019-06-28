# -*- coding: utf-8 -*-

# @Date    : 2019-06-27
# @Author  : Peng Shiyu

from __future__ import unicode_literals, print_function
import six

from puremysql.sql_builder import SQLBuilder


class SQLBuilderUtil(object):
    @classmethod
    def get_key_str(cls, fields):
        """
        获取 键 的字符串拼接
        :param fields: str / list
        :return: str

        eg:
        >>> SQLBuilderUtil.get_key_str(["name", "age"])
        '`name`, `age`'

        >>> SQLBuilderUtil.get_key_str("name, age")
        'name, age'

        """
        if isinstance(fields, six.string_types):
            fields_str = fields
        else:
            fields_str = ", ".join(["`{}`".format(field) for field in fields])

        return fields_str

    @classmethod
    def get_value_str(cls, keys):
        """
        获取 值 的字符串拼接
        :param keys: list
        :return: str

        eg:
        >>> SQLBuilderUtil.get_value_str(["name", "age"])
        '%(name)s, %(age)s'

        """
        return ", ".join(["%({})s".format(key) for key in keys])

    @classmethod
    def get_key_value_str(cls, keys):
        """
        获取 键-值 的字符串拼接
        :param keys: list
        :return: str

        eg:
        >>> SQLBuilderUtil.get_key_value_str(["name", "age"])
        '`name`=%(name)s, `age`=%(age)s'

        """
        return ", ".join(["`{0}`=%({0})s".format(key) for key in keys])

    @classmethod
    def get_select_sql(cls, table, fields, where):
        """
        获取简单的select 语句
        :param table: str
        :param fields: list / str
        :param where: str
        :return: str

        eg:
        >>> SQLBuilderUtil.get_select_sql("student", ["name", "age"], "id=1")
        'SELECT `name`, `age` FROM student WHERE id=1'

        """

        fields_str = cls.get_key_str(fields)

        sql_builder = SQLBuilder()
        sql_builder.select(fields_str)
        sql_builder.from_(table)
        sql_builder.where(where)

        return sql_builder.build()

    @classmethod
    def get_insert_sql(cls, table, keys):
        """
        获取简单的带参insert 语句
        :param table: str
        :param keys: list
        :return: str

        eg:
        >>> SQLBuilderUtil.get_insert_sql("student", ["name", "age"])
        'INSERT INTO student (`name`, `age`) VALUES  (%(name)s, %(age)s)'

        """
        keys_str = cls.get_key_str(keys)
        values_str = cls.get_value_str(keys)

        sql_builder = SQLBuilder()
        sql_builder.insert_into(table)
        sql_builder.parentheses(keys_str)
        sql_builder.values()
        sql_builder.parentheses(values_str)

        return sql_builder.build()

    @classmethod
    def get_delete_sql(cls, table, where):
        """
        获取简单的delete 语句
        :param table: str
        :param where: str
        :return: str

        eg:
        >>> SQLBuilderUtil.get_delete_sql("student", "id=1")
        'DELETE FROM student WHERE id=1'

        """

        sql_builder = SQLBuilder()
        sql_builder.delete_from(table)
        sql_builder.where(where)

        return sql_builder.build()

    @classmethod
    def get_update_sql(cls, table, keys, where):
        """
        获取简单的带参update 语句
        :param table: str
        :param keys: list
        :param where: str
        :return: str

        eg:
        >>> SQLBuilderUtil.get_update_sql("student", ["name", "age"], "id=1")
        'UPDATE student SET `name`=%(name)s, `age`=%(age)s WHERE id=1'

        """
        key_value_str = cls.get_key_value_str(keys)
        sql_builder = SQLBuilder()
        sql_builder.update(table)
        sql_builder.set(key_value_str)
        sql_builder.where(where)

        return sql_builder.build()

    @classmethod
    def get_list_keys(cls, data):
        """
        列表中字典key值校验
        :param data: list(dict)
        :return: list(key)

        eg:
        >>> user1 = {"name": "Tom", "age": 23}
        >>> user2 = {"name": "Jack", "age": 24}
        >>> user3 = {"name": "Jack", "age": 24, "school": "Stanford University"}

        >>> data = [user1, user2]
        >>> SQLBuilderUtil.get_list_keys(data)
        ['name', 'age']

        >>> data = [user1, user2, user3]
        >>> SQLBuilderUtil.get_list_keys(data)
        Traceback (most recent call last):
            ...
        Exception: data key not equal!

        """

        keys = data[0].keys()
        for item in data:
            if item.keys() != keys:
                raise Exception("data key not equal!")

        return [key for key in keys]


if __name__ == '__main__':
    import doctest

    doctest.testmod()
