from functools import wraps

from tcell_agent.agent import TCellAgent
from tcell_agent.policies.policy_types import PolicyTypes
from tcell_agent.instrumentation.better_ip_address import better_ip_address
from tcell_agent.instrumentation.context import TCellInstrumentationContext
from tcell_agent.instrumentation.decorators import safe_wrap_function
from tcell_agent.instrumentation.utils import header_keys_from_request_env
from tcell_agent.tcell_logger import get_module_logger


# Easy test mocking
def get_logger():
    return get_module_logger(__name__)


def report_login_event(
        request_env,
        status,
        user_id,
        session_id,
        document_uri,
        user_agent=None,
        referrer=None,
        remote_address=None,
        header_keys=None,
        user_valid=None,
        password=None):

    from tcell_hooks.v1 import LOGIN_SUCCESS, LOGIN_FAILURE

    if user_agent is None:
        user_agent = request_env.get("HTTP_USER_AGENT")
    if referrer is None:
        referrer = request_env.get("HTTP_REFERER")
    if header_keys is None:
        header_keys = header_keys_from_request_env(request_env)
    if remote_address is None and request_env != {}:
        remote_address = better_ip_address(request_env)

    tcell_context = TCellInstrumentationContext()
    tcell_context.user_agent = user_agent
    tcell_context.remote_address = remote_address
    tcell_context.session_id = session_id
    tcell_context.fullpath = document_uri
    tcell_context.referrer = referrer

    login_policy = TCellAgent.get_policy(PolicyTypes.LOGIN)
    if status not in [LOGIN_SUCCESS, LOGIN_FAILURE]:
        get_logger().error("Unkown login status: {status}".format(status=status))
    elif (status == LOGIN_SUCCESS) and login_policy.login_success_enabled:
        login_policy.report_login_success(
            user_id=user_id,
            header_keys=header_keys,
            tcell_context=tcell_context
        )
    elif (status == LOGIN_FAILURE) and login_policy.login_failed_enabled:
        login_policy.report_login_failure(
            user_id=user_id,
            password=password,
            header_keys=header_keys,
            user_valid=user_valid,
            tcell_context=tcell_context
        )


def _instrument():
    import tcell_hooks.v1

    old_send_login_event = getattr(tcell_hooks.v1, "send_login_event")

    @wraps(old_send_login_event)
    def login_send(status,
                   session_id,
                   user_agent,
                   referrer,
                   remote_address,
                   header_keys,
                   user_id,
                   document_uri,
                   **kwargs):
        safe_wrap_function(
            "Sending Login Event",
            report_login_event,
            {},
            status,
            user_id,
            session_id,
            document_uri,
            user_agent=user_agent,
            referrer=referrer,
            remote_address=remote_address,
            header_keys=header_keys,
            user_valid=kwargs.get("user_valid"),
            password=kwargs.get("password"))

    setattr(tcell_hooks.v1, "send_login_event", login_send)

    old_send_django_login_event = getattr(tcell_hooks.v1, "send_django_login_event")

    @wraps(old_send_django_login_event)
    def django_send(status, django_request, user_id, session_id, **kwargs):
        safe_wrap_function(
            "Sending Django Login Event",
            report_login_event,
            django_request.META,
            status,
            user_id,
            session_id,
            django_request.get_full_path(),
            user_valid=kwargs.get("user_valid"),
            password=kwargs.get("password"))
    setattr(tcell_hooks.v1, "send_django_login_event", django_send)

    old_send_flask_login_event = getattr(tcell_hooks.v1, "send_flask_login_event")

    @wraps(old_send_flask_login_event)
    def flask_send(status, flask_request, user_id, session_id, **kwargs):
        safe_wrap_function(
            "Sending Flask Login Event",
            report_login_event,
            flask_request.environ,
            status,
            user_id,
            session_id,
            flask_request.url,
            user_valid=kwargs.get("user_valid"),
            password=kwargs.get("password"))
    setattr(tcell_hooks.v1, "send_flask_login_event", flask_send)


def instrument_tcell_hooks():
    try:
        import tcell_hooks  # pylint: disable=unused-variable

        _instrument()
    except ImportError:
        pass
    except Exception as e:
        get_logger().debug("Could not instrument tcell_hooks: {e}".format(e=e))
        get_logger().exception(e)
