# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2018 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Data Models for Email Bouncer Daemon
"""

from __future__ import unicode_literals, absolute_import

import datetime

import six
import sqlalchemy as sa
from sqlalchemy import orm

from rattail.db.model import Base, uuid_column
from rattail.db.model import User


class EmailAttempt(Base):
    """
    Represents an attempt to send an email.  Ideally the generated message body
    is persisted on disk, in addition to these details.
    """
    __tablename__ = 'email_attempt'

    uuid = uuid_column()

    key = sa.Column(sa.String(length=254), nullable=False, doc="""
    Config key for the email being sent.
    """)

    sender = sa.Column(sa.Text(), nullable=False, doc="""
    Value for the From: email header.
    """)

    to = sa.Column(sa.Text(), nullable=False, doc="""
    Value for the To: email header.
    """)

    cc = sa.Column(sa.Text(), nullable=True, doc="""
    Value for the Cc: email header.
    """)

    bcc = sa.Column(sa.Text(), nullable=True, doc="""
    Value for the Bcc: email header.
    """)

    subject = sa.Column(sa.String(length=254), nullable=False, default='', doc="""
    Value for the Subject: email header.
    """)

    sent = sa.Column(sa.DateTime(), nullable=False, doc="""
    Date and time when email send attempt was first made.
    """)

    status_code = sa.Column(sa.Integer(), nullable=False, doc="""
    Status code for the email.
    """)

    status_text = sa.Column(sa.Text(), nullable=True, doc="""
    Status text for the email, if applicable.
    """)

    def __str__(self):
        if six.PY2:
            return self.subject.encode('utf8')
        return self.subject

    if six.PY2:
        def __unicode__(self):
            return self.subject


@six.python_2_unicode_compatible
class EmailBounce(Base):
    """
    Represents an email bounce notification message.  This table is populated
    by the Bouncer daemon and then exposed as a workflow queue within Tailbone.
    """
    __tablename__ = 'email_bounce'
    __table_args__ = (
        sa.ForeignKeyConstraint(['processed_by_uuid'], ['user.uuid'], name='email_bounce_fk_processed_by'),
        )

    uuid = uuid_column()

    config_key = sa.Column(sa.String(length=20), nullable=False, doc="""
    Key for the configuration profile with which the bounce is associated.
    This profile is also what determines the handler for the bounce.
    """)

    bounced = sa.Column(sa.DateTime(), nullable=False, default=datetime.datetime.utcnow, doc="""
    Date and time when the email bounce was discovered.  Defaults to current time.
    """)

    bounce_recipient_address = sa.Column(sa.String(length=255), nullable=False, doc="""
    Email address to which the bounce notification message was sent.
    """)

    intended_recipient_address = sa.Column(sa.String(length=255), nullable=True, doc="""
    Email address of the original intended recipient, if one could be determined.
    """)

    intended_recipient_key = sa.Column(sa.String(length=20), nullable=True, doc="""
    Generic key for the intended recipient.  This must be populated and
    interpreted by a custom bounce handler.
    """)

    processed = sa.Column(sa.DateTime(), nullable=True, doc="""
    Date and time when the email bounce was fully processed by a user.
    """)

    processed_by_uuid = sa.Column(sa.String(length=32), nullable=True)

    processed_by = orm.relationship(User, doc="""
    Reference to the :class:`rattail.db.model.User` who processed the bounce.
    """)

    def __str__(self):
        if self.intended_recipient_address:
            return str(self.intended_recipient_address)
        return str(self.bounce_recipient_address)
