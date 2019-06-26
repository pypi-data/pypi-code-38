# -*- coding: utf-8 -*-
# Copyright (c) 2018  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Filip Valder <fvalder@redhat.com>
#            Chenxiong Qi <cqi@redhat.com>
#            Qixiang Wan <qwan@redhat.com>

import logging
import smtplib

from email.message import Message
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr, parseaddr
from ursa_major.utils import jinja2_env
from ursa_major.logger import log


class MailAPI:
    def __init__(self, config):
        """
        Instantiate Mail API (connect to mail server)
        """

        # Set coding
        self.coding = 'utf-8'

        # Load configuration
        self.conf = config

        # Configure Jinja2 environment
        self.env = jinja2_env('mail')

        # Configure sender's e-mail address
        f_realname, f_addr = parseaddr(self.conf['mail_from'])
        if not f_addr:
            raise Exception("Unable to parse sender's e-mail address. "
                            "Check 'mail_from' in configuration of ursa-major.")
        self.fromaddr = formataddr((f_realname, f_addr))

        # Set up mail log level
        log_level = self.conf.get('mail_log_level', 'NOTSET')
        self.log_level = getattr(logging, log_level.upper())

        # Set up mail processing
        self.processing = self._processing()

        # Initiate SMTP connection
        self.server = self._connect()

    def _processing(self):
        if 'mail_processing' not in self.conf:
            return False

        if self.conf['mail_processing'].lower() in ['enable', 'yes', 'true']:
            return True
        elif self.conf['mail_processing'].lower() in ['disable', 'no', 'false']:
            return False
        else:
            raise ValueError(
                "Unknown value for 'mail_processing' option: {}".format(
                    self.conf['mail_processing']))

    def _connect(self):
        """
        Connect to mail server
        """

        if not self.processing:
            return

        server = None

        address = self.conf['mail_server']
        try:
            server = smtplib.SMTP(address)
        except Exception:
            log.exception("Cannot connect to SMTP server at %r." % address)
            raise
        if not server:
            return

        try:
            server.starttls()
        except Exception:
            log.exception("STARTTLS extension not supported by server. "
                          "WARNING! Communication with the server will not be "
                          "secured.")

        server.ehlo_or_helo_if_needed()

        return server

    def _is_connected(self):
        """
        Helper for checking SMTP connection status
        """

        try:
            status = self.server.noop()[0]
        except Exception:  # smtplib.SMTPServerDisconnected
            status = -1
        return True if status == 250 else False

    def _mail_render(self, template, data=None):
        """
        Render mail body (plain text/HTML) using Jinja2 and provided data
        """

        template += ".j2"
        log.debug("Rendering template '%s'." % (template))
        text = self.env.get_template(template)
        if data:
            msg = text.render(data=data)
        else:
            msg = text.render()

        return msg

    def _process_recipients(self, *addrs):
        """
        Process recipients (mail addresses) and return properly formatted
        commar-separated list of addresses.
        """

        all_addrs = list()
        for addr in addrs:
            all_addrs += [addr] if isinstance(addr, str) else addr

        # process only non-empty addresses
        all_addrs = [a for a in all_addrs if a]

        for i, a in enumerate(all_addrs):
            realname, addr = parseaddr(a)
            if not addr:
                log.warning("Unable to parse recipient's e-mail address. "
                            "Please check: %s", a if a else '<missing-address>')
            all_addrs[i] = realname, addr

        return ', '.join([formataddr((r, a)) for r, a in all_addrs if a])

    def _mail_headers(self, *headers):
        """
        This method formats headers for message envelope. Typically 'From',
        'To' and 'Subject' which aren't included by default.

        :param headers: a 3-tuple of header name, its value and True/False
                        bool whether to apply encoding;
                        this arg may be repeated multiple times for different
                        headers
        :return: message headers as string
        """

        msg = Message()
        for header_name, header_value, use_encode in headers:
            if use_encode:
                msg[header_name] = Header(header_value, self.coding,
                                          header_name=header_name).encode()
            else:
                msg[header_name] = Header(header_value, header_name=header_name)
        return msg.as_string().rstrip('\n') + '\n'

    def send_mail(self, template, toaddrs, subject='', data=None, ccs='',
                  bccs='', replyto=None):
        """
        Send e-mail rendered using predefined Jinja2 template.

        :param template: Jinja2 mail template name omitting the .j2 suffix
        :param toaddrs: str or list identifying message recipient(s)
                        (To: header)
        :param subject: message subject; this will be prefixed with
                        a configured prefix (if non-empty)
        :param data: data to be processed/rendered in the template
        :param ccs: str or list identifying additional message recipient(s)
                    (Cc: header)
        :param bccs: str or list identifying additional message recipient(s)
                     (Bcc: header)
        :param replyto: str identifying address for replies (Reply-To: header)
        """

        # Check if we're still connected to the mail server
        # If not => reconnect!
        if self.processing and not self._is_connected():
            self.server = self._connect()

        # Process mail template
        content = self._mail_render(template, data)
        if template.endswith('.html'):
            msg = MIMEMultipart('alternative')
            msg.attach(MIMEText(content, 'html', self.coding))
        elif template.endswith('.txt'):
            msg = MIMEText(content, _charset=self.coding)
        else:
            log.error("Unrecognized template format.")
            return

        # Process recipient(s)
        toaddrs = self._process_recipients(toaddrs)
        mail_always_cc = self.conf.get('mail_always_cc', '')
        mail_always_cc = [e.strip() for e in mail_always_cc.split(',') if '@' in e]
        ccs = self._process_recipients(ccs, mail_always_cc)

        mail_always_bcc = self.conf.get('mail_always_bcc', '')
        mail_always_bcc = [e.strip() for e in mail_always_bcc.split(',') if '@' in e]
        bccs = self._process_recipients(bccs, mail_always_bcc)

        # Process subject
        if 'mail_subject_prefix' in self.conf and self.conf['mail_subject_prefix']:
            subject = self.conf['mail_subject_prefix'] + ' ' + subject

        # Prepare the most important headers (will be used
        # for S/MIME envelope later)
        mail_envelope = self._mail_headers(
            ('From', self.fromaddr, False), ('To', toaddrs, False),
            ('Subject', subject, True))

        if ccs:
            msg['Cc'] = Header(ccs, header_name='Cc')
        if bccs:
            msg['Bcc'] = Header(bccs, header_name='Bcc')
        msg['Reply-To'] = Header(
            replyto if replyto else self.conf.get('mail_replyto', self.fromaddr),
            header_name='Reply-To')

        mail = mail_envelope + msg.as_string()

        # To addresses should be a list, a bare string will be treated as a list
        # with 1 address, CCs and BCCs should be added in to to-addresses, the
        # distinction between TO, CC and BCC occurs only in the text headers.
        # At the SMTP level, everybody is a recipient.
        to_addrs = [n.strip() for n in
                    (toaddrs.split(',') + ccs.split(',') + bccs.split(',')) if n]

        try:
            if self.processing:
                self.server.sendmail(self.fromaddr, to_addrs, mail)
            log.log(self.log_level, mail)
        except smtplib.SMTPException:
            log.exception("Cannot send mail to recipients: %s" % (toaddrs))
