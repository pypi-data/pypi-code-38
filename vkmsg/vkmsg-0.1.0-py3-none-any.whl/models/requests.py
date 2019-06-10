class IncomingMessage(object):
    def __init__(self, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])


class IncomingRequest(object):
    def __init__(self, type, group_id, **kwargs):
        self.type = type
        self.group_id = group_id
        dialog_messages = ['message_new', 'message_reply', 'message_edit']
        for key in kwargs:
            setattr(self, key, kwargs[key])
        if self.type in dialog_messages:
            self.object = IncomingMessage(**self.object)
