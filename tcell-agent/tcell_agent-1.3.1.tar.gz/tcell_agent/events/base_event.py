from __future__ import unicode_literals


class SensorEvent(dict):
    def __init__(self,
                 event_type,
                 flush_right_away=False,
                 ensure_delivery=False,
                 send_event=True,
                 queue_wait=False):
        dict.__init__(self)
        self.queue_wait = queue_wait
        self.send_event = send_event
        self.flush_right_away = flush_right_away
        self.ensure_delivery = ensure_delivery
        self["event_type"] = event_type

    def get_debug_data(self):
        return "id: {id} type: {event_type}".format(
            id=hex(id(self)), event_type=self.get("event_type", "<unknown>"))
