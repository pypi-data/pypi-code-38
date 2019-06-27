class Filter(dict):
    _RESERVED_KEYS = [
        "_name", "topic",
    ]
    RESERVED_KEYS = []

    def __init__(self, **data):
        super(Filter, self).__init__(**data)

    def __eq__(self, other):
        return self.name == other.name

    def _match_dict(self, message, data):
        for filter_key, filter_value in data.items():
            if filter_key in self._RESERVED_KEYS + self.RESERVED_KEYS:
                continue

            message_value = message.get(filter_key)

            if isinstance(filter_value, dict):
                if not self._match_dict(message_value, filter_value):
                    return False
            elif isinstance(filter_value, (list, tuple)):
                if message_value not in filter_value:
                    return False
            elif message_value != filter_value:
                return False

        return True

    def subscribe(self, socket):
        if "topic" in self:
            socket.subscribe(self["topic"].encode("ascii"))

    def match(self, topic, message):
        if self.topic != topic:
            return False
        else:
            return self._match_dict(message, self)

    @property
    def name(self):
        return self.get("_name") or self.get("name")

    @property
    def topic(self):
        return self.get("topic")
