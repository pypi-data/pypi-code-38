# -*- coding: utf-8 -*-
# !/usr/bin/python
# Create Date 2019/1/29 0029
__author__ = 'huohuo'

# from django.http import JsonResponse
import requests
from alipay import AliPay
import json
import os
import time,qrcode
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
#注意：一个是支付宝公钥，一个是应用私钥


def pay(order_id, total_amount, subject):
    # order_id = request.POST.get("order_id")
    # 创建用于进行支付宝支付的工具对象
    alipay = init_alipay()

    # 电脑网站支付，api_alipay_trade_page_pay 需要跳转到https://openapi.alipay.com/gateway.do? + order_string
    # APP支付， api_alipay_trade_wap_pay
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=order_id,
        total_amount=str(total_amount),  # 将Decimal类型转换为字符串交给支付宝
        subject=subject,
        return_url='https://www.gene.ac/event/success/',
        notify_url=None  # 可选, 不填则使用默认notify url
    )
    # 让用户进行支付的支付宝页面网址
    url = ALIPAY_URL + "?" + order_string
    print url
    return {"code": 0, "message": "请求支付成功", "url": url}


def check_pay(out_trade_no):
    # 创建用于进行支付宝支付的工具对象
    alipay = init_alipay()
    biz_content = {}
    if out_trade_no:
        biz_content["out_trade_no"] = out_trade_no
    data = alipay.build_body("alipay.trade.query", biz_content)
    url = alipay._gateway + "?" + alipay.sign_data(data)
    raw_string = requests.request('GET', url, timeout=15, headers={'Content-Type': 'application/json'})
    res = raw_string.json()
    return res.get('alipay_trade_query_response')


def init_alipay():
    # 创建用于进行支付宝支付的工具对象
    alipay = AliPay(
        appid=ALIPAY_APPID,
        app_notify_url=None,  # 默认回调url
        app_private_key_string=app_private_key_string,
        alipay_public_key_string=alipay_public_key_string,
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        sign_type="RSA2",  # RSA2,官方推荐，配置公钥的时候能看到
        debug=False  # 默认False  配合沙箱模式使用
    )
    return alipay


def get_qr_code(code_url):
    '''
    生成二维码
    :return None
    '''
    #print(code_url)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=1
    )
    qr.add_data(code_url)  # 二维码所含信息
    img = qr.make_image()  # 生成二维码图片
    img.save(r'qr_test_ali.png')
    print('二维码保存成功！')


def preCreateOrder(subject, out_trade_no, total_amount):
    '''
    创建预付订单
    :param subject: order_desc
    :param out_trade_no:int
    :param total_amount:(float,'eg:0.01')
    :return None：表示预付订单创建失败  [或]  code_url：二维码url
    '''
    alipay = init_alipay()

    print 'subject', subject
    print 'out_trade_no', out_trade_no
    print 'total_amount', total_amount
    result = alipay.api_alipay_trade_precreate(subject=subject, out_trade_no=out_trade_no, total_amount=total_amount)
    print('返回值：', result)
    code_url = result.get('qr_code')
    if not code_url:
        print(result.get('预付订单创建失败：','msg'))
        return
    else:
        get_qr_code(code_url)
        #return code_url


def query_order(out_trade_no, cancel_time):
    '''
    :param out_trade_no: 商户订单号 int
    :param cancel_time:int and 'secs'
    :return: None
    '''
    print('预付订单已创建,请在%s秒内扫码支付,过期订单将被取消！'% cancel_time)
    # check order status
    _time = 0
    for i in range(10):
        # check every 3s, and 10 times in all

        print("now sleep 2s")
        time.sleep(2)

        result = init_alipay().api_alipay_trade_query(out_trade_no=out_trade_no)
        if result.get("trade_status", "") == "TRADE_SUCCESS":
            print('订单已支付!')
            print('订单查询返回值：',result)
            break

        _time += 2
        if _time >= cancel_time:
            cancel_order(out_trade_no,cancel_time)
            return


def cancel_order(out_trade_no, cancel_time=None):
    '''
    撤销订单
    :param out_trade_no: int
    :param cancel_time: 撤销前的等待时间(若未支付)，撤销后在商家中心-交易下的交易状态显示为"关闭"
    :return:
    '''
    alipay = init_alipay()
    print out_trade_no
    result = alipay.api_alipay_trade_cancel(out_trade_no=out_trade_no)
    #print('取消订单返回值：', result)
    resp_state = result.get('msg')
    action = result.get('action')
    if resp_state=='Success':
        if action=='close':
            if cancel_time:
                print("%s秒内未支付订单，订单已被取消！" % cancel_time)
        elif action=='refund':
            print('该笔交易目前状态为：',action)

        return action

    else:
        print('请求失败：',resp_state)
        return


def need_refund(out_trade_no, refund_amount, out_request_no):
    '''
    退款操作
    :param out_trade_no: 商户订单号 str or int
    :param refund_amount: 退款金额，小于等于订单金额 int or float
    :param out_request_no: 商户自定义参数，用来标识该次退款请求的唯一性,可使用 out_trade_no_退款金额*100 的构造方式 str
    :return:
    '''
    result = init_alipay().api_alipay_trade_refund(out_trade_no=out_trade_no,
                                                   refund_amount=refund_amount,
                                                   out_request_no=out_request_no)

    if result["code"] == "10000":
        return result  #接口调用成功则返回result
    else:
        return result["msg"] #接口调用失败则返回原因


def refund_query(out_request_no, out_trade_no):
    '''
    退款查询：同一笔交易可能有多次退款操作（每次退一部分）
    :param out_request_no: 商户自定义的单次退款请求标识符 str
    :param out_trade_no: 商户订单号 str or int
    :return:
    '''
    result = init_alipay().api_alipay_trade_fastpay_refund_query(out_request_no, out_trade_no=out_trade_no)

    if result["code"] == "10000":
        return result  #接口调用成功则返回result
    else:
        return result["msg"] #接口调用失败则返回原因


def create_order(out_trade_no, total_amount, subject):
    alipay = init_alipay()
    order_string = alipay.api_alipay_trade_app_pay(
        out_trade_no=out_trade_no,
        total_amount=total_amount,
        subject=subject,
        notify_url="https://example.com/notify" # 可选, 不填则使用默认notify url
    )
    print order_string


if __name__ == '__main__':
    # cancel_order(1527212120)
    subject = "Early-bird (by Mar. 10, 2019)"
    out_trade_no = int(time.time())
    total_amount = 0.01
    # from jy_word.web_tool import format_time
    # timestamp = format_time(out_trade_no)
    # print out_trade_no
    # result = pay(out_trade_no, total_amount, subject)
    # print result['message']
    out_trade_no = 1550651456
    out_trade_no = '20190221085620055000'
    print 'ALIPAY_APPID', ALIPAY_APPID
    result2 = check_pay(out_trade_no)
    # print result2

    # # pay_test(out_trade_no, timestamp)
    # preCreateOrder(subject, out_trade_no,total_amount)
    # #
    # query_order(out_trade_no,40)
    # #
    # # print('5s后订单自动退款')
    # # time.sleep(5)
    # print(need_refund(out_trade_no,0.01,111))
    # #
    # # print('5s后查询退款')
    # # time.sleep(5)
    # print(refund_query(out_request_no=111, out_trade_no=out_trade_no))
    # # 操作完登录 https://authsu18.alipay.com/login/index.htm中的对账中心查看是否有一笔交易生成并退款
    # create_order(out_trade_no, total_amount, subject)
    

