import os
import xml.etree.ElementTree as ET
from . import (AError, ACommandLineTool)


_commandlineTool = ACommandLineTool.CommandLineTool('mysql')
_commandlineTool.checkExistence()
def getCommandLineTool():
    return _commandlineTool


class MySQL_Error(AError.Error):
    pass


def fixSQLStr(s):
    """
    当使用os.system执行MySQL命令行时，SQL字符串中若包含`则必须用\转义，否则在Linux下会报错；比如：
    mysql -h127.0.0.1 -P3306 -uroot -p123456 -e "CREATE DATABASE `test`;"
    sh: test: command not found
    """
    s = s.replace('\\`', '`')
    if os.name != 'nt':
        s = s.replace('`', '\\`')
    return s


def execSQLStr(sqlStr, options):
    """执行一个普通的SQL语句"""
    if not sqlStr.endswith(';'):
        sqlStr += ';'
    sqlStr = fixSQLStr(sqlStr)

    cmd = ''
    if options != '':
        cmd += options + ' '
    cmd += '-e "%s"' % sqlStr

    _commandlineTool.execCommand(cmd)


def execSQLFile(sqlFilePath, options):
    """执行一个SQL文件"""
    cmd = ''
    if options != '':
        cmd += options + ' '
    cmd += '< %s' % sqlFilePath

    _commandlineTool.execCommand(cmd)


def getQueryResult(queryStr, options):
    """
    执行一个SELECT查询，并返回结果集    
    结果集为行列的二维数组
    """
    def parseRecordset(queryResultStr):
        root = ET.fromstring(queryResultStr)
        rows = []
        for rowNode in root.iterfind('row'):
            row = []
            for fieldNode in rowNode.iterfind('field'):
                row.append('' if fieldNode.text is None else fieldNode.text)
            rows.append(row)
        return rows

    if not queryStr.endswith(';'):
        queryStr += ';'
    # 默认使用AOS.systemOutput不需要fixSQLStr
    # queryStr = fixSQLStr(queryStr)

    cmd = '--xml=true '
    if options != '':
        cmd += options + ' '
    cmd += '-e "%s"' % queryStr

    result = _commandlineTool.execOutputCommand(cmd)

    skip = 'Warning: Using a password on the command line interface can be insecure.\n'
    if result.startswith(skip):
        result = result[len(skip):]

    return parseRecordset(result)


class Connection:
    def __init__(self, hostport=('127.0.0.1', 3306), userpass=('root',''), charset='utf8'):
        self.hostport = hostport
        self.userpass = userpass
        self.charset = charset
        self.commonOptionStr = '-h%s -P%d -u%s -p%s --default-character-set=%s' % (hostport[0], hostport[1], userpass[0], userpass[1], charset)

    def execSQLStr(self, sqlStr, extraOptions=''):
        options = self.commonOptionStr
        if extraOptions != '':
            options += ' ' + extraOptions
        execSQLStr(sqlStr, options)

    def execSQLFile(self, sqlFilePath, extraOptions=''):
        options = self.commonOptionStr
        if extraOptions != '':
            options += ' ' + extraOptions
        execSQLFile(sqlFilePath, options)

    def getQueryResult(self, queryStr, extraOptions=''):
        options = self.commonOptionStr
        if extraOptions != '':
            options += ' ' + extraOptions
        return getQueryResult(queryStr, options)

    def getDB(self, dbName):
        """注意并非使用MySQL use语法，多个DB对象可同时进行查询"""
        return DB(self, dbName)


class DB:
    def __init__(self, connection, name):
        self.connection = connection
        self.name = name

    def execSQLStr(self, sqlStr, extraOptions=''):
        options = '-D%s' % self.name
        if extraOptions != '':
            options += ' ' + extraOptions
        self.connection.execSQLStr(sqlStr, options)

    def execSQLFile(self, sqlFilePath, extraOptions=''):
        options = '-D%s' % self.name
        if extraOptions != '':
            options += ' ' + extraOptions
        self.connection.execSQLFile(sqlFilePath, options)

    def getQueryResult(self, queryStr, extraOptions=''):
        options = '-D%s' % self.name
        if extraOptions != '':
            options += ' ' + extraOptions
        return self.connection.getQueryResult(queryStr, options)