import logging
import os
from functools import partial
from git import Repo
import traceback
import shutil

from openProduction.station import Station
from openProduction.connectors import ConnectionManager
from openProduction.common import Types, misc

def _checkGitRemote(wdir, stationName, url):
    ok = True
    initNewRepo = False
    logger = logging.getLogger(misc.getAppName())
    if os.path.exists(wdir):
        delFolder = False
        repo = Repo.init(wdir)
        try:
            remote = repo.remote()
            if remote.url != url:
                logger.error("directory %s is a git repo, but remote URL is set to %s"%(wdir, url))
                ok = False
        except:
            logger.info("directory %s exists, but appears to be no valid git repository, \
erasing folder, as user previously agreed to lose changes"%wdir)
            logger.info("full traceback:\n%s"%traceback.format_exc())
            delFolder = True
            
        if delFolder:
            try:
                shutil.rmtree(wdir)
            except:
                logger.error("error deleting folder %s"%wdir)
                logger.info("full traceback:\n%s"%traceback.format_exc())
                ok = False
                
            if ok:
                initNewRepo = True
    else:
        initNewRepo = True
        
    if initNewRepo:
        try:
            repo = Repo.clone_from(url, wdir)
        except:
            logger.error("error cloning git repository from %s"%url)
            logger.info("full traceback:\n%s"%traceback.format_exc())
            ok = False
            
    return ok

class StationInstaller:
    def __init__(self):
        self.logger = logging.getLogger(misc.getAppName())
    
    def _printBanner(self):
        
        licStr = "This project is licensed under %s, see the accompanied VERSION file for more details"%misc.getLicense(misc.License.Type)
        
        print("="*len(licStr))
        print("Welcome to openProduction %s"%misc.getVersion())
        print("")
        print(" * Documentation: %s"%misc.getLink(misc.Links.Documentation))
        print(" * Sources:       %s"%misc.getLink(misc.Links.SourceCode))
        print("")
        print(licStr)
        print("="*len(licStr))
    
    def run(self):
        ok = False
        self._printBanner()
        print("")
        question = "Do you want to install a new station on this PC (answer 'no' if you just updated %s)"%misc.getAppName()
        yes = misc.queryYesNo(question, default="no")
        if not yes:
            return

        appFolder = misc.getDefaultAppFolder()
        question = "Do you want to use the default workspace %s for this station"%(appFolder)
        ret = misc.queryYesNo(question)
        if ret == False:
            appFolder = misc.queryFolder("Please specify the installation folder: ")
            print ("... installing into %s"%appFolder)
            
        def stationExists(value):
            value = str(value)
            if Station.Station.stationExists(appFolder, value):
                question = "Station already exists, do you want to override the station (WARNING: all settings of this station will be lost)"
                yes = misc.queryYesNo(question, default="no")
                return yes
            else:
                try:
                    os.makedirs(os.path.join(appFolder, value))
                    os.makedirs(os.path.join(appFolder, value, "repo"))
                    rv = True
                except Exception as e:
                    print ("could not create folder %s, error message: %s"%(value, str(e)))
                    rv = False
            return rv
            
        stationName = misc.queryString("Please give the station name: ", cb=stationExists)
        ok, scmConfig = self.promptSCM(appFolder, stationName)
        if ok:
            ok, connectorName, connectorConfig = self.promptConnection()
        if ok:
            print("-------------------------------------------------------------")
            print("installing station now...")
            config = {}
            config["SCM"] = scmConfig
            config["connectors"] = {}
            config["connectors"]["connectorName"] = connectorName
            config["connectors"]["connectorConfig"] = connectorConfig
            station = Station.Station.createStation(appFolder, stationName, config)
            if station != None:
                station.saveStation()
            else:
                print ("something went wrong, see log for more details")
        
    def promptSCM(self, appFolder, stationName):
        ok = True
        auth = {}
        print("")
        print("-------------------------------")
        print("Configuration of git connection")
        print("")
        print("Set username and email address")
        username = misc.queryString("Please specify your git username: ")
        email = misc.queryString("Please specify your git email: ")
        print("")
        print("Selection Authentication method")
        print("-------------------------------------------------------------")
        print("*         SSH key")
        print("          username/password (not implemented yet)")
        print("-------------------------------------------------------------")
        print("")
        question = ("Press enter to keep the current choice[*] "
                    "or type selection number: ")
        rv = misc.queryChoice(question, choice=[0], default=0, typ=int)
        if rv == 0:
            auth["AuthType"] = "ssh"
            auth["Type"] = "git"
            auth["username"] = username
            auth["email"] = email
            repoFolder = os.path.join(appFolder, stationName, "repo")
            url = misc.queryString("Please specify the remote URL to use: ",
                                   cb=partial(_checkGitRemote, repoFolder, stationName))
            auth["remote"] = url
        return ok, auth
        
    def promptConnection(self):
        m = ConnectionManager.ConnectionManager()
        print("")
        print("-------------------------------------------------------------")
        print("The following connectors are available to create this station")
        print("")
        print("Selection Description")
        print("-------------------------------------------------------------")
        idxs = []
        for idx, name in enumerate(m.getConnectors()):
            
            if idx == 0:
                printStr = "*% 8d %s"%(idx, name)
            else:
                printStr = "% 9d %s"%(idx, name)
                
            print(printStr)
            idxs.append(idx)
     
        print("")
        question = "Press enter to keep the current choice[*] or type selection number: "
        rv = misc.queryChoice(question, choice=idxs, default=idxs[0], typ=int)
        connectorName = m.getConnectors()[rv]
        ok = True
        connectorConfig = {}
        cfg = m.getConnectorConfigDesc(connectorName)
        connectorConfig = self.prompConnectorCfg(cfg)
        return ok, connectorName, connectorConfig
        
    def prompConnectorCfg(self, config):
        connectorCfg = {}
        if len(config) > 0:
            print("-------------------------------------------------------------")
            print("This connector requires additional configuration")
            print("-------------------------------------------------------------")
        for cfg in config:
            question = "%s (%s): "%(cfg.name, cfg.description)
            if isinstance(cfg, Types.Path):
                val = misc.queryFolder(question)
            elif isinstance(cfg, Types.String):
                val = misc.queryString(question)
            elif isinstance(cfg, Types.Password):
                val = misc.queryPassword(question)
            elif isinstance(cfg, Types.Int):
                val = misc.queryInteger(question, minVal=cfg.minVal, maxVal=cfg.maxVal)
            else:
                raise RuntimeError("unsupported type " + str(cfg))
            connectorCfg[cfg.name] = val
        return connectorCfg