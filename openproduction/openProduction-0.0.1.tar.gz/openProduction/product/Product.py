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
            
        self.folder = folder
            
        self.discover(folder, revisionData["params"])
            
        self.name = productData["name"]
        version = productData["version"]
        revision = revisionData["revision_id"]
        url = productData["git_url"]
        self.version = Version.Version(version, revision, url)
        
        if ioHandler == None:
            ioHandler = TestSuiteIO.BaseIOHandler()

        self._iohandler = ioHandler
        self._ui = ui
        
        self._createProductRunner(folder)
        
    def discover(self, folder, params):
        self.params = TestParams.TestParams(params, folder)
  
    @staticmethod
    def load(station, name, version, revision, ioHandler=None, ui=None):
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
                scm = SCM.SCM(scmDir, stepData)
                
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
        
if __name__ == "__main__":
    from openProduction.station import Station
    from openProduction import log
    import time
    
    logger = log.initLogger()
    logger.setLevel(logging.DEBUG)
    
    workspace = misc.getDefaultAppFolder()
    stationName = "klebestation"
    station = Station.Station.loadStation(workspace, stationName)
    name = "Bauernstolz"
        
    if station != None:
        if 0:
            version = "AA"
            patch = -1
            url = ""
            version = Version.Version(version, patch, url)

            prodDir = r"D:\work\openProduction\openProduction\examples\Klebestation"
            prod = Product(name, version, prodDir)
            rv = prod.save(station)
        elif 1:
            version = "AA"
            revision = -1
            url = ""
            version = Version.Version(version, revision, url, isDirty=True)
            prodDir = r"D:\work\openProduction\openProduction\examples\Klebestation"
            io = TestRunnerCli.IOHandlerCli()
            p = Product(name, version, prodDir, ioHandler=io)
            cli = TestRunnerCli.TestSuiteCliRunner(testSuiteRunner=p.productRunner.suiteRunner)
                
            print("starting product")
            future = p.productRunner.load(startTrigger=True)
            
            
            while True:
                time.sleep(10)
            p.productRunner.unload()
#            print("stopping product now!")
        else:
            vers = Version.Version("AA", 2, "")
            p = Product.load(station.scm, "Bauernstolz", vers, discardChanges=True)
            cli = TestRunnerCli.TestSuiteCliRunner(testSuiteRunner=p.productRunner.suiteRunner)
                
            print("starting product")
            future = p.productRunner.load(startTrigger=True)
    else:
        print ("error loading station")
        
    