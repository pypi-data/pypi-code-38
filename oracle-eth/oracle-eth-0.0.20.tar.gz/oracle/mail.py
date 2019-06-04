#! /usr/bin/env python
# -*- coding: utf8 -*-
"""
Author:       yuyongpeng@hotmail.com
Github:       https://github.com/yuyongpeng/
Date:         2019-04-11 14:32:39
LastEditors:  
LastEditTime: 2019-04-11 14:32:39
Description:  
"""
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from oracle.logger import logger

def send_email(mail_subject, mail_host, mail_sender, mail_pass, mail_receiver=[], mail_body='', mail_port=465):
    """
    发送邮件的类库
    :param mail_subject:    邮件主题
    :param mail_host:       邮箱ip或域名
    :param mail_sender:     邮件发送者的邮箱
    :param mail_pass:       邮箱的密码
    :param mail_receiver:   邮件接收者的邮箱
    :param mail_body:       邮件的内容
    :param mail_port:       邮箱的端口
    :return:
    """
    ret = True
    try:
        for mail in mail_receiver:
            msg = MIMEText(mail_body, 'plain', 'utf-8')
            msg['From'] = formataddr(["sender", mail_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
            msg['To'] = formataddr(["receiver", mail])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
            msg['Subject'] = mail_subject  # 邮件的主题，也可以说是标题

            server = smtplib.SMTP_SSL(mail_host, mail_port)  # 发件人邮箱中的SMTP服务器，端口是25
            server.login(mail_sender, mail_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
            server.sendmail(mail_sender, mail, msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
            server.quit()  # 关闭连接
    except Exception as e:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        logger.error(e)
        ret = False
    return ret

