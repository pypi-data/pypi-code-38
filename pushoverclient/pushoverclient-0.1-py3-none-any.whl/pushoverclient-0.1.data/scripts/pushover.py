#!python

""" Pushover Client 
    Author: Jonathon Chambers<jonathon@jonathonchambers.com>
"""

import sys
import requests
import logging

class PushoverPriority:
    """ Pushover Enums """
    NOALERT = -2
    QUIET = -1
    NORMAL = 0
    HIGH = 1
    CONFIRM_NEEDED = 2

class PushoverClient:
    API_ENDPOINT = "https://api.pushover.net/1/messages.json"
    def __init__(self, appToken: str):
        """ Constructor function that takes a Pushover Application Token """
        self.token = appToken
        self.setupLog()

    def setupLog(self):
        ## Setup Logging
        LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
        logging.basicConfig(filename = "PushOverClient.log",
                            level = logging.DEBUG,
                            format = LOG_FORMAT,
                            filemode = 'w')
        self.log = logging.getLogger("com.jonathonchambers.pushoverclient")


    def send_message(self, 
                     user: str,
                     message: str, 
                     title: str = None, 
                     priority: PushoverPriority = None,
                     retry: int = 60,
                     expire: int = 180
                     ):
        """ Sends a message to a user.
        Parameters
        ----------
        user : str,
            The user token for the user that you wish to send a message to.
        message : str,
            The actual message that you wish to send.
        title : str, 
            Per PushoverAPI Docs: your message's title, otherwise your app's name is used 
        priority: PushoverPriority
            The Pushover Priority of the message -- Determines how the message is displayed.
        retry : int, 
            Per PushoverAPI Docs: The retry parameter specifies how often (in seconds) 
            the Pushover servers will send the same notification to the user.
        expire : int,
            Per PushoverAPI Docs: The expire parameter specifies how many seconds your 
            notification will continue to be retried for (every retry seconds). 
            If the notification has not been acknowledged in expire seconds, 
            it will be marked as expired and will stop being sent to the user. 
            Note that the notification is still shown to the user after it is expired, 
            but it will not prompt the user for acknowledgement. This parameter must 
            have a maximum value of at most 10800 seconds (3 hours). 
        """
        
        # Setup a dict for Pushover Variables
        request_data = {
            "token": self.token,
            "user": user,
            "message": message,
            "title": title,
            "priority": priority,
            "expire": expire,
            "retry": retry
        }
        self.log.debug("Data Variable: ")
        self.log.debug(request_data)
        req = requests.post(PushoverClient.API_ENDPOINT, data = request_data)

        if ((req.status_code == 200) or (req.status_code == 201)):
            return True
        else:
            self.log.error("Pushover Client Pushing Message Failed")
            self.log.debug(req.text)
            return False
