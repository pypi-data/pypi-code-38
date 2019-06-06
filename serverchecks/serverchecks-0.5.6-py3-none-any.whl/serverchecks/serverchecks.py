#!/usr/bin/env python3
import argparse
import asyncio
import imaplib
import importlib.util
import poplib
import smtplib
import socket
import ssl
from datetime import datetime, timedelta
from email.message import EmailMessage
from timeit import default_timer as timer
from typing import List, Optional, Union, Dict
from urllib.error import URLError
from urllib.request import urlopen

import dns.resolver
import yaml
from dns.exception import DNSException
from dns.message import Message
from dns.name import Name


class Outcome:
    def __init__(self, status: bool, info: str) -> None:
        self.status: bool = status
        self.info: str = info

    def __str__(self):
        status = u"\u2713" if self.status else u"\u2717"
        return f'{status} {self.info}'


##########################
### PORT
##########################

async def port_test(host: str, port: int) -> Outcome:
    timeout: float = 3.0
    try:
        with socket.create_connection((host, port), timeout) as sock:
            return Outcome(True, f'Connection to {host}:{port} successful')
    except OSError as e:
        return Outcome(False, f'Connection to {host}:{port} failed: {e}')


##########################
### TLS
##########################

def _date(d: str) -> Optional[datetime]:
    try:
        # try decoding locale representation first
        return datetime.strptime(d, '%c')
    except ValueError:
        try:
            # try 'Jan 30 23:00:15 2019 GMT' representation
            return datetime.strptime(d, '%b %d %H:%M:%S %Y %Z')
        except ValueError:
            return None


async def tls_test(host: str, port: int = 443, days: int = 3) -> Outcome:
    context: ssl.SSLContext = ssl.create_default_context()
    timeout: float = 3.0

    try:
        with socket.create_connection((host, port), timeout) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssl_sock:
                cert = ssl_sock.getpeercert()
    except ssl.SSLError as e:
        return Outcome(False, f'TLS error for {host}: {e}')
    else:
        not_before: datetime = _date(cert.get('notBefore'))
        not_after: datetime = _date(cert.get('notAfter'))

        now: datetime = datetime.now()

        if not not_before or not not_after:
            return Outcome(False, f'Unable to determine notBefore or notAfter dates in {cert}')

        if now < not_before:
            return Outcome(False, f'TLS certificate for {host} not valid as {now} is before {not_before}')

        target_date: datetime = now + timedelta(days=days)
        if target_date > not_after:
            return Outcome(False, f'TLS certificate for {host} not valid as {target_date} is after {not_after}')

        return Outcome(True, f'Certificate for {host} valid until {not_after}')


##########################
### URL
##########################

async def url_test(url: str, code: int = 200) -> Outcome:
    timeout: float = 3.0
    try:
        ret = urlopen(url, timeout=timeout)
    except (URLError, socket.timeout) as e:
        return Outcome(False, f'URL {url} failed: {e}')
    else:
        ret_code = ret.getcode()
        if ret_code == code:
            return Outcome(True, f'URL {url} returned code {ret_code}')
        else:
            return Outcome(False, f'URL {url} returned code {ret_code} vs expected {code}')


##########################
### DNSSEC
##########################

async def dnssec_test(name: str) -> Outcome:
    try:
        # First obtain the list of nameservers for the tested domain

        name: Name = dns.name.from_text(name)

        # obtain an IP of a nameserver
        answers: List[dns.resolver.Answer] = dns.resolver.query(name, rdtype=dns.rdatatype.NS)

        if len(answers.rrset) == 0:
            return Outcome(False, f'DNSSEC test for {name} failed due to empty response: {answers}')

        for answer in answers.rrset:
            answer = answer.to_text()

        response = dns.resolver.query(answer, rdtype=dns.rdatatype.A)

    except (AttributeError, DNSException) as e:
        return Outcome(False, f'DNSSEC: Unable to obtain the list of nameservers for {name}: {e}')

    for nameserver_ip in response.rrset:

        nameserver_ip = nameserver_ip.to_text()

        try:

            # obtain DNSKEY from the nameserver
            req_dnskey = dns.message.make_query(name, rdtype=dns.rdatatype.DNSKEY, want_dnssec=True)
            response: Message = dns.query.udp(req_dnskey, nameserver_ip, timeout=2.0)
        except (AttributeError, DNSException) as e:
            return Outcome(False, f'DNSSEC: unable to obtain DNSKEY for {name}: {e}')
        else:

            if response.rcode() != 0:
                return Outcome(False, f'DNSSEC: DNSKEY response {name} from {nameserver_ip} failed: {response.rcode()}')

            if len(response.answer) < 2:
                return Outcome(False, f'DNSSEC test for {name} failed due to empty response: {response.answer}')

            print(f'*** DNSSEC validation for {name} at {nameserver_ip}:')
            for ans in response.answer:
                for a in ans:
                    print(a)

            try:

                # print(f'*** DNSSEC validation for {name} at {nameserver_ip}:\n\ta0={response.answer[0]}\n\ta1={response.answer[1]}')

                # now actually attempt DNSSEC validation on the received record
                dns.dnssec.validate(response.answer[0], response.answer[1], {name: response.answer[0]})

            except (AttributeError, DNSException) as e:
                return Outcome(False, f'DNSSEC validation for {name} at {nameserver_ip} failed: {response}: {e}')

            else:
                return Outcome(True, f'DNSSEC fully validated for {name}')


