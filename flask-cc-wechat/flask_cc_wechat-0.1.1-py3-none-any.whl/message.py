import json
import time

import requests

from . import WECHAT_API_URL
from .token import TokenUtil


class SendMessage(object):
    """
    给用户发送信息
    """

    def __init__(self):
        self.ToUserName = ""
        self.FromUserName = ""
        self.CreateTime = str(int(time.time()))
        self.MsgType = ""
        self.Content = ""

    def send_text(self):
        """
        发送文本消息
        :param toUserName:
        :param content:
        :param msgType:
        :return:
        """
        sendXml = """<xml>
         <ToUserName><![CDATA[%s]]></ToUserName>
         <FromUserName><![CDATA[%s]]></FromUserName>
         <CreateTime>%s</CreateTime>
         <MsgType><![CDATA[text]]></MsgType>
         <Content><![CDATA[%s]]></Content>
         </xml>
        """
        return sendXml % (
            self.ToUserName,
            self.FromUserName,
            self.CreateTime,
            self.Content)

    def send_tm_message(self, postdata):
        access_token = TokenUtil.access_token()
        post_url = WECHAT_API_URL + \
            "cgi-bin/message/template/send?access_token=%s" % access_token

        response = requests.post(post_url, data=postdata.encode('utf-8'))
        jsonreturn = json.loads(response.text)
        print(jsonreturn)
        if jsonreturn["errcode"] == 0:
            return True
        else:
            return False
