from apex_client.objects import ApexObject
from apex_client.objects.events.mixins import EventParticipantMixin


class SessionParticipant(EventParticipantMixin, ApexObject):
    valid_properties = ['id', 'participant_name', 'participant_email', 'participant_cell_phone_number',
                        'participant_phone_number', 'event', 'event_name', 'session', 'session_name', 'company_name',
                        'group', 'group_name', 'status', 'sessions', 'hours', 'event_days', 'invoice', 'portal',
                        'portal_name', 'event_identifier', 'attendance', 'coach', 'coach_name', 'coach_email',
                        'hours_daily', 'invoice_status', 'invoice_total_price', 'invoice_total_price_default_currency']
    date_properties = ['event_start_date', 'event_end_date', 'session_start_date', 'session_end_date', 'booked_date',
                       'confirmation_sent', 'invitation_sent']

    def __str__(self):
        return f"{self.event_name}: {self.participant_name} - {self.session_name} - {self.status}"
