import os
import traceback
from openProduction.common import Version, Constants, misc, SCM
from openProduction.product import ProductExecutor
from openProduction.suite import TestRunnerCli, TestParams, TestSuiteIO
import logging
import distutils.dir_util
from openProduction.connectors.BaseConnector import ConnectorErrors

class Product:
    def __init__(self, productData, revisionData, folder, ioHandler=None, ui=None):
        self.logger = logging.getLogger(misc.getAppName())
        
        version = productData["version"]
        revision = revisionData["revision_id"]
        url = productData["git_url"]
        
        self.version = Version.Version(version, revision, url)
        self.productID = productData['product_id']
        self.productStepID = productData['product_step_id']
            
        self.folder = folder
            
        self.discover(folder, revisionData["params"])
            
        self.name = productData["name"]
        
        if ioHandler == None:
            ioHandler = TestSuiteIO.BaseIOHandler()

        self._iohandler = ioHandler
        self._ui = ui
        
        self._createProductRunner(folder)
        
    def discover(self, folder, params):
        self.params = TestParams.TestParams(params, folder)
  
    @staticmethod
    def load(station, name, version, revision, ioHandler=None, ui=None):
        ok = True
        p = None
        logger = logging.getLogger(misc.getAppName())
        
        logger.info("getProductStepByName")
        rv, stepData = station.serverIF.getProductStepByName(station.stationName, name, version)
        if rv == ConnectorErrors.NO_ERROR:
            if revision == None:
                logger.info("getLatestProductRevision")
                rv, revData = station.serverIF.getLatestProductRevision(stepData["product_step_id"])
            else:
                logger.info("getProductRevision")
                rv, revData = station.serverIF.getProductRevision(revision)

            if rv == ConnectorErrors.NO_ERROR:    
                scmDir = os.path.join(station.workspace, "repo")
                stepData["commit_id"] = revData["commit_id"]
                
                try:
                    scm = SCM.SCM(scmDir, stepData)
                except:
                    logger.error("error creating SCM object")
                    logger.info("full traceback:\n%s"%traceback.format_exc())
                    ok = False
                
                if ok == True:
                    try:
                        scm.checkoutProductRevision()
                        ok = True
                    except:
                        logger.error("error checkout product revision")
                        logger.info("full traceback:\n%s"%traceback.format_exc())
                        ok = False
                    
                if ok == True:
                    try:
                        p = Product(stepData, revData, scmDir, ioHandler=ioHandler, ui=ui)
                    except:
                        logger.error("error loading product %s with version %s"%(name, version))
                        logger.info("full traceback:\n%s"%traceback.format_exc())
            else:
                logger.error("get latest revision for product_step_id %d failed with %s"(stepData["product_step_id"], rv.name))
        else:
            logger.error("query for product %s, version %s @ station %s failed with %s"(name, version, station.stationName, rv.name))
        return p       
    
    def _createProductRunner(self, folder):                
        self.productRunner = ProductExecutor.ProductRunner(folder, self.name, self.params,
                                                           ioHandler=self._iohandler, ui=self._ui)
