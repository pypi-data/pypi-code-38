from copy import deepcopy
from requests import cookies, get, post
from retry import retry


class Login:
    def __init__(self, username, password):
        self._username = username
        self._password = password

        self._cookies = cookies.RequestsCookieJar()

        self._headers = {
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
            'DNT': '1',
            'Connection': 'keep-alive',
        }

    @retry(tries=3,delay=5,max_delay=5)
    def _login(self):
        headers = deepcopy(self._headers)
        headers.update({
            'Host': 'www.mabangerp.com',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        })

        data = {
            'username': self._username,
            'password': self._password,
            '$isMallRpcFinds': '',
            'remember': '1'
        }

        response = post('https://www.mabangerp.com/index.php?mod=main.doLogin', headers=headers, data=data)
        if response.ok:
            self._cookies.update(response.cookies)
        else:
            raise Exception(' network timeout !')
        return self

    @retry(tries=3, delay=5, max_delay=5)
    def _pLogin(self):
        url = 'https://www.mabangerp.com/index.php?mod=main.plogin&v=&isMallRpcFinds='
        headers = deepcopy(self._headers)
        headers.update({
            'Upgrade-Insecure-Requests': '1',
            'Proxy-Connection': 'keep-alive',
        })

        data = {
            "mod": 'main.plogin',
            "v": '',
            "is": 'isMallRpcFinds',
        }
        # request 中是可以使用hooks
        response = get(url, headers=headers, data=data, cookies=self._cookies, hooks=dict(response=self._update_cookies))

        if response.ok:
            self._cookies.update(response.cookies)
        else:
            raise Exception('network timeout error......')
        return self

    def _update_cookies(self, r, *args, **kwargs):
        '''
        重定向的时候更新cookies的钩子函数
        :param r: response的对象
        :param args:
        :param kwargs: 返回是否超时等的对象
        :return:
        '''
        self._cookies.update(r.cookies)

    def getCookies(self):
        self._login()._pLogin()

        return self._cookies