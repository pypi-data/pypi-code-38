import openProduction.connectors.BaseConnector as plugintypes
from openProduction.common import Types, misc
import socket
import logging
import traceback
import pymysql
import json

class MySQLConnector(plugintypes.BaseConnector):    
    def __init__(self):
        __fields__ = [Types.String("user", "Username to access SQL database", ""),
                      Types.Password("password", "Password to access SQL database (WARNING: do not use a root-db password. This password is stored in plain-text)", ""),
                      Types.String("hostname", "Hostname (or IP) of SQL database", ""),
                      Types.Int("port", "Port of SQL database", "", minVal=1, maxVal=65535)
                      ]
        super(MySQLConnector, self).__init__(__fields__)
        self._unconfigured = True
        self.logger = logging.getLogger(misc.getAppName())
        self.err = ""
        self.transactionOpen = False
        
    def getValueDataType(self, value):
        dt = ""
        if isinstance(value, Types.Int):
            dt = "INT"
        elif isinstance(value, Types.Bool):
            dt = "BIT"
        elif isinstance(value, Types.Float):
            dt = "FLOAT"
        elif isinstance(value, Types.String):
            dt = "TEXT"
        elif isinstance(value, Types.Date):
            dt = "DATETIME"
        else:
            raise RuntimeError("unsupported data type %s"%Types.String)
        return dt
    
    def getDescription(self):
        return "This connector uses your local (or a shared) file system"
    
    def listDatabases(self):
        connection = pymysql.connect(host=self.host, user=self.username, port=self.port, password=self.password, charset=self.charset, cursorclass=pymysql.cursors.DictCursor)
        sql = "SHOW DATABASES;"        
        c = connection.cursor()
        r = c.execute(sql)
        if r > 0:
            rv = c.fetchall()
        else:
            rv = []
        
        return rv
    
    def deleteRows(self, dbname, table, filt):
        sql = "DELETE FROM `%s`.`%s` WHERE %s;"%(dbname, table, filt)
        rv, data = self._execSQLWithFetch(sql)
        if rv == plugintypes.ConnectorErrors.NO_ERROR and data == None:
            rv = plugintypes.ConnectorErrors.NOT_FOUND
        return rv
        
    def deleteDatabase(self, dbName):
        sql = "DROP DATABASE %s;"%dbName
        rv, rowID = self._execSQLWithoutFetch(sql)
        return rv
    
    def createDatabase(self, dbName):
        notExists = ""    
        sql = "CREATE DATABASE %s %s;"%(notExists, dbName)
        rv, rowID = self._execSQLWithoutFetch(sql)
        return rv
    
    def createTables(self, dbName, tables):
        sqls = []
        params = []
        for tab in tables:
            sql, param = self._createTable(dbName, tab)
            sqls.append(sql)
            params.append(param)
        
        rv, rowID = self._execSQLWithoutFetch(sqls, params=params)
        return rv
    
    def createTable(self, dbName, tableName, columns):
        tables = [{"columns": columns, "name": tableName}]
        return self.createTables(dbName, tables)
    
    def _createTable(self, dbName, table):
        primaryKey = []
        references = []
        lines = []
        columns = table["columns"]
        tableName = table["name"]
        escapes = []
        jsonChecks = []
        for col in columns:
            colName = col["name"]
            dtype = col["type"]
            notNull = ""
            if "notNull" in col:
                if col["notNull"] == True:
                    notNull = "NOT NULL"
            autoInc = ""
            if "autoIncrement" in col:
                if col["autoIncrement"] == True:
                    autoInc = "AUTO_INCREMENT"
            unique = ""
            if "unique" in col:
                if col["unique"] == True:
                    unique = "UNIQUE"
            default = ""
            if "default" in col:
                default = "DEFAULT %s"
                escapes.append(str(col["default"]))
            if "constraint" in col:
                constraint = col["constraint"]
            else:
                constraint = ""
            line = "`%s` %s %s %s %s %s %s"%(colName, dtype, notNull, unique, autoInc, default, constraint)
            lines.append(line)
            
            if "primaryKey" in col:
                if col["primaryKey"] == True:
                    primaryKey.append(colName)
                    
            if "foreign" in col:
                ref = "FOREIGN KEY (`%s`) REFERENCES `%s`(`%s`) ON DELETE CASCADE ON UPDATE CASCADE"%(colName, col["foreign"][0],col["foreign"][1])
                references.append(ref)
                
            if dtype.lower() == "json":
                jsonChecks.append("CHECK (JSON_VALID(%s))"%colName)
        
        if primaryKey != []:
            keys = ",".join(primaryKey)
            primaryKey = "PRIMARY KEY (%s)"%keys
            lines.append(primaryKey)
            
        uniqueLines = []
        if "uniqueKey" in table:
            if type(table["uniqueKey"]) == type([]):
                #list of lists?
                if type(table["uniqueKey"][0]) == type([]):        
                    for uniques in table["uniqueKey"]:
                        uniqueCols = ['`' +x+'`' for x in uniques]
                        uniqueLines.append("UNIQUE KEY(%s)"%(",".join(uniqueCols)))
                else:
                    uniqueCols = ['`' +x+'`' for x in table["uniqueKey"]]
                    uniqueLines.append("UNIQUE KEY(%s)"%(",".join(uniqueCols)))

        lines = lines + references + uniqueLines + jsonChecks

        content = ",\n".join(lines)
        sql = "CREATE TABLE `%s`.`%s` (%s);"%(dbName, tableName, content)
        # print(sql)
        return sql, escapes
    
    def changeColumnDataType(self, dbName, tableName, columnName, dataTypeString):
        sql = "ALTER TABLE %s.%s MODIFY COLUMN %s %s;"%(dbName, tableName, columnName, dataTypeString)
        rv, rowID = self._execSQLWithoutFetch(sql)
        return rv
    
    def createColumn(self, dbName, tableName, columnName, dataTypeString, constraints=None):
        if constraints == None:
            constraints = ""
        sql = "ALTER TABLE %s.%s ADD %s %s %s;"%(dbName, tableName, columnName, dataTypeString, constraints)
        rv, rowID = self._execSQLWithoutFetch(sql)
        return rv
    
    def saveValues(self, dbName, table, values):
        colNames = []
        valNames = []
        vals = []
        for val in values:
            colNames.append("`" + val.name + "`")
            valNames.append("%s")
            vals.append(val.value)
        
        valNames = (", ").join(valNames)
        colNames = (", ").join(colNames)
        sql = "INSERT INTO `%s`.`%s` (%s) VALUES (%s);"%(dbName, table, colNames, valNames)
        return self._execSQLWithoutFetch(sql, params=vals)
    
    def addRow(self, dbName, table, entries):        
        colNames = []
        valArr = []
        vals = []
        
        if type(entries) == type([]):
            for val in entries:
                colNames.append("`" + val.name + "`")
                valArr.append("%s")
                vals.append(val.value)
        elif type(entries) == type({}):
            for key, val in entries.items():
                colNames.append("`" + key + "`")
                valArr.append("%s")
                if type(val) == type({}):
                    val = json.dumps(val)
                vals.append(val)
        
        valArr = (", ").join(valArr)
        colNames = (", ").join(colNames)
        sql = "INSERT INTO `%s`.`%s` (%s) VALUES (%s);"%(dbName, table, colNames, valArr)
        return self._execSQLWithoutFetch(sql, params=vals)
    
    def updateRow(self, dbName, table, entries, filt):
        colNames = []
        vals = []
        
        if type(entries) == type([]):
            for val in entries:
                colNames.append(val.name)
                vals.append(val.value)
        elif type(entries) == type({}):
            for key, val in entries.items():
                colNames.append(key)
                if type(val) == type({}):
                    val = json.dumps(val)
                vals.append(val)
        
        cols = ["%s"%x+"=%s" for x in colNames]
        values = ",".join(cols)
        sql = "UPDATE `%s`.`%s` SET %s WHERE %s;"%(dbName, table, values, filt)
        rv, row_id = self._execSQLWithoutFetch(sql, params=vals)
        return rv
        
    def getData(self, dbName, table, columns, filt=None, joins=None, orderBy=None):
        colNames = (", ").join(columns)
        if filt != None:
            filt = "WHERE " + filt
        else:
            filt = ""
        if joins != None:
             joins = ["INNER JOIN "+x for x in joins]
             joins = "\n".join(joins)
        else:
            joins = ""
            
        if orderBy != None:
            order = "ORDER BY %s"%orderBy
        else:
            order = ""
            
        sql = "SELECT %s from `%s`.`%s` %s %s %s;"%(colNames, dbName, table, joins, filt, order)
        return self._execSQLWithFetch(sql)
    
    def getColumnDataType(self, dbName, table, columnName):
        sql = "SELECT `DATA_TYPE` \
FROM `INFORMATION_SCHEMA`.`COLUMNS` \
WHERE `TABLE_SCHEMA`='%s' \
AND `TABLE_NAME`='%s' \
AND `COLUMN_NAME`='%s';"%(dbName, table, columnName) 
        ok, rv = self._execSQLWithFetch(sql)
        
        colType = ""
        if ok == plugintypes.ConnectorErrors.NO_ERROR and rv != None:
            if len(rv) > 0:
                colType = rv[0]["DATA_TYPE"].upper()
        return ok, colType
    
    def dataBaseExists(self, dbName):
        ok = True
        sql = "SELECT SCHEMA_NAME \
FROM INFORMATION_SCHEMA.SCHEMATA \
WHERE SCHEMA_NAME = '%s';"%dbName
        ok, rv = self._execSQLWithFetch(sql)
        if ok == plugintypes.ConnectorErrors.NO_ERROR and rv != None:
            ok = False
        return ok
    
    def tableExists(self, dbName, table):
        ok = True
        sql = "SELECT *  \
FROM information_schema.tables \
WHERE table_schema = '%s'  \
AND table_name = '%s'"%(dbName, table)
        ok, rv = self._execSQLWithFetch(sql)
        if ok == plugintypes.ConnectorErrors.NO_ERROR and rv != None:
            ok = False
        return ok
    
    def getColumnNames(self, dbName, table):
        colNames = []
        
        sql = "SELECT `COLUMN_NAME` \
FROM `INFORMATION_SCHEMA`.`COLUMNS` \
WHERE `TABLE_SCHEMA`='%s' \
AND `TABLE_NAME`='%s';"%(dbName, table)
        ok, rv = self._execSQLWithFetch(sql)
        
        if ok == plugintypes.ConnectorErrors.NO_ERROR and rv != None:
            for col in rv:
                colNames.append(col["COLUMN_NAME"])

        return ok, colNames
    
    def _execSQLWithFetch(self, sql, db=None, params=[]):
        data = None
        rv = plugintypes.ConnectorErrors.NO_ERROR
        
        con = pymysql.connect(host=self.host,
                             user=self.username,
                             port=self.port,
                             password=self.password,
                             charset=self.charset,
                             db=db,
                             max_allowed_packet=32*1024*1024,
                             cursorclass=pymysql.cursors.DictCursor)               
        
        try:
            c = con.cursor()
            r = c.execute(sql, params)
            con.commit()
            if r > 0:
                data =  c.fetchall()
        except pymysql.err.OperationalError as e:
            if e.args[0] == 1044:
                rv = plugintypes.ConnectorErrors.FORBIDDEN
            else:
                self.logger.error("SQL statement '%s' failed with error message %s"%(sql, str(e)))
                self.logger.info("full traceback:\n%s"%traceback.format_exc())
                rv = plugintypes.ConnectorErrors.UNSPECIFIC
        except pymysql.err.ProgrammingError as e:
            if e.args[0] == 1007:
                rv = plugintypes.ConnectorErrors.EXISTS
            else:
                self.logger.error("SQL statement '%s' failed with error message %s"%(sql, str(e)))
                self.logger.info("full traceback:\n%s"%traceback.format_exc())
                rv = plugintypes.ConnectorErrors.UNSPECIFIC
        except pymysql.err.IntegrityError as e:
            if e.args[0] == 1062:
                rv = plugintypes.ConnectorErrors.EXISTS
            else:
                self.logger.error("SQL statement '%s' failed with error message %s"%(sql, str(e)))
                self.logger.info("full traceback:\n%s"%traceback.format_exc())
                rv = plugintypes.ConnectorErrors.UNSPECIFIC
        except pymysql.err.InternalError as e:
            if e.args[0] == 1008:
                rv = plugintypes.ConnectorErrors.NOT_FOUND
            else:
                self.logger.error("SQL statement '%s' failed with InternalError error message %s"%(sql, str(e)))
                self.logger.info("full traceback:\n%s"%traceback.format_exc())
                rv = plugintypes.ConnectorErrors.UNSPECIFIC                
        except Exception as e:
            rv = plugintypes.ConnectorErrors.UNSPECIFIC
            self.logger.error("SQL statement '%s' failed with error message %s"%(sql, str(e)))
            self.logger.info("full traceback:\n%s"%traceback.format_exc())     
        finally:
            c.close()
            
        return rv, data
    
    def startTransaction(self, db):
        rv = plugintypes.ConnectorErrors.NO_ERROR
        try:
            self.transactionOpen = True
            self.connection = pymysql.connect(host=self.host,
                                 user=self.username,
                                 port=self.port,
                                 password=self.password,
                                 charset=self.charset,
                                 db=db,
                                 max_allowed_packet=32*1024*1024,
                                 cursorclass=pymysql.cursors.DictCursor)
            self.connection.autocommit = False
        except Exception as e:
            rv = plugintypes.ConnectorErrors.UNSPECIFIC
            self.logger.error("mysql connection failed with %s error message %s"%(type(e), str(e)))
            self.logger.info("full traceback:\n%s"%traceback.format_exc())
        return rv
        
    def commitTransaction(self):
        rv = plugintypes.ConnectorErrors.NO_ERROR
        try:
            self.connection.commit()
        except Exception as e:
            rv = plugintypes.ConnectorErrors.UNSPECIFIC
            self.logger.error("mysql commit failed with %s error message %s"%(type(e), str(e)))
            self.logger.info("full traceback:\n%s"%traceback.format_exc())
            self.connection.rollback()
            self.logger.info("sql transaction rollback due to previsous commit error")
        finally:
            self.connection.close()
            self.transactionOpen = False
        return rv
    
    def rollbackTransaction(self):
        rv = plugintypes.ConnectorErrors.NO_ERROR
        try:
            self.connection.rollback()
        except Exception as e:
            rv = plugintypes.ConnectorErrors.UNSPECIFIC
            self.logger.error("mysql commit failed with %s error message %s"%(type(e), str(e)))
            self.logger.info("full traceback:\n%s"%traceback.format_exc())
        finally:
            self.connection.close()
            self.transactionOpen = False
        return rv
        
    def _execSQLWithoutFetch(self, sql, db=None, params=[]):
        rowID = None
        rv = plugintypes.ConnectorErrors.NO_ERROR
        
        if self.transactionOpen == False:
            connection = pymysql.connect(host=self.host,
                                 user=self.username,
                                 port=self.port,
                                 password=self.password,
                                 charset=self.charset,
                                 db=db,
                                 max_allowed_packet=32*1024*1024,
                                 cursorclass=pymysql.cursors.DictCursor)
        else:
            connection = self.connection
        
        try:
            with connection.cursor() as cursor:
                # Create a new record
                if type(sql) == type([]):
                    for idx in range(len(sql)):
                        cursor.execute(sql[idx], params[idx])
                else:
                    cursor.execute(sql, params)
        
            rowID = cursor.lastrowid
            
            if self.transactionOpen == False:
                connection.commit()
        except pymysql.err.OperationalError as e:
            if e.args[0] == 1044:
                rv = plugintypes.ConnectorErrors.FORBIDDEN
            else:
                self.logger.error("SQL statement '%s' failed with OperationalError error message %s"%(sql, str(e)))
                self.logger.info("full traceback:\n%s"%traceback.format_exc())
                rv = plugintypes.ConnectorErrors.UNSPECIFIC
        except pymysql.err.ProgrammingError as e:
            if e.args[0] == 1007:
                rv = plugintypes.ConnectorErrors.EXISTS
            else:
                self.logger.error("SQL statement '%s' failed with ProgrammingError error message %s"%(sql, str(e)))
                self.logger.info("full traceback:\n%s"%traceback.format_exc())
                rv = plugintypes.ConnectorErrors.UNSPECIFIC
        except pymysql.err.IntegrityError as e:
            if e.args[0] == 1062:
                rv = plugintypes.ConnectorErrors.EXISTS
            else:
                self.logger.error("SQL statement '%s' failed with IntegrityError error message %s"%(sql, str(e)))
                self.logger.info("full traceback:\n%s"%traceback.format_exc())
                rv = plugintypes.ConnectorErrors.UNSPECIFIC
        except pymysql.err.InternalError as e:
            if e.args[0] == 1008:
                rv = plugintypes.ConnectorErrors.NOT_FOUND
            else:
                self.logger.error("SQL statement '%s' failed with InternalError error message %s"%(sql, str(e)))
                self.logger.info("full traceback:\n%s"%traceback.format_exc())
                rv = plugintypes.ConnectorErrors.UNSPECIFIC
        except Exception as e:
            rv = plugintypes.ConnectorErrors.UNSPECIFIC
            self.logger.error("SQL statement '%s' failed with %s error message %s"%(sql, type(e), str(e)))
            self.logger.info("full traceback:\n%s"%traceback.format_exc())
        finally:
            if self.transactionOpen == False:
                connection.close()
            
        return rv, rowID
    
    def errmsg(self):
        return self.err
    
    def _onNewConfig(self):
        rv = plugintypes.ConnectorErrors.NO_ERROR
        self.port = self.config["port"]
        self.username = self.config["user"]
        self.password = self.config["password"]
        self.charset = 'utf8'
            
        host = self.config["hostname"]
        try:
            self.logger.info("trying to resolve host %s"%host)
            self.host = socket.gethostbyname(host)
        except:
            rv = plugintypes.ConnectorErrors.NOT_FOUND
            self.logger.error("Error resolving host %s"%str(host))
            self.logger.info("full traceback:\n%s"%traceback.format_exc())
            
        if rv == plugintypes.ConnectorErrors.NO_ERROR:
            self.logger.info("host %s resolved to IP %s"%(host, self.host))
            try:
                self.logger.info("trying to connect to db-server %s:%d"%(self.host, self.port))    
                pymysql.connect(host=self.host, user=self.username, port=self.port, password=self.password, charset=self.charset, cursorclass=pymysql.cursors.DictCursor)
                self.logger.info("...ok")
            except:
                rv = plugintypes.ConnectorErrors.FORBIDDEN
                self.logger.error("Error conencting to mysql server")
                self.logger.info("full traceback:\n%s"%traceback.format_exc())
        
        return rv