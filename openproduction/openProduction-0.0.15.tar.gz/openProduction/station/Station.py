import json
import os
import logging
from openProduction.common import misc, Version
from openProduction.product import Product
import traceback
from openProduction.station import StationLoader
from openProduction.suite import TestSuite, TestLoader, TestParams
from openProduction.product import ProductExecutorCtor
from openProduction.server import ServerInterface
from openProduction.connectors import BaseConnector

class Station:
    
    instance = None
    
    def __init__(self, workspace, stationName, config, resultConnector, stationID, ioHandler=None):
        if not Station.instance:
            Station.instance = Station.__Station(workspace, stationName, config, resultConnector, stationID, ioHandler=ioHandler)
            
    def __getattr__(self, name):
        return getattr(self.instance, name)
    def __setattr__(self, name, value):
        return setattr(self.instance, name, value)
    
    class __Station:
        def __init__(self, workspace, stationName, config, resultConnector, stationID, ioHandler=None):            
            self.logger = logging.getLogger(misc.getAppName())
            self.workspace = workspace
            self.stationName = stationName
            self.config = config
            self.resultConnector = resultConnector
            self.loadedProduct = None
            self.stationID = stationID
            self.serverIF = ServerInterface.ServerInterface.create(workspace)
            self.productData = None
            self.ioHandler = ioHandler
            rv, data = self.serverIF.listStationProducts(self.stationID)
            if rv == BaseConnector.ConnectorErrors.NO_ERROR:
                self.productData = data
            
        def getStationName(self):
            return self.stationName
        
        def getProductData(self):
            if self.productData == None:
                rv, data = self.serverIF.listStationProducts(self.stationID)
                if rv == BaseConnector.ConnectorErrors.NO_ERROR:
                    self.productData = data
            else:
                rv = BaseConnector.ConnectorErrors.NO_ERROR
                
            return rv, self.productData
    
        def listProducts(self):
            return self.getProductData()
        
        def getProductID(self, productName):
            productID = None
            rv, productData = self.getProductData()
            if productData != None:
                for p in productData:
                    if p["name"] == productName:
                        productID = p["product_id"]
            return productID

        def loadProduct(self, name, version, revision=None, ui=None, discardChanges=False):
            self.loadedProduct = Product.Product.load(self, name, version, revision, ioHandler=self.ioHandler, ui=ui)
            return self.loadedProduct

        def listProductVersions(self, productName):
            productID = self.getProductID(productName)
            if productID != None:
                return self.serverIF.listStationProductSteps(self.stationID, productID)
            else:
                return BaseConnector.ConnectorErrors.NOT_FOUND, None
            
        def listProductRevisions(self, productName, versionName):
            productID = self.getProductID(productName)
            if productID != None:
                filt = "`product_id`=%d and `version` like '%s' and `station_id`=%d"%(productID, versionName, self.stationID)
                rv, data = self.serverIF.listProductSteps(filt)
                if rv == BaseConnector.ConnectorErrors.NO_ERROR:
                    productStepID = data[0]["product_step_id"]
                    filt = "`product_step_id`=%d"%productStepID
                return self.serverIF.listProductRevisions(filt)
            else:
                return BaseConnector.ConnectorErrors.NOT_FOUND, None            

        def saveStation(self):
            ok = False
            fname = os.path.join(self.workspace, self.stationName, "config.json")
            try:
                f = open(fname, "w")
                f.write(json.dumps(self.config))
                f.close()
                ok = True
            except Exception as e:
                self.logger.error("saving station failed with error message %s"%str(e))
                self.logger.info("full traceback:\n%s"%traceback.format_exc())
            return ok
    
    @staticmethod
    def getInstance():
        return Station.instance
            
    @staticmethod
    def localStationExists(workspace, name):
        p = os.path.join(workspace, name)
        if os.path.exists(p):
            return True
        else:
            return False
    
    @staticmethod
    def listStations(workspace):
        names = []
        s = ServerInterface.ServerInterface.create(workspace)
        rv, data = s.listStations()
        if rv == BaseConnector.ConnectorErrors.NO_ERROR:
            names = [x["name"] for x in data]
        return names
    
    @staticmethod
    def createStation(workspace, stationName, config):
        workdir = os.path.abspath(os.path.join(workspace, stationName))
        ok, resultConnector = StationLoader.StationLoader.loadConnector(config["connectors"], workdir)
        if ok:
            s = ServerInterface.ServerInterface.create(workspace)
            rv, data = s.listStations("name like '%s'"%stationName)
            if rv == BaseConnector.ConnectorErrors.NO_ERROR:
                stationID = data[0]["station_id"]
                return Station(workspace, stationName, config, resultConnector, stationID)
        return None

    @staticmethod
    def loadStationAsync(workspace, stationName, ioHandler=None, ui=None):
        
        params = TestParams.TestParams({"workspace": workspace, 
                                        "stationName": stationName},
                                        None)

        suite = TestSuite.TestSuite("station loader",  "", params=params, values=None)
        suiteRunner = TestSuite.TestSuiteRunner(suite, stopOnFail=True, stopOnExcept=True)
        
        loader = TestLoader.TestModuleLoader(StationLoader)
        ctor = ProductExecutorCtor.ProductExecutorCtor(ioHandler, params, suite.values, suite.tempParams, ui)
        tgs = loader.discover(ctor)
        for tg in tgs:
            suite.addTestCaseGroup(tg)
        
        return suiteRunner

    @staticmethod
    def loadStation(workspace, stationName, ioHandler=None, ui=None):
        runner = Station.loadStationAsync(workspace, stationName, ioHandler, ui)
        fut = runner.loadSuite()
        fut.result(timeout = 60)
        fut = runner.run()
        fut.result(timeout = 60)
        return Station.getInstance()