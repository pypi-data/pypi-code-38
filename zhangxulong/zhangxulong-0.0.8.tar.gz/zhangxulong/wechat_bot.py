# coding=utf8
import requests
import itchat


class Wechat_Bot:
    def __init__(self, tuling_api_key='52075fb8edc7463ab304cf80a2b5ffe0'):
        self.KEY = tuling_api_key

        # 请求图灵机器人并得到返回消息
        def get_response(msg, nickname):
            apiUrl = 'http://www.tuling123.com/openapi/api'
            data = {
                'key': self.KEY,
                'info': msg,
                'userid': nickname
            }
            try:
                r = requests.post(apiUrl, data=data).json()
                return r.get('text')
            except:
                return

        # 微信私聊回复
        @itchat.msg_register(itchat.content.TEXT)
        def tuling_reply(msg):
            default_reply = 'I received: ' + msg['Text']
            # 调用图灵机器人
            reply = get_response(msg['Text'], msg['FromUserName'])
            return reply or default_reply

        # 微信群聊回复
        @itchat.msg_register(itchat.content.TEXT, isGroupChat=True)
        def text_reply(msg):
            if msg['isAt']:
                # 调用机器人
                reply = get_response(msg['Text'], msg['FromUserName'])
                itchat.send(u'@%s\u2005: %s' % (msg['ActualNickName'], reply), msg['FromUserName'])

        itchat.auto_login(hotReload=True)
        itchat.run()


if __name__ == '__main__':
    wechat_bot = Wechat_Bot()
