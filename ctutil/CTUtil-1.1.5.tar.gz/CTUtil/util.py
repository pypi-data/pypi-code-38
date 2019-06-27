import json
import uuid
import os
import logging
import re
import base64
from typing import Dict, Type, Callable, Union, Any, List, Iterable, Tuple
from datetime import datetime, date, time
from urllib.parse import quote
import requests
from traceback import print_exc

from Crypto.Cipher import AES
from CTUtil.types import DateSec
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf.urls import RegexURLPattern
from django.http import HttpRequest
import random

try:
    from aliyunsdkcore.client import AcsClient
    from aliyunsdkcore.profile import region_provider
    from aliyunsdkdysmsapi.request.v20170525 import SendSmsRequest
except:
    print_exc()


logger = logging.getLogger()
logger.setLevel(logging.ERROR)
logger_formatter = logging.Formatter(
    "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")


def get_client_ip(request: HttpRequest):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_date_range(date: date) -> Tuple[datetime, datetime]:
    return datetime.combine(date, time.min), datetime.combine(date, time.max)


def queryset_paging(queryset: Iterable[Any], page: int, page_size: int):
    return queryset[(page - 1) * page_size: page * page_size]


def jstimestamp_to_datetime(jstimestamp: int):
    return datetime.fromtimestamp(jstimestamp // 1000)


def get_django_all_url(urlpatterns: List[Any]):
    urls = []

    def search_url(src_urls: List[Any], root: str, pre_urls: List[str]):
        for url in src_urls:
            _root = os.path.join(root, url._regex).replace('^', '')
            if isinstance(url, RegexURLPattern):
                pre_urls.append(_root)
            else:
                search_url(url.url_patterns, _root, pre_urls)

    search_url(urlpatterns, '/', urls)
    return urls


def set_default_file_path(files_dir: str='image',
                          file_type: str='jpeg') -> str:
    _date: Type[date] = datetime.now().date()
    dir_path = os.path.join('static', files_dir, format(_date, '%Y%m%d'))
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    filename = '{file_name}.{file_type}'.format(
        file_name=str(uuid.uuid4()).replace('-', ''), file_type=file_type)
    path = os.path.join(dir_path, filename)
    return path


def process_base64_in_content(post: dict) -> None:
    content: str = post.setdefault('content', '')
    if not content:
        return
    search_base64 = re.search('\"data\:image\/(.*?)\;base64\,(.*?)\"', content)
    if not search_base64:
        return
    image_type = search_base64.group(1)
    image_base64_string = search_base64.group(2)
    image_decode = base64.b64decode(image_base64_string)
    file_path = set_default_file_path(file_type=image_type)
    with open(file_path, 'wb') as f:
        f.write(image_decode)
    content = content.replace(
        search_base64.group(), '\"{path}\"'.format(path=file_path))
    post['content'] = content


def make_code(count: int=4) -> str:
    data = [str(random.randint(0, 9)) for i in range(count)]
    return ''.join(data)


def process_file_return_path(request,
                             files_name: str='file',
                             files_dir: str='image'):
    myFile = request.FILES.get(files_name)
    if not myFile:
        return
    if myFile:
        file_type = (myFile.name).split(".")[-1]
        file_path = set_default_file_path(file_type=file_type)
        with open(file_path, 'wb+') as f:
            for chunk in myFile.chunks():
                f.write(chunk)
        return file_path.replace('\\', '/')


def process_files_return_pathlist(request, files_dir: str='image'):
    myFiles = request.FILES
    data_list = []
    if myFiles:
        for myFile in myFiles.itervalues():
            file_type = (myFile.name).split(".")[-1]
            file_path = set_default_file_path(file_type=file_type)
            with open(file_path, 'wb+') as f:
                for chunk in myFile.chunks():
                    f.write(chunk)
            data_list.append(file_path.replace('\\', '/'))
    return data_list


class TokenSerializer(object):

    def __init__(self, salt: str, overtime_sec: Type[DateSec]=DateSec.DAY):
        self.s = Serializer(salt, expires_in=overtime_sec)

    def encode(self, data: Dict[str, Any]) -> bytes:
        return self.s.dumps(data)

    def decode(self, data: bytes) -> Dict[str, Any]:
        return self.s.loads(data)


class SMS(object):
    # 阿里云大于短信客户端接口
    """
        阿里大于接口返回
        docstring here
            return data: {
                'RequestId': '请求id',
                'Code': '状态码',
                'Message': '状态码描述',
                'BizId': '回执id',
            }
    """

    REGION = "cn-hangzhou"
    PRODUCT_NAME = "Dysmsapi"
    DOMAIN = "dysmsapi.aliyuncs.com"

    def __init__(self, ACCESS_KEY_ID, ACCESS_KEY_SECRET, sign_name,
                 template_code):
        self.acs_client = AcsClient(ACCESS_KEY_ID, ACCESS_KEY_SECRET,
                                    self.REGION)
        region_provider.add_endpoint(self.PRODUCT_NAME, self.REGION,
                                     self.DOMAIN)

        self.sign_name = sign_name
        self.template_code = template_code

    # 发送信息
    def send_sms(self, phone: str, code: int, context: Union[None, Dict[str, Any]]=None):
        business_id = uuid.uuid1()
        smsRequest = SendSmsRequest.SendSmsRequest()
        smsRequest.set_TemplateCode(self.template_code)
        if context:
            smsRequest.set_TemplateParam(json.dumps(context))
        smsRequest.set_OutId(business_id)
        smsRequest.set_SignName(self.sign_name)
        smsRequest.set_PhoneNumbers(phone)

        smsResponse: bytes = self.acs_client.do_action_with_exception(smsRequest)
        return json.loads(smsResponse)

    def __unicode__(self):
        return self.PRODUCT_NAME


class WxLogin(object):
    # 网页端微信第三方登录接口
    def __init__(self, APPID, APPSECRET):
        self.appid = APPID
        self.secret = APPSECRET
        self.redirect_url = quote('https://www.cingta.com/')

    # 生成二维码url
    def create_code_url(self):
        return 'https://open.weixin.qq.com/connect/qrconnect?appid={APPID}&redirect_uri={redirrect_uri}&response_type=code&scope={scope}&state=STATE#wechat_redirect'.format(
            APPID=self.appid,
            redirrect_uri=self.redirect_url,
            scope='snsapi_login', )

    # 获取open_id
    def get_access_token(self, code):
        url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid={APPID}&secret={APPSECRET}&code={CODE}&grant_type=authorization_code'.format(
            APPID=self.appid,
            APPSECRET=self.secret,
            CODE=code, )
        resp = requests.get(url).json()
        return resp

    # 获取unionid
    @staticmethod
    def get_unionid(token, openid):
        url = 'https://api.weixin.qq.com/sns/userinfo?access_token={token}&openid={openid}'.format(
            token=token,
            openid=openid, )
        resp = requests.get(url).json()
        return resp.get('unionid')


