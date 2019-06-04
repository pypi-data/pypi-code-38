#!/usr/bin/env python3
import sys
from functools import partial
from typing import List, Optional

import sleekxmpp
from netwell.checkers import URL, Outcome, DNS, Port, set_output, Output
from requests import Response

from sleekxmpp import JID


class Sendmail(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password, recipients, message, subject):
        super(Sendmail, self).__init__(jid, password)
        self.recipients = recipients
        self.msg = message
        self.subject = subject
        self.add_event_handler('session_start', self.start)

    def start(self, event):
        #self.send_presence()
        for recipient in self.recipients:
            self.send_message(mto=recipient,
                              msubject=self.subject,
                              mbody=self.msg,
                              mtype='normal')

        self.disconnect(wait=True)

class XMPPOutput(Output):
    def __init__(self, jid:JID, password:str, recipients=List[str]):
        super().__init__()
        self.jid = jid
        self.jid.resource = 'server-checks'
        self.password = password
        self.recipients = recipients
        self.message = None
        self.subject = None

    def error(self, text) -> None:
        self.line_error = True
        self.info(text)

        xmpp = Sendmail(self.jid, self.password, self.recipients, text, 'OSSEC Alert')
        if xmpp.connect():
            xmpp.process(block=True)

output = XMPPOutput(jid=JID('ossecm@jabber.ccc.de'), password='enahNgahthea5quiThai', recipients=['webcookies@jabber.ccc.de'])

set_output(output)

def http(code: int, resp: Response, outcome: Outcome):
    if resp.status_code != code:
        outcome.fail(f'Got code {resp.status_code}, expected {code}')


http_200 = partial(http, 200)
http_200.__name__ = 'http_200'

As = (
    'webcookies.org',
    'webcookies.info',
    'otto.krvtz.net',
    'ssb.webcookies.pub',
    'echelon.pl',
    'ipsec.pl',
    'kabardians.com',
)

DNS(*As).resolves()

AAAAs = (
    'postgres.prod.krvtz.net',
    'redis.prod.krvtz.net',
    'apm.prod.krvtz.net',
    'postgres.dev.krvtz.net',
    'redis.dev.krvtz.net',
    'y.webcookies.pub',
)

Port('ssb.webcookies.pub', 8008).is_open()  # SSB
Port('ssb.webcookies.pub', 8989).is_open()  # SSB WS
Port('ssb.webcookies.pub', 31337).is_open()  # Yggdrasil
Port('ssb.webcookies.pub', 3282).is_open()  # dat

URL('http://y.webcookies.pub/').check_response(http_200)

WEBSERVERS = (
    'ssb.webcookies.pub',
    'webcookies.org',
    'www.webcookies.org',
    'webcookies.info',
    'www.webcookies.info',
    'ipsec.pl',
    'echelon.pl',
    'kabardians.com',
)

for fqdn in WEBSERVERS:
    http_url = f'http://{fqdn}/'
    https_url = f'https://{fqdn}/'
    URL(http_url).check_response(http_200)
    URL(https_url).check_response(http_200)
    Port(fqdn, 443).ssl_valid_for(days=7)

SSH_SERVERS = ('otto', 'tyler', 'worker', 'worker3', 'ssb', 'kibana', 'kautsky', 'prol')

for server in SSH_SERVERS:
    Port(f'{server}.krvtz.net', 22).is_open()
