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

import uuid
from threading import Lock
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from quartet_epcis.models import choices
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

class UUIDModel(models.Model):
    '''
    A base model which uses UUIDs for primary key values.
    '''
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_('Unique ID'),
        verbose_name=_('Unique ID'))

    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created"),
        help_text=_("When this record was created."),
    )
    modified = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Modified"),
        help_text=_("When this record was last modified."),
    )

    class Meta:
        abstract = True


class SourceModel(models.Model):
    '''
    Abstract model class for any classes that reference a UUIDModel
    super-class.  Includes the UUID model UUID and a reference to the
    object type.
    '''
    source_event_id = models.UUIDField(
        help_text=_('The UUID of the source event within the '
                    'Quartet database.'),
        verbose_name=_('Source Event UUID'),
        null=False
    )
    source_event_type = models.CharField(
        max_length=2,
        choices=choices.EVENT_TYPE_CHOICES,
        help_text=_('The type of originating event: Object, Aggregation, '
                    'Transaction or Transformation.'),
        verbose_name=_('Source Event Type')
    )

    def __str__(self):
        return str(self.source_event_id) or ''

    class Meta:
        abstract = True


class EPCISEvent(UUIDModel):
    '''
    The base EPCIS event as defined by GS1 on page 38 of the EPCIS 1.2 draft.
    '''
    event_time = models.DateTimeField(
        db_index=True,
        null=False,
        editable=False,
        help_text=_('The date and time at which the EPCIS Capturing '
                    'Application asserts the event occurred.'),
        verbose_name=_('Event Time')
    )
    event_timezone_offset = models.CharField(
        max_length=6,
        null=True,
        help_text=_('The time zone offset in effect at the '
                    'time and place the event occurred, expressed as an '
                    'offset from UTC'),
        verbose_name=_('Event Timezone Offset'),
        default='+00:00'
    )
    record_time = models.DateTimeField(
        null=True,
        help_text=_('The date and time at which this event was'
                    ' recorded by an EPCIS Repository.'),
        verbose_name=_('Record Time'),
        default=timezone.now
    )
    event_id = models.CharField(
        max_length=150,
        null=True,
        default=haikunate,
        help_text=_('An identifier for this event as specified by the '
                    'capturing application, globally unique across all events '
                    'other than error declarations. Not to be confused with '
                    'the unique id/primary key for events within a database.'),
        verbose_name=_('Event ID'),
        db_index=True
    )

    def __str__(self):
        return self.event_time or ''

    class Meta:
        abstract = True


class EPCISBusinessEvent(EPCISEvent):
    '''
    Abstract base-class for super-classes with an Action,
    biz step, biz location, etc...basically
    every main EPCIS class except the TransformationEvent class.
    '''
    action = models.CharField(
        max_length=10,
        choices=choices.ACTION_CHOICES,
        null=False,
        help_text=_('How this event relates to the lifecycle of the '
                    'EPCs named in this event.'),
        verbose_name=_('Action')
    )
    biz_step = models.CharField(
        max_length=150,
        null=True,
        help_text=_('The business step of which this event was a part.'),
        verbose_name=_('Business Step')
    )
    disposition = models.CharField(
        max_length=150,
        null=True,
        help_text=_('The business condition of the objects associated '
                    'with the EPCs, presumed to hold true until '
                    'contradicted by a subsequent event..'),
        verbose_name=_('Disposition')
    )
    read_point = models.CharField(
        max_length=150,
        null=True,
        help_text=_('The read point at which the event took place.'),
        verbose_name=_('Read Point')
    )
    biz_location = models.CharField(
        max_length=150,
        null=True,
        help_text=_('The business location where the objects '
                    'associated with the EPCs may be found, '
                    'until contradicted '
                    'by a subsequent event.'),
        verbose_name=_('Business Location')
    )

    def __str__(self):
        return self.event_time or ''

    class Meta:
        abstract = True
