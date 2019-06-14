from Homevee.APIModule import APIModule
from Homevee.Item.Event import Event
from Homevee.Item.Status import *
from Homevee.Manager.EventManager import EventManager

ACTION_KEY_GET_EVENTS = "getevents"
ACTION_KEY_GET_EVENT_TYPES = "geteventtypes"
ACTION_KEY_GET_UNSEEN_EVENTS = "getunseenevents"

class EventAPIModule(APIModule):
    def __init__(self):
        super(EventAPIModule, self).__init__()
        self.event_manager = EventManager()
        return

    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_GET_EVENTS: self.get_events,
            ACTION_KEY_GET_EVENT_TYPES: self.get_event_types,
            ACTION_KEY_GET_UNSEEN_EVENTS: self.get_unseen_events
        }
        return mappings

    def get_events(self, user, request, db):
        events = self.event_manager.get_events(user, type, request['limit'], request['offset'], db)
        return Status(type=STATUS_OK, data={'events': Event.list_to_dict(events)})

    def get_event_types(self, user, request, db):
        types = self.event_manager.get_event_types(db)
        return Status(type=STATUS_OK, data={'types': types})

    def get_unseen_events(self, user, request, db):
        count = self.event_manager.get_unseen_events(user, db)
        return Status(type=STATUS_OK, data={'count': count})