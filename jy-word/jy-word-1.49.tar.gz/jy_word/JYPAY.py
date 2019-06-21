# -*- coding: utf-8 -*-
# !/usr/bin/python
# Create Date 2019/2/18 0018
__author__ = 'huohuo'
import datetime
import hashlib
import requests
import random
import sys
import time
import urllib
import xml.etree.ElementTree as ET

reload(sys)
sys.setdefaultencoding('utf-8')


#处理函数，对参数按照key=value的格式，并按照参数名ASCII字典序排序
def format_rq(obj):
    return '&'.join(["{0}={1}".format(k, obj.get(k))for k in sorted(obj)])


# 对字符串进行MD5加密
def str2md5(text, text_unicode='utf-8'):
    return hashlib.md5(text.encode(text_unicode)).hexdigest()


#根据当前系统时间来生成商品订单号。时间精确到微秒
def getWxPayOrdrID():
    date = datetime.datetime.now()
    #根据当前系统时间来生成商品订单号。时间精确到微秒
    payOrdrID=date.strftime("%Y%m%d%H%M%S%f")
    return payOrdrID


# 生成随机字符串
def getNonceStr(length=30):
    data = "123456789zxcvbnmasdfghjklqwertyuiopZXCVBNMASDFGHJKLQWERTYUIOP"
    nonce_str = ''.join(random.sample(data, length))
    return nonce_str


def xml_to_dict(xml_data):
    '''
    xml to dict
    :param xml_data:
    :return:
    '''
    xml_dict = {}
    root = ET.fromstring(xml_data)
    for child in root:
        xml_dict[child.tag] = child.text
    return xml_dict


def dict_to_xml(dict_data):
    '''
    dict to xml
    :param dict_data:
    :return:
    '''
    xml = ["<xml>"]
    for k, v in dict_data.iteritems():
        xml.append("<{0}>{1}</{0}>".format(k, v))
    xml.append("</xml>")
    return "".join(xml)


class JYWXPAY:

    def __init__(self, app_id, Mch_id, Mch_key):
        self.app_id = app_id
        self.Mch_id = Mch_id
        self.Mch_key = Mch_key

    # 生成签名(微信)
    def format_sign(self, obj):
        stringSignTemp = '{0}&key={1}'.format(format_rq(obj), self.Mch_key)
        return str2md5(stringSignTemp).upper()

    def wx_request(self, action, order_info):
        url = 'https://api.mch.weixin.qq.com/pay/%s' % action
        order_info['appid'] = self.app_id
        order_info['mch_id'] = self.Mch_id
        order_info['nonce_str'] = getNonceStr()
        order_info['sign'] = self.format_sign(order_info) #获取签名
        body_data = dict_to_xml(order_info)  # 拿到封装好的xml数据
        #请求微信接口下单
        respone = requests.post(url, body_data.encode("utf-8"), headers={'Content-Type': 'application/xml'})
        #回复数据为xml,将其转为字典
        return xml_to_dict(respone.content)

    # 微信支付统一下单
    def get_wx_order(self, order_info):
        price = order_info.get('total_amount')
        order_info = {
            "body": order_info.get('subject'),#商品描述
            "notify_url": order_info.get('notify_url'), #支付成功的回调地址
            "openid": order_info.get('openid'), #用户标识
            "out_trade_no": order_info.get('out_trade_no'), #商户订单号
            "spbill_create_ip": order_info.get('cip'),  #客户端终端 request.remote_addr
            "total_fee": str(int((float(price) * 100))),   #总金额 单位为分
            "trade_type": 'JSAPI'  #交易类型 小程序取值如下：JSAPI
        }
        content = self.wx_request('unifiedorder', order_info)
        if content["return_code"] == 'SUCCESS':
            data = {
                'appId': self.app_id,
                'nonceStr': content.get("nonce_str"), # 获取随机字符串
                'package': "prepay_id="+content.get("prepay_id"), # 获取预支付交易会话标识
                'signType': 'MD5',
                'timeStamp': str(int(time.time()))
            }
            #获取paySign签名，这个需要我们根据拿到的prepay_id和nonceStr进行计算签名
            data['paySign'] = self.format_sign(data)
            # 封装返回给前端的数据
            return {'status': 4000001, 'message': 'success', 'data': data}
        return {'status': content.get('return_code'), 'message': content.get('return_msg')}

    # 根据商品订单号查询微信付款情况
    def query_order(self, out_trade_no):
        order_info = {"out_trade_no": out_trade_no}
        content = self.wx_request('orderquery', order_info)
        total_fee = content.get('total_fee')
        if total_fee is not None:
            content['total_amount'] = '%.02f' % (float(total_fee) / 100)
        pay_time = content.get('time_end')
        if pay_time is not None:
            content['pay_time'] = pay_time
        status = content.get('trade_state')
        msg = content.get('trade_state_desc')
        if msg is None:
            msg = content.get('return_msg')
        # print status, msg
        return {'status': status, 'message': msg, 'order_info': content}


