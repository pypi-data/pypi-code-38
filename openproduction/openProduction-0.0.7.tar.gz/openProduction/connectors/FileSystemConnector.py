import openProduction.connectors.BaseConnector as plugintypes
import os
import shutil
import pandas

class FileSystemConnector(plugintypes.BaseConnector):    
    def __init__(self):
        __fields__ = []
        super(FileSystemConnector, self).__init__(__fields__)
    
    def createDatabase(self, dbname):
        path = os.path.join(self.workDir, dbname)
        if not os.path.exists(path):
            os.makedirs(path)
            pandas.DataFrame().to_hdf(os.path.join(path+"tables.hdf5"), "_init_")
    
    def deleteDatabase(self, dbname):
        path = os.path.join(self.workDir, dbname)
        shutil.rmtree(path)
        return True
        
    def createTable(self, dbName, tableName, errorIfExists=True):
        file = os.path.join(self.workDir, dbName, "tables.hdf5")
        if os.path.exists(file):
            store = pandas.HDFStore(file,'r')
            if ("/"+tableName in store.keys()) and errorIfExists==True:
                store.close()
                raise RuntimeError("Table %s already exists"%tableName)
            elif ("/"+tableName not in store.keys()):
                store.close()
                pandas.DataFrame().to_hdf(file, tableName)
        elif os.path.exists(file) == False:
            self.createDatabase(dbName)
            pandas.DataFrame().to_hdf(file, tableName)
        return True
        
    def listDatabases(self):
        dbs = []
        for f in os.listdir(self.workDir):
            absF = os.path.join(self.workDir, f)
            if os.path.isdir(absF):
                dbs.append(os.path.split(absF)[-1])
        return dbs

    def addRow(self, dbName, table, entries):
        fname = os.path.join(self.workDir, dbName, table + ".hdf5")
        rows = pandas.read_hdf(fname)
        
        return ok
        raise NotImplementedError("addRow method has to be defined in connector's plugin")
    
    def getColumns(self, dbName, table, columnName):
        raise NotImplementedError("getColumns method has to be defined in connector's plugin")    
    
    def getDescription(self):
        return "This connector uses your local file system"
    
    def _onNewConfig(self):
        ok = True
        
        if not os.path.exists(self.workDir):
            os.makedirs(self.workDir)
        return ok