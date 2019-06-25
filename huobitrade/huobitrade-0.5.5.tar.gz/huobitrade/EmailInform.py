#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/12 0012 10:35
# @Author  : Hadrianl 
# @File    : EmailInform.py
# @Contact   : 137150224@qq.com

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
import datetime as dt
import sys

def setEmailConf(host, port, username, password, sender):
    global HOST, PORT, USERNAME, PASSWORD, SENDER, RECEIVER
    HOST, PORT, USERNAME, PASSWORD, SENDER= host, port, username, password, sender




def send_connect_failed(receiver):
    me = "AWS" + "<" + SENDER + ">"
    msg = MIMEMultipart()
    msg['Subject'] = 'HUOBILOG'
    msg['From'] = me
    msg['To'] = receiver

    txt = MIMEText(f'{dt.datetime.now()}-{os.path.split(sys.argv[0][1])}连接中断', _subtype='plain', _charset='utf-8')
    msg.attach(txt)

    # try:
    #     att = MIMEApplication(open('huobi.log', 'rb').read())
    #     att.add_header('Content-Disposition', 'attachment', filename='huobi.log')
    #     msg.attach(att)
    # except Exception as e:
    #     print(e)

    smtp = smtplib.SMTP()
    smtp.connect(HOST, PORT)
    smtp.login(USERNAME, PASSWORD)
    smtp.sendmail(me, receiver, msg.as_string())
    smtp.quit()