class JYWX:

    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self.gateway = 'https://api.weixin.qq.com/cgi-bin/'

    def wx_request(self, method, action, params=None, json=None, headers=None):
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        res = requests.request(method, '%s%s' % (self.gateway, action), params=params, json=json, headers=headers)
        if res.status_code == 200:
            return res.json()
        return None


    def get_token(self):
        rq = {'grant_type': 'client_credential', 'appid': self.app_id, 'secret': self.app_secret}
        return self.wx_request('GET', 'token', params=rq)

    def send_msg(self):
        token = self.get_token().get('access_token')
        rq = {
            "touser": "ochiws76uvCapRK11chSqJxp5nZM",
            "msgtype": 'text',
            "text": {"content": 'hello xiaohuo'}
        }
        if token is not None:
            return self.wx_request('POST', 'message/custom/send?access_token=%s' % token, json=rq)
        return None


# ===================支付宝==================
try:
    from alipay import AliPay
except:
    print 'pip install python-alipay-sdk'


class JYALIPAY:

    def __init__(self, ALIPAY_APPID, app_private_key_string, alipay_public_key_string, debug=False):
        self.alipay = AliPay(
            appid=ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            sign_type="RSA2",  # RSA2,官方推荐，配置公钥的时候能看到
            debug=debug  # 默认False  配合沙箱模式使用
        )

    def get_order(self, order_info):
        # 创建用于进行支付宝支付的工具对象
        # 电脑网站支付，api_alipay_trade_page_pay
        # APP支付， api_alipay_trade_wap_pay
        # 电脑端需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        func = self.alipay.api_alipay_trade_page_pay
        if order_info.get('type') == 'app':
            func = self.alipay.api_alipay_trade_wap_pay
        total_amount = order_info.get('total_amount')
        order_string = func(
            out_trade_no=order_info.get('out_trade_no'),
            total_amount=str(total_amount),  # 将Decimal类型转换为字符串交给支付宝
            subject=order_info.get('subject'),
            return_url=order_info.get('return_url'),
            notify_url=None  # 可选, 不填则使用默认notify url
        )
        # 让用户进行支付的支付宝页面网址
        url = self.alipay._gateway + "?" + order_string
        return {'status': 1, 'message': 'success', 'url': url}

    def query_order(self, out_trade_no):
        # 创建用于进行支付宝支付的工具对象
        # 调用alipay工具查询支付结果
        biz_content = {'out_trade_no': out_trade_no}
        data = self.alipay.build_body("alipay.trade.query", biz_content)
        url = self.alipay._gateway + "?" + self.alipay.sign_data(data)
        while True:
            raw_string = requests.request('GET', url, timeout=15, headers={'Content-Type': 'application/json'})
            response = raw_string.json().get('alipay_trade_query_response')
            trade_status = response.get('trade_status')
            # 判断支付结果
            if trade_status == 'WAIT_BUYER_PAY':
                continue
            else:
                pay_time = response.get('send_pay_date')
                if pay_time is not None:
                    response['pay_time'] = pay_time
                return {"status": trade_status, "message": response.get("trade_status"), 'order_info': response}