class WXBizDataCrypt:
    # 微信小程序解码, 腾讯官方代码, 直接调用
    def __init__(self, appId, sessionKey):
        self.appId = appId
        self.sessionKey = sessionKey

    def decrypt(self, encryptedData, iv):
        sessionKey = base64.b64decode(self.sessionKey)
        encryptedData = base64.b64decode(encryptedData)
        iv = base64.b64decode(iv)

        cipher = AES.new(sessionKey, AES.MODE_CBC, iv)
        data = self._unpad(cipher.decrypt(encryptedData))
        decrypted = json.loads(data)

        if decrypted['watermark']['appid'] != self.appId:
            raise Exception('Invalid Buffer')

        return decrypted

    def _unpad(self, s):
        return s[:-ord(s[len(s) - 1:])]


class WxMiniInterface(object):
    # 微信小程序各种接口
    def __init__(self, APPID: str, APPSECRET: str):
        self.APPID = APPID
        self.APPSECRET = APPSECRET

    def get_user_session(self, code: str) -> Dict[str, str]:
        url = 'https://api.weixin.qq.com/sns/jscode2session?appid={AppID}&secret={AppSecret}&js_code={code}&grant_type=authorization_code'.format(
            AppID=self.APPID,
            AppSecret=self.APPSECRET,
            code=code, )
        resp = requests.get(url).json()
        return resp

    def get_user_info(self, session: str, encryptedata: str, iv: str) -> str:
        wx_mini = WXBizDataCrypt(self.APPID, session)
        userinfo = wx_mini.decrypt(encryptedata, iv)
        return userinfo

    def send_template_msg(self, **templatedata) -> Dict[str, str]:
        get_user_info = set(
            ['touser', 'template_id', 'page', 'form_id', 'data'])
        if not (get_user_info & set(templatedata.keys()) == get_user_info):
            raise TypeError(
                'send_template_msg missing required positional arguments: touser, template_id, page, form_id or data'
            )

        token_url: str = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}'.format(
            APPID=self.APPID,
            APPSECRET=self.APPSECRET, )
        token: Dict[str, str] = requests.get(token_url).json()
        if token.get('errcode'):
            raise TypeError('error APPID or error APPSECRET')
        _token = token.get('access_token', '')
        template_url: str = 'https://api.weixin.qq.com/cgi-bin/message/wxopen/template/send?access_token={ACCESS_TOKEN}'.format(
            ACCESS_TOKEN=_token, )
        resp = requests.post(
            template_url, data=json.dumps(templatedata)).json()
        return resp
