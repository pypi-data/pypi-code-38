from enum import Enum, unique

# ********************************************************************************
# commandline option possible datatypes
@unique
class OptionType(Enum):
    """
    Type of the value of a configuration option
    """
    Int = 'int',
    Float = 'float',
    String = 'string',
    Boolean = 'boolean'

# ********************************************************************************
# a commandline option
class ConfigOpt:
    """
    A commandline configuration option.
    """
    def __init__(self, longopt, shortopt=None, desc=None, hasarg=False, value=None, otype=OptionType.String, cfgFieldName=None):
        self.longopt = longopt
        self.shortopt = shortopt
        self.hasarg = hasarg
        self.description = desc
        self.value = value
        self.otype=otype
        self.cfgFieldName = cfgFieldName

    def helpString(self):
        helpMessage=''
        if self.shortopt != None:
            helpMessage='-' + self.shortopt + ' ,'
        helpMessage+= '--' + self.longopt
        if self.hasarg == True:
            helpMessage+= " <arg>"
        if self.description != None:
            helpMessage = '{:30}'.format(helpMessage)
            helpMessage+= " - " + self.description
        return helpMessage

    def castValue(self):
        if self.hasarg == True and self.value is not None:
            if self.otype == OptionType.Int:
                self.value =  int(self.value)
            elif self.otype == OptionType.Float:
                self.value =  float(self.value)
            elif self.otype == OptionType.Boolean:
                self.value = { 'True' : True,
                               'True' : True,
                               't' : True,
                               '1' : True,
                               'False' : False,
                               'false' : False,
                               'f' : False,
                               '0' : False}[self.value]
                self.value = bool(self.value)
            return self

# ********************************************************************************
# add support for accessing a class like a dictionary.
class DictLike:
    """
    Class used like an interface that makes a configuration class (data object) behave like a dictionary.
    """
    # overwrite __getitem__ to allow dictory style access to options
    def __getitem__(self, key):
        if key not in self.__dict__:
            raise AttributeError("No such attribute: " + key)
        return self.__dict__[key]

    # overwrite __setitem__ to allow dictory style setting of options
    def __setitem__(self,key,value):
        if key not in self.__dict__:
            raise AttributeError("No such attribute: " + key)
        self.__dict__[key] = value

    # get access to list of field names
    def getValidKeys(self):
        return self.__dict__

    # check whether configuration is valid
    def validateConfiguration(self):
        return True