##########################
### IMAP
##########################

def _imap_test(imap: imaplib.IMAP4, user: Optional[str] = None, password: Optional[str] = None):
    if not len(imap.capabilities) > 0:
        return Outcome(False, f'IMAP capabilities are empty on {imap.host}:{imap.port}: {imap.capabilities}')

    if not user:
        return Outcome(True, f'IMAP test successful on {imap.host}:{imap.port} (not authenticated)')

    if not imap.login(user, password):
        return Outcome(False, f'IMAP login failed on {imap.host}:{imap.port}')

    imap.select()
    status, messages = imap.search(None, 'ALL')
    if status != 'OK':
        return Outcome(False, f'Cannot search messages on {imap.host}:{imap.port}')

    imap.close()

    return Outcome(True, f'IMAP test successful on {imap.host}:{imap.port} (authenticated)')


async def imaps_test(server: str, user: Optional[str] = None, password: Optional[str] = None):
    imap = imaplib.IMAP4_SSL(server)

    return _imap_test(imap, user, password)


async def imap_test(server: str, user: Optional[str] = None, password: Optional[str] = None):
    imap = imaplib.IMAP4(server)

    if not imap.starttls():
        return Outcome(False, f'STARTTLS failed on {imap.host}:{imap.port}')

    return _imap_test(imap, user, password)


##########################
### POP3
##########################

async def pop3s_test(server: str, user: Optional[str] = None, password: Optional[str] = None):
    pop3 = poplib.POP3_SSL(server)
    return _pop3_test(pop3, user, password)


async def pop3_test(server: str, user: Optional[str] = None, password: Optional[str] = None):
    pop3 = poplib.POP3(server)

    if not pop3.stls():
        return Outcome(False, f'STARTTLS failed on {pop3.host}:{pop3.port}')

    return _pop3_test(pop3, user, password)


def _pop3_test(pop3: Union[poplib.POP3, poplib.POP3_SSL], user: Optional[str] = None, password: Optional[str] = None):
    if not len(pop3.capa().items()) > 0:
        return Outcome(False, f'POP3 capabilities empty on {pop3.host}:{pop3.port}: {pop3.capa()}')

    if not user:
        pop3.close()
        return Outcome(True, f'POP3 test successful on {pop3.host}:{pop3.port} (not authenticated)')

    try:
        pop3.user(user)
        pop3.pass_(password)
    except poplib.error_proto as e:
        return Outcome(False, f'POP3 authentication failed on {pop3.host}:{pop3.port}: {e}')

    pop3.uidl()
    status, messages, num = pop3.list()
    if not status.startswith(b'+OK'):
        return Outcome(False, f'POP3 status failed on {pop3.host}:{pop3.port}: {status}')

    pop3.close()


##########################
### SMTP
##########################

async def smtp_test(server: str, user: Optional[str] = None, password: Optional[str] = None, port: int = 25):
    try:
        smtp = smtplib.SMTP(server, timeout=2.0, port=port)
    except socket.timeout as e:
        return Outcome(False, f'SMTP {server}:{port} timed out: {e}')

    # STARTTLS usually requires EHLO
    smtp.ehlo('example.com')

    try:
        smtp.starttls()
    except smtplib.SMTPNotSupportedError as e:
        return Outcome(False, f'SMTP STARTTLS failed on {server}:{port}: {e}')

    auth = 'not authenticated'

    if user:
        msg = EmailMessage()
        msg.set_content('test')
        msg['From'] = user
        msg['To'] = user
        msg['Subject'] = 'test'

        smtp.login(user, password)
        smtp.send_message(msg, user, user)

        auth = 'authenticated'

    smtp.quit()

    return Outcome(True, f'SMTP successful on {server}:{port}: {auth}')


async def run_checks(tasks: List) -> bool:
    start = timer()
    results = await asyncio.gather(*tasks)
    stop = timer()

    ok_tasks = [1 if a.status else 0 for a in results]

    for res in results:
        print(res)

    print(f'{len(tasks)} tests completed in {stop - start:.2f} seconds, {sum(ok_tasks)} successful')

    return len(tasks) == len(ok_tasks)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', nargs=1, type=argparse.FileType('r'), help='Configuration file')
    args = parser.parse_args()

    data: Dict = yaml.load(args.config_file)

    checks: List = []

    for check_name, targets in data.get('checks', {}).items():
        spec = importlib.util.find_spec(f'serverchecks.checks.{check_name}')
        if spec is None:
            print(f'Cannot find check {check_name}, skipping')
            continue
        module = importlib.util.module_from_spec(spec)
        for target in targets:
            checks.append(module.check(target))

    start = timer()
    results = asyncio.run(run_checks(checks))
    stop = timer()

    print(results)
