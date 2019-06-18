import os
import sys

from ctypes import cdll, c_uint8, c_void_p, c_size_t, c_int, c_char_p, POINTER


_NATIVE_LIB = None


def get_native_lib():
    return _NATIVE_LIB


def get_linux_variant():
    if ("linux" in sys.platform) and os.path.isfile("/etc/alpine-release"):
        return "alpine-"

    return ""


version = "4.2.3"
prefix = {"win32": ""}.get(sys.platform, "lib")
extension = {"darwin": ".dylib", "win32": ".dll"}.get(sys.platform, ".so")
variant = get_linux_variant()


def load_native_lib():
    global _NATIVE_LIB  # pylint: disable=global-statement

    library_filename = "{}tcellagent-{}{}{}".format(prefix, variant, version, extension)
    _NATIVE_LIB = cdll.LoadLibrary(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                library_filename)))

    ###
    # All calls below have the following response interface
    #
    #    restype [int]: 0+ length of buffer_out answer
    #                   -1 general error
    #                   -2 buffer_out is null
    #                   -X buffer_out is not big enough for response. X represents how big the response was going to be
    ###

    _NATIVE_LIB.create_agent.argtypes = [c_char_p, c_size_t, POINTER(c_uint8), c_size_t]
    _NATIVE_LIB.create_agent.restype = c_int

    _NATIVE_LIB.request_policies.argtypes = [c_void_p, POINTER(c_uint8), c_size_t]
    _NATIVE_LIB.request_policies.restype = c_int

    _NATIVE_LIB.appfirewall_apply.argtypes = [c_void_p, c_char_p, c_size_t, POINTER(c_uint8), c_size_t]
    _NATIVE_LIB.appfirewall_apply.restype = c_int

    _NATIVE_LIB.patches_apply.argtypes = [c_void_p, c_char_p, c_size_t, POINTER(c_uint8), c_size_t]
    _NATIVE_LIB.patches_apply.restype = c_int

    _NATIVE_LIB.cmdi_apply.argtypes = [c_void_p, c_char_p, c_size_t, POINTER(c_uint8), c_size_t]
    _NATIVE_LIB.cmdi_apply.restype = c_int

    _NATIVE_LIB.get_headers.argtypes = [c_void_p, c_char_p, c_size_t, POINTER(c_uint8), c_size_t]
    _NATIVE_LIB.get_headers.restype = c_int

    _NATIVE_LIB.get_js_agent_script_tag.argtypes = [c_void_p, c_char_p, c_size_t, POINTER(c_uint8), c_size_t]
    _NATIVE_LIB.get_js_agent_script_tag.restype = c_int

    _NATIVE_LIB.check_http_redirect.argtypes = [c_void_p, c_char_p, c_size_t, POINTER(c_uint8), c_size_t]
    _NATIVE_LIB.check_http_redirect.restype = c_int

    _NATIVE_LIB.report_metrics.argtypes = [c_void_p, c_char_p, c_size_t, POINTER(c_uint8), c_size_t]
    _NATIVE_LIB.report_metrics.restype = c_int

    _NATIVE_LIB.login_fraud_apply.argtypes = [c_void_p, c_char_p, c_size_t, POINTER(c_uint8), c_size_t]
    _NATIVE_LIB.login_fraud_apply.restype = c_int

    _NATIVE_LIB.free_agent.argtypes = [c_void_p]
    _NATIVE_LIB.free_agent.restype = c_int

    _NATIVE_LIB.send_sanitized_events.argtypes = [c_void_p, c_char_p, c_size_t, POINTER(c_uint8), c_size_t]
    _NATIVE_LIB.send_sanitized_events.restype = c_int

    _NATIVE_LIB.log_message.argtypes = [c_void_p, c_char_p, c_size_t, POINTER(c_uint8), c_size_t]
    _NATIVE_LIB.log_message.restype = c_int

    _NATIVE_LIB.update_policies.argtypes = [c_void_p, c_char_p, c_size_t, POINTER(c_uint8), c_size_t]
    _NATIVE_LIB.update_policies.restype = c_int

    _NATIVE_LIB.test_event_sender.argtypes = [c_char_p, c_size_t, POINTER(c_uint8), c_size_t]
    _NATIVE_LIB.test_event_sender.restype = c_int

    _NATIVE_LIB.test_policies.argtypes = [c_char_p, c_size_t, POINTER(c_uint8), c_size_t]
    _NATIVE_LIB.test_policies.restype = c_int
