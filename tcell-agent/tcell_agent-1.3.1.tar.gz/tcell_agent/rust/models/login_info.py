class LoginInfo(dict):
    def __init__(self,
                 success,
                 user_id,
                 password,
                 header_keys,
                 user_valid,
                 tcell_context):
        dict.__init__(self)

        if success:
            self["event_name"] = "Success"
        else:
            self["event_name"] = "Failure"

        self["user_id"] = user_id
        self["user_agent"] = tcell_context.user_agent
        self["remote_address"] = tcell_context.remote_address
        self["header_keys"] = header_keys
        self["password"] = password
        self["session_id"] = tcell_context.session_id
        self["full_uri"] = tcell_context.fullpath
        self["referrer"] = tcell_context.referrer

        if user_valid is not None:
            self["user_valid"] = user_valid
