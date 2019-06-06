from apex_client.objects import ApexObject


class Day(ApexObject):
    valid_properties = ['id', 'uuid', 'name', 'event', 'booked_participant_count', 'preliminary_participant_count',
                        'reserved_participant_count']
    date_properties = ['start_date', 'end_date']

    def __init__(self, json_data):
        super().__init__(json_data)

        self.session_object = None

    @property
    def session(self):
        from .session import Session

        if not self.session_object and self.event:
            self.session_object = Session.get(self.event)

        return self.session_object

    def __str__(self):
        return f"{self.start_date.isoformat() if self.start_date else ''} - " \
               f"{self.end_date.isoformat() if self.end_date else ''}"
