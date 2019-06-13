from enum import Enum, unique
from capexplain.cl.cfgoption import DictLike
import logging

# logger for this module
log = logging.getLogger(__name__)

################################################################################
# Cmd types
@unique
class CmdTypes(Enum):
    Mine = 1,
    Explain = 2,
    Stats = 3,
    Help = 4,
    GUI = 5

# ********************************************************************************
# Information about a command for capexplain
class Command:

    def __init__(self, cmd, cmdstr, helpMessage, execute, options=None):
        self.cmd = cmd
        self.cmdstr = cmdstr
        self.options=options
        self.helpMessage=helpMessage
        self.execute = execute

    def helpString(self):
        return '{:30}- {}'.format(self.cmdstr,self.helpMessage)

    def __str__(self):
        return self.__dict__.__str__()

# ********************************************************************************
# multiple indexes for the options for a command
class CmdOptions:

    def constructOptions(self):
        self.shortopts = ''
        self.longopts = []
        self.shopt_map = {}
        self.longopt_map = {}
        self.cmdConfig = {}
        for opt in self.optionlist:
            self.cmdConfig[opt.longopt] = opt # mapping from configuration option names to configuration objects
            if opt.shortopt != None:
                self.shortopt_map['-' + opt.shortopt] = opt # map short option to configuration object
                self.shortopts+=opt.shortopt
                if opt.hasarg:
                    self.shortopts+=':'
            self.longopt_map['--' + opt.longopt] = opt
            if opt.hasarg:
                self.longopts.append(opt.longopt + '=')
            else:
                self.longopts.append(opt.longopt)

    def __init__(self, optionlist):
        self.optionlist = optionlist
        self.shortopt=''
        self.longopts=''
        self.longopt_map = {}
        self.shortopt_map = {}
        self.constructOptions()

    def setupConfig(self, config : DictLike):
        o = self
        for opt in o.cmdConfig:
            option = o.cmdConfig[opt]
            if option.value != None:
                key =  opt if (option.cfgFieldName is None) else option.cfgFieldName
                val = option.value
                log.debug("option: {}:{}".format(key,val))
                if key in config.getValidKeys():
                    config[key] = val
                else:
                    log.warning("unhandled config option <{}>".format(option.longopt))

    def setupConfigAndConnection(self, conn, config: DictLike):
        o = self
        for opt in o.cmdConfig:
            option = o.cmdConfig[opt]
            if option.value != None:
                key =  opt if (option.cfgFieldName is None) else option.cfgFieldName
                val = option.value
                log.debug("option: {}:{}".format(key,val))
                if key in conn.getValidKeys():
                    conn[key] = val
                elif key in config.getValidKeys():
                    config[key] = val
                else:
                    log.warning("unhandled config option <{}>".format(option.longopt))
        
