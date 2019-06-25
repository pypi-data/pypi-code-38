import requests
import json
import operator
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from ..config import config

def _send_email(sender, receivers, subject, content, smtp_info):
    if not smtp_info:
        return
    if not sender:
        sender = config.EMAIL_SENDER
    msg = MIMEText(content)
    msg['Subject'] = subject
    msg['From'] = sender

    host = smtp_info['host']
    port = smtp_info['port']
    user = smtp_info['user']
    password = smtp_info['password']

    s = smtplib.SMTP_SSL(host=host, port=port)
    try:
        s.connect(host, port)
    except Exception as e:
        print('failed to connect to smtp host: %s, port: %d, error: %s' % (host, port, e))
        return
    try:
        s.login(user, password)
    except Exception as e:
        print(
            'failed to login to smtp host: %s, port: %d, user: %s, password: %s, error: %s' %
            (host, port, user, password, e))
        return
    try:
        s.sendmail(sender, receivers, msg.as_string())
    except Exception as e:
        print('failed to send to smtp host: %s, port: %d, user: %s, password: %s, msg: %s, error: %s' %
              (host, port, user, password, msg.as_string(), e))

    try:
        s.quit()
    except Exception as e:
        print('did send to smtp host: %s, port: %d, user: %s, password: %s, msg: %s, but failed to quit, error: %s' %
              (host, port, user, password, msg.as_string(), e))

def send_notify_mail(data, params):
    smtp_conf = params.get('smtp_conf', None)
    sender = params.get('email_sender', None)

    message = ''
    subject = 'App Store商品更新'
    for it in data:
        result = it.get('result', {})
        updated = result.get('updated', [])
        added = result.get('added', [])
        if len(updated) <= 0 and len(added) <= 0:
            continue
        meta = it.get('meta', {})
        message = '%sname: %s\n' % (message, meta.get('name', ''))
        message = '%sapi: %s\n' % (message, meta['api'])
        message = '%senvironment: %s\n' % (message, meta['env'])
        message = '%supdated: %d, added: %d\n' % (message, len(updated), len(added))
        resp = result.get('response', None)
        if not resp:
            message = message
        elif 200 <= resp.status_code < 400:
            message = '%sresponse data: %s\n' % (message, resp.json())
        else:
            message = '%shttp response: %s\n' % (message, resp)

    emails = params.get('subscribers', [])
    mode = params['mode']
    if len(emails) and message != '':
        if mode == 'upload':
            message = '%s\n\n\n商品数据已上传到App Store。对于AppStore之前已有的商品，不需要额外操作，对于AppStore之前没有的新增商品，还需要到https://itunesconnect.apple.com手工提交审核。（注：不要提交名字中包含dev.或sim.开头的测试商品，否则审核可能无法通过。）！\n' % message
        else:
            message = '%s\n\n\n收到后台商品更新或新增商品通知，请手工执行iapsync工具以同步更新到AppStore！\n' % message
        message = '%s\n\ntimestamp: %s\n\n\n' % (message, datetime.today().isoformat())
        _send_email(sender, emails, subject, message, smtp_conf)
