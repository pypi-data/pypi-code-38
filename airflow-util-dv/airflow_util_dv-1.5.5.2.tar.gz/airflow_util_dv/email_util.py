import time
from email.mime.text import MIMEText
import logging
import traceback
import smtplib
import socket


class send_mail():

    def __init__(self):
        logging.info('Mail service start successfully!')
        self.host = socket.gethostname()
        self.ip = socket.gethostbyname(self.host)

    def send_mail(self,  **kwargs):
        r"""
        send mail util
        :param title:
        :param messages_list:
        :param from_addr:
        :param password:
        :param smtp_server:
        :param smtp_port:
        :param is_tls:
        :param mail_address:
        :return:
        """
        messages = ''
        password = kwargs['password']
        smtp_server = kwargs['smtp_server']
        smtp_port = kwargs['smtp_port']
        is_tls = kwargs['tls']
        mail_address = kwargs['mail_address']
        from_addr = kwargs['from_addr']
        title = kwargs['title']
        messages_list = kwargs['messages']
        to_addr = [email.replace('\n', '') for email in mail_address.split(',')]
        list_ = ''
        retry_num = 0
        loop = True
        for i in messages_list:
            list_ += i + '<br>'
        messages += list_
        messages += '<br>'*10
        messages += 'This Notification is Sent by Following Machine:' + '<br>'
        messages += 'hostname: ' + self.host + '<br>'
        messages += 'ip: ' + self.ip + '<br>'
        msg = MIMEText(messages, 'html', 'utf-8')
        msg['From'] = from_addr
        msg['To'] = ','.join(to_addr)
        msg['Subject'] = title
        while loop:
            # 发邮件连续发三次，如果超过三次就报异常信息
            if retry_num > 2:
                raise Exception("邮件连接失败")
            # 连接服务器发送邮件
            try:
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.connect(smtp_server, 587)
                server.ehlo()
                if is_tls:
                    server.starttls()
                server.set_debuglevel(1)
                server.login(from_addr, password)
                server.sendmail(from_addr, to_addr, msg.as_string())
                server.quit()
                logging.info('Email send succeeded!!!')
                loop = False
                retry_num += 1
            except Exception:
                logging.error("Error %s", traceback.format_exc())
                time.sleep(10)
                loop = True
                retry_num += 1
                logging.warn("retry num "+str(retry_num))

