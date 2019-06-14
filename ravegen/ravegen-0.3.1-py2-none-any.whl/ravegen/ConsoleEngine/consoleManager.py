import readline
import Utils.sad as sad
import Utils.errorHandler as errorHandler
import Utils.logManager as logManager
import Utils.utils as utils

consoleErrorHandler = errorHandler.ErrorHandler("Console Manager")

def verifyArgs(argv):
    if(len(argv) < 2):
        consoleErrorHandler.addError("Args needed", sad._CRITICAL_ERROR_)
        printHelp()
    commands, commandsInfo = getConsoleCommands()
    ansFatherCommand = None
    for i in range(1, len(argv)):
        command = argv[i]
        if ansFatherCommand is None:
            if not _is_Father(command):
                consoleErrorHandler.addError("Command " + command + " doesn't exists", sad._CRITICAL_ERROR_)
            else:
                if command in commands:
                    ansFatherCommand = command
                else:
                    consoleErrorHandler.addError("Command " + command + " doesn't exists", sad._CRITICAL_ERROR_)
        else:
            if _is_Father(command):
                consoleErrorHandler.addError("Command " + ansFatherCommand + " and command " + command + " can't be together", sad._CRITICAL_ERROR_)
            else:
                options = _splitOptions(command)
                for option in options:
                    if not option in commandsInfo[ansFatherCommand][sad._CONSOLE_ENGINE_OPTION_TAG_]:
                        consoleErrorHandler.addError("Command " + ansFatherCommand + " doesn't have option " + option, sad._CRITICAL_ERROR_)

    consoleErrorHandler.handle()

def printHelp():
    _, commandsInfo = getConsoleCommands()
    logManager.printConsole("Rave Gen - By ChrisChV")
    logManager.printConsole("Program for generate basic telegram bots with python-telegram-bot")
    logManager.printConsole("COMMANDS\n")
    for command, info in commandsInfo.iteritems():
        logManager.printConsole("\t" + command + ": " + info[sad._CONSOLE_ENGINE_INFO_OPTION_])
        if info[sad._CONSOLE_ENGINE_OPTION_TAG_]:
            logManager.printConsole("\tOPTIONS")
            for option, optionInfo in info[sad._CONSOLE_ENGINE_OPTION_TAG_].iteritems():
                logManager.printConsole("\t\t-" + option + ": " + optionInfo)

def getConsoleCommands(installFlag = True):
    if installFlag:
        commandsFile = open(utils.getInstalationPath() + sad._DF_ + sad._RAVEGEN_SRC_PATH_  + sad._DF_ + sad._CONSOLE_ENGINE_COMMANDS_FILE_NAME, 'r')
    else:
        commandsFile = open(sad._CONSOLE_ENGINE_COMMANDS_FILE_DEV_PATH, 'r')
    commandsInfo = {}
    commands = []
    for line in commandsFile:
        tokens = line.split(" ")
        infoString = ""
        for i in range(2, len(tokens)):
            infoString += tokens[i] + " "
        infoString = infoString[:-1]
        infoString = infoString.rstrip('\n')
        if tokens[1] == 'None':
            tempDic = {sad._CONSOLE_ENGINE_OPTION_TAG_: {}, sad._CONSOLE_ENGINE_INFO_OPTION_: infoString}
            commandsInfo[tokens[0]] = tempDic
            commands.append(tokens[0])
        else:
            commandsInfo[tokens[1]][sad._CONSOLE_ENGINE_OPTION_TAG_][tokens[0]] = infoString
    commandsFile.close()
    return commands, commandsInfo

def getOptions(argv):
    options = []
    for i in range(2,len(argv)):
        option = argv[i]
        options += _splitOptions(option)
    return options

def _setAutocompleter():
    readline.parse_and_bind("tab: complete")
    readline.set_completer(_completer)

def _completer(text, state):
    commands, _ = getConsoleCommands()
    options = [i for i in commands if i.startswith(text)]
    if state < len(options):
        return options[state]
    return None

def _is_Father(command):
    if(command[0] == '-'):
        return False
    return True

def _splitOptions(command):
    options = []
    for i in range(1,len(command)):
        options.append(command[i])
    return options
