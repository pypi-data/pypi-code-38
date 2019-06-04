import sqlite3


def read_SQLite_table(db, table, sql=None, field='*'):
    '''
    返回SQLite中表的查询结果
    :param db: <str> 数据库文件名
    :param table: <str> 要查的表名
    :param sql: <str> 要执行的SQL语句, 不指定的话就生成一个SQL语句
    :param field: <field> 要查询的字段, 不指定就查询所有字段;
        可以接收<list, tuple, str>等类型
    :param list_: <True, False>, 为True时返回列表, 为False时以生成器形式返回
    '''
    if not sql:
        if isinstance(field, (list, tuple)):
            field = ','.join(field)
        sql = 'select {} from {};'.format(field, table)
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        cur.execute(sql)
        result = cur.fetchall()
        result = [list(e) for e in result]
        return result


def showtables(db):
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        cur.execute('SELECT name FROM sqlite_master WHERE type="table" ORDER BY name;')
        tables = [r for r in cur.fetchall()]
    return tables


def gen_insert_sql(table_name, content, fields=None, filename=None):
    """
    接收一个CSV内容, 生成插入语句
    :param table_name: 要插入的表名
    :param content: list, 要写入的内容
    :param: fields: list, 要写入的字段名, 不输入时默认为所有字段
    :param filename: 要写入的文件名
    :return:
    """
    if fields:
        pat = 'INSERT INTO {}\n      ({})\nVALUES{};\n'
        sql = pat.format(table_name, ','.join(fields),
                         ',\n      '.join(['({})'.format(','.join(['"{}"'.format(f) for f in e])) for e in content]))
    else:
        pat = 'INSERT INTO {}\nVALUES{};\n'
        sql = pat.format(table_name,
                         ',\n      '.join(['({})'.format(','.join(['"{}"'.format(f) for f in e])) for e in content]))
    if filename:
        with open(filename, mode='a+', encoding='utf8') as f:
            f.write(sql)
    return sql
