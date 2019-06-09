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

from quartet_epcis.models import abstractmodels, choices
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Event(abstractmodels.EPCISBusinessEvent):
    '''
    An omnibus event structure intended to support the
    EPCIS object, transaction, aggregation and transformation
    events.
    '''
    type = models.CharField(
        max_length=2,
        null=False,
        help_text=_('The type of event.'),
        verbose_name=_('Event Type'),
        choices=choices.EVENT_TYPE_CHOICES
    )
    message_id = models.CharField(
        max_length=100,
        null=False,
        help_text=_('The unique id of the originating message.'),
        verbose_name=_('Message ID')
    )

    def __str__(self):
        return "%s: %s" % (self.type, self.event_time) or ''

    class Meta:
        app_label = 'quartet_epcis'
        verbose_name = _('Event')
        verbose_name_plural = _('Events')
        ordering = ['-event_time']


class TransformationID(abstractmodels.UUIDModel):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        null=False,
        help_text=_('The source event.'),
        verbose_name=_('Event')
    )
    identifier = models.CharField(
        max_length=150,
        null=False,
        help_text=_('The Transformation event ID.'),
        verbose_name=_('TransformationID')
    )

    def __str__(self):
        return str(self.identifier) or ''

    class Meta:
        app_label = 'quartet_epcis'
        verbose_name = _('Transformation ID')
        verbose_name_plural = _('Transformation IDs')


class ErrorDeclaration(models.Model):
    '''
    EPCIS Event error declarations.
    '''
    declaration_time = models.DateTimeField(
        help_text=_('The time at which the error was declared.'),
        verbose_name=_('Declaration Time'),
        default=timezone.now
    )
    reason = models.CharField(
        max_length=150,
        null=True,
        help_text=_('The reason for the error.'),
        verbose_name=_('Reason')
    )
    corrective_event_ids = models.TextField(
        help_text=_('A delimited list of EPCIS event ids.'),
        verbose_name=_('Corrective Event IDs'),
        null=True
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        null=False,
        help_text=_('The source event.'),
        verbose_name=_('Event')
    )

    def __str__(self):
        return str(self.declaration_time) or ''

    class Meta:
        app_label = 'quartet_epcis'
        verbose_name = _('Error Declaration')
        verbose_name_plural = _('Error Declarations')


class QuantityElement(models.Model):
    '''
    The EPCIS QuantityElement as outlined in section 7.3.3.3 of the protocol.
    '''
    epc_class = models.CharField(
        max_length=200,
        null=False,
        help_text=_('The EPC class.'),
        verbose_name=_('EPC Class')
    )
    quantity = models.FloatField(
        help_text=_('The Quantity value.'),
        verbose_name=_('Quantity')
    )
    uom = models.CharField(
        max_length=150,
        null=True,
        help_text=_('The unit of measure relative to the quantity.'),
        verbose_name=_('Unit of Measure (UOM)')
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        null=False,
        help_text=_('The source event.'),
        verbose_name=_('Event')
    )
    is_output = models.BooleanField(
        default=False,
        help_text=_('True if this quantity element was provided as '
                    'the output as part of a transformation event.'),
        verbose_name=_('Is Output')
    )

    def __str__(self):
        return "%s: %s" % (self.epc_class, self.quantity) or ''

    class Meta:
        app_label = 'quartet_epcis'
        verbose_name = _('Quantity Element')
        verbose_name_plural = _('Quantity Elements')


class BusinessTransaction(models.Model):
    '''
    The BusinessTransaction model as related to a specific event
    model.
    A BusinessTransaction identifies a particular business
    transaction. An example of a business
    transaction is a specific purchase order. Business Transaction
    information may be included in EPCIS
    events to record an event’s participation in particular
    business transactions.
    As defined in section 7.3.5.3 of the protocol.
    '''
    biz_transaction = models.CharField(
        max_length=200,
        null=False,
        help_text=_('The business transaction.'),
        verbose_name=_('Business Transaction')
    )
    type = models.CharField(
        max_length=200,
        null=True,
        help_text=_('The type of business transaction.'),
        verbose_name=_('Type')
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        null=False,
        help_text=_('The source event.'),
        verbose_name=_('Event')
    )

    def __str__(self):
        return "%s" % self.biz_transaction or ''

    class Meta:
        app_label = 'quartet_epcis'
        verbose_name = _('Business Transaction')
        verbose_name_plural = _('Business Transactions')


