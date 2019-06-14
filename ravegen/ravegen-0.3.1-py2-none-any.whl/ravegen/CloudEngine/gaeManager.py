import RaveEngine.configManager as configManager
import Utils.commandManager as commandManager
import Utils.errorHandler as errorHandler
import Utils.logManager as logManager
import Utils.inputManager as inputManager
import Utils.utils as utils
import Utils.sad as sad
import sys


gaeErrorHandler = errorHandler.ErrorHandler("GAE Manager")

def initConfiguration():
    logManager.printVerbose("Verifying configuration...")
    logManager.printVerbose("Verifying Google Cloud installation...")
    _verifyGAEInstallation()
    logManager.printVerbose("Verifying Curl installation...")
    _verifyCurlInstallation()
    logManager.printVerbose("Verifying Google Cloud login...")
    while True:
        if not _verifyGAELogin():
            logManager.printVerbose("Can't find google account")
            logManager.printVerbose("Google login...")
            _GAELogin()
        else:
            break
    config = configManager.getConfig()
    projectName = configManager.get(config, sad._DEPLOY_GAE_OPTION, sad._CONFIG_PROJECT_NAME_OPTION_)
    logManager.printVerbose("Verifiying project name...")
    if projectName != None and projectName != sad._INIT_CONFIG_PROJECT_NAME:
        logManager.printVerbose("Project name found: " + projectName)
    else:
        projectName = _getNewGAEName(config)
    if _verifyGAEProject(projectName):
        logManager.printVerbose("The project has already been created in Google Cloud")
        token = configManager.get(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_TOKEN_OPTION_)
        deployUrl = sad._HTTPS_ + projectName + sad._GAE_URL_
        configManager.set(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_DEPLOY_URL_OPTION, deployUrl)
        configManager.set(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_WEBHOOK_PATH_OPTION, token)
    else:
        logManager.printVerbose("Project hasn't been created in Google Cloud")
        while True:
            _GAECreate(projectName)
            if _verifyGAEProject(projectName):
                token = configManager.get(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_TOKEN_OPTION_)
                deployUrl = sad._HTTPS_ + projectName + sad._GAE_URL_
                configManager.set(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_DEPLOY_URL_OPTION, deployUrl)
                configManager.set(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_WEBHOOK_PATH_OPTION, token)
                break
            logManager.printVerbose("The project can't created in Google Cloud. Read the errors above and chose a new Google Cloud project name")
            projectName = _getNewGAEName(config)
    _GAEsetProject(projectName)
    logManager.printVerbose("All Configurations... OK")

def deploy():
    config = configManager.getConfig()
    deployUrl = configManager.get(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_DEPLOY_URL_OPTION)
    if deployUrl is None or deployUrl == sad._INIT_CONFIG_DEPLOY_URL:
        gaeErrorHandler.addError("Deploy Url is emprty", sad._CRITICAL_ERROR_)
    webhookPath = configManager.get(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_WEBHOOK_PATH_OPTION)
    if webhookPath is None or webhookPath == sad._INIT_CONFIG_WEBHOOK_PATH:
        webhookPath = configManager.get(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_TOKEN_OPTION_)
    gaeErrorHandler.handle()
    _createSkeleton()
    commandManager.runGAEDeploy()
    _deleteSkeleton()
    commandManager.runCurlCommand(deployUrl + "set_webhook")
    logManager.printVerbose("\nDeploying bot in Google Cloud...OK")

def deleteCloudApp():
    config = configManager.getConfig()
    projectName = configManager.get(config, sad._DEPLOY_GAE_OPTION, sad._CONFIG_PROJECT_NAME_OPTION_)
    if projectName != None and projectName != sad._INIT_CONFIG_PROJECT_NAME:
        commandManager.runGAEDeleteProject(projectName)
        configManager.set(config, sad._DEPLOY_GAE_OPTION, sad._CONFIG_PROJECT_NAME_OPTION_, "")
        configManager.set(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_DEPLOY_URL_OPTION, "")
        configManager.set(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_WEBHOOK_PATH_OPTION, "")

def _createSkeleton():
    appConfigFile = open(sad._GAE_APPENGINE_CONFIG_FILE_NAME_, 'w')
    appConfigFile.write("import os\n")
    appConfigFile.write("from google.appengine.ext import vendor\n")
    appConfigFile.write("vendor.add(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib'))\n")
    appConfigFile.close()
    commandManager.runCpCommand(sad.OUTPUT_BOT_PATH, sad._ACTUAL_PATH)
    appYamlFile = open(sad._GAE_APP_YAML, 'w')
    runtimeFile = open(sad._CONFIG_RUNTIME_FILE_PATH_, 'r')
    runtime = runtimeFile.readline()
    runtimeFile.close()
    appYamlFile.write("runtime: " + runtime + "\n")
    appYamlFile.write("api_version: 1\n")
    appYamlFile.write("threadsafe: yes\n\n")
    appYamlFile.write("handlers:\n")
    appYamlFile.write("- url: .*\n")
    appYamlFile.write("  script: bot.app\n\n")
    appYamlFile.write("libraries:\n")
    appYamlFile.write("- name: webapp2\n")
    appYamlFile.write("  version: \"2.5.2\"\n")
    appYamlFile.write("- name: flask\n")
    appYamlFile.write("  version: latest\n")
    appYamlFile.write("- name: ssl\n")
    appYamlFile.write("  version: latest\n")
    appYamlFile.close()
    if _generateReq():
        commandManager.runCpCommand(sad._GAE_TEMP_REQ_FILE_PATH, sad._GAE_REQ_FILE_NAME)
        logManager.printVerbose("We need to install the requirements")
        logManager.printVerbose("We need sudo privileges")
        logManager.printVerbose("Command to run: sudo pip install -t lib -r requirements.txt")
        commandManager.runPipInstallReq()
    commandManager.runRmCommand(sad._GAE_TEMP_REQ_FILE_PATH)
    commandManager.runTouchSudoCommand(sad._GAE_LIB_DIR_NAME_ + sad._DF_ + sad._INIT_PY)

