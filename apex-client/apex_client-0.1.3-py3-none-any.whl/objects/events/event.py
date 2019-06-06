import datetime
from typing import Optional

from django.template.defaultfilters import date as _date

from apex_client.objects import ApexObject
from apex_client.objects.exceptions import MultipleObjectsReturned
from apex_client.request import ApexRequest

from .event_area import EventArea
from .event_participant import EventParticipant
from .mail_template import MailTemplate
from .session import Session
from .type import Type


class Event(ApexObject):
    valid_properties = ['id', 'slug', 'identifier', 'event_id', 'order', 'name', 'uuid', 'is_active', 'is_template',
                        'description', 'parent', 'number_of_days', 'timezone', 'venue', 'venue_name', 'venue_city',
                        'min_participants', 'max_participants', 'language', 'invoiced_date', 'promote_program',
                        'portal_participants', 'booked_participant_count']
    date_properties = ['date_created', 'date_modified', 'start_date', 'end_date']

    def __init__(self, json_data: dict):
        from apex_client.objects.portals import PortalEvent

        super().__init__(json_data)

        keys = json_data.keys()

        self.areas = []
        self.mail_templates = []
        self.portals = []
        self.sessions = []
        self.types = []

        if 'areas' in keys:
            for item in json_data['areas']:
                if isinstance(item, dict):
                    self.areas.append(EventArea(item))

        if 'mail_templates' in keys:
            for item in json_data['mail_templates']:
                if isinstance(item, dict):
                    self.mail_templates.append(MailTemplate(item))

        if 'portals' in keys:
            for item in json_data['portals']:
                if isinstance(item, dict):
                    self.portals.append(PortalEvent(item))

        if 'sessions' in keys:
            for item in json_data['sessions']:
                if isinstance(item, dict):
                    self.sessions.append(Session(item))

        if 'types' in keys:
            for item in json_data['types']:
                if isinstance(item, dict):
                    self.types.append(Type(item))

    @classmethod
    def get(cls, event_id: int, template: Optional[bool] = False) -> Optional['Event']:
        if template:
            return Event._get(f'templates/{event_id}/')
        else:
            return Event._get(f'events/{event_id}/')

    @classmethod
    def get_by_slug(cls, slug: str) -> Optional['Event']:
        results = ApexRequest.search_all(f'templates/', {
            'slug': slug,
            'is_active': True,
            'extra_fields': 'sessions,prices,areas,mail_templates,portals,types'
        })

        if results is None or len(results) == 0:
            return None

        if len(results) == 1:
            return cls(results[0])
        else:
            raise MultipleObjectsReturned

    @property
    def dates(self):
        dates = []

        for session in self.sessions:
            if len(session.days) == 1:
                dates.append(f"{_date(session.start_date, 'j M')}")
            else:
                if session.start_date.month == session.end_date.month:
                    dates.append(f"{_date(session.start_date, 'j')}-{_date(session.end_date, 'j M')}")
                else:
                    dates.append(f"{_date(session.start_date, 'j M')}-{_date(session.end_date, 'j M')}")

        return ", ".join(dates)

    def get_events(self, coming: bool = False, days_before: int = 1) -> list:
        events = []

        if self.is_template:
            params = {
                'ordering': 'start_date',
                'extra_fields': 'sessions,prices,portals'
            }

            if coming:
                now = datetime.datetime.utcnow() + datetime.timedelta(days=days_before)
                params.update({'start_date': now.strftime("%Y-%m-%d")})

            results = ApexRequest.search_all(f'templates/{self.id}/events/', params)

            for item in results:
                events.append(Event(item))

        return events

    def get_participants(self, status=None) -> list:
        participants = []

        if not self.is_template:
            params = {}

            if status:
                params.update({'status': status})

            results = ApexRequest.search_all(f'events/{self.id}/participants/', params)

            for item in results:
                participants.append(EventParticipant(item))

        return participants

    def is_bookable(self, portal_id: int = None) -> bool:
        bookable = False

        if self.booked_participant_count < self.max_participants:
            bookable = True

        if portal_id and self.portal_participants and str(portal_id) in self.portal_participants.keys():
            booked_participants = self.portal_participants[str(portal_id)]
            max_participants = 0

            for portal in self.portals:
                if portal.portal_id == portal_id:
                    max_participants = portal.max_participants

                if portal.event_id == self.id and portal.portal_id == portal_id:
                    max_participants = portal.max_participants
                    break

            if booked_participants < max_participants:
                bookable = True
            else:
                bookable = False

        return bookable

    def has_few_places_left(self, portal_id: int = None) -> bool:
        few_places_left = False

        if self.booked_participant_count > self.max_participants - 3:
            few_places_left = True

        if not few_places_left and portal_id and self.portal_participants and \
                str(portal_id) in self.portal_participants.keys():
            booked_participants = self.portal_participants[str(portal_id)]
            max_participants = 0

            for portal in self.portals:
                if portal.portal_id == portal_id:
                    max_participants = portal.max_participants

                if portal.event_id == self.id and portal.portal_id == portal_id:
                    max_participants = portal.max_participants
                    break

            if booked_participants > max_participants - 3:
                few_places_left = True

        return few_places_left

    def __str__(self):
        return f"{self.event_id}: {self.name}"
