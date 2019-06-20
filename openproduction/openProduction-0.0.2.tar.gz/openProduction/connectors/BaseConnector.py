from yapsy.IPlugin import IPlugin
from openProduction.connectors import Config
import traceback
from openProduction.common import misc
import logging
from enum import Enum

PROD_RUN_PRE = "Product_"
PROD_RUN_STAT_PRE = "Station_"

class ConnectorErrors(Enum):
    NO_ERROR = 0
    INVALID_CONFIG = 1
    EXISTS = 2
    FORBIDDEN = 3
    NOT_FOUND = 4
    UNSPECIFIC = 5
    INVALID_PARAM = 6

class BaseConnector(IPlugin):
    def __init__(self, configDescription):
        super(BaseConnector, self).__init__()
        self.configDescription = configDescription
        self.logger = logging.getLogger(misc.getAppName())
        try:
            self.config = Config.Config(configDescription)            
        except Exception as e:
            self.logger.error("loading connector config failed with error message %s"%str(e))
            self.logger.info("full traceback:\n%s"%traceback.format_exc())
            self.config = []
            
    def startTransaction(self, dbName):
        raise NotImplementedError("startTransaction method has to be defined in connector's plugin")
    
    def commitTransaction(self):
        raise NotImplementedError("commitTransaction method has to be defined in connector's plugin")
        
    def rollbackTransaction(self):
        raise NotImplementedError("rollbackTransaction method has to be defined in connector's plugin")
            
    def getValueDataType(self, value):
        raise NotImplementedError("getValueDatatype method has to be defined in connector's plugin")
    
    def createColumn(self, dbName, tableName, columnName, dataTypeString, constraints=None):
        raise NotImplementedError("createDatabase method has to be defined in connector's plugin")
    
    def createDatabase(self, dbName):
        raise NotImplementedError("createDatabase method has to be defined in connector's plugin")
    
    def deleteDatabase(self, dbName):
        raise NotImplementedError("deleteDatabase method has to be defined in connector's plugin")
    
    def createTables(self, dbName, tables):
        raise NotImplementedError("createTables method has to be defined in connector's plugin")
    
    def createTable(self, dbName, tableName, columns):
        raise NotImplementedError("createTable method has to be defined in connector's plugin")
        
    def listDatabases(self):
        raise NotImplementedError("createTable method has to be defined in connector's plugin")

    def addRow(self, dbName, table, entries):
        raise NotImplementedError("addRow method has to be defined in connector's plugin")
        
    def updateRow(self, dbName, table, entries, filt):
        raise NotImplementedError("updateRow method has to be defined in connector's plugin")
        
    def deleteRows(self, dbname, table, filt):
        raise NotImplementedError("deleteRows method has to be defined in connector's plugin")
        
    def getData(self, dbName, table, columns, filt=None):
        raise NotImplementedError("getData method has to be defined in connector's plugin")
    
    def getColumnNames(self, dbName, table):
        raise NotImplementedError("getColumnNames method has to be defined in connector's plugin")
    
    def getColumnContent(self, dbName, table, columnName):
        raise NotImplementedError("getColumnContent method has to be defined in connector's plugin")
        
    def getColumnDataType(self, dbName, table, columnName):
        raise NotImplementedError("getColumnDataType method has to be defined in connector's plugin")
    
    def getDescription(self):
        raise NotImplementedError("getDescription method has to be defined in connector's plugin")
        
    def _onNewConfig(self):
        raise NotImplementedError("_onNewConfig method has to be defined in connector's plugin")
        
    def changeColumnDataType(self, dbName, table, columnName, dataTypeString):
        raise NotImplementedError("changeColumnDataType method has to be defined in connector's plugin")
        
    def saveValues(self, dbName, table, values):
        raise NotImplementedError("saveValues method has to be defined in connector's plugin")
        
    def syncColumns(self, dbName, tableName, values):
        ok = True
        
        if self.dataBaseExists(dbName) == False:
            self.logger.info("database %s doesn't exist. Creating it..."%dbName)            
            ok = self.createDatabase(dbName)            

        if ok and self.tableExists(dbName, tableName) == False:
            self.logger.info("table %s.%s doesn't exist. Creating it..."%(dbName, tableName))            
            ok = self.createTable(dbName, tableName)
        
        anyError = False
        rv, existingColumns = self.getColumnNames(dbName, tableName)
        if rv:
            existingColumns = [x.upper() for x in existingColumns]
            for val in values:
                columnName = val.name
                dataTypeString = self.getValueDataType(val)
                if val.name.upper() not in existingColumns:
                    
                    
                    ok = self.createColumn(dbName, tableName, columnName, dataTypeString, errorIfExists=True)
                    if not ok:
                        anyError = True
                        self.logger.warning("adding column %s to database %s.%s failed"%(columnName, dbName, tableName))
                    else:
                        self.logger.info("added column %s to database %s.%s"%(columnName, dbName, tableName))
                else:
                    rv, dtype = self.getColumnDataType(dbName, tableName, columnName)
                    if rv:
                        if dataTypeString.upper() != dtype:
                            rv = self.changeColumnDataType(dbName, tableName, columnName, dataTypeString)
                            if rv:
                                self.logger.info("changed column %s to datatype %s"%(columnName, dataTypeString))
                            else:
                                self.logger.warning("changing datatype of column %s to datatype %s failed"%(columnName, dataTypeString))
        else:
            anyError = True
            
        if anyError:
            ok = False
        else:
            ok = True
        return ok

    def getDBName(self, product, station):
        return PROD_RUN_PRE + product
    
    def getTableName(self, product, station):
        return PROD_RUN_STAT_PRE + station

    def createProduct(self, product, station):
        err = False
        dbName = self.getDBName(product, station)
        tableName = self.getTableName(product, station)
        
        ok = self.createDatabase(dbName, errorIfExists=False)
        if ok == False:
            err = True
        ok = self.createTable(dbName, tableName, errorIfExists=False)
        
        if err:
            ok = False
            
        return ok
            
        
    def deleteProduct(self, product, station):
        dbName = self.getDBName(product, station)
        return self.deleteDatabase(dbName)
                
    def applyConfig(self, config, workDir):
        rv = ConnectorErrors.NO_ERROR
        self.workDir = workDir
        if self.config != []:
            ok = self.config.fromDict(config)
            if ok:
                rv = self._onNewConfig()
            else:
                rv = ConnectorErrors.INVALID_CONFIG
        return rv
            
    def testConfig(self, config):
        ok = True
        description = "Success"
        
        try:
            c = Config.Config(self.configDescription)
        except Exception as e:
            description = "loading connector config failed with error message %s"%str(e)
            self.logger.error(description)
            self.logger.info("full traceback:\n%s"%traceback.format_exc())
            ok = False
            
        if ok:
            if c.fromJson(config) == False:
                ok = False
                description = c.errmsg()
        
        return ok, description
    
    def getConfig(self):
        return self.config