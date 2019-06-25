# -*- coding: utf-8 -*-

import smtplib
import socket

from email.mime.text import MIMEText
from ..logger.logger import Logger


class SenderException(Exception):
    def __init__(self, info):
        super().__init__(self)
        self._info = info

    def __str__(self):
        return self._info


class Sender(object):
    def __init__(self, config):
        self._debug = config['debug']
        self._smtp = config.get('smtp', None)
        if self._smtp is None:
            raise SenderException('missing smtp configuration')
        self._server = None

    def _connect(self):
        ssl = self._smtp.get('ssl', False)
        if ssl is True:
            self._server = smtplib.SMTP_SSL(host=self._smtp.get('host', ''), port=self._smtp.get('port', ''),
                                            timeout=self._smtp.get('timeout', 0))
        else:
            self._server = smtplib.SMTP(host=self._smtp.get('host', ''), port=self._smtp.get('port', ''),
                                        timeout=self._smtp.get('timeout', 0))
        if self._debug is True:
            self._server.set_debuglevel(1)
        else:
            self._server.set_debuglevel(0)
        self._server.login(self._smtp.get('user', ''), self._smtp.get('pass', ''))

    def connect(self):
        try:
            self._connect()
        except (OSError, smtplib.SMTPException, socket.timeout) as _:
            raise SenderException('failed to connect smtp server')
        Logger.debug('connected to %s' % self._smtp.get('host', ''))

    def disconnect(self):
        if self._server is None:
            return
        try:
            self._server.quit()
        except (OSError, smtplib.SMTPException) as _:
            Logger.debug('failed to disconnect smtp server')
            return
        Logger.debug('disconnected from %s' % self._smtp.get('host', ''))

    def send(self, data):
        if self._server is None:
            raise SenderException('required to connect smtp server')
        msg = MIMEText(data['content'], 'plain', 'utf-8')
        msg['Subject'] = data['subject']
        msg['From'] = data['from']
        msg['To'] = ','.join(data['to'])
        self._server.sendmail(data['from'], data['to'], msg.as_string())
