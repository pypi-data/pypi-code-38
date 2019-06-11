import hashlib
import requests
import demjson
# print("hello,world")


class youdaup:

    APPID = ''
    APPSECRECT = ''
    tourl = 'http://upload.youda.com.cn/getoken'
    filetourl = "http://upload.youda.com.cn/upload_file"

    def __init__(self, appid, appsecrect):
        self.APPID = appid
        self.APPSECRECT = appsecrect

    '''
    @recordId 
    @mediaIndex 
    @isRepeat 
    @saveKey    必传
    @scope      必传
    @returnUrl  必传
    @appid      必传
    '''

    def getoken(self, saveKey, scope, returnUrl, **kawrgs):
        strc = saveKey + scope + returnUrl + self.APPID + self.APPSECRECT

        m = hashlib.md5()
        b = strc.encode(encoding='utf-8')
        m.update(b)
        str_md5 = m.hexdigest()

        r = kawrgs

        r.update({
            "saveKey": saveKey,
            "scope": scope,
            "returnUrl": returnUrl,
            "sign": str_md5,
            "appid": self.APPID
        })

        p = requests.post(self.tourl, data=r)
        cc = demjson.decode(p.text)
        if cc['code'] == 200:
            return cc['token']
        else:
            return False

    def upload(self, token, filepath):
        files = {'file': open(filepath, 'rb')}
        token = {
            "token": token
        }
        r = requests.post(self.filetourl, files=files, data=token)
        return r.text
