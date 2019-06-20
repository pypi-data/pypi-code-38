import logging
from openProduction.common import misc
from openProduction.station import StationLoader
import glob
import os

class StationManager:

    def __init__(self, workspace):
        self.logger = logging.getLogger(misc.getAppName())
        self.workspace = workspace

    def listStations(self):
        self.logger.info("looking for stations in path %s"%self.workspace)
        globExpr = os.path.join(self.workspace, "*", "config.json")
        stations = []
        for filename in glob.iglob(globExpr):
            stationName = os.path.split(os.path.relpath(filename, self.workspace))[0]
            
            self.logger.info("found candidate '%s'"%stationName)
            s = StationLoader.StationLoader(self.workspace, stationName)
            if s.load():
                stations.append(stationName)
            
        return stations