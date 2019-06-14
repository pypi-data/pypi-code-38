import herokuManager
import gaeManager
import Utils.sad as sad
import Utils.logManager as logManager
import Utils.inputManager as inputManager
import RaveEngine.configManager as configManager
import signal

def configure():
    config = configManager.getConfig()
    hosting = configManager.get(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_HOSTING_OPTION_)
    if hosting == sad._DEPLOY_HEROKU_OPTION:
        herokuManager.initConfiguration()
        signal.signal(signal.SIGINT, herokuManager.sigintHandler)
    elif hosting == sad._DEPLOY_GAE_OPTION:
        gaeManager.initConfiguration()
        signal.signal(signal.SIGINT, gaeManager.sigintHandler)

def deploy():
    config = configManager.getConfig()
    hosting = configManager.get(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_HOSTING_OPTION_)
    if hosting == sad._DEPLOY_HEROKU_OPTION:
        herokuManager.deploy()
    elif hosting == sad._DEPLOY_GAE_OPTION:
        gaeManager.deploy()

def destroy():
    config = configManager.getConfig()
    hosting = configManager.get(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_HOSTING_OPTION_)
    logManager.printVerbose("WARNING: This action delete the bot in the cloud")
    token = inputManager.getInput("For security, paste here the bot token: ")
    if token == configManager.get(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_TOKEN_OPTION_):
        logManager.printVerbose("Deleting bot in the cloud...")
        if hosting == sad._DEPLOY_HEROKU_OPTION:
                herokuManager.deleteCloudApp()
        elif hosting == sad._DEPLOY_GAE_OPTION:
                gaeManager.deleteCloudApp()
    else:
        logManager.printVerbose("Ufff, the tokens don't match")
