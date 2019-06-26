from openProduction.suite import TestSuite
from openProduction.product import ProductExecutor
from openProduction.station import Station
from openProduction.common import misc
from openProduction.connectors.BaseConnector import ConnectorErrors
import logging 

class ResultConnector(ProductExecutor.ProductExecutor):
    """Result connector setup hooks"""
    
    def __init__(self, ctor):
        super(ResultConnector, self).__init__(ctor)
        self.logger = logging.getLogger(misc.getAppName())
        self.station = Station.Station.getInstance()
        
        if self.station != None:
            self.stationName = self.station.stationName
            
    def installRunner(self, runner):
        self.testSuiteRunner = runner
        
    def install(self, testSuite):
        hint = TestSuite.InstallHints(mustBeLast=True)
        testSuite.addMethodHint(self.teardown_result_00100, hint)
        self.testSuite = testSuite

    def teardown_result_00100(self, params, values):
        """Durchlaufergebnisse ablegen"""
        if self.station != None and self.station.loadedProduct != None:
            if "NO_TRANSMIT_RESULTS" in params:
                self.logger.info("Skippe Erbenisübertragung, 'NO_TRANSMIT_RESULTS' in params gesetzt, Parameter sind:")
                self.logger.info(str(values))
                return TestSuite.ExecutionResult.SKIP
            else:
                if "NO_LOG_RESULTS" not in params:
                    f = open("log.txt", "w")
                    f.write(self.testSuiteRunner.suiteResults.getLogText())
                    f.close()
                    values.addFile("log.txt")
                
                values.move("result")
                values["revision_id"] = self.station.loadedProduct.version.revision
                values["station_id"] = self.station.stationID
                values["duration"] = self.testSuiteRunner.suiteResults.executionTime
                values["testCaseResults"] = self.testSuiteRunner.suiteResults.toDict()
                values["openProductionVersion"] = misc.getVersion()
                values["success"] = self.testSuiteRunner.suiteResults.isSuccessful()
                values["deviceID"] = values.getDeviceID()
                values["tempParams"] = self.tempParams.getParams()
                self.logger.info("Übertrage Ergebnisse")
                rv, data = self.station.serverIF.createProductResult(values.getParams())
                self.assertEqual(rv, ConnectorErrors.NO_ERROR, "Fehler beim Speichern der Durchlaufergebnisse")
                result_id = data["product_result_id"]
                
                for f in values.getFiles():
                    if "sftp_config_id" in params:
                        sftp_config_id = params["sftp_config_id"]
                    else:
                        sftp_config_id = 1
                    data = {"result_id":result_id, "filename": f, "sftp_config_id": sftp_config_id}
                    rv = self.station.serverIF.createProductResultFile(data)
                    self.logger.info("Übertrage Datei %s"%f)
                    self.assertEqual(rv, ConnectorErrors.NO_ERROR, "Fehler beim Speichern der Datei %s"%f)
        else:
            if self.station == None:
                self.logger.info("Skippe Erbenisübertragung, station=None")
            else:
                self.logger.info("Skippe Erbenisübertragung, station.loadedProduct=None")
            return TestSuite.ExecutionResult.SKIP
        