def sigintHandler(sig, frame):
    _deleteSkeleton()
    sys.exit()

def _deleteSkeleton():
    commandManager.runRmCommand(sad._GAE_APPENGINE_CONFIG_FILE_NAME_)
    commandManager.runRmCommand(sad._OUTPUT_BOT_NAME_)
    commandManager.runRmCommand(sad._GAE_APP_YAML)
    commandManager.runRmCommand(sad._GAE_REQ_FILE_NAME)


def _verifyGAEInstallation():
    commandManager.runLsCommand(sad._GAE_PATH_, writeFile=sad._TEMP_LS_VERIFY_FILE_NAME)
    tempFile = open(sad._TEMP_LS_VERIFY_FILE_NAME, 'r')
    line = tempFile.readline()
    tempFile.close()
    commandManager.runRmCommand(sad._TEMP_LS_VERIFY_FILE_NAME)
    tokens = line.split(' ')
    tokens[0] = tokens[0].rstrip('\n')
    if tokens[0] != sad._GAE_PATH_:
        logManager.printVerbose("Google Cloud SDK is not installed")
        if utils.hasSupport():
            gaeErrorHandler.addError("You have to install Google Cloud SDK. Instructions: https://cloud.google.com/sdk/docs/quickstart-debian-ubuntu", sad._CRITICAL_ERROR_)
        else:
            gaeErrorHandler.addError("Google Cloud SDK is no installed", sad._CRITICAL_ERROR_)
    gaeErrorHandler.handle()

def _verifyGAELogin():
    commandManager.runGAEAuthListCommand(writeFile=sad._TEMP_GAE_AUTH_FILE_NAME)
    tempFile = open(sad._TEMP_GAE_AUTH_FILE_NAME, 'r')
    tempFile.readline()
    line = tempFile.readline()
    tokens = line.split(' ')
    tempFile.close()
    commandManager.runRmCommand(sad._TEMP_GAE_AUTH_FILE_NAME)
    return tokens[0] == sad._GAE_LOGIN_ACTIVE_

def _verifyGAEProject(projectName):
    commandManager.runGAEListProjects(sad._TEMP_LS_VERIFY_FILE_NAME)
    tempFile = open(sad._TEMP_LS_VERIFY_FILE_NAME)
    flag = False
    for line in tempFile:
        tokens = line.split(' ')
        if tokens[0] == projectName:
            flag = True
            break
    tempFile.close()
    commandManager.runRmCommand(sad._TEMP_LS_VERIFY_FILE_NAME)
    return flag

def _verifyCurlInstallation():
    commandManager.runLsCommand(sad._CURL_PATH, writeFile=sad._TEMP_LS_VERIFY_FILE_NAME)
    tempFile = open(sad._TEMP_LS_VERIFY_FILE_NAME, 'r')
    line = tempFile.readline()
    tempFile.close()
    commandManager.runRmCommand(sad._TEMP_LS_VERIFY_FILE_NAME)
    tokens = line.split(' ')
    tokens[0] = tokens[0].rstrip('\n')
    if tokens[0] != sad._CURL_PATH:
        logManager.printVerbose("Curl is not installed")
        flagOption = inputManager.getYesNoAnswer("Do you want to install Curl (Y/n): ")
        if not flagOption:
            gaeErrorHandler.addError("Curl is necessary to deploy the bot", sad._CRITICAL_ERROR_)
        else:
            if utils.hasSupport():
                commandManager.runPackageManagerInstall(sad._CURL_PACKAGE)
            else:
                gaeErrorHandler.addError("Curl is necessary to deploy the bot", sad._CRITICAL_ERROR_)
    gaeErrorHandler.handle()

def _generateReq():
    requirements = []
    installedReq = open(sad._GAE_REQ_INSTALLED_FILE_PATH, 'r')
    for line in installedReq:
        requirements.append(line.rstrip('\n'))
    installedReq.close()
    reqFile = open(sad._CONFIG_REQ_FILE_PAHT_, 'r')
    tempReq = open(sad._GAE_TEMP_REQ_FILE_PATH, 'w')
    installedReq = open(sad._GAE_REQ_INSTALLED_FILE_PATH, 'a')
    flag = False

    for line in reqFile:
        line = line.rstrip('\n')
        if not line in requirements:
            tempReq.write(line + '\n')
            installedReq.write(line + '\n')
            flag = True
    tempReq.close()
    installedReq.close()
    reqFile.close()
    return flag

def _GAELogin():
    commandManager.runGAELogin()

def _GAECreate(projectName):
    commandManager.runGAENewProject(projectName)

def _GAEsetProject(projectName):
    commandManager.runGAESetProject(projectName)

def _getNewGAEName(config):
    projectName = inputManager.getInput("Enter new GAE project name: ")
    configManager.set(config, sad._DEPLOY_GAE_OPTION, sad._CONFIG_PROJECT_NAME_OPTION_, projectName)
    return projectName
