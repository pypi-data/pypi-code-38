# -*- coding: utf-8 -*-
"""
Created on Sun Jun 23 16:33:09 2019

@author: Markus
"""
import pandas as pd
from openProduction.connectors.BaseConnector import ConnectorErrors
from openProduction.server import ServerInterface

class Report:
    def __init__(self, serverIF):
        self.serverIF = serverIF
        
    @staticmethod
    def create(workDir):
        return Report(ServerInterface.ServerInterface.create(workDir))
    
    def getNumDevices(self, productName, stationName):
        pass
    
    def getResultKeys(self, productName, productVersion, stationName, onlyLatestRev=False, specificRev=None):
        rv = ConnectorErrors.NO_ERROR
        columns = ["JSON_KEYS(`result`) AS 'keys'"]
        data = None
        
        if specificRev != None:
            filt = ["ProductResults.`revision_id`=%d"%specificRev]
        elif onlyLatestRev:
            rv, rev = self.serverIF.getLatestProductRevisionByName(stationName, productName, productVersion)
            if rv == ConnectorErrors.NO_ERROR:
                revId= rev["revision_id"]
                filt = ["ProductResults.`revision_id`=%d"%revId]
        else:
            filt = []
            if stationName != None:
                filt += ["station.`name` like '%s'"%stationName]
            if productName != None:
                filt += ["prod.`name` like '%s'"%productName]
            if productVersion != None:
                filt += ["steps.`version` like '%s'"%productVersion]
            
        if rv == ConnectorErrors.NO_ERROR:
            filt += ["`success`=1"]
            filt = " and ".join(filt)
            
            joins = [
                     "`%s`.`Stations` station ON station.station_id = ProductResults.station_id"%self.serverIF.dbName,
                     "`%s`.`ProductRevisions` rev ON rev.revision_id = ProductResults.revision_id"%self.serverIF.dbName,
                     "`%s`.`ProductSteps` steps ON steps.product_step_id = rev.product_step_id"%self.serverIF.dbName,
                     "`%s`.`Products` prod ON steps.product_id = prod.product_id"%self.serverIF.dbName,
                     ]            
            rv, data = self.serverIF.listProductResults(filt=filt, columns=columns, joins=joins)
            
            if rv == ConnectorErrors.NO_ERROR:
                if onlyLatestRev or specificRev != None:
                    data = data[0]
            
        return rv, data
    
    def getDeviceResults(self, productName, productVersion, stationName, deviceID=None, resultKeys=None, onlyGood=True):
        columns = ["`deviceID`", "`duration`", "ProductResults.`date` as date", "ProductResults.`revision_id` as revision_id"]
        
        filt = []
        if stationName != None:
            filt += ["station.`name` like '%s'"%stationName]
        if productName != None:
            filt += ["prod.`name` like '%s'"%productName]
        if productVersion != None:
            filt += ["steps.`version` like '%s'"%productVersion]
        if deviceID != None:
            filt += ["`deviceID` like '%s'"%deviceID]
        
        if onlyGood:
            filt += ["`success`=1"]
        
        columns += ["success"]
            
        filt = " and ".join(filt)
        
        joins = [
                 "`%s`.`Stations` station ON station.station_id = ProductResults.station_id"%self.serverIF.dbName,
                 "`%s`.`ProductRevisions` rev ON rev.revision_id = ProductResults.revision_id"%self.serverIF.dbName,
                 "`%s`.`ProductSteps` steps ON steps.product_step_id = rev.product_step_id"%self.serverIF.dbName,
                 "`%s`.`Products` prod ON steps.product_id = prod.product_id"%self.serverIF.dbName,
                 ]
        
        
        if resultKeys != None:
            for k in resultKeys:
                if k.find("UNQUOTE_") == 0:
                    k = k[len("UNQUOTE_"):]
                    columns.append("JSON_UNQUOTE(JSON_EXTRACT(`result`, '$.%s')) as %s"%(k,k))
                else:
                    columns.append("JSON_EXTRACT(`result`, '$.%s') as %s"%(k,k))
        
        rv, data = self.serverIF.listProductResults(filt=filt, columns=columns, joins=joins)
        if rv == ConnectorErrors.NO_ERROR:
            p = pd.DataFrame(data)
            if resultKeys != None:
                for k in resultKeys:
                    if k.find("UNQUOTE_") == 0:
                        continue
                    try:
                        p[k] = pd.to_numeric(p[k])
                    except:
                        pass
        else:
            p = None
        return p
    
if __name__ == "__main__":
    from openProduction.common import misc
    from pylab import *
    
    rep = Report.create(misc.getDefaultAppFolder())
    rv = rep.getResultKeys("Bauernstolz", "AA", "Klebestation", onlyLatestRev=True)