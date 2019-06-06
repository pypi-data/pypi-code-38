from apex_client.objects import ApexObject


class EventArea(ApexObject):
    valid_properties = ['id', 'uuid', 'area_id', 'event_id', 'area_name', 'area_slug', 'level']

    def __init__(self, json_data: dict):
        super().__init__(json_data)

        self.event_object = None
        self.area_object = None

    @property
    def event(self):
        from .event import Event

        if self.event_object is None and self.event_id:
            self.event_object = Event.get(self.event_id)

        return self.event_object

    @property
    def area(self):
        from .area import Area

        if self.area_object is None and self.area_id:
            self.area_object = Area.get(self.area_id)

        return self.area_object

    def __str__(self):
        return f"{self.area_name}: {self.event_id}"
