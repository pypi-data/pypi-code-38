from apex_client.objects import ApexObject
from apex_client.objects.events import Event

from .portal import Portal


class PortalEvent(ApexObject):
    valid_properties = ['id', 'uuid', 'portal_id', 'event_id', 'portal_name', 'is_available', 'max_participants',
                        'booked_participants_count', 'identifier', 'event_name', 'is_active', 'number_of_days']

    def __init__(self, json_data: dict):
        super().__init__(json_data)

        self.event_object = None
        self.portal_object = None

    @property
    def event(self):
        if not self.event_object and self.event_id:
            self.event_object = Event.get(self.event_id, True)

            if not self.event_object:
                self.event_object = Event.get(self.event_id)

        return self.event_object

    @property
    def portal(self):
        if not self.portal_object and self.portal_id:
            self.portal_object = Portal.get(self.portal_id)

        return self.portal_object

    def __str__(self):
        return f"{self.event_name}: {self.portal_name}"
