import io
import ConfigParser
import utils as utils
import sad as sad


def printVerbose(_string):
    if _verbose():
        print(_string)

def printLog(_string):
    if _log():
        logFile = open(sad._LOG_FILE_PATH_, 'a+')
        logFile.write(utils.getTime() + ": " + _string + "\n")
        logFile.close()

def printConsole(_string):
    print(_string)

def print_all(_string):
    printVerbose(_string)
    printLog(_string)

def _verbose():
    if not utils.file_Or_Directory_Exists(sad._ACTUAL_PATH, sad._CONFIG_DIR_NAME_):
        return True

    elif not utils.file_Or_Directory_Exists(sad._CONFIG_DIR_NAME_, sad._CONFIG_FILE_NAME_):
        return True

    configFile = open(sad._CONFIG_FILE_PATH, 'r')
    configStream = configFile.read()
    config = ConfigParser.RawConfigParser(allow_no_value=False)
    config.readfp(io.BytesIO(configStream))
    configFile.close()
    if not config.has_section(sad._CONFIG_RAVEGEN_SECTION_):
        return True
    if not config.has_option(sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_VERBOSE_OPTION_):
        return True

    return config.getboolean(sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_VERBOSE_OPTION_)

def _log():
    if not utils.file_Or_Directory_Exists(sad._ACTUAL_PATH, sad._CONFIG_DIR_NAME_):
        return False

    elif not utils.file_Or_Directory_Exists(sad._CONFIG_DIR_NAME_, sad._CONFIG_FILE_NAME_):
        return False

    configFile = open(sad._CONFIG_FILE_PATH, 'r')
    configStream = configFile.read()
    config = ConfigParser.RawConfigParser(allow_no_value=False)
    config.readfp(io.BytesIO(configStream))
    configFile.close()
    if not config.has_section(sad._CONFIG_RAVEGEN_SECTION_):
        return True
    if not config.has_option(sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_LOG_OPTION_):
        return True
    return config.getboolean(sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_LOG_OPTION_)
    