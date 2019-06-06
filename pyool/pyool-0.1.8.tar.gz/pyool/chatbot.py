import requests 
import time 
from .logger_setting import logger  



# Defining ChatBot specific Class to send messages to Dingtalk 

class ChatBot: 

    def send_markdown(self, payload, access_token, retry_time = 0, buffering = 5): 

        """
        Sending markdown content in payload to Dingtalk

        Parameters
        ----------
        payload : dict
            the information to be sent 
        access_token : str
            the token of the DingTalk ChatBot that is given when generating the ChatBot
            example is https://oapi.dingtalk.com/robot/send?access_token={} 
            the string behind the "access_token" is what to be input here
        retry_time : int
            number of times to retry sending the message 
        buffering : int 
            the number of seconds waiting between retries 

        Returns
        -------
        bool
            True if successful
        
        Raises
        ------
        RuntimeError
            if failed to send message 

        Examples
        --------

        """

        url = "https://oapi.dingtalk.com/robot/send?access_token=" + str(access_token)  
        headers = {"Content-Type": "application/json;charset=utf-8"}

        attempt = 0 

        while attempt == 0 or attempt < retry_time:
            logger.info("Sending to Dingtalk .....")

            r = requests.post(url, headers = headers, json = payload) 

            if (r.text == """{"errcode":0,"errmsg":"ok"}""" or r.text == """{"errmsg":"ok","errcode":0}"""): 
                logger.info("Message is sent.")
                return True 

            else: 
                attempt += 1
                logger.error("Attempt {}. {}. Retrying .....".format(attempt, r.text)) 
                time.sleep(buffering)
                continue 
            
        raise RuntimeError("Cannnot send message due to: %s" % r.text) 



    def send2ding(self, title, message, access_token, retry_time = 3, buffering = 5):

        """
        Generate payload from inputs to attach with the message and send out to DingTalk
        using send_markdown()

        Parameters
        ----------
        title : str
            title of the message 
        message : str
            content of the message 
        access_token : string
            the token of the DingTalk ChatBot that is given when generating the ChatBot
            example is https://oapi.dingtalk.com/robot/send?access_token={} 
            the string behind the "access_token" is what to be input here 
        retry_time : int
            number of times to retry sending the message 
        buffering : int 
            the number of seconds waiting between retries 

        Returns
        -------
        bool
            True if successful

        Raises
        ------
        RuntimeError
            if failed to send message 

        Examples
        --------
        
        """

        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": message 
            }, 
            "at": {}
        }

        self.send_markdown(payload = payload, access_token = access_token, retry_time = retry_time, buffering = buffering) 
