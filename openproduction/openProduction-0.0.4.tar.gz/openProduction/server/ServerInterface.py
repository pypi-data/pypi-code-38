from openProduction.common import misc
from openProduction.connectors.BaseConnector import ConnectorErrors
import logging
from openProduction.connectors import ConnectionManager, BaseConnector
import traceback
import os
import json

class ServerInterface:
    DB_REFIX = "db_op_"
    STATION_TABLE = "Stations"
    PRODUCT_TABLE = "Products"
    PRODUCT_REVISIONS_TABLE = "ProductRevisions"
    PRODUCT_STEPS_TABLE = "ProductSteps"
    PRODUCT_STATION_LINK_TABLE = "ProductStationLink"
    PRODUCT_RESULTS_TABLE = "ProductResults"
    GIT_CREDENTIALS_TABLE = "GitCredentials"
    
    def __init__(self, workDir, connector, workspace):
        self.logger = logging.getLogger(misc.getAppName())
        self.workDir = workDir
        self.connector = connector
        self.workspace = workspace
        self.dbName = self._workspace2dbName(workspace)
        
    @staticmethod        
    def create(workDir):
        logger = logging.getLogger(misc.getAppName())
        cfgFile = os.path.abspath(os.path.join(workDir, "config.json"))
        
        logger.info("trying to open file %s"%os.path.abspath(cfgFile))
        try:
            f = open(cfgFile)
        except Exception as e:
            logger.error("opening config file %s failed with error message %s"%(cfgFile, str(e)))
            logger.info("full traceback:\n%s"%traceback.format_exc())
            return None
            
        logger.info("trying to parse content of config file to json")
        try:
            config = json.load(f)
        except Exception as e:
            logger.error("parsing config file %s failed with error message %s"%(cfgFile, str(e)))
            logger.info("full traceback:\n%s"%traceback.format_exc())
            return None
            
        connectorName = config["connectors"][0]["connectorName"]
        connectorCfg = config["connectors"][0]["connectorConfig"]        
        logger.info("trying to load connector '%s'"%connectorName)
        c = ConnectionManager.ConnectionManager()
        rv, connector = c.loadConnector(connectorName, connectorCfg, workDir)        
        if rv.value != BaseConnector.ConnectorErrors.NO_ERROR.value:
            logger.error("loading connector station failed with error %s"%str(rv))
            return None

        workspace = config["workspace"]        
        return ServerInterface(workDir, connector, workspace)
    
    def _workspace2dbName(self, workspace):
        return ServerInterface.DB_REFIX+workspace   
    
    ##########################################################################
    #                       git credentials manipulation                     #
    ##########################################################################
    def createGitCredentials(self, data):
        rv, _id = self.connector.addRow(self.dbName, self.GIT_CREDENTIALS_TABLE, data)
        if rv == ConnectorErrors.NO_ERROR:
            data["credential_id"] = _id
        return rv, data
            
    def deleteGitCredentials(self, credential_id):
        filt = "`credential_id` = %d"%credential_id
        return self.connector.deleteRows(self.dbName, self.GIT_CREDENTIALS_TABLE, filt)
    
    def listGitCredentials(self, filt=None):
        return self.connector.getData(self.dbName, self.GIT_CREDENTIALS_TABLE, ["*"], filt=filt)
    
    def updateGitCredentials(self, credential_id, data):
        filt = "`credential_id` = %d"%credential_id
        return self.connector.updateRow(self.dbName, self.GIT_CREDENTIALS_TABLE, data, filt)
    
    def getGitCredentials(self, credential_id):
        filt = "`credential_id` = %d"%credential_id
        rv, data = self.connector.getData(self.dbName, self.GIT_CREDENTIALS_TABLE, ["*"], filt=filt)
        if data == None:
            rv = ConnectorErrors.NOT_FOUND
        else:
            data = data[0]
        return rv, data    
    
    def _gitCredentialsTable(self):
        columns = [{
                "name": "git_credential_id",
                "type": "int",
                "primaryKey": True,
                "notNull": True,
                "autoIncrement": True,
            },
            {
                "name": "git_url",
                "type": "CHAR(255)",
                "unique": True,
                "notNull": True
            },
            {
                "name": "git_username",
                "type": "CHAR(255)",
                "notNull": True
            },
            {
                "name": "git_password",
                "type": "CHAR(255)",
                "notNull": True
            },
            {
                "name": "git_usermail",
                "type": "CHAR(255)",
                "notNull": True
            }
        ]
        table = {
            "name": self.GIT_CREDENTIALS_TABLE,
            "columns": columns
        }
        return table    
    
    
    ##########################################################################
    #                    product station link manipulation                   #
    ##########################################################################
    def createProductStationLink(self, data):
        rv, _id = self.connector.addRow(self.dbName, self.PRODUCT_STATION_LINK_TABLE, data)
        if rv == ConnectorErrors.NO_ERROR:
            data["link_id"] = _id
        return rv, data
            
    def deleteProductStationLink(self, link_id):
        filt = "`link_id` = %d"%link_id
        return self.connector.deleteRows(self.dbName, self.PRODUCT_STATION_LINK_TABLE, filt)
    
    def listProductStationLinks(self, filt=None):
        return self.connector.getData(self.dbName, self.PRODUCT_STATION_LINK_TABLE, ["*"], filt=filt)
    
    def updateProductStationLink(self, link_id, data):
        filt = "`link_id` = %d"%link_id
        return self.connector.updateRow(self.dbName, self.PRODUCT_STATION_LINK_TABLE, data, filt)
    
    def getProductStationLink(self, link_id):
        filt = "`link_id` = %d"%link_id
        rv, data = self.connector.getData(self.dbName, self.PRODUCT_STATION_LINK_TABLE, ["*"], filt=filt)
        if data == None:
            rv = ConnectorErrors.NOT_FOUND
        else:
            data = data[0]
        return rv, data    
    
    def _productStationLinkTable(self):
        columns = [{
                "name": "link_id",
                "type": "int",
                "primaryKey": True,
                "notNull": True,
                "autoIncrement": True,
            },
            {
                "name": "product_id",
                "type": "int",
                "notNull": True,
                "foreign": [self.PRODUCT_TABLE, "product_id"]
            },
            {
                "name": "station_id",
                "type": "int",
                "notNull": True,
                "foreign": [self.STATION_TABLE, "station_id"]
            },
            {
                "name": "order",
                "type": "int",
                "notNull": True
            }
        ]
        table = {
            "name": self.PRODUCT_STATION_LINK_TABLE,
            "columns": columns,
            "uniqueKey": ["product_id", "order"]
        }
        return table    

    ##########################################################################
    #                      Product result manipulation                       #
    ##########################################################################
    def createProductResult(self, data):
        rv, _id = self.connector.addRow(self.dbName, self.PRODUCT_RESULTS_TABLE, data)
        if rv == ConnectorErrors.NO_ERROR:
            data["product_result_id"] = _id
        return rv, data
            
    def deleteProductResult(self, product_result_id):
        filt = "`product_result_id` = %d"%product_result_id
        return self.connector.deleteRows(self.dbName, self.PRODUCT_RESULTS_TABLE, filt)
    
    def listProductResults(self):
        return self.connector.getData(self.dbName, self.PRODUCT_RESULTS_TABLE, ["*"], filt=None)    
    
    def getProductResult(self, product_result_id):
        filt = "`product_result_id` = %d"%product_result_id
        rv, data = self.connector.getData(self.dbName, self.PRODUCT_RESULTS_TABLE, ["*"], filt=filt)
        if data == None:
            rv = ConnectorErrors.NOT_FOUND
        else:
            data = data[0]
        return rv, data
    
    def _productResultsTable(self):
        columns = [{
                "name": "product_result_id",
                "type": "int",
                "primaryKey": True,
                "notNull": True,
                "autoIncrement": True,
            },
            {
                "name": "revision_id",
                "type": "int",
                "notNull": True,
                "foreign": [self.PRODUCT_REVISIONS_TABLE, "revision_id"]
            },
            {
                "name": "station_id",
                "type": "int",
                "notNull": True,
                "foreign": [self.STATION_TABLE, "station_id"]
            },
            {
                "name": "result",
                "type": "JSON",
                "notNull": True
            },
            {
                "name": "duration",
                "type": "FLOAT ",
                "notNull": True
            },
            {
                "name": "testCaseResults",
                "type": "JSON",
                "notNull": True
            },                    
            {
                "name": "openProductionVersion",
                "type": "CHAR(11)",
                "notNull": True
            },
            {
                "name": "success",
                "type": "bool",
                "notNull": True
            },
            {
                "name": "date",
                "type": "DATETIME",
                "constraint": "DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
            },
            {
                "name": "deviceID",
                "type": "CHAR(40)",
                "notNull": True
            },
        ]
        table = {
            "name": self.PRODUCT_RESULTS_TABLE,
            "columns": columns
        }
        return table
    
    ##########################################################################
    #                       Product steps manipulation                       #
    ##########################################################################
    def createProductStep(self, data, revisionData):
        stepData = None
        rv = self.connector.startTransaction(self.dbName)
        if rv == ConnectorErrors.NO_ERROR:
            # add to product table
            rv, _id = self.connector.addRow(self.dbName, self.PRODUCT_STEPS_TABLE, data)
            
            if rv == ConnectorErrors.NO_ERROR:
                stepData = data
                stepData["product_step_id"] = _id
                revisionData["product_step_id"] = _id
                rv, _id = self.createProductRevision(revisionData)
                if rv == ConnectorErrors.NO_ERROR:
                    revisionData["revision_id"] = _id
                            
            if rv != ConnectorErrors.NO_ERROR:
                self.connector.rollbackTransaction()
                stepData = None
                revisionData = None
            else:
                rv = self.connector.commitTransaction()
        else:
            revisionData = None
        
        return rv, stepData, revisionData
        
        
        rv, _id = self.connector.addRow(self.dbName, self.PRODUCT_STEPS_TABLE, data)        
        if rv == ConnectorErrors.NO_ERROR:
            data["product_step_id"] = _id
        return rv, data
            
    def deleteProductStep(self, product_step_id):
        filt = "`product_step_id` = %d"%product_step_id
        return self.connector.deleteRows(self.dbName, self.PRODUCT_STEPS_TABLE, filt)
    
    def listProductSteps(self, filt=None):
        return self.connector.getData(self.dbName, self.PRODUCT_STEPS_TABLE, ["*"], filt=filt)
    
    def updateProductStep(self,  product_step_id):
        filt = "`product_step_id` = %d"%product_step_id
        return self.connector.updateRow(self.dbName, self.PRODUCT_STEPS_TABLE, data, filt)
    
    def getProductStep(self, product_step_id):
        filt = "`product_step_id` = %d"%product_step_id
        rv, data = self.connector.getData(self.dbName, self.PRODUCT_STEPS_TABLE, ["*"], filt=filt)
        if data == None:
            rv = ConnectorErrors.NOT_FOUND
        else:
            data = data[0]
        return rv, data

    def getProductStepByName(self, stationName, productName, versionName):
        filt = "prod.`name` like '%s' and station.`name` like '%s' and version like '%s'"%(productName, stationName, versionName)
        
        joins = ["`%s`.`Products` prod ON prod.product_id = ProductSteps.product_id"%self.dbName,
                 "`%s`.`Stations` station ON station.station_id = ProductSteps.station_id"%self.dbName,
                 "`%s`.`GitCredentials` cred ON cred.git_credential_id = ProductSteps.git_credential_id"%self.dbName
                 ]
        
        rv, data = self.connector.getData(self.dbName, self.PRODUCT_STEPS_TABLE, ["*"], filt=filt, joins=joins)
        if data == None:
            rv = ConnectorErrors.NOT_FOUND
        else:
            data = data[0]
        return rv, data
    
    def _productStepsTable(self):
        columns = [{
                "name": "product_step_id",
                "type": "int",
                "primaryKey": True,
                "notNull": True,
                "autoIncrement": True,
            },
            {
                "name": "product_id",
                "type": "int",
                "notNull": True,
                "foreign": [self.PRODUCT_TABLE, "product_id"]
            },
            {
                "name": "version",
                "type": "CHAR(255)",
                "notNull": True
            },
            {
                "name": "git_credential_id",
                "type": "int",
                "notNull": True,
                "foreign": [self.GIT_CREDENTIALS_TABLE, "git_credential_id"]
            },
            {
                "name": "git_branch",
                "type": "CHAR(255)",
                "notNull": True
            },
            {
                "name": "description",
                "type": "CHAR(255)",
                "notNull": True
            },
            {
                "name": "image",
                "type": "MEDIUMBLOB",
                "notNull": True
            },
            {
                "name": "state",
                "type": "int",
                "default": 0,
                "notNull": True
            },
            {
                "name": "station_id",
                "type": "int",
                "notNull": True,
                "foreign": [self.STATION_TABLE, "station_id"]
            }
        ]
        table = {
            "name": self.PRODUCT_STEPS_TABLE,
            "columns": columns,
            "uniqueKey": ["product_id", "version", "station_id"]
        }
        return table
    
    ##########################################################################
    #                      product revision manipulation                     #
    ##########################################################################
    def createProductRevision(self, data):
        if "product_step_id" not in data:
            return ConnectorErrors.INVALID_PARAM, None
        else:
            rv, rvData = self.getLatestProductRevision(data["product_step_id"])
            if rv != ConnectorErrors.NOT_FOUND:
                return ConnectorErrors.EXISTS, None
        
        rv, _id = self.connector.addRow(self.dbName, self.PRODUCT_REVISIONS_TABLE, data)
        if rv == ConnectorErrors.NO_ERROR:
            data["revision_id"] = _id
        return rv, data
            
    def deleteProductRevision(self, revision_id):
        filt = "`revision_id` = %d"%revision_id
        return self.connector.deleteRows(self.dbName, self.PRODUCT_REVISIONS_TABLE, filt)
    
    def listProductRevisions(self, filt=None, joins=None):
        return self.connector.getData(self.dbName, self.PRODUCT_REVISIONS_TABLE, ["*"], filt=filt, joins=joins, orderBy="revision_id DESC")
    
    def getLatestProductRevision(self, product_step_id):
        filt = "`product_step_id` = %d and revision_id=(select max(revision_id) from `%s`.`%s` WHERE `product_step_id` = %d)"%(product_step_id, self.dbName, self.PRODUCT_REVISIONS_TABLE, product_step_id)
        rv, rvData = self.connector.getData(self.dbName, self.PRODUCT_REVISIONS_TABLE, ["*"], filt=filt)
        if rvData == None:
            rv = ConnectorErrors.NOT_FOUND
        else:
            rvData = rvData[0]
            rvData["params"] = json.loads(rvData["params"])
        return rv, rvData
    
    def updateProductRevision(self, product_step_id, data):
        entry = None
        if "product_step_id" in data:
            data.pop("product_step_id", None)    
        
        rv, rvData = self.getLatestProductRevision(product_step_id)
        if rv == ConnectorErrors.NO_ERROR:
            entry = rvData
            entry.pop("revision_id", None)
            entry.pop("date", None)
            for key, val in data.items():
                entry[key] = val
            rv, _id = self.connector.addRow(self.dbName, self.PRODUCT_REVISIONS_TABLE, entry)
            entry["revision_id"] = _id
        
        return rv, entry
    
    def updateProductRevisionByName(self, stationName, productName, versionName, data):
        rv, rvData = self.getProductStepByName(stationName, productName, versionName)
        if rv == ConnectorErrors.NO_ERROR:
            stepId = rvData["product_step_id"]
            rv, rvData = self.updateProductRevision(stepId, data)
        else:
            rvData = None
        return rv, rvData
        
        
    def getProductRevision(self, revision_id):
        filt = "`revision_id` = %d"%revision_id
        rv, data = self.connector.getData(self.dbName, self.PRODUCT_REVISIONS_TABLE, ["*"], filt=filt)
        if data == None:
            rv = ConnectorErrors.NOT_FOUND
        else:
            data = data[0]
            data["params"] = json.loads(data["params"])
        return rv, data
    
    def _productRevisionTable(self):
        columns = [{
                "name": "revision_id",
                "type": "int",
                "primaryKey": True,
                "notNull": True,
                "autoIncrement": True,
            },
            {
                "name": "product_step_id",
                "type": "int",
                "notNull": True,
                "foreign": [self.PRODUCT_STEPS_TABLE, "product_step_id"]
                
            },
            {
                "name": "params",
                "type": "JSON",
                "notNull": True
            },            
            {
                "name": "commit_id",
                "type": "CHAR(40)",
                "notNull": True
            },
            {
                "name": "date",
                "type": "DATETIME",
                "constraint": "DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
            }
        ]
        table = {
            "name": self.PRODUCT_REVISIONS_TABLE,
            "columns": columns
        }
        return table    

    ##########################################################################
    #                             product manipulation                       #
    ##########################################################################
    def createProduct(self, data, stationLinks):
        """stationLinks: list of dicts
        """
        productData = None
        linkData = None
        rv = self.connector.startTransaction(self.dbName)
        if rv == ConnectorErrors.NO_ERROR:
            # add to product table
            rv, _id = self.connector.addRow(self.dbName, self.PRODUCT_TABLE, data)
            
            if rv == ConnectorErrors.NO_ERROR:
                productData = data
                productData["product_id"] = _id
                linkData = []
                
                # add to station link table
                if type(stationLinks) == type({}):
                    stationLinks = [stationLinks]
                
                for link in stationLinks:
                    link["product_id"] = _id
                    rv, stationLink = self.createProductStationLink(link)
                    if rv == ConnectorErrors.NO_ERROR:
                        linkData.append(stationLink)
                    else:
                        break
            
            if rv != ConnectorErrors.NO_ERROR:
                self.connector.rollbackTransaction()
                productData = None
                linkData = None
            else:
                rv = self.connector.commitTransaction()
        
        return rv, productData, linkData
            
    def deleteProduct(self, product_id):
        filt = "`product_id` = %d"%product_id
        return self.connector.deleteRows(self.dbName, self.PRODUCT_TABLE, filt)
    
    def listProducts(self, filt=None):
        return self.connector.getData(self.dbName, self.PRODUCT_TABLE, ["*"], filt=filt)
    
    def updateProduct(self, product_id, data):
        filt = "`product_id` = %d"%product_id
        return self.connector.updateRow(self.dbName, self.PRODUCT_TABLE, data, filt)
    
    def getProduct(self, product_id):
        filt = "`product_id` = %d"%product_id
        rv, data = self.connector.getData(self.dbName, self.PRODUCT_TABLE, ["*"], filt=filt)
        if data == None:
            rv = ConnectorErrors.NOT_FOUND
        else:
            data = data[0]
        return rv, data    
    
    def _productTable(self):
        columns = [{
                "name": "product_id",
                "type": "int",
                "primaryKey": True,
                "notNull": True,
                "autoIncrement": True,
            },
            {
                "name": "name",
                "type": "CHAR(255)",
                "notNull": True,
                "unique": True,
            },
            {
                "name": "description",
                "type": "CHAR(255)",
                "notNull": True
            },
            {
                "name": "state",
                "type": "int",
                "default": 0,
                "notNull": True
            }
        ]
        table = {
            "name": self.PRODUCT_TABLE,
            "columns": columns
        }
        return table

    ##########################################################################
    #                             station manipulation                       #
    ##########################################################################
    def createStation(self, data):
        rv, station_id = self.connector.addRow(self.dbName, self.STATION_TABLE, data)
        if rv == ConnectorErrors.NO_ERROR:
            data["station_id"] = station_id
        return rv, data
            
    def deleteStation(self, station_id):
        filt = "`station_id` = %d"%station_id
        return self.connector.deleteRows(self.dbName, self.STATION_TABLE, filt)
    
    def listStations(self, filt=None):
        return self.connector.getData(self.dbName, self.STATION_TABLE, ["*"], filt=filt)
    
    def updateStation(self, station_id, data):
        filt = "`station_id` = %d"%station_id
        return self.connector.updateRow(self.dbName, self.STATION_TABLE, data, filt)
    
    def getStation(self, station_id):
        filt = "`station_id` = %d"%station_id
        rv, data = self.connector.getData(self.dbName, self.STATION_TABLE, ["*"], filt=filt)
        if data == None:
            rv = ConnectorErrors.NOT_FOUND
        else:
            data = data[0]
        return rv, data
    
    def listStationProducts(self, station_id):
        filt = "`station_id` = %d"%station_id
        joins = ["`%s`.`Products` prod ON prod.product_id = ProductStationLink.product_id"%self.dbName]
        return self.connector.getData(self.dbName, self.PRODUCT_STATION_LINK_TABLE, ["prod.*"], filt=filt, joins=joins)

    def listStationProductSteps(self, station_id, product_id):
        filt = "steps.`station_id` = %d and steps.`product_id` = %d"%(station_id, product_id)
        joins = ["`%s`.`ProductSteps` steps ON (steps.`product_id` = ProductStationLink.`product_id` and \
steps.`station_id` = ProductStationLink.`station_id`)"%self.dbName]
        return self.connector.getData(self.dbName, self.PRODUCT_STATION_LINK_TABLE, ["steps.*"], filt=filt, joins=joins)
    
    def _stationTable(self):
        columns = [{
                "name": "station_id",
                "type": "int",
                "primaryKey": True,
                "notNull": True,
                "autoIncrement": True,
            },
            {
                "name": "name",
                "type": "CHAR(255)",
                "notNull": True,
                "unique": True,
            },
            {
                "name": "description",
                "type": "CHAR(255)",
                "notNull": True
            }
        ]
        table = {
            "name": self.STATION_TABLE,
            "columns": columns
        }
        return table
        
    ##########################################################################
    #                            workspace manipulation                      #
    ##########################################################################
    
    def createWorkspace(self, workspace):
        if workspace in self.listWorkspaces():
            return ConnectorErrors.EXISTS
        
        dbName = self._workspace2dbName(workspace)
        
        rv = self.connector.createDatabase(dbName)
        if rv == ConnectorErrors.NO_ERROR:
            tables = []
            tables.append(self._stationTable())
            tables.append(self._gitCredentialsTable())
            tables.append(self._productTable())
            tables.append(self._productStepsTable())
            tables.append(self._productRevisionTable())
            tables.append(self._productResultsTable())
            tables.append(self._productStationLinkTable())
            rv = self.connector.createTables(self.dbName, tables)
        else:
            return rv
        
        return rv
    
    def deleteWorkspace(self, workspace):
        dbName = self._workspace2dbName(workspace)
        return self.connector.deleteDatabase(dbName)
    
    def listWorkspaces(self):
        rv = []
        dbs = self.connector.listDatabases()
        for db in dbs:
            if db["Database"].find(ServerInterface.DB_REFIX) == 0:
                rv.append(db["Database"][len(ServerInterface.DB_REFIX):])
        return rv