# ====================清华支付===========
class JYTSINGHUAPAY:

    def __init__(self, t_partner, t_key):
        self.t_partner = t_partner
        self.t_key = t_key

    def get_url(self, action, rq, is_sign=True):
        # 合作方编号，秘钥
        # 正式请求路由
        rq['t_partner'] = self.t_partner
        if is_sign:
            rq['t_sign'] = str2md5((format_rq(rq) + self.t_key).encode('gbk'))
        return {'url': 'http://zhifu.tsinghua.edu.cn/sfpt/%s?%s' % (action, urllib.urlencode(rq)), 'order_info': rq}

    def get_order(self, t_rq):
        # out_trade_no = rq.get('out_trade_no')
        # t_item = rq.get('t_item')
        # t_business = rq.get('t_business')
        # t_out_trade_no = '%s%s%s%d' % (t_business[:4], t_item, out_trade_no, random.randrange(0, 10))
        # t_rq = {
        #     't_out_trade_no': t_out_trade_no,
        #     't_item': t_item,
        #     't_name': rq.get('subject'),
        #     't_total_fee': rq.get('total_amount'),
        #     't_return_url': '%s/event/success/' % (rq.get('origin').rstrip('/')),
        #     't_pay_type': '2',  # 1手机端支付，2 PC端支付, 目前仅支持传入2
        #     't_datetime': out_trade_no,
        #     't_username': 'user_name',
        # }
        # username = rq.get('account')
        # if username is not None:
        #     t_rq['t_username'] = username
        return self.get_url('requestPayAction!payment.action', t_rq)

    def query_order(self, t_out_trade_no):
        rq = {'t_out_trade_no': t_out_trade_no, 't_version': '1.1'}
        url_info = self.get_url('queryPayAction.action', rq, is_sign=False)
        response = requests.request('GET', url_info.get('url'))
        status = 'FAIL'
        message = 'query order'
        order_info = url_info.get('order_info')
        if response.status_code == 200:
            data = response.json()
            status = str(data.get('err'))
            if status == '0':
                status = 'SUCCESS'
            message = data.get('msg')
            order_info = data.get('detail')
            if isinstance(order_info, dict):
                order_info['t_total_amount'] = order_info.get('t_total_fee')
                order_info['t_pay_time'] = t_out_trade_no.split(order_info.get('t_item'))[1][:14]
        return {'status': status, 'message': message, 'order_info': order_info}

    def down_bill(self, rq):
        # rq = {
        #     't_item': t_item,
        #     't_bill_date': datetime.datetime.now().strftime('%Y%m%d'),
        # }
        url_info = self.get_url('requestBillAction.action', rq)
        res = requests.request('get', url_info.get('url'))
        if res.status_code == 200:
            return res.text
        return url_info


if __name__ == "__main__":
    # # print str2md5('bdcbdc19871212')
    # # print query_wxorder('20190221164954776532')
    # # print query_alipay('20190221225635096698')
    # # print query_alipay('20190223121236774713')
    # # print query_wxorder('20190223121236774713')
    out_trade_no = '20190225144618259000' #燃41 侯玉文
    # out_trade_no = '20190226044259187762' #数4 杨建科
    # # out_trade_no = '20190221164954776532'
    # # print query_alipay(out_trade_no)
    # # print query_wxorder(out_trade_no)
    # # print str2md5('HPPTESTPYTHONPROJECT:hpp.123456')
    # # get_order_tsinghua('test1')
    #
    # # query_order_tsinghua('tcdf100862201903050929598090003')
    ts = JYTSINGHUAPAY('2025', 'fb097338e13afb1f')
    print ts.down_bill({'t_item': 100862, 't_bill_date': '20190305'})
    # # print len(out_trade_no)
    # jy_wx = JYWX('wx78f7ae678bcfbfd1', 'f836cc553408bf9ff400e800deb41713')
    # print jy_wx.send_msg()
