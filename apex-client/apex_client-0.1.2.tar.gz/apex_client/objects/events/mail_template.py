from apex_client.objects import ApexObject


class MailTemplate(ApexObject):
    valid_properties = ['id', 'uuid', 'template_type', 'content', 'subject', 'sender_name', 'sender_email']
    mapped_properties = {
        'event': 'event_id'
    }

    def __init__(self, json_data: dict):
        super().__init__(json_data)

        self.event_object = None

    @property
    def event(self):
        from .event import Event

        if not self.event_object and self.event_id:
            self.event_object = Event.get(self.event_id)

        return self.event_object