class InstanceLotMasterData(models.Model):
    '''
    Instance Lot Master Data as related to a specific event or document
    via the source model UUID.
    '''
    name = models.CharField(
        max_length=150,
        null=False,
        help_text=_('The name of the ILMD entry.'),
        verbose_name=_('Name')
    )
    value = models.CharField(
        max_length=255,
        null=False,
        help_text=_('The value of the ILMD entry.'),
        verbose_name=_('Value')
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        null=False,
        help_text=_('The source event.'),
        verbose_name=_('Event')
    )

    def __str__(self):
        return "%s: %s" % (self.name, self.value) or ''

    class Meta:
        app_label = 'quartet_epcis'
        verbose_name = _('ILMD Entry')
        verbose_name_plural = _('ILMD Entries')


class Source(abstractmodels.UUIDModel):
    '''
    A Source relative to a specific event model.

    A Source or Destination is used to provide
    additional business context when an EPCIS event is
    part of a business transfer; that is, a process
    in which there is a transfer of ownership,
    responsibility, and/or custody of physical or digital objects.
    '''
    type = models.CharField(
        max_length=150,
        null=False,
        help_text=_('The source type.'),
        verbose_name=_('Type')
    )
    source = models.CharField(
        max_length=150,
        null=False,
        help_text=_('The source identifier.'),
        verbose_name=_('Source')
    )

    def __str__(self):
        return "%s: %s" % (self.type, self.source) or ''

    class Meta:
        app_label = 'quartet_epcis'
        verbose_name = _('Source')
        verbose_name_plural = _('Sources')


class SourceEvent(models.Model):
    '''
    An intersection entity for the source and event
    many to many relationship.
    '''
    event = models.ForeignKey(
        Event,
        help_text=_('The event within which the source was reported.'),
        verbose_name=_('Event'),
        null=False,
        on_delete=models.CASCADE
    )
    source = models.ForeignKey(
        Source,
        help_text=_('A source within the event.'),
        verbose_name=_('Source'),
        null=False,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return "%s:%s" % (self.event, self.source) or ''

    class Meta:
        app_label = 'quartet_epcis'


class Destination(abstractmodels.UUIDModel):
    '''
    A Source or Destination is used to provide
    additional business context when an EPCIS event is
    part of a business transfer; that is, a process
    in which there is a transfer of ownership,
    responsibility, and/or custody of physical or digital objects.
    '''
    type = models.CharField(
        max_length=150,
        null=False,
        help_text=_('The source type.'),
        verbose_name=_('Type')
    )
    destination = models.CharField(
        max_length=150,
        null=False,
        help_text=_('The Destination identifier.'),
        verbose_name=_('Destination')
    )

    def __str__(self):
        return '%s: %s' % (self.type, self.destination) or ''

    class Meta:
        app_label = 'quartet_epcis'
        verbose_name = _('Destination')
        verbose_name_plural = _('Destinations')


class DestinationEvent(models.Model):
    '''
    An intersection entity for the destination and event
    many to many relationship.
    '''
    event = models.ForeignKey(
        Event,
        help_text=_('The event within which the destination was reported.'),
        verbose_name=_('Event'),
        null=False,
        on_delete=models.CASCADE
    )
    destination = models.ForeignKey(
        Destination,
        help_text=_('A destination within the event.'),
        verbose_name=_('Destination'),
        null=False,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return '%s: %s' % (self.event, self.destination) or ''

    class Meta:
        app_label = 'quartet_epcis'
