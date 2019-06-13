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
Data Models for User Messages
"""

from __future__ import unicode_literals, absolute_import

import datetime

import six
import sqlalchemy as sa
from sqlalchemy import orm

from .core import Base, uuid_column
from .users import User


class Message(Base):
    """
    Represents a message, sent from one user to other user(s).
    """
    __tablename__ = 'message'
    __table_args__ = (
        sa.ForeignKeyConstraint(['sender_uuid'], ['user.uuid'], name='message_fk_sender'),
    )

    uuid = uuid_column()
    sender_uuid = sa.Column(sa.String(length=32), nullable=False)

    sender = orm.relationship(
        User, doc="""
        Reference to the user who sent the message.
        """,
        backref=orm.backref('sent_messages', cascade='all, delete-orphan', doc="""
        List of all messages which have ever been sent by the user.
        """))

    subject = sa.Column(sa.String(length=255), nullable=True, doc="""
    Subject for the message.
    """)

    body = sa.Column(sa.Text(), nullable=True, doc="""
    Body for the message.  This is assumed to be of type 'text/html'.
    """)

    sent = sa.Column(sa.DateTime(), nullable=False, default=datetime.datetime.utcnow, doc="""
    UTC timestamp when the message was sent.
    """)

    def __str__(self):
        if six.PY2:
            return (self.subject or '').encode('utf8')
        return (self.subject or '')

    if six.PY2:
        def __unicode__(self):
            return (self.subject or '')

    def add_recipient(self, user, **kwargs):
        """
        Add the given user to the message's recipients list, unless it's
        already there.
        """
        if not self.has_recipient(user):
            kwargs['recipient'] = user
            self.recipients.append(MessageRecipient(**kwargs))

    def has_recipient(self, user):
        """
        Returns boolean indicating whether the given user is listed among the
        message's recipients.
        """
        for recipient in self.recipients:
            if recipient.recipient is user:
                return True
        return False


@six.python_2_unicode_compatible
class MessageRecipient(Base):
    """
    Represents the combination of a single message and a single recipient.
    Also tracks status of the message for that recipient, i.e. whether it shows
    in their "inbox".
    """
    __tablename__ = 'message_recip'
    __table_args__ = (
        sa.ForeignKeyConstraint(['message_uuid'], ['message.uuid'], name='message_recip_fk_message'),
        sa.ForeignKeyConstraint(['recipient_uuid'], ['user.uuid'], name='message_recip_fk_recipient'),
        sa.UniqueConstraint('message_uuid', 'recipient_uuid', name='message_recip_uq_message_recipient'),
    )

    uuid = uuid_column()
    message_uuid = sa.Column(sa.String(length=32), nullable=False)
    recipient_uuid = sa.Column(sa.String(length=32), nullable=False)

    status = sa.Column(sa.Integer(), nullable=False, doc="""
    Status code for the message; used to indicate inbox vs. archive.
    """)

    message = orm.relationship(
        Message, doc="""
        Reference to the message which has been "received".
        """,
        backref=orm.backref('recipients', cascade='all, delete-orphan', doc="""
        List of recipients for the message.
        """,
        ))

    recipient = orm.relationship(
        User, doc="""
        Reference to the user who "received" the message.
        """,
        backref=orm.backref('_messages'))

    def __str__(self):
        return str(self.recipient)
