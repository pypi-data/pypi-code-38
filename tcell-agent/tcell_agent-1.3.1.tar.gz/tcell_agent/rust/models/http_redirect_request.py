class HttpRedirectRequest(dict):
    def __init__(self,
                 location_header,
                 from_domain,
                 status_code,
                 tcell_context):
        dict.__init__(self)

        self["location_header"] = location_header
        self["local_server"] = from_domain
        self["status_code"] = status_code

        self["method"] = tcell_context.method
        self["path"] = tcell_context.path
        self["remote_addr"] = tcell_context.remote_address
        self["full_uri"] = tcell_context.fullpath
        self["route_id"] = tcell_context.route_id
        self["session_id"] = tcell_context.session_id
        self["user_id"] = tcell_context.user_id
