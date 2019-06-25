# -*- coding: utf-8 -*-
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

from EPCPyYes.core.v1_2.events import EventType
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

ACTION_CHOICES = (
    ('ADD', 'Add'),
    ('OBSERVE', 'Observe'),
    ('DELETE', 'Delete')
)

EVENT_CHOICES = (
    (EventType.Object.value, EventType.Object.value),
    (EventType.Transaction.value, EventType.Transaction.value),
    (EventType.Transformation.value, EventType.Transformation.value),
    (EventType.Aggregation.value, EventType.Aggregation.value)
)


class EPCISOutputCriteria(models.Model):
    """
    Based on the contents of an inbound event or groups of events,
    this model can be used to examine the contents of the events and
    determine what rules to execute for messaging.
    """
    name = models.CharField(
        max_length=150,
        verbose_name=_("Name"),
        help_text=_("The name of the criteria record"),
        null=False,
        unique=True
    )
    sender_identifier = models.CharField(
        max_length=250,
        verbose_name=_("SBDH Sender Identifier"),
        help_text=_("Typically an SGLN but an identifier that is in the SBDH "
                    "and uniquely identifies a sending entity."),
        null=True
    )
    receiver_identifier = models.CharField(
        max_length=250,
        verbose_name=_("SBDH Receiver Identifier"),
        help_text=_("Typically an SGLN but an identifier that is in the SBDH "
                    "and uniquely identifies a receiving entity."),
        null=True
    )
    event_type = models.CharField(
        max_length=20,
        verbose_name=_("Event Type"),
        help_text=_("The type of EPCIS event."),
        null=True,
        choices=EVENT_CHOICES
    )
    action = models.CharField(
        max_length=20,
        verbose_name=_("Action"),
        help_text=_("The EPCIS event's ACTION type."),
        null=True,
        choices=ACTION_CHOICES
    )
    biz_step = models.CharField(
        max_length=150,
        verbose_name=_("Business Step (BizStep)"),
        help_text=_("The business step URN.  Can be a CBV value or any custom"
                    "uri.  If CBV it must be exactly as specified in v1.2"),
        null=True
    )
    disposition = models.CharField(
        max_length=150,
        verbose_name=_("Disposition"),
        help_text=_("A Disposition URN- can be CBV or custom."),
        null=True
    )
    read_point = models.CharField(
        max_length=150,
        null=True,
        help_text=_('The read point URN.  Typically representing a sub-site.'),
        verbose_name=_('Read Point')
    )
    biz_location = models.CharField(
        max_length=150,
        null=True,
        help_text=_('The business location URN.  Typically representing '
                    'a site'),
        verbose_name=_('Business Location')
    )
    source_type = models.CharField(
        max_length=150,
        verbose_name=_("Source Type"),
        help_text=_("The type of the source- a CBV 1.2 URI or custom URI."),
        null=True
    )
    source_id = models.CharField(
        max_length=200,
        verbose_name=_("Source ID"),
        help_text=_("A URI that identifies the source specified in the "
                    "Source Type field."),
        null=True
    )
    destination_type = models.CharField(
        max_length=150,
        verbose_name=_("Destination Type"),
        help_text=_(
            "The type of the Destination- a CBV 1.2 URI or custom URI."),
        null=True
    )
    destination_id = models.CharField(
        max_length=200,
        verbose_name=_("Destination ID"),
        help_text=_("A URI that identifies the Destination specified in the "
                    "Destination Type field."),
        null=True
    )
    authentication_info = models.ForeignKey(
        'quartet_output.AuthenticationInfo',
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Authentication Info"),
        help_text=_("The Authentication Info to use."),
    )
    end_point = models.ForeignKey(
        'quartet_output.EndPoint',
        null=False,
        on_delete=models.PROTECT,
        verbose_name=_("End Point"),
        help_text=_("A prtocol-specific endpoint defining where any output"
                    " data will be sent."),
    )

    def clean(self):
        """
        Require that if both source and destination fields are configured if
        one or the other type/id is.
        """
        if self.source_type or self.source_id:
            if not (self.source_type and self.source_id):
                raise ValidationError(_("If either the Source Type or ID "
                                        "are specified then both must be."))
        if self.destination_type or self.destination_id:
            if not (self.destination_type and self.destination_id):
                raise ValidationError(_("If either the Destination Type or ID "
                                        "are specified then both must be."))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('EPCIS Output Criteria')
        verbose_name_plural = _('EPCIS Output Criteria')


class EndPoint(models.Model):
    """
    Defines a generic endpoint.
    """
    name = models.CharField(
        max_length=150,
        verbose_name=_("Name"),
        help_text=_("The name of the endpoint"),
        null=False,
        unique=True
    )
    urn = models.CharField(
        max_length=1000,
        verbose_name=_("URL"),
        help_text=_("A uniform resource locator that includes "
                    "protocol information."),
        null=False
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('End Point')
        verbose_name_plural = _('End Points')


class AuthenticationInfo(models.Model):
    """
    Holds data relative to basic auth needed by EndPoints for HTTP and other
    username/password protocols.  Encryption of the password is handled
    through the API layer.  Do not bypass the API when creating users or
    you run the risk of exposing authentication data.
    """
    username = models.CharField(
        max_length=150,
        verbose_name=_("Username"),
        help_text=_("The username."),
        null=False
    )
    password = models.CharField(
        max_length=25,
        verbose_name=_("Password"),
        help_text=_("The password for the user."),
        null=False
    )
    type = models.CharField(
        max_length=25,
        verbose_name=_("Type"),
        help_text=_("The type of authentication to use.  For example, Basic,"
                    " Digest, SSH, etc.  This is optional depending on whether"
                    " or not any steps require this information.")
    )
    description = models.CharField(
        max_length=200,
        verbose_name=_("Description"),
        help_text=_("An optional description."),
        null=True
    )
    private_key = models.TextField(
        verbose_name=_("Private Key"),
        help_text=_("Any private key value if applicable."),
        null=True
    )
    public_key = models.TextField(
        verbose_name=_("Public Key"),
        help_text=_("Any public key info if applicable."),
        null=True
    )

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = _('Authentication Info')
        verbose_name_plural = _('Authentication Info')
