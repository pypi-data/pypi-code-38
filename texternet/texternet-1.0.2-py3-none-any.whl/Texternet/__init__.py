#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import OrderedDict
from datetime import datetime

from twilio.rest import Client

name = 'Texternet'

"""This is the class that manages communication between the Texternet server and the Twilio API."""
class Texternet:
    pass
    def __init__(self, ACCOUNT_SID, AUTH_TOKEN, PHONENUM):
        """
                This method sets up a new connection to the Twilio API.

                """
        self.account_sid = ACCOUNT_SID
        self.auth_token = AUTH_TOKEN
        self.Login = False
        self.username = None
        self.userInfo = None
        self.client = Client(self.account_sid, self.auth_token)
        self.phone_num = PHONENUM

    def getMessages(self, date):
        """
                Using a given time, you get the messages from that point on.
                
                Parameters
                ----------
                date : datetime.datetime
                    The date of the starting point.
                    
                """
        messages = self.client.messages.list(
            date_sent_after=date,
            to=self.phone_num,
        )
        return messages

    def sendMessage(self, number, msg):
        """
                Sends a given text message to a given number.
                
                Parameters
                ----------
                number : str
                    given phone number preceded by the counry code. (ex. '+18171111111')

                msg : str
                    The message to be sent to the specified number.

                """
        message = self.client.messages.create(body=msg, from_=self.phone_num, to=number)
        return message.sid

    def sendFile(self, number, file):
        """
                Sends a given file to a given number.
                
                Parameters
                ----------
                number : str
                    given phone number preceded by the counry code. (ex. '+18171111111')

                file : str
                    The URL of the file to be sent to the specified number.

                """
        message = self.client.messages.create(
            from_=self.phone_num,
            media_url=file,
            to=number,
        )
        return message.sid


if __name__ == "__main__":
    print("can't run this file.")
