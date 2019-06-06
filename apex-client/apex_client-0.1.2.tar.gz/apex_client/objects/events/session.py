from typing import Optional

from apex_client.objects import ApexObject
from apex_client.request import ApexRequest

from .day import Day
from .session_participant import SessionParticipant


class Session(ApexObject):
    valid_properties = ['id', 'identifier', 'event_id', 'order', 'name', 'uuid', 'parent', 'is_active', 'is_template',
                        'number_of_days', 'timezone', 'venue', 'venue_name', 'venue_city', 'min_participants',
                        'max_participants', 'language']
    date_properties = ['date_created', 'date_modified', 'start_date', 'end_date']

    def __init__(self, json_data):
        super().__init__(json_data)

        self.days = []
        self.session_participants = []

        if 'days' in json_data.keys():
            for item in json_data['days']:
                self.days.append(Day(item))

    def get_participants(self, status: Optional[str] = None) -> list:
        if not self.is_template and (not self.session_participants or status):
            self.session_participants = []
            results = ApexRequest.search_all(f'events/{self.parent}/sessions/{self.id}/participants/',
                                             {'status': status} if status else None)

            if results:
                for item in results:
                    self.session_participants.append(SessionParticipant(item))

        return self.session_participants

    def __str__(self):
        return f"{self.event_id}#{self.order} - {self.name}"
