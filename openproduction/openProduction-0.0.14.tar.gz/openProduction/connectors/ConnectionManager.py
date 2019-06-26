from yapsy.PluginManager import PluginManager
import os
from openProduction.common import misc
import logging
from openProduction.connectors import BaseConnector

class ConnectionManager:
    def __init__(self):
        self.logger = logging.getLogger(misc.getAppName())
        self._manager = PluginManager()
        self._manager.setPluginPlaces([os.path.abspath(os.path.dirname(__file__))])
        self._manager.setCategoriesFilter({
                "Connectors" : BaseConnector.BaseConnector})
        
        self._manager.collectPlugins()
    
        # Loop round the plugins and print their names.
        self._connectors = []
        
        self.logger.info("loading connector plugins now")
#        for plugin in self._manager.getAllPlugins():
        for plugin in self._manager.getPluginsOfCategory("Connectors"):
            self.logger.info("found connector '%s'"%plugin.name)
            self._connectors.append(plugin.name)
            
        self._connectors = sorted(self._connectors)
        self.logger.info("... found %d connector(s)"%len(self._connectors))
    
    def getConnectors(self):
        return self._connectors
    
    def getConnectorConfigDesc(self, name):
        cfg = []
        connector = self._manager.activatePluginByName(name, category="Connectors")
        if connector != None:
            cfg = connector.getConfig()
        return cfg
    
    def loadConnector(self, name, config, workdir):
        rv = BaseConnector.ConnectorErrors.NO_ERROR
        connector = self._manager.activatePluginByName(name, category="Connectors")
        if connector != None:
            rv = connector.applyConfig(config, workdir)
        return rv, connector