import cmd2
from openProduction.station import StationManager, Station, StationInstaller
from openProduction.product import ProductInstaller
from openProduction.common import misc
import argparse

class StationCli(cmd2.Cmd):
    intro = '===============================================================================\n\
Welcome to the openProduction station shell.   Type help or ? to list commands.\n'
    
    def __init__(self, workspace, stationName="", productName="", productVersion="", productRevision=None):
        cmd2.Cmd.__init__(self, use_ipython=True)
        self._load(workspace)
        self._loadStation(stationName)
        self._loadProduct(productName, productVersion, productRevision)
        
    def _load(self, workspace):
        self.workspace = workspace
        self.stationManager = StationManager.StationManager(self.workspace)
        self.station = None
        self.productionRun = None
        self.prompt = "> "
    
    def _loadStation(self, stationName):
        if stationName != "":
            self.station = Station.Station.loadStation(self.workspace, stationName)
            if self.station != None:
                self.prompt = "(%s) "%stationName

    def _loadProduct(self, productName, version, revision):
        if productName != "" and version != "" and self.station != None:
            self.product = self.station.loadProduct(productName, version, revision)
            if self.product != None:
                self.prompt = "(%s - %s[%s.%d]) "%(self.station.getStationName(), self.product.getProductName(), self.product.getProductVersion(), self.product.getProductRevision())

    productCreate_parser = argparse.ArgumentParser()
    productCreate_parser.add_argument('productName', type=str, help='product name')
    productCreate_parser.add_argument('productVersion', type=str, help='product version')
    @cmd2.with_argparser(productCreate_parser)
    def do_createProduct(self, arg):
        """create a new production run"""
        if self.station != None:
            installer = ProductInstaller.ProductInstaller()
            installer.run(self.station, productName=arg.productName,
                          productVersion=arg.productVersion)
        else:
            print("no station loaded")
        
    def do_getWorkspace(self, arg):
        """Get current workspace"""
        print(self.workspace)
    
    workspaceSetter_parser = argparse.ArgumentParser()
    workspaceSetter_parser.add_argument('workspace', type=str, help='workspace')
    @cmd2.with_argparser(workspaceSetter_parser)
    def do_setWorkspace(self, arg):
        """Set current workspace"""
        self._load(arg.workspace)
    
    def do_installNewStation(self, arg):
        """Install a new station"""
        installer = StationInstaller.StationInstaller()
        installer.run()
        
    def do_listStations(self, arg):
        """List all available stations"""
        stations = "\t".join(self.stationManager.listStations())
        print("Available stations on this machine: ", stations)

    loadStation_parser = argparse.ArgumentParser()
    loadStation_parser.add_argument('stationName', type=str, help='station to load')
    @cmd2.with_argparser(loadStation_parser)
    def do_loadStation(self, arg):
        """Load given station"""
        self._loadStation(arg.stationName)
            
    def do_exit(self, arg):
        'Stop recording, close the turtle window, and exit:  BYE'
        print('Thank you for using openProduction')
        return True

if __name__ == '__main__':
    pass
    #StationCli("prog").cmdloop()