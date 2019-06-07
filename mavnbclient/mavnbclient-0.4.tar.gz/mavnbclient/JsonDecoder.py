#!/usr/bin/python

import datetime
import Message
import json
import logging
from NBException import JsonEncodeException, JsonDecodeException

logger = logging.getLogger(__name__)

def validateMsgObject(msgObject):
	logger.debug("Enter")
	if msgObject.recipient == "":
		logger.error("Recipient is empty")
		raise JsonEncodeException("Recipient is empty", "Add the User Id", msgObject)
	if msgObject.messageType == "Text" and msgObject.messageText == "":
		logger.error("Text is empty")
		raise JsonEncodeException("Text is empty", "add a message body", msgObject)
	if msgObject.messageType == "File" and msgObject.fileJson == "":
		logger.error("File Json is empty")
		raise JsonEncodeException("File Json is empty", "add a file json", msgObject)
	if msgObject.messageType == "RichCard" and msgObject.richCard == "":
		logger.error("Rich Card is empty")
		raise JsonEncodeException("Rich Card is empty", "add a Rich Card", msgObject)

def validateDecodedMessage(msgObject, msgJson):
	logger.debug("Enter")
	if msgObject.sender == "":
		logger.error("Sender is empty")
		raise JsonDecodeException("Sender is empty", "Add the User Id", msgJson)
	if msgObject.messageType == "Text" and msgObject.messageText == "":
		logger.error("Text is empty")
		raise JsonDecodeException("Text is empty", "add a message body", msgJson)
	if msgObject.messageType == "File" and msgObject.fileJson == "":
		logger.error("File Json is empty")
		raise JsonDecodeException("File Json is empty", "add a file json")
	if msgObject.messageType == "RichCard" and msgObject.richCard == "":
		logger.error("Rich Card is empty")
		raise JsonDecodeException("Rich Card is empty", "add a Rich Card", msgJson)
	if msgObject.messageType == "GeoLoc" and msgObject.geoLoc == "":
		logger.error("GeoLocation is empty")
		raise JsonDecodeException("GeoLocation is empty", "add a GeoLocation")
	

def encodeMessageObj(msgObj, suggestedChipList = ""):
	logger.debug("Enter")
	validateMsgObject(msgObj)
	logger.info("Encoding Msg Object {}".format(msgObj.toString()))
	message = "{\"RCSMessage\": {"
	isDeliveredNeeded = False
	isDisplayedNeeded = False
	for report in msgObj.reportsRequired:
		if report == "Delivered":
			isDeliveredNeeded = True
		if report == "Displayed":
			isDisplayedNeeded = True
	if isDeliveredNeeded == True and isDisplayedNeeded == True:
		message += "{\"reportRequest\": [\"Delivered\", \"Displayed\"],"
	if isDeliveredNeeded == True and isDisplayedNeeded == False:
		message += "{\"reportRequest\": [\"Delivered\"],"
	if isDeliveredNeeded == False and isDisplayedNeeded == True:
		message += "\"reportRequest\": [\"Displayed\"],"

	message += "\"timestamp\": \""+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\""

	if msgObj.messageText != "":
		message += ", \"textMessage\": \"" + msgObj.messageText + "\""
	
	if msgObj.messageType == "File":
		message +=  ", \"fileMessage\" :" + msgObj.fileJson
	
	if msgObj.suggestedChipList != "":
		message += "," + "\"suggestedChipList\" : " + msgObj.suggestedChipList

	if msgObj.richCard != "":
		message += ", \"richcardMessage\" : " + msgObj.richCard

	message += "},"
	message += "\"messageContact\": {"
	message += "\"userContact\": "
	message += "\"" + msgObj.recipient + "\"}"
	message += "}"
	logger.info("Msg Json = {}".format(message))
	return message

def encodeStatusObj(msgObj, status):
	logger.debug("Enter")
	logger.info("Encoding Msg Object {}".format(msgObj.toString()))
	message = "{\"RCSMessage\": {"
	message += "\"status\": \""+status+"\"}"
	message += "}"
	logger.info("Msg Json = {}".format(message))
	return message

def encodeIsTypingObj(msgObj):
	logger.debug("Enter")
	logger.info("Encoding Msg Object {}".format(msgObj.toString()))
	message = "{\"RCSMessage\": {"
	message += "\"isTyping\": \"active\"},"
	message += "\"messageContact\": {"
	message += "\"userContact\": "
	message += "\"" + msgObj.recipient + "\"}"
	message += "}"
	logger.info("Msg Json = {}".format(message))
	return message

def decodeIncomingMessage(msgString):
	logger.debug("Enter")
	logger.info("Decoding Msg String {}".format(msgString))
	jsonMsg = json.loads(msgString)
	if jsonMsg["event"] == "messageStatus":
		return decodeStatusReport(jsonMsg)
	if jsonMsg["event"] == "message":
		return decodeMessage(jsonMsg, msgString)
	if jsonMsg["event"] == "isTyping":
		return decodeIsTyping(jsonMsg)
	if jsonMsg["event"] == "response":
		return decodeSuggestedResponse(jsonMsg)

