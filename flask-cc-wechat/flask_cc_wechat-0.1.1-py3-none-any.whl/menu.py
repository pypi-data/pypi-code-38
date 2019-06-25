import requests
from . import WECHAT_API_URL


class Menu(object):
    """
    自定义菜单栏
    """

    def __init__(self):
        pass

    def create(self, postData, accessToken):
        postUrl = WECHAT_API_URL + \
            "cgi-bin/menu/create?access_token=%s" % accessToken
        request = requests.post(postUrl, data=postData.encode('utf-8'))
        self.get_current_selfmenu_info(accessToken)
        if request.status_code == 200:
            return True
        else:
            return False

    def query(self, accessToken):
        postUrl = WECHAT_API_URL + \
            "cgi-bin/menu/get?access_token=%s" % accessToken
        requests.get(postUrl)

    def delete(self, accessToken):
        postUrl = WECHAT_API_URL + \
            "cgi-bin/menu/delete?access_token=%s" % accessToken
        requests.get(postUrl)

    def get_current_selfmenu_info(self, accessToken):
        postUrl = WECHAT_API_URL + \
            "cgi-bin/get_current_selfmenu_info?access_token=%s" % accessToken
        request = requests.get(postUrl)
        return request.text
