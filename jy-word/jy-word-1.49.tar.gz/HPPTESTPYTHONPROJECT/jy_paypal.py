# -*- coding: utf-8 -*-
# !/usr/bin/python
# Create Date 2019/1/29 0029
__author__ = 'huohuo'
import requests
import paypalrestsdk

client_id = 'client_id'
secret = 'secret'
grant_type = 'client_credentials'
api_hosts = 'http://fa-online.tsinghua.edu.cn/sftp/requestPayAction!payment.action'
rq_pay = {
    "intent": "sale",
    "payer": {"payment_method": "paypal"},
    "redirect_urls": {
        "return_url": "http://172.16.110.197:3303/event/success/",
        "cancel_url": "http://172.16.110.197:3303/event/#event_payment"},
    "transactions": [{
        "item_list": {
            "items": [{
                "name": "item",
                "sku": "item",
                "price": "1.50",
                "currency": "USD",
                "quantity": 1}]},
        "amount": {
            "total": "1.5",
            "currency": "USD"},
        "description": "This is the payment transaction description."}]
}


def get_access_token():
    rq = {'grant_type': grant_type}
    url = '%s/v1/oauth2/token' % api_hosts
    headers = {'Accept': 'application/json'}
    r = requests.request('post', url, headers=headers, auth=(client_id, secret), params=rq)
    if r.status_code == 200:
        res = r.json()
        return res
    else:
        print r.status_code
    return None


def pay():
    res1 = get_access_token()
    for k in res1:
        print k, res1[k]
    access_token = res1.get('access_token')
    url = '%s/v1/payments/payment' % api_hosts
    authorization = 'bearer %s' % access_token
    print authorization
    headers = {'Authorization': authorization}
    r = requests.request('post', url, headers=headers, json=rq_pay, auth=(client_id, secret))
    if r.status_code == 200:
        res = r.json()
        print res
        return res.get('access_token')
    else:
        print r.status_code, r.text


def pay_sdk():
    paypalrestsdk.configure({
        "mode": "sandbox", # sandbox or live
        "client_id": client_id, "client_secret": secret})
    payment = paypalrestsdk.Payment(rq_pay)
    # paypalrestsdk.Order()
    if payment.create():
        print 'create', payment
    else:
        print(payment.error)

def get_order_tsinghua():
    import datetime
    out_trade_no = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
    total_fee = 0.01
    pay_type = '2'  # 1手机端支付，2 PC端支付
    alipay = 100862
    wxpay = 100863
    rq = {
        't_partner': '2025',
        't_out_trade_no': 'tcdf%s%s1234' % (alipay, out_trade_no[:-3]),
        't_business': 'tcdf2019_wk',
        't_user_id': '410881199102215029',
        't_user_id_type': '0',
        't_username': '霍佩佩',
        't_name': '测试',
        't_summary': 'ceshi',
        't_total_fee': '%0.2f' % total_fee,
        't_return_url': 'https://www.gene.ac/event/success/',
        't_pay_type': pay_type,
        't_datetime': out_trade_no[:-3]
    }



# pay()
if __name__ == "__main__":
    # pay_sdk()
    get_order_tsinghua()
    pass
    

