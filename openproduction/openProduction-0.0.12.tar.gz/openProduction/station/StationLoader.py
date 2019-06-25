import os
import json
from openProduction.connectors import ConnectionManager
from openProduction.station import Station
from openProduction.product import ProductExecutor
from openProduction.connectors import BaseConnector
from openProduction.server import ServerInterface
from openProduction.common import misc
import logging

class StationLoader(ProductExecutor.ProductExecutor):
    """Station Loader class"""
    
    def __init__(self, ctor):
        super(StationLoader, self).__init__(ctor)
        self.logger = logging.getLogger(misc.getAppName())
        self.workspace = self.params["workspace"]
        self.name = self.params["stationName"]
        self.cfgFile = os.path.join(self.workspace, "config.json")
            
    def step__00100(self, params, values):
        """load config file"""
        self.config = None
        
        self.ioHandler.message("trying to open file %s"%os.path.abspath(self.cfgFile))

        f = open(self.cfgFile)
        
        self.logger.info("trying to parse content of config file to json")
        self.config = json.load(f)
        self.logger.info("checking config file for required keywords")
        rv = self._checkCfg(self.config)
        self.assertEqual(rv, True, "station configuration file is invalid")

    def step__00200(self, params, values):
        """load connector"""
        connectorName = self.config["connectors"][0]["connectorName"]
        connectorCfg = self.config["connectors"][0]["connectorConfig"]
        
        self.logger.info("trying to load connector '%s'"%connectorName)

        c = ConnectionManager.ConnectionManager()
        rv, self.connector = c.loadConnector(connectorName, connectorCfg, self.workspace)
        
        if rv == BaseConnector.ConnectorErrors.INVALID_CONFIG:
            self.assertNotEqual(rv, BaseConnector.ConnectorErrors.INVALID_CONFIG, "connector config invalid: %s"%self.connector.config.errmsg())
        
        self.assertNotEqual(rv, BaseConnector.ConnectorErrors.NOT_FOUND.value, "database server not found, check IP address or hostname of server")
        self.assertNotEqual(rv, BaseConnector.ConnectorErrors.FORBIDDEN, "Connection with sql server failed, check username/password")
        
        self.assertEqual(rv, BaseConnector.ConnectorErrors.NO_ERROR, "loading connector '%s' failed with msgcode %d (%s)"%(connectorName, rv.value, rv.name))
        self.assertNotEqual(self.connector, None)
        
    def step__00300(self, params, values):
        """check if station exists"""
        s = ServerInterface.ServerInterface.create(self.workspace)
        rv, data = s.listStations()
        self.assertEqual(rv, BaseConnector.ConnectorErrors.NO_ERROR, "query station names failed with %s"%rv.name)
        names = [x["name"] for x in data]
        nameFound = self.name in names
        self.assertEqual(nameFound, True, "station %s not found in database, available stations are %s"%(self.name, names))
        for d in data:
            if d["name"] == self.name:
                self.stationID = d["station_id"]
        
    def step__00400(self, params, values):
        """construct station"""
        self.logger.info("trying to construct station '%s'"%self.name)        
        self.station = Station.Station(self.workspace, self.name, self.config, self.connector, self.stationID, ioHandler=self.ioHandler)
        self.assertNotEqual(self.station, None, "constructing station %s failed"%self.name)
        
        
    def _checkCfg(self, config):
        ok = True
        #TODO: use json schme validation
#        for keyword in self.REQUIRED:
#            if keyword not in config:
#                self.logger.error("keyword '%s' required but not found in station config %s"%(keyword, self.cfgFile))
#                ok = False
        return ok
                