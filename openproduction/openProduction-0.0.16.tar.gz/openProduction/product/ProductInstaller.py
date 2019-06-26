from openProduction.common import misc
from openProduction.product import Product
import logging
import traceback

class ProductInstaller:
    
    def __init__(self):
        self.logger = logging.getLogger(misc.getAppName())
    
    def run(self, station, productName=None, productVersion=None):
        print ("Welcome to the product CLI installer")
        if productName == None:
            productName = misc.queryString("Please give a productName: ")
            productVersion = misc.queryString("Please give a productVersion: ")
        elif productVersion == None:
            productVersion = misc.queryString("Please give a productVersion: ")
            
        executor = misc.queryFile("Please specify the location of the station executor script: ")
        params = misc.queryFile("Please specify the location of the parameter file: ")
        
        revision = station.scm.getNextRevision(productName, productVersion)
        
        self.logger.info("Installing product %s with version %s. \
Revision for this product is %d"%(productName, productVersion, revision))
        
        product = Product(productName, productVersion, revision, executor, params)
        
        try:
            product.save(station)
            self.logger.info("...ok")
            ok = True
        except:
            self.logger.error("error adding product %s.%s.%d"%(productName,
                                                          productVersion,
                                                          revision))
            self.logger.info("full traceback:\n%s"%traceback.format_exc())
            ok = False
            
        return ok