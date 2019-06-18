# -*- coding: utf-8 -*-
import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from pyramid.compat import text_


class SMTPClient:
    def __init__(self, smpt, sender):
        '''
            :param smtp: Simple Mail Transfer Protocol (SMTP) to send mails
            :param sender: Sender of the mail
        '''
        self.smtp = smpt
        self.sender = sender

    @property
    def smtp_obj(self):  # pragma no cover
        return smtplib.SMTP(self.smtp)

    def send_mail(self, receivers, subject, message_plain, message_html=None, cc=None, bcc=None, files=None):
        '''

        send an email

        :param receivers: Receivers (list)
        :param subject: Email subject
        :param message_plain: Email message (plain text)
        :param message_html: Email message (html version)
        :param cc: carbon copy (list)
        :param bcc: blind carbon copy (list)
        :param files: array for attachments with {'name': filename, 'data': binary attachmentdata}
        '''
        msg = MIMEMultipart('alternative')
        msg['Subject'] = Header(subject, "utf-8")
        msg['From'] = Header(text_(self.sender), "utf-8")
        msg['To'] = Header(text_('; '.join(receivers)), "utf-8")
        if cc:
            msg['CC'] = Header(text_('; '.join(cc)), "utf-8")
        else:
            cc = []
        if bcc:
            msg['BCC'] = Header(text_('; '.join(bcc)), "utf-8")
        else:
            bcc = []
        if message_html:
            part1 = MIMEText(message_plain, 'plain', _charset="UTF-8")
            part2 = MIMEText(message_html, 'html', _charset="UTF-8")

            # Attach parts into message container.
            # According to RFC 2046, the last part of a multipart message, in this case
            # the HTML message, is best and preferred.
            msg.attach(part1)
            msg.attach(part2)
        else:
            part1 = MIMEText(message_plain, 'plain', _charset="UTF-8")
            msg.attach(part1)
        if files:
            for f in files or []:
                maintype, subtype = f['mime'].split("/", 1)
                attachment = MIMEBase(maintype, subtype)
                attachment.set_payload(f['data'])
                encoders.encode_base64(attachment)
                attachment.add_header("Content-Disposition", "attachment", filename=f['name'])
                msg.attach(attachment)
        self.smtp_obj.sendmail(self.sender, receivers + cc + bcc, msg.as_string())
