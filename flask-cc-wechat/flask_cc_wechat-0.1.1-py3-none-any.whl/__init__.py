WECHAT_API_URL = 'https://api.weixin.qq.com/'


class Wechat(object):

    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(self.app)

    def init_app(self, app):

        self.config = app.config

        assert self.config.get('WXAPPID'), 'WXAPPID must in config'
        assert self.config.get('WXAPPSECRET'), 'WXAPPSECRET must in config'
