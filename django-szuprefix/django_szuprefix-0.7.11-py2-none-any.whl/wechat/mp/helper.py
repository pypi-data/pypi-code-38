#!/usr/bin/env python   
# -*- coding:utf-8 -*-   
# Author:DenisHuang   
from ..models import OrderPrepayId, User
from ..apps import MP as settings
from ..helper import BaseApi
from . import signals
import urllib, json, hashlib, time
from django.shortcuts import resolve_url
from django_szuprefix.utils import datautils
import logging

log = logging.getLogger('wechat')

from django.utils.crypto import get_random_string

OAUTH_SCOPE = settings.get("OAUTH_SCOPE")
APPID = settings.get("APPID")
APPSECRET = settings.get("APPSECRET")
MENU = settings.get("MENU")
TOKEN = settings.get("TOKEN")
PAY_KEY = settings.get("PAY_KEY")
PAID_NOTIFY_URL = settings.get("PAID_NOTIFY_URL")
MCH_ID = settings.get("MCH_ID")


class MpApi(BaseApi):
    cgi_url = "https://api.weixin.qq.com/cgi-bin/"

    def __init__(self, **kwargs):
        super(MpApi, self).__init__(**kwargs)
        self.appid = APPID

    def get_access_token_url(self):
        return "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" % (
            APPID, APPSECRET)

    def get_jsapi_ticket_url(self):
        return "https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=%s&type=jsapi" % self.token

    def get_qrcode_ticket(self, scene=0, limit=False, expire_seconds=60):
        scene_type = isinstance(scene, int) and "id" or "str"
        action = "QR_%s%sSCENE" % (limit and "LIMIT_" or "", scene_type == "str" and "STR_" or "")
        d = {"expire_seconds": expire_seconds,
             "action_name": action,
             "action_info": {"scene": {"scene_%s" % scene_type: scene}}
             }
        return self.cgi_call("qrcode/create", d)

    def get_message_template_id(self, template_id_short):
        d = {
            "template_id_short": template_id_short
        }
        data = self.cgi_call("template/api_add_template", d)
        return data.get("template_id")

    def send_template_message(self, openid, templateid, context):
        d = {"touser": openid,
             "template_id": templateid,
             "url": "http://weixin.qq.com/download",
             "data": context
             }
        data = self.cgi_call("message/template/send", d)
        return data.get('msgid')

    def login(self, code=None):
        url = "https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code" % (
            APPID, APPSECRET, code)
        data = json.loads(urllib.urlopen(url).read())
        if not "access_token" in data:
            raise ValueError("wechat oauth2 error:%s" % data)
        url = "https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s&lang=zh_CN" % (
            data['access_token'], data['openid'])
        data2 = json.loads(urllib.urlopen(url).read())
        data.update(data2)
        return data

    def get_or_create_user(self, data):
        openId = data.get("openid")
        for s in ['access_token', 'expires_in', 'privilege', 'refresh_token', 'scope']:
            data.pop(s, None)
        user, created = User.objects.update_or_create(
            openid=openId,
            defaults=data)
        return user

    def check_tencent_signature(self, request):
        signature = request.GET["signature"]
        timestamp = request.GET["timestamp"]
        nonce = request.GET["nonce"]
        tok = TOKEN
        s = [tok, timestamp, nonce]
        s.sort()
        sha1 = hashlib.sha1()
        sha1.update("".join(s))
        sign = sha1.hexdigest()
        if sign != signature:
            log.info("signature invalid: %s  %s" % (sign, signature))
        return sign == signature

    def create_menu(self, data=None):
        return self.cgi_call("menu/create", data or MENU)

    def get_menu(self):
        return self.cgi_call("menu/get")

    def get_user_info(self, openId):
        return self.cgi_call("user/info", extraParams=("&openid=%s&lang=zh_CN" % openId))

    def get_current_selfmenu(self):
        return self.cgi_call("get_current_selfmenu_info")

    def get_materialcount(self):
        return self.cgi_call("material/get_materialcount")

    def get_material_list(self, data):
        return self.cgi_call("material/batchget_material", data)

    def download_media(self, mediaId):
        return self.cgi_call("media/get", extraParams="&media_id=%s" % mediaId, retrieve=True)

    def send_message(self, openId, content):
        d = {
            "touser": openId,
            "msgtype": "text",
            "text":
                {
                    "content": content
                }
        }

        return self.cgi_call("message/custom/send", d)

    def merchant_call(self, func, data):
        url = "https://api.weixin.qq.com/merchant/%s?access_token=%s" % (func, self.token)
        response = json.loads(urllib.urlopen(url, json.dumps(data, ensure_ascii=False)).read())
        return response

    def _cache_prepayid(self, order_number, prepay_id):
        if prepay_id and order_number:
            OrderPrepayId.objects.create(order_number=order_number, prepay_id=prepay_id)

    def get_order_prepayid(self, order_number):
        p = OrderPrepayId.objects.filter(order_number=order_number).first()
        return p and p.prepay_id

    def order(self, openId, orderId, orderTitle, totalFee, ip, detail="", notifyUrl=PAID_NOTIFY_URL):
        d = {"appid": APPID,
             "mch_id": MCH_ID,
             "device_info": "WEB",
             "nonce_str": get_random_string(32),
             "fee_type": "CNY",
             "notify_url": resolve_url(notifyUrl),
             "trade_type": "JSAPI",
             "body": orderTitle,
             "detail": detail,
             "openid": openId,
             "total_fee": int(totalFee * 100),
             "spbill_create_ip": ip,
             "out_trade_no": orderId
             }

        s = datautils.dict2xml(d)
        s = u"<xml>%s<sign>%s</sign></xml>" % (s, self.get_signature(d, key=self.PAY_KEY))
        url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
        response = urllib.urlopen(url, s.encode("utf8")).read()
        data = datautils.xml2dict(response)
        if data.get("return_code") != "SUCCESS":
            raise ValueError("wechat order failed:%s" % data)
        self._cache_prepayid(orderId, data.get("prepay_id"))
        return data

    def get_jspay_params(self, order_number):
        d = {"appId": APPID,
             "nonceStr": get_random_string(32),
             "timeStamp": int(time.time()),
             "package": "prepay_id=%s" % self.get_order_prepayid(order_number),
             "signType": "MD5"}
        sign = self.get_signature(d, hash=hashlib.md5, key=self.PAY_KEY)
        d["paySign"] = sign
        return d

    def filter_order(self, status=None, begintime=None, endtime=None):
        import time
        data = {}
        if status:
            data["status"] = status
        if begintime:
            data["begintime"] = time.mktime(begintime.timetuple())
        if begintime:
            data["endtime"] = time.mktime(endtime.timetuple())
        result = self.merchant_call("order/getbyfilter", data)
        return result

    def pay_result_notify(self, xml):
        data = datautils.xml2dict(xml)
        sign = data.pop('sign')
        sign2 = self.get_signature(data, hash=hashlib.md5, key=self.PAY_KEY)
        log.info(xml)
        log.info(sign)
        log.info(sign2)
        ps = signals.weixin_pay_result_notice.send_robust(sender=None, result=data)
        log.debug(str(ps))
        d = {"return_code": "SUCCESS", "return_msg": "OK"}
        if sign != sign2:
            d = {"return_code": "FAIL", "return_msg": "Sign Invalid"}
        return "<xml>%s</xml>" % datautils.dict2xml(d)


api = MpApi()
