from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram.ext import CallbackQueryHandler
import telegram
import json
import sadDec
import time
import logging


class FunctionManager:
    def __init__(self):
        self.commands = {}
        self.messages = {}
        self.errors = {}
        self.functions = {}
        self.callback = None
        self.dispatcher = None


    def addCommand(self, commandHandler):
        self.commands[commandHandler.funcName] = commandHandler

    def addMessage(self, messageHandler):
        self.messages[messageHandler.funcName] = messageHandler

    def addError(self, errorHandler):
        self.errors[errorHandler.funcName] = errorHandler

    def addFunction(self, functionHandler):
        self.functions[functionHandler.funcName] = functionHandler

    def addCallBack(self, callbackHandler):
        self.callback = callbackHandler

    def test_run(self):
        for _, func in self.messages.iteritems():
            func(message=func.filter)

    def generateHandlers(self, dispatcher):
        self.dispatcher = dispatcher
        self.generateCommandHandlers(dispatcher)
        self.generateMsgHandlers(dispatcher)
        self.generateErrorHandlers(dispatcher)
        self.generateHelpCommand(dispatcher)
        if self.callback:
            dispatcher.add_handler(CallbackQueryHandler(self.callback))
        else:
            dispatcher.add_handler(CallbackQueryHandler(self.rv_callbackQueryHandler))

    def generateCommandHandlers(self, distpatcher):
        for _, command in self.commands.iteritems():
            distpatcher.add_handler(CommandHandler(command.funcName, command, pass_args = command.passArgs))

    def generateMsgHandlers(self, dispatcher):
        for _, message in self.messages.iteritems():
            if(message.filter == sadDec._MESSAGE_HANDLER_TEXT_):
                dispatcher.add_handler(MessageHandler(Filters.text, message))

    def generateErrorHandlers(self, dispatcher):
        for _, error in self.errors.iteritems():
            dispatcher.add_error_handler(error)

    def rv_callbackQueryHandler(self, bot, update):
        query = update.callback_query
        try:
            data = json.loads(query.data)
        except json.JSONDecodeError:
            data = query.data

        if isinstance(data, dict) and sadDec._CALLBACK_QUERY_COMMAND_OPTION in data:
            text = '/' + data[sadDec._CALLBACK_QUERY_COMMAND_OPTION]
            if sadDec._CALLBACK_QUERY_ARGS_OPTION in data:
                text += ' ' + data[sadDec._CALLBACK_QUERY_ARGS_OPTION]
            newUpdate_dic = {}
            newUpdate_dic['update_id'] = update['update_id']
            newUpdate_dic['message'] = {}
            newUpdate_dic['message']['date'] =  time.mktime(update['callback_query']['message']['date'].timetuple())
            newUpdate_dic['message']['message_id'] = update['callback_query']['message']['message_id']
            newUpdate_dic['message']['from'] = {}
            newUpdate_dic['message']['from']['username'] = update['callback_query']['from_user']['username']
            newUpdate_dic['message']['from']['first_name'] = update['callback_query']['from_user']['first_name']
            newUpdate_dic['message']['from']['last_name'] = update['callback_query']['from_user']['last_name']
            newUpdate_dic['message']['from']['is_bot'] = update['callback_query']['from_user']['is_bot']
            newUpdate_dic['message']['from']['laguage_code'] = update['callback_query']['from_user']['language_code']
            newUpdate_dic['message']['from']['id'] = update['callback_query']['from_user']['id']
            newUpdate_dic['message']['chat'] = {}
            newUpdate_dic['message']['chat']['username'] = update['callback_query']['message']['chat']['username']
            newUpdate_dic['message']['chat']['first_name'] = update['callback_query']['message']['chat']['first_name']
            newUpdate_dic['message']['chat']['last_name'] = update['callback_query']['message']['chat']['last_name']
            newUpdate_dic['message']['chat']['type'] = update['callback_query']['message']['chat']['type']
            newUpdate_dic['message']['chat']['id'] = update['callback_query']['message']['chat']['id']
            newUpdate_dic['message']['text'] = text
            newUpdate_dic['message']['entities'] = [{}]
            newUpdate_dic['message']['entities'][0]['length'] = len(data[sadDec._CALLBACK_QUERY_COMMAND_OPTION]) + 1
            newUpdate_dic['message']['entities'][0]['type'] = "bot_command"
            newUpdate_dic['message']['entities'][0]['offset'] = 0

            newUpdate = telegram.Update.de_json(newUpdate_dic, bot)
            self.dispatcher.process_update(newUpdate)
        elif isinstance(data, dict) and sadDec._CALLBACK_QUERY_FUNCTION_OPTION in data:
            if data[sadDec._CALLBACK_QUERY_FUNCTION_OPTION] in self.functions:
                funcName = data[sadDec._CALLBACK_QUERY_FUNCTION_OPTION]
                del data[sadDec._CALLBACK_QUERY_FUNCTION_OPTION]
                self.functions[funcName](bot, update, **data)
            else:
                logging.error("Function " + data[sadDec._CALLBACK_QUERY_FUNCTION_OPTION] + " doesn't exist")
        else:
            logging.error("Error in the callback_query format")
            logging.error(data)

    def generateHelpCommand(self, dispatcher):
        if sadDec._BOT_HELP_COMMAND_ not in self.commands:
            def help(bot, update):
                replyText = bot.first_name + "\n"
                replyText += "*Commands:*\n"
                for key, func in self.commands.iteritems():
                    key = self.formatFunctionName(key)
                    if(func.description):
                        replyText += "/" + key + ": " + func.description + "\n"
                    else:
                        replyText += "/" + key + "\n"
                for key, func in self.messages.iteritems():
                    if(func.filter == sadDec._MESSAGE_HANDLER_TEXT_):
                        replyText += "*For text messages:* " + func.description
                update.effective_message.reply_text(replyText, parse_mode=telegram.ParseMode.MARKDOWN)
            dispatcher.add_handler(CommandHandler(sadDec._BOT_HELP_COMMAND_, help))

    def formatFunctionName(self, key):
        newKey = ""
        for c in key:
            if(c == '_'):
                newKey += "\\"
            newKey += c
        return newKey

functionManager = FunctionManager()
