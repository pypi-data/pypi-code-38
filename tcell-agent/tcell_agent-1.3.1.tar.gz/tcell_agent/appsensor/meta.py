class AppSensorMeta(object):
    def __init__(self):
        self.encoding = "utf-8"

        self.remote_address = None
        self.method = None
        self.location = None
        self.path = None
        self.route_id = None
        self.session_id = None
        self.user_id = None

        self.get_dict = None
        self.post_dict = None
        self.cookie_dict = None
        self.headers_dict = None
        self.files_dict = None
        self.request_body = None
        self.content_type = None
        self.request_content_bytes_len = 0
        self.user_agent_str = None

        self.path_dict = {}

        self.response_content_bytes_len = 0
        self.response_code = 200

        self.request_processed = False
        self.response_processed = False

        self.csrf_reason = None
        self.sql_exceptions = []
        self.database_result_sizes = []

    def path_parameters_data(self, path_dict):
        self.path_dict = path_dict or {}
