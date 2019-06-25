# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2018 SerialLab Corp.  All rights reserved.

from threading import Lock
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils import models as utils
from haikunator import Haikunator


haiku = Haikunator()

def haikunate():
    '''
    Since the haikunator is a class method
    it could not be used directly as a default callable for
    a django field...hence this function.
    '''
    try:
        lock = Lock()
        lock.acquire()
        ret = haiku.haikunate(token_length=8, token_hex=True)
    finally:
        lock.release()
    return ret

document_type_choices = (
    ('Events', 'Events'),
    ('MasterData', 'MasterData'),
    ('QueryControl-Request', 'QueryControl-Request'),
    ('QueryControl-Response', 'QueryControl-Response'),
    ('QueryCallback', 'QueryCallback'),
    ('Query', 'Query')
)

partner_choices = (
    ('Sender', 'Sender'),
    ('Receiver', 'Receiver')
)


class Message(models.Model):
    '''
    An umbrella model to unify all headers and events that arrived
    as part of a single message.  If the message had a unique id supplied in
    the header, that will be used (albeit redunantly) along with a UUID4
    for each message as the primary key.
    '''
    utils.AutoCreatedField(
        help_text=_('The date and time this record was created.'),
        verbose_name=_('Created Date')
    )

    def __str__(self):
        return str(self.id) or ''

    class Meta:
        app_label = 'quartet_epcis'


class SBDH(models.Model):
    '''
    The db model representing the sbdh as defined by GS1.
    '''
    header_version = models.CharField(
        max_length=10,
        null=False,
        help_text=_('Descriptor which contains version '
                    'information for the SBDH.  Default is 1.0'),
        verbose_name=_('Header Version'),
        default='1.0'
    )
    document_identification = models.ForeignKey(
        'quartet_epcis.DocumentIdentification',
        null=False,
        on_delete=models.CASCADE
    )
    message = models.ForeignKey(
        'quartet_epcis.Message',
        on_delete=models.CASCADE,
        help_text=_('The message this header was associated with.'),
        verbose_name=_('Message')
    )

    def __str__(self):
        return '%s: %s' % (self.document_identification, self.message) or ''

    class Meta:
        verbose_name = _('SBDH')
        verbose_name_plural = _('SBDHs')
        app_label = 'quartet_epcis'


class Partner(models.Model):
    '''
    Trading partner data.
    '''
    partner_type = models.CharField(
        max_length=20,
        null=False,
        help_text=_('The type of partner.  Either Sender or Receiver.'),
        verbose_name=_('Partner Type'),
        choices=partner_choices
    )
    authority = models.CharField(
        max_length=20,
        null=True,
        help_text=_('The identifying authority/format for the '
                    'identification field. Default is SGLN.'),
        verbose_name=_('authority'),
        default='SGLN'
    )
    identifier = models.CharField(
        max_length=100,
        null=True,
        help_text=_('An identifier that is in line with the authority '
                    'specified in the authority field.  Typically an '
                    'SGLN URN value.'),
        verbose_name=_('Identifier')
    )
    contact = models.CharField(
        max_length=50,
        null=True,
        help_text=_('The contact/name info.'),
        verbose_name=_('Contact')

    )
    email_address = models.EmailField(
        max_length=100,
        null=True,
        help_text=_('The email address for the partner.'),
        verbose_name=_('Email Address')
    )

    fax_number = models.CharField(
        max_length=20,
        null=True,
        help_text=_('Fax number.'),
        verbose_name=_('Fax Number')
    )
    telephone_number = models.CharField(
        max_length=20,
        null=True,
        help_text=_('Telephone number for the partner.'),
        verbose_name=_('Telephone number.')
    )
    contact_type_identifier = models.CharField(
        max_length=40,
        null=True,
        help_text=_('The type of contact- for example, '),
        verbose_name=_('Role of the contact in this business process.')
    )
    header = models.ForeignKey(
        'quartet_epcis.SBDH',
        on_delete=models.CASCADE,
        help_text=_('The related SBDH.'),
        verbose_name=_('SBDH')
    )

    def __str__(self):
        if self.authority:
            ret = '{0}:{1}'.format(self.authority, self.identifier) or ''
        else:
            ret = '{0}:{1}'.format(self.id, self.partner_type) or ''
        return ret

    class Meta:
        verbose_name = _('Partner')
        verbose_name_plural = _('Partners')
        app_label = 'quartet_epcis'


class DocumentIdentification(models.Model):
    '''
    The core model for the GS1 SBDH document identification element.
    '''
    standard = models.CharField(
        max_length=20,
        null=False,
        default='EPCglobal',
        help_text=_('The originator of the standard that the '
                    'following document falls under.  '
                    'Default is EPCglobal.'),
        verbose_name=_('Standard')
    )
    type_version = models.CharField(
        max_length=10,
        null=False,
        help_text=_('Descriptor which contains versioning information '
                    'or number of the standard that defines the document'
                    'which is specified in the ’Type’ data element, e.g. '
                    'values could be ‘1.3’ or ‘D.96A’, etc.'),
        verbose_name=_('Version'),
        default='1.0'
    )
    instance_identifier = models.CharField(
        max_length=100,
        null=False,
        help_text=_('Descriptor which contains reference information '
                    'which uniquely identifies this instance of the SBD '
                    'between the sender and the receiver.'),
        verbose_name=_('Instance Identifier'),
        db_index=True
    )
    document_type = models.CharField(
        max_length=25,
        null=False,
        help_text=_('A logical indicator representing the type of '
                    'Business Data being sent or the named type of '
                    'business data.'),
        verbose_name=_('Type'),
        choices=document_type_choices
    )
    multiple_type = models.NullBooleanField(
        default=False,
        help_text=_('A flag to indicate that there is more than one '
                    'type of Document in the instance.'),
        verbose_name=_('Multiple Type')
    )
    creation_date_and_time = models.CharField(
        max_length=35,
        null=True,
        help_text=_('Descriptor which contains date and time of '
                    'SBDH/document creation.'),
        verbose_name=_('Creation Date and Time')
    )

    def __str__(self):
        return 'Document Id {0}: {1}'.format(self.id,
                                             self.creation_date_and_time) or ''

    class Meta:
        verbose_name = _('Document Identification')
        verbose_name_plural = _('Document Identifications')
        app_label = 'quartet_epcis'
