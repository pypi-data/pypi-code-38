from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import functools
import MessageHandler
import CommandHandler
import FunctionHandler
import Error
import functionManager
import CallBackHandler
import sadDec
import json
import logging

def _convertToJson(string):
    dic_res = {}
    tuples = string.split(',')
    for _tuple in tuples:
        values = _tuple.split('::')
        values[0] = values[0].strip()
        values[1] = values[1].strip()
        dic_res[values[0]] = values[1]
    return dic_res

def _build_callback(data):
    return_value = json.dumps(data)
    return return_value

def _generateMenu(menu):
        keyboard = []
        for row in menu:
            keyboard.append([])
            for button in row:
                data = _convertToJson(button[1])
                if sadDec._MENU_DATA_COMMAND_OPTION in data or sadDec._MENU_DATA_FUNCTION_OPTION in data:
                    keyboard[-1].append(InlineKeyboardButton(button[0], callback_data=_build_callback(data)))
                elif sadDec._MENU_DATA_URL_OPTION in data:
                    keyboard[-1].append(InlineKeyboardButton(button[0], url=data[sadDec._MENU_DATA_URL_OPTION]))
                else:
                    logging.error("Bad menu formatting")
                    return None
        reply_markup = InlineKeyboardMarkup(keyboard)
        return reply_markup

class RaveGen:
    def __init__(self, handler):
        functools.update_wrapper(self, handler)
        self.handler = handler
        self.getNewHandler()


    def getNewHandler(self):
        if(self.handler.handlerType == sadDec._HANDLER_TYPE_COMMAND_):
            functionManager.functionManager.addCommand(self.c_handler())

        elif(self.handler.handlerType == sadDec._HANDLER_TYPE_MESSAGE_):
            functionManager.functionManager.addMessage(self.m_handler(filter=self.handler.filter))

        elif(self.handler.handlerType == sadDec._HANDLER_TYPE_ERROR_):
            functionManager.functionManager.addError(self.e_handler())

        elif(self.handler.handlerType == sadDec._HANDLER_TYPE_FUNCTION_):
            functionManager.functionManager.addFunction(self.f_handler())

        elif(self.handler.handlerType == sadDec._HANDLER_TYPE_CALLBACK_):
            functionManager.functionManager.addCallBack(self.cb_handler())

    def m_handler(self, *arg, **karg):
        _filter = karg["filter"]
        def _m_handler(bot, update):
            message = update.effective_message.text
            reply = self.handler(message=message)
            if reply is None:
                return
            if isinstance(reply, (str,unicode)):
                update.effective_message.reply_text(reply)
            else:
                try:
                    reply_markup = _generateMenu(reply[sadDec._MENU_INDEX_])
                    update.effective_message.reply_text(reply[sadDec._MESSAGE_INDEX_], reply_markup=reply_markup)
                except IndexError:
                    logging.error("Bad menu formatting")

        _newMessageHandler = MessageHandler.MessageHandler(_m_handler, _filter, funcName=self.handler.funcName, description=self.handler.description)
        return _newMessageHandler

    def c_handler(self, *arg, **karg):
        def _c_handler(bot, update, args = None):
            message = ''
            if(args != None):
                message = ' '.join(args)
            reply = self.handler(message=message)
            if reply is None:
                return
            if isinstance(reply, (str,unicode)):
                update.effective_message.reply_text(reply)
            else:
                try:
                    reply_markup = _generateMenu(reply[sadDec._MENU_INDEX_])
                    update.effective_message.reply_text(reply[sadDec._MESSAGE_INDEX_], reply_markup=reply_markup)
                except IndexError:
                    logging.error("Bad menu formatting")

        _newCommandHandler = CommandHandler._Command(_c_handler, funcName=self.handler.funcName, passArgs=True, description=self.handler.description)
        return _newCommandHandler

    def e_handler(self, *arg, **karg):
        def _e_handler(bot, update, error):
            reply = self.handler(message=str(error))
        _newErrorHandler = Error.Error(_e_handler, funcName=self.handler.funcName)
        return _newErrorHandler

    def f_handler(self, *arg, **karg):
        def _f_handler(bot, update, *arg, **karg):
            reply = self.handler(*arg, **karg)
            if reply is None:
                return
            if isinstance(reply, (str,unicode)):
                update.effective_message.reply_text(reply)
            else:
                try:
                    reply_markup = _generateMenu(reply[sadDec._MENU_INDEX_])
                    update.effective_message.reply_text(reply[sadDec._MESSAGE_INDEX_], reply_markup=reply_markup)
                except IndexError:
                    logging.error("Bad menu formatting")
        _newFunctionHandler = FunctionHandler.RaveFunction(_f_handler, funcName=self.handler.funcName)
        return _newFunctionHandler

    def cb_handler(self, *arg, **karg):
        def _cb_handler(bot, update, *arg, **karg):
            query = update.callback_query
            reply = self.handler(query, *arg, **karg)
            if reply is None:
                return
            if isinstance(reply, (str,unicode)):
                update.effective_message.reply_text(reply)
            else:
                try:
                    reply_markup = _generateMenu(reply[sadDec._MENU_INDEX_])
                    update.effective_message.reply_text(reply[sadDec._MESSAGE_INDEX_], reply_markup=reply_markup)
                except IndexError:
                    logging.error("Bad menu formatting")
        _newCallBackHandler = CallBackHandler.CallBack(_cb_handler, funcName=self.handler.funcName)
        return _newCallBackHandler
