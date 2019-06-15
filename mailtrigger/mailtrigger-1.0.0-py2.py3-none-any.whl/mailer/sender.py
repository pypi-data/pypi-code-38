# -*- coding: utf-8 -*-

import json
import smtplib

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
        def _load(name):
            with open(name, 'r') as f:
                data = json.load(f)
            return data.get('debug', False), data.get('smtp', None)
        self._debug, self._smtp = _load(config)
        if self._smtp is None:
            raise SenderException('missing smtp configuration in %s' % config)
        self._server = None

    def _connect(self):
        if self._smtp['ssl'] is True:
            self._server = smtplib.SMTP_SSL(self._smtp['host'], self._smtp['port'])
        else:
            self._server = smtplib.SMTP(self._smtp['host'], self._smtp['port'])
        if self._debug is True:
            self._server.set_debuglevel(1)
        else:
            self._server.set_debuglevel(0)
        self._server.login(self._smtp['user'], self._smtp['pass'])

    def connect(self):
        try:
            self._connect()
        except smtplib.SMTPException as _:
            raise SenderException('failed to connect smtp server')
        Logger.debug('connected to %s' % self._smtp['host'])

    def disconnect(self):
        if self._server is None:
            return
        try:
            self._server.quit()
        except smtplib.SMTPException as _:
            Logger.debug('failed to disconnect smtp server')
            return
        Logger.debug('disconnected from %s' % self._smtp['host'])

    def send(self, data):
        if self._server is None:
            raise SenderException('required to connect smtp server')
        msg = MIMEText(data['content'], 'plain', 'utf-8')
        msg['Subject'] = data['subject']
        msg['From'] = data['from']
        msg['To'] = data['to']
        self._server.sendmail(data['from'], data['to'], msg.as_string())
