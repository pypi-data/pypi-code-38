from typing import Optional

from apex_client.request import ApexRequest

from apex_client.objects import ApexObject
from apex_client.objects.events.mixins import EventParticipantMixin


class EventParticipant(EventParticipantMixin, ApexObject):
    STATUSES = ['booked', 'canceled', 'preliminary', 'reserve', 'rescheduled']

    valid_properties = ['id', 'participant_name', 'participant_email', 'participant_cell_phone_number',
                        'participant_phone_number', 'event', 'event_name', 'company_name', 'group',
                        'group_name', 'status', 'sessions', 'hours', 'event_days', 'invoice', 'portal', 'portal_name',
                        'event_identifier', 'attendance', 'coach', 'coach_name', 'coach_email', 'hours_daily',
                        'invoice_status', 'invoice_total_price', 'invoice_total_price_default_currency']
    date_properties = ['event_start_date', 'event_end_date', 'booked_date', 'confirmation_sent', 'invitation_sent']

    @classmethod
    def get(cls, event_id: int, participant_id: int) -> Optional['EventParticipant']:
        response = ApexRequest.get(f'events/{event_id}/participants/{participant_id}/')

        if response['status_code'] == 200:
            return cls(response['response'])

        return None

    def update(self) -> bool:
        if self.status in EventParticipant.STATUSES:
            response = ApexRequest.patch(f'events/{self.event}/participants/{self.participant}/',
                                         {'status': self.status, 'hours_daily': self.hours_daily})

            if response['status_code'] == 200:
                return True

        return False

    def __str__(self):
        return f"{self.event_name}: {self.participant_name} - {self.status}"
