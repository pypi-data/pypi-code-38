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
import logging
from typing import List
from gettext import gettext as _
from rest_framework import views
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.exceptions import NotFound
from rest_framework import status
from EPCPyYes.core.v1_2 import template_events
from quartet_epcis.db_api.queries import EPCISDBProxy
from quartet_epcis.models import events, headers, entries

logger = logging.getLogger(__name__)
EventList = List[events.Event]
proxy = EPCISDBProxy()


class FormatHelperMixin:
    '''
    This mixin helps determine whether or not to call the xml template_event
    functionality or the JSON functionality based on the inbound
    content type of the HTTP request or the explicit format request
    in the HTTP query parameters.
    '''

    def get_formatted_data(self, request: Request, template_event,
                           format=None):
        if 'xml' in request.content_type.lower() or \
            'xml' in request.query_params.get('format', '') or \
            format == 'xml':
            response_data = template_event.render()
        else:
            # else render JSON
            response_data = template_event.render_dict()
        return response_data


class EventDetailView(views.APIView, FormatHelperMixin):
    # sentinal queryset for rights management
    queryset = events.Event.objects.none()

    def get(self, request: Request, format=None, event_id: str = None):
        '''
        Based on an inbound event id, will return the full event data as
        JSON or XML string.  The event_id that is passed in can be either the
        primary key of the event in the database or the actual EPCIS event_id
        value that uniquely identifies the event.

        The URI for a given event is as below (assuming that the urls.py
        was configured for access via `epcis`):

        .. code-block:: text

            # default format is json so format query parameter is optional
            http[s]:/[hostname]:[port]/epcis/event-detail/[event id]/?format=[xml,json]

            # for example
            http://localhost:8000/epcis/event-detail/1d1fa10f-4421-4f2a-af10-4ddb4951807c/?format=json

        :return: A JSON string representing the event.

        '''

        response_data = {}
        try:
            if event_id:
                event = proxy.get_event_by_id(event_id)
                response_data = self.get_formatted_data(request, event, format)
            response = Response(response_data, status=status.HTTP_200_OK)
        except events.Event.DoesNotExist:
            response = Response('Event with id %s could not be '
                                'found' % event_id, status.HTTP_404_NOT_FOUND)
        return response



class EntryEventHistoryView(views.APIView, FormatHelperMixin):
    '''
    Returns all of the events associated with a given EPC/Entry.
    '''
    # sentinal queryset for permissions
    queryset = entries.Entry.objects.none()

    def get(self, request: Request, format=None, entry_pk: str = None,
            entry_identifier: str = None):
        '''
        Will pull out the event history of a given entry based on either
        it's primary key value in the data store or its identifier field
        which is typically the textual identifier such as an EPC urn.

        .. code-block:: text

            # default format is json so format query parameter is optional
            http[s]:/[hostname]:[port]/epcis/events-by-entry-id/?format=[xml,json]

            # an example get reques for xml format
            http://localhost:8000/epcis/events-by-entry-id/urn:epc:id:sgtin:305555.05555sdf55.1/?format=xml

        :param request: The HTTP request
        :param format: json or xml
        :param entry_pk: The entry primary key.
        :param entry_identifier: The entry identifier.
        :return: A series of XML or JSON structures representing the events
        associated with the inbound id.

        '''
        args = {'epc_pk': entry_pk} if entry_pk else {
            'epc': entry_identifier}
        # get a list of EPCPyYes events from the DB proxy
        events = proxy.get_events_by_epc(**args)
        if len(events) > 0:
            epcis_document = template_events.EPCISEventListDocument(events)
            response_data = self.get_formatted_data(request, epcis_document,
                                                    format)
            return Response(response_data, status.HTTP_200_OK)
        else:
            raise NotFound(_('The entry with id %s could not be found.' % \
                             str(args)))


class EventsByILMDView(views.APIView, FormatHelperMixin):
    '''
    Gets all events associated with an ILMD name and value pair.
    For example Lot:2233
    '''
    queryset = events.Event.objects.none()

    def get(self, request: Request, format=None, ilmd_name=None,
            ilmd_value=None):
        pyyes_events = proxy.get_events_by_ilmd(ilmd_name, ilmd_value)
        if len(pyyes_events) > 0:
            epcis_document = template_events.EPCISEventListDocument(
                pyyes_events)
            response_data = self.get_formatted_data(request,
                                                    epcis_document,
                                                    format=format)
            return Response(response_data, status.HTTP_200_OK)
        else:
            msg = _('No events could be found that match name %s ' \
                    'and value %s' % (ilmd_name, ilmd_value))
            logger.debug(msg)
            raise NotFound(msg)


class MessageDetail(views.APIView, FormatHelperMixin):
    '''
    Returns a list of the full EPCIS messages that were received.
    '''
    queryset = headers.Message.objects.none()

    def get(self, request: Request, format=None, message_id=None):
        '''
        Returns a full EPCIS message based on the inbpund message id.
        '''
        # get the message
        try:
            db_message = headers.Message.objects.get(id=message_id)
            message = proxy.get_full_message(db_message)
            return Response(self.get_formatted_data(request, message))
        except headers.Message.DoesNotExist:
            found_message_id = 'The message with id %s could not ' \
                               'be found' % message_id
            logger.debug()
            raise NotFound(found_message_id)