def decodeSuggestedResponse(jsonMsg):
	logger.debug("Enter")
	message = Message.Message()
	message.sender = jsonMsg["messageContact"]["userContact"]
	message.recipient = jsonMsg["messageContact"].get("tParticipantAddress","")
	message.msgId = jsonMsg["RCSMessage"]["msgId"]
	message.timestamp = jsonMsg["RCSMessage"]["timestamp"]
	message.suggestedResponse = json.dumps(jsonMsg["RCSMessage"]["suggestedResponse"])
	message.messageType = "SuggestedResponse"
	logger.info("Decoded Msg Object {}".format(message.toString()))
	return message

def decodeMessage(jsonMsg, msgString):
	logger.debug("Enter")
	message = Message.Message()
	message.sender = jsonMsg["messageContact"]["userContact"]
	message.recipient = jsonMsg["messageContact"].get("tParticipantAddress","")
	message.msgId = jsonMsg["RCSMessage"]["msgId"]
	message.report = jsonMsg["RCSMessage"].get("reportRequest", "")
	message.timestamp = jsonMsg["RCSMessage"]["timestamp"]
	message.callbackUrl = jsonMsg["callbackURL"]
	message.callbackUrlValidity = jsonMsg["callbackUrlValidity"]
	try:
		message.messageText = jsonMsg["RCSMessage"]["textMessage"]
		message.messageType = "Text"
	except:
		logger.info("textMessage is not present check for GeoLoc")
		message.geoLoc = jsonMsg["RCSMessage"]["geolocationPushMessage"]
		message.messageType = "GeoLoc"

	for report in message.report:
		if report == "Delivered":
			message.isDisplayed = True
		if report == "Displayed":
			message.isDelivered = True
	logger.info("Decoded Msg Object {}".format(message.toString()))
	validateDecodedMessage(message, msgString)
	return message

def decodeIsTyping(jsonMsg):
	logger.debug("Enter")
	message = Message.Message()
	message.messageType = "IsTyping"
	message.sender = jsonMsg["messageContact"]["userContact"]
	message.recipient = jsonMsg["messageContact"].get("tParticipantAddress","")
	message.msgId = jsonMsg["RCSMessage"].get("msgId","")
	message.timestamp = jsonMsg["RCSMessage"]["timestamp"]
	logger.info("Decoded Msg Object {}".format(message.toString()))
	return message

def decodeStatusReport(jsonMsg):
	logger.debug("Enter")
	status = Message.Message()
	status.messageType = "Status"
	status.sender = jsonMsg["messageContact"]["userContact"]
	status.recipient = jsonMsg["messageContact"].get("tParticipantAddress","")
	status.msgId = jsonMsg["RCSMessage"]["msgId"]
	status.reportType = jsonMsg["RCSMessage"]["status"]
	status.timestamp = jsonMsg["RCSMessage"]["timestamp"]
	logger.info("Decoded Msg Object {}".format(status.toString()))
	return status

if __name__ == "__main__":
	'''
	statusMessage = "{\"callbackURL\": \"38.96.209.251:8081\", \"RCSMessage\": {\"msgId\": \"c6410ac7-515e-49b8-be27-2e9b78afbee0\", \"timestamp\": \"2018-11-19T02:27:24Z\", \"status\": \"displayed\"}, \"event\": \"messageStatus\", \"messageContact\": {\"userContact\": \"+19843033304\", \"tParticipantAddress\": \"\"}}"
	msg = decodeIncomingMessage(statusMessage)
	print msg.toString()

	message = "{\"callbackURL\": \"38.96.209.251:8081\", \"RCSMessage\": {\"reportRequest\": [\"Displayed\"], \"msgId\": \"101716dc-fcce-4f44-bd56-71bff74053d3\", \"timestamp\": \"2018-11-19T02:27:41Z\", \"textMessage\": \"Hello\"}, \"event\": \"message\", \"messageContact\": {\"userContact\": \"+19843033304\", \"tParticipantAddress\": \"SJI871542607110@botplatform.lab.t-mobile.com\"}}"
	msg = decodeIncomingMessage(message)
	print msg.toString()

	msgObj = Message.Message(messageType = "Status", msgId = "1234", recipient = "2345", reportType = "delivered" )
	encodeMessageObj(msgObj)

	status = encodeStatusObj(msgObj)
	print status
	logger.info(status)

	msgObj = Message.Message(messageType = "IsTyping", msgId = "1234", recipient = "2345", reportType = "delivered" )
	encodeIsTypingObj(msgObj)
	'''

	msgObject1 = Message.Message()
	validateMsgObject(msgObject1)
	
