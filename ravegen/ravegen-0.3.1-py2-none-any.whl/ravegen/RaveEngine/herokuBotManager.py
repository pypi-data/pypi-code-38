import Utils.sad as sad
import configManager as configManager
import Utils.errorHandler as errorHandler

herokuBotErrorHandler = errorHandler.ErrorHandler("Horuku Bot Manager Error Handler")

def generateBot(outputBotFile):
    config = configManager.getConfig()
    TOKEN = config.get(sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_TOKEN_OPTION_)
    port = configManager.get(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_DEPLOY_PORT_OPRION)
    webhookURL = configManager.get(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_DEPLOY_URL_OPTION)
    if webhookURL is None or webhookURL == sad._INIT_CONFIG_DEPLOY_URL:
        herokuBotErrorHandler.addError("Deploy URL is empty", errorType=sad._CRITICAL_ERROR_)
    webhookPath = configManager.get(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_WEBHOOK_PATH_OPTION)
    outputBotFile.write('\n')
    outputBotFile.write("if __name__ == \"__main__\":\n")
    outputBotFile.write("\tTOKEN = \"" + TOKEN + "\"\n")
    if port is None or port == sad._INIT_CONFIG_DEPLOY_PORT:
        outputBotFile.write("\tPORT = os.environ.get('PORT')\n")
    else:
        outputBotFile.write("\tPORT = " + str(port) + "\n")
    outputBotFile.write("\tlogging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)\n")
    outputBotFile.write("\tlogger = logging.getLogger(__name__)\n")
    outputBotFile.write("\tupdater = Updater(TOKEN)\n")
    outputBotFile.write("\tdispatcher = updater.dispatcher\n")
    outputBotFile.write("\tfunctionManager.functionManager.generateHandlers(dispatcher)\n")
    if webhookPath is None or webhookPath == sad._INIT_CONFIG_WEBHOOK_PATH:
        outputBotFile.write("\tupdater.start_webhook(listen=\"0.0.0.0\", port=int(PORT), url_path=TOKEN)\n")
        webhookURL += TOKEN
    else:
        outputBotFile.write("\tupdater.start_webhook(listen=\"0.0.0.0\", port=int(PORT), url_path=\"" + webhookPath + "\")\n")
        webhookURL += webhookPath
    outputBotFile.write("\tupdater.bot.setWebhook(\"" + webhookURL + "\")\n")
    outputBotFile.write("\tupdater.idle()\n")
    outputBotFile.close()

    herokuBotErrorHandler.handle()
