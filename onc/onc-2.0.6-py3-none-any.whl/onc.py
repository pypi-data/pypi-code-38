import json
from modules._OncDiscovery import _OncDiscovery
from modules._OncDelivery  import _OncDelivery
from modules._OncRealTime  import _OncRealTime
from modules._OncArchive   import _OncArchive

class ONC:
    """
    Python ONC Api Client Library
    Common library wrapper
    """

    def __init__(self, token, production: bool=True, showInfo: bool=False, outPath: str='output', timeout: int=60):
        # Build the configuration dict
        self.config = {
            "token"    : token,
            "showInfo" : showInfo,
            "timeout"  : timeout,
            "baseUrl"  : 'https://data.oceannetworks.ca/',
            "outPath"  : ''
        }

        # sanitize outPath
        outPath = outPath.replace('\\', '/')
        if outPath[-1] == '/':
            outPath = outPath[:-1]
        self.config['outPath'] = outPath
        
        # switch to qa if needed
        if not production:
            self.config['baseUrl'] = 'https://qa.oceannetworks.ca/'

        # Create service objects
        self.discovery = _OncDiscovery(self.config)
        self.delivery  = _OncDelivery(self.config)
        self.realTime  = _OncRealTime(self.config)
        self.archive   = _OncArchive(self.config)
        
        self.pollPeriod = 2.0 # Default seconds to wait between consecutive download tries of a file (when no estimate processing time is available)


    def print(self, obj, filename: str=""):
        """
        Helper for printing a JSON dictionary to the console or to a file
        @filename: if present, creates the file and prints to it
        """
        text = json.dumps(obj, indent=4)
        if filename == '':
            print(text)
        else:
            with open(filename, 'w+') as file:
                file.write(text)

    
    # PUBLIC METHOD WRAPPERS

    # Discovery methods

    def getLocations(self, filters: dict):
        return self.discovery.getLocations(filters)
    
    def getLocationHierarchy(self, filters: dict):
        return self.discovery.getLocationHierarchy(filters)
    
    def getDeployments(self, filters: dict):
        return self.discovery.getDeployments(filters)
    
    def getDevices(self, filters: dict):
        return self.discovery.getDevices(filters)
    
    def getDeviceCategories(self, filters: dict):
        return self.discovery.getDeviceCategories(filters)
    
    def getProperties(self, filters: dict):
        return self.discovery.getProperties(filters)
    
    def getDataProducts(self, filters: dict):
        return self.discovery.getDataProducts(filters)
    
    # Delivery methods

    def orderDataProduct(self, filters: dict, maxRetries: int=0, downloadResultsOnly: bool=False, includeMetadataFile: bool=True, overwrite: bool=False):
        return self.delivery.orderDataProduct(filters, maxRetries, downloadResultsOnly, includeMetadataFile, overwrite)
    
    def requestDataProduct(self, filters: dict):
        return self.delivery.requestDataProduct(filters)
    
    def runDataProduct(self, dpRequestId: int, waitComplete: bool=True):
        return self.delivery.runDataProduct(dpRequestId, waitComplete)
    
    def downloadDataProduct(self, runId: int, maxRetries: int=0, downloadResultsOnly: bool=False, includeMetadataFile: bool=True, overwrite: bool=False):
        return self.delivery.downloadDataProduct(runId, maxRetries, downloadResultsOnly, includeMetadataFile, overwrite)
    
    # Real-time methods

    def getDirectScalar(self, filters: dict=None, allPages: bool=False):
        return self.realTime.getDirectScalar(filters, allPages)
    
    def getDirectRawByLocation(self, filters: dict=None, allPages: bool=False):
        return self.realTime.getDirectRawByLocation(filters, allPages)
    
    def getDirectRawByDevice(self, filters: dict=None, allPages: bool=False):
        return self.realTime.getDirectRawByDevice(filters, allPages)
    
    # Archive file methods

    def getListByLocation(self, locationCode: str, filters: dict=None):
        return self.archive.getListByLocation(locationCode, filters)
    
    def getListByDevice(self, deviceCode: str, filters: dict=None):
        return self.archive.getListByDevice(deviceCode, filters)
    
    def getFile(self, filename: str='', overwrite: bool=True):
        return self.archive.getFile(filename, overwrite)
    
    def getDirectFiles(self, filters: dict=None, overwrite: bool=True):
        return self.archive.getDirectFiles(filters, overwrite)