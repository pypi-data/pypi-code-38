#!/usr/bin/python
# -*- coding: utf-8 -*-

import happybase

from service_config import GET_CONF
from kdbase.log import logger

__thrift_host = GET_CONF('hbase_thrift', 'host')
__thrift_port = int(GET_CONF('hbase_thrift', 'port'))

thrift_conn = None
retry_times = 3

# throws ConnectTimeOutException
def get_thrift_conn():
    global thrift_conn # pylint: disable=W0603
    if not thrift_conn:
        thrift_reconn()

# throws ConnectTimeOutException
def thrift_reconn():
    global thrift_conn # pylint: disable=W0603
    if thrift_conn:
        thrift_conn.close()
    for i in range(retry_times):
        thrift_conn = happybase.Connection(
                __thrift_host, __thrift_port, timeout=120*1000)
        if thrift_conn:
            break
    else:
        raise ConnectTimeOutException('thrift_reconn', retry_times)
    

# throws ConnectTimeOutException
def _put_cols(table, row, cols): #(column_family, column, data)
    col_dict = {}
    for (column_family, column, content) in cols:
        cf = '%s:%s' % (column_family, column)
        col_dict[cf] = content

    conn = get_thrift_conn()
    table = conn.table(table)

    table.put(row, col_dict, wal=True)
    return True

# throws ConnectTimeOutException
def put_cols(table, row, cols): #(column_family, column, data)
    succ = False
    for i in range(retry_times):
        try:
            ret = _put_cols(table, row, cols)
            succ = True
            break
        except Exception, e: # pylint: disable=W0703
            logger().error('exception:[%s]', str(e))
            thrift_reconn()
    if not succ:
        logger().info('put col failed %d times, table[%s], rowkey[%s]',
                      retry_times, table, row)
    return succ

# throws ConnectTimeOutException
def _put_col(table, row, column_family, column, content):
    cf = '%s:%s' % (column_family, column)
    conn = get_thrift_conn()
    table = conn.table(table)
    table.put(row, {cf : content}, wal=True)
    return True

# throws ConnectTimeOutException
def put_col(table, row, column_family, column, content):
    succ = False
    for i in range(retry_times):
        try:
            ret = _put_col(table, row, column_family, column, content)
            succ = True
            break
        except Exception, e:
            logger().error('exception:[%s]', str(e))
            thrift_reconn()
    if not succ:
        logger().info('put col failed %d times, rowkey[%s]', retry_times, row)
    return succ

# throws ConnectTimeOutException
def get_regions(table):
    conn = get_thrift_conn()
    table = conn.table(table)
    return table.regions()

# throws ConnectTimeOutException
def _get(table, row, column_family, column):
    conn = get_thrift_conn()
    table = conn.table(table)
    if column_family and column:
        columns = []
        columns.append('%s:%s' % (column_family, column))
        return table.row(row, columns=columns)
    elif column_family:
        columns = []
        columns.append('%s' % (column_family))
        return table.row(row, columns=columns)

    else:
        return table.row(row)

# throws ConnectTimeOutException
def get(table, row, column_family=None, column=None):
    succ = False
    for i in range(retry_times):
        ret = _get(table, row, column_family, column)
        succ = True
        return ret
    else:
        logger().error('exception:[%s]', str(e))
        thrift_reconn()
        logger().info('hbase get failed %d times, rowkey[%s]',
                      retry_times, row)
        raise ConnectTimeOutException('hbase get', retry_times)

# throws ConnectTimeOutException
def get_col(table, row, column_family, column):
    return get(table, row, column_family, column)

# throws ConnectTimeOutException
# columns must be ["family1:col1", "family2:col2"]
def _get_cols(table, row, columns):
    assert type(columns) == list
    conn = get_thrift_conn()
    table = conn.table(table)
    return table.row(row, columns=columns)


# columns must be ["family1:col1", "family2:col2"]
def get_cols(table, row, columns):
    succ = False
    for i in range(retry_times):
        ret = _get_cols(table, row, columns)
        succ = True
        return ret
    else:
        logger().error('exception:[%s]', str(e))
        thrift_reconn()
        logger().info('hbase get_cols failed %d times, rowkey[%s]',
                      retry_times, row)
        raise ConnectTimeOutException('hbase get', retry_times)

def delete(table, row, columns=None):
    conn = get_thrift_conn()
    table = conn.table(table)
    if columns:
        table.delete(row, columns=columns)
    else:
        table.delete(row)

def test():
    data = open('/tmp/test').read()
    print len(data)
    print put_col('kv_store_prd', 'test_wzs', 'data', 'data', data)
    return
    print get_col('file_table_prd_v2', '87-1234567890--11_22_70_seq_png', 'content', '!!!')
    return
    print put_cols(
        'users', 'wang', [('cf', 'sex', 'female'), ('cf', 'tag', '1')])
    print put_cols(
        'users', 'tang', [('cf', 'sex', 'male'), ('cf', 'tag', '2')])
    print put_cols(
        'users', 'zhang', [('cf', 'sex', 'female'), ('cf', 'tag', '2')])
    print get('users', 'cui')
    print get('users', 'tang')
    print get('users', 'cui', 'cf')
    print get('users', 'cui', 'cf', 'sex')
    print get_col('users', 'cui', 'cf', 'sex')

def main():
    print '1:', get_col('kv_store_prd', 'row', 'data', 'key')
    print put_col('kv_store_prd', 'row', 'data', 'key', 'val')

    print put_cols(
        'kv_store_prd', 'wang', [('data', 'sex', 'female'), ('data', 'tag', '1')])
    print '2:', get_col('kv_store_prd', 'wang', 'data', 'sex')
    print '3:', get_col('kv_store_prd', 'wang', 'data', 'tag')
    print '4:', get_cols('kv_store_prd', 'wang', ['data:tag', 'data:sex', 'data:b'])
    delete('kv_store_prd', 'wang')
    print '5', get_cols('kv_store_prd', 'wang', ['data:tag', 'data:sex', 'data:b'])


if __name__ == '__main__':
    main()
