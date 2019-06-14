import RaveEngine.configManager as configManager
import Utils.sad as sad
import Utils.errorHandler as errorHandler

gaeBotErrorHandler = errorHandler.ErrorHandler("GAE Bot Manager Error Handler")

def generateBot(outputBotFile):
    config = configManager.getConfig()
    TOKEN = configManager.get(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_TOKEN_OPTION_)
    deployUrl = configManager.get(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_DEPLOY_URL_OPTION)
    if deployUrl is None or deployUrl == sad._INIT_CONFIG_DEPLOY_URL:
        gaeBotErrorHandler.addError("Deploy Url is emprty", sad._CRITICAL_ERROR_)
    webhookPath = configManager.get(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_WEBHOOK_PATH_OPTION)


    outputBotFile.write("from telegram import Update\n")
    outputBotFile.write("from flask import Flask, request\n\n")
    outputBotFile.write("app = Flask(__name__)\n")
    outputBotFile.write("global updater\n")
    outputBotFile.write("global TOKEN\n")
    outputBotFile.write("TOKEN = '" + TOKEN + "'\n")
    outputBotFile.write("updater = Updater(TOKEN)\n\n")

    if webhookPath is None or webhookPath == sad._INIT_CONFIG_WEBHOOK_PATH:
        outputBotFile.write("@app.route('/' + TOKEN, methods=['POST'])\n")
    else:
        outputBotFile.write("@app.route('/" + webhookPath + "', methods=['POST'])\n")
    outputBotFile.write("def webhook_handler():\n")
    outputBotFile.write("\tif request.method == 'POST':\n")
    outputBotFile.write("\t\tlogging.info(request.get_json(force=True))\n")
    outputBotFile.write("\t\tupdate = Update.de_json(request.get_json(force=True), updater.bot)\n")
    outputBotFile.write("\t\tupdater.dispatcher.process_update(update)\n")
    outputBotFile.write("\treturn 'ok'\n\n\n")
    outputBotFile.write("@app.route('/set_webhook', methods=['GET', 'POST'])\n")
    outputBotFile.write("def set_webhook():\n")
    outputBotFile.write("\tdispatcher = updater.dispatcher\n")
    outputBotFile.write("\tfunctionManager.functionManager.generateHandlers(dispatcher)\n")
    if webhookPath is None or webhookPath == sad._INIT_CONFIG_WEBHOOK_PATH:
        outputBotFile.write("\ts = updater.bot.setWebhook('" + deployUrl + "' + TOKEN)\n")
    else:
        outputBotFile.write("\ts = updater.bot.setWebhook('" + deployUrl + webhookPath + "')\n")
    outputBotFile.write("\tif s:\n")
    outputBotFile.write("\t\treturn 'webhook setup ok'\n")
    outputBotFile.write("\telse:\n")
    outputBotFile.write("\t\treturn 'webhook setup failed'\n\n\n")
    outputBotFile.write("@app.route('/')\n")
    outputBotFile.write("def index():\n")
    outputBotFile.write("\treturn 'Hello World'\n")
    outputBotFile.close()

    gaeBotErrorHandler.handle()
