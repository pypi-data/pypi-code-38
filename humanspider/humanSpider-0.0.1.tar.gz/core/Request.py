import hashlib


class Request(object):
    def __init__(self):
        self.method = "GET"
        self.url = None
        self.headers = None
        self.cookies = None
        self.data = None
        self.json = None
        self.proxies = None
        self.files = None
        self.auth = None
        self.timeout = None
        self.allow_redirects = True
        self.hooks = None  # 区分request对象类别的钩子
        self.stream = None
        self.verify = None
        self.cert = None
        self.retry = 0

    def hash(self):
        sha1 = hashlib.sha1()
        sha1.update(str(self).encode('utf-8'))
        return sha1.hexdigest()

    def __str__(self):
        return '{"Request": {"url": ' + str(self.url) + ', "headers": ' + str(self.headers) + ', "cookies": ' + \
               str(self.cookies) + ', "data": ' + str(self.data) + ', "json": ' + str(self.json) + ', "proxies": ' + \
               str(self.proxies) + ', "auth": ' + str(self.auth) + ', "timeout": ' + str(self.timeout) \
               + ', "verify": ' + str(self.verify) + '"}}'
