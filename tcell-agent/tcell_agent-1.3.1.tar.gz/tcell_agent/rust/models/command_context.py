class EmptyContext(object):
    def __init__(self):
        self.method = None
        self.path = None
        self.remote_address = None
        self.route_id = None
        self.session_id = None
        self.user_id = None
        self.uri = None


class CommandContext(dict):
    def __init__(self, cmd, tcell_context):
        dict.__init__(self)

        if not tcell_context:
            tcell_context = EmptyContext()

        self["command"] = cmd
        self["method"] = tcell_context.method
        self["path"] = tcell_context.path
        self["remote_address"] = tcell_context.remote_address
        self["route_id"] = tcell_context.route_id
        self["session_id"] = tcell_context.session_id
        self["user_id"] = tcell_context.user_id
        self["full_uri"] = tcell_context.uri
