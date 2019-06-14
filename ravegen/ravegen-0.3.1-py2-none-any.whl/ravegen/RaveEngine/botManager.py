from telegram.ext import Updater
import logging
import Utils.sad as sad
import Utils.commandManager as commandManager
import Utils.utils as utils
import Utils.logManager as logManager
import RaveEngine.herokuBotManager as herokuBotManager
import RaveEngine.gaeBotManager as gaeBotManager
import CloudEngine.cloudManager as cloudManager
import configManager as configManager

def generateBot(testFlag = True):
    config = configManager.getConfig()
    hosting = configManager.get(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_HOSTING_OPTION_)
    commandManager.runMkdirCommand(sad._OUTPUT_BOT_DIR_)
    commandManager.runLsCommand(sad._MODULES_DIR_, writeFile=sad._TEMP_LS_MODULES_FILE_NAME)
    modules = []
    tempLsFile = open(sad._TEMP_LS_MODULES_FILE_NAME, 'r')

    for line in tempLsFile:
        modules.append(line.rstrip('\n'))

    tempLsFile.close()
    modules = [module.split('.')[0] for module in modules if len(module.split('.')) == 2 and module.split('.')[1] == sad._MODULES_EXTENTION_]

    initFile = open(sad._MODULES_DIR_ + sad._DF_ + sad._INIT_PY, 'w')
    for module in modules:
        if module != sad.__INIT__:
            initFile.write("from " + module + " import *\n")
    initFile.close()

    commandManager.runRmCommand(sad._TEMP_LS_MODULES_FILE_NAME)

    outputBotFile = open(sad.OUTPUT_BOT_PATH, 'w')
    utils._generateHeaders(outputBotFile, testFlag)
    outputBotFile.write("import sys\n")
    outputBotFile.write("import os\n")
    outputBotFile.write("from telegram.ext import Updater\n")
    outputBotFile.write("import ravegen.Decorators.functionManager as functionManager\n")
    outputBotFile.write("sys.path.insert(0, '.')\n")
    outputBotFile.write("import modules\n")
    outputBotFile.write("import logging\n")

    if testFlag:
        _generateTestBot(outputBotFile)
    else:
        if hosting == sad._DEPLOY_HEROKU_OPTION:
            herokuBotManager.generateBot(outputBotFile)
        elif hosting == sad._DEPLOY_GAE_OPTION:
            gaeBotManager.generateBot(outputBotFile)


def deployBot(withOptions = False, testFlag = True, generateFlag = True):
    if not withOptions:
        if utils.file_Or_Directory_Exists(sad._ACTUAL_PATH, sad._OUTPUT_BOT_DIR_):
            if utils.file_Or_Directory_Exists(sad._OUTPUT_BOT_DIR_, sad._OUTPUT_BOT_NAME_):
                generateFlag = False
                headers = utils._getHeaders()
                testFlag = headers[sad._HEADER_TOKEN_FLAG] == sad._STR_TRUE_
    if testFlag:
        if generateFlag:
            generateBot(testFlag)
        logManager.printVerbose("Running Test Bot")
        commandManager.runPythonCommand(sad.OUTPUT_BOT_PATH)
        commandManager.runRmCommand(sad._MODULES_DIR_ + sad._DF_ + sad._LINUX_ALL_TAG_ + sad._PYC_EXTENTION)
    else:
        cloudManager.configure()
        if generateFlag:
            generateBot(testFlag)
        cloudManager.deploy()


def changeState(testFlag):
    if testFlag:
        deployBot(withOptions=True)
    else:
        logManager.printVerbose("Changing to deploy mode...")
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        logger = logging.getLogger(__name__)
        config = configManager.getConfig()
        updater = Updater(config.get(sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_TOKEN_OPTION_))
        webhookURL = configManager.get(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_DEPLOY_URL_OPTION)
        webhookPath = configManager.get(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_WEBHOOK_PATH_OPTION)
        if(webhookURL[-1] == '/'):
            webhookURL = webhookURL[:-1]
        if(webhookPath[-1] == '/'):
            webhookPath = webhookPath[:-1]
        webhookURL += sad._DF_ + webhookPath
        logManager.printVerbose("Changing webhook to: " + webhookURL)
        updater.bot.setWebhook(webhookURL)
        logManager.printVerbose("DONE")


def _generateTestBot(outputBotFile):
    config = configManager.getConfig()
    TOKEN = config.get(sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_TOKEN_TEST_OPTION)
    port = configManager.get(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_DEPLOY_PORT_OPRION)
    outputBotFile.write('\n')
    outputBotFile.write("if __name__ == \"__main__\":\n")
    outputBotFile.write("\tTOKEN = \"" + TOKEN + "\"\n")
    if port != None and port != sad._INIT_CONFIG_DEPLOY_PORT:
        outputBotFile.write("\tPORT = " + str(port) + "\n")
    outputBotFile.write("\tlogging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)\n")
    outputBotFile.write("\tlogger = logging.getLogger(__name__)\n")
    outputBotFile.write("\tupdater = Updater(TOKEN)\n")
    outputBotFile.write("\tdispatcher = updater.dispatcher\n")
    outputBotFile.write("\tfunctionManager.functionManager.generateHandlers(dispatcher)\n")
    outputBotFile.write("\tupdater.bot.deleteWebhook()\n")
    outputBotFile.write("\tupdater.start_polling()\n")
    outputBotFile.write("\tupdater.idle()\n")
    outputBotFile.close()
