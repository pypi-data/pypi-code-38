from django.utils.datastructures import MultiValueDict

from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.config.configuration import TCellAgentConfiguration
from tcell_agent.config.logging_options import LoggingOptions
from tcell_agent.instrumentation.context import TCellInstrumentationContext


class ConfigurationBuilder(object):
    """
    Provides defaults for all settings needed by the native agent
    upon creation.

    """

    def __init__(self):
        self.configuration = TCellAgentConfiguration()
        self.configuration.config_filename = "tcell_agent.config"
        self.configuration.demomode = False
        self.configuration.enable_event_manager = False
        self.configuration.fetch_policies_from_tcell = False
        self.configuration.max_csp_header_bytes = None
        self.configuration.app_id = "TestAppId-AppId"
        self.configuration.api_key = "TestAppId-AppId"
        self.configuration.tcell_api_url = "https://api.tcell-preview.io/agents/api/v1"
        self.configuration.tcell_input_url = "https://input.tcell-preview.io/api/v1"
        self.configuration.hmac_key = None
        self.configuration.password_hmac_key = None
        self.configuration.allow_payloads = True
        self.configuration.js_agent_api_base_url = self.configuration.tcell_api_url
        self.configuration.js_agent_url = "https://jsagent.tcell.io/tcellagent.min.js"
        self.configuration.cache_folder = None
        self.configuration.log_directory = "tcell/logs"
        self.configuration.logging_options = LoggingOptions({"enabled": False})
        self.configuration.host_identifier = "python-test-suite"
        self.configuration.reverse_proxy_ip_address_header = "X-Forwarded-For"

    def update_attribute(self, attribute, setting):
        setattr(self.configuration, attribute, setting)
        return self

    def build(self):
        return self.configuration


class ContextBuilder(object):
    """
    Provides defaults for most settings used in a request

    """

    def __init__(self):
        self.context = TCellInstrumentationContext()
        self.context.session_id = "session-id"
        self.context.user_id = "user-id"
        self.context.user_agent = "user-agent"
        self.context.remote_address = "127.0.0.1"
        self.context.route_id = "route-id"
        self.context.path = "/some/path"
        self.context.fullpath = "/some/path?hide-my-value=sensitive"
        self.context.uri = "http://domain.com/some/path?hide-my-value=sensitive"
        self.context.ip_blocking_triggered = False
        self.context.method = "GET"
        self.context.referrer = "http://domain.com/home?_utm=some-value"

    def update_attribute(self, attribute, setting):
        setattr(self.context, attribute, setting)
        return self

    def build(self):
        return self.context


class AppSensorMetaBuilder(object):
    """
    Provides defaults for most settings used in a request

    """

    def __init__(self):
        self.appsensor_meta = AppSensorMeta()
        self.appsensor_meta.session_id = "session-id"
        self.appsensor_meta.user_id = "user-id"
        self.appsensor_meta.user_agent_str = "user-agent"
        self.appsensor_meta.remote_address = "127.0.0.1"
        self.appsensor_meta.route_id = "route-id"
        self.appsensor_meta.path = "/some/path"
        self.appsensor_meta.location = "http://domain.com/some/path?hide-my-value=sensitive"
        self.appsensor_meta.method = "GET"
        self.appsensor_meta.get_dict = MultiValueDict()
        self.appsensor_meta.post_dict = MultiValueDict()
        self.appsensor_meta.cookie_dict = {}
        self.appsensor_meta.headers_dict = {}
        self.appsensor_meta.files_dict = MultiValueDict()
        self.appsensor_meta.request_content_bytes_len = 0
        self.appsensor_meta.path_dict = {}
        self.appsensor_meta.response_content_bytes_len = 0
        self.appsensor_meta.response_code = 200
        self.appsensor_meta.request_processed = True
        self.appsensor_meta.response_processed = True
        self.appsensor_meta.csrf_reason = None
        self.appsensor_meta.sql_exceptions = []
        self.appsensor_meta.database_result_sizes = []

    def update_attribute(self, attribute, setting):
        setattr(self.appsensor_meta, attribute, setting)
        return self

    def build(self):
        return self.appsensor_meta
