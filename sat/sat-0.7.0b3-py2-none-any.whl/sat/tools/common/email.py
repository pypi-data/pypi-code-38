#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SàT: a jabber client
# Copyright (C) 2009-2019 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""email sending facilities"""

from __future__ import absolute_import
from email.mime.text import MIMEText
from twisted.mail import smtp
from sat.core.constants import Const as C
from sat.tools import config as tools_config


def sendEmail(config, to_emails, subject=u"", body=u"", from_email=None):
    """Send an email using SàT configuration

    @param config (SafeConfigParser): the configuration instance
    @param to_emails(list[unicode], unicode): list of recipients
        if unicode, it will be split to get emails
    @param subject(unicode): subject of the message
    @param body(unicode): body of the message
    @param from_email(unicode): address of the sender
    @return (D): same as smtp.sendmail
    """
    if isinstance(to_emails, basestring):
        to_emails = to_emails.split()
    email_host = tools_config.getConfig(config, None, u"email_server") or u"localhost"
    email_from = tools_config.getConfig(config, None, u"email_from")
    if email_from is None:
        # we suppose that email domain and XMPP domain are identical
        domain = tools_config.getConfig(config, None, u"xmpp_domain", u"example.net")
        email_from = u"no_reply@" + domain
    email_sender_domain = tools_config.getConfig(config, None, u"email_sender_domain")
    email_port = int(tools_config.getConfig(config, None, u"email_port", 25))
    email_username = tools_config.getConfig(config, None, u"email_username")
    email_password = tools_config.getConfig(config, None, u"email_password")
    email_auth = C.bool(tools_config.getConfig(config, None, "email_auth", C.BOOL_FALSE))
    email_starttls = C.bool(tools_config.getConfig(config, None, "email_starttls",
                            C.BOOL_FALSE))

    msg = MIMEText(body, "plain", "UTF-8")
    msg[u"Subject"] = subject
    msg[u"From"] = email_from
    msg[u"To"] = u", ".join(to_emails)

    return smtp.sendmail(
        email_host.encode("utf-8"),
        email_from.encode("utf-8"),
        [email.encode("utf-8") for email in to_emails],
        msg.as_string(),
        senderDomainName=email_sender_domain.encode("utf-8") if email_sender_domain
                                                             else None,
        port=email_port,
        username=email_username.encode("utf-8") if email_username else None,
        password=email_password.encode("utf-8") if email_password else None,
        requireAuthentication=email_auth,
        requireTransportSecurity=email_starttls,
    )
