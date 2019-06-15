# -*- coding: utf-8 -*-

import json
import smtplib

from email.mime.text import MIMEText
from ..logger.logger import Logger


class SenderException(Exception):
    def __init__(self, info):
        super().__init__(self)
        self.info = info

    def __str__(self):
        return self.info


class Sender(object):
    def __init__(self, config):
        self._logger = Logger()
        self._debug, self._smtp = self._load(config)
        if self._smtp is None:
            raise SenderException('missing smtp configuration in %s' % config)

    def _connect(self):
        if self._smtp['ssl'] is True:
            self._server = smtplib.SMTP_SSL(self._smtp['host'], self._smtp['port'])
        else:
            self._server = smtplib.SMTP(self._smtp['host'], self._smtp['port'])
        self._server.set_debuglevel(0)
        self._server.login(self._smtp['user'], self._smtp['pass'])

    def _load(self, name):
        with open(name, 'r') as f:
            data = json.load(f)
        return data.get('debug', False), data.get('smtp', None)

    def connect(self):
        try:
            self._connect()
        except smtplib.SMTPException as _:
            raise SenderException('failed to connect smtp server')
        self._logger.info('connected to %s' % self._smtp['host'])

    def disconnect(self):
        self._logger.info('disconnected from %s' % self._smtp['host'])
        if self._server is not None:
            self._server.quit()

    def send(self, data):
        msg = MIMEText(data['content'], 'plain', 'utf-8')
        msg['Subject'] = data['subject']
        msg['From'] = data['from']
        msg['To'] = data['to']
        self._server.sendmail(data['from'], data['to'], msg.as_string())
