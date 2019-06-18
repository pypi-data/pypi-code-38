from tcell_agent.config.logging_options import LoggingOptions
from tcell_agent.loggers.module_logger import ModuleLogger
from tcell_agent.loggers.python_logger import PythonLogger
from tcell_agent.loggers.native_agent_logger import NativeAgentLogger
from tcell_agent.rust.models.agent_config import AgentConfig
from tcell_agent.rust.models.appfirewall_request_response import AppfirewallRequestResponse
from tcell_agent.rust.models.command_context import CommandContext
from tcell_agent.rust.models.http_redirect_request import HttpRedirectRequest
from tcell_agent.rust.models.login_info import LoginInfo
from tcell_agent.rust.models.patches_request import PatchesRequest
from tcell_agent.rust.native_callers import NativeAgentCaller, NativeCaller
from tcell_agent.rust.native_library import get_native_lib


class NativeAgent(object):
    def __init__(self, agent_ptr, logging_options):
        self.agent_ptr = agent_ptr
        self.logger = NativeAgentLogger(agent_ptr, logging_options)

    def get_module_logger(self, module_name):
        return ModuleLogger(module_name, self.logger)

    def log_response_errors(self, errors):
        for error in errors:
            self.logger.log_message("error", error, __name__)

    def call_with_one_argument(self, message, native_method_name, bytes_to_allocate):
        caller = NativeAgentCaller(self.agent_ptr,
                                   native_method_name,
                                   bytes_to_allocate)
        caller.append_parameter(message)
        response = caller.execute()
        self.log_response_errors(response.get_errors())

        return response.get_response_without_errors()

    def apply_appfirewall(self, appsensor_meta):
        if appsensor_meta:
            return self.call_with_one_argument(
                message=AppfirewallRequestResponse(appsensor_meta=appsensor_meta),
                native_method_name="appfirewall_apply",
                bytes_to_allocate=1024 * 8)

        return {}

    def apply_patches(self, appsensor_meta):
        if appsensor_meta:
            return self.call_with_one_argument(
                message=PatchesRequest(appsensor_meta=appsensor_meta),
                native_method_name="patches_apply",
                bytes_to_allocate=1024 * 8)

        return {}

    def apply_cmdi(self, cmd, tcell_context):
        if cmd and cmd.strip():
            return self.call_with_one_argument(
                message=CommandContext(cmd, tcell_context),
                native_method_name="cmdi_apply",
                bytes_to_allocate=1024 * 8)

        return {}

    def get_headers(self, tcell_context):
        if tcell_context:
            message = {
                "method": tcell_context.method,
                "path": tcell_context.path,
                "route_id": tcell_context.route_id,
                "session_id": tcell_context.session_id
            }
            return self.call_with_one_argument(
                message=message,
                native_method_name="get_headers",
                bytes_to_allocate=1024 * 16)

        return {}

    def get_js_agent_script_tag(self, tcell_context):
        if tcell_context:
            message = {
                "method": tcell_context.method,
                "path": tcell_context.path
            }
            return self.call_with_one_argument(
                message=message,
                native_method_name="get_js_agent_script_tag",
                bytes_to_allocate=1024 * 8)

        return {}

    def check_http_redirect(self,
                            location_header,
                            from_domain,
                            status_code,
                            tcell_context):
        if tcell_context:
            return self.call_with_one_argument(
                message=HttpRedirectRequest(location_header,
                                            from_domain,
                                            status_code,
                                            tcell_context),
                native_method_name="check_http_redirect",
                bytes_to_allocate=1024 * 8)

        return {}

    def login_fraud_apply(self,
                          success,
                          user_id,
                          password,
                          header_keys,
                          user_valid,
                          tcell_context):
        return self.call_with_one_argument(
            message=LoginInfo(success,
                              user_id,
                              password,
                              header_keys,
                              user_valid,
                              tcell_context),
            native_method_name="login_fraud_apply",
            bytes_to_allocate=1024 * 8)

    def request_policies(self):
        caller = NativeAgentCaller(agent_ptr=self.agent_ptr,
                                   native_method_name="request_policies",
                                   bytes_to_allocate=1024 * 32)
        response = caller.execute()
        self.log_response_errors(response.get_errors())

        return response.get_response_without_errors()

    def report_metrics(self,
                       request_time,
                       route_id,
                       session_id,
                       user_id,
                       user_agent,
                       remote_address):
        if request_time:
            message = {
                "elapsed_time": request_time,
                "route_id": route_id,
                "session_id": session_id,
                "user_id": user_id,
                "user_agent": user_agent,
                "remote_address": remote_address
            }
            return self.call_with_one_argument(
                message=message,
                native_method_name="report_metrics",
                bytes_to_allocate=1024 * 8)

        return {}

    def send_sanitized_events(self, events):
        if events:
            message = {
                "events": events
            }
            return self.call_with_one_argument(
                message=message,
                native_method_name="send_sanitized_events",
                bytes_to_allocate=1024 * 8)

        return {}

    # NOTE: this is only used in tests
    def update_policies(self, policy):
        if get_native_lib():
            return self.call_with_one_argument(
                message=policy,
                native_method_name="update_policies",
                bytes_to_allocate=1024 * 32)

        return {}


class PlaceholderNativeAgent(NativeAgent):
    def __init__(self, logging_options, log_directory):
        super(PlaceholderNativeAgent, self).__init__(
            None,
            LoggingOptions({"enabled": False})
        )
        self.logger = PythonLogger(logging_options, log_directory)


def create_native_agent(configuration):
    if get_native_lib():
        caller = NativeCaller(native_method_name="create_agent",
                              bytes_to_allocate=1024 * 8)
        caller.append_parameter(AgentConfig(configuration))
        response = caller.execute()

        if response.get_errors():
            logger = PythonLogger(configuration.logging_options,
                                  configuration.log_directory)
            for error in response.get_errors():
                logger.log_message("error", error, __name__)

        agent_ptr = response.get_response_without_errors().get("agent_ptr")
        if agent_ptr:
            return NativeAgent(agent_ptr,
                               configuration.logging_options)

    return PlaceholderNativeAgent(configuration.logging_options,
                                  configuration.log_directory)
