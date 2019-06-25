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

from django.db import models
from django.utils.translation import gettext_lazy as _

from quartet_epcis.models import abstractmodels, events
from quartet_epcis.models.choices import EVENT_TYPE_CHOICES, ACTION_CHOICES


class Entry(abstractmodels.UUIDModel):
    '''
    Represents an entry in the general ledger of serialized items and/or
    logical numbers used for serialized goods processing.
    '''
    identifier = models.CharField(
        max_length=150,
        null=False,
        help_text=_('The primary unique id for the entry.'),
        verbose_name=_('EPC URN'),
        db_index=True,
        unique=True
    )
    parent_id = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        verbose_name=_("Parent ID"),
        related_name='parent_identifier',
        help_text=_("The parent of this identifier (if any)."),
        null=True
    )
    top_id = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        verbose_name=_("Top ID"),
        help_text=_("The top level id (if any)."),
        related_name='top_identifier',
        null=True
    )
    last_event = models.ForeignKey(
        'quartet_epcis.Event',
        null=True,
        on_delete=models.PROTECT,
        verbose_name=_("Last Event"),
        help_text=_("The last event to affect the status of this entry."),
    )
    last_event_time = models.DateTimeField(
        verbose_name=_("Last Event Time"),
        help_text=_("The time of the event that last affected the status of"
                    "this entry."),
        null=True
    )
    last_disposition = models.CharField(
        max_length=150,
        null=True,
        help_text=_('The business condition of the objects associated '
                    'with the EPCs, presumed to hold true until '
                    'contradicted by a subsequent event..'),
        verbose_name=_('Last Disposition')
    )
    last_aggregation_event = models.ForeignKey(
        'quartet_epcis.Event',
        related_name='last_agg_event',
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Last Aggregation Event"),
        help_text=_("Used mostly for internal tracking and performance during"
                    "parsing.  This tracks the last aggregation event that"
                    "affected the entry."),
    )
    last_aggregation_event_time = models.DateTimeField(
        verbose_name=_("Last Aggregation Event Time"),
        help_text=_("The time of the event that last affected the status of"
                    "this entries hierarchical relation to other entries."),
        null=True
    )
    last_aggregation_event_action = models.CharField(
        null=True,
        max_length=10,
        verbose_name=_("Last Aggregation Action"),
        help_text=_("The action (ADD or DELETE) of the last aggregation "
                    "event that affected this entry.  Observation events "
                    "are not noted."),
        choices=ACTION_CHOICES
    )
    is_parent = models.BooleanField(
        default=False,
        null=False,
        verbose_name=_("Is Parent"),
        help_text=_("True if this entry is a parent in any hierarchies. False"
                    "if not.")
    )
    decommissioned = models.BooleanField(
        default=False,
        null=False,
        verbose_name=_("Decommissioned"),
        help_text=_("Whether or not the entry has been decommissioned.  Once"
                    "an entry is decommissioned, it can no longer take place"
                    "in business processes."),
    )

    def __str__(self):
        return self.identifier or ''

    class Meta:
        verbose_name = _('Entry')
        verbose_name_plural = _('Entries')
        app_label = 'quartet_epcis'
        ordering = ['created']


class EntryEvent(models.Model):
    '''
    An intersection entity for events and entries.
    '''
    event = models.ForeignKey(
        'quartet_epcis.Event',
        null=False,
        help_text=_('The UUID of the event.'),
        verbose_name=_('Event ID'),
        db_index=True,
        on_delete=models.CASCADE
    )
    event_type = models.CharField(
        null=False,
        max_length=3,
        verbose_name=_("Event Type"),
        help_text=_("The type of event (Aggregation, Object, Transaction or"
                    " Transformation."),
        choices=EVENT_TYPE_CHOICES
    )
    event_time = models.DateTimeField(
        null=False,
        help_text=_('The Event\'s eventTime.'),
        verbose_name=_('Event Time'),
        db_index=True
    )
    entry = models.ForeignKey(
        'quartet_epcis.Entry',
        null=False,
        help_text=_('The Unique ID of the Entry'),
        verbose_name=_('Entry ID'),
        db_index=True,
        on_delete=models.CASCADE
    )
    identifier = models.CharField(
        max_length=150,
        null=False,
        help_text=_('A redundant entry ID entry for fast event composition.'),
        verbose_name=_('EPC URN'),
        db_index=True
    )
    is_parent = models.BooleanField(
        default=False,
        help_text=_('Whether or not this entry was the parent of it\'s '
                    'constituent event.'),
        verbose_name=_('Is Event Parent')
    )
    output = models.BooleanField(
        default=False,
        help_text=_('Whether or not the entry was the output of '
                    'a Transformation event.'),
        verbose_name=_('Transformation Output')
    )
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

    def __str__(self):
        return self.identifier or ''

    class Meta:
        verbose_name = _('Entry Event Record')
        verbose_name_plural = _('Entry Event Records')
        index_together = ["event", "entry"]
        app_label = 'quartet_epcis'